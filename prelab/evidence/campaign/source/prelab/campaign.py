"""Run and independently verify declared coupon stress scenarios."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.model import LoadSpec
from soldershape.solver import engine_info, solve
from coupons.tools.analyze import analytical

SOURCES = ("prelab/campaign.py", "prelab/protocol.json", "soldershape/model.py",
           "soldershape/solver.py", "coupons/tools/analyze.py", "coupons/experiment.json")


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def sha(content):
    return hashlib.sha256(content).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


@dataclass(frozen=True)
class CouponRequest:
    spec: LoadSpec
    correction_um: float


def request(protocol, scenario, arm, mapping):
    values = {**scenario["common"], **scenario["arms"].get(arm, {})}
    parameters = protocol["parameters"]
    lower = parameters["lower_nominal_mm"][arm] + values["lower_bias_um"] / 1000
    upper = parameters["upper_nominal_mm"] + values["upper_bias_um"] / 1000
    liquid = math.pi / 6 * (values["sphere_diameter_um"] / 1000)**3 * values["liquid_volume_factor"]
    fraction = protocol["boundaries"][mapping]["depth_fraction"]
    lower_depth = fraction * values["lower_metal_um"] / 1000
    upper_depth = fraction * values["upper_metal_um"] / 1000
    envelope = liquid + math.pi / 4 * (lower**2 * lower_depth + upper**2 * upper_depth)
    spec = LoadSpec(lower_diameter_mm=lower, upper_diameter_mm=upper, volume_mm3=envelope,
                    offset_mm=values["offset_mm"],
                    normal_load_uN=values["cap_mass_mg"] * parameters["g_m_s2"] / parameters["joint_count"],
                    surface_tension_n_m=values.get("gamma_n_m", parameters["gamma_n_m"]),
                    density_g_cm3=parameters["density_g_cm3"], gravity=False)
    return CouponRequest(spec, 1000 * (lower_depth + upper_depth))


def plan(protocol):
    rows, jobs = [], {}
    if protocol["domain"] != "actual_SS-C220-C270-R1_coupon":
        raise ValueError("This campaign requires the actual coupon domain, not published Table 3.")
    ids = [row["id"] for row in protocol["scenarios"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Scenario identifiers must be unique.")
    for scenario in protocol["scenarios"]:
        for mapping in protocol["boundaries"]:
            for arm in protocol["parameters"]["lower_nominal_mm"]:
                item = request(protocol, scenario, arm, mapping)
                jobs[item.spec.sha256] = item.spec.to_dict()
                rows.append({"scenario": scenario["id"], "group": scenario["group"], "arm": arm,
                             "mapping": mapping, "request_sha256": item.spec.sha256,
                             "correction_um": item.correction_um})
    control = LoadSpec(**{**request(protocol, protocol["scenarios"][0], "C220", "literal_rims").spec.to_dict(),
                          "normal_load_uN": protocol["native_controls"]["unattainable_load_uN"]})
    jobs[control.sha256] = control.to_dict()
    return {"rows": rows, "jobs": jobs, "negative_control": control.sha256}


def accepted(result):
    return (result.get("status") == "refinement_checked"
            and result.get("load_balance", {}).get("status") == "balanced"
            and not result.get("model_warnings"))


def summarize(protocol, table, results):
    pairs = []
    for scenario in protocol["scenarios"]:
        for mapping in protocol["boundaries"]:
            arms = {}
            for arm in protocol["parameters"]["lower_nominal_mm"]:
                item = request(protocol, scenario, arm, mapping)
                result = results[item.spec.sha256]
                good = accepted(result)
                gap = result["equilibrium"]["standoff_mm"] * 1000 - item.correction_um if good else None
                approximate = analytical(item.spec, item.correction_um)["gap_um"]
                arms[arm] = {"status": result["status"], "accepted_numerically": good,
                             "gap_um": gap, "analytical_gap_um": approximate,
                             "native_minus_analytical_um": gap - approximate if good else None,
                             "numerical_threshold_margin_um": gap - protocol["objectives"]["pad_face_gap_threshold_um"] if good else None,
                             "request_sha256": item.spec.sha256}
            complete = all(row["accepted_numerically"] for row in arms.values())
            difference = arms["C220"]["gap_um"] - arms["C270"]["gap_um"] if complete else None
            pairs.append({"scenario": scenario["id"], "group": scenario["group"], "mapping": mapping,
                          "arms": arms, "C220_minus_C270_um": difference,
                          "ordering": "inconclusive" if difference is None else "C220_higher" if difference > 0 else "C270_higher" if difference < 0 else "equal",
                          "exceeds_requested_pair_measurement_budget": abs(difference) > protocol["objectives"]["paired_measurement_budget_um"] if complete else None})
    cross = []
    nominal = [row for row in pairs if row["scenario"] == "nominal"]
    for a in nominal:
        for b in nominal:
            x, y = a["arms"]["C220"]["gap_um"], b["arms"]["C270"]["gap_um"]
            cross.append({"C220_mapping": a["mapping"], "C270_mapping": b["mapping"],
                          "C220_minus_C270_um": x-y if x is not None and y is not None else None,
                          "scope": "Different wetting states are hypotheses, not observed arm differences."})
    return {"schema": "soldershape.prelab.results.v1", "domain": protocol["domain"],
            "scope": protocol["scope"], "expanded_rows": len(table["rows"]), "distinct_requests": len(table["jobs"]),
            "accepted_distinct_requests": sum(accepted(result) for result in results.values()),
            "failed_distinct_requests": sum(not accepted(result) for result in results.values()),
            "negative_control": {"request_sha256": table["negative_control"],
                                 "rejected": not accepted(results[table["negative_control"]]),
                                 "status": results[table["negative_control"]]["status"]},
            "pairs": pairs, "nominal_cross_boundary_pairs": cross,
            "physical_qualification": "unqualified",
            "whole_cap_minimum_clearance": "not established",
            "hot_to_cold_transformation": "unqualified"}


def worker(request_path, destination):
    spec = LoadSpec(**read(request_path))
    producer = engine_info()
    try:
        result = solve(spec)
    except Exception as error:
        result = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "engine_failure",
                  "error": str(error), "evidence": getattr(error, "evidence", {}), "engine": engine_info()}
    result["producer_engine"] = producer
    with gzip.open(destination, "wb") as stream:
        stream.write(encode(result))


def validate_native_result(result, spec, key, engine):
    if result.get("input") != spec or result.get("input_sha256") != key:
        raise ValueError("Native receipt input differs from the declared request.")
    if result.get("status") == "refinement_checked" and not result.get("engine"):
        raise ValueError("Numerically checked native result requires its engine identity.")
    for field in ("source_sha256", "binary_sha256"):
        if result.get("producer_engine", {}).get(field) != engine[field]:
            raise ValueError("Native receipt engine differs from campaign identity.")
        if result.get("engine") and result["engine"].get(field) != engine[field]:
            raise ValueError("Native result contradicts its producer engine.")


def load_results(directory, table, engine):
    results = {}
    for key, spec in table["jobs"].items():
        with gzip.open(directory / "receipts" / (key + ".json.gz"), "rb") as stream:
            result = json.load(stream)
        validate_native_result(result, spec, key, engine)
        results[key] = result
    return results


def run(directory, workers):
    if directory.exists():
        raise ValueError("Use a new output directory. Existing campaigns remain unchanged.")
    engine = engine_info()
    if not engine["ready"]:
        raise ValueError(engine)
    code = {name: (ROOT / name).read_bytes() for name in SOURCES}
    protocol = json.loads(code["prelab/protocol.json"])
    table = plan(protocol)
    directory.mkdir(parents=True)
    (directory / "receipts").mkdir()
    (directory / "requests").mkdir()
    for name, data in code.items():
        target = directory / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (directory / "plan.json").write_bytes(encode(table))
    for key, spec in table["jobs"].items():
        (directory / "requests" / (key + ".json")).write_bytes(encode(spec))

    def calculate(key):
        command = [sys.executable, str(Path(__file__).resolve()), "worker",
                   str(directory / "requests" / (key + ".json")), str(directory / "receipts" / (key + ".json.gz"))]
        subprocess.run(command, check=True, cwd=ROOT)
        return key

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(calculate, key) for key in table["jobs"]]
        for count, future in enumerate(as_completed(futures), 1):
            key = future.result()
            print(f"Completed {count}/{len(futures)} native requests {key[:12]}", flush=True)
    if any((ROOT / name).read_bytes() != content for name, content in code.items()):
        raise ValueError("Calculation source changed during campaign. Partial evidence retained.")
    if engine_info() != engine:
        raise ValueError("Native engine identity changed during campaign.")
    report = summarize(protocol, table, load_results(directory, table, engine))
    (directory / "report.json").write_bytes(encode(report))
    files = {str(path.relative_to(directory)): sha(path.read_bytes()) for path in directory.rglob("*") if path.is_file()}
    manifest = {"schema": "soldershape.prelab.manifest.v1", "files": files, "engine": engine,
                "source_sha256": {name: sha(data) for name, data in code.items()},
                "expanded_rows": len(table["rows"]), "distinct_requests": len(table["jobs"]),
                "scope": "Local integrity and numerical scenario verification. No trusted timestamp, signature, interval proof or physical validation."}
    (directory / "manifest.json").write_bytes(encode(manifest))
    return verify(directory)


def verify(directory):
    manifest = read(directory / "manifest.json")
    actual = {str(path.relative_to(directory)) for path in directory.rglob("*") if path.is_file()}
    if actual != {*manifest["files"], "manifest.json"}:
        raise ValueError("Campaign member set differs, including missing or extra receipts.")
    for name, digest in manifest["files"].items():
        path = directory / name
        if not path.resolve().is_relative_to(directory.resolve()) or sha(path.read_bytes()) != digest:
            raise ValueError("Campaign member hash differs: " + name)
    for name in SOURCES:
        if (sha((ROOT / name).read_bytes()) != manifest["source_sha256"][name]
                or sha((directory / "source" / name).read_bytes()) != manifest["source_sha256"][name]):
            raise ValueError("Current calculation source differs: " + name)
    protocol = read(directory / "source/prelab/protocol.json")
    table = plan(protocol)
    if table != read(directory / "plan.json"):
        raise ValueError("Request accounting differs from archived protocol.")
    for key, spec in table["jobs"].items():
        if read(directory / "requests" / (key + ".json")) != spec:
            raise ValueError("Native request changed.")
    results = load_results(directory, table, manifest["engine"])
    expected = summarize(protocol, table, results)
    if expected != read(directory / "report.json"):
        raise ValueError("Reported conclusion differs from verified native receipts.")
    if manifest["expanded_rows"] != len(table["rows"]) or manifest["distinct_requests"] != len(table["jobs"]):
        raise ValueError("Manifest count differs from protocol.")
    return {"passed": True, "expanded_rows": len(table["rows"]), "distinct_requests": len(table["jobs"]),
            "accepted_requests": expected["accepted_distinct_requests"], "failed_requests": expected["failed_distinct_requests"],
            "negative_control_rejected": expected["negative_control"]["rejected"], "physical_qualification": "unqualified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "verify"):
        child = commands.add_parser(name)
        child.add_argument("directory", type=Path)
        if name == "run":
            child.add_argument("--workers", type=int, choices=(1, 2, 3, 4), default=2)
    child = commands.add_parser("worker")
    child.add_argument("request", type=Path)
    child.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "worker":
        worker(args.request, args.destination)
        return
    result = run(args.directory.resolve(), args.workers) if args.command == "run" else verify(args.directory.resolve())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
