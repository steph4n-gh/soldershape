"""Exports bind the exact solved geometry to its inputs and engine evidence."""

import csv
import hashlib
from html import escape
import io
import json
import math
from pathlib import Path
import zipfile

from .model import InputError, JointSpec, LoadSpec, joint_spec_from_dict
from . import __version__

PYTHON_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


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


def screen_pair(reference, candidate):
    if any(row["status"] != "refinement_checked" for row in (reference, candidate)):
        return {"status": "numerical_failure", "headline": "At least one case has no checked equilibrium.",
                "details": [row.get("error", "Numerical checks did not pass.") for row in (reference, candidate) if row["status"] != "refinement_checked"],
                "reference_rule_met": None, "candidate_rule_met": None}
    warnings = [warning for row in (reference, candidate) for warning in row.get("model_warnings", [])]
    if warnings:
        return {"status": "outside_model_scope", "headline": "Numerical success reaches a physical model limit.",
                "details": warnings+["No volume preference follows. Missing substrate contact can change these forces."],
                "reference_rule_met": None, "candidate_rule_met": None}
    met = [row["forces"]["x_uN"]*row["input"]["offset_mm"] < 0 and row["forces"]["z_uN"] <= 0
           for row in (reference, candidate)]
    headline = "Inspect both force directions against the declared fixture objective."
    if met[0] != met[1]:
        labels = ["Reference", "Candidate"]
        inputs = [row["input"] for row in (reference, candidate)]
        if ({key: value for key, value in inputs[0].items() if key != "volume_mm3"}
                == {key: value for key, value in inputs[1].items() if key != "volume_mm3"}
                and inputs[0]["volume_mm3"] != inputs[1]["volume_mm3"]):
            labels = ["Less solder", "More solder"]
            if inputs[0]["volume_mm3"] > inputs[1]["volume_mm3"]:
                labels.reverse()
        passed = 0 if met[0] else 1
        failed = 1-passed
        failure = "pushes upward." if (reference, candidate)[failed]["forces"]["z_uN"] > 0 else "does not."
        headline = f"{labels[passed]} meets this declared fixture objective. {labels[failed]} {failure}"
    return {"status": "conditional_comparison", "headline": headline,
            "details": ["The objective requires lateral restoration and no upward separating force at the held gap.",
                        "This numerical screen does not select a production solder volume."],
            "reference_rule_met": met[0], "candidate_rule_met": met[1]}


def _quantity(value, unit):
    if unit == "mm":
        return f"{value*1000:.6g} µm ({value:.6g} mm)"
    if unit == "mm³":
        return f"{value*1000:.6g} nL ({value:.6g} mm³)"
    return f"{value:.6g} {unit}"


def review_record(results, comparison=None, *, source="", board_selection=None):
    """Describe saved numerical rows without deriving a production recommendation."""
    qualification = "Physical force accuracy is unqualified. Numerical checks are not physical validation or production approval."
    rows = []
    fields = (("lower_diameter_mm", "Lower pad diameter", "mm"),
              ("upper_diameter_mm", "Upper pad diameter", "mm"),
              ("volume_mm3", "Solder volume", "mm³"), ("offset_mm", "Offset", "mm"),
              ("standoff_mm", "Held wetted-plane gap", "mm"),
              ("normal_load_uN", "Downward supported load", "µN"),
              ("surface_tension_n_m", "Surface tension", "N/m"),
              ("density_g_cm3", "Density", "g/cm³"))
    for index, result in enumerate(results):
        inputs = result["input"]
        loaded = "normal_load_uN" in inputs
        status = result["status"]
        warnings = list(result.get("model_warnings", []))
        label = result.get("design") or ("Result" if len(results) == 1 else f"Offset {index+1}")
        facts = [f"Solder volume {_quantity(inputs['volume_mm3'], 'mm³')}; offset {_quantity(inputs['offset_mm'], 'mm')}."]
        condition = (f"Downward supported load {_quantity(inputs['normal_load_uN'], 'µN')}." if loaded else
                     f"Held wetted-plane gap {_quantity(inputs['standoff_mm'], 'mm')}.")
        facts.append(condition)
        if status == "failed":
            headline = "No equilibrium prediction is available."
            facts.append("No force or solved gap is available for this failed row.")
        else:
            headline = "Checked prediction under supported load." if loaded else "Checked prediction at a held gap."
            if status != "refinement_checked":
                headline = "Numerical checks did not pass."
                facts.append("Returned numbers are unchecked numerical output. No comparative conclusion follows.")
            forces = result.get("forces", {})
            if loaded and "standoff_mm" in result.get("equilibrium", {}):
                facts.append(f"Solved wetted-plane gap {_quantity(result['equilibrium']['standoff_mm'], 'mm')}.")
            if "x_uN" in forces:
                offset, lateral = inputs["offset_mm"], forces["x_uN"]
                facts.append(f"X force {_quantity(lateral, 'µN')}.")
                if offset == 0:
                    facts.append("Zero offset has no lateral restoration comparison.")
                else:
                    restoring = -math.copysign(1, offset)*lateral
                    direction = "toward alignment" if restoring > 0 else "away from alignment" if restoring < 0 else "zero"
                    facts.append(f"Restoring force {_quantity(restoring, 'µN')} ({direction}).")
            if "z_uN" in forces:
                vertical = forces["z_uN"]
                direction = "upward" if vertical > 0 else "downward" if vertical < 0 else "zero"
                facts.append(f"Z force {_quantity(vertical, 'µN')} ({direction}).")
                if loaded:
                    if status == "refinement_checked" and result.get("load_balance", {}).get("status") == "balanced":
                        facts.append("Upward solder force balances the declared downward load within the numerical tolerance.")
                    else:
                        facts.append("Positive Z is the load-support direction. This row has not established a checked load balance.")
                elif vertical > 0:
                    facts.append("The solder pushes the upper pad upward at this held gap.")
                elif vertical < 0:
                    facts.append("The solder pulls the upper pad downward at this held gap.")
            if warnings:
                headline = "A model limit blocks a design preference."
                facts.append("Retain these observations, but no volume preference follows from a model-limited row.")
        row = {"label": label, "input_sha256": result["input_sha256"], "numerical_status": status,
               "headline": headline, "facts": facts,
               "inputs": [{"label": label, "value": _quantity(inputs[key], unit)} for key, label, unit in fields if key in inputs],
               "warnings": warnings, "input": dict(inputs)}
        row["inputs"].append({"label": "Gravity", "value": "Included" if inputs.get("gravity") else "Excluded"})
        if status == "failed":
            row["error"] = result.get("error", "Numerical calculation failed.")
        else:
            for key in ("equilibrium", "forces", "load_balance"):
                if key in result:
                    row[key] = result[key]
        rows.append(row)
    footprint = results[0].get("footprint", {}) if results else {}
    context = {"footprint_name": footprint.get("name", ""),
               "pad_identifier": footprint.get("pad", {}).get("identifier", ""),
               "source_footprint_sha256": hashlib.sha256(source.encode()).hexdigest() if source else footprint.get("sha256", "")}
    if board_selection is not None:
        context["board_selection"] = board_selection
    kind = "comparison" if comparison is not None else "single" if len(rows) == 1 else "sweep"
    headline = rows[0]["headline"] if len(rows) == 1 else "Inspect each saved offset. No sweep optimum is claimed."
    facts = list(rows[0]["facts"]) if len(rows) == 1 else []
    if comparison is not None:
        allowed = comparison.get("status") == "compared" and all(row["numerical_status"] == "refinement_checked" and not row["warnings"] for row in rows)
        headline = "The comparison is inconclusive."
        if not allowed:
            facts = [comparison.get("reason", "Numerical or model-scope checks block a comparative conclusion.")]
        else:
            headline = "Compare these predictions under the declared condition."
            delta = comparison.get("delta", {})
            facts = []
            if "gap_mm" in delta and "normal_load_uN" in results[0]["input"]:
                facts.append(f"Candidate minus reference solved gap {_quantity(delta['gap_mm'], 'mm')} under the same downward load.")
                facts.append("Upward load support is expected in this supported-load comparison.")
            if delta.get("restoring_force_uN") is not None:
                facts.append(f"Candidate minus reference restoring force {_quantity(delta['restoring_force_uN'], 'µN')}.")
            elif all(result["input"]["offset_mm"] == 0 for result in results):
                facts.append("Zero offset has no lateral restoration comparison.")
            if "vertical_force_uN" in delta:
                facts.append(f"Candidate minus reference Z force {_quantity(delta['vertical_force_uN'], 'µN')}.")
            if board_selection is not None and all("standoff_mm" in result["input"] and result["input"]["offset_mm"] != 0 for result in results) and len(results) == 2:
                screen = screen_pair(*results)
                headline = screen["headline"]
                facts.extend(screen["details"])
            else:
                facts.append("These forces and gaps do not select a production solder volume.")
    record = {"schema": "soldershape.review.v1", "kind": kind, "headline": headline, "facts": facts,
              "physical_qualification": "unqualified", "rows": rows, "context": context, "qualification": qualification,
              "convention": ["The model assumes an isolated equilibrium joint with fully wetted pinned circular rims. Wetting chemistry, thermal reflow and neighboring joints are unresolved.",
                             "Forces act on the upper pad. Positive X follows the prescribed offset axis; positive Z is upward.",
                             "At nonzero offset, restoring force is -sign(offset) × X force. Positive restoring force points toward alignment.",
                             "Engineering values are displayed to six significant digits. Exact canonical inputs and forces are retained below."],
              "next_steps": ["Check the declared dimensions, material and boundary assumptions against the actual process.",
                             "Measure physical joint geometry and forces before using these predictions for production decisions.",
                             "Replay the accompanying numerical evidence; replay verifies numerical agreement, not physical accuracy."]}
    if comparison is not None:
        record["comparison_status"] = comparison.get("status")
        if comparison.get("reason"):
            record["comparison_reason"] = comparison["reason"]
    return record


def review_html(record):
    """Return a self-contained readable brief with escaped saved values."""
    def text(value):
        return escape(str(value), quote=True)
    def listing(items):
        return "<ul>"+"".join("<li>"+text(item)+"</li>" for item in items)+"</ul>"
    context = record["context"]
    pieces = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
              '<title>SolderShape numerical review</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:920px;margin:40px auto;padding:0 20px;color:#152623}h1,h2{line-height:1.2}section{border-top:1px solid #acbfba;margin-top:28px;padding-top:16px}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d5dfdc;padding:7px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}.qualification{padding:16px;background:#fff2cf}code{overflow-wrap:anywhere}</style>',
              '<h1>SolderShape numerical review</h1>',
              '<p>This report works as a standalone HTML file. Its evidence links work only when it sits in the extracted accompanying evidence ZIP. The linked source, CSV, receipts and manifest are separate files, not embedded in this HTML.</p>',
              '<p class="qualification">'+text(record["qualification"])+"</p>",
              "<h2>"+text(record["headline"])+"</h2>", listing(record["facts"]),
              "<p>Footprint "+text(context["footprint_name"])+". Pad "+text(context["pad_identifier"])+".</p>",
              "<p>Source footprint SHA-256 <code>"+text(context["source_footprint_sha256"])+"</code>.</p>"]
    if "board_selection" in context:
        selection = context["board_selection"]
        pieces.append("<p>Board component "+text(selection.get("reference", ""))+". Pad "+text(selection.get("pad_identifier", ""))+". Board SHA-256 <code>"+text(selection.get("board_sha256", ""))+"</code>.</p>")
    for index, row in enumerate(record["rows"]):
        pieces.extend(["<section><h2>"+text(row["label"])+"</h2><p>"+text(row["headline"])+"</p>",
                       "<p>Numerical status <strong>"+text(row["numerical_status"])+"</strong>. Input SHA-256 <code>"+text(row["input_sha256"])+"</code>.</p>", listing(row["facts"]),
                       "<table><thead><tr><th>Declared input</th><th>Value</th></tr></thead><tbody>",
                       "".join("<tr><td>"+text(item["label"])+"</td><td>"+text(item["value"])+"</td></tr>" for item in row["inputs"]), "</tbody></table>"])
        if row["warnings"]:
            pieces.extend(["<h3>Model warnings</h3>", listing(row["warnings"])])
        if "error" in row:
            pieces.append("<p>Retained failure <strong>"+text(row["error"])+"</strong>.</p>")
        exact = {key: row[key] for key in ("input", "equilibrium", "forces", "load_balance") if key in row}
        pieces.extend(["<details><summary>Exact canonical values</summary><pre>"+text(json_bytes(exact).decode())+"</pre></details>",
                       f'<p>Links within the extracted evidence ZIP <a href="case-{index:02d}/input.json">input JSON</a> and <a href="case-{index:02d}/result.json">result JSON</a>.</p></section>'])
    command = "python3 tools/verify_board.py FILE.zip --replay" if "board_selection" in context else "python3 -m soldershape replay FILE.zip"
    pieces.extend(["<section><h2>Conventions</h2>", listing(record["convention"]), "<h2>Next steps</h2>", listing(record["next_steps"]),
                   '<h3>Links within the extracted accompanying evidence ZIP</h3><p><a href="results.csv">CSV</a>, <a href="source.kicad_mod">source footprint</a> and <a href="manifest.json">SHA-256 manifest</a>.</p>',
                   "<p>Replay <code>"+text(command)+"</code>. Archived scripts and this HTML are evidence; replay never executes them.</p></section></html>"])
    return ("\n".join(pieces)+"\n").encode()


def verify_review(archive, results, *, board_selection=None):
    names = set(archive.namelist())
    members = {"review.json", "review.html"}
    if not names & members:
        return
    if not members <= names or "source.kicad_mod" not in names:
        raise InputError("A source-bound review requires both review files and its source footprint.")
    comparison = json.loads(archive.read("comparison.json")) if "comparison.json" in names else None
    expected = review_record(results, comparison, source=archive.read("source.kicad_mod").decode(), board_selection=board_selection)
    saved = json.loads(archive.read("review.json"))
    if not isinstance(saved, dict):
        raise InputError("Invalid saved review.")
    for key in ("schema", "kind", "physical_qualification", "context", "comparison_status", "comparison_reason"):
        if saved.get(key) != expected.get(key):
            raise InputError("Archived review context differs from its numerical evidence.")
    rows = saved.get("rows")
    if not isinstance(rows, list) or len(rows) != len(expected["rows"]):
        raise InputError("Archived review rows differ from its numerical evidence.")
    canonical = ("label", "input_sha256", "numerical_status", "input", "equilibrium", "forces", "load_balance", "warnings", "error")
    for row, original in zip(rows, expected["rows"], strict=True):
        if not isinstance(row, dict) or any(row.get(key) != original.get(key) for key in canonical):
            raise InputError("Archived review row differs from its canonical numerical result.")



def make_bundle(results, source="", editable_case=None, comparison=None, *, board_selection=None):
    files = {"results.csv": results_csv(results)}
    if source:
        files["source.kicad_mod"] = source.encode()
        review = review_record(results, comparison, source=source, board_selection=board_selection)
        files["review.json"] = json_bytes(review)
        files["review.html"] = review_html(review)
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
            review_members = {"review.json", "review.html"} & set(names)
            if review_members and review_members != {"review.json", "review.html"}:
                raise InputError("A review requires both review files.")
            if manifest.get("board_schema") is None:
                verify_review(archive, [saved for _, saved in cases])
            return cases
    except (zipfile.BadZipFile, KeyError, ValueError, TypeError) as error:
        if isinstance(error, InputError):
            raise
        raise InputError("Invalid SolderShape bundle: " + str(error)) from error
