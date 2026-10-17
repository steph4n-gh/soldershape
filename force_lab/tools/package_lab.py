"""Build and inspect the separate force-experiment quotation handoff."""

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
QUOTE_STATUS = {"prepared_for_quote": True, "lab_accepted": False,
                "fabrication_released": False, "physically_validated": False}
REQUIRED_FILES = {"force_lab/protocol.json", "force_lab/cad/spec.json", "force_lab/cad/model.py",
                  "force_lab/README.md", "force_lab/RFQ.md", "force_lab/BOM.csv", "force_lab/PROCEDURE.md",
                  "force_lab/tools/analyze.py", "force_lab/tools/verify_cad.py",
                  "force_lab/templates/inputs.csv", "force_lab/templates/outcomes-template.csv",
                  "force_lab/templates/calibration.json", "force_lab/templates/input_covariance.json",
                  "force_lab/planning/native-120/plan.json", "drawings-and-handbook.pdf"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(output):
    files = {}
    for directory in ("force_lab", "soldershape"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" and path.name != ".DS_Store":
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    for name in ("tools/setup_engine.py", "THIRD_PARTY.md", "LICENSE", "demo/protocol.json",
                 "demo/recording.json", "demo/data/stress-cases.zip", "expansion/research/metrology.md",
                 "expansion/research/design-judgment.md", "expansion/PRODUCT-ENDSTATE.md"):
        path = ROOT / name
        if path.is_file():
            files[name] = path.read_bytes()
    pdf = ROOT / "output/pdf/soldershape-force-lab-handoff.pdf"
    if not pdf.is_file():
        raise ValueError("Render and inspect the force-lab handoff PDF before packaging.")
    files["drawings-and-handbook.pdf"] = pdf.read_bytes()
    if not REQUIRED_FILES <= files.keys() or not any(name.endswith(".step") for name in files):
        raise ValueError("The quotation package is missing a required deliverable.")
    manifest = {"schema": "soldershape.force-lab-package.v1", "status": QUOTE_STATUS,
        "scope": "Matching isolated pinned-rim hot-force experiment. Vendor interfaces and physical accuracy remain unqualified.",
        "files": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in sorted(files.items())}}
    files["package-manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return verify(output)


def verify(path):
    archive_bytes = Path(path).read_bytes()
    if len(archive_bytes) > 250_000_000:
        raise ValueError("The lab package exceeds 250 MB compressed.")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 800:
            raise ValueError("Duplicate or excessive package members.")
        if sum(item.file_size for item in archive.infolist()) > 750_000_000:
            raise ValueError("The lab package exceeds 750 MB uncompressed.")
        if any(PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or "\\" in name for name in names):
            raise ValueError("Unsafe package member name.")
        manifest = json.loads(archive.read("package-manifest.json"))
        if manifest["schema"] != "soldershape.force-lab-package.v1":
            raise ValueError("Unknown package schema.")
        if manifest.get("status") != QUOTE_STATUS:
            raise ValueError("Only an explicitly unqualified quotation package is supported.")
        if set(names) != set(manifest["files"]) | {"package-manifest.json"}:
            raise ValueError("Package member set differs from its manifest.")
        if not REQUIRED_FILES <= manifest["files"].keys() or not any(name.endswith(".step") for name in manifest["files"]):
            raise ValueError("The quotation package is incomplete.")
        for name, expected in manifest["files"].items():
            data = archive.read(name)
            if len(data) != expected["bytes"] or digest(data) != expected["sha256"]:
                raise ValueError("Package member identity mismatch: " + name)
    return {"verified": True, "archive_sha256": digest(archive_bytes), "members": len(names),
            "bytes": len(archive_bytes), "status": manifest["status"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("build", "verify"))
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.archive) if args.operation == "build" else verify(args.archive), indent=2))


if __name__ == "__main__":
    main()
