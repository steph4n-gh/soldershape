import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.board import verify_board


def report(path):
    verification = verify_board(path)
    if not verification["passed"]:
        raise ValueError("Board archive verification failed.")
    with zipfile.ZipFile(io.BytesIO(path.read_bytes())) as archive:
        return json.loads(archive.read("board-report.json")), verification["archive_sha256"]


def verify():
    original, original_sha = report(ROOT / "board_demo/data/default-comparison.zip")
    changed, changed_sha = report(ROOT / "decision_walkthrough/evidence/gap-330-probe.zip")
    request = json.loads(json.dumps(original["request"]))
    request["parameters"]["standoff_mm"] = .33
    if changed["request"] != request or original["request"]["parameters"]["standoff_mm"] != .3:
        raise ValueError("The trial must change only held gap from 300 to 330 micrometers.")
    if changed["selection"] != original["selection"]:
        raise ValueError("The source selection changed during the gap trial.")
    expected = (
        ((-184.52638094190732, -181.28387853829275), (-164.3854725452698, 13.385897738397528)),
        ((-169.062859622926, -227.38953775806067), (-170.45539126847586, -82.27612770208692)),
    )
    rows = []
    for value, forces, gap in zip((original, changed), expected, (300, 330), strict=True):
        if value["physical_qualification"] != "unqualified":
            raise ValueError("Numerical evidence must retain physical uncertainty.")
        for result, pair in zip(value["results"], forces, strict=True):
            if result["status"] != "refinement_checked" or result.get("model_warnings"):
                raise ValueError("A trial result did not pass its numerical gates.")
            for axis, target in zip(("x_uN", "z_uN"), pair, strict=True):
                if abs(result["forces"][axis] - target) > 1e-6:
                    raise ValueError("The retained native force differs from the checked experiment.")
        rows.append({"held_gap_um": gap, "forces_uN": [r["forces"] for r in value["results"]],
                     "reference_rule_met": value["screen"]["reference_rule_met"],
                     "candidate_rule_met": value["screen"]["candidate_rule_met"]})
    if [(r["reference_rule_met"], r["candidate_rule_met"]) for r in rows] != [(True, False), (True, True)]:
        raise ValueError("The declared fixture decision did not change as recorded.")
    return {"passed": True, "original_archive_sha256": original_sha, "changed_archive_sha256": changed_sha,
            "only_changed_input": "standoff_mm", "cases": rows, "physical_qualification": "unqualified",
            "scope": "Two sampled held-gap hypotheses on one identified source pad. Not a process tolerance or physical error bound."}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
