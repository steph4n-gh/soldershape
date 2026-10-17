"""Check the actual browser downloads and preserved scientific baselines."""

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import read_bundle
from soldershape.board import verify_board


class Brief(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.resources = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "a":
            self.links.append(attributes["href"])
        if tag in {"script", "link", "img", "iframe", "object", "embed", "video", "audio"}:
            self.resources.append(tag)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    evidence = ROOT / "refinement2/evidence"
    checks = []
    for name in ("joint-comparison", "loaded-comparison", "board-comparison", "offset-sweep", "failed-single"):
        path = evidence / (name + ".zip")
        cases = read_bundle(path)
        with zipfile.ZipFile(path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            for member, digest in manifest["files"].items():
                assert sha(archive.read(member)) == digest, (name, member)
            review = json.loads(archive.read("review.json"))
            assert review["physical_qualification"] == "unqualified"
            assert len(review["rows"]) == len(cases)
            for row, (_, result) in zip(review["rows"], cases, strict=True):
                assert row["input"] == result["input"]
                assert row["input_sha256"] == result["input_sha256"]
                assert row["numerical_status"] == result["status"]
                if result["status"] == "failed":
                    assert "forces" not in row and "equilibrium" not in row
                else:
                    assert row.get("forces") == result.get("forces")
                    assert row.get("equilibrium") == result.get("equilibrium")
            html = archive.read("review.html")
            parser = Brief()
            parser.feed(html.decode())
            assert not parser.resources, parser.resources
            assert all(link in archive.namelist() for link in parser.links)
            assert "works as a standalone HTML file" in html.decode()
            standalone = evidence / (name.replace("-comparison", "") + "-review.html")
            if standalone.exists():
                assert standalone.read_bytes() == html
            checks.append({"archive": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes()),
                           "cases": len(cases), "members": len(archive.namelist()),
                           "status": [result["status"] for _, result in cases],
                           "html_sha256": sha(html), "external_resources": parser.resources,
                           "relative_evidence_links_resolve_after_extraction": True})
    assert verify_board(evidence / "board-comparison.zip")["passed"]
    preserved = {}
    for name in ("soldershape/model.py", "soldershape/solver.py", "soldershape/study.py",
                 "demo/data/stress-cases.zip", "board_demo/data/default-comparison.zip",
                 "board_demo/data/browser-comparison.zip"):
        original = subprocess.check_output(["git", "show", "11379f8:" + name], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        assert current == original, name
        preserved[name] = sha(current)
    for name, digest in {
        "output/soldershape-force-lab-r1.zip": "0b4ee985fc0bde510385e92656bfac7c8df92e73f3be4a4e69e5770e9fa63274",
        "output/pdf/soldershape-force-lab-handoff.pdf": "cf4bf5712ae9b15b44466ff22a584ad930d14b8eb132c6934a32c5c7acc8d08f",
        "output/soldershape-coupon-r1-refined.zip": "f20c7e9cb70bb400c3ad2a6fbb97c088757a39f5ecdd9db3f6bf4683e16bb1ea",
    }.items():
        assert sha((ROOT / name).read_bytes()) == digest, name
        preserved[name] = digest
    receipt = {"passed": True, "downloads": checks, "preserved": preserved,
               "html_check": "Structural inspection and exact direct-download/ZIP equality. The browser policy blocked file URLs; no offline visual rendering was performed.",
               "physical_qualification": "unqualified"}
    target = ROOT / "refinement2/artifact-checks.json"
    target.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
