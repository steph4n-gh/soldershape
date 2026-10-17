#!/usr/bin/env python3
"""Freeze prospective coupon predictions and score separately recorded outcomes."""

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
COUPONS = ROOT / "coupons"
sys.path.insert(0, str(ROOT))
from soldershape.model import LoadSpec, spherical_gap_mm
from soldershape.solver import engine_info, solve

INPUT_NUMBERS = (
    "cap_mass_mg", "solder_kit_mass_mg", "lower_diameter_mm", "upper_diameter_mm",
    "lower_metal_um", "upper_metal_um", "pre_offset_mm",
)
INPUT_COLUMNS = ("cap_id",) + tuple(
    column for name in INPUT_NUMBERS for column in (name, name.rsplit("_", 1)[0] + "_U_" + name.rsplit("_", 1)[1])
) + ("measurement_evidence", "measured_at_utc")
OUTCOME_COLUMNS = (
    "cap_id", "phase", "status", "mean_gap_um", "mean_gap_U_um", "min_gap_um", "min_gap_U_um",
    "max_gap_um", "max_gap_U_um", "joints_measured", "full_volume_3d", "observed_offset_mm",
    "observed_offset_U_mm", "defects", "measurement_evidence", "measured_at_utc", "temperature_C", "temperature_U_C",
    "wetted_joints", "wetting_boundary_status", "wetting_evidence", "range_U_um", "range_uncertainty_evidence",
    "pair_difference_U_um", "pair_uncertainty_evidence",
)
METADATA_KEYS = {"alloy", "flux", "reflow_profile", "temperature_C", "temperature_U_C",
                 "liquid_density_g_cm3", "surface_tension_n_m", "coverage_factor", "pilot",
                 "measurement_method", "hot_method_evidence", "lab"}
CODE_FILES = ("coupons/tools/analyze.py", "soldershape/model.py", "soldershape/solver.py")


class DataError(ValueError):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda value: (_ for _ in ()).throw(DataError(f"Nonfinite JSON {value}.")))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def number(value, name, minimum=0, positive=False):
    if isinstance(value, bool) or value is None or str(value).strip() == "":
        raise DataError(f"{name} is required.")
    try:
        value = float(value)
    except (TypeError, ValueError) as error:
        raise DataError(f"{name} must be a number.") from error
    if not math.isfinite(value) or value < minimum or (positive and value <= minimum):
        raise DataError(f"{name} must be finite and {'greater than' if positive else 'at least'} {minimum}.")
    return value


def timestamp(value, name):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as error:
        raise DataError(f"{name} must be an ISO timestamp with UTC timezone.") from error
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise DataError(f"{name} must include UTC timezone.")
    return result


def text_required(value, name):
    if not isinstance(value, str) or not value.strip():
        raise DataError(f"{name} needs an evidence reference or recorded value.")
    return value


def read_csv(path, columns=None):
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise DataError("CSV needs unique column names.")
        if columns is not None and set(reader.fieldnames) != set(columns):
            raise DataError(f"CSV columns must be exactly {','.join(columns)}.")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise DataError("CSV has a missing or extra cell.")
    return rows


def allocation():
    rows = read_csv(COUPONS / "allocation.csv")
    rows = [row for row in rows if row.get("role") == "confirmatory"]
    required = {"cap_id", "run_id", "pair_id", "arm"}
    if not rows or not required <= set(rows[0]):
        raise DataError("Allocation needs confirmatory cap_id, run_id, pair_id and arm.")
    if len(rows) != 24 or len({row["cap_id"] for row in rows}) != 24:
        raise DataError("This experiment revision requires 24 unique confirmatory caps.")
    if set(row["arm"] for row in rows) != {"C220", "C270"}:
        raise DataError("Confirmatory allocation needs C220 and C270.")
    pairs = {}
    for row in rows:
        pairs.setdefault((row["run_id"], row["pair_id"]), []).append(row["arm"])
    if len(pairs) != 12 or any(sorted(arms) != ["C220", "C270"] for arms in pairs.values()):
        raise DataError("Confirmatory allocation needs 12 within-run C220/C270 pairs.")
    if len({row["run_id"] for row in rows}) != 3:
        raise DataError("Confirmatory allocation needs three run blocks.")
    return rows


def templates(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if any((output / name).exists() for name in ("inputs.csv", "outcomes.csv", "metadata.json")):
        raise DataError("Refusing to overwrite an existing worksheet.")
    for name, columns in (("inputs.csv", INPUT_COLUMNS), ("outcomes.csv", OUTCOME_COLUMNS)):
        path = output / name
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, columns)
            writer.writeheader()
            for row in allocation():
                value = {"cap_id": row["cap_id"]}
                if name == "outcomes.csv":
                    value.update(phase="post_reflow", status="measurement_missing", wetting_boundary_status="unobserved")
                writer.writerow(value)
    metadata = {key: None for key in sorted(METADATA_KEYS)}
    metadata.update(liquid_density_g_cm3={"value": None, "U": None, "source": None},
                    surface_tension_n_m={"value": None, "U": None, "source": None},
                    pilot={"qualified": None, "evidence": None})
    write_json(output / "metadata.json", metadata)


def validate_metadata(data, spec):
    if not isinstance(data, dict) or set(data) != METADATA_KEYS:
        raise DataError("Metadata must contain the exact template fields, with no outcome fields.")
    for name in ("alloy", "flux", "reflow_profile", "measurement_method", "lab"):
        text_required(data[name], name)
    data["temperature_C"] = number(data["temperature_C"], "temperature_C", minimum=0, positive=True)
    data["temperature_U_C"] = number(data["temperature_U_C"], "temperature_U_C", positive=True)
    if data["temperature_C"] - data["temperature_U_C"] <= spec["assembly"]["liquidus_C"]:
        raise DataError("The entire frozen temperature interval must be above the alloy liquidus.")
    if data["hot_method_evidence"] is not None and not isinstance(data["hot_method_evidence"], str):
        raise DataError("hot_method_evidence must be an evidence reference or null for an unqualified hot method.")
    if number(data["coverage_factor"], "coverage_factor") != 2:
        raise DataError("This revision requires expanded uncertainties with coverage factor 2.")
    for name in ("liquid_density_g_cm3", "surface_tension_n_m"):
        value = data[name]
        if not isinstance(value, dict) or set(value) != {"value", "U", "source"}:
            raise DataError(f"{name} needs value, U and source.")
        central = number(value["value"], name, positive=True)
        uncertainty = number(value["U"], name + " U", positive=True)
        if uncertainty >= central:
            raise DataError(f"{name} U must be smaller than its value.")
        value.update(value=central, U=uncertainty)
        text_required(value["source"], name + " source")
    pilot = data["pilot"]
    if not isinstance(pilot, dict) or set(pilot) != {"qualified", "evidence"} or pilot["qualified"] is not True:
        raise DataError("Pilot qualification is required before confirmatory freeze.")
    text_required(pilot["evidence"], "pilot evidence")
    return data


def validate_inputs(path, spec, now):
    expected = {row["cap_id"]: row for row in allocation()}
    rows = read_csv(path, INPUT_COLUMNS)
    if len(rows) != len(expected) or {row["cap_id"] for row in rows} != set(expected):
        raise DataError("Inputs need each of the 24 allocated caps exactly once.")
    for row in rows:
        for name in INPUT_NUMBERS:
            row[name] = number(row[name], row["cap_id"] + " " + name, positive=name != "pre_offset_mm")
            u_name = name.rsplit("_", 1)[0] + "_U_" + name.rsplit("_", 1)[1]
            row[u_name] = number(row[u_name], u_name, positive=True)
            if name != "pre_offset_mm" and row[u_name] >= row[name]:
                raise DataError(f"{u_name} must be smaller than its central value.")
        if row["pre_offset_mm"] + row["pre_offset_U_mm"] > spec["model"]["max_pre_outcome_offset_mm"]:
            raise DataError("Pre-outcome offset including uncertainty exceeds the declared gate.")
        nominal_lower = spec["arms"][expected[row["cap_id"]]["arm"]]["pad_diameter_mm"]
        for name, nominal in (("lower", nominal_lower), ("upper", spec["cap"]["pad_diameter_mm"])):
            if 1000*(abs(row[name+"_diameter_mm"]-nominal)+row[name+"_diameter_U_mm"]) > spec["fabrication"]["pad_diameter_target_tolerance_um"]:
                raise DataError(f"{name} pad diameter fails the target tolerance including uncertainty.")
        text_required(row["measurement_evidence"], "input measurement evidence")
        if timestamp(row["measured_at_utc"], "input measured_at_utc") > now:
            raise DataError("Input measurement time is in the future.")
    return rows


def request(row, metadata, spec, mapping, gravity=False):
    count = spec["array"]["joint_count"]
    volume = row["solder_kit_mass_mg"] / count / metadata["liquid_density_g_cm3"]["value"]
    correction = 0
    if mapping == "two_pad_cylinders":
        volume += math.pi * (row["lower_diameter_mm"] / 2)**2 * row["lower_metal_um"] / 1000
        volume += math.pi * (row["upper_diameter_mm"] / 2)**2 * row["upper_metal_um"] / 1000
        correction = row["lower_metal_um"] + row["upper_metal_um"]
    return LoadSpec(lower_diameter_mm=row["lower_diameter_mm"], upper_diameter_mm=row["upper_diameter_mm"],
                    volume_mm3=volume, offset_mm=row["pre_offset_mm"],
                    normal_load_uN=row["cap_mass_mg"] * spec["model"]["g_m_s2"] / count,
                    surface_tension_n_m=metadata["surface_tension_n_m"]["value"],
                    density_g_cm3=metadata["liquid_density_g_cm3"]["value"], gravity=gravity), correction


def analytical(spec, correction):
    height = spherical_gap_mm(spec.lower_diameter_mm, spec.upper_diameter_mm, spec.volume_mm3)
    p, q = spec.upper_diameter_mm / 2, spec.lower_diameter_mm / 2
    j = (height**2 + p*p + q*q) / (p*p + q*q)
    u = p*q / (p*p + q*q)
    stiffness = spec.surface_tension_n_m * (4*math.pi/5) * j * (j*(j+4)+10*u*u) / (j*j-4*u*u)**1.5
    return {"gap_um": 1000*height - correction - spec.normal_load_uN/stiffness,
            "stiffness_N_m": stiffness, "scope": "Eq. 9 aligned small-load approximation. Offset and gravity omitted."}


def prediction(row, metadata, spec, mapping, cache, directory, gravity=False):
    native_request, correction = request(row, metadata, spec, mapping, gravity)
    key = native_request.sha256
    if key not in cache:
        result = solve(native_request)
        receipt = directory / "receipts" / (key + ".json.gz")
        receipt.parent.mkdir(exist_ok=True)
        with gzip.open(receipt, "wt") as stream:
            json.dump(result, stream, allow_nan=False)
        cache[key] = result
    result = cache[key]
    good = result["status"] == "refinement_checked" and result.get("load_balance", {}).get("status") == "balanced"
    return {"mapping": mapping, "gravity": gravity, "request": native_request.to_dict(), "request_sha256": key,
            "native_status": result["status"], "native_error": result.get("error"),
            "predicted_pad_face_gap_um": 1000*result["equilibrium"]["standoff_mm"] - correction if good else None,
            "analytical": analytical(native_request, correction),
            "receipt": "receipts/" + key + ".json.gz"}


def sensitivity(row, metadata, spec):
    central = analytical(*request(row, metadata, spec, "literal_rims"))["gap_um"]
    shifts = []
    for name in ("cap_mass_mg", "solder_kit_mass_mg", "lower_diameter_mm", "upper_diameter_mm"):
        u_name = name.rsplit("_", 1)[0] + "_U_" + name.rsplit("_", 1)[1]
        values = []
        for sign in (-1, 1):
            changed = dict(row, **{name: row[name] + sign*row[u_name]})
            values.append(analytical(*request(changed, metadata, spec, "literal_rims"))["gap_um"])
        shifts.append({"input": name, "max_abs_shift_um": max(abs(value-central) for value in values)})
    for name in ("liquid_density_g_cm3", "surface_tension_n_m"):
        values = []
        for sign in (-1, 1):
            changed = dict(metadata, **{name: dict(metadata[name], value=metadata[name]["value"]+sign*metadata[name]["U"])})
            values.append(analytical(*request(row, changed, spec, "literal_rims"))["gap_um"])
        shifts.append({"input": name, "max_abs_shift_um": max(abs(value-central) for value in values)})
    return {"one_at_a_time_shifts": shifts, "sum_abs_shifts_um": sum(value["max_abs_shift_um"] for value in shifts),
            "scope": "Analytical sensitivity screen. Not a propagated native uncertainty interval. Offset, copper, interactions and correlations omitted."}


def generate_predictions(rows, metadata, spec, output):
    cache, predictions = {}, []
    for row in rows:
        predictions.append({"cap_id": row["cap_id"], "models": [
            prediction(row, metadata, spec, "literal_rims", cache, output),
            prediction(row, metadata, spec, "two_pad_cylinders", cache, output),
            prediction(row, metadata, spec, "literal_rims", cache, output, gravity=True)],
            "analytical_input_sensitivity": sensitivity(row, metadata, spec)})
    return predictions, len(cache)


def freeze(inputs, metadata, output):
    output = Path(output)
    if output.exists():
        raise DataError("Freeze directory must not exist. Existing freezes are never overwritten.")
    spec = read_json(COUPONS / "experiment.json")
    material = validate_metadata(read_json(metadata), spec)
    if material["alloy"] != spec["assembly"]["alloy"]:
        raise DataError("Alloy differs from this experiment revision.")
    rows = validate_inputs(inputs, spec, datetime.now(timezone.utc))
    code_hashes = {name: sha(ROOT / name) for name in CODE_FILES}
    output.mkdir(parents=True)
    for source, name in ((inputs, "inputs.csv"), (metadata, "metadata.json"),
                         (COUPONS / "experiment.json", "experiment.json"), (COUPONS / "allocation.csv", "allocation.csv")):
        shutil.copyfile(source, output / name)
    predictions, count = generate_predictions(rows, material, spec, output)
    if code_hashes != {name: sha(ROOT / name) for name in CODE_FILES}:
        raise DataError("Prediction code changed during the freeze. Partial receipts are preserved without a completed manifest.")
    for name in ("experiment.json", "allocation.csv"):
        if sha(output / name) != sha(COUPONS / name):
            raise DataError("Experiment or allocation changed during the freeze. No completed manifest was written.")
    write_json(output / "predictions.json", {"kind": "prospective_frozen_predictions", "caps": predictions})
    files = {str(path.relative_to(output)): sha(path) for path in output.rglob("*") if path.is_file()}
    manifest = {"schema": "soldershape.coupon.freeze.v1", "frozen_at_utc": utc_now(),
                "experiment_id": spec["experiment_id"], "files": files,
                "code_sha256": code_hashes, "engine": engine_info(), "distinct_native_requests": count,
                "scope": "Central predictions at measured inputs. Input uncertainty is retained but not propagated through the native solver. No confirmatory outcomes supplied."}
    write_json(output / "manifest.json", manifest)
    return manifest


def plan(output):
    output = Path(output)
    if output.exists():
        raise DataError("Planning output directory must not exist.")
    output.mkdir(parents=True)
    spec = read_json(COUPONS / "experiment.json")
    assumptions = spec["planning_assumptions_only"]
    density = assumptions["density_g_cm3"]
    metadata = {"liquid_density_g_cm3": {"value": density},
                "surface_tension_n_m": {"value": assumptions["gamma_n_m"]}}
    rows = []
    for arm, geometry in spec["arms"].items():
        row = {"cap_id": arm, "cap_mass_mg": assumptions["cap_mass_mg"],
               "solder_kit_mass_mg": assumptions["solid_sphere_volume_mm3"] * density * spec["array"]["joint_count"],
               "lower_diameter_mm": geometry["pad_diameter_mm"], "upper_diameter_mm": spec["cap"]["pad_diameter_mm"],
               "lower_metal_um": assumptions["lower_finished_metal_um"], "upper_metal_um": assumptions["upper_finished_metal_um"],
               "pre_offset_mm": assumptions["offset_mm"]}
        rows.append(row)
    cache = {}
    predictions = [{"cap_id": row["cap_id"], "models": [
        prediction(row, metadata, spec, "literal_rims", cache, output),
        prediction(row, metadata, spec, "two_pad_cylinders", cache, output),
        prediction(row, metadata, spec, "literal_rims", cache, output, gravity=True)]} for row in rows]
    report = {"kind": "NOT_FROZEN_NOT_PHYSICAL_DATA", "assumptions": assumptions,
              "warning": "Planning geometry only. Liquid volume equals solid sphere volume by assumption. These are not laboratory inputs or registered physical predictions.",
              "distinct_native_requests": len(cache), "caps": predictions}
    write_json(output / "plan.json", report)
    return report


def verify_freeze(directory):
    directory = Path(directory)
    manifest = read_json(directory / "manifest.json")
    if manifest.get("schema") != "soldershape.coupon.freeze.v1":
        raise DataError("Not a prospective coupon freeze.")
    for name, digest in manifest["files"].items():
        path = directory / name
        if path.resolve().parent != directory.resolve() and directory.resolve() not in path.resolve().parents:
            raise DataError("Freeze manifest contains an unsafe path.")
        if not path.is_file() or sha(path) != digest:
            raise DataError(f"Frozen file changed or missing: {name}.")
    for name, digest in manifest["code_sha256"].items():
        if sha(ROOT / name) != digest:
            raise DataError(f"Prediction code changed since freeze: {name}.")
    for name in ("experiment.json", "allocation.csv"):
        if sha(COUPONS / name) != manifest["files"][name]:
            raise DataError(f"Experiment or allocation changed since freeze: {name}.")
    return manifest


def outcome_rows(path, expected, frozen_at):
    rows = read_csv(path, OUTCOME_COLUMNS)
    seen = set()
    for row in rows:
        key = row["cap_id"], row["phase"]
        if row["cap_id"] not in expected or row["phase"] not in ("post_reflow", "molten") or key in seen:
            raise DataError("Outcomes have an unknown cap/phase or duplicate cap within phase.")
        seen.add(key)
        if row["status"] not in ("measured", "assembly_failed", "measurement_missing"):
            raise DataError("Outcome status must be measured, assembly_failed or measurement_missing.")
        if row["status"] != "measured":
            if any(row[name].strip() for name in ("mean_gap_um", "min_gap_um", "max_gap_um")):
                raise DataError("Unmeasured outcomes cannot contain measured heights.")
            if row["status"] == "assembly_failed":
                text_required(row["defects"], "assembly failure reason")
                text_required(row["measurement_evidence"], "assembly failure evidence")
                failed_at = timestamp(row["measured_at_utc"], "failure time")
                if failed_at <= frozen_at or failed_at > datetime.now(timezone.utc):
                    raise DataError("Confirmatory outcomes must follow the completed freeze.")
            continue
        for name in ("mean_gap_um", "min_gap_um", "max_gap_um", "mean_gap_U_um", "min_gap_U_um", "max_gap_U_um",
                     "observed_offset_mm", "observed_offset_U_mm", "temperature_U_C"):
            row[name] = number(row[name], name, positive=name.endswith("_U_um") or name in ("observed_offset_U_mm", "temperature_U_C"))
        row["temperature_C"] = number(row["temperature_C"], "temperature_C", minimum=-273.15)
        joints = number(row["joints_measured"], "joints_measured", positive=True)
        if joints != int(joints) or joints > 20 or row["full_volume_3d"] not in ("true", "false"):
            raise DataError("joints_measured must be 1..20 and full_volume_3d must be true or false.")
        row["joints_measured"] = int(joints)
        if row["full_volume_3d"] == "true" and joints != 20:
            raise DataError("A whole-cap 3D minimum requires all twenty joint interfaces.")
        if not row["min_gap_um"] <= row["mean_gap_um"] <= row["max_gap_um"]:
            raise DataError("Observed min, mean and max gaps are inconsistent.")
        text_required(row["defects"], "defects, use none when inspected and absent")
        text_required(row["measurement_evidence"], "outcome evidence")
        if row["wetting_boundary_status"] not in ("matches_frozen", "fails", "unobserved"):
            raise DataError("wetting_boundary_status must be matches_frozen, fails or unobserved.")
        if row["wetted_joints"].strip():
            wetted = number(row["wetted_joints"], "wetted_joints")
            if wetted != int(wetted) or wetted > 20:
                raise DataError("wetted_joints must be 0..20, or blank when unobserved.")
            row["wetted_joints"] = int(wetted)
            text_required(row["wetting_evidence"], "observed wetting evidence")
        else:
            row["wetted_joints"] = None
        if row["wetting_boundary_status"] != "unobserved":
            text_required(row["wetting_evidence"], "wetting boundary evidence")
        if row["wetting_boundary_status"] == "matches_frozen" and row["wetted_joints"] != 20:
            raise DataError("A matching frozen boundary requires twenty observed wetted joints.")
        if row["range_U_um"].strip():
            row["range_U_um"] = number(row["range_U_um"], "range_U_um", positive=True)
            text_required(row["range_uncertainty_evidence"], "range uncertainty evidence")
        elif row["range_uncertainty_evidence"].strip():
            raise DataError("A range uncertainty reference requires its expanded uncertainty value.")
        if row["pair_difference_U_um"].strip():
            row["pair_difference_U_um"] = number(row["pair_difference_U_um"], "pair_difference_U_um", positive=True)
            text_required(row["pair_uncertainty_evidence"], "pair uncertainty evidence")
        observed_at = timestamp(row["measured_at_utc"], "outcome measured_at_utc")
        if observed_at <= frozen_at:
            raise DataError("Confirmatory outcomes must follow the completed freeze.")
        if observed_at > datetime.now(timezone.utc):
            raise DataError("Outcome measurement time is in the future.")
    return { (row["cap_id"], row["phase"]): row for row in rows }


def score(directory, outcomes, output):
    directory = Path(directory)
    manifest = verify_freeze(directory)
    spec = read_json(directory / "experiment.json")
    metadata = read_json(directory / "metadata.json")
    inputs = {row["cap_id"]: row for row in read_csv(directory / "inputs.csv", INPUT_COLUMNS)}
    assignments = allocation()
    observed = outcome_rows(outcomes, {row["cap_id"] for row in assignments}, timestamp(manifest["frozen_at_utc"], "frozen_at_utc"))
    predicted = {row["cap_id"]: row for row in read_json(directory / "predictions.json")["caps"]}
    caps = []
    for assignment in assignments:
        cap = {key: assignment[key] for key in ("cap_id", "arm", "run_id", "pair_id")}
        cap["phases"] = {}
        for phase in ("post_reflow", "molten"):
            row = observed.get((cap["cap_id"], phase))
            assessment = {"status": row["status"] if row else "measurement_missing", "clearance": "inconclusive", "central_model_agreement": "inconclusive"}
            if row and row["status"] == "measured":
                assessment["observed"] = row
                full = row["full_volume_3d"] == "true" and row["joints_measured"] == 20
                uncertainty_ok = max(row[name] for name in ("mean_gap_U_um", "min_gap_U_um", "max_gap_U_um")) <= spec["measurement"]["max_gap_expanded_U_um"]
                reference_temperature = metadata["temperature_C"] if phase == "molten" else spec["measurement"]["temperature_C"]
                temperature_tolerance = metadata["temperature_U_C"] if phase == "molten" else spec["measurement"]["temperature_tolerance_C"]
                temperature_ok = abs(row["temperature_C"]-reference_temperature) + row["temperature_U_C"] <= temperature_tolerance
                if phase == "molten":
                    temperature_ok = temperature_ok and row["temperature_C"]-row["temperature_U_C"] > spec["assembly"]["liquidus_C"]
                range_uncertainty = row["range_U_um"] if row["range_U_um"] != "" else row["min_gap_U_um"] + row["max_gap_U_um"]
                guarded_range = row["max_gap_um"] - row["min_gap_um"] + range_uncertainty
                range_ok = guarded_range <= spec["model"]["max_gap_range_um"]
                wetting_ok = row["wetted_joints"] == 20
                boundary_ok = row["wetting_boundary_status"] == "matches_frozen"
                hot_method_ok = bool(metadata["hot_method_evidence"] and metadata["hot_method_evidence"].strip())
                phase_method_ok = phase == "post_reflow" or hot_method_ok
                geometry_ok = (
                    full and uncertainty_ok and temperature_ok and phase_method_ok and wetting_ok
                    and row["defects"].strip().lower() == "none"
                    and row["observed_offset_mm"] + row["observed_offset_U_mm"] <= spec["model"]["max_outcome_offset_mm"]
                    and range_ok
                )
                incoming = inputs[cap["cap_id"]]
                offset_drift = row["observed_offset_mm"]-float(incoming["pre_offset_mm"])
                offset_consistent = abs(offset_drift) <= row["observed_offset_U_mm"]+float(incoming["pre_offset_U_mm"])
                model_eligible = geometry_ok and boundary_ok and offset_consistent and phase == "molten"
                assessment.update(full_cap_coverage=full, measurement_uncertainty_gate=uncertainty_ok,
                                  temperature_gate=temperature_ok, geometry_gate=geometry_ok,
                                  all_joints_wetted_gate=wetting_ok, frozen_wetting_boundary_gate=boundary_ok,
                                  guarded_gap_range_um=guarded_range, gap_range_gate=range_ok,
                                  range_uncertainty_source="lab supplied range budget" if row["range_U_um"] != "" else "sum of minimum and maximum expanded uncertainties",
                                  hot_method_gate=hot_method_ok, model_eligibility_gate=model_eligible,
                                  observed_minus_pre_offset_mm=offset_drift, frozen_offset_consistency_gate=offset_consistent)
                if full and uncertainty_ok and temperature_ok and phase_method_ok:
                    low, high = row["min_gap_um"]-row["min_gap_U_um"], row["min_gap_um"]+row["min_gap_U_um"]
                    threshold = spec["measurement"]["clearance_threshold_um"]
                    assessment["clearance"] = "above_guardband" if low >= threshold else "below_guardband" if high < threshold else "inconclusive"
                models = []
                for model in predicted[cap["cap_id"]]["models"]:
                    value = model["predicted_pad_face_gap_um"]
                    delta = row["mean_gap_um"]-value if value is not None else None
                    budget = spec["model"]["height_error_budget_um"]
                    agreement = "inconclusive"
                    if delta is not None and model_eligible:
                        agreement = "consistent_at_frozen_inputs" if abs(delta)+row["mean_gap_U_um"] <= budget else "disagrees_at_frozen_inputs" if abs(delta)-row["mean_gap_U_um"] > budget else "inconclusive"
                    models.append({"mapping": model["mapping"], "gravity": model["gravity"], "mean_minus_prediction_um": delta, "agreement": agreement})
                assessment["models"] = models
                assessment["central_model_agreement"] = models[0]["agreement"]
            cap["phases"][phase] = assessment
        caps.append(cap)
    runs = []
    for run_id in sorted({cap["run_id"] for cap in caps}):
        pairs = []
        for pair_id in sorted({cap["pair_id"] for cap in caps if cap["run_id"] == run_id}):
            arms = {cap["arm"]: cap for cap in caps if cap["run_id"] == run_id and cap["pair_id"] == pair_id}
            pair = {"pair_id": pair_id}
            for phase in ("post_reflow", "molten"):
                values = {arm: cap["phases"][phase] for arm, cap in arms.items()}
                if all(value["status"] == "measured" and value.get("geometry_gate") for value in values.values()):
                    a, b = values["C220"]["observed"], values["C270"]["observed"]
                    supplied = (a["pair_difference_U_um"], b["pair_difference_U_um"])
                    if any(value != "" for value in supplied) and supplied[0] != supplied[1]:
                        raise DataError("Both cap rows must record the same supplied pair uncertainty.")
                    uncertainty = supplied[0] if supplied[0] != "" else a["mean_gap_U_um"]+b["mean_gap_U_um"]
                    pair[phase] = {"C220_minus_C270_um": a["mean_gap_um"]-b["mean_gap_um"],
                                   "conservative_expanded_U_um": uncertainty,
                                   "uncertainty_source": "lab supplied pair budget" if supplied[0] != "" else "sum of cap expanded uncertainties",
                                   "uncertainty_gate": uncertainty <= spec["measurement"]["max_pair_expanded_U_um"]}
                else:
                    pair[phase] = None
            pairs.append(pair)
        run = {"run_id": run_id, "pairs": pairs}
        for phase in ("post_reflow", "molten"):
            usable = [pair[phase] for pair in pairs if pair[phase] is not None and pair[phase]["uncertainty_gate"]]
            run[phase] = {"complete_pairs": len(usable), "mean_C220_minus_C270_um": statistics.mean(value["C220_minus_C270_um"] for value in usable) if usable else None,
                          "conservative_U_um": statistics.mean(value["conservative_expanded_U_um"] for value in usable) if usable else None}
        runs.append(run)
    decisions = {}
    for phase in ("post_reflow", "molten"):
        blocks = [run[phase] for run in runs]
        complete = all(block["complete_pairs"] == 4 for block in blocks)
        positive = complete and all(block["mean_C220_minus_C270_um"] > block["conservative_U_um"] for block in blocks)
        negative = complete and all(block["mean_C220_minus_C270_um"] < -block["conservative_U_um"] for block in blocks)
        decisions[phase] = {"direction": "C220_higher_in_all_three_runs" if positive else "C270_higher_in_all_three_runs" if negative else "inconclusive",
                            "scope": "Guarded observed cap-level paired direction. No population confidence interval or production yield claim."}
    hot = [cap["phases"]["molten"]["central_model_agreement"] for cap in caps]
    liquid_verdict = "disagrees_at_frozen_inputs" if "disagrees_at_frozen_inputs" in hot else "consistent_at_frozen_inputs" if all(value == "consistent_at_frozen_inputs" for value in hot) else "inconclusive"
    report = {"schema": "soldershape.coupon.score.v1", "scored_at_utc": utc_now(),
              "freeze_manifest_sha256": sha(directory / "manifest.json"), "outcomes_sha256": sha(outcomes),
              "attempted_caps": len(caps), "caps": caps, "runs": runs, "decisions": decisions,
              "liquid_model_verdict": liquid_verdict,
              "limitations": ["Cold geometry cannot qualify a molten equilibrium model.",
                              "Central agreement does not propagate input uncertainty through the native solver. The analytical sensitivity screen is not a native prediction interval.",
                              "The comparison is one coupon construction and process. It does not qualify manufacturing yield, fatigue or electrical reliability.",
                              "The single-joint model assumes equal cap load sharing. Tilt, sidewall wetting, warpage and final-offset drift can invalidate that assumption."]}
    write_json(output, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    template_parser = commands.add_parser("templates")
    template_parser.add_argument("--output", type=Path, default=COUPONS / "data")
    plan_parser = commands.add_parser("plan")
    plan_parser.add_argument("--output", type=Path, required=True)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.add_argument("--inputs", type=Path, required=True)
    freeze_parser.add_argument("--metadata", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    score_parser = commands.add_parser("score")
    score_parser.add_argument("--freeze", type=Path, required=True)
    score_parser.add_argument("--outcomes", type=Path, required=True)
    score_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "templates":
            templates(args.output)
            print(f"Blank worksheets written to {args.output}. Null and blank physical inputs cannot be frozen.")
        elif args.command == "plan":
            report = plan(args.output)
            print(json.dumps({"kind": report["kind"], "distinct_native_requests": report["distinct_native_requests"]}))
        elif args.command == "freeze":
            report = freeze(args.inputs, args.metadata, args.output)
            print(json.dumps({"frozen_at_utc": report["frozen_at_utc"], "distinct_native_requests": report["distinct_native_requests"]}))
        else:
            report = score(args.freeze, args.outcomes, args.output)
            print(json.dumps({"attempted_caps": report["attempted_caps"], "liquid_model_verdict": report["liquid_model_verdict"], "decisions": report["decisions"]}))
    except (DataError, ValueError, OSError, KeyError) as error:
        parser.exit(2, f"Data rejected. {error}\n")


if __name__ == "__main__":
    main()
