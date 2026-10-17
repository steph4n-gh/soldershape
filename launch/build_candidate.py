"""Build the committed source plus the three optional prebuilt lab downloads."""

import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("output/soldershape-force-lab-r1.zip", "output/pdf/soldershape-force-lab-handoff.pdf",
          "output/soldershape-coupon-r1-refined.zip")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT).strip():
        raise RuntimeError("Commit the source changes before building a release candidate.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    directory = ROOT / "output/launch-release"
    directory.mkdir(parents=True, exist_ok=True)
    raw = directory / "candidate.tar"
    subprocess.run(["git", "archive", "--format=tar", "--prefix=soldershape/", "--output", str(raw), commit], cwd=ROOT, check=True)
    with tarfile.open(raw, "a") as archive:
        for name in ASSETS:
            archive.add(ROOT / name, arcname="soldershape/" + name, recursive=False)
    hashes = {}
    with tarfile.open(raw) as archive:
        for item in archive:
            if item.isfile():
                hashes[item.name.removeprefix("soldershape/")] = hashlib.file_digest(archive.extractfile(item), "sha256").hexdigest()
    manifest = {"schema": "soldershape.release-candidate.v1", "source_commit": commit,
                "status": "unpublished_research_preview_candidate", "physical_qualification": "unqualified", "sha256": hashes}
    payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with tarfile.open(raw, "a") as archive:
        member = tarfile.TarInfo("soldershape/RELEASE-MANIFEST.json")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))
    target = directory / ("soldershape-research-candidate-" + commit[:12] + ".tar.gz")
    with raw.open("rb") as source, target.open("wb") as compressed:
        with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, mtime=0) as destination:
            shutil.copyfileobj(source, destination)
    receipt = {"source_commit": commit, "candidate": str(target), "bytes": target.stat().st_size,
               "sha256": sha(target), "files": len(hashes), "prebuilt_lab_files": {name: hashes[name] for name in ASSETS},
               "native_engine_included": False, "status": "unpublished_research_preview_candidate"}
    (ROOT / "launch/candidate-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
