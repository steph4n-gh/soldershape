"""Isolated prescribed-wetting finite-copper research calculations."""

from dataclasses import asdict, dataclass
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys

from soldershape.model import InputError, JointSpec, LoadSpec


ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "33666d32c92b6753925bb2fd29dc62ce5fed618b"
REPRESENTATION = "prescribed-wetting-finite-copper-envelope-v1"
MAX_INTERFACE_BYTES = 8_000_000
ADAPTER_SOURCE = Path(__file__).read_bytes()


@dataclass(frozen=True)
class FinitePadRequest:
    liquid: LoadSpec
    lower_metal_mm: float
    upper_metal_mm: float
    lower_wetting_depth_mm: float
    upper_wetting_depth_mm: float

    def __post_init__(self):
        if not isinstance(self.liquid, LoadSpec) or self.liquid.gravity:
            raise InputError("Finite-pad liquid must be a LoadSpec with gravity disabled.")
        for side in ("lower", "upper"):
            thickness = getattr(self, side + "_metal_mm")
            depth = getattr(self, side + "_wetting_depth_mm")
            if any(isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) for value in (thickness, depth)):
                raise InputError("Metal thickness and prescribed wetting depth must be finite numbers.")
            if not 0 < thickness <= 1 or not 0 <= depth <= thickness:
                raise InputError("Require 0 < metal thickness <= 1 mm and 0 <= wetting depth <= thickness.")

    def to_dict(self):
        return {"representation": REPRESENTATION, **asdict(self)}

    @classmethod
    def from_dict(cls, value):
        data = dict(value)
        if data.pop("representation", REPRESENTATION) != REPRESENTATION:
            raise InputError("Unknown finite-pad boundary representation.")
        return cls(**{**data, "liquid": LoadSpec.from_dict(data["liquid"])})

    @property
    def sha256(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def envelope_spec(request: FinitePadRequest) -> LoadSpec:
    liquid = request.liquid
    added = math.pi / 4 * (liquid.lower_diameter_mm**2 * request.lower_wetting_depth_mm + liquid.upper_diameter_mm**2 * request.upper_wetting_depth_mm)
    return LoadSpec(**{**liquid.to_dict(), "volume_mm3": liquid.volume_mm3 + added})


def _identities():
    production = {}
    for name in ("soldershape/model.py", "soldershape/solver.py"):
        current = (ROOT / name).read_bytes()
        baseline = subprocess.run(["git", "show", BASELINE_COMMIT + ":" + name], cwd=ROOT, check=True, capture_output=True).stdout
        production[name] = {"sha256": hashlib.sha256(current).hexdigest(), "baseline_sha256": hashlib.sha256(baseline).hexdigest(), "matches_baseline": current == baseline}
    if not all(value["matches_baseline"] for value in production.values()):
        raise RuntimeError("Production numerical source differs from the declared baseline.")
    return {"baseline_commit": BASELINE_COMMIT, "production": production, "adapter_sha256": hashlib.sha256(ADAPTER_SOURCE).hexdigest()}


def native_model(request: FinitePadRequest, gap_mm: float | None = None, normal_load_uN=None):
    from soldershape import solver

    envelope = envelope_spec(request)
    if gap_mm is None:
        from soldershape.model import spherical_gap_mm
        gap_mm = spherical_gap_mm(envelope.lower_diameter_mm, envelope.upper_diameter_mm, envelope.volume_mm3)
    return _adapt_model(request, solver._model(envelope.at_gap(gap_mm), normal_load_uN))


def _adapt_model(request, model):
    params = "\n".join(f"parameter {name} = {value / 10:.17g}" for name, value in (
        ("lower_metal", request.lower_metal_mm), ("upper_metal", request.upper_metal_mm),
        ("lower_depth", request.lower_wetting_depth_mm), ("upper_depth", request.upper_wetting_depth_mm)))
    constraints = "\n".join((
        params,
        "constraint 5 nonnegative", "formula: z-lower_depth+lower_metal",
        "constraint 6 nonnegative", "formula: height-upper_depth+upper_metal-z",
        "constraint 7 nonnegative", "formula: maximum(z-lower_depth,(x^2+y^2-lower_radius^2)/(2*lower_radius))",
        "constraint 8 nonnegative", "formula: maximum(height-upper_depth-z,((x-offset)^2+y^2-upper_radius^2)/(2*upper_radius))",
    ))
    if model.count("\nvertices\n") != 1:
        raise RuntimeError("Native model vertex boundary changed.")
    model = model.replace("\nvertices\n", "\n" + constraints + "\nvertices\n")
    section = None
    adapted = []
    counts = {"vertices": 0, "edges": 0, "faces": 0}
    for line in model.splitlines():
        if line in ("vertices", "edges", "faces", "bodies", "read"):
            section = line
        if line[:1].isdigit() and section in counts:
            if section == "edges" and int(line.split()[0]) >= 13 or section == "faces" and "tension S_TENSION" in line:
                if "constraints " in line:
                    line = line.replace("constraints 1,3", "constraints 1,3,5,6,7,8").replace("constraints 2,4", "constraints 2,4,5,6,7,8")
                else:
                    line += " constraints 5,6,7,8"
                counts[section] += 1
        adapted.append(line)
    if counts != {"vertices": 0, "edges": 6, "faces": 6}:
        raise RuntimeError("Native model topology changed before finite-pad adaptation.")
    return "\n".join(adapted) + "\n"


def _commands(original, level_count, loaded):
    commands = original(level_count, loaded).replace("hessian_seek", "hessian_seek\ng 5")
    samples = '\n'.join(('{',
        'foreach vertex vv do printf "QV %d %.17g %.17g %.17g\\n",vv.id,vv.x,vv.y,vv.z;',
        'foreach edge ee do printf "QE %d %d %d %d\\n",ee.id,ee.vertex[1].id,ee.vertex[2].id,ee.midv;',
        'foreach facet ff where ff.density > 0 do printf "QF %d %d %d %d\\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id;',
        '} >>> "interface.txt"'))
    marker = "r\nlinear\nrecalc\n"
    if commands.count(marker) != 1:
        raise RuntimeError("Native quadratic export boundary changed.")
    return commands.replace(marker, "r\n" + samples + "\nlinear\nrecalc\n")


def _interface_diagnostics(text, request, height_mm):
    vertices, edges, facets = {}, {}, []
    for line in text.splitlines():
        row = line.split()
        if row[0] == "QV":
            vertices[int(row[1])] = tuple(float(value) * 10 for value in row[2:])
        elif row[0] == "QE":
            edges[frozenset((int(row[2]), int(row[3])))] = int(row[4])
        elif row[0] == "QF":
            facets.append(tuple(map(int, row[2:])))
        else:
            raise ValueError("Unrecognized quadratic-interface record.")
    if not facets:
        raise ValueError("No liquid-air quadratic facets exported.")
    lower_radius, upper_radius = request.liquid.lower_diameter_mm / 2, request.liquid.upper_diameter_mm / 2
    tolerance = max(1e-7, height_mm * 1e-6)
    minima = {"lower_substrate": math.inf, "upper_substrate": math.inf, "lower_copper": math.inf, "upper_copper": math.inf}
    contacts = {key: 0 for key in minima}
    penetration_count = 0
    sample_count = 0
    for ids in facets:
        corners = [vertices[index] for index in ids]
        mids = [vertices[edges[frozenset((ids[i], ids[(i+1) % 3]))]] for i in range(3)]
        lower_rim = [abs(v[2]) <= tolerance and abs((v[0]**2+v[1]**2-lower_radius**2)/(2*lower_radius)) <= tolerance for v in corners]
        upper_rim = [abs(v[2]-height_mm) <= tolerance and abs(((v[0]-request.liquid.offset_mm)**2+v[1]**2-upper_radius**2)/(2*upper_radius)) <= tolerance for v in corners]
        for i in range(5):
            for j in range(5-i):
                a, b, c = i / 4, j / 4, 1 - (i+j) / 4
                weights = (a*(2*a-1), b*(2*b-1), c*(2*c-1), 4*a*b, 4*b*c, 4*c*a)
                point = [sum(weight * vertex[axis] for weight, vertex in zip(weights, corners + mids)) for axis in range(3)]
                x, y, z = point
                radial_lower = (x*x+y*y-lower_radius**2) / (2*lower_radius)
                radial_upper = ((x-request.liquid.offset_mm)**2+y*y-upper_radius**2) / (2*upper_radius)
                values = {
                    "lower_substrate": z-request.lower_wetting_depth_mm+request.lower_metal_mm,
                    "upper_substrate": height_mm-request.upper_wetting_depth_mm+request.upper_metal_mm-z,
                    "lower_copper": max(z-request.lower_wetting_depth_mm, radial_lower),
                    "upper_copper": max(height_mm-request.upper_wetting_depth_mm-z, radial_upper),
                }
                support = [index for index, value in enumerate((a, b, c)) if value > 0]
                rim = len(support) <= 2 and (all(lower_rim[index] for index in support) or all(upper_rim[index] for index in support))
                for key, value in values.items():
                    minima[key] = min(minima[key], value)
                    if abs(value) <= tolerance and not rim:
                        contacts[key] += 1
                penetration_count += min(values.values()) < -tolerance
                sample_count += 1
    return {"method": "15 barycentric samples per curved quadratic liquid-air facet before flattening; zero-tension caps excluded", "continuous_clearance_certified": False,
            "free_facets": len(facets), "samples": sample_count, "tolerance_mm": tolerance, "minimum_constraint_values_mm": minima,
            "penetrating_samples": penetration_count, "new_contact_samples": contacts, "active_new_contact": any(contacts.values()), "intrusion_detected": bool(penetration_count)}


def _save_native(directory, result):
    (directory / "native.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    inventory = {}

    def visit(value, path):
        if not isinstance(value, dict):
            return
        if "model_fe" in value and "commands" in value:
            target = directory / "raw" / path
            target.mkdir(parents=True, exist_ok=True)
            for key, name in (("model_fe", "joint.fe"), ("commands", "commands.txt"), ("stdout", "stdout.txt"), ("stderr", "stderr.txt"), ("quadratic_interface", "interface.txt")):
                if key in value:
                    (target / name).write_text(value[key])
        for key, child in value.items():
            if isinstance(child, dict):
                visit(child, path / key)
    visit(result, Path("native"))
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name not in ("result.json", "worker.stderr", "worker.stdout"):
            inventory[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return inventory


def _worker(job, directory):
    from soldershape import solver

    request = FinitePadRequest.from_dict(job["request"])
    identities = _identities()
    (directory / "adapter.py").write_bytes(ADAPTER_SOURCE)
    envelope = envelope_spec(request)
    original_model, original_commands, original_run = solver._model, solver._commands, solver._run
    if job["kind"] != "bare_fixed":
        solver._model = lambda spec, normal_load_uN=None: _adapt_model(request, original_model(spec, normal_load_uN))
    solver._commands = lambda level_count=2, loaded=False: _commands(original_commands, level_count, loaded)

    def run_with_interface(path, evidence):
        original_run(path, evidence)
        interface = path / "interface.txt"
        if not interface.is_file() or interface.stat().st_size > MAX_INTERFACE_BYTES:
            raise solver.SolverError("Quadratic interface is missing or oversized.", evidence)
        evidence["quadratic_interface"] = interface.read_text()
    solver._run = run_with_interface
    try:
        if job["kind"] == "loaded":
            native = solver.solve_loaded(envelope)
        else:
            fixed = envelope.at_gap(job["envelope_height_mm"])
            native = solver._solve_fixed(fixed) if job["level_count"] == 2 else solver._solve_with_levels(fixed, job["level_count"])
    except solver.SolverError as error:
        native = {"status": "failed", "error": str(error), "evidence": error.evidence}
    height = native.get("equilibrium", {}).get("standoff_mm")
    final_evidence = native.get("evidence", {})
    if "fixed_gap_verification" in final_evidence:
        final_evidence = final_evidence["fixed_gap_verification"]["evidence"]
    interface = final_evidence.get("quadratic_interface")
    diagnostics = _interface_diagnostics(interface, request, height) if interface is not None and height is not None else None
    numerical = native.get("status") == "refinement_checked" and not native.get("model_warnings")
    gap = height - request.lower_wetting_depth_mm - request.upper_wetting_depth_mm if height is not None else None
    eligible = job["kind"] != "bare_fixed" and numerical and gap is not None and gap > 0 and diagnostics is not None and not diagnostics["intrusion_detected"] and not diagnostics["active_new_contact"]
    result = {"schema": "soldershape.prelab.finite.v1", "request": request.to_dict(), "request_sha256": request.sha256,
              "calculation_sha256": hashlib.sha256(json.dumps(job, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
              "kind": job["kind"], "status": native["status"], "numeric_gates_passed": numerical,
              "physical_eligibility": eligible, "physical_validation": "unqualified; prescribed wetting hypothesis only",
              "accepted_face_gap_mm": gap if eligible else None, "attempted_face_gap_mm": gap,
              "envelope_height_mm": height, "liquid_volume_mm3": request.liquid.volume_mm3, "envelope_volume_mm3": envelope.volume_mm3,
              "copper_volume_mm3": envelope.volume_mm3-request.liquid.volume_mm3, "interface": diagnostics,
              "forces": native.get("forces"), "levels": native.get("levels"), "diagnostics": native.get("diagnostics"),
              "load_balance": native.get("load_balance"), "error": native.get("error"), "identities": identities,
              "engine": solver.engine_info(), "energy_erg": native.get("levels", [{}])[-1].get("energy_erg")}
    result["files"] = _save_native(directory, native)
    return result


def _isolated(request, directory, kind="loaded", envelope_height_mm=None, level_count=2):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    job = {"request": request.to_dict(), "kind": kind, "envelope_height_mm": envelope_height_mm, "level_count": level_count}
    (directory / "request.json").write_text(json.dumps(job, indent=2, sort_keys=True) + "\n")
    with (directory / "worker.stdout").open("wb") as stdout, (directory / "worker.stderr").open("wb") as stderr:
        completed = subprocess.run([sys.executable, "-m", "prelab.finite", "--worker", str(directory)], cwd=ROOT,
                                   env={**os.environ, "LC_ALL": "C"}, stdout=stdout, stderr=stderr, timeout=600)
    if completed.returncode or not (directory / "result.json").is_file():
        result = {"schema": "soldershape.prelab.finite.v1", "status": "failed", "request": request.to_dict(),
                  "request_sha256": request.sha256, "accepted_face_gap_mm": None, "physical_eligibility": False,
                  "error": "Isolated worker failed; inspect retained worker.stderr.", "returncode": completed.returncode}
        (directory / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return json.loads((directory / "result.json").read_text())


def solve_finite_pad(request: FinitePadRequest, directory: Path) -> dict:
    return _isolated(request, directory)


def fixed_energy_check(request: FinitePadRequest, directory: Path, face_gap_mm=None, delta_mm=0.0005, level_count=2):
    if isinstance(delta_mm, bool) or not isinstance(delta_mm, (float, int)) or not math.isfinite(delta_mm) or delta_mm <= 0:
        raise InputError("Energy-check displacement must be positive and finite.")
    if level_count not in (2, 3):
        raise InputError("Energy-check level count must be 2 or 3.")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    if face_gap_mm is None:
        loaded = solve_finite_pad(request, directory / "loaded")
        face_gap_mm = loaded["accepted_face_gap_mm"]
    if face_gap_mm is None:
        result = {"status": "failed", "error": "No eligible loaded face gap for reaction check.", "physical_validation": "unqualified"}
    else:
        rows = []
        for levels in sorted(set((level_count, 3))):
            for step in (delta_mm, delta_mm / 2):
                values = []
                for sign in (-1, 1):
                    height = face_gap_mm + request.lower_wetting_depth_mm + request.upper_wetting_depth_mm + sign * step
                    name = f"levels{levels}-step{step:.9f}-{'minus' if sign < 0 else 'plus'}"
                    values.append(_isolated(request, directory / name, "fixed", height, levels))
                eligible = all(value["physical_eligibility"] for value in values)
                reaction = -50 * (values[1]["energy_erg"]-values[0]["energy_erg"]) / step if eligible else None
                refinement_reactions = [{"level": minus["level"], "minus_facets": minus["facets"], "plus_facets": plus["facets"],
                                         "reaction_uN": -50*(plus["energy_erg"]-minus["energy_erg"])/step}
                                        for minus, plus in zip(values[0].get("levels") or [], values[1].get("levels") or [])] if eligible else []
                rows.append({"level_count": levels, "delta_mm": step, "reaction_uN": reaction,
                             "reactions_by_refinement": refinement_reactions,
                             "minus_status": values[0]["status"], "plus_status": values[1]["status"],
                             "conditional_fixed_wetting_eligible": eligible,
                             "minus_request_sha256": values[0]["request_sha256"], "plus_request_sha256": values[1]["request_sha256"],
                             "minus_calculation_sha256": values[0].get("calculation_sha256"), "plus_calculation_sha256": values[1].get("calculation_sha256")})
        reactions = [refinement["reaction_uN"] for row in rows for refinement in row["reactions_by_refinement"][-2:]]
        spread = max(reactions)-min(reactions) if all(row["reaction_uN"] is not None for row in rows) else None
        residual = max(abs(value-request.liquid.normal_load_uN) for value in reactions) if reactions else None
        tolerance = max(.01, 2*spread) if spread is not None else None
        capillary_scale = 2*math.pi*(request.liquid.lower_diameter_mm+request.liquid.upper_diameter_mm)/4*request.liquid.surface_tension_n_m*1000
        normalization = max(max(map(abs, reactions), default=0), .01*capillary_scale)
        converged = spread is not None and spread/normalization <= .01
        passed = converged and residual <= tolerance
        result = {"status": "reaction_checked" if passed else "failed", "face_gap_mm": face_gap_mm,
                  "target_reaction_uN": request.liquid.normal_load_uN, "checks": rows, "reaction_spread_uN": spread,
                  "maximum_load_residual_uN": residual, "numerical_tolerance_uN": tolerance,
                  "reaction_change_relative": spread/normalization if spread is not None else None, "reaction_change_threshold_relative": .01,
                  "check_kind": "Fresh relaxed capillary energies at two central-difference steps and extra refinement; not bare affine reaction.",
                  "physical_validation": "unqualified; prescribed fixed wetting and sampled inactive obstacles only"}
    (directory / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, required=True)
    args = parser.parse_args()
    output = _worker(json.loads((args.worker / "request.json").read_text()), args.worker)
    (args.worker / "result.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
