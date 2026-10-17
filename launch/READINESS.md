# Launch readiness

The project is suitable for a clearly labeled research preview after the publication steps below. It is not a physically qualified PCB design authority. Practitioner demand remains untested.

## Prepared

- Short README with actual screenshot and one consistent default port.
- One complete getting-started comparison, model/validation reference and developer guide.
- Contributor instructions, local runtime security boundary, unreleased changelog and prepared source/boundary CI workflow.
- MIT license for original project material, selected under the owner's authorization. Third-party terms remain separate.
- Three actual UI screenshots, a 24-second still-capture walkthrough, captions and transcript. Editorial timing is explicit.
- Static Sites introduction, a recorded comparison selector, local guide, validation explanation and attribution pages. It does not run the native solver or accept board uploads.
- Attributed example wrapper with an unchanged original Board ZIP and all notices. The website also serves that ZIP's original extracted evidence, so its review links work.
- New known-source generic exports retain the exact original KiCad or ULX3S notice in their existing manifest. All new evidence archives also carry the project MIT notice with an explicit scope excluding user and third-party input rights. Unknown user sources receive no assigned third-party source license. Historical archives remain untouched.
- New coupon package builds include the project license. Existing frozen lab packages remain unchanged.

## Verification

The initial application suite passed 99 tests in `launch/tests-full.txt`. The final suite passes 100 tests in `launch/tests-final.txt`; eight independent notice/capacity/compatibility checks also pass in `launch/project-notice-review.md`. The portable boundary/case/input set passes 27 tests in `launch/portable-tests.txt`. JavaScript syntax checks pass. The CI workflow is prepared; hosted GitHub CI has not run because no public repository is configured.

The provenance and documentation audits describe the pre-repair state. `launch/review.md` independently checks the repairs and bounded claims. `launch/media-inventory.json` records the served files. `launch/site-receipt.json` records actual deployment and DNS state. `launch/checks.json` records doc links, evidence/media identities and package checks when complete.

The history scan examined all 10 prior commits. Its 22 pattern matches are scientific JSON `capillary_relative` numeric values, not credentials. `launch/secret-scan.json` retains per-finding structural classification without secret content. Pattern scanning is not proof that every possible secret is absent. No hosted write credential is stored in source.

## Public launch steps still needed

1. Create the intended public GitHub repository and set this checkout's remote. No repository URL is invented in the guides.
2. Configure a working private vulnerability-reporting channel and update SECURITY.md and contributor links.
3. Run the prepared workflow on hosted CI and qualify the exact public release commit. Other operating systems remain unqualified.
4. Attach the complete source/distribution package, original notices, media and hashes to a clearly labeled research release. A raw Git clone omits the ignored prebuilt lab ZIPs and PDF. Include those explicit assets in the complete release package or build them separately. The core Board workflow does not require them.
5. Change the Sites audience only when public publication is requested. The prepared site preserves owner-private access and truthfully identifies source publication as pending.

Physical qualification is a separate investment step. It is required before a production-accuracy claim, not an implied outcome of open-sourcing an experimental workbench. No public source repository, release tag, binary distribution, hosted native solver or completed physical test is claimed here.

## Reproduce the preparation

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest tests.test_boundaries tests.test_cases tests.test_web_inputs -v
python3 tools/prepare_launch_assets.py
python3 launch/check_launch.py
python3 -m http.server 8770 --bind 127.0.0.1 --directory website/dist
```

The Sites publishing mirror is `output/launch-site`. It has independent ignored Git metadata. `website/dist` and its exact hosting identity remain tracked in the application repository. Short-lived write credentials pass through the source helper's hidden stdin only. The site's source commit and deployment receipt are distinct from the application's source commit.

Experience First replaced an engineering-history introduction with a complete newcomer path. Prove It Works required actual downloads, playback and packaging checks. The existing numerical algorithms and physical claims are unchanged.

The custom hostname is active with TLS. Sites access remains owner-only. Its identity gate was observed at the real hostname. The owner sign-in flow encountered the identity provider's browser security verification; deployed content was not visually inspected beyond that gate. The same exact pushed static source passed local browser controls, full video playback, actual download, narrow-layout and HTTP link checks. No bypass token or security-warning workaround was used.

Original Board notices and extracted native logs retain trailing spaces. The staged whitespace checker reports those preserved bytes. Source formatting passes with only `website/dist/media/evidence` and the copied original `BOARD-LICENSE.md` excluded; their exact bytes are verified against the archived source.

## Clean candidate evidence

The first complete candidate at source commit `e89f071` extracted without Git metadata or an engine cache. All 1,100 members matched its release manifest. It downloaded and built the pinned native engine, solved and replayed the two-volume CLI example, and completed the default Board comparison through the actual browser. The downloaded Board archive passed identity verification and reproduced the recorded X/Z forces with zero difference. All five workbench pages and three prebuilt lab download routes returned HTTP 200. Receipts are in `launch/fresh-candidate.json`, `launch/fresh-http.json` and `launch/fresh-replay.json`.

The final project-license attachment is a subsequent packaging correction. It adds a notice and scope metadata, not numerical logic. Seven fully evidenced loaded rows with a known footprint use exactly 100 members under the unchanged limit. The final complete candidate and its separate smoke check are recorded in `launch/candidate-receipt.json` and `launch/final-candidate-check.json`.
