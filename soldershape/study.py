import csv
import hashlib
import html
import io
import json
import math
from pathlib import Path
import zipfile

from .artifacts import json_bytes, make_bundle, read_bundle
from .model import InputError, LoadSpec, request_from_footprint
from .solver import SolverError, solve
from . import model, solver

SCHEMA = "soldershape.study.v1"
REPORT_SCHEMA = "soldershape.study-report.v1"
CODE_FILES = ("model.py", "solver.py", "study.py")
LOADED_CODE_SHA256 = {"model.py": model.PYTHON_SOURCE_SHA256, "solver.py": solver.PYTHON_SOURCE_SHA256,
                      "study.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
SMALL_LOAD_FRACTION = .01
EQ9_SOURCE = "https://imapsjmep.org/article/39820.pdf"
SCOPE = [
    "Physical accuracy is unqualified. Numerical agreement does not validate real solder joints.",
    "Volume screening evaluates three finite samples. Their extrema are not continuous tolerance bounds, probabilities or yield estimates.",
    "The Eq. 9 approximation requires aligned circular pinned rims, gravity off, positive stiffness and compression no greater than one percent of unloaded height. The one-percent limit is a conservative software policy, not an experimentally validated error bound.",
    "A footprint does not resolve board-level mask settings, drawn mask geometry, finished CAM or wetting. Boundary evidence is a user declaration, not automatic verification.",
    "The reported gap lies between wetted pad faces. It is not package underbody clearance above solder mask.",
    "The normal load is per isolated joint. Equal load sharing, rigid parallel parts and identical joints are assumptions, not a package mechanics model.",
    "The two-pad cylinder hypothesis uses an equivalent liquid computational domain. Its mesh is not the measured physical solder shape.",
    "No result approves fabrication or qualifies thermal reflow, contact angles, wetting chemistry, solidification, fatigue or manufacturing yield.",
]


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _code_sources():
    return {name: (Path(__file__).parent / name).read_bytes() for name in CODE_FILES}


def _code_hashes(sources):
    return {name: hashlib.sha256(content).hexdigest() for name, content in sources.items()}


def _text(value, name, maximum=4000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise InputError(f"{name} needs a nonempty evidence or source declaration of at most {maximum} characters.")
    return value.strip()


def _number(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise InputError(f"{name} must be a finite number between {low} and {high}.")
    return float(value)


def _keys(value, expected, name):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise InputError(f"{name} must contain exactly {', '.join(expected)}.")


def read_study(data):
    _keys(data, ("schema", "reference", "candidate", "parameters", "requirement", "volume_fraction", "two_pad", "input_evidence"), "A study")
    if data["schema"] != SCHEMA:
        raise InputError("Unsupported study schema.")
    parameters = data["parameters"]
    if not isinstance(parameters, dict) or "lower_diameter_mm" in parameters or "standoff_mm" in parameters:
        raise InputError("A study uses a supported load. Each lower diameter comes from its own footprint.")
    arms = {}
    normalized_parameters = None
    for key in ("reference", "candidate"):
        arm = data[key]
        _keys(arm, ("footprint_text", "pad_index", "boundary_evidence"), key)
        boundary = _text(arm["boundary_evidence"], key + " boundary_evidence")
        spec, _ = request_from_footprint(arm["footprint_text"], arm["pad_index"], parameters)
        if not isinstance(spec, LoadSpec):
            raise InputError("Study parameters require normal_load_uN instead of a prescribed gap.")
        normalized_parameters = spec.to_dict()
        del normalized_parameters["lower_diameter_mm"]
        arms[key] = {"footprint_text": arm["footprint_text"], "pad_index": arm["pad_index"], "boundary_evidence": boundary}
    requirement = data["requirement"]
    _keys(requirement, ("pad_face_gap_um", "source"), "requirement")
    requirement = {"pad_face_gap_um": _number(requirement["pad_face_gap_um"], "pad_face_gap_um", 0, 10000),
                   "source": _text(requirement["source"], "requirement source")}
    fraction = _number(data["volume_fraction"], "volume_fraction", 0, .20)
    two_pad = data["two_pad"]
    if two_pad is not None:
        _keys(two_pad, ("lower_metal_um", "upper_metal_um", "evidence"), "two_pad")
        if normalized_parameters["gravity"]:
            raise InputError("The two-pad equivalent-volume hypothesis requires gravity off.")
        two_pad = {name: _number(two_pad[name], name, 0, 1000) for name in ("lower_metal_um", "upper_metal_um")}
        two_pad["evidence"] = _text(data["two_pad"]["evidence"], "two-pad evidence")
    result = {"schema": SCHEMA, **arms, "parameters": normalized_parameters, "requirement": requirement,
              "volume_fraction": fraction, "two_pad": two_pad, "input_evidence": _text(data["input_evidence"], "input_evidence")}
    for _, mapping, spec, _, _ in _requests(result):
        for factor in (1-fraction, 1+fraction):
            _request(result, spec.lower_diameter_mm, mapping, factor)
    return result


def _request(study, diameter, mapping, factor=1):
    parameters = {**study["parameters"], "lower_diameter_mm": diameter}
    parameters["volume_mm3"] *= factor
    correction = 0
    if mapping == "two_pad_cylinders":
        metal = study["two_pad"]
        for size, name in ((diameter, "lower_metal_um"), (parameters["upper_diameter_mm"], "upper_metal_um")):
            parameters["volume_mm3"] += math.pi*(size/2)**2*metal[name]/1000
            correction += metal[name]
    return LoadSpec.from_dict(parameters), correction


def _requests(study):
    mappings = ["literal_rims"] + (["two_pad_cylinders"] if study["two_pad"] is not None else [])
    for mapping in mappings:
        for key, design in (("reference", "Reference"), ("candidate", "Candidate")):
            arm = study[key]
            original, footprint = request_from_footprint(arm["footprint_text"], arm["pad_index"], study["parameters"])
            spec, correction = _request(study, original.lower_diameter_mm, mapping)
            yield design, mapping, spec, correction, footprint


def _analytical(spec, correction):
    if spec.offset_mm != 0 or spec.gravity:
        return {"gap_um": None, "eligible": False, "reason": "The analytical screen requires zero offset and gravity off."}
    a, b = spec.lower_diameter_mm/2, spec.upper_diameter_mm/2
    low, high = 0.0, (6*spec.volume_mm3/math.pi)**(1/3)
    for _ in range(80):
        height = (low+high)/2
        if math.pi*height*((a*a+b*b)/2+height*height/6) < spec.volume_mm3:
            low = height
        else:
            high = height
    height = (low+high)/2
    j = 1+height*height/(a*a+b*b)
    u = a*b/(a*a+b*b)
    denominator = j*j-4*u*u
    if denominator <= 0:
        return {"gap_um": None, "eligible": False, "reason": "The analytical stiffness is numerically singular for this geometry."}
    stiffness = spec.surface_tension_n_m*(4*math.pi/5)*j*(j*(j+4)+10*u*u)/denominator**1.5
    if not math.isfinite(stiffness) or stiffness <= 0:
        return {"gap_um": None, "eligible": False, "reason": "The analytical stiffness must be finite and positive."}
    compression_um = spec.normal_load_uN/stiffness
    compression_fraction = compression_um/(height*1000)
    eligible = stiffness > 0 and compression_fraction <= SMALL_LOAD_FRACTION
    gap = height*1000-compression_um-correction
    eligible = eligible and gap > 0
    reason = "Aligned Eq. 9 finite sample within the one-percent software policy." if eligible else "Eq. 9 exceeds the one-percent compression policy or gives a nonpositive pad-face gap."
    return {"gap_um": gap if eligible else None, "eligible": eligible, "reason": reason,
            "unloaded_domain_height_um": height*1000, "compression_fraction": compression_fraction, "stiffness_N_m": stiffness}


def _decision(study, results, samples, nominal):
    next_actions = ["Verify finished copper, mask openings and pinned wetting boundaries for both revisions.",
                    "Measure or justify liquid solder volume, per-joint load and material properties before using these planning inputs.",
                    "Run the controlled physical coupon pilot. Compare liquid-state measurements before claiming equilibrium accuracy."]
    if any(result["status"] != "refinement_checked" or result.get("pad_face_gap_um") is None for result in results):
        return {"status": "numerical_failure", "headline": "At least one nominal solve failed its numerical checks.",
                "reasons": ["Failed requests and their evidence are retained. No design conclusion is available."], "next_actions": next_actions}
    if any(result.get("model_warnings") for result in results):
        return {"status": "model_scope_inconclusive", "headline": "The solved geometry exceeds the checked model scope.",
                "reasons": [warning for result in results for warning in result.get("model_warnings", [])], "next_actions": next_actions}
    if any(not sample["eligible"] for sample in samples):
        return {"status": "sensitivity_unavailable", "headline": "The analytical volume screen is unavailable for these inputs.",
                "reasons": sorted({sample["reason"] for sample in samples if not sample["eligible"]}), "next_actions": next_actions}
    disagreed = [row for row in nominal if abs(row["native_minus_analytical_um"]) > max(.1, abs(row["native_gap_um"])*.001)]
    if disagreed:
        return {"status": "sensitivity_unavailable", "headline": "Native and analytical nominal gaps disagree beyond the software check.",
                "reasons": ["The agreement check is max(0.1 micrometer, 0.1 percent of native nominal gap). It is not a physical accuracy bound."], "next_actions": next_actions}
    threshold = study["requirement"]["pad_face_gap_um"]
    if any((row["native_gap_um"] >= threshold) != (row["analytical_gap_um"] >= threshold) for row in nominal):
        return {"status": "assumption_sensitive", "headline": "Native and analytical calculations disagree about the gap criterion.",
                "reasons": ["A nominal result lies too close to the criterion for the two numerical methods to support the same threshold answer. Small absolute agreement does not resolve that decision."],
                "next_actions": next_actions}
    for mapping in {row["mapping"] for row in nominal}:
        pair = {row["design"]: row for row in nominal if row["mapping"] == mapping}
        native_difference = pair["Candidate"]["native_gap_um"]-pair["Reference"]["native_gap_um"]
        analytical_difference = pair["Candidate"]["analytical_gap_um"]-pair["Reference"]["analytical_gap_um"]
        if native_difference*analytical_difference < 0 or (native_difference == 0) != (analytical_difference == 0):
            return {"status": "assumption_sensitive", "headline": "Native and analytical calculations disagree about revision ordering.",
                    "reasons": ["Small nominal differences do not support a consistent ordering between the two revisions."],
                    "next_actions": next_actions}
    changed = []
    for design in ("Reference", "Candidate"):
        signs = {sample["margin_um"] >= 0 for sample in samples if sample["design"] == design}
        if len(signs) > 1:
            changed.append(design)
    ranking = set()
    for mapping in {row["mapping"] for row in samples}:
        for point in ("low", "nominal", "high"):
            pair = {row["design"]: row["gap_um"] for row in samples if row["mapping"] == mapping and row["volume_sample"] == point}
            ranking.add(pair["Candidate"] >= pair["Reference"])
    if changed or len(ranking) > 1:
        reasons = []
        if changed:
            reasons.append("The declared pad-face-gap criterion changes sides across the sampled assumptions for " + " and ".join(changed) + ".")
        if len(ranking) > 1:
            reasons.append("The ordering of the two revisions changes across the sampled assumptions.")
        reasons.append("A board choice would depend on unverified geometry or volume assumptions. No physical pass follows.")
        return {"status": "assumption_sensitive", "headline": "The decision depends on the declared assumptions.", "reasons": reasons, "next_actions": next_actions}
    return {"status": "screened_samples", "headline": "The criterion and ordering stay unchanged at the sampled points.",
            "reasons": ["Only the declared endpoint and center samples were screened. This is not a continuous tolerance result or a qualified PCB design recommendation.",
                        "For aligned nominal gap alone, the analytical formula provides a sufficient baseline; a native solve does not establish extra physical accuracy."],
            "next_actions": next_actions}


def _report(study, results, code_hashes=None):
    samples, nominal = [], []
    threshold = study["requirement"]["pad_face_gap_um"]
    for (design, mapping, spec, correction, footprint), result in zip(_requests(study), results, strict=True):
        expected = {"design": design, "mapping": mapping, "input": spec.to_dict(), "input_sha256": spec.sha256, "footprint": footprint}
        if any(result.get(key) != value for key, value in expected.items()):
            raise InputError("A native result does not match the regenerated study request or source footprint.")
        gap = None
        if result["status"] == "refinement_checked":
            gap = result.get("equilibrium", {}).get("standoff_mm")
            if isinstance(gap, bool) or not isinstance(gap, (float, int)) or not math.isfinite(gap):
                raise InputError("A successful study result needs a finite solved height.")
            gap = gap*1000-correction
            if gap <= 0:
                gap = None
        result["pad_face_gap_um"] = gap
        result["mesh_scope"] = "Equivalent computational domain; not measured physical solder shape." if mapping == "two_pad_cylinders" else "Unqualified pinned-rim equilibrium computational domain."
        analytical = _analytical(spec, correction)
        analytic_gap = analytical["gap_um"]
        nominal.append({"design": design, "mapping": mapping, "lower_diameter_mm": spec.lower_diameter_mm,
                        "native_gap_um": gap, "analytical_gap_um": analytic_gap,
                        "native_minus_analytical_um": gap-analytic_gap if gap is not None and analytic_gap is not None else None,
                        "margin_um": gap-threshold if gap is not None else None, "status": result["status"]})
        for point, factor in (("low", 1-study["volume_fraction"]), ("nominal", 1), ("high", 1+study["volume_fraction"])):
            sampled, correction = _request(study, spec.lower_diameter_mm, mapping, factor)
            value = _analytical(sampled, correction)
            samples.append({"design": design, "mapping": mapping, "volume_mm3": study["parameters"]["volume_mm3"]*factor,
                            "volume_sample": point, "method": "analytical_eq9", **value,
                            "margin_um": value["gap_um"]-threshold if value["gap_um"] is not None else None})
    return {"schema": REPORT_SCHEMA, "study": study, "study_sha256": _digest(study), "physical_qualification": "unqualified",
            "calculation_code_sha256": dict(LOADED_CODE_SHA256) if code_hashes is None else code_hashes,
            "results": results, "decision": _decision(study, results, samples, nominal), "samples": samples, "nominal": nominal,
            "scope": list(SCOPE), "analytical_baseline": {"source": EQ9_SOURCE, "method": "Unloaded spherical segment plus published Eq. 9 axial stiffness.",
                                                    "formula": "V = pi*k*(p^2+q^2)/2 + pi*k^3/6; j = (k^2+p^2+q^2)/(p^2+q^2); u = p*q/(p^2+q^2); Kz = gamma*(4*pi/5)*j*(j*(j+4)+10*u^2)/(j^2-4*u^2)^(3/2); h = k-F/Kz.",
                                                    "units": "k,p,q,h in meters for dimensional formula; Kz in N/m; F in N. Code solves k in mm and converts compression from micronewtons to micrometers.",
                                                    "maximum_compression_fraction_policy": SMALL_LOAD_FRACTION,
                                                    "nominal_agreement_policy": "max(0.1 micrometer, 0.1 percent of native nominal gap). Software check only."}}


def run_study(data):
    study = read_study(data)
    code_hashes = dict(LOADED_CODE_SHA256)
    if code_hashes != _code_hashes(_code_sources()):
        raise InputError("Calculation files differ from the code loaded in this process. Restart SolderShape before computing.")
    results = []
    for design, mapping, spec, _, footprint in _requests(study):
        try:
            result = solve(spec)
        except SolverError as error:
            result = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": str(error), "evidence": error.evidence}
        results.append({**result, "design": design, "mapping": mapping, "footprint": footprint})
    if code_hashes != _code_hashes(_code_sources()):
        raise InputError("Calculation source changed during the study. Recompute before exporting a completed report.")
    return _report(study, results, code_hashes)


def _samples_csv(report):
    stream = io.StringIO(newline="")
    fields = ["design", "mapping", "volume_sample", "volume_mm3", "method", "gap_um", "margin_um", "eligible", "reason"]
    writer = csv.DictWriter(stream, fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(report["samples"])
    return stream.getvalue().encode()


def _decision_html(report):
    escape = lambda value: html.escape(str(value), quote=True)
    number = lambda value: "unavailable" if value is None else f"{value:.4f}"
    study, decision = report["study"], report["decision"]
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SolderShape decision brief</title>',
             '<style>body{font:16px system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #bbb;padding:.5rem;text-align:left}code{overflow-wrap:anywhere}h1{line-height:1.2}.notice{border:2px solid #985b00;padding:1rem}a{color:#164f91}@media print{body{max-width:none;font-size:10pt}table{font-size:8pt}tr{break-inside:avoid}}</style>',
             '<h1>SolderShape decision brief</h1><p class="notice"><strong>Physical qualification is unqualified.</strong> Numerical agreement does not validate real solder joints. This report does not approve fabrication.</p>',
             '<h2>'+escape(decision["headline"])+'</h2><p>Status <code>'+escape(decision["status"])+'</code>.</p><ul>']
    parts.extend('<li>'+escape(reason)+'</li>' for reason in decision["reasons"])
    parts.extend(['</ul><h2>Declared study question</h2><p>Minimum pad-face gap '+number(study["requirement"]["pad_face_gap_um"])+' micrometers.</p>',
                  '<p>'+escape(study["requirement"]["source"])+'</p><p>Input evidence '+escape(study["input_evidence"])+'.</p>',
                  '<h2>Source revisions and boundary evidence</h2><ul>'])
    for key in ("reference", "candidate"):
        parts.append('<li>'+escape(key.title())+' '+escape(study[key]["boundary_evidence"])+'. Footprint hash <code>'+escape(next(row["footprint"]["sha256"] for row in report["results"] if row["design"].lower() == key))+'</code>.</li>')
    parts.append('</ul><h2>Shared calculation inputs</h2><table><tr><th>Quantity</th><th>Value</th></tr>')
    labels = {"upper_diameter_mm": "Upper pad diameter, mm", "volume_mm3": "Liquid solder volume per joint, mm³",
              "normal_load_uN": "External supported load per joint, µN", "offset_mm": "Lateral offset, mm",
              "surface_tension_n_m": "Surface tension, N/m", "density_g_cm3": "Liquid density, g/cm³", "gravity": "Solder gravity enabled"}
    for key, label in labels.items():
        parts.append('<tr><td>'+escape(label)+'</td><td>'+escape(study["parameters"][key])+'</td></tr>')
    parts.append('<tr><td>Declared volume sample fraction</td><td>'+escape(study["volume_fraction"])+'</td></tr></table>')
    if study["two_pad"] is not None:
        metal = study["two_pad"]
        parts.append('<h2>Two-pad hypothesis inputs</h2><p>Lower finished metal '+escape(metal["lower_metal_um"])+' µm. Upper finished metal '+escape(metal["upper_metal_um"])+' µm.</p><p>'+escape(metal["evidence"])+'</p>')
    parts.append('<h2>Nominal computation</h2><p>The two-pad mesh is an equivalent computational domain. Its height is reduced by both metal thicknesses to report pad-face gap. It is not a measured solder shape.</p><table><thead><tr><th>Revision</th><th>Geometry hypothesis</th><th>Numerical status</th><th>Lower copper mm</th><th>Native gap µm</th><th>Eq. 9 gap µm</th><th>Difference µm</th><th>Margin µm</th></tr></thead><tbody>')
    for row in report["nominal"]:
        parts.append('<tr>'+''.join('<td>'+escape(value)+'</td>' for value in (row["design"], row["mapping"], row["status"], number(row["lower_diameter_mm"]), number(row["native_gap_um"]), number(row["analytical_gap_um"]), number(row["native_minus_analytical_um"]), number(row["margin_um"])))+'</tr>')
    parts.append('</tbody></table>')
    for result in report["results"]:
        if result.get("error"):
            parts.append('<p>'+escape(result["design"]+' / '+result["mapping"]+': '+result["error"])+'</p>')
    parts.append('<h2>Finite analytical volume samples</h2><p>These are three sampled values per arm and hypothesis. They are not a continuous uncertainty bound.</p><table><thead><tr><th>Revision</th><th>Hypothesis</th><th>Sample</th><th>Volume mm³</th><th>Gap µm</th><th>Margin µm</th><th>Eligible</th></tr></thead><tbody>')
    for row in report["samples"]:
        parts.append('<tr>'+''.join('<td>'+escape(value)+'</td>' for value in (row["design"], row["mapping"], row["volume_sample"], f'{row["volume_mm3"]:.9g}', number(row["gap_um"]), number(row["margin_um"]), row["eligible"]))+'</tr>')
    parts.append('</tbody></table><h2>Limits</h2><ul>')
    parts.extend('<li>'+escape(value)+'</li>' for value in report["scope"])
    parts.append('</ul><h2>Next actions</h2><ol>')
    parts.extend('<li>'+escape(value)+'</li>' for value in decision["next_actions"])
    parts.extend(['</ol><p>Study SHA-256 <code>'+escape(report["study_sha256"])+'</code>.</p>',
                  '<p>Analytical reference <a href="'+escape(EQ9_SOURCE)+'">published Eq. 9</a>. Archived engine scripts are evidence only. Replay regenerates requests and never executes archived scripts.</p></html>'])
    return ''.join(parts).encode()


def bundle_study(report):
    study = read_study(report.get("study"))
    regenerated = _report(study, json.loads(json.dumps(report.get("results"), allow_nan=False)))
    if report != regenerated:
        raise InputError("The report does not match its normalized study and regenerated conclusions.")
    sources = _code_sources()
    if _code_hashes(sources) != report["calculation_code_sha256"]:
        raise InputError("Calculation source changed after the report. Recompute before exporting.")
    with zipfile.ZipFile(io.BytesIO(make_bundle(report["results"]))) as archive:
        files = {name: archive.read(name) for name in archive.namelist() if name != "manifest.json"}
        manifest = json.loads(archive.read("manifest.json"))
    for index, result in enumerate(report["results"]):
        if result["mapping"] == "two_pad_cylinders":
            for suffix in ("obj", "stl"):
                original = f"case-{index:02d}/mesh-mm.{suffix}"
                if original in files:
                    files[f"case-{index:02d}/equivalent-domain-mm.{suffix}"] = files.pop(original)
    files.update({"study.json": json_bytes(study), "study-report.json": json_bytes(report), "decision.html": _decision_html(report),
                  "samples.csv": _samples_csv(report), "reference.kicad_mod": study["reference"]["footprint_text"].encode(),
                  "candidate.kicad_mod": study["candidate"]["footprint_text"].encode()})
    files.update({"calculation-source/"+name: content for name, content in sources.items()})
    manifest.update(study_schema=SCHEMA, study_sha256=report["study_sha256"],
                    replay="python3 -m soldershape replay FILE.zip; archived scripts are never executed",
                    files={name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())})
    files["manifest.json"] = json_bytes(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content)
    return buffer.getvalue()


def replay_study(path):
    try:
        cases = read_bundle(path)
        with zipfile.ZipFile(path) as archive:
            saved = json.loads(archive.read("study-report.json"))
            saved_sources = {name: archive.read("calculation-source/"+name) for name in CODE_FILES}
            if _code_hashes(saved_sources) != saved.get("calculation_code_sha256"):
                raise InputError("Archived calculation source does not match its recorded identity.")
            study = read_study(json.loads(archive.read("study.json")))
            if saved.get("study") != study or saved.get("study_sha256") != _digest(study):
                raise InputError("Saved study report does not match its normalized study.")
            results = []
            for index, (_, result) in enumerate(cases):
                result["evidence"] = json.loads(archive.read(f"case-{index:02d}/evidence.json"))
                results.append(result)
            expected = _report(study, results, saved["calculation_code_sha256"])
            if saved != expected:
                raise InputError("Saved study conclusions or samples do not match regenerated calculations.")
            for name, content in (("reference.kicad_mod", study["reference"]["footprint_text"].encode()),
                                  ("candidate.kicad_mod", study["candidate"]["footprint_text"].encode()),
                                  ("decision.html", _decision_html(saved)), ("samples.csv", _samples_csv(saved))):
                if archive.read(name) != content:
                    raise InputError("Saved study export does not match regenerated content for " + name)
        current = run_study(study)
        checks = []
        for previous, fresh in zip(saved["results"], current["results"], strict=True):
            passed = previous["status"] == fresh["status"] == "refinement_checked"
            gap_difference = None
            force_differences = None
            if passed:
                gap_difference = abs(fresh["pad_face_gap_um"]-previous["pad_face_gap_um"])
                force_differences = {axis: abs(fresh["forces"][axis]-previous["forces"][axis]) for axis in ("x_uN", "z_uN")}
                scale = fresh["input"]["surface_tension_n_m"]*fresh["input"]["lower_diameter_mm"]*500
                passed = gap_difference <= max(.01, abs(previous["pad_face_gap_um"])*.001) and all(
                    difference <= max(abs(previous["forces"][axis])*.01, scale*.0001) for axis, difference in force_differences.items())
                passed = passed and fresh.get("load_balance", {}).get("status") == previous.get("load_balance", {}).get("status") == "balanced"
            checks.append({"design": fresh["design"], "mapping": fresh["mapping"], "input_sha256": fresh["input_sha256"],
                           "previous_status": previous["status"], "current_status": fresh["status"], "gap_difference_um": gap_difference,
                           "force_difference_uN": force_differences,
                           "source_matches": bool(fresh.get("engine", {}).get("source_sha256")) and fresh.get("engine", {}).get("source_sha256") == previous.get("engine", {}).get("source_sha256"),
                           "binary_matches": bool(fresh.get("engine", {}).get("binary_sha256")) and fresh.get("engine", {}).get("binary_sha256") == previous.get("engine", {}).get("binary_sha256"),
                           "passed": passed})
        conclusion_matches = current["decision"] == saved["decision"] and current["samples"] == saved["samples"]
        return {"passed": all(row["passed"] for row in checks) and conclusion_matches, "integrity_verified": True,
                "verification_kind": "numerical_equivalence",
                "exact_engine_provenance": all(row["source_matches"] and row["binary_matches"] for row in checks),
                "calculation_source_matches": current["calculation_code_sha256"] == saved["calculation_code_sha256"],
                "requests_regenerated": True, "conclusion_matches": conclusion_matches, "checks": checks,
                "physical_qualification": "unqualified", "study_sha256": current["study_sha256"], "decision": current["decision"]}
    except (InputError, OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as error:
        return {"passed": False, "error": str(error), "physical_qualification": "unqualified"}
