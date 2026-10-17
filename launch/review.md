# Independent launch-preparation review

Reviewed the working tree against `79170fc6cb339ef787a029c02892d92829724203` on 2026-10-16. The scope covers the new README, guides, license and notices, launch media metadata, static site, `tools/prepare_launch_assets.py`, the origin-notice export change and coupon packaging change. This is a review of the prepared source and artifacts. Browser playback, deployed access, DNS and clean-machine installation are outside this review.

## Result

No unresolved correctness finding was identified in the reviewed scope. Two documentation discrepancies were reported and corrected during review. `board_demo/APP.md` now starts from the repository root. `website/README.md` now identifies `output/launch-site` as the publishing mirror.

The presentation consistently distinguishes recorded results, local native computation and physical qualification. It describes one isolated joint, states that the board supplies context and preserves the unresolved published-force failure. It makes no new-solver, process-accuracy or production-readiness claim. The public source repository and release tag are explicitly pending. The prepared CI workflow is not described as a hosted CI success.

The MIT grant covers original project material under the owner's delegated license choice. Separate KiCad and ULX3S notices remain explicit. The native C engine is downloaded locally rather than redistributed as a cleared binary. This review confirms that treatment in the files. It is not a comprehensive legal clearance of the upstream engine or all downstream uses.

## Checks performed

- Ran `python3 -m unittest tests.test_export_notices -v`. All five tests passed. Exact known sources retain their original notice, unknown source bytes receive no assigned third-party license, source-free study exports retain their existing form, and a changed notice fails manifest verification.
- Verified byte counts and SHA-256 values for all 13 files in `launch/media-inventory.json` against the served files.
- Verified every member of the nine-member recorded-example wrapper against its manifest. Its inner ZIP is byte-identical to `refinement2/evidence/board-comparison.zip`, with SHA-256 `b6bf18f68ce868fa1a1cd1151be0360f1c7d20667b25154d569af1a825e16d64`. Review JSON, HTML and notice copies match the served files.
- Compared all 16 historical tracked ZIPs against the exact bytes in `79170fc`. None changed.
- Compared `soldershape/model.py`, `soldershape/solver.py` and `soldershape/study.py` against `79170fc`. None changed.
- Checked local targets and fragments in all six site HTML files. No unexpected missing target was found. The seven links from the original `media/review.html` to extracted evidence members are deliberately absent from the hosted site. The report and download instructions explicitly state that those links require extracting the inner ZIP.
- Checked the published board counts against `board_demo/context.json`. The site matches 235 components and 1,177 pads. The force values and 40/56 nL comparison match the immutable review rows.
- Confirmed the two pinned GitHub Action commits exist in the official [actions/checkout repository](https://github.com/actions/checkout/commit/11d5960a326750d5838078e36cf38b85af677262) and [actions/setup-python repository](https://github.com/actions/setup-python/commit/a26af69be951a213d495a4c3e4e4022e16d87065). This does not establish that the workflow has run on GitHub.

The recorded full-suite receipt reports 99 passing tests. The portable receipt reports 27 passing tests. Those counts were read from the saved receipts rather than independently rerun in full during this review.

## Code and prose review

The new origin-notice helper uses exact source-byte identity and existing manifest handling. It does not infer permission for arbitrary uploads. The wrapper generator preserves the original inner archive and emits a manifest for the new distribution unit. The static interaction reads the recorded review and uses DOM text content. It does not execute a solver or accept user PCB data.

No comment deletion, restoration, workaround fix, suppression removal, constraint encoding or architect follow-up was needed in this review. No scoped code comment or suppression required a finding. No application or documentation file was edited by the reviewer.

## Release limits

A public source repository, verified public acquisition links, release tag and private vulnerability-reporting route still need to exist before the prepared source is presented as a completed public release. Deployment, hostname status and final user-facing launch instructions belong in the release owner's readiness record. Those files were still being prepared during this review and their temporary absence was not treated as an implementation defect.

The video is an explicitly labeled 24-second sequence of real still captures. It is not a continuous interaction recording or a solver timing measurement. This review checks its metadata and hash, not visual playback. Physical force qualification and prospective laboratory measurements remain open.
