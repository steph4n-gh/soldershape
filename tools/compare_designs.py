"""Replay the declared fixed-gap solder-volume decision through the public solver."""

import argparse
import csv
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import make_bundle, read_bundle
from soldershape.model import InputError, parse_case, request_from_footprint
from soldershape.solver import SolverError, engine_info, solve


@dataclass(frozen=True)
class Candidate:
    identifier: str
    volume_mm3: float


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def integrate(function, intervals=1024):
    step = 2 * math.pi / intervals
    return step / 3 * (function(0) + function(2 * math.pi)
                       + sum((4 if index % 2 else 2) * function(index * step)
                             for index in range(1, intervals)))


def cylinder_baseline(spec):
    radius = math.sqrt(spec.volume_mm3 / (math.pi * spec.standoff_mm))
    height, offset = spec.standoff_mm, spec.offset_mm
    length = lambda theta: math.sqrt(height * height + (offset * math.cos(theta)) ** 2)
    area = radius * integrate(length)
    derivative_x = radius * integrate(lambda theta: offset * math.cos(theta) ** 2 / length(theta))
    derivative_z = radius * integrate(lambda theta: height / length(theta) - length(theta) / (2 * height))
    scale = -1000 * spec.surface_tension_n_m
    return {"area_mm2": area, "effective_radius_mm": radius,
            "pad_radius_difference_mm": radius - spec.lower_diameter_mm / 2,
            "forces": {"x_uN": scale * derivative_x, "z_uN": scale * derivative_z},
            "gravity_included": False}


def check_baseline(spec, acceptance):
    baseline = cylinder_baseline(spec)
    differences = {}
    for axis, field in (("x", "offset_mm"), ("z", "standoff_mm")):
        displacement = 1e-5 * max(abs(getattr(spec, field)), .01)
        above = cylinder_baseline(replace(spec, **{field: getattr(spec, field) + displacement}))
        below = cylinder_baseline(replace(spec, **{field: getattr(spec, field) - displacement}))
        force = -1000 * spec.surface_tension_n_m * (above["area_mm2"] - below["area_mm2"]) / (2 * displacement)
        differences[axis] = abs(force / baseline["forces"][axis + "_uN"] - 1)
    aligned = cylinder_baseline(replace(spec, offset_mm=0))
    expected = -math.pi * spec.surface_tension_n_m * 1000 * aligned["effective_radius_mm"]
    cylinder_error = abs(aligned["forces"]["z_uN"] / expected - 1)
    passed = (max(differences.values()) <= acceptance["baseline_derivative_relative_tolerance"]
              and cylinder_error <= acceptance["baseline_cylinder_limit_relative_tolerance"]
              and aligned["forces"]["x_uN"] == 0)
    return {"passed": passed, "area_derivative_relative_errors": differences,
            "aligned_cylinder_z_relative_error": cylinder_error,
            "interpretation": "Checks the approximation's implementation. It does not qualify the approximation for pinned solder joints."}


def envelope(mesh, pitch):
    vertices = mesh["vertices_mm"]
    lower = [min(vertex[axis] for vertex in vertices) for axis in (0, 1)]
    upper = [max(vertex[axis] for vertex in vertices) for axis in (0, 1)]
    clearance = min(pitch / 2 + lower[0], pitch / 2 - upper[0],
                    pitch / 2 + lower[1], pitch / 2 - upper[1])
    return {"xy_min_mm": lower, "xy_max_mm": upper, "pitch_cell_clearance_mm": clearance,
            "scope": "Axis-aligned pitch cell centered on the board pad. This screen does not model adjacent joints or wetting."}


def compute(spec, identity, receipts, refresh):
    key = hashlib.sha256(json.dumps({"input": spec.to_dict(), "identity": identity}, sort_keys=True).encode()).hexdigest()
    path = receipts / (key + ".json.gz")
    cached = path.exists() and not refresh
    if cached:
        with gzip.open(path, "rt") as stream:
            receipt = json.load(stream)
        if receipt["identity"] != identity or receipt["result"]["input"] != spec.to_dict():
            raise InputError("A cached receipt does not match its identity.")
        result = receipt["result"]
    else:
        try:
            result = solve(spec)
        except SolverError as error:
            result = {"input": spec.to_dict(), "input_sha256": spec.sha256,
                      "status": "failed", "error": error.message, "evidence": error.evidence}
        with gzip.open(path, "wt") as stream:
            json.dump({"identity": identity, "result": result}, stream, allow_nan=False)
    return result, {"path": str(path.relative_to(ROOT)), "sha256": digest(path), "cached": cached}


def summarize_candidate(candidate, rows, acceptance):
    checked = all(row["status"] == acceptance["every_case_status"] for row in rows)
    restoring = checked and all(row["restoring_x_uN"] > 0 for row in rows)
    no_upward = checked and all(row["force_z_uN"] <= acceptance["eligible_maximum_z_force_uN"] for row in rows)
    inside = checked and all(row["pitch_cell_clearance_mm"] >= acceptance["eligible_minimum_pitch_cell_clearance_mm"] for row in rows)
    eligible = checked and restoring and no_upward and inside
    valid = [row for row in rows if row["status"] == "refinement_checked"]
    baseline_eligible = all(row["baseline_force_z_uN"] <= 0 and row["baseline_restoring_x_uN"] > 0
                            and row["baseline_pitch_cell_clearance_mm"] >= 0 for row in rows)
    return {"candidate": candidate.identifier, "nominal_volume_mm3": candidate.volume_mm3,
            "tested_scenarios": len(rows), "all_numerically_checked": checked,
            "all_restoring": restoring, "no_upward_force_in_samples": no_upward,
            "inside_pitch_cell_in_samples": inside, "eligible": eligible,
            "minimum_restoring_x_uN": min((row["restoring_x_uN"] for row in valid), default=None),
            "maximum_restoring_x_uN": max((row["restoring_x_uN"] for row in valid), default=None),
            "force_z_extent_uN": [min(row["force_z_uN"] for row in valid), max(row["force_z_uN"] for row in valid)] if valid else None,
            "minimum_pitch_cell_clearance_mm": min((row["pitch_cell_clearance_mm"] for row in valid), default=None),
            "baseline_eligible": baseline_eligible,
            "baseline_minimum_restoring_x_uN": min(row["baseline_restoring_x_uN"] for row in rows)}


def report_text(report):
    numerical = report["numerical_summary"]
    refinement = (f'Observed refinement changes are at most {numerical["maximum_lateral_refinement_change_uN"]:.6f} µN laterally and {numerical["maximum_axial_refinement_change_uN"]:.6f} µN axially.'
                  if numerical["maximum_lateral_refinement_change_uN"] is not None
                  else "No candidate has a qualified force result.")
    checked_count = sum(row["status"] == "refinement_checked" for row in report["cases"] + report["gravity_controls"]["cases"])
    lines = ["# Solder-volume comparison at a prescribed gap", "", report["protocol"]["decision"], "",
             "This is a conditional volume-screening example. The separating-load rule and the volume tolerance are declared assumptions.", "",
             "| Nominal volume, mm³ | Restoring force range, µN | Axial force range, µN | Minimum cell clearance, mm | Eligible in tested scenarios |",
             "| --- | --- | --- | --- | --- |"]
    for row in report["candidates"]:
        lateral = "inconclusive" if row["minimum_restoring_x_uN"] is None else f'{row["minimum_restoring_x_uN"]:.3f} to {row["maximum_restoring_x_uN"]:.3f}'
        vertical = "inconclusive" if row["force_z_extent_uN"] is None else " to ".join(f"{value:.3f}" for value in row["force_z_extent_uN"])
        clearance = "inconclusive" if row["minimum_pitch_cell_clearance_mm"] is None else f'{row["minimum_pitch_cell_clearance_mm"]:.5f}'
        lines.append(f'| {row["nominal_volume_mm3"]:.3f} | {lateral} | {vertical} | {clearance} | {row["eligible"]} |')
    lines.extend(["", "Positive axial force separates the pads. Negative axial force pulls the pads together. Lateral force is reported as a positive restoring magnitude at the positive imposed offset.", "",
                  report["selection"]["explanation"], "", report["baseline_comparison"]["interpretation"], "",
                  f'The comparison contains {report["scenario_count"]} volume scenarios at {report["distinct_design_input_count"]} distinct inputs. Three additional nominal-volume controls turn gravity off. The numerical checks pass for {checked_count} of the 18 scenarios, including repeated inputs.', "",
                  refinement + " These changes estimate sensitivity to mesh refinement. They do not bound physical error.", "",
                  "The sheared-cylinder approximation has a volume-dependent effective radius. It does not preserve the fixed wetted rim. Its predicted forces are useful as a cheap competing calculation, but the changed radius makes its failure informative about the boundary condition.", "",
                  report["gravity_controls"]["interpretation"], "",
                  "The numerical status checks refinement, equilibrium stationarity, volume conservation, and export topology. It does not establish physical accuracy for the chosen alloy, temperature, and flux.", "",
                  report["protocol"]["volume_uncertainty"], "", report["protocol"]["scope"], "",
                  report["protocol"]["component_volume_note"], "",
                  "A different separating-load requirement can select a different volume. These results do not predict free assembly height, placement yield, or alignment time.", "",
                  "Reproduce the run with the source and engine identity in `comparison.json`.", "", "```sh",
                  f'python3 tools/compare_designs.py --solver-sha256 {report["identity"]["files"]["soldershape/solver.py"]}',
                  "```", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=ROOT / "examples" / "design-comparison.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "design-comparison")
    parser.add_argument("--solver-sha256", required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    args.protocol = args.protocol.resolve()
    args.output = args.output.resolve()
    solver_path = ROOT / "soldershape" / "solver.py"
    if digest(solver_path) != args.solver_sha256:
        parser.error("The solver does not match the explicitly selected revision.")
    protocol = json.loads(args.protocol.read_text())
    if protocol["schema"] != 1:
        parser.error("Unsupported comparison protocol schema.")
    candidates = [Candidate(row["id"], row["volume_mm3"]) for row in protocol["candidates"]]
    if len(candidates) != 3 or len({row.identifier for row in candidates}) != len(candidates):
        parser.error("This frozen comparison requires three distinct candidates.")
    factors = protocol["volume_factors"]
    if factors != [.9, .95, 1, 1.05, 1.1]:
        parser.error("This frozen comparison requires its five declared volume scenarios.")
    source_path = ROOT / protocol["footprint"]
    source = source_path.read_text()
    spec, footprint = request_from_footprint(source, protocol["pad_index"], protocol["parameters"])
    if spec.offset_mm <= 0 or spec.lower_diameter_mm != spec.upper_diameter_mm:
        parser.error("The cylinder comparison requires equal circular pads and a positive offset.")
    baseline_checks = check_baseline(spec, protocol["acceptance"])
    if not baseline_checks["passed"]:
        parser.error("The analytic approximation failed its derivative checks.")
    files = (Path(__file__), args.protocol, solver_path, ROOT / "soldershape" / "model.py",
             ROOT / "soldershape" / "artifacts.py", source_path)
    identity = {"files": {str(path.relative_to(ROOT)): digest(path) for path in files}, "engine": engine_info()}
    if not identity["engine"]["ready"]:
        parser.error(identity["engine"]["error"])
    args.output.mkdir(parents=True, exist_ok=True)
    receipts = args.output / "receipts"
    receipts.mkdir(exist_ok=True)
    write_json(args.output / "frozen-protocol.json", protocol)
    rows, summaries, bundles = [], [], []
    for candidate in candidates:
        candidate_rows, results = [], []
        for factor in factors:
            if digest(solver_path) != args.solver_sha256:
                raise InputError("The solver changed during the run. Existing receipts are preserved.")
            point = replace(spec, volume_mm3=candidate.volume_mm3 * factor)
            result, receipt = compute(point, identity, receipts, args.refresh)
            result["footprint"] = footprint
            results.append(result)
            baseline = cylinder_baseline(point)
            radius = baseline["effective_radius_mm"]
            baseline_clearance = protocol["pitch_mm"] / 2 - radius - point.offset_mm
            row = {"candidate": candidate.identifier, "nominal_volume_mm3": candidate.volume_mm3,
                   "volume_factor": factor, "actual_volume_mm3": point.volume_mm3,
                   "status": result["status"], "input_sha256": point.sha256,
                   "restoring_x_uN": None, "force_z_uN": None, "pitch_cell_clearance_mm": None,
                   "baseline_restoring_x_uN": -baseline["forces"]["x_uN"],
                   "baseline_force_z_uN": baseline["forces"]["z_uN"],
                   "baseline_effective_radius_mm": radius,
                   "baseline_pad_radius_difference_mm": baseline["pad_radius_difference_mm"],
                   "baseline_pitch_cell_clearance_mm": baseline_clearance,
                   "receipt": receipt["path"], "receipt_sha256": receipt["sha256"], "cached": receipt["cached"],
                   "force_refinement_absolute_x_uN": None, "force_refinement_absolute_z_uN": None,
                   "stationarity_energy_change_relative": None,
                   "error": result.get("error", "")}
            if "forces" in result:
                geometry = envelope(result["mesh"], protocol["pitch_mm"])
                changes = result["diagnostics"]["force_component_changes"]
                row.update(restoring_x_uN=-result["forces"]["x_uN"], force_z_uN=result["forces"]["z_uN"],
                           pitch_cell_clearance_mm=geometry["pitch_cell_clearance_mm"],
                           force_refinement_absolute_x_uN=changes["x"]["absolute_uN"],
                           force_refinement_absolute_z_uN=changes["z"]["absolute_uN"],
                           stationarity_energy_change_relative=result["diagnostics"]["stationarity_energy_change_relative"])
            rows.append(row)
            candidate_rows.append(row)
            print(json.dumps({key: row[key] for key in ("candidate", "volume_factor", "status", "restoring_x_uN", "force_z_uN")}), flush=True)
        summary = summarize_candidate(candidate, candidate_rows, protocol["acceptance"])
        bundle_path = args.output / (candidate.identifier + ".zip")
        bundle_path.write_bytes(make_bundle(results, source))
        reopened = read_bundle(bundle_path)
        if len(reopened) != len(results) or any(saved["input_sha256"] != result["input_sha256"] for (_, saved), result in zip(reopened, results)):
            raise InputError("The saved comparison bundle does not reopen as the computed cases.")
        bundles.append({"candidate": candidate.identifier, "path": str(bundle_path.relative_to(ROOT)),
                        "sha256": digest(bundle_path), "reopened_cases": len(reopened)})
        summaries.append(summary)
    gravity_rows, gravity_results = [], []
    for candidate in candidates:
        point = replace(spec, volume_mm3=candidate.volume_mm3, gravity=False)
        result, receipt = compute(point, identity, receipts, args.refresh)
        result["footprint"] = footprint
        gravity_results.append(result)
        nominal = next(row for row in rows if row["candidate"] == candidate.identifier and row["volume_factor"] == 1)
        gravity_rows.append({"candidate": candidate.identifier, "status": result["status"], "input_sha256": point.sha256,
                             "force_x_uN": result.get("forces", {}).get("x_uN"),
                             "force_z_uN": result.get("forces", {}).get("z_uN"),
                             "gravity_on_force_z_uN": nominal["force_z_uN"],
                             "axial_difference_uN": result.get("forces", {}).get("z_uN", 0) - (nominal["force_z_uN"] or 0) if "forces" in result else None,
                             "baseline_force_z_uN": nominal["baseline_force_z_uN"],
                             "receipt": receipt["path"], "receipt_sha256": receipt["sha256"], "cached": receipt["cached"]})
    gravity_path = args.output / "gravity-controls.zip"
    gravity_path.write_bytes(make_bundle(gravity_results, source))
    gravity_reopened = read_bundle(gravity_path)
    if len(gravity_reopened) != len(gravity_results):
        raise InputError("The no-gravity control bundle does not reopen.")
    bundles.append({"candidate": "gravity-controls", "path": str(gravity_path.relative_to(ROOT)),
                    "sha256": digest(gravity_path), "reopened_cases": len(gravity_reopened)})
    if any(digest(path) != identity["files"][str(path.relative_to(ROOT))] for path in files):
        raise InputError("A source file changed during the run. Receipts are preserved without publishing a mixed result.")
    eligible = [row for row in summaries if row["eligible"]]
    complete = (all(row["all_numerically_checked"] and row["all_restoring"] for row in summaries)
                and all(row["status"] == "refinement_checked" for row in gravity_rows))
    winner = max(eligible, key=lambda row: row["minimum_restoring_x_uN"]) if complete and eligible else None
    baseline_eligible = [row for row in summaries if row["baseline_eligible"]]
    baseline_winner = max(baseline_eligible, key=lambda row: row["baseline_minimum_restoring_x_uN"]) if baseline_eligible else None
    explanation = (f'The declared rule selects {winner["candidate"]}. Every tested scenario for this candidate passes the numerical checks and satisfies the nonseparating-load and pitch-cell constraints.'
                   if winner else "The declared rule does not select a candidate. A numerical failure or an empty feasible set makes the result inconclusive.")
    comparison = {"winner": baseline_winner["candidate"] if baseline_winner else None,
                  "different_selection": bool(winner and baseline_winner and winner["candidate"] != baseline_winner["candidate"]),
                  "interpretation": "The volume-equivalent sheared cylinder selects " + (baseline_winner["candidate"] if baseline_winner else "no candidate")
                  + ". Its force calculation does not enforce the fixed pad radius. Compare its axial-force signs with the solved pinned-rim shapes before using it for volume selection."}
    wrong_sign = [row["candidate"] for row in gravity_rows
                  if row["status"] == "refinement_checked" and row["force_z_uN"] * row["baseline_force_z_uN"] < 0]
    control_interpretation = ("With gravity disabled in both calculations, the approximation still predicts the wrong axial-force sign for "
                              + ", ".join(wrong_sign) + ". Omitting gravity does not explain this nominal sign disagreement."
                              if wrong_sign else "The no-gravity controls do not establish a nominal axial-sign disagreement.")
    valid = [row for row in rows if row["status"] == "refinement_checked"]
    editable_case = None
    if winner:
        case = parse_case({"schema": "soldershape.case.v1", "footprint_text": source,
                           "pad_index": protocol["pad_index"],
                           "parameters": {**protocol["parameters"], "volume_mm3": winner["nominal_volume_mm3"]},
                           "baseline": {"upper_diameter_mm": spec.upper_diameter_mm,
                                        "volume_mm3": protocol["parameters"]["volume_mm3"]}})
        case_path = args.output / "winning-case.soldershape.json"
        write_json(case_path, case)
        if parse_case(json.loads(case_path.read_text())) != case:
            raise InputError("The editable winning case does not reopen as its normalized inputs.")
        editable_case = {"path": str(case_path.relative_to(ROOT)), "sha256": digest(case_path),
                         "schema": case["schema"], "contains_computed_results": False}
    report = {"schema": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
              "identity": identity, "protocol": protocol, "baseline_checks": baseline_checks,
              "scenario_count": len(rows), "distinct_design_input_count": len({row["input_sha256"] for row in rows}),
              "distinct_solver_input_count": len({row["input_sha256"] for row in rows + gravity_rows}),
              "fresh_engine_run_count": sum(not row["cached"] for row in rows + gravity_rows),
              "cached_scenario_count": sum(row["cached"] for row in rows + gravity_rows),
              "candidates": summaries, "cases": rows,
              "numerical_summary": {"maximum_lateral_refinement_change_uN": max((row["force_refinement_absolute_x_uN"] for row in valid), default=None),
                                    "maximum_axial_refinement_change_uN": max((row["force_refinement_absolute_z_uN"] for row in valid), default=None),
                                    "maximum_stationarity_energy_change_relative": max((row["stationarity_energy_change_relative"] for row in valid), default=None)},
              "gravity_controls": {"cases": gravity_rows, "baseline_wrong_sign_without_gravity": wrong_sign,
                                   "interpretation": control_interpretation},
              "selection": {"status": "selected_under_declared_rule" if winner else "inconclusive", "candidate": winner["candidate"] if winner else None,
                            "existing_candidate": protocol["existing_candidate"], "explanation": explanation},
              "baseline_comparison": comparison, "bundles": bundles, "editable_case": editable_case,
              "passed": bool(complete and winner and baseline_checks["passed"])}
    write_json(args.output / "comparison.json", report)
    with (args.output / "cases.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "report.md").write_text(report_text(report))
    print(json.dumps({"selection": report["selection"], "passed": report["passed"], "cases": len(rows)}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InputError, OSError, ValueError, KeyError) as error:
        print("Comparison failed: " + str(error), file=sys.stderr)
        raise SystemExit(2)
