"""Package the reviewed lab handoff and verify its exact file hashes."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "package-manifest.json"


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate package members.")
        manifest = json.loads(archive.read(MANIFEST))
        expected = manifest["sha256"]
        if set(names) != set(expected) | {MANIFEST}:
            raise ValueError("Package members differ from manifest.")
        for name, digest in expected.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                raise ValueError(f"Package hash mismatch: {name}")
    return {"status": "all_members_verified", "files": len(expected),
            "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build(output):
    excluded = {"__pycache__", ".DS_Store"}
    paths = [path for path in (ROOT / "coupons").rglob("*")
             if path.is_file() and not excluded.intersection(path.parts)
             and path.suffix not in {".pyc", ".kicad_prl", ".lck"}]
    paths += [ROOT / "soldershape" / name for name in ("__init__.py", "model.py", "solver.py")]
    paths += [ROOT / "tools/setup_engine.py", ROOT / "THIRD_PARTY.md", ROOT / "LICENSE",
              ROOT / "output/pdf/soldershape-lab-handoff.pdf"]
    members = {str(path.relative_to(ROOT)): path.read_bytes() for path in sorted(paths)}
    members["START_HERE.txt"] = (
        "SolderShape external-lab coupon package SS-C220-C270-R1\n\n"
        "Read coupons/README.md, LAB_RFQ.md and PROCEDURE.md.\n"
        "Printable guide: output/pdf/soldershape-lab-handoff.pdf\n"
        "Status: prepared for lab quote and pilot; not fabrication released.\n"
        "No physical outcomes, orders, accepted quotes or vendor messages.\n\n"
        "From this archive root, verify with:\n"
        "python3 coupons/tools/package_lab.py --verify /path/to/original.zip\n"
        "python3 coupons/tools/verify_boards.py\n"
        "python3 -m unittest discover -s coupons/tests -v\n\n"
        "The native engine is not redistributed. Build it only if modeling is required:\n"
        "python3 tools/setup_engine.py\n"
        "See THIRD_PARTY.md for upstream source and notices.\n"
    ).encode()
    manifest = {"schema": "soldershape.lab-package.v1", "experiment_id": "SS-C220-C270-R1",
                "status": "prepared_for_lab_quote_not_fabrication_released",
                "physical_outcomes_present": False,
                "sha256": {name: hashlib.sha256(data).hexdigest() for name, data in members.items()}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        members[MANIFEST] = (json.dumps(manifest, indent=2) + "\n").encode()
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return verify(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verify", type=Path)
    group.add_argument("--output", type=Path, default=ROOT / "output/soldershape-coupon-r1.zip")
    args = parser.parse_args()
    print(json.dumps(verify(args.verify) if args.verify else build(args.output), indent=2))


if __name__ == "__main__":
    main()
