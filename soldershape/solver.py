"""Pinned circular-pad equilibrium computation and measured numerical checks."""

from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import os
import re
import signal
import subprocess
import tempfile
import time

from .model import JointSpec

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / ".engine"
SOURCE_SHA256 = "be7d60d9eb690f1fb124e2ecc12237a7a35be1935bfa5e92be3fe912207a3b6b"
MAX_OUTPUT_BYTES = 3_000_000
MAX_MESH_BYTES = 4_000_000
TIMEOUT_SECONDS = 90
NUMBER = r"[-+\d.eE]+"


class SolverError(RuntimeError):
    def __init__(self, message, evidence=None):
        super().__init__(message)
        self.message = message
        self.evidence = evidence or {}


def engine_info():
    binary = ENGINE / "src" / "evolver"
    try:
        info = json.loads((ENGINE / "provenance.json").read_text())
        actual_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
    except (OSError, ValueError):
        return {"ready": False, "error": "Run python3 tools/setup_engine.py to build the pinned local engine.", "source_sha256": SOURCE_SHA256}
    if info.get("source_sha256") != SOURCE_SHA256 or info.get("binary_sha256") != actual_hash:
        return {"ready": False, "error": "Engine identity differs from setup provenance. Rerun python3 tools/setup_engine.py.", "source_sha256": SOURCE_SHA256}
    return {"ready": True, **info}


def _model(spec):
    lower, upper = spec.lower_diameter_mm / 20, spec.upper_diameter_mm / 20
    lines = [
        'evolver_version "2.70"',
        f"parameter S_TENSION = {spec.surface_tension_n_m * 1000:.17g}",
        f"parameter SOLDER_DENSITY = {spec.density_g_cm3:.17g}",
        f"gravity_constant {980 if spec.gravity else 0}",
        f"parameter height = {spec.standoff_mm / 10:.17g}",
        f"parameter lower_radius = {lower:.17g}",
        f"parameter upper_radius = {upper:.17g}",
        f"parameter offset = {spec.offset_mm / 10:.17g}",
        "constraint 1", "formula: z = 0", "constraint 2", "formula: z = height",
        "constraint 3", "formula: x^2 + y^2 = lower_radius^2",
        "constraint 4", "formula: (x-offset)^2 + y^2 = upper_radius^2", "vertices",
    ]
    for index in range(6):
        lines.append(f"{index + 1} lower_radius*cos({index}*pi/3) lower_radius*sin({index}*pi/3) 0 constraints 1,3 fixed")
    for index in range(6):
        lines.append(f"{index + 7} offset+upper_radius*cos({index}*pi/3) upper_radius*sin({index}*pi/3) height constraints 2,4 fixed")
    lines.append("edges")
    for base, constraints in ((0, "1,3"), (6, "2,4")):
        for index in range(6):
            lines.append(f"{base + index + 1} {base + index + 1} {base + (index + 1) % 6 + 1} constraints {constraints} fixed")
    for index in range(6):
        lines.append(f"{index + 13} {index + 1} {index + 7}")
    lines.append("faces")
    for index in range(6):
        lines.append(f"{index + 1} {index + 1} {(index + 1) % 6 + 13} -{index + 7} -{index + 13} tension S_TENSION")
    lines.extend([
        "7 -6 -5 -4 -3 -2 -1 fixed no_refine tension 0",
        "8 7 8 9 10 11 12 fixed no_refine tension 0 constraint 2",
        "bodies",
        f"1 1 2 3 4 5 6 7 8 volume {spec.volume_mm3 / 1000:.17g} density SOLDER_DENSITY",
        "read", "hessian_normal",
        f"dx := {1e-5 * min(lower, upper):.17g}",
        f"dz := {1e-5 * spec.standoff_mm / 10:.17g}",
        "new_offset := offset;",
        "do_offset := { doff := new_offset-offset; offset := new_offset; set vertex x x+doff*z/height; recalc; }",
        "do_xforce := { new_offset := offset+dx; do_offset; energy_plus := total_energy-body[1].pressure*(body[1].volume-body[1].target); new_offset := offset-2*dx; do_offset; energy_minus := total_energy-body[1].pressure*(body[1].volume-body[1].target); xforce := -(energy_plus-energy_minus)/(2*dx); new_offset := offset+dx; do_offset; }",
        "do_zforce := { set vertex z z+dz*z/height; height := height+dz; recalc; energy_plus := total_energy-body[1].pressure*(body[1].volume-body[1].target); set vertex z z-2*dz*z/height; height := height-2*dz; recalc; energy_minus := total_energy-body[1].pressure*(body[1].volume-body[1].target); zforce := -(energy_plus-energy_minus)/(2*dz); set vertex z z+dz*z/height; height := height+dz; recalc; }",
    ])
    return "\n".join(lines) + "\n"


def _commands(level_count=2):
    lines = ["M 2", "u", "g 3", "r", "g 30", "r", "g 30", "hessian_seek", "hessian_seek"]
    for level in range(level_count):
        if level:
            lines.extend(["r", "g 30", "hessian_seek", "hessian_seek", "hessian_seek"])
        lines.extend([
            "energy_before := total_energy", "g 30", "hessian_seek", "hessian_seek",
            "stationarity_delta := abs(total_energy-energy_before)",
            "do_xforce", "do_zforce", "eigenprobe 0",
            f'printf "SS_LEVEL {level} %d %.17g %.17g %.17g %.17g %.17g %d %.17g\\n",facet_count,xforce,zforce,total_energy,body[1].volume,(body[1].volume-body[1].target)/body[1].target,eigen_neg,stationarity_delta',
        ])
    lines.extend([
        "r", "linear", "recalc",
        '{ foreach vertex vv do printf "VERTEX %d %.17g %.17g %.17g\\n",vv.id,vv.x,vv.y,vv.z; foreach facet ff do printf "TRIANGLE %d %d %d %d\\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id; } >>> "mesh.txt"',
        'printf "SS_DONE %d %.17g\\n",facet_count,body[1].volume', "quit 0",
    ])
    return "\n".join(lines) + "\n"


def _run(directory, evidence):
    stdout_path, stderr_path = directory / "stdout.txt", directory / "stderr.txt"
    termination = "completed"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen([str(ENGINE / "src" / "evolver"), "joint.fe"], cwd=directory, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, start_new_session=True, env={**os.environ, "LC_ALL": "C"})
        process.stdin.write(evidence["commands"].encode())
        process.stdin.close()
        deadline = time.monotonic() + TIMEOUT_SECONDS
        while process.poll() is None:
            if time.monotonic() > deadline:
                termination = "timeout"
            elif stdout_path.stat().st_size + stderr_path.stat().st_size > MAX_OUTPUT_BYTES:
                termination = "output_limit"
            elif (directory / "mesh.txt").exists() and (directory / "mesh.txt").stat().st_size > MAX_MESH_BYTES:
                termination = "mesh_limit"
            if termination != "completed":
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                break
            time.sleep(.05)
    evidence["stdout"] = stdout_path.read_bytes()[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
    evidence["stderr"] = stderr_path.read_bytes()[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
    evidence["returncode"] = process.returncode
    evidence["termination"] = termination
    if termination != "completed" or process.returncode:
        raise SolverError(f"Engine failed ({termination}, exit {process.returncode}).", evidence)
    if stdout_path.stat().st_size + stderr_path.stat().st_size > MAX_OUTPUT_BYTES:
        raise SolverError("Engine output exceeds its size limit.", evidence)
    if re.search(r"\b(?:ERROR|WARNING)\b", evidence["stdout"] + evidence["stderr"]):
        raise SolverError("Engine reported a numerical or command error. Inspect the captured solver output.", evidence)


def _mesh(path, target_volume):
    if not path.is_file() or path.stat().st_size > MAX_MESH_BYTES:
        raise SolverError("Solver mesh is missing or exceeds its size limit.")
    vertices, facets = {}, []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) == 5 and parts[0] == "VERTEX":
            identifier = int(parts[1])
            if identifier in vertices:
                raise SolverError("Solver mesh contains duplicate vertex identifiers.")
            vertices[identifier] = [float(value) * 10 for value in parts[2:]]
        elif len(parts) == 5 and parts[0] == "TRIANGLE":
            facets.append([int(value) for value in parts[2:]])
        else:
            raise SolverError("Solver returned an unrecognized mesh record.")
    if not 4 <= len(vertices) <= 60000 or not 4 <= len(facets) <= 100000:
        raise SolverError("Solver returned an empty or oversized mesh.")
    if not all(math.isfinite(value) for vertex in vertices.values() for value in vertex):
        raise SolverError("Solver mesh contains a nonfinite coordinate.")
    ordered = sorted(vertices)
    indices = {identifier: index for index, identifier in enumerate(ordered)}
    edges = Counter()
    directed = Counter()
    volume = 0.0
    minimum_area = math.inf
    triangles = []
    for facet in facets:
        if len(set(facet)) != 3 or any(vertex not in vertices for vertex in facet):
            raise SolverError("Solver returned an invalid mesh facet.")
        a, b, c = [vertices[index] for index in facet]
        u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        area = math.sqrt(sum(value*value for value in cross)) / 2
        if area <= 0:
            raise SolverError("Solver mesh contains a degenerate triangle.")
        minimum_area = min(minimum_area, area)
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
        for index in range(3):
            start, end = facet[index], facet[(index+1) % 3]
            edges[tuple(sorted((start, end)))] += 1
            directed[start, end] += 1
        triangles.append([indices[index] for index in facet])
    closed = set(edges.values()) == {2}
    oriented = all(directed[a, b] == 1 and directed[b, a] == 1 for a, b in edges)
    if not closed or not oriented or volume <= 0:
        raise SolverError("Solver mesh is not a positively oriented closed surface.")
    checks = {"closed": closed, "oriented": oriented, "nondegenerate": True, "volume_mm3": volume, "vertices": len(vertices), "triangles": len(triangles), "edges": len(edges), "euler_characteristic": len(vertices)-len(edges)+len(triangles), "minimum_triangle_area_mm2": minimum_area, "volume_relative_error": abs(volume/target_volume-1), "self_intersections_checked": False}
    return {"vertices_mm": [vertices[index] for index in ordered], "triangles": triangles}, checks


def _solve_with_levels(spec: JointSpec, level_count: int) -> dict:
    engine = engine_info()
    if not engine["ready"]:
        raise SolverError(engine["error"])
    evidence = {"model_fe": _model(spec), "commands": _commands(level_count), "stdout": "", "stderr": ""}
    try:
        with tempfile.TemporaryDirectory(prefix="soldershape-") as temporary:
            directory = Path(temporary)
            (directory / "joint.fe").write_text(evidence["model_fe"])
            _run(directory, evidence)
            pattern = rf"SS_LEVEL (\d+) (\d+) ({NUMBER}) ({NUMBER}) ({NUMBER}) ({NUMBER}) ({NUMBER}) (\d+) ({NUMBER})\n"
            matches = re.findall(pattern, evidence["stdout"])
            if len(matches) != level_count or [int(row[0]) for row in matches] != list(range(level_count)):
                raise SolverError("Engine did not return every expected refinement level.", evidence)
            levels = []
            for row in matches:
                level, facets, fx, fz, energy, volume, residual, negatives, stationarity = row
                values = list(map(float, (fx, fz, energy, volume, residual, stationarity)))
                if not all(math.isfinite(value) for value in values):
                    raise SolverError("Engine returned a nonfinite numerical result.", evidence)
                levels.append({"level": int(level), "facets": int(facets), "force_x_uN": float(fx)*10, "force_z_uN": float(fz)*10, "energy_erg": float(energy), "volume_mm3": float(volume)*1000, "volume_relative_error": abs(float(residual)), "negative_eigenvalues": int(negatives), "stationarity_energy_change_erg": float(stationarity), "stationarity_energy_change_relative": float(stationarity)/max(abs(float(energy)), 1e-30)})
            if not re.search(rf"SS_DONE \d+ ({NUMBER})\n", evidence["stdout"]):
                raise SolverError("Engine did not complete mesh export.", evidence)
            mesh, checks = _mesh(directory / "mesh.txt", spec.volume_mm3)
    except SolverError as error:
        if not error.evidence:
            error.evidence = evidence
        raise
    except (OSError, ValueError, OverflowError) as error:
        raise SolverError(f"Could not read engine result: {error}", evidence) from error
    previous, final = levels[-2:]
    force_scale = 2 * math.pi * ((spec.lower_diameter_mm + spec.upper_diameter_mm)/4) * spec.surface_tension_n_m * 1000
    deltas = {}
    for component in ("x", "z"):
        key = f"force_{component}_uN"
        absolute = abs(final[key] - previous[key])
        normalization = max(abs(final[key]), force_scale*.01)
        deltas[component] = {"absolute_uN": absolute, "normalization_uN": normalization, "relative": absolute/normalization, "capillary_relative": absolute/force_scale}
    warnings = []
    if max(level["volume_relative_error"] for level in levels) > .001:
        warnings.append("Curved solver volume residual exceeds 0.1 percent.")
    if final["negative_eigenvalues"]:
        warnings.append("The final local Hessian has negative eigenvalues.")
    if final["stationarity_energy_change_relative"] > 1e-7:
        warnings.append("Additional relaxation changed energy by more than 1e-7 relative.")
    change = max(delta["relative"] for delta in deltas.values())
    if change > .01:
        warnings.append("A force component changes by more than 1 percent under refinement, with a 1 percent capillary-scale normalization floor.")
    if checks["volume_relative_error"] > .001:
        warnings.append("Flat display/export tessellation volume differs from the requested volume by more than 0.1 percent.")
    diagnostics = {"volume_relative_error": final["volume_relative_error"], "force_change_relative": change, "force_component_changes": deltas, "force_normalization": "max(abs(final component), 0.01 * capillary force scale)", "capillary_force_scale_uN": force_scale, "negative_eigenvalues": final["negative_eigenvalues"], "stationarity_energy_change_relative": final["stationarity_energy_change_relative"], "stationarity_threshold_relative": 1e-7, "force_change_threshold_relative": .01, "mesh_volume_error_relative": checks["volume_relative_error"], "finite_difference_displacement_mm": {"x": 1e-5*min(spec.lower_diameter_mm, spec.upper_diameter_mm)/2, "z": 1e-5*spec.standoff_mm}, "solver_termination": evidence["termination"], "warnings": warnings}
    return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "not_converged" if warnings else "refinement_checked", "forces": {"x_uN": final["force_x_uN"], "z_uN": final["force_z_uN"]}, "diagnostics": diagnostics, "levels": levels, "mesh": mesh, "mesh_checks": checks, "engine": engine, "evidence": evidence}


def solve(spec: JointSpec) -> dict:
    result = _solve_with_levels(spec, 2)
    if result["status"] == "not_converged" and not result["diagnostics"]["negative_eigenvalues"]:
        preliminary = result
        result = _solve_with_levels(spec, 3)
        result["diagnostics"]["additional_refinement_reason"] = preliminary["diagnostics"]["warnings"]
        result["diagnostics"]["initial_refinement_check"] = {
            "status": preliminary["status"],
            "force_change_relative": preliminary["diagnostics"]["force_change_relative"],
            "stationarity_energy_change_relative": preliminary["diagnostics"]["stationarity_energy_change_relative"],
            "mesh_volume_error_relative": preliminary["diagnostics"]["mesh_volume_error_relative"],
        }
        result["evidence"]["preliminary_attempt"] = preliminary["evidence"]
    return result
