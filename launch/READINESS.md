# Launch readiness

The current launch preparation follows the guided Board decision. The README, setup guide, validation reference, six actual application captures, captioned 36-second still sequence and static introduction use the same U1/J16 question. At a 300 µm held gap, only 40 nL meets the declared numerical fixture rule. At 330 µm, both 40 and 56 nL meet it. These are hypothetical process scenarios, not measured manufacturing limits.

The project can be presented as a research preview. It is not a physically qualified PCB design authority. Practitioner demand and willingness to pay remain untested. The [publication record](../publication/RESULTS.md) identifies the public release and deployment. The [local final-check record](../launch_sync/RESULTS.md) preserves the preceding qualification. Earlier receipts qualify their own historical commits only.

## What is prepared

- A complete local workflow from actual source copper through assumptions, native computation, readable review, editable inputs, numerical evidence and a matching lab question.
- A recorded introduction that selects both held-gap scenarios and both volumes from exact retained native evidence. It does not run a solver or accept board uploads.
- Six actual JPEG screenshots, a captioned 36-second video assembled from those stills, and an equivalent transcript. Timing is editorial and there is no audio.
- A downloadable example with both unchanged native ZIPs, exact extracted review members, original Board and footprint notices and the project MIT grant.
- Separate notice-bearing force and height-coupon packages. The app's fixed download routes select these new names. Older packages remain unchanged. The force kit uses 200 µm pads and needs adaptation for the 400 µm board question. Neither experiment is fabrication released or physically validated.
- MIT for original project material. Third-party terms remain separate in [THIRD_PARTY.md](../THIRD_PARTY.md). No native engine binary or engine C source is redistributed.
- Contributor instructions, runtime security scope and the [source and boundary CI workflow](https://github.com/steph4n-gh/soldershape/actions/workflows/checks.yml). Hosted results and exact commit identity belong to the publication record.

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

## Public release

The owner authorized publication on 2026-10-17. The [GitHub repository](https://github.com/steph4n-gh/soldershape) is public. [Private vulnerability reporting](https://github.com/steph4n-gh/soldershape/security/advisories/new) is enabled. The current source and security docs identify those destinations.

The [publication record](../publication/RESULTS.md) is the authority for the exact CI run, research prerelease, asset hashes, Site version, deployment and public-access verification. The intended release is [v0.4.0-preview.1](https://github.com/steph4n-gh/soldershape/releases/tag/v0.4.0-preview.1). The release is marked as a prerelease because physical qualification and other native platforms remain open.

A raw source clone omits ignored prebuilt lab ZIPs and PDFs. The complete release package includes those explicit assets. It also retains substantial numerical evidence, so the download is large. License notices remain separate from fabrication readiness and physical validation.

## Site and credentials

`website/dist` is the canonical static source. Its exact Sites identity is tracked in `website/.openai/hosting.json`. The publishing mirror is `output/launch-site` with separate ignored Git metadata. Source commit, saved version and deployed version are distinct identities. Short-lived credentials pass through the source helper's hidden stdin, never source, arguments or receipts.

The real hostname previously showed its owner identity gate. Public audience and deployment are separately verified during this publication. No bypass credential is used for anonymous launch checks.

## Historical evidence

[Initial provenance audit](provenance-audit.md), [earlier review](review.md), [earlier Site deployment](site-receipt.json) and [earlier complete candidate](candidate-receipt.json) remain unchanged. Their older screenshots, counts, source commits and numerical evidence are not the current launch inventory. The previous complete candidate pinned `ac8b3a1` before the pre-lab work and Board walkthrough.

The [current independent release audit](../launch_sync/release-audit.md) inspected the full 15-commit baseline and recursively expanded current archives. Its 22 Gitleaks matches were scientific JSON numbers, with no verified credential finding. Pattern scans have explicit scope limits and cannot prove every possible secret absent. Reproducibility receipts retain absolute local paths as public metadata if the history is released.

Laziness Protocol kept the static Site and immutable numerical records. Prove It Works requires actual browser selectors, downloads, playback and a newly extracted candidate, rather than treating successful source packaging as physical validation.
