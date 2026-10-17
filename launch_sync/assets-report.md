# Walkthrough asset tools

The launch page consumes the same two recorded Board comparisons as the application walkthrough. The asset tools bind its display data and downloads to those original archives. They do not calculate website-specific recommendations.

## Data contract

`tools/prepare_launch_assets.py` reads the original `decision_walkthrough/evidence/ui-gap-300.zip` and `ui-gap-330.zip`. It calls the trusted `soldershape.board.verify_board` for each archive. Both must have two cases, remain physically unqualified, and differ only in the held wetted-plane gap. Each extracted member keeps its original bytes.

`website/dist/media/walkthrough.json` has the following shape.

```text
schema = soldershape.launch-walkthrough.v1
application_ui_commit = 9c1cced6ff0dd037963d828e4e4eef3ede32a3db
source_capture = the complete docs/media/capture-manifest.json object
physical_qualification = unqualified
scenarios = two records
    id = gap-300 or gap-330
    label = 300 µm held gap or 330 µm held gap
    held_gap_um = 300 or 330
    archive_sha256 = SHA-256 of the original scenario ZIP
    evidence_url = media/evidence/review.html or media/gap-330-evidence/review.html
    screen = the unchanged board-report.json screen object
    rows = the unchanged review.json rows array
```

The generator resolves the application UI commit through Git. The checker can run from an extracted source candidate without a Git directory. It checks the captured commit against the full recorded identity.

The capture manifest supplies `capture_ui_commit`, `capture_date`, `video_kind`, `duration_seconds`, and `files`. The file list contains six actual JPEG captures, `walkthrough.mp4`, and `walkthrough.vtt`. The duration is 36 seconds. The generator preserves all additional metadata. It does not invent capture dates or recording claims.

## Download and inventory

`soldershape-recorded-example.zip` uses `soldershape.public-example.v2`. Each scenario folder contains the original `board-comparison.zip` and its exact extracted members. The extracted HTML reviews have their evidence links available in the same folder. The original inner ZIPs and their manifests remain unchanged.

The wrapper also contains project, board, KiCad, and third-party notices, replay instructions, and a manifest that hashes every other member. These are integrity checks. They are not a signature or physical qualification.

The new inventory uses `soldershape.launch-assets.v2`. It records the capture manifest identity, complete source capture metadata, both trusted archive verification results, and every served media file's byte count and SHA-256.

## Commands for the coordinator

After the actual captures, video, captions, and capture manifest are ready, generate the maintained assets with a fresh receipt.

```sh
python3 tools/prepare_launch_assets.py --receipt launch_sync/evidence/media-inventory.json
```

Check the finished local site, its actual browser download, and the current inventory.

```sh
python3 launch/check_launch.py --inventory launch_sync/evidence/media-inventory.json --receipt launch_sync/evidence/checks.json --download /path/to/downloaded-example.zip --base-url http://127.0.0.1:8770
```

After committing the reviewed source, build the exact committed candidate into a new directory.

```sh
python3 launch/build_candidate.py --output-dir output/launch-sync-release --receipt launch_sync/evidence/candidate-receipt.json
```

All three commands retain their historical default receipt paths for compatibility. Use explicit new paths to preserve earlier launch receipts.

The asset generator replaces its two maintained evidence extraction directories. It removes only the three obsolete maintained PNGs and the two legacy top-level aliases. It does not change the source evidence ZIPs or historical receipt files when an explicit new receipt is supplied.

## Checks performed by this delegate

Python compilation, all three `--help` commands, and `git diff --check` passed. This delegate did not run generators, build release candidates, capture the UI, or publish anything. The coordinator owns the generated artifacts and live acceptance checks.

Model the Domain put each gap's archive, review rows, and screen into one scenario record. Laziness Protocol reused the trusted Board verifier. Build the Lever made asset copying and evidence checks repeatable instead of editing the website's numbers by hand.
