"""Replay the frozen Figure 5 physical comparison through the public solver."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from dataclasses import replace
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.model import JointSpec
from soldershape.solver import SolverError, engine_info, solve

DIRECTORY = ROOT / "evidence" / "physical"
RECEIPTS = DIRECTORY / "prediction-receipts"
MAPPINGS = ("published_flat_substrate", "literal_copper_rim", "uncorrected_interface_gap")
TRACKS = {"prior_default": .48, "published_fit": .4}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def provenance():
    return {
        "files": {str(path.relative_to(ROOT)): sha256(path) for path in (
            Path(__file__), ROOT / "soldershape" / "solver.py", ROOT / "soldershape" / "model.py",
            DIRECTORY / "protocol.json", DIRECTORY / "nist-extraction.json")},
        "engine": engine_info(),
    }


def observations(extraction):
    indexed = {row["id"]: row for row in extraction["observations"]}
    pairs = [tuple(pair) for pair in extraction["paired_ids"]]
    for option in extraction["duplicate_pairing_options"]:
        pairs.extend(tuple(pair) for pair in option)
    rows = []
    for height_id, offset_id in dict.fromkeys(pairs):
        h, x = indexed[height_id], indexed[offset_id]
        force = (h["shear_uN"] + x["shear_uN"]) / 2
        bounds = {}
        for name, measurement in (("h_um", h), ("x_um", x)):
            lower, upper = measurement["plotted_lower_um"], measurement["plotted_upper_um"]
            error = measurement["digitization_dimension_bound_um"]
            bounds[name] = [None if lower is None else lower-error,
                            None if upper is None else upper+error]
        rows.append({
            "id": height_id + "-" + offset_id,
            "height_id": height_id, "offset_id": offset_id,
            "pairing": "unambiguous" if [height_id, offset_id] in extraction["paired_ids"] else "ambiguous_duplicate",
            "phase": "calibration" if force <= 81 and [height_id, offset_id] in extraction["paired_ids"] else "held_out",
            "h_um": h["value_um"], "x_um": x["value_um"],
            "observed_shear_uN": force,
            "observed_shear_interval_uN": [min(row["shear_uN"] - row["digitization_force_bound_uN"] for row in (h, x)),
                                            max(row["shear_uN"] + row["digitization_force_bound_uN"] for row in (h, x))],
            "input_bounds": bounds,
        })
    return rows


def specification(row, mapping, extraction, volume_factor=1, h_um=None, x_um=None, coordinate_factor=1):
    h = row["h_um"] if h_um is None else h_um
    x = row["x_um"] if x_um is None else x_um
    thickness = extraction["pad_thickness_mm"]
    diameter = extraction["pad_diameter_mm"]
    solder = extraction["solder_volume_mm3"] * volume_factor
    volume = solder + 2*math.pi*(diameter/2)**2*thickness if mapping == MAPPINGS[0] else solder
    gap = h*coordinate_factor/1000 - (2*thickness if mapping == MAPPINGS[1] else 0)
    return JointSpec(diameter, diameter, gap, volume, x*coordinate_factor/1000, 1, 9, False)


def flat_plane_diagnostics(result):
    if "mesh" not in result:
        return {"status": "unavailable", "reason": "The solver did not return a mesh."}
    spec = result["input"]
    vertices = result["mesh"]["vertices_mm"]
    height = spec["standoff_mm"]
    tolerance = 1e-9
    minimum = min(point[2] for point in vertices)
    maximum = max(point[2] for point in vertices)
    below = [point for point in vertices if point[2] < -tolerance]
    above = [point for point in vertices if point[2] > height+tolerance]
    records = {}
    for name, points, center, radius in (("below_lower", below, 0, spec["lower_diameter_mm"]/2),
                                         ("above_upper", above, spec["offset_mm"], spec["upper_diameter_mm"]/2)):
        radii = [math.hypot(point[0]-center, point[1]) for point in points]
        records[name] = {"vertices": len(points), "outside_pad_radius_vertices": sum(r > radius+tolerance for r in radii),
                         "pad_radius_mm": radius, "radial_extent_mm": [min(radii), max(radii)] if radii else None,
                         "example_vertices_mm": points[:4]}
    return {"status": "violates_flat_substrate_planes" if below or above else "no_sampled_vertex_violation_detected",
            "z_extent_mm": [minimum, maximum], "gap_mm": height,
            "lower_excursion_um": max(0, -minimum)*1000, "upper_excursion_um": max(0, maximum-height)*1000,
            "coordinate_roundoff_tolerance_mm": tolerance,
            "scope": "Sampled exported vertices. This can detect an intrusion but does not certify the full curved surface or a wetting condition.",
            **records}


def compute(case, identity, refresh=False):
    name, spec = case
    solver_files = {key: value for key, value in identity["files"].items() if key.startswith("soldershape/")}
    key_input = {"input": spec.to_dict(), "code": solver_files,
                 "binary_sha256": identity["engine"].get("binary_sha256")}
    key = hashlib.sha256(json.dumps(key_input, sort_keys=True).encode()).hexdigest()
    path = RECEIPTS / (key + ".json.gz")
    if path.exists() and not refresh:
        with gzip.open(path, "rt") as source:
            receipt = json.load(source)
        result = receipt["result"]
        cached = True
    else:
        try:
            result = solve(spec)
        except SolverError as error:
            result = {"input": spec.to_dict(), "input_sha256": spec.sha256,
                      "status": "engine_error", "error": error.message, "evidence": error.evidence}
        receipt = {"provenance": identity, "result": result}
        with gzip.open(path, "wt") as target:
            json.dump(receipt, target, allow_nan=False)
        cached = False
    summary = {key: result[key] for key in ("input", "input_sha256", "status", "forces", "diagnostics", "levels", "mesh_checks", "error") if key in result}
    summary.update({"case": name, "receipt": str(path.relative_to(ROOT)), "receipt_sha256": sha256(path),
                    "restoring_shear_uN_at_1N_per_m": -result["forces"]["x_uN"] if "forces" in result else None,
                    "normal_force_uN_at_1N_per_m_diagnostic_only": result.get("forces", {}).get("z_uN"),
                    "flat_plane_diagnostics": flat_plane_diagnostics(result)})
    print(json.dumps({"case": name, "status": result["status"],
                      "unit_shear_uN": summary["restoring_shear_uN_at_1N_per_m"], "cached": cached}), flush=True)
    return name, summary


def run_cases(cases, identity, workers, refresh):
    if workers == 1:
        return dict(compute(case, identity, refresh) for case in cases)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(lambda case: compute(case, identity, refresh), cases))


def fit_gamma(rows, central):
    calibration = [row for row in rows if row["phase"] == "calibration"]
    cases = [central[MAPPINGS[0] + "/" + row["id"]] for row in calibration]
    if len(calibration) != 3 or any(case["status"] != "refinement_checked" for case in cases):
        return {"status": "inconclusive", "reason": "All three frozen calibration rows must pass numerical checks.",
                "calibration_ids": [row["id"] for row in calibration], "gamma_N_per_m": None}
    unit = [case["restoring_shear_uN_at_1N_per_m"] for case in cases]
    measured = [row["observed_shear_uN"] for row in calibration]
    gamma = sum(x*y for x, y in zip(unit, measured)) / sum(x*x for x in unit)
    if not math.isfinite(gamma) or gamma <= 0:
        return {"status": "inconclusive", "reason": "The fitted material scale is not a positive finite surface tension.",
                "calibration_ids": [row["id"] for row in calibration], "gamma_N_per_m": None}
    return {"status": "fitted_on_calibration_only", "gamma_N_per_m": gamma,
            "calibration_ids": [row["id"] for row in calibration], "intercept_uN": 0,
            "method": "Unweighted least squares, one multiplicative coefficient, zero intercept.",
            "calibration_flat_plane_statuses": {case["case"]: case.get("flat_plane_diagnostics", {}).get("status") for case in cases},
            "scope": "Gamma is fitted only to the three central primary-mapping low-force rows. It is not refitted for sensitivities or held-out rows."}


def score(case, row, gamma):
    if gamma is None or case["status"] != "refinement_checked":
        return {"status": "inconclusive", "numerical_status": case["status"]}
    prediction = case["restoring_shear_uN_at_1N_per_m"] * gamma
    error = prediction - row["observed_shear_uN"]
    plane_status = case.get("flat_plane_diagnostics", {}).get("status")
    normal_direction = case["normal_force_uN_at_1N_per_m_diagnostic_only"] > 0
    physical_status = "conditional_fixed_geometry_prediction"
    if not normal_direction:
        physical_status = "incompatible_normal_load_direction_at_sampled_geometry"
    elif plane_status == "violates_flat_substrate_planes":
        physical_status = "inconclusive_substrate_intrusion"
    return {"status": "scored", "gamma_N_per_m": gamma, "predicted_shear_uN": prediction,
            "error_uN": error, "absolute_error_uN": abs(error),
            "relative_error": error/row["observed_shear_uN"], "restoring_direction": prediction > 0,
            "physical_comparison_status": physical_status,
            "normal_load_direction_compatible": normal_direction,
            "flat_plane_status": plane_status,
            "interpretation": "Raw conditional force residual. A numerical score does not establish physical geometry admissibility or absolute accuracy."}


def aggregate(scored):
    valid = [row for row in scored if row["status"] == "scored"]
    return {"scored": len(valid), "inconclusive": len(scored)-len(valid),
            "scored_with_incompatible_normal_direction": sum(row.get("normal_load_direction_compatible") is False for row in valid),
            "scored_with_detected_substrate_intrusion": sum(row.get("flat_plane_status") == "violates_flat_substrate_planes" for row in valid),
            "MAE_uN": sum(row["absolute_error_uN"] for row in valid)/len(valid) if valid else None,
            "RMSE_uN": math.sqrt(sum(row["error_uN"]**2 for row in valid)/len(valid)) if valid else None,
            "maximum_absolute_error_uN": max((row["absolute_error_uN"] for row in valid), default=None),
            "incomplete": len(valid) != len(scored)}


def envelope(cases, row, gamma, expected_count):
    failed = [case["case"] for case in cases if case["status"] != "refinement_checked"]
    intrusions = [case["case"] for case in cases if case["flat_plane_diagnostics"]["status"] == "violates_flat_substrate_planes"]
    wrong_normal = [case["case"] for case in cases if case["status"] == "refinement_checked"
                    and case["normal_force_uN_at_1N_per_m_diagnostic_only"] <= 0]
    valid = [case["restoring_shear_uN_at_1N_per_m"]*gamma for case in cases
             if case["status"] == "refinement_checked" and gamma is not None]
    complete = len(cases) == expected_count and not failed and not intrusions and not wrong_normal and gamma is not None
    observed = row["observed_shear_interval_uN"]
    extent = [min(valid), max(valid)] if valid else None
    overlaps = max(extent[0], observed[0]) <= min(extent[1], observed[1]) if extent else None
    return {"status": "sampled_corners_complete" if complete else "inconclusive",
            "expected_count": expected_count, "attempted": len(cases), "failed_cases": failed,
            "substrate_intrusion_cases": intrusions,
            "incompatible_normal_direction_cases": wrong_normal,
            "sampled_force_extent_uN": extent,
            "observed_force_interval_intersects_sampled_extent": overlaps if complete else None,
            "interpretation": "Nonstatistical sampled sensitivity extent. Corners do not certify every interior extremum or a confidence level."}


def sensitivity_cases(rows, extraction):
    cases, index = [], {}
    for row in rows:
        prefix = row["id"]
        index[prefix] = {"geometry_volume": [], "geometry_only": [], "volume_only": [], "solidification": []}
        for factor in (.94, 1.06):
            name = prefix + "/volume-" + str(factor)
            cases.append((name, specification(row, MAPPINGS[0], extraction, volume_factor=factor)))
            index[prefix]["volume_only"].append(name)
        complete = all(value is not None for limits in row["input_bounds"].values() for value in limits)
        if complete:
            for h, x in itertools.product(row["input_bounds"]["h_um"], row["input_bounds"]["x_um"]):
                name = prefix + f"/geometry-h{h:g}-x{x:g}"
                cases.append((name, specification(row, MAPPINGS[0], extraction, h_um=h, x_um=x)))
                index[prefix]["geometry_only"].append(name)
                for factor in (.94, 1.06):
                    name = prefix + f"/corner-h{h:g}-x{x:g}-v{factor:g}"
                    cases.append((name, specification(row, MAPPINGS[0], extraction, volume_factor=factor, h_um=h, x_um=x)))
                    index[prefix]["geometry_volume"].append(name)
        name = prefix + "/geometry-systematic-1.015"
        cases.append((name, specification(row, MAPPINGS[0], extraction, coordinate_factor=1.015)))
        index[prefix]["solidification"].append(name)
    return cases, index


def markdown(report):
    lines = ["# Frozen physical comparison", "", report["verdict"], "",
             "The primary source is [Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827), DOI `10.1115/1.1463732`, Figure 5. The measured joints remain pinned at circular pad perimeters.", "",
             "The published flat-plane approximation uses measured interface separation as model gap and adds both 5 micrometer copper-pad slabs to solder volume. The literal rim mapping is a separate sensitivity. The uncorrected interface mapping is an intentionally wrong negative control.", "",
             "Normal-force magnitude is diagnostic only. Figure 5 has no specimen-specific normal-load table. The 1.95 mN value belongs to a different set. No force-ratio validation is reported. The known downward applied load does require an upward joint reaction; that sign supplies a separate physical diagnostic.", "",
             "## Central primary predictions", "",
             "The observed shear center is the mean of the two readings of the same plotted load. Its bound is the union of their digitization intervals. Both alternative pairings at 112 micronewtons remain in the report.", "",
             "| Pair | Phase | Observed shear µN | Numerical status | Shear at 0.48 N/m µN | Shear at published-fit 0.4 N/m µN | Held-out-calibrated shear µN |", "|---|---|---:|---|---:|---:|---:|"]
    def value(number):
        return "inconclusive" if number is None else f"{number:.4f}"
    for row in report["rows"]:
        tracks = row["mappings"][MAPPINGS[0]]["scores"]
        lines.append(f"| {row['id']} | {row['phase']} | {row['observed_shear_uN']:.2f} | {row['mappings'][MAPPINGS[0]]['status']} | {value(tracks['prior_default'].get('predicted_shear_uN'))} | {value(tracks['published_fit'].get('predicted_shear_uN'))} | {value(tracks['held_out'].get('predicted_shear_uN'))} |")
    fit = report["held_out_calibration"]
    lines += ["", f"The frozen low-force fit has status `{fit['status']}` and gamma `{fit['gamma_N_per_m']}` N/m. Only h1-x1, h2-x2, and h3-x3 enter this zero-intercept fit. No high-force row enters calibration.", "",
              "The published 0.4 N/m value was fitted to all physical data in the paper. Its agreement is calibration-dependent consistency. The inherited 0.48 N/m default is generic and uncalibrated for this process.", "",
              "| Duplicate pairing | Material track | Available-row MAE µN | Available-row RMSE µN | Held-out MAE µN | Held-out RMSE µN | Scored central rows |", "|---|---|---:|---:|---:|---:|---:|"]
    for pairing, mappings in report["aggregates"].items():
        for track, phases in mappings[MAPPINGS[0]].items():
            all_rows, held_out = phases["all"], phases["held_out"]
            lines.append(f"| {pairing} | {track} | {value(all_rows['MAE_uN'])} | {value(all_rows['RMSE_uN'])} | {value(held_out['MAE_uN'])} | {value(held_out['RMSE_uN'])} | {all_rows['scored']}/6 |")
    lines += ["", "Incomplete aggregate metrics describe only the scored subset. They do not establish agreement for the missing specimens.", "",
              "## Held-out errors and sensitivity", "",
              "Errors below use the single gamma fitted on the three low-force central rows. The eight corners vary the plotted height and offset bounds, digitization bounds, and solder volume by plus or minus 6 percent. Pad-slab volume stays fixed. These are nonstatistical sensitivities. No confidence coverage is claimed.", "",
              "| Pair | Central error µN | Relative error % | Sampled geometry+volume extent µN | Observed interval overlap | Sensitivity status |", "|---|---:|---:|---|---|---|"]
    for row in report["rows"]:
        if row["phase"] != "held_out":
            continue
        track = row["mappings"][MAPPINGS[0]]["scores"]["held_out"]
        sensitivity = row.get("sensitivities", {}).get("held_out", {}).get("geometry_volume", {})
        extent = sensitivity.get("sampled_force_extent_uN")
        lines.append(f"| {row['id']} | {value(track.get('error_uN'))} | {value(track.get('relative_error')*100 if 'relative_error' in track else None)} | {str([round(x, 4) for x in extent]) if extent else 'not run'} | {sensitivity.get('observed_force_interval_intersects_sampled_extent')} | {sensitivity.get('status', 'not run')} |")
    lines += ["", "The h1-x1 lower offset error bar is clipped. Its missing bound is not replaced with a fabricated zero or a symmetric guess. Its complete geometry sensitivity remains inconclusive. Geometry-only and volume-only samples are reported separately in predictions.json. The 1.5 percent increase in both measured coordinates is a separate systematic scenario. It is not added as an independent random error or combined with a second shrinkage correction.", "",
              "## Normal-load direction", "",
              "Independent review identified this diagnostic after the frozen predictions. It changes no inputs, fitted parameters, or prespecified score. The weighted upper wafer applies a downward normal load, so the reaction on the upper pad must point upward. Every positive surface tension preserves the modeled force direction. At the central measured geometries, h4-x4 and h4-x5 predict downward reactions of 5675.29 and 6084.38 micronewtons at 1 N/m. Both are incompatible with that known load direction under the paper's equal per-joint interpretation. The conclusion holds under either duplicate pairing. It does not reject every uncertain geometry or volume. Missing normal-load magnitudes still prevent a force-magnitude or force-ratio score.", "",
              "## Flat substrate constraints", "",
              "The current model fixes the circular rims but does not constrain every side-surface vertex between the two solid planes. A numerically stable shape can therefore enter a solid substrate. Detected intrusion makes a physical comparison inconclusive under the paper's flat-substrate approximation. The raw conditional force residual is retained.", "",
              "| Pair | Sampled plane status | Lower excursion µm | Upper excursion µm |", "|---|---|---:|---:|"]
    for row in report["rows"]:
        geometry = row["mappings"][MAPPINGS[0]]["flat_plane_diagnostics"]
        lines.append(f"| {row['id']} | {geometry['status']} | {value(geometry.get('lower_excursion_um'))} | {value(geometry.get('upper_excursion_um'))} |")
    lines += ["", "The plane check uses a 1e-9 mm arithmetic tolerance. This is not a physical acceptance tolerance. It examines exported vertices and can detect intrusion. Absence of a sampled violation does not prove the continuous curved surface is admissible. Radial positions and example violating coordinates are stored with each result. No normal-force accuracy is inferred from local stability.", "",
              "## Coverage and limits", "",
              f"Central numerical statuses are `{json.dumps(report['central_status_counts'], sort_keys=True)}`. Sensitivity numerical statuses are `{json.dumps(report['sensitivity_status_counts'], sort_keys=True)}`. The two-gamma public-solver check has status `{report['surface_tension_scaling_check']['status']}`.", "",
              "Aggregate errors use six specimens for each pairing assignment. The duplicate assignments are not pooled as four independent specimens. Complete paired results, all numerical failures, and each negative control remain in predictions.json and predictions.csv.", "",
              "A sampled corner extent does not certify that the nonlinear function has no interior extremum. The calibration gamma's uncertainty is not propagated into the held-out extent. The low-force offset uncertainty is large. Same-process surface tension, individual ball volumes, specimen pairing, and molten geometry remain unidentified. Post-solidification geometry may differ from molten equilibrium.", "",
              "Numerical convergence certifies the recorded local checks. It does not certify global minimum shape, solid-plane admissibility, physical pinning, or same-process material accuracy. A failed or substrate-intruding corner makes that sensitivity result inconclusive. A central failed calibration row prevents the held-out fit. The 144 micronewton point is retained.", "",
              "## Reproduce", "", "```sh", "python3 tools/validate_physical.py --stage full --workers 2", "```", "",
              "The runner uses public solve calls. Receipts contain inputs, numerical levels, the mesh, model text, engine commands, stdout, stderr, and code and data hashes. Cache entries require the same physical input, solver code, model code, and engine binary. Use `--refresh` to repeat the computations. `--stage central` repeats only central mappings and the two-gamma scaling check.", "",
              "The pre-repair comparison remains in prediction-receipts/baseline-predictions.json and baseline-validation-report.md. Its numerical failures are preserved. Early primary-case receipts retain the failed engine output.", "",
              "Model the Domain changed each observation into one paired record with explicit uncertainty and pairing identity. Prove It Works changed validation into a public-solver replay with raw receipts. Explain the Number changed aggregate reporting into separate calibration, held-out, sensitivity, and numerical-status results.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("central", "full"), default="full")
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    extraction = json.loads((DIRECTORY / "nist-extraction.json").read_text())
    protocol = json.loads((DIRECTORY / "protocol.json").read_text())
    if protocol.get("frozen_before_predictions") is not True:
        raise SystemExit("The physical protocol must be frozen before predictions.")
    identity = provenance()
    if not identity["engine"].get("ready"):
        raise SystemExit(identity["engine"].get("error"))
    RECEIPTS.mkdir(exist_ok=True)
    rows = observations(extraction)
    central_cases = [(mapping + "/" + row["id"], specification(row, mapping, extraction))
                     for mapping in MAPPINGS for row in rows]
    central = run_cases(central_cases, identity, args.workers, args.refresh)
    fit = fit_gamma(rows, central)
    gammas = {**TRACKS, "held_out": fit["gamma_N_per_m"]}
    scaling_spec = specification(rows[1], MAPPINGS[0], extraction)
    scaling = run_cases([("scaling/gamma-0.4", replace(scaling_spec, surface_tension_n_m=.4))], identity, 1, args.refresh)
    reference = central[MAPPINGS[0] + "/" + rows[1]["id"]]
    actual = scaling["scaling/gamma-0.4"]
    differences = {}
    if reference["status"] == actual["status"] == "refinement_checked":
        for axis in ("x_uN", "z_uN"):
            differences[axis] = actual["forces"][axis]/(.4*reference["forces"][axis])-1
    scaling_check = {"reference_case": reference["case"], "actual_gamma_0_4_solve": actual,
                     "force_relative_deviation_from_exact_scaling": differences,
                     "status": "numerically_checked" if differences and max(abs(x) for x in differences.values()) < .001 else "inconclusive"}
    sensitivities, index = {}, {}
    if args.stage == "full":
        cases, index = sensitivity_cases(rows, extraction)
        sensitivities = run_cases(cases, identity, args.workers, args.refresh)
    for row in rows:
        row["mappings"] = {}
        for mapping in MAPPINGS:
            case = central[mapping + "/" + row["id"]]
            row["mappings"][mapping] = {**case, "scores": {name: score(case, row, gamma) for name, gamma in gammas.items()}}
        if args.stage == "full":
            row["sensitivity_cases"] = {kind: [sensitivities[name] for name in names] for kind, names in index[row["id"]].items()}
            row["sensitivities"] = {track: {kind: envelope(row["sensitivity_cases"][kind], row, gamma, count)
                                          for kind, count in (("geometry_volume", 8), ("geometry_only", 4), ("volume_only", 2))}
                                    for track, gamma in gammas.items()}
            row["solidification_systematic"] = {track: score(row["sensitivity_cases"]["solidification"][0], row, gamma)
                                                for track, gamma in gammas.items()}
    aggregates = {}
    unambiguous = [row["id"] for row in rows if row["pairing"] == "unambiguous"]
    by_id = {row["id"]: row for row in rows}
    for number, option in enumerate(extraction["duplicate_pairing_options"], 1):
        ids = unambiguous + ["-".join(pair) for pair in option]
        aggregates["duplicate_pairing_" + str(number)] = {
            mapping: {track: {phase: aggregate([by_id[id]["mappings"][mapping]["scores"][track] for id in ids
                                              if phase == "all" or by_id[id]["phase"] == phase])
                              for phase in ("all", "calibration", "held_out")}
                      for track in gammas}
            for mapping in MAPPINGS}
    final_identity = provenance()
    if final_identity != identity:
        raise SystemExit("Input code, engine, script, or frozen data changed during validation. Preserved receipts are versioned. Rerun on the current version.")
    report = {"schema": 1, "generated_at_UTC": datetime.now(timezone.utc).isoformat(), "stage": args.stage,
              "provenance": identity, "source": {key: extraction[key] for key in ("source_url", "source_sha256", "doi", "figure")},
              "held_out_calibration": fit, "surface_tension_scaling_check": scaling_check,
              "rows": rows, "aggregates": aggregates,
              "central_status_counts": {status: sum(case["status"] == status for case in central.values()) for status in sorted({case["status"] for case in central.values()})},
              "post_prediction_normal_direction_diagnostic": "Added after independent review. A positive normal reaction on the upper pad is required by the known downward weight. Sign is independent of any positive gamma. This does not supply the missing force magnitude or reject all uncertain geometries.",
              "primary_status_counts": {status: sum(row["mappings"][MAPPINGS[0]]["status"] == status for row in rows)
                                        for status in sorted({row["mappings"][MAPPINGS[0]]["status"] for row in rows})},
              "sensitivity_status_counts": {status: sum(case["status"] == status for case in sensitivities.values()) for status in sorted({case["status"] for case in sensitivities.values()})},
              "central_flat_plane_status_counts": {status: sum(case["flat_plane_diagnostics"]["status"] == status for case in central.values())
                                                   for status in sorted({case["flat_plane_diagnostics"]["status"] for case in central.values()})},
              "sensitivity_flat_plane_status_counts": {status: sum(case["flat_plane_diagnostics"]["status"] == status for case in sensitivities.values())
                                                       for status in sorted({case["flat_plane_diagnostics"]["status"] for case in sensitivities.values()})},
              "verdict": "General absolute physical accuracy remains inconclusive. Raw force residuals are conditional on the declared mappings. Unresolved numerical cases, substrate intrusion, calibration dependence, and missing specimen and material information prevent a physical pass."}
    write_json(DIRECTORY / "predictions.json", report)
    with (DIRECTORY / "predictions.csv").open("w", newline="") as target:
        fields = ["id", "phase", "pairing", "mapping", "track", "gamma_N_per_m", "observed_shear_uN", "h_um", "x_um", "model_gap_mm", "model_volume_mm3", "numerical_status", "score_status", "predicted_shear_uN", "error_uN", "relative_error", "physical_comparison_status", "flat_plane_status", "lower_excursion_um", "upper_excursion_um", "normal_force_uN_diagnostic_only", "receipt"]
        writer = csv.DictWriter(target, fields)
        writer.writeheader()
        for row in rows:
            for mapping, case in row["mappings"].items():
                for track, scored in case["scores"].items():
                    writer.writerow({"id": row["id"], "phase": row["phase"], "pairing": row["pairing"], "mapping": mapping, "track": track,
                                     "gamma_N_per_m": gammas[track], "observed_shear_uN": row["observed_shear_uN"], "h_um": row["h_um"], "x_um": row["x_um"],
                                     "model_gap_mm": case["input"]["standoff_mm"], "model_volume_mm3": case["input"]["volume_mm3"],
                                     "numerical_status": case["status"], "score_status": scored["status"], "predicted_shear_uN": scored.get("predicted_shear_uN"),
                                     "error_uN": scored.get("error_uN"), "relative_error": scored.get("relative_error"),
                                     "physical_comparison_status": scored.get("physical_comparison_status"), "flat_plane_status": case["flat_plane_diagnostics"]["status"],
                                     "lower_excursion_um": case["flat_plane_diagnostics"].get("lower_excursion_um"), "upper_excursion_um": case["flat_plane_diagnostics"].get("upper_excursion_um"),
                                     "normal_force_uN_diagnostic_only": case["normal_force_uN_at_1N_per_m_diagnostic_only"]*gammas[track] if gammas[track] is not None and case["normal_force_uN_at_1N_per_m_diagnostic_only"] is not None else None,
                                     "receipt": case["receipt"]})
    (DIRECTORY / "validation-report.md").write_text(markdown(report))
    print(json.dumps({"report": "evidence/physical/predictions.json", "central_status_counts": report["central_status_counts"],
                      "sensitivity_status_counts": report["sensitivity_status_counts"], "held_out_calibration": fit,
                      "verdict": report["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
