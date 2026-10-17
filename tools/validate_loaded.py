"""Forward predictions for the frozen external standoff table and declared design screen.

No measured height enters a solver request. Full failed and successful native
receipts are gzip-cached by code, engine and input identity. Product uses stdlib.
"""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.model import LoadSpec, spherical_gap_mm
from soldershape.solver import SolverError, engine_info, solve

DEST = ROOT / "evidence/model-repair"
DATA = DEST / "independent-evidence.json"
FROZEN_DATA = "febf6be52f0531e79ffc33b553ec8d79cc802bfc54a76438c3a7ce34e10c91d9"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(refresh=False):
    if digest(DATA) != FROZEN_DATA:
        raise RuntimeError("The frozen physical extraction changed. Preserve its identity before scoring.")
    dataset = json.loads(DATA.read_text())
    identity = {"data": FROZEN_DATA, "model": digest(ROOT / "soldershape/model.py"),
                "solver": digest(ROOT / "soldershape/solver.py"), "engine": engine_info()}
    campaign_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    cache = DEST / "loaded-receipts" / campaign_key
    if refresh:
        cache /= "refresh-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    cache.mkdir(parents=True, exist_ok=True)
    rows = []

    def calculate(record, scenario, gamma=.48, mapping="published", offset=0, gravity=False, volume_factor=1):
        lower = record["substrate_pad_diameter_um"]/1000
        volume = .01745*volume_factor
        thickness = .034 if mapping == "published" else 0
        volume += math.pi*(lower/2)**2*thickness
        spec = LoadSpec(lower, .28, volume, offset, 4, gamma, 9, gravity)
        key = spec.sha256
        receipt = cache / (key + ".json.gz")
        if receipt.exists() and not refresh:
            with gzip.open(receipt, "rt") as source:
                result = json.load(source)
        else:
            try:
                result = solve(spec)
            except SolverError as error:
                result = {"status": "failed", "input": spec.to_dict(), "input_sha256": spec.sha256,
                          "error": str(error), "evidence": error.evidence}
            with gzip.open(receipt, "wt") as target:
                json.dump(result, target, sort_keys=True, allow_nan=False)
        row = {"id": record["id"], "scenario": scenario, "mapping": mapping,
               "input": spec.to_dict(), "status": result["status"],
               "receipt": str(receipt.relative_to(ROOT)), "receipt_sha256": digest(receipt),
               "measured_rim_um": record["measured_rim_standoff_um"],
               "published_native_rim_um": record["published_surface_evolver_standoff_um"],
               "published_analytic_loaded_rim_um": record["published_analytical_loaded_standoff_um"],
               "sphere_unloaded_rim_um": (spherical_gap_mm(lower, .28, volume)-thickness)*1000}
        if "equilibrium" in result:
            row.update(predicted_rim_um=(result["equilibrium"]["standoff_mm"]-thickness)*1000,
                       load_balance=result["load_balance"], model_warnings=result.get("model_warnings", []))
            row["height_error_um"] = row["predicted_rim_um"]-row["measured_rim_um"]
        if "error" in result:
            row["error"] = result["error"]
        rows.append(row)
        print(record["id"], scenario, gamma, row["status"], row.get("predicted_rim_um"), flush=True)

    for record in dataset["records"]:
        for gamma in dataset["preprediction_protocol"]["material_scenarios_N_m"]:
            calculate(record, "primary", gamma=gamma)
        calculate(record, "literal-rim", mapping="literal")
        calculate(record, "gravity-on", gravity=True)
        if record["reported_offset_um"] is not None:
            calculate(record, "reported-offset", offset=record["reported_offset_um"]/1000)
        if record["substrate_pad_diameter_um"] in (220, 270, 320):
            for factor in (.95, 1.05):
                calculate(record, f"volume-{factor}", volume_factor=factor)
    primary = [r for r in rows if r["scenario"] == "primary"]
    checked = [r for r in primary if r["status"] == "refinement_checked"]
    nominal = [r for r in checked if r["input"]["surface_tension_n_m"] == .48]
    report = {"identity": identity, "protocol": "evidence/model-repair/forward-protocol.md",
              "physical_verdict": "Conditional geometry consistency and nominal screening only; no process qualification without measured uncertainty.",
              "summary": {"primary_count": len(primary), "primary_checked": len(checked),
                          "nominal_mean_absolute_error_um": sum(abs(r["height_error_um"]) for r in nominal)/len(nominal) if nominal else None,
                          "nominal_sphere_mean_absolute_error_um": sum(abs(r["sphere_unloaded_rim_um"]-r["measured_rim_um"]) for r in nominal)/len(nominal) if nominal else None},
              "rows": rows}
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (cache / "report.json").write_text(serialized)
    (DEST / "loaded-physical-results.json").write_text(serialized)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Recompute instead of reading identity-matched receipts.")
    args = parser.parse_args()
    report = run(args.refresh)
    print(json.dumps(report["summary"], indent=2))
    sys.exit(0 if report["summary"]["primary_checked"] == report["summary"]["primary_count"] else 1)
