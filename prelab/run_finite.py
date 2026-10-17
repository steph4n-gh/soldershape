"""Replay the settled finite-copper controls without repeating abandoned adapters."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path

from prelab.finite import FinitePadRequest, ROOT, _isolated, fixed_energy_check


def run(destination):
    destination.mkdir(parents=True, exist_ok=False)
    controls = json.loads((ROOT / "prelab/finite-controls.json").read_bytes())
    jobs = controls["jobs"]

    def calculate(pair):
        name, job = pair
        result = _isolated(FinitePadRequest.from_dict(job["request"]), destination / name,
                           job["kind"], job["envelope_height_mm"], 3 if "penetrating" not in name else job["level_count"])
        return name, result

    with ThreadPoolExecutor(max_workers=2) as pool:
        centers = dict(pool.map(calculate, jobs.items()))
    energies = {}
    for arm, name in (("C220", "v4-C220-full-fixed"), ("C270", "v5-C270-full-fixed-extra")):
        job = jobs[name]
        request = FinitePadRequest.from_dict(job["request"])
        gap = job["envelope_height_mm"] - request.lower_wetting_depth_mm - request.upper_wetting_depth_mm
        energies[arm] = fixed_energy_check(request, destination / (arm + "-energy"), gap, level_count=3)
    inventory = {str(path.relative_to(destination)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in destination.rglob("*") if path.is_file()}
    report = {"scope": "Fixed-gap conditional finite-copper controls and relaxed energy derivatives. No new loaded solver or physical qualification.",
              "centers": {name: {key: result.get(key) for key in
                                  ("status", "numeric_gates_passed", "physical_eligibility", "accepted_face_gap_mm", "interface")}
                          for name, result in centers.items()},
              "energy_checks": energies,
              "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                                ("prelab/run_finite.py", "prelab/finite.py", "prelab/finite-controls.json", "soldershape/model.py", "soldershape/solver.py")},
              "files": inventory, "physical_qualification": "unqualified"}
    (destination / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"centers": {name: row["status"] for name, row in report["centers"].items()},
                      "energy_checks": {arm: row["status"] for arm, row in energies.items()}}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    run(args.destination.resolve())
