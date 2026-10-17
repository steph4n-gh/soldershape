# Independent launch source review

Reviewed on 2026-10-17 against baseline `9c1cced6ff0dd037963d828e4e4eef3ede32a3db`, notice correction `78943a2c5e85866578decc1cfec5b222f9bd166d`, regeneration correction `3644c08bbf0ef1976bc634bba323779055583e6b`, and the working source changes. This is an independent reviewer using the inherited parent model. It is not model diversity or physical qualification. Only this review file was written by the reviewer. No deployment, generator, receipt, or server was changed.

## Current judgment

The numerical presentation and evidence packaging support a bounded research preview. The four displayed force pairs and fixture outcomes match the retained native Board archives. The UI and prose preserve physical uncertainty, the distinction between held-gap force and free-package support, the 200 µm fixture adaptation, and the separate 220 versus 270 µm clearance coupon.

The coordinator corrected all three documentation findings. Direct reinspection confirmed the generated wrapper README, Site hash-location statement, and current handoff recipes. The resulting stale media digest has also been repaired and independently rechecked. No blocking source-review finding remains. The coordinator still owns exact committed candidate extraction, native newcomer smoke checks, final browser playback and save-only Site qualification. This source review does not substitute for those checks.

## Findings and disposition

1. The generated example README gives replay arguments relative to the wrong directory. `tools/prepare_launch_assets.py`, in `example_files`, tells readers to run from a source checkout but uses `gap-300/board-comparison.zip` and `gap-330/board-comparison.zip`. Those folders belong to the separately extracted download. Use `/path/to/package/gap-300/board-comparison.zip` and its 330 µm counterpart, with an explicit instruction to replace the package path. The Site setup page already uses the correct form. Regenerate the wrapper and verify its actual download after this correction.
2. Raw-clone regeneration instructions produce filenames the app and candidate builder no longer consume. `force_lab/README.md` currently builds `output/soldershape-force-lab-r1.zip`. `coupons/README.md` builds `output/soldershape-coupon-r1.zip`. The notice-bearing fixed routes and `launch/build_candidate.py` require `output/soldershape-force-lab-r1-noticed.zip` and `output/soldershape-coupon-r1-noticed.zip`. `docs/getting-started.md` directs clone users to those guides for regeneration. Update the current build and verification recipes, or give one exact recipe in the maintained setup guide. Preserve historical package bytes.

Both numbered recipe findings are now repaired. The wrapper uses explicit `/path/to/package/` arguments. The handoff recipes select the noticed filenames at commit `3644c08bbf0ef1976bc634bba323779055583e6b`. Both rebuilt packages pass their own manifest verifiers. The updated force ZIP SHA-256 is `8f464edcfff0ce3b871050d76dc3a540a2c9fd590abd44f676fbc75a531a7f98`. The updated coupon SHA-256 is `c026038bae917917afadc2166e99b602a5cf9448012b4410fc83bd5da427a546`.

The Site setup page previously claimed the wrapper README identifies exact hashes. The exact hashes are in `manifest.json`. The coordinator corrected the page to identify that manifest and retain the README for replay instructions.

## Media follow-up and closure

The original `docs/media/lab-handoff.jpg` visibly prints the former force ZIP digest beginning `b0d7f2ba`. Rebuilding that package after the guide repair changed its digest to `8f464edc`. The current Lab page correctly removed the self-referential hardcoded digest and gives the existing manifest-verification command. Recapture this last frame from settled source, record its distinct source identity if the first five frames remain at `78943a2`, then rebuild and recheck the video and served assets. Otherwise the launch still contains an advertised digest that does not match its current download. No numerical evidence or first-five-frame change is required.

Closed after direct recheck. The coordinator refreshed all six actual captures at `3644c08bbf0ef1976bc634bba323779055583e6b`. The new Lab frame visibly states the member-manifest integrity procedure and contains no old archive digest. All six JPEG signatures and hashes agree with the new capture manifest. The served JSON identifies the same capture commit. All 100 served media identities match the refreshed inventory. The 92-member wrapper matches the regenerated expected bytes, including the corrected path instructions. FFprobe again reports exactly 36 seconds, H.264 at 1920 by 1080 and 24 frames per second, and no audio stream. Final uninterrupted browser playback and actual download remain the coordinator's explicit controls.

## Independent checks at the first media snapshot

- `python3 decision_walkthrough/verify.py` passed. It retained the literal 300 and 330 µm force pairs, unchanged pad binding, only-gap input change, fixture outcomes and unqualified physical status. This offline verifier checks the original default and gap probe archives. The separate served-media checks below verify the two UI-export archives used by the Site.
- `python3 -m unittest tests.test_workspace_http -v` passed all four checks. The fixed download routes preserve the selected notice-bearing package bytes.
- `python3 -m unittest tests.test_boundaries tests.test_cases tests.test_web_inputs -v` passed all 27 checks.
- `python3 -m unittest prelab.test_campaign.CouponRequests prelab.test_finite -v` passed all 14 checks.
- `node --check website/dist/site.js` passed. The three changed launch tools parsed successfully with Python AST.
- Direct inspection of `read_walkthrough()` matched the entire served `walkthrough.json` to both original UI archives. Both requests and corresponding case inputs differ only in held gap. The Site selects retained rows and screen booleans. It does not calculate forces or generate a physical recommendation.
- All 100 served media files matched the current inventory by member set, byte length and SHA-256. Both extracted evidence trees contain exactly 42 original members each, with identical bytes. The example wrapper contains exactly the expected 92 members and preserves both original inner ZIPs.
- Both advertised standalone lab ZIPs contain the exact root MIT grant. Their own package-verification commands also pass every manifest member. The force package SHA-256 is `b0d7f2ba7922a36afd571a27d26cd41c2b798e9630adfa45e746e242de9d2b5e`. Its 18,801,708 bytes agree with the Lab page's rounded 18.8 MB label. The coupon package SHA-256 is `bec71613b4959aec64e27e6a986c6760a55083f82704d9c011a688b0b81af402`.
- The six JPEGs have the JPEG signature and match their source capture manifest hashes. Visual inspection of the assumption, 300 µm, 330 µm, expanded-input and Lab captures matches the described sequence and limitations.
- FFprobe reports a 36.000000-second H.264 stream at 1920 by 1080 and 24 frames per second. No audio stream is present. The six caption intervals and concat source each cover the intended six-second stages. This is metadata and source inspection. Root owns actual uninterrupted browser playback.
- A direct HTML link and fragment check found no broken references among seven HTML pages and 108 local references. The maintained README, current launch readiness page and documentation link targets exist.

## Remaining publication gates

No public repository, private vulnerability-reporting endpoint, hosted CI run, release tag, or public Site audience is established by this review. Existing readiness and security docs state those gaps. The Site must stay owner-private during the current save-only preparation. Physical validation remains a separate gate before process accuracy or production decisions can be claimed.

Prove It Works required checking exact archive members and actual notice bytes instead of trusting a build or a prior report. It also kept source review separate from the coordinator's pending exact-candidate and browser checks.
