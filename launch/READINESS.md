# Launch readiness

The current launch preparation follows the guided Board decision. The README, setup guide, validation reference, six actual application captures, captioned 36-second still sequence and static introduction use the same U1/J16 question. At a 300 µm held gap, only 40 nL meets the declared numerical fixture rule. At 330 µm, both 40 and 56 nL meet it. These are hypothetical process scenarios, not measured manufacturing limits.

The project can be presented as a research preview. It is not a physically qualified PCB design authority. Practitioner demand and willingness to pay remain untested. The [current final-check record](../launch_sync/RESULTS.md) identifies the exact candidate, checks, saved Site source and remaining publication steps. Earlier receipts below qualify their own historical commits only.

## What is prepared

- A complete local workflow from actual source copper through assumptions, native computation, readable review, editable inputs, numerical evidence and a matching lab question.
- A recorded introduction that selects both held-gap scenarios and both volumes from exact retained native evidence. It does not run a solver or accept board uploads.
- Six actual JPEG screenshots, a captioned 36-second video assembled from those stills, and an equivalent transcript. Timing is editorial and there is no audio.
- A downloadable example with both unchanged native ZIPs, exact extracted review members, original Board and footprint notices and the project MIT grant.
- Separate notice-bearing force and height-coupon packages. The app's fixed download routes select these new names. Older packages remain unchanged. The force kit uses 200 µm pads and needs adaptation for the 400 µm board question. Neither experiment is fabrication released or physically validated.
- MIT for original project material. Third-party terms remain separate in [THIRD_PARTY.md](../THIRD_PARTY.md). No native engine binary or engine C source is redistributed.
- Contributor instructions, runtime security scope and a prepared source/boundary CI workflow. Hosted CI has not run.

## Reproduce the checks

From the repository root, keep new receipts separate from historical records.

```sh
python3 tools/setup_engine.py
python3 -m unittest discover -s tests -v
python3 decision_walkthrough/verify.py
python3 prelab/verify.py
python3 tools/prepare_launch_assets.py --receipt launch_sync/evidence/media-inventory.json
python3 launch/check_launch.py --inventory launch_sync/evidence/media-inventory.json --receipt output/launch-check-new.json
python3 -m http.server 8770 --bind 127.0.0.1 --directory website/dist
```

After committing source, build the complete distribution with its optional lab downloads.

```sh
python3 launch/build_candidate.py --output-dir output/launch-release-new --receipt output/candidate-new.json
```

A raw Git clone omits the ignored prebuilt lab ZIPs and PDFs. The complete candidate includes the three advertised lab download files explicitly. Follow [getting started](../docs/getting-started.md) after extraction. The core Board workflow does not require prebuilt lab documents. Current application checks cover Apple Silicon macOS. Portable boundary checks are not native Linux qualification.

## Publication steps still needed

1. Create the intended public GitHub repository and set this checkout's remote. No repository URL is invented in the guides.
2. Configure a working private vulnerability-reporting channel and update SECURITY.md and contributor links.
3. Run the prepared workflow on hosted CI and qualify the exact public release commit. Other operating systems remain unqualified.
4. Attach the complete source package, notices, media and hashes to a clearly labeled research release. A full source clone carries roughly 425 MB of retained evidence before Git compression. The largest two research archives are about 69 and 53 MB.
5. Publish the reviewed Site version and change its audience when launch is requested. The existing hostname and TLS are active. Saving source does not change the live deployment or owner-only access.

Physical qualification remains a separate investment step before production-accuracy claims. No public repository, release tag, hosted native solver or completed physical test is claimed here.

## Site and credentials

`website/dist` is the canonical static source. Its exact Sites identity is tracked in `website/.openai/hosting.json`. The publishing mirror is `output/launch-site` with separate ignored Git metadata. Source commit, saved version and deployed version are distinct identities. Short-lived credentials pass through the source helper's hidden stdin, never source, arguments or receipts.

The real hostname previously showed its owner identity gate. That access boundary remains in place. Local browser controls exercise the reviewed source without bypassing the Site authentication gate.

## Historical evidence

[Initial provenance audit](provenance-audit.md), [earlier review](review.md), [earlier Site deployment](site-receipt.json) and [earlier complete candidate](candidate-receipt.json) remain unchanged. Their older screenshots, counts, source commits and numerical evidence are not the current launch inventory. The previous complete candidate pinned `ac8b3a1` before the pre-lab work and Board walkthrough.

The [current independent release audit](../launch_sync/release-audit.md) inspected the full 15-commit baseline and recursively expanded current archives. Its 22 Gitleaks matches were scientific JSON numbers, with no verified credential finding. Pattern scans have explicit scope limits and cannot prove every possible secret absent. Reproducibility receipts retain absolute local paths as public metadata if the history is released.

Laziness Protocol kept the static Site and immutable numerical records. Prove It Works requires actual browser selectors, downloads, playback and a newly extracted candidate, rather than treating successful source packaging as physical validation.
