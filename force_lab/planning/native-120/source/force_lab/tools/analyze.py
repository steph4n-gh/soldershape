#!/usr/bin/env python3
"""Independent prospective hot-joint force experiment and numerical planning."""

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "force_lab"
sys.path.insert(0, str(ROOT))
from soldershape.model import JointSpec, PYTHON_SOURCE_SHA256 as MODEL_SHA
from soldershape.solver import solve, engine_info, SolverError, PYTHON_SOURCE_SHA256 as SOLVER_SHA

FIELDS = ("lower_diameter_mm", "upper_diameter_mm", "standoff_mm", "offset_mm", "volume_mm3")
MATERIAL = ("surface_tension_n_m", "density_g_cm3")
PARAMETERS = FIELDS + MATERIAL
INPUT_COLUMNS = ("specimen_id",) + FIELDS + ("transverse_offset_mm", "transverse_U_mm", "measured_at_utc", "measurement_evidence")
OUTCOME_COLUMNS = ("specimen_id", "status", "corrected_force_uN", "measured_at_utc", "measurement_evidence", "wetting_boundary", "wetting_evidence", "stable", "stability_evidence", "actual_gap_mm", "actual_offset_mm", "actual_transverse_offset_mm", "actual_transverse_U_mm", "actual_temperature_C", "tilt_deg", "dwell_drift_um")
CODE = {"force_lab/tools/analyze.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "soldershape/model.py": MODEL_SHA, "soldershape/solver.py": SOLVER_SHA}
UNITS = {**dict.fromkeys(FIELDS, "mm"), "volume_mm3": "mm3", "surface_tension_n_m": "N/m", "density_g_cm3": "g/cm3"}
SNAPSHOT = ("inputs.csv", "metadata.json", "calibration.json", "input_covariance.json", "protocol.json", "allocation.csv")


class DataError(ValueError):
    pass


def digest(content):
    return hashlib.sha256(content).hexdigest()


def read_json(content):
    return json.loads(content, parse_constant=lambda value: (_ for _ in ()).throw(DataError("Nonfinite JSON is forbidden.")))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def code_hashes():
    if CODE != {name: digest((ROOT / name).read_bytes()) for name in CODE}:
        raise DataError("Loaded calculation code differs from disk. Restart Python.")
    return dict(CODE)


def utc(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as error:
        raise DataError("A recorded UTC ISO timestamp is required.") from error
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise DataError("Timestamps must use UTC.")
    return parsed


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise DataError(label + " requires a recorded value or independent evidence reference.")
    return value


def number(value, label, positive=False):
    if isinstance(value, bool) or value is None or str(value).strip() == "":
        raise DataError(label + " is required.")
    try:
        value = float(value)
    except (TypeError, ValueError) as error:
        raise DataError(label + " must be numeric.") from error
    if not math.isfinite(value) or (positive and value <= 0):
        raise DataError(label + " must be finite" + (" and positive." if positive else "."))
    return value


def csv_rows(content, columns):
    reader = csv.DictReader(io.StringIO(content.decode(), newline=""))
    if reader.fieldnames is None or len(set(reader.fieldnames)) != len(reader.fieldnames) or set(reader.fieldnames) != set(columns):
        raise DataError("CSV columns must match the template exactly.")
    rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise DataError("CSV has an extra or missing cell.")
    return rows


def save_csv(path, columns, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, columns)
        writer.writeheader()
        writer.writerows(rows)


def assignments():
    rows = []
    for block in range(1, 4):
        for axis in ("x", "z"):
            for offset in (40, 120):
                for pair in (1, 2):
                    volumes = (5, 7) if (block + pair + (axis == "z")) % 2 else (7, 5)
                    for sequence, volume in enumerate(volumes, 1):
                        pair_id = f"B{block}-{axis}-{offset}-P{pair}"
                        rows.append({"specimen_id": f"{pair_id}-V{volume}", "block": str(block), "axis": axis, "offset_mm": str(offset / 1000), "volume_mm3": str(volume / 1000), "pair_id": pair_id, "within_pair_sequence": str(sequence), "role": "confirmatory"})
    return rows


def allocation(content):
    columns = tuple(assignments()[0])
    actual = csv_rows(content, columns)
    if actual != assignments():
        raise DataError("Allocation differs from the fixed 48 independent-specimen protocol.")
    return actual


def templates(output):
    output = Path(output)
    if output.exists():
        raise DataError("Template directory must not exist.")
    output.mkdir(parents=True)
    assigned = assignments()
    save_csv(output / "inputs.csv", INPUT_COLUMNS, [{"specimen_id": row["specimen_id"]} for row in assigned])
    save_csv(output / "outcomes-template.csv", OUTCOME_COLUMNS, [{"specimen_id": row["specimen_id"], "status": "measurement_missing"} for row in assigned])
    evidence = {"value": None, "evidence": None}
    metadata = {key: None for key in ("lab", "alloy", "atmosphere", "oxide_removal", "temperature_C", "temperature_U_C", "liquidus_C", "coverage_factor", "coverage_justification", "process_evidence", "independent_input_evidence", "hot_commissioning_evidence", "sign_calibration_evidence", "contact_line_method_evidence", "input_observed_at_utc", "cross_domain_independence_evidence")}
    metadata.update(surface_tension_n_m=dict(evidence), density_g_cm3=dict(evidence), commissioning_passed=None, inputs_independent_of_forces=None, unlinked_sources_independent=None, gravity_orientation="horizontal pads; gravity is -z", interface="solder/gas; pinned circular rims")
    write_json(output / "metadata.json", metadata)
    variables = [row["specimen_id"] + "." + field for row in assigned for field in FIELDS] + ["metadata." + field for field in MATERIAL]
    components = [{"id": key, "standard_u": None, "source_unit": UNITS[key.rsplit('.', 1)[1]], "evidence": None, "coefficients": {key: 1}} for key in variables]
    write_json(output / "input_covariance.json", {"kind": "standard_uncertainty_source_components", "budget_complete": None, "completeness_evidence": None, "components": components, "instructions": "Each independent physical source has one ID, source unit, standard uncertainty and signed coefficients. Use the same ID, unit and standard uncertainty in calibration.json when that source also affects corrected force. Coefficients convert source units into each affected variable's units. Replace independent entries when sharing is known. Unknown covariance is not independence."})
    write_json(output / "calibration.json", {"kind": "standard_force_uncertainty_source_components", "budget_complete": None, "completeness_evidence": None, "coverage_factor": None, "coverage_justification": None, "components": [{"id": row["specimen_id"], "standard_u": None, "source_unit": "uN", "evidence": None, "coefficients": {row["specimen_id"]: 1}} for row in assigned], "instructions": "Coefficients convert the named source unit into uN. Include assembled transfer calibration, hot zero, repeatability, residual cross-axis/torque, tare and compliance. Shared sources use the same ID, unit and standard uncertainty in both budgets. Certify independence of differently named sources with metadata evidence. No sqrt(n) reduction of shared terms."})
    for name in ("raw-timeseries.csv", "transfer-calibration.csv", "hot-blanks.csv"):
        (output / name).write_bytes((LAB / "templates" / name).read_bytes())
    return {"directory": str(output), "specimens": len(assigned), "status": "BLANK_PHYSICAL_DATA"}


def components(data, variables, label):
    if data.get("budget_complete") is not True:
        raise DataError(label + " budget is unknown or incomplete.")
    text(data.get("completeness_evidence"), label + " completeness")
    result, seen, variances = [], set(), dict.fromkeys(variables, 0.0)
    for item in data.get("components", []):
        if set(item) != {"id", "standard_u", "source_unit", "evidence", "coefficients"}:
            raise DataError(label + " component fields must match the template.")
        identifier = text(item["id"], "source id")
        if identifier in seen:
            raise DataError("Duplicate uncertainty source id.")
        seen.add(identifier)
        u = number(item["standard_u"], identifier + " standard uncertainty", positive=True)
        unit = text(item["source_unit"], identifier + " source unit")
        text(item["evidence"], identifier + " evidence")
        coeff = item["coefficients"]
        if not isinstance(coeff, dict) or not coeff or set(coeff) - set(variables):
            raise DataError(label + " coefficients contain missing or unknown variables.")
        coefficients = {key: number(value, key + " coefficient") for key, value in coeff.items()}
        if not any(coefficients.values()):
            raise DataError("An uncertainty source cannot have only zero coefficients.")
        for key, value in coefficients.items():
            variances[key] += (u * value) ** 2
        result.append({"id": identifier, "standard_u": u, "source_unit": unit, "coefficients": coefficients})
    if not result or any(value <= 0 for value in variances.values()):
        raise DataError(label + " needs quantified positive uncertainty for every variable.")
    return result, variances


def variance(weights, sources):
    return sum((source["standard_u"] * sum(weights.get(key, 0) * value for key, value in source["coefficients"].items())) ** 2 for source in sources)


def residual_variance(force_weights, input_weights, force_sources, input_sources):
    projections = {}
    for sign, weights, sources in ((1, force_weights, force_sources), (-1, input_weights, input_sources)):
        for source in sources:
            projections[source["id"]] = projections.get(source["id"], 0) + sign * source["standard_u"] * sum(weights.get(key, 0) * value for key, value in source["coefficients"].items())
    return sum(value ** 2 for value in projections.values())


def validate(snapshots):
    protocol = read_json(snapshots["protocol.json"])
    assigned = allocation(snapshots["allocation.csv"])
    rows = csv_rows(snapshots["inputs.csv"], INPUT_COLUMNS)
    identifiers = {row["specimen_id"] for row in assigned}
    if len(rows) != len(identifiers) or {row["specimen_id"] for row in rows} != identifiers:
        raise DataError("Each allocated independent specimen is required exactly once.")
    metadata = read_json(snapshots["metadata.json"])
    expected = set(read_json((LAB / "templates" / "metadata.json").read_bytes()))
    if set(metadata) != expected:
        raise DataError("Metadata must match the template and cannot contain outcomes.")
    for key in expected - set(MATERIAL) - {"temperature_C", "temperature_U_C", "liquidus_C", "coverage_factor", "commissioning_passed", "inputs_independent_of_forces", "unlinked_sources_independent"}:
        text(metadata[key], key)
    if metadata["commissioning_passed"] is not True or metadata["inputs_independent_of_forces"] is not True:
        raise DataError("Independently observed inputs and passed hot commissioning are required.")
    if metadata["unlinked_sources_independent"] is not True:
        raise DataError("Unknown cross-domain covariance cannot be treated as independence. Identify shared sources and independently justify unlinked-source independence.")
    if metadata["gravity_orientation"] != "horizontal pads; gravity is -z" or metadata["interface"] != "solder/gas; pinned circular rims":
        raise DataError("Actual gravity or interface differs from the fixed-rim model.")
    for key in ("temperature_C", "temperature_U_C", "liquidus_C", "coverage_factor"):
        metadata[key] = number(metadata[key], key, positive=key in ("temperature_U_C", "coverage_factor"))
    if metadata["coverage_factor"] != 2 or metadata["temperature_C"] - metadata["temperature_U_C"] <= metadata["liquidus_C"]:
        raise DataError("Document k=2 coverage and an entirely molten temperature interval.")
    now = datetime.now(timezone.utc)
    if utc(metadata["input_observed_at_utc"]) > now:
        raise DataError("Input observation is in the future.")
    for field in MATERIAL:
        if not isinstance(metadata[field], dict) or set(metadata[field]) != {"value", "evidence"}:
            raise DataError(field + " needs an independent value and evidence.")
        metadata[field]["value"] = number(metadata[field]["value"], field, positive=True)
        text(metadata[field]["evidence"], field + " independent evidence")
    inputs = {}
    for row in rows:
        specimen = row["specimen_id"]
        for field in FIELDS:
            row[field] = number(row[field], specimen + " " + field, positive=True)
        row["transverse_offset_mm"] = number(row["transverse_offset_mm"], specimen + " transverse offset")
        row["transverse_U_mm"] = number(row["transverse_U_mm"], specimen + " transverse expanded uncertainty", positive=True)
        if abs(row["transverse_offset_mm"]) + row["transverse_U_mm"] > protocol["gates"]["max_transverse_bound_mm"]:
            raise DataError("Transverse displacement plus expanded uncertainty exceeds the apparatus-domain bound.")
        text(row["measurement_evidence"], "independent geometry/volume evidence")
        if utc(row["measured_at_utc"]) > now:
            raise DataError("Input measurement is in the future.")
        inputs[specimen] = row
    variables = [key + "." + field for key in inputs for field in FIELDS] + ["metadata." + field for field in MATERIAL]
    input_sources, input_variances = components(read_json(snapshots["input_covariance.json"]), variables, "input")
    calibration = read_json(snapshots["calibration.json"])
    force_sources, force_variances = components(calibration, identifiers, "force")
    source_identities = {source["id"]: (source["standard_u"], source["source_unit"]) for source in input_sources}
    for source in force_sources:
        if source["id"] in source_identities and source_identities[source["id"]] != (source["standard_u"], source["source_unit"]):
            raise DataError("Shared uncertainty source has inconsistent standard uncertainty or source unit.")
    if number(calibration.get("coverage_factor"), "force coverage factor") != 2:
        raise DataError("This revision requires justified k=2 force coverage.")
    text(calibration.get("coverage_justification"), "force coverage justification")
    for row in assigned:
        incoming = inputs[row["specimen_id"]]
        targets = {"lower_diameter_mm": .2, "upper_diameter_mm": .2, "standoff_mm": .15, "offset_mm": float(row["offset_mm"]), "volume_mm3": float(row["volume_mm3"])}
        for field, target in targets.items():
            if abs(incoming[field] - target) > .02 * target:
                raise DataError("Measured geometry/volume left this protocol's nominal 2 percent design window.")
    for filename in ("calibration.json", "input_covariance.json"):
        if set(read_json(snapshots[filename])) != set(read_json((LAB / "templates" / filename).read_bytes())):
            raise DataError(filename + " fields must match the template and cannot contain outcomes.")
    for key, var in input_variances.items():
        owner, field = key.rsplit(".", 1)
        value = metadata[field]["value"] if owner == "metadata" else inputs[owner][field]
        if 2 * math.sqrt(var) > protocol["gates"]["max_input_relative_U"] * abs(value):
            raise DataError("Input uncertainty exceeds the local 2 percent relative-U screen for " + key + ". Reduce uncertainty or redesign and register a broader numerical analysis.")
    if any(2 * math.sqrt(value) > protocol["gates"]["max_individual_force_U_uN"] for value in force_variances.values()):
        raise DataError("Commissioned individual force uncertainty exceeds 2 uN.")
    return protocol, assigned, inputs, metadata, input_sources, force_sources, input_variances


def request(row, metadata):
    return JointSpec(**{field: row[field] for field in FIELDS}, **{field: metadata[field]["value"] for field in MATERIAL}, gravity=True)


def native(spec, cache, output):
    if spec.sha256 not in cache:
        try:
            result = solve(spec)
        except SolverError as error:
            result = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": str(error), "evidence": error.evidence}
        path = output / "receipts" / (spec.sha256 + ".json.gz")
        path.parent.mkdir(exist_ok=True)
        with gzip.open(path, "wt") as stream:
            json.dump(result, stream, allow_nan=False)
        cache[spec.sha256] = result
    return cache[spec.sha256]


def receipt_engine(result, archived_engine):
    if not isinstance(archived_engine, dict) or not isinstance(archived_engine.get("ready"), bool):
        raise DataError("Archived engine identity is missing or malformed.")
    if "engine" in result:
        if result["engine"] != archived_engine:
            raise DataError("Native receipt engine contradicts the archived engine identity.")
    elif result.get("status") != "failed":
        raise DataError("A completed native receipt requires its archived engine identity.")


def qualified(result):
    return result["status"] == "refinement_checked" and not result.get("model_warnings")


def prediction_from_receipts(spec, protocol, fetch, uncertainty=None, full=False):
    central = fetch(spec)
    result = {"request": spec.to_dict(), "request_sha256": spec.sha256, "status": central["status"], "model_warnings": central.get("model_warnings", []), "forces_uN": central.get("forces"), "refinement_changes_uN": {axis: central.get("diagnostics", {}).get("force_component_changes", {}).get(axis, {}).get("absolute_uN") for axis in ("x", "z")}, "jacobian": {}, "sensitivity_checks": [], "eligible": qualified(central)}
    for field in PARAMETERS:
        step = max(protocol["local_steps"][field], 2 * math.sqrt((uncertainty or {}).get(field, 0)))
        signs = (-1, 1) if full or field in ("standoff_mm", "volume_mm3") else (0, 1)
        shifted = [central if sign == 0 else fetch(JointSpec(**{**spec.to_dict(), field: getattr(spec, field) + sign * step})) for sign in signs]
        good = qualified(central) and all(qualified(value) for value in shifted)
        result["eligible"] = result["eligible"] and good
        check = {"parameter": field, "step": step, "scheme": "central" if signs[0] == -1 else "forward", "request_sha256": [value["input_sha256"] for value in shifted], "statuses": [value["status"] for value in shifted], "qualified": good}
        if good:
            result["jacobian"][field] = {axis: (shifted[1]["forces"][axis + "_uN"] - shifted[0]["forces"][axis + "_uN"]) / ((signs[1] - signs[0]) * step) for axis in ("x", "z")}
            check["midpoint_nonlinearity_uN"] = {axis: abs((shifted[0]["forces"][axis + "_uN"] + shifted[1]["forces"][axis + "_uN"]) / 2 - central["forces"][axis + "_uN"]) if signs[0] == -1 else None for axis in ("x", "z")}
            check["force_change_uN"] = {axis: shifted[1]["forces"][axis + "_uN"] - shifted[0]["forces"][axis + "_uN"] for axis in ("x", "z")}
            check["numerical_change_floor_uN"] = {axis: sum(value["diagnostics"]["force_component_changes"][axis]["absolute_uN"] for value in shifted) for axis in ("x", "z")}
            check["resolved_force_change"] = {axis: abs(check["force_change_uN"][axis]) > check["numerical_change_floor_uN"][axis] for axis in ("x", "z")}
        result["sensitivity_checks"].append(check)
    return result


def prediction(spec, protocol, cache, output, uncertainty=None, full=False):
    return prediction_from_receipts(spec, protocol, lambda value: native(value, cache, output), uncertainty, full)


def planning_derivation(cases, protocol):
    report = {}
    measurement_U = protocol["gates"]["max_individual_force_U_uN"]
    normal_prediction_U = math.sqrt(max(0, protocol["gates"]["max_normal_combined_guard_uN"] ** 2 - measurement_U ** 2))
    if all(case["eligible"] for case in cases):
        delta = cases[1]["forces_uN"]["x_uN"] - cases[0]["forces_uN"]["x_uN"]
        target = abs(delta) / protocol["gates"]["min_contrast_to_combined_guard"]
        prediction_U = math.sqrt(max(0, target ** 2 - 2 * protocol["gates"]["max_individual_force_U_uN"] ** 2))
        one_source = {}
        for field in PARAMETERS:
            j5, j7 = cases[0]["jacobian"][field]["x"], cases[1]["jacobian"][field]["x"]
            z7 = abs(cases[1]["jacobian"][field]["z"])
            checks = [next(check for check in case["sensitivity_checks"] if check["parameter"] == field) for case in cases]
            resolved_x = all(check["resolved_force_change"]["x"] for check in checks)
            shared_change = checks[1]["force_change_uN"]["x"] - checks[0]["force_change_uN"]["x"]
            shared_resolved = resolved_x and abs(shared_change) > sum(check["numerical_change_floor_uN"]["x"] for check in checks)
            resolved_z = checks[1]["resolved_force_change"]["z"]
            contrast_domain = protocol["gates"]["max_input_relative_U"] * min(case["request"][field] for case in cases)
            normal_domain = protocol["gates"]["max_input_relative_U"] * cases[1]["request"][field]
            def limit(budget, denominator, resolved, domain):
                candidate = budget / denominator if denominator and resolved else None
                return candidate if candidate is not None and candidate <= domain else None
            one_source[field] = {"contrast_max_expanded_U_if_fully_shared": limit(prediction_U, abs(j7 - j5), shared_resolved, contrast_domain), "contrast_max_each_expanded_U_if_independent_equal": limit(prediction_U, math.hypot(j5, j7), resolved_x, contrast_domain), "normal_7nL_max_expanded_U_if_only_source": limit(normal_prediction_U, z7, resolved_z, normal_domain), "resolution": {"shared_contrast": shared_resolved, "independent_contrast": resolved_x, "normal_7nL": resolved_z}, "max_expanded_U_within_registered_local_domain": {"contrast": contrast_domain, "normal_7nL": normal_domain}, "null_limit_explanation": "Null means the finite force change is unresolved above the saved refinement floor, or its algebraic budget crossing lies outside the protocol's 2 percent relative-U domain. Retain the raw Jacobian, but do not infer an allowable input tolerance."}
        report["planning_targets"] = {"lateral_contrast_uN": delta, "normal_7nL_uN": cases[1]["forces_uN"]["z_uN"], "max_combined_contrast_guard_uN": target, "max_prediction_contrast_U_with_two_independent_measured_U2_uN": prediction_U, "max_prediction_normal_U_with_measurement_U2_uN": normal_prediction_U, "one_source_at_a_time_limits": one_source, "warning": "Each limit spends the entire input budget on one source. They are not simultaneous tolerances, ignore numerical/discrepancy allowance, and are not measured capability. Shared and independent limits differ because covariance matters."}
        scenarios = {}
        for name, supplied in {
            "initial_budget_negative_control": {"lower_diameter_mm": .0005, "upper_diameter_mm": .0005, "standoff_mm": .0005, "offset_mm": .0005, "volume_mm3": .0001, "surface_tension_n_m": .0048, "density_g_cm3": .09},
            "tighter_budget_candidate_unmeasured": {"lower_diameter_mm": .00025, "upper_diameter_mm": .00025, "standoff_mm": .00025, "offset_mm": .0005, "volume_mm3": .00002, "surface_tension_n_m": .0048, "density_g_cm3": .09},
        }.items():
            contrast_variance, normal_variance = 0.0, 0.0
            for field, U in supplied.items():
                j5, j7 = cases[0]["jacobian"][field]["x"], cases[1]["jacobian"][field]["x"]
                contrast_variance += ((j7 - j5) * U) ** 2 if field in MATERIAL else (j5 * U) ** 2 + (j7 * U) ** 2
                normal_variance += (cases[1]["jacobian"][field]["z"] * U) ** 2
            numerical = {axis: sum(case["refinement_changes_uN"][axis] + sum(check["midpoint_nonlinearity_uN"][axis] or 0 for check in case["sensitivity_checks"]) for case in cases) for axis in ("x", "z")}
            normal_numeric = cases[1]["refinement_changes_uN"]["z"] + sum(check["midpoint_nonlinearity_uN"]["z"] or 0 for check in cases[1]["sensitivity_checks"])
            contrast_guard = math.sqrt(contrast_variance + 2 * measurement_U ** 2) + numerical["x"]
            normal_guard = math.sqrt(normal_variance + measurement_U ** 2) + normal_numeric
            scenarios[name] = {"kind": "UNMEASURED_ALLOCATION_NOT_INSTRUMENT_CAPABILITY", "expanded_input_U": supplied, "coverage_factor": 2, "covariance_assumptions": "Geometry and volume independent between specimens and inputs; gamma and density fully shared between volumes; all source groups otherwise independent. No ensemble averaging.", "lateral_contrast_input_U_uN": math.sqrt(contrast_variance), "normal_7nL_input_U_uN": math.sqrt(normal_variance), "lateral_contrast_measurement_U_uN": math.sqrt(2) * measurement_U, "normal_measurement_U_uN": measurement_U, "contrast_numerical_guard_uN": numerical["x"], "normal_numerical_guard_uN": normal_numeric, "contrast_combined_decision_guard_uN": contrast_guard, "normal_combined_decision_guard_uN": normal_guard, "contrast_gate_passes_local_screen": contrast_guard <= target, "normal_gate_passes_local_screen": normal_guard <= protocol["gates"]["max_normal_combined_guard_uN"] and abs(cases[1]["forces_uN"]["z_uN"]) > math.sqrt(normal_variance) + normal_numeric, "scope": "First-order planning only. Numerical guard adds observed refinement changes and central-step midpoint nonlinearities. Forward-step nonlinearities, mixed interactions, hysteresis and physical discrepancy are unbounded. A passed allocation still needs measured capability and a fresh full-central physical freeze."}
        report["planning_budget_scenarios"] = scenarios
    return report


def planning_report(cases, protocol, hashes, engine, count):
    return {"kind": "UNQUALIFIED_PLANNING_NOT_FROZEN_PHYSICAL_PREDICTIONS", "warning": "Example gamma and density do not identify an alloy or temperature. Local finite differences are numerical sensitivity, not physical validation or an uncertainty bound.", "code_sha256": hashes, "engine": engine, "protocol_sha256": digest((LAB / "protocol.json").read_bytes()), "cases": cases, "distinct_native_requests": count, "input_units": UNITS, **planning_derivation(cases, protocol)}


def plan(output):
    output = Path(output)
    if output.exists():
        raise DataError("Planning output must not exist.")
    hashes = code_hashes()
    output.mkdir(parents=True)
    protocol = read_json((LAB / "protocol.json").read_bytes())
    cache, cases = {}, []
    for volume in (.005, .007):
        cases.append(prediction(JointSpec(**protocol["planning_inputs_only"], volume_mm3=volume), protocol, cache, output))
    report = planning_report(cases, protocol, hashes, engine_info(), len(cache))
    if hashes != code_hashes():
        raise DataError("Code changed during planning. Preserve partial receipts and restart.")
    for name in (*hashes, "force_lab/protocol.json"):
        path = output / "source" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    report["files"] = {str(path.relative_to(output)): digest(path.read_bytes()) for path in output.rglob("*") if path.is_file()}
    write_json(output / "plan.json", report)
    return report


def freeze(source, output):
    source, output = Path(source), Path(output)
    if output.exists():
        raise DataError("Freeze output must not exist.")
    if (source / "outcomes.csv").exists():
        raise DataError("Confirmation outcomes must not exist at freeze. Keep the blank template separate.")
    hashes = code_hashes()
    snapshots = {name: (source / name).read_bytes() for name in SNAPSHOT[:4]}
    snapshots.update({name: (LAB / name).read_bytes() for name in SNAPSHOT[4:]})
    protocol, assigned, inputs, metadata, _, _, variances = validate(snapshots)
    output.mkdir(parents=True)
    for name, content in snapshots.items():
        (output / name).write_bytes(content)
    cache, predicted = {}, {}
    for row in assigned:
        specimen = row["specimen_id"]
        uncertainty = {field: variances[("metadata" if field in MATERIAL else specimen) + "." + field] for field in PARAMETERS}
        predicted[specimen] = prediction(request(inputs[specimen], metadata), protocol, cache, output, uncertainty, full=True)
    write_json(output / "predictions.json", {"kind": "PROSPECTIVE_PHYSICAL_INPUT_PREDICTIONS", "specimens": predicted, "scope": "Central native forces with local first-order uncertainty sensitivities. No force outcomes supplied or fitted."})
    if hashes != code_hashes() or (source / "outcomes.csv").exists():
        raise DataError("Code changed or outcomes appeared during freeze. Partial receipts retained without a manifest.")
    for name in SNAPSHOT:
        if (output / name).read_bytes() != snapshots[name]:
            raise DataError("Snapshot changed during freeze.")
    for name in SNAPSHOT[4:]:
        if (LAB / name).read_bytes() != snapshots[name]:
            raise DataError("Protocol or allocation changed during freeze.")
    files = {str(path.relative_to(output)): digest(path.read_bytes()) for path in output.rglob("*") if path.is_file()}
    manifest = {"schema": "soldershape.force-freeze.v2", "frozen_at_utc": datetime.now(timezone.utc).isoformat(), "files": files, "code_sha256": hashes, "engine": engine_info(), "distinct_native_requests": len(cache), "eligible_native_predictions": sum(value["eligible"] for value in predicted.values()), "specimens": len(predicted)}
    write_json(output / "manifest.json", manifest)
    return {**manifest, "manifest_sha256": digest((output / "manifest.json").read_bytes()), "instruction": "Register this manifest digest independently with the lab before acquiring confirmation outcomes. Failed native predictions remain preserved and cannot support endpoint agreement."}


def frozen(directory, expected_sha):
    directory = Path(directory)
    code_hashes()
    manifest_bytes = (directory / "manifest.json").read_bytes()
    if digest(manifest_bytes) != expected_sha:
        raise DataError("Manifest does not match the independently registered SHA-256.")
    manifest = read_json(manifest_bytes)
    if manifest.get("schema") != "soldershape.force-freeze.v2" or manifest.get("code_sha256") != CODE:
        raise DataError("Frozen schema or loaded source differs.")
    actual = {str(path.relative_to(directory)) for path in directory.rglob("*") if path.is_file()}
    if actual != set(manifest["files"]) | {"manifest.json"}:
        raise DataError("Frozen directory member set changed.")
    snapshot = {}
    for name, sha in manifest["files"].items():
        path = directory / name
        if path.is_symlink() or directory.resolve() not in path.resolve().parents:
            raise DataError("Unsafe frozen path.")
        content = path.read_bytes()
        if digest(content) != sha:
            raise DataError("Frozen bytes changed for " + name + ".")
        snapshot[name] = content
        if name.startswith("receipts/") and name.endswith(".json.gz"):
            receipt_engine(read_json(gzip.decompress(content)), manifest.get("engine"))
    for name in SNAPSHOT[4:]:
        if (LAB / name).read_bytes() != snapshot[name]:
            raise DataError("Current protocol or allocation differs from freeze.")
    return manifest, snapshot


def endpoint(weights, axis, inputs, metadata, predicted, observed, input_sources, force_sources, protocol):
    issues, input_weights = [], {}
    predicted_value, measured_value, numerical_guard = 0.0, 0.0, 0.0
    individual_disagreements = []
    for specimen, weight in weights.items():
        item, observation = predicted[specimen], observed.get(specimen)
        if not item["eligible"]:
            issues.append(specimen + " numerical or scope failure")
            continue
        predicted_value += weight * item["forces_uN"][axis + "_uN"]
        numerical_guard += abs(weight) * item["refinement_changes_uN"][axis]
        numerical_guard += abs(weight) * sum(check["midpoint_nonlinearity_uN"].get(axis, 0) or 0 for check in item["sensitivity_checks"])
        for field in PARAMETERS:
            key = ("metadata" if field in MATERIAL else specimen) + "." + field
            input_weights[key] = input_weights.get(key, 0) + weight * item["jacobian"][field][axis]
        if observation is None or observation["status"] != "measured":
            issues.append(specimen + " missing/failed physical observation")
            continue
        if observation["wetting_boundary"] != "pinned_both" or observation["stable"] != "true":
            issues.append(specimen + " unknown/failed wetting or equilibrium")
        row = inputs[specimen]
        for field, actual in (("standoff_mm", "actual_gap_mm"), ("offset_mm", "actual_offset_mm")):
            u = math.sqrt(variance({specimen + "." + field: 1}, input_sources))
            if abs(observation[actual] - row[field]) > 2 * u:
                issues.append(specimen + " actual coordinates left frozen input interval")
        if abs(observation["actual_temperature_C"] - metadata["temperature_C"]) > metadata["temperature_U_C"]:
            issues.append(specimen + " temperature left frozen interval")
        transverse, transverse_U = observation["actual_transverse_offset_mm"], observation["actual_transverse_U_mm"]
        if transverse is None or transverse_U is None or abs(transverse) + transverse_U > protocol["gates"]["max_transverse_bound_mm"]:
            issues.append(specimen + " transverse alignment unobserved or outside apparatus-domain bound")
        if abs(observation["tilt_deg"]) > protocol["gates"]["max_tilt_deg"] or observation["dwell_drift_um"] > protocol["gates"]["max_drift_um"]:
            issues.append(specimen + " excessive tilt or dwell drift")
        measured_value += weight * observation["corrected_force_uN"]
        local_input_weights = {("metadata" if field in MATERIAL else specimen) + "." + field: item["jacobian"][field][axis] for field in PARAMETERS}
        local_guard = 2 * math.sqrt(residual_variance({specimen: 1}, local_input_weights, force_sources, input_sources)) + item["refinement_changes_uN"][axis]
        local_guard += sum(check["midpoint_nonlinearity_uN"].get(axis, 0) or 0 for check in item["sensitivity_checks"])
        if abs(observation["corrected_force_uN"] - item["forces_uN"][axis + "_uN"]) > local_guard:
            individual_disagreements.append(specimen)
    input_U = 2 * math.sqrt(variance(input_weights, input_sources))
    measurement_U = 2 * math.sqrt(variance(weights, force_sources))
    residual_U = 2 * math.sqrt(residual_variance(weights, input_weights, force_sources, input_sources))
    combined = residual_U + numerical_guard
    return {"predicted_uN": predicted_value, "observed_uN": measured_value if not issues else None, "input_first_order_U_uN": input_U, "measurement_U_uN": measurement_U, "residual_first_order_U_uN": residual_U, "numerical_and_one_at_a_time_nonlinearity_guard_uN": numerical_guard, "combined_decision_guard_uN": combined, "issues": issues, "status": "inconclusive" if issues else "agreement_within_declared_guard" if abs(measured_value - predicted_value) <= combined else "disagreement_exceeds_declared_guard", "independent_specimens": len(weights), "individual_disagreements": individual_disagreements}


def score(directory, outcomes, output, expected_sha):
    output = Path(output)
    if output.exists():
        raise DataError("Score output must not exist.")
    manifest, snapshots = frozen(directory, expected_sha)
    protocol, assigned, inputs, metadata, input_sources, force_sources, _ = validate(snapshots)
    content = Path(outcomes).read_bytes()
    rows = csv_rows(content, OUTCOME_COLUMNS)
    observed = {}
    by_id = {row["specimen_id"]: row for row in assigned}
    for row in rows:
        specimen = row["specimen_id"]
        if specimen not in by_id or specimen in observed:
            raise DataError("Unknown or duplicate outcome specimen. Dwell repeats do not increase n.")
        if row["status"] not in ("measured", "measurement_missing", "assembly_failed", "out_of_domain"):
            raise DataError("Unknown outcome status.")
        if row["status"] == "measured":
            for field in ("corrected_force_uN", "actual_gap_mm", "actual_offset_mm", "actual_temperature_C", "tilt_deg", "dwell_drift_um"):
                row[field] = number(row[field], field)
            for field in ("actual_transverse_offset_mm", "actual_transverse_U_mm"):
                row[field] = number(row[field], field, positive=field == "actual_transverse_U_mm") if str(row[field]).strip() else None
            if row["actual_gap_mm"] <= 0 or row["dwell_drift_um"] < 0:
                raise DataError("Gap must be positive and drift nonnegative.")
            for field in ("measurement_evidence", "wetting_evidence", "stability_evidence"):
                text(row[field], field)
            if row["wetting_boundary"] not in ("pinned_both", "failed", "unobserved") or row["stable"] not in ("true", "false", "unknown"):
                raise DataError("Wetting and stability must be explicitly observed or unknown.")
            observed_at = utc(row["measured_at_utc"])
            if not utc(manifest["frozen_at_utc"]) < observed_at <= datetime.now(timezone.utc):
                raise DataError("Confirmation measurements must follow freeze and cannot be future dated.")
        elif row["corrected_force_uN"].strip():
            raise DataError("Unmeasured outcomes cannot contain forces.")
        observed[specimen] = row
    predicted = read_json(snapshots["predictions.json"])["specimens"]
    endpoints, block_assessments, absolute_lateral = [], [], []
    for offset in (.04, .12):
        group = [row for row in assigned if float(row["offset_mm"]) == offset]
        lateral = [row for row in group if row["axis"] == "x"]
        weights = {row["specimen_id"]: (1 if float(row["volume_mm3"]) == .007 else -1) / 6 for row in lateral}
        comparison = endpoint(weights, "x", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
        comparison.update(kind="5_minus_7nL_restoring_magnitude", offset_mm=offset)
        for block in ("1", "2", "3"):
            block_weights = {row["specimen_id"]: (1 if float(row["volume_mm3"]) == .007 else -1) / 2 for row in lateral if row["block"] == block}
            block_result = endpoint(block_weights, "x", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
            block_result.update(block=block, kind="5_minus_7nL_restoring_magnitude", offset_mm=offset)
            block_assessments.append(block_result)
            if block_result["status"] != "agreement_within_declared_guard":
                comparison["issues"].append("Preparation block " + block + " disagrees or is incomplete")
                if comparison["status"] == "agreement_within_declared_guard":
                    comparison["status"] = block_result["status"]
        if comparison["measurement_U_uN"] > 3 or comparison["combined_decision_guard_uN"] * 3 > abs(comparison["predicted_uN"]):
            comparison["issues"].append("Force contrast discrimination margin failed")
            comparison["status"] = "inconclusive"
        endpoints.append(comparison)
        for volume in (.005, .007):
            x_group = [row for row in lateral if float(row["volume_mm3"]) == volume]
            absolute = endpoint({row["specimen_id"]: 1 / 6 for row in x_group}, "x", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
            absolute.update(kind="mean_absolute_lateral_force", volume_mm3=volume, offset_mm=offset)
            for block in ("1", "2", "3"):
                block_result = endpoint({row["specimen_id"]: .5 for row in x_group if row["block"] == block}, "x", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
                block_result.update(block=block, kind="mean_absolute_lateral_force", volume_mm3=volume, offset_mm=offset)
                block_assessments.append(block_result)
                if block_result["status"] != "agreement_within_declared_guard":
                    absolute["issues"].append("Preparation block " + block + " disagrees or is incomplete")
                    if absolute["status"] == "agreement_within_declared_guard":
                        absolute["status"] = block_result["status"]
            if absolute["individual_disagreements"] and absolute["status"] == "agreement_within_declared_guard":
                absolute["issues"].append("Individual absolute x disagreement cannot cancel in the contrast")
                absolute["status"] = "disagreement_exceeds_declared_guard"
            if absolute["combined_decision_guard_uN"] > 3:
                absolute["issues"].append("Absolute force precision gate failed")
                absolute["status"] = "inconclusive"
            absolute_lateral.append(absolute)
            normal = [row for row in group if row["axis"] == "z" and float(row["volume_mm3"]) == volume]
            normal_result = endpoint({row["specimen_id"]: 1 / 6 for row in normal}, "z", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
            normal_result.update(kind="mean_normal_force", volume_mm3=volume, offset_mm=offset)
            for block in ("1", "2", "3"):
                block_result = endpoint({row["specimen_id"]: .5 for row in normal if row["block"] == block}, "z", inputs, metadata, predicted, observed, input_sources, force_sources, protocol)
                block_result.update(block=block, kind="mean_normal_force", volume_mm3=volume, offset_mm=offset)
                block_assessments.append(block_result)
                if block_result["status"] != "agreement_within_declared_guard":
                    normal_result["issues"].append("Preparation block " + block + " disagrees or is incomplete")
                    if normal_result["status"] == "agreement_within_declared_guard":
                        normal_result["status"] = block_result["status"]
            if normal_result["individual_disagreements"]:
                normal_result["issues"].append("Opposing specimen residuals cannot be hidden by averaging")
                if normal_result["status"] == "agreement_within_declared_guard":
                    normal_result["status"] = "disagreement_exceeds_declared_guard"
            guard = normal_result["combined_decision_guard_uN"]
            normal_result["predicted_sign_resolved"] = abs(normal_result["predicted_uN"]) > normal_result["input_first_order_U_uN"] + normal_result["numerical_and_one_at_a_time_nonlinearity_guard_uN"]
            normal_result["observed_sign_resolved"] = normal_result["observed_uN"] is not None and abs(normal_result["observed_uN"]) > normal_result["measurement_U_uN"]
            if guard > 3 or not normal_result["predicted_sign_resolved"] or not normal_result["observed_sign_resolved"]:
                normal_result["issues"].append("Normal force or sign discrimination gate failed")
                normal_result["status"] = "inconclusive"
            endpoints.append(normal_result)
    all_assessments = endpoints + absolute_lateral
    statuses = {item["status"] for item in all_assessments}
    overall = "disagreement_exceeds_declared_guard" if "disagreement_exceeds_declared_guard" in statuses else "inconclusive" if "inconclusive" in statuses else "supports_declared_force_endpoints_only"
    report = {"kind": "PROSPECTIVE_FORCE_ENDPOINT_ASSESSMENT", "overall_status": overall, "absolute_lateral_force_assessments": absolute_lateral, "freeze_manifest_sha256": expected_sha, "outcomes_sha256": digest(content), "outcomes_supplied": len(rows), "allocated_independent_specimens": 48, "endpoints": endpoints, "preparation_block_assessments": block_assessments, "scope": "Agreement concerns declared isolated hot fixed-rim endpoints under a local first-order input uncertainty screen. It is not physical validation of a whole PCB, a production recommendation, or a model-discrepancy coverage claim. Shared uncertainty remains shared; repeated frames were not counted as specimens."}
    code_hashes()
    output.mkdir(parents=True)
    (output / "outcomes.csv").write_bytes(content)
    write_json(output / "assessment.json", report)
    return report


def verify_plan(directory):
    directory = Path(directory)
    report_bytes = (directory / "plan.json").read_bytes()
    report = read_json(report_bytes)
    hashes = code_hashes()
    if report["code_sha256"] != hashes or report["protocol_sha256"] != digest((LAB / "protocol.json").read_bytes()):
        raise DataError("Planning source or protocol differs from current code.")
    files = report["files"]
    actual = {str(path.relative_to(directory)) for path in directory.rglob("*") if path.is_file()}
    if actual != set(files) | {"plan.json"}:
        raise DataError("Planning directory member set changed.")
    for name, sha in files.items():
        path = directory / name
        if path.is_symlink() or directory.resolve() not in path.resolve().parents or digest(path.read_bytes()) != sha:
            raise DataError("Planning receipt or source snapshot changed.")
    expected_source = {"source/" + name for name in (*hashes, "force_lab/protocol.json")}
    for name in (*hashes, "force_lab/protocol.json"):
        if (directory / "source" / name).read_bytes() != (ROOT / name).read_bytes():
            raise DataError("Planning source snapshot differs from its declared producer.")
    protocol = read_json((LAB / "protocol.json").read_bytes())
    consumed = set()
    def fetch(spec):
        name = "receipts/" + spec.sha256 + ".json.gz"
        consumed.add(name)
        result = read_json(gzip.decompress((directory / name).read_bytes()))
        if result["input"] != spec.to_dict() or result["input_sha256"] != spec.sha256:
            raise DataError("Planning receipt differs from the expected native request.")
        if result["status"] not in ("refinement_checked", "not_converged", "failed"):
            raise DataError("Unknown native planning status.")
        receipt_engine(result, report["engine"])
        return result
    cases = [prediction_from_receipts(JointSpec(**protocol["planning_inputs_only"], volume_mm3=volume), protocol, fetch) for volume in (.005, .007)]
    if set(files) != expected_source | consumed:
        raise DataError("Planning receipts do not match the complete expected request set.")
    derived = planning_report(cases, protocol, hashes, report["engine"], len(consumed))
    if report != {**derived, "files": files}:
        raise DataError("Planning targets, sensitivities, qualification or budget conclusions differ from raw receipts.")
    return {"status": "PLANNING_BYTES_AND_DECISIONS_VERIFIED_NOT_PHYSICAL_VALIDATION", "native_requests": len(consumed), "native_replay_performed": False, "plan_sha256": digest(report_bytes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("templates", "plan"):
        sub.add_parser(command).add_argument("output")
    sub.add_parser("verify-plan").add_argument("directory")
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("inputs_directory")
    freeze_parser.add_argument("output")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("freeze_directory")
    verify_parser.add_argument("--manifest-sha256", required=True)
    score_parser = sub.add_parser("score")
    score_parser.add_argument("freeze_directory")
    score_parser.add_argument("outcomes")
    score_parser.add_argument("output")
    score_parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "templates":
            result = templates(args.output)
        elif args.command == "plan":
            result = plan(args.output)
            result = {key: value for key, value in result.items() if key != "cases"}
        elif args.command == "verify-plan":
            result = verify_plan(args.directory)
        elif args.command == "freeze":
            result = freeze(args.inputs_directory, args.output)
        elif args.command == "verify":
            result = frozen(args.freeze_directory, args.manifest_sha256)[0]
        else:
            result = score(args.freeze_directory, args.outcomes, args.output, args.manifest_sha256)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (DataError, OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Force analysis rejected input: {error}\n")


if __name__ == "__main__":
    main()
