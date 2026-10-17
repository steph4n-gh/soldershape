# Documentation synchronization

The assigned prose now describes one Board decision. Actual ULX3S U1/J16 lower copper supplies the 400 µm source geometry. The upper pad and process values remain hypothetical. At a 300 µm held gap, only 40 nL meets the declared numerical fixture rule. At 330 µm, both 40 and 56 nL meet it. Two sampled hypotheses do not establish manufacturing tolerance, a physical error bound or a production choice.

## Changed files

- `README.md` leads with the design question, explicit example load and restore, changed-gap action, result invalidation, evidence and matching lab handoff. Its image points to `board-explorer.jpg`, matching the actual JPEG capture bytes. Its media link describes six actual stills and a 36-second video.
- `docs/README.md` makes the decision walkthrough the entry point and links the current engineering record.
- `docs/getting-started.md` gives the exact visible sequence. It distinguishes the initial verified recording from fresh native computation, explains the force signs, preserves all eight recorded force values, and follows exports through `/lab#board-question`.
- `docs/development.md` uses explicit new output paths, separates the offline archive check from native replay, and describes current browser acceptance checks. The mocked shared-UI runner has an explicit new receipt path.
- `docs/model-and-validation.md` tabulates both gaps and both volumes beside their numerical outcomes. It separates identified copper, assumed process conditions, numerical consistency and physical accuracy.
- `website/dist/start.html` gives the matching local workflow and replay commands for both immutable inner archives.
- `website/dist/validation.html` carries the same numerical results, limits and lab requirements.
- `website/dist/transcript.html` describes six six-second actual captures, no audio and editorial timing. It uses the agreed public media and review paths.

The held-gap fixture objective remains distinct from supporting a free package's weight. The existing 200 µm fixture requires adaptation and qualification for this 400 µm joint. The separate 220 versus 270 µm twenty-joint height coupon uses a 185 µm clearance target. Its conditional pad ranking cannot qualify these board-joint forces.

## Verification

`python3 decision_walkthrough/verify.py` passed. It verifies the two retained native archives, exact force values, source-pad binding, one-input gap change and numerical fixture outcomes. It does not run a new physical experiment or qualify force accuracy.

A local reference check parsed the eight assigned documents. At the time of this check, every current local reference existed except the three references to `media/gap-330-evidence/review.html`, which the root-owned asset build will produce under the agreed contract. `git diff --check` passed for all eight assigned files. Their authored text contains no em dash.

The image extension was subsequently updated to `.jpg` after the capture owner identified the actual JPEG format. The root acceptance pass checks the completed capture files. No generator, Git commit, deployment, application-source edit or third-party-notice edit ran in this workstream. Publication state remains pending in the pages. No public source URL or hosted solver was invented.

## Root integration checks

The root owner still needs to produce the six actual captures, refresh `docs/media/README.md`, replace the old media, and check the capture-to-transcript correspondence. `website/dist/credits.html` still had the old 24-second and three-still description when read. That page is outside this workstream's write scope.

The agreed package is `media/soldershape-recorded-example.zip`. Its immutable native archives are `gap-300/board-comparison.zip` and `gap-330/board-comparison.zip`. The public reviews are `media/evidence/review.html` and `media/gap-330-evidence/review.html`. Root must verify these generated paths and the actual downloaded bytes before release.

Technical Writing gave each document a clear task or reference role. Unslop kept the claims concrete. Existing structure and routes were reused. Final source packaging, running-browser checks, Site audience and public-release readiness belong to the root acceptance pass.
