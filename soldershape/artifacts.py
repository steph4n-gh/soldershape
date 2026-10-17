"""Exports bind the exact solved geometry to its inputs and engine evidence."""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

from .model import InputError, JointSpec, LoadSpec, joint_spec_from_dict
from . import __version__


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def results_csv(results):
    output = io.StringIO(newline="")
    fields = ["row", "design", "status", "pad", "lower_diameter_mm", "upper_diameter_mm", "standoff_mm", "volume_mm3",
              "offset_mm", "normal_load_uN", "load_residual_uN", "surface_tension_n_m", "density_g_cm3", "gravity", "force_x_uN", "force_z_uN",
              "volume_relative_error", "force_change_relative", "error"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for i, result in enumerate(results):
        row = {key: result["input"].get(key, "") for key in fields if key in result["input"]}
        label = str(result.get("footprint", {}).get("pad", {}).get("identifier", ""))
        if label.startswith(("=", "+", "-", "@")):
            label = "'" + label
        row.update(row=i, design=result.get("design", ""), status=result["status"], pad=label,
                   standoff_mm=result.get("equilibrium", result["input"]).get("standoff_mm", ""),
                   load_residual_uN=result.get("load_balance", {}).get("residual_uN", ""),
                   force_x_uN=result.get("forces", {}).get("x_uN", ""),
                   force_z_uN=result.get("forces", {}).get("z_uN", ""),
                   volume_relative_error=result.get("diagnostics", {}).get("volume_relative_error", ""),
                   force_change_relative=result.get("diagnostics", {}).get("force_change_relative", ""),
                   error=result.get("error", ""))
        writer.writerow(row)
    return output.getvalue().encode()


def mesh_obj(mesh):
    lines = ["# SolderShape solved mesh; coordinates in millimeters"]
    lines.extend("v " + " ".join(f"{v:.17g}" for v in vertex) for vertex in mesh["vertices_mm"])
    lines.extend("f " + " ".join(str(i + 1) for i in tri) for tri in mesh["triangles"])
    return ("\n".join(lines) + "\n").encode()


def mesh_stl(mesh):
    lines = ["solid soldershape_mm"]
    vertices = mesh["vertices_mm"]
    for tri in mesh["triangles"]:
        a, b, c = (vertices[i] for i in tri)
        u, v = ([b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)])
        normal = [u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0]]
        length = math.sqrt(sum(x*x for x in normal))
        if not length > 0:
            raise ValueError("Cannot export a degenerate triangle.")
        lines.append("facet normal " + " ".join(f"{x/length:.17g}" for x in normal))
        lines.append(" outer loop")
        for vertex in (a, b, c):
            lines.append("  vertex " + " ".join(f"{x:.17g}" for x in vertex))
        lines.extend((" endloop", "endfacet"))
    lines.append("endsolid soldershape_mm")
    return ("\n".join(lines) + "\n").encode()


def make_bundle(results, source="", editable_case=None, comparison=None):
    files = {"results.csv": results_csv(results)}
    if source:
        files["source.kicad_mod"] = source.encode()
    if editable_case is not None:
        files["editable-case.json"] = json_bytes(editable_case)
    if comparison is not None:
        files["comparison.json"] = json_bytes(comparison)
    for i, result in enumerate(results):
        prefix = f"case-{i:02d}/"
        files[prefix + "input.json"] = json_bytes(result["input"])
        files[prefix + "result.json"] = json_bytes({k: v for k, v in result.items() if k != "evidence"})
        evidence = result.get("evidence", {})
        files[prefix + "evidence.json"] = json_bytes(evidence)
        static_evidence = evidence.get("fixed_gap_verification", {}).get("evidence", evidence)
        native_evidence = evidence.get("native_height_solve", {}).get("evidence", evidence.get("failed_native_attempt", {}))
        for stage, receipt in (("", static_evidence), ("load-height/", native_evidence)):
            if stage and not receipt:
                continue
            for key, filename in (("model_fe", "model.fe"), ("commands", "run.cmd"), ("stdout", "stdout.txt"), ("stderr", "stderr.txt")):
                files[prefix + stage + filename] = str(receipt.get(key, "")).encode()
        if "mesh" in result:
            files[prefix + "mesh-mm.obj"] = mesh_obj(result["mesh"])
            files[prefix + "mesh-mm.stl"] = mesh_stl(result["mesh"])
    manifest = {"schema": 1, "application": f"SolderShape {__version__}", "case_count": len(results),
                "units": {"length": "mm", "volume": "mm^3", "force": "micronewton", "energy": "erg"},
                "assumptions": "Fully wetted pinned circular pads; prescribed offset and either gap or supported normal load; isolated equilibrium joint. Material/process accuracy is not qualified. Numerical checks are not physical validation.",
                "replay": "python3 -m soldershape replay FILE.zip; archived scripts are evidence and are never executed by replay",
                "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}}
    files["manifest.json"] = json_bytes(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    return buffer.getvalue()


def read_bundle(path):
    if Path(path).stat().st_size > 40_000_000:
        raise InputError("Bundle exceeds 40 MB.")
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            names = [info.filename for info in members]
            if len(members) > 100 or len(set(names)) != len(names) or sum(i.file_size for i in members) > 160_000_000:
                raise InputError("Bundle exceeds the member or uncompressed size limit.")
            if any(name.startswith("/") or ".." in name.split("/") or "\\" in name for name in names):
                raise InputError("Bundle contains an unsafe filename.")
            manifest = json.loads(archive.read("manifest.json"))
            if not isinstance(manifest, dict) or manifest.get("schema") != 1 or not isinstance(manifest.get("files"), dict):
                raise InputError("Unsupported bundle schema.")
            if set(names) != {"manifest.json", *manifest["files"]}:
                raise InputError("Bundle file manifest does not match its members.")
            for name, digest in manifest["files"].items():
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise InputError("Bundle integrity check failed for " + name)
            count = manifest.get("case_count")
            if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 7:
                raise InputError("Invalid bundle case count.")
            cases = []
            for i in range(count):
                spec = joint_spec_from_dict(json.loads(archive.read(f"case-{i:02d}/input.json")))
                saved = json.loads(archive.read(f"case-{i:02d}/result.json"))
                if not isinstance(saved, dict) or saved.get("status") not in ("failed", "not_converged", "refinement_checked"):
                    raise InputError("Invalid saved result status.")
                if saved.get("input_sha256") != spec.sha256 or saved.get("input") != spec.to_dict():
                    raise InputError("Saved result does not match its normalized input.")
                if saved["status"] != "failed":
                    if isinstance(spec, LoadSpec):
                        equilibrium = JointSpec.from_dict(saved.get("equilibrium"))
                        if equilibrium != spec.at_gap(equilibrium.standoff_mm):
                            raise InputError("Saved loaded geometry does not match its request.")
                        balance = saved.get("load_balance")
                        if not isinstance(balance, dict) or balance.get("target_uN") != spec.normal_load_uN or balance.get("status") not in ("balanced", "not_balanced"):
                            raise InputError("Saved result is missing its load balance.")
                        for key in ("residual_uN", "tolerance_uN"):
                            value = balance.get(key)
                            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                                raise InputError("Saved result contains an invalid load balance.")
                        if balance["tolerance_uN"] < 0 or saved["status"] == "refinement_checked" and (balance["status"] != "balanced" or abs(balance["residual_uN"]) > balance["tolerance_uN"]):
                            raise InputError("Saved result did not pass its load balance.")
                    forces, engine = saved.get("forces"), saved.get("engine")
                    if not isinstance(forces, dict) or not isinstance(engine, dict):
                        raise InputError("Saved result is missing forces or engine provenance.")
                    for key in ("x_uN", "z_uN"):
                        value = forces.get(key)
                        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                            raise InputError("Saved result contains an invalid force.")
                cases.append((spec, saved))
            return cases
    except (zipfile.BadZipFile, KeyError, ValueError, TypeError) as error:
        if isinstance(error, InputError):
            raise
        raise InputError("Invalid SolderShape bundle: " + str(error)) from error
