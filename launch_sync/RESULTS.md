# Walkthrough launch synchronization

The maintained README, guides, six actual JPEG captures, captioned 36-second still sequence and static Site now follow the same U1/J16 decision. Only held gap changes between the 300 and 330 µm scenarios. The Site selects native recorded rows and fixture booleans. Physical force accuracy remains unqualified.

The settled application passed all 100 tests. The portable boundary and pure pre-lab set passed all 41 tests. Independent source review found no remaining blocking finding after repairing the archive hash wording, replay paths, lab regeneration filenames and stale last-frame checksum. Both new standalone lab packages include exact project and third-party notices. Original evidence archives remain unchanged.

The final browser-downloaded example matches the served package bytes. All 100 media assets and 108 local references across seven HTML pages pass the launch checker. All four gap/volume selections display the correct values and evidence targets. The 390 px comparison has no horizontal overflow. The regenerated 36-second video reached its end with captions showing. It has no audio and does not represent computation timing.

Site version 2 is saved from source commit `b79a95f6ecac61838ee468eabcc522a05bce2d75`. Its 108 canonical static files and helper-injected hosting manifest match the reviewed source. The source helper archive also contains macOS AppleDouble metadata. The saved version has no deployment ID. The current hostname remains owner-only with zero external visitors. No public audience or public source repository was created.

The complete candidate pins application source `55d12b26b33aa73bdf7a82c473a0583880dfc774`. Its 420,695,686 bytes have SHA-256 `6e408af0ec6b62a00ba36904658d9489e2b4decc988e89f5d826bd5dda320ca9`. All 1,470 members matched the release manifest in a fresh extraction without Git metadata or an engine cache. A deliberate README modification was rejected and the original bytes restored. The extracted package passed all 41 portable checks and the asset and walkthrough verifiers before native setup. Source files occupied 452,185,741 bytes at the freeze. The complete package is large because it retains the research evidence.

Fresh setup downloaded and built the pinned engine without modifying its numerical source. The CLI two-volume example solved and replayed with zero force difference. The real extracted application computed both 300 and 330 µm Board scenarios through the normal UI. The downloaded 330 µm Board ZIP passed source-pad binding, all-member integrity and both native replays with zero force difference. The five workbench pages and all three optional prebuilt lab downloads returned HTTP 200. The download bodies matched the exact candidate files. These are Apple Silicon macOS checks. They do not establish physical accuracy or native support on another operating system.

The [final check receipt](evidence/final-check.json), [candidate identity](evidence/candidate-receipt.json), [fresh member check](evidence/fresh-manifest.json), [fresh browser observations](evidence/fresh-board-browser.json) and [fresh Board replay](evidence/fresh-board-replay.json) retain the results. The [actual fresh Board archive](evidence/fresh-board-gap-330.zip) is preserved separately. This later receipt-only update does not alter the qualified application, Site or candidate bytes.

Temporary preview servers on 8770 and 8771 were stopped after QA. The main local workbench remains on 8769. Existing user drafts and historical numerical records were preserved.

## Setup and verification commands

From the source root, the normal application setup remains:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8769
```

The current workbench already uses 8769. Choose a free port for a second instance. For package verification, extract the candidate into a new directory and replace `/path/to/fresh/soldershape` below. The manifest check must run before setup, tests or imports create caches in that directory.

```sh
python3 launch_sync/verify_candidate.py /path/to/fresh/soldershape --receipt output/fresh-check-new.json
cd /path/to/fresh/soldershape
python3 -m unittest tests.test_boundaries tests.test_cases tests.test_web_inputs prelab.test_campaign.CouponRequests prelab.test_finite -v
python3 decision_walkthrough/verify.py
python3 launch/check_launch.py --inventory launch_sync/evidence/media-inventory.json --receipt output/site-check-new.json
python3 tools/setup_engine.py
python3 -m soldershape solve-case examples/centering-volume.soldershape.json --output output/centering-new.zip
python3 -m soldershape replay output/centering-new.zip
python3 -m soldershape serve --port 8771
```

In the browser, compute the 300 µm pair, choose **Try a 330 µm held gap**, and download the board-bound evidence. Verify its actual location with `python3 tools/verify_board.py /path/to/download.zip --replay`. The [getting-started guide](../docs/getting-started.md) explains the complete decision and the lab boundary.

## Remaining publication steps

Create the public repository, configure private vulnerability reporting, run hosted CI, publish a research release with its complete assets and hashes, then deploy the reviewed Site version with the intended audience. Physical testing remains necessary before production-accuracy claims. A raw clone omits ignored prebuilt lab files. The complete candidate includes them.

## Evidence

- [Independent source review](final-review.md) and [release audit](release-audit.md).
- [Final browser and link checks](evidence/checks-browser-final.json).
- [Final playback](evidence/video-playback-final.json) and [media inventory](evidence/media-inventory.json).
- [Full application tests](evidence/tests-settled.txt) and [portable tests](evidence/portable-tests.txt).
- [Saved Site version](evidence/site-save.json), [archive check](evidence/site-archive-check.json) and [unchanged access state](evidence/site-state-final.json).

Laziness Protocol reused the static Site, native verifier and existing package builders. Model the Domain kept each gap's rows, screen and evidence together. Prove It Works required actual controls, downloads and playback. Build the Lever made asset and candidate checks repeatable. Experience First kept one question across the documentation and launch page. Separate Before Serializing Shared State gave the documentation, tooling and audit workers disjoint writable paths.
