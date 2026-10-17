"""Package attributed recorded evidence without changing the original archive."""

import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "website/dist/media"
INNER = ROOT / "refinement2/evidence/board-comparison.zip"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    original = INNER.read_bytes()
    expected = "b6bf18f68ce868fa1a1cd1151be0360f1c7d20667b25154d569af1a825e16d64"
    if sha(original) != expected:
        raise ValueError("The recorded inner evidence identity changed.")
    with zipfile.ZipFile(INNER) as archive:
        review = archive.read("review.json")
        html = archive.read("review.html")
        for name in archive.namelist():
            target = DESTINATION / "evidence" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
    notices = {"PROJECT-LICENSE.txt": ROOT / "LICENSE",
               "BOARD-LICENSE.md": ROOT / "board_demo/source/LICENSE.md",
               "KICAD-LICENSE.md": ROOT / "examples/KICAD-LICENSE.md",
               "THIRD_PARTY.md": ROOT / "THIRD_PARTY.md"}
    files = {"board-comparison.zip": original, "review.html": html, "review.json": review}
    files.update({name: path.read_bytes() for name, path in notices.items()})
    files["README.md"] = (
        "# SolderShape recorded Board example\n\n"
        "Status: hypothetical process inputs; physical force accuracy unqualified.\n"
        "Only U1/J16 is computed. The ULX3S board supplies context.\n\n"
        "The inner board-comparison.zip is the unchanged native evidence archive.\n"
        "Its SHA-256 is " + expected + ".\n"
        "Open review.html for exact values. For its evidence links, extract the inner ZIP\n"
        "and open the review.html inside that extracted folder. The outer review is a convenience copy.\n\n"
        "From a SolderShape source checkout with the pinned engine installed, replay the inner ZIP:\n"
        "python3 tools/verify_board.py /path/to/board-comparison.zip --replay\n\n"
        "The outer manifest hashes every member. The inner manifest remains unchanged.\n"
        "Neither is an independent signature or physical validation.\n\n"
        "ULX3S is by EMARD and its contributors; retain BOARD-LICENSE.md and its logo terms.\n"
        "Numerical computation and BGA methods are Ken Brakke's Surface Evolver work.\n"
        "Original SolderShape code and documentation use PROJECT-LICENSE.txt.\n"
        "Third-party material retains its own terms in THIRD_PARTY.md.\n"
        "This is not a board or fixture fabrication release.\n"
    ).encode()
    manifest = {"schema": "soldershape.public-example.v1", "physical_qualification": "unqualified",
                "inner_archive_sha256": expected,
                "sha256": {name: sha(data) for name, data in sorted(files.items())}}
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    with zipfile.ZipFile(DESTINATION / "soldershape-recorded-example.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    for name, path in notices.items():
        shutil.copyfile(path, DESTINATION / name)
    for path in (ROOT / "docs/media").iterdir():
        if path.suffix in {".png", ".mp4", ".vtt"}:
            shutil.copyfile(path, DESTINATION / path.name)
    shutil.copyfile(ROOT / "board_demo/assets/board.svg", DESTINATION / "board.svg")
    for old_name in ("recorded-case.json", "review.html"):
        (DESTINATION / old_name).unlink(missing_ok=True)
    inventory = {"schema": "soldershape.launch-assets.v1", "capture_ui_commit": "79170fc6cb339ef787a029c02892d92829724203",
                 "capture_date": "2026-10-16", "video_kind": "three actual UI still captures, eight seconds each, no solver timing claim",
                 "inner_archive_sha256": expected,
                 "files": {str(path.relative_to(DESTINATION)): {"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                           for path in sorted(DESTINATION.rglob("*")) if path.is_file()}}
    (ROOT / "launch/media-inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({"assets": len(inventory["files"]), "inner_archive_unchanged": True,
                      "public_example_sha256": inventory["files"]["soldershape-recorded-example.zip"]["sha256"]}))


if __name__ == "__main__":
    main()
