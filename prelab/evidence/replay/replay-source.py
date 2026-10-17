"""Freshly recompute nominal, critical and rejected coupon requests."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prelab.campaign import accepted, encode, engine_info, read, sha, verify


def replay(campaign, destination):
    verify(campaign)
    if destination.exists():
        raise ValueError("Replay output must be new.")
    manifest = read(campaign / "manifest.json")
    if engine_info() != manifest["engine"]:
        raise ValueError("Replay requires the exact archived engine identity.")
    table = read(campaign / "plan.json")
    selected = {row["request_sha256"] for row in table["rows"] if row["scenario"] in
                ("nominal", "opposed-requested-endpoints", "opposed-wider-volume")}
    selected.add(table["negative_control"])
    destination.mkdir(parents=True)

    def calculate(key):
        target = destination / (key + ".json.gz")
        subprocess.run([sys.executable, str(ROOT / "prelab/campaign.py"), "worker",
                        str(campaign / "requests" / (key + ".json")), str(target)], check=True, cwd=ROOT)
        with gzip.open(campaign / "receipts" / (key + ".json.gz"), "rt") as stream:
            original = json.load(stream)
        with gzip.open(target, "rt") as stream:
            fresh = json.load(stream)
        if not accepted(original):
            return {"request_sha256": key, "passed": not accepted(fresh),
                    "expected_rejection": True, "original_status": original["status"], "fresh_status": fresh["status"]}
        gap = 1000 * (fresh["equilibrium"]["standoff_mm"] - original["equilibrium"]["standoff_mm"]) if accepted(fresh) else None
        forces = {axis: fresh["forces"][axis] - original["forces"][axis] for axis in ("x_uN", "z_uN")} if accepted(fresh) else None
        return {"request_sha256": key, "gap_difference_um": gap, "force_difference_uN": forces,
                "passed": bool(accepted(fresh) and abs(gap) <= .01 and max(abs(x) for x in forces.values()) <= .01)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(calculate, sorted(selected)))
    report = {"passed": all(row["passed"] for row in rows), "requests": rows,
              "engine": manifest["engine"], "campaign_manifest_sha256": sha((campaign / "manifest.json").read_bytes()),
              "replay_code_sha256": sha(Path(__file__).read_bytes()),
              "scope": "Fresh numerical replay with exact engine. No physical validation."}
    report["receipt_sha256"] = {path.name: sha(path.read_bytes()) for path in destination.glob("*.json.gz")}
    (destination / "report.json").write_bytes(encode(report))
    return {"passed": report["passed"], "requests": len(rows), "expected_rejections": sum(row.get("expected_rejection", False) for row in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.campaign.resolve(), args.destination.resolve()), indent=2))
