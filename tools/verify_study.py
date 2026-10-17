import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import read_bundle
from soldershape.model import InputError
from soldershape.study import replay_study


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description="Verify the actual 220/270 micrometer planning-study export.")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--replay", action="store_true", help="Recompute all four cases with the installed native engine.")
    args = parser.parse_args()
    payload = args.archive.read_bytes()
    cases = read_bundle(args.archive)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        report = json.loads(archive.read("study-report.json"))
        check(len(cases) == 4, "The planning example must retain four native cases.")
        check(report["physical_qualification"] == "unqualified", "Numerical work must not claim physical qualification.")
        check(report["decision"]["status"] == "assumption_sensitive", "The pad hypothesis must change the planning conclusion.")
        check(len(report["samples"]) == 12, "The finite analytical screen must retain all twelve points.")
        expected = {("Reference", "literal_rims"): 223.31880160132934,
                    ("Candidate", "literal_rims"): 207.52181485954353,
                    ("Reference", "two_pad_cylinders"): 178.20338122353706,
                    ("Candidate", "two_pad_cylinders"): 167.31387797077113}
        for row in report["nominal"]:
            check(row["status"] == "refinement_checked", "A nominal native solve failed.")
            check(abs(row["native_gap_um"]-expected[(row["design"], row["mapping"])]) < .1,
                  "The example gap changed by more than the 0.1 micrometer numerical replay check.")
        for key, diameter in (("reference", .220), ("candidate", .270)):
            check(archive.read(key+".kicad_mod").decode() == report["study"][key]["footprint_text"],
                  "The exported footprint differs from the studied source.")
            rows = [row for row in report["nominal"] if row["design"].lower() == key]
            check(all(row["lower_diameter_mm"] == diameter for row in rows), "A lower diameter lost its source identity.")
        for name, digest in report["calculation_code_sha256"].items():
            check(hashlib.sha256(archive.read("calculation-source/"+name)).hexdigest() == digest,
                  "Archived calculation source differs from its identity.")
        names = archive.namelist()
        check("case-02/equivalent-domain-mm.stl" in names and "case-02/mesh-mm.stl" not in names,
              "Equivalent-domain geometry must be labeled as such.")
        broken = io.BytesIO()
        with zipfile.ZipFile(broken, "w") as changed:
            for name in names:
                data = archive.read(name)
                changed.writestr(name, data+b" " if name == "samples.csv" else data)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)/"changed.zip"
        path.write_bytes(broken.getvalue())
        try:
            read_bundle(path)
        except InputError:
            pass
        else:
            raise AssertionError("An edited sample table passed archive integrity.")
    result = {"passed": True, "archive_sha256": hashlib.sha256(payload).hexdigest(),
              "native_cases": 4, "analytical_samples": 12, "tamper_control_rejected": True,
              "decision": report["decision"], "physical_qualification": "unqualified",
              "nominal": report["nominal"], "calculation_code_sha256": report["calculation_code_sha256"]}
    if args.replay:
        result["replay"] = replay_study(args.archive)
        check(result["replay"]["passed"], "Fresh native replay failed.")
        check(result["replay"]["exact_engine_provenance"], "The release replay must use the retained engine identity.")
        check(result["replay"]["calculation_source_matches"], "The release replay must use the retained calculation source.")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
