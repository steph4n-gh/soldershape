"""Reproduce the seven-row archive limit regression using a retained native receipt."""

import gzip
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.artifacts import make_bundle, read_bundle
from soldershape.model import LoadSpec


def main():
    campaign = json.loads((ROOT / "evidence/model-repair/loaded-physical-results.json").read_text())
    row = next(row for row in campaign["rows"] if row["id"] == "vanveen2004-q220"
               and row["scenario"] == "primary" and row["input"]["surface_tension_n_m"] == .4)
    receipt = ROOT / row["receipt"]
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == row["receipt_sha256"], "Receipt identity changed."
    with gzip.open(receipt, "rt") as source:
        result = json.load(source)
    footprint = '(footprint "Archive regression" (pad "1" smd circle (at 0 0) (size .22 .22) (layers "F.Cu")))'
    case = {"schema": "soldershape.case.v1", "footprint_text": footprint, "pad_index": 0,
            "parameters": {key: value for key, value in result["input"].items() if key != "lower_diameter_mm"}, "baseline": None}
    output = ROOT / "output/seven-loaded-cases.zip"
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(make_bundle([result]*7, footprint, case))
    recovered = read_bundle(output)
    assert len(recovered) == 7 and all(isinstance(spec, LoadSpec) and "standoff_mm" not in spec.to_dict() for spec, _ in recovered)
    with zipfile.ZipFile(output) as archive:
        assert archive.read("case-00/model.fe") and archive.read("case-00/load-height/model.fe")
        report = {"passed": True, "cases": len(recovered), "members": len(archive.infolist()),
                  "compressed_bytes": output.stat().st_size,
                  "uncompressed_bytes": sum(member.file_size for member in archive.infolist()),
                  "source_receipt_sha256": row["receipt_sha256"]}
    (ROOT / "evidence/model-repair/archive-verification.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
