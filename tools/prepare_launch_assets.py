"""Package the recorded Board walkthrough without changing its evidence archives."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.board import verify_board

DESTINATION = ROOT / "website/dist/media"
CAPTURE = ROOT / "docs/media/capture-manifest.json"
UI_COMMIT = "3644c08bbf0ef1976bc634bba323779055583e6b"
SCENARIOS = (("gap-300", 300, "evidence"), ("gap-330", 330, "gap-330-evidence"))
NOTICES = {"PROJECT-LICENSE.txt": ROOT / "LICENSE",
           "BOARD-LICENSE.md": ROOT / "board_demo/source/LICENSE.md",
           "KICAD-LICENSE.md": ROOT / "examples/KICAD-LICENSE.md",
           "THIRD_PARTY.md": ROOT / "THIRD_PARTY.md"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def read_walkthrough():
    capture = json.loads(CAPTURE.read_bytes())
    if capture["capture_ui_commit"] != UI_COMMIT:
        raise ValueError("Capture metadata must identify the walkthrough UI commit.")
    media = capture["files"]
    if (len(media) != len(set(media)) or len(media) != 8
            or sum(Path(name).suffix == ".jpg" for name in media) != 6
            or {"walkthrough.mp4", "walkthrough.vtt"} - set(media)):
        raise ValueError("Capture metadata must list six JPEGs, the video and its captions.")
    for name in media:
        if Path(name).name != name or not (ROOT / "docs/media" / name).is_file():
            raise ValueError("Capture metadata names an absent or invalid media file.")
    if not capture.get("capture_date") or not capture.get("video_kind") or capture.get("duration_seconds") != 36:
        raise ValueError("Capture metadata must describe the date, still video and 36-second duration.")
    scenarios, archives, requests, verifications = [], {}, [], {}
    for identifier, gap, folder in SCENARIOS:
        path = ROOT / "decision_walkthrough/evidence" / ("ui-" + identifier + ".zip")
        verification = verify_board(path)
        if not verification["passed"] or verification["case_count"] != 2:
            raise ValueError("The recorded Board scenario did not pass trusted verification.")
        original = path.read_bytes()
        with zipfile.ZipFile(path) as archive:
            members = {}
            for name in archive.namelist():
                relative = PurePosixPath(name)
                if relative.is_absolute() or ".." in relative.parts or name.endswith("/") or name in members:
                    raise ValueError("The evidence archive has an unsafe or duplicate member.")
                members[name] = archive.read(name)
        report = json.loads(members["board-report.json"])
        review = json.loads(members["review.json"])
        if report["physical_qualification"] != "unqualified" or review["physical_qualification"] != "unqualified":
            raise ValueError("Recorded force predictions must remain physically unqualified.")
        if len(review["rows"]) != 2 or any(row["input"]["standoff_mm"] != gap / 1000 for row in review["rows"]):
            raise ValueError("The scenario rows differ from their declared held gap.")
        request = json.loads(json.dumps(report["request"]))
        if request["parameters"].pop("standoff_mm") != gap / 1000:
            raise ValueError("The scenario request differs from its declared held gap.")
        requests.append(request)
        scenarios.append({"id": identifier, "label": f"{gap} µm held gap", "held_gap_um": gap,
                          "archive_sha256": sha(original), "evidence_url": f"media/{folder}/review.html",
                          "screen": report["screen"], "rows": review["rows"]})
        archives[identifier] = {"original": original, "members": members, "folder": folder}
        verifications[identifier] = verification
    if requests[0] != requests[1]:
        raise ValueError("The paired recorded requests must differ only in held gap.")
    for first, second in zip(scenarios[0]["rows"], scenarios[1]["rows"], strict=True):
        a, b = dict(first["input"]), dict(second["input"])
        a.pop("standoff_mm")
        b.pop("standoff_mm")
        if a != b:
            raise ValueError("The paired case inputs must differ only in held gap.")
    document = {"schema": "soldershape.launch-walkthrough.v1", "application_ui_commit": UI_COMMIT,
                "source_capture": capture, "physical_qualification": "unqualified", "scenarios": scenarios}
    return document, archives, verifications


def example_files(document, archives):
    files = {name: path.read_bytes() for name, path in NOTICES.items()}
    for identifier, archive in archives.items():
        files[identifier + "/board-comparison.zip"] = archive["original"]
        files.update({identifier + "/" + name: data for name, data in archive["members"].items()})
    files["README.md"] = (
        "# SolderShape recorded Board walkthrough\n\n"
        "These are hypothetical process inputs at the actual ULX3S U1/J16 copper pad.\n"
        "Only the selected isolated joint is computed. Physical force accuracy remains unqualified.\n"
        "The paired scenarios change only the held wetted-plane gap, from 300 to 330 µm.\n"
        "Each scenario compares 40 and 56 nL at 240 µm offset on 400 µm circular pads.\n\n"
        "Open gap-300/review.html and gap-330/review.html for the exact conditional results.\n"
        "Each folder also contains the unchanged original board-comparison.zip and exact extracted members.\n"
        "From a source checkout, replace /path/to/package with the extracted wrapper directory\n"
        "and verify each original archive with the trusted verifier:\n\n"
        "    python3 tools/verify_board.py /path/to/package/gap-300/board-comparison.zip\n"
        "    python3 tools/verify_board.py /path/to/package/gap-330/board-comparison.zip\n\n"
        "Add --replay after installing the pinned native engine to repeat the calculations.\n"
        "Numerical replay does not establish physical accuracy, production approval or manufacturing yield.\n"
        "The outer manifest hashes every other member. Inner archive bytes and manifests remain unchanged.\n"
        "These hashes provide local integrity checks, not an independent signature.\n\n"
        "ULX3S is by EMARD and its contributors. Retain BOARD-LICENSE.md and its logo terms.\n"
        "Numerical computation and BGA methods are Ken Brakke's Surface Evolver work.\n"
        "Original SolderShape code and documentation use PROJECT-LICENSE.txt.\n"
        "Third-party material retains its own terms in THIRD_PARTY.md and KICAD-LICENSE.md.\n"
        "This is not a board or fixture fabrication release.\n"
    ).encode()
    files["manifest.json"] = encoded({"schema": "soldershape.public-example.v2",
                                     "physical_qualification": "unqualified",
                                     "application_ui_commit": document["application_ui_commit"],
                                     "scenarios": [{"id": row["id"], "held_gap_um": row["held_gap_um"],
                                                    "archive_sha256": row["archive_sha256"]}
                                                   for row in document["scenarios"]],
                                     "sha256": {name: sha(data) for name, data in sorted(files.items())}})
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=ROOT / "launch/media-inventory.json")
    args = parser.parse_args()
    if subprocess.check_output(["git", "rev-parse", UI_COMMIT], cwd=ROOT, text=True).strip() != UI_COMMIT:
        raise ValueError("The walkthrough UI commit cannot be resolved.")
    document, archives, verifications = read_walkthrough()
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for archive in archives.values():
        folder = DESTINATION / archive["folder"]
        if folder.exists():
            shutil.rmtree(folder)
        for name, data in archive["members"].items():
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    files = example_files(document, archives)
    with zipfile.ZipFile(DESTINATION / "soldershape-recorded-example.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    for name, path in NOTICES.items():
        shutil.copyfile(path, DESTINATION / name)
    for name in ("board-explorer.png", "comparison-review.png", "result-inputs.png"):
        (DESTINATION / name).unlink(missing_ok=True)
    for name in document["source_capture"]["files"]:
        shutil.copyfile(ROOT / "docs/media" / name, DESTINATION / name)
    shutil.copyfile(CAPTURE, DESTINATION / "capture-manifest.json")
    shutil.copyfile(ROOT / "board_demo/assets/board.svg", DESTINATION / "board.svg")
    (DESTINATION / "walkthrough.json").write_bytes(encoded(document))
    for old_name in ("recorded-case.json", "review.html"):
        (DESTINATION / old_name).unlink(missing_ok=True)
    inventory = {"schema": "soldershape.launch-assets.v2", "application_ui_commit": UI_COMMIT,
                 "capture_manifest_sha256": sha(CAPTURE.read_bytes()), "source_capture": document["source_capture"],
                 "physical_qualification": "unqualified", "scenarios": verifications,
                 "files": {str(path.relative_to(DESTINATION)): {"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                           for path in sorted(DESTINATION.rglob("*")) if path.is_file()}}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(encoded(inventory))
    print(json.dumps({"assets": len(inventory["files"]), "original_archives_unchanged": True,
                      "public_example_sha256": inventory["files"]["soldershape-recorded-example.zip"]["sha256"],
                      "receipt": str(args.receipt)}))


if __name__ == "__main__":
    main()
