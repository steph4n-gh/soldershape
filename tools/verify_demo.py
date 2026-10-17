import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import read_bundle
from soldershape.demo import read_demo
from soldershape.model import InputError
from soldershape.solver import SolverError, solve


def failure_signature(evidence):
    output = evidence.get("stdout", "")+"\n"+evidence.get("stderr", "")
    messages = {f"{kind} {code}: "+re.sub(r"Index:\s*\d+", "Index:<negative modes>", message.strip())
                for kind, code, message in re.findall(r"\b(WARNING|ERROR)\s+(\d+):\s*([^\n]+)", output)}
    return {"native_messages": sorted(messages), "termination": evidence.get("termination"), "returncode": evidence.get("returncode")}


def main():
    parser = argparse.ArgumentParser(description="Verify all recorded demo cases including their expected limits.")
    parser.add_argument("archive", nargs="?", type=Path, default=ROOT/"demo/data/stress-cases.zip")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    demo = read_demo()
    content = args.archive.read_bytes()
    assert hashlib.sha256(content).hexdigest() == demo["archive"]["sha256"], "Downloaded bytes differ from the displayed archive."
    cases = read_bundle(args.archive)
    assert len(cases) == 7
    assert [point["screen"]["status"] for point in demo["samples"]] == ["conditional_comparison", "conditional_comparison", "outside_model_scope", "numerical_failure"]
    for point in demo["samples"][:2]:
        assert point["screen"]["reference_rule_met"] and not point["screen"]["candidate_rule_met"]
    assert all(point["screen"]["candidate_rule_met"] is None for point in demo["samples"][2:])
    broken = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(content)) as source, zipfile.ZipFile(broken, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            target.writestr(name, data+b" " if name == "results.csv" else data)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)/"changed.zip"
        path.write_bytes(broken.getvalue())
        try:
            read_bundle(path)
        except InputError:
            pass
        else:
            raise AssertionError("Changed CSV was accepted.")
    checks = []
    if args.replay:
        for index, (spec, previous) in enumerate(cases):
            try:
                current = solve(spec)
            except SolverError as error:
                current = {"status": "failed", "error": str(error), "evidence": error.evidence}
            check = {"input_sha256": spec.sha256, "previous_status": previous["status"], "current_status": current["status"]}
            check["expected_failure_reproduced"] = False
            if previous["status"] == current["status"] == "failed":
                with zipfile.ZipFile(io.BytesIO(content)) as archive:
                    old_signature = failure_signature(json.loads(archive.read(f"case-{index:02d}/evidence.json")))
                new_signature = failure_signature(current["evidence"])
                check.update(previous_failure_signature=old_signature, current_failure_signature=new_signature)
                check["expected_failure_reproduced"] = bool(old_signature["native_messages"]) and new_signature == old_signature
            check["verified"] = check["expected_failure_reproduced"]
            if previous["status"] == current["status"] == "refinement_checked":
                differences = {axis: abs(previous["forces"][axis]-current["forces"][axis]) for axis in ("x_uN", "z_uN")}
                scale = spec.surface_tension_n_m*spec.lower_diameter_mm*500
                check.update(force_difference_uN=differences,
                             model_scope_matches=current["model_warnings"] == previous["model_warnings"],
                             exact_engine_provenance=current["engine"]["source_sha256"] == previous["engine"]["source_sha256"] and current["engine"]["binary_sha256"] == previous["engine"]["binary_sha256"])
                check["verified"] = check["model_scope_matches"] and check["exact_engine_provenance"] and all(
                    difference <= max(abs(previous["forces"][axis])*.01, scale*.0001) for axis, difference in differences.items())
            checks.append(check)
        assert all(row["verified"] for row in checks), checks
    print(json.dumps({"recording_verified": True, "all_cases_numerically_successful": False,
                      "physical_qualification": "unqualified", "tamper_rejected": True,
                      "archive_sha256": demo["archive"]["sha256"], "cases": len(cases),
                      "replayed": bool(args.replay), "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
