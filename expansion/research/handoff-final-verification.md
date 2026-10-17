# Final portability and handoff verification

This is a fresh same-family, read-only verification of the portability repair. It does not repeat the earlier scientific review, change the solver, inspect the shared browser, or establish physical validation. I changed only this report. All independent mutation controls used temporary directories and synthetic observations.

## Portability result

The current 30 force-analysis behavior controls passed in 1.450 seconds. I separately created a synthetic planning record and prospective freeze, then replaced both `engine_info()` and `solve()` with functions that raise `AssertionError`. Static planning verification, externally registered freeze verification and synthetic scoring all succeeded without invoking either function. The static planning result explicitly reports `native_replay_performed: false`. Exact synthetic outcomes support only the declared isolated endpoints.

I then changed the archived engine identity. Planning verification rejected the contradiction with the recorded receipt producer. A changed frozen manifest failed against its original independently registered SHA-256. Even supplying the changed manifest digest could not hide the contradiction between its archived producer and its receipts. These are integrity controls, not evidence that any synthetic force is physical data.

The repair removes the current host engine as a prerequisite for reading archived evidence. It retains the loaded-source versus disk check, exact protocol and allocation snapshots, exact member and file hashes, expected planning request identities, complete receipt-set checks, and comparisons of every completed receipt's engine identity with the archived producer. Native planning and physical-input freezing still invoke the native solver. Failed attempts may retain an unavailable archived engine and remain failed evidence; a completed receipt cannot silently lose its producer identity.

The prospective freeze continues to require an independently registered manifest digest. Static archival verification does not claim authentication by a third party, replay on another architecture, or physical accuracy.

## Package tool review and controls

I inspected `package_lab.py` and `verify_handoff.py`. The latter reads the package bytes, verifies its identity, extracts into a new directory, and invokes the extracted analyzer and behavior controls with that directory as the working root. Its optional CAD Python path is resolved before changing the subprocess working directory. It records whether an engine cache exists and expressly limits the result to static evidence, synthetic controls and optional neutral CAD readback.

Four independent synthetic archive mutations were rejected: changed member bytes, a missing protocol member, a parent-traversal member name, and a fabricated `physically_validated: true` status. The synthetic nominal archive was only an integrity-control fixture; its pretend STEP bytes were not passed to the CAD verifier and are not represented as valid geometry.

## Retained source identities

| File | SHA-256 |
|---|---|
| `force_lab/tools/analyze.py` | `2613c2d36a4732555b6f423371066a5e80549ad81e0d8f89e200f899ec6acd02` |
| `force_lab/tests/test_analysis.py` | `4cf711b3f29473a48afa5f3f0da70ec897b4fce736a488cf7424abb8179cd21a` |
| `force_lab/tools/package_lab.py` | `5a1426ba088c5d417be180576e7ae0ff3cee14019481e16a0ba3c3665e8644c3` |
| `force_lab/tools/verify_handoff.py` | `d13d64a2521b1781dc55d2d033806f7f5f1ec1f651b863eda78feaf3b72641a6` |
| `soldershape/model.py` | `543720e8a6999896410aaf22651846c71b4f4736923ffe0ada0767ce35619657` |
| `soldershape/solver.py` | `c7bcfcc2c5f24e6e783540b3fcabc45a8d15308ded887aca2ae41442ddf4c8a6` |
| `force_lab/protocol.json` | `3320633962e270b1258c30a8f7ab013bc53f81359080507b54092f8eaefb6276` |

The earlier failed extracted check remains preserved by root in `expansion/extracted-check-1.log`. It exposed a host-cache dependency and is superseded only by the fresh extracted result below. The earlier planning record was preserved intact at `output/force-plan-pre-portability`; it is not the current producer qualification.

## Final native record and extracted package

The regenerated native plan independently passes `verify-plan` for all 20 expected requests. Both nominal volume cases are eligible and `refinement_checked`. Plan SHA-256 is `928978bb11345a7167bd5a1944f89d80edbf7d819cbc147b8b27e016f25c4a1b`. I repeated this check with both host-engine functions raising and obtained the same result without replay. The archived producer is Surface Evolver 2.70a, upstream source SHA-256 `be7d60d9eb690f1fb124e2ecc12237a7a35be1935bfa5e92be3fe912207a3b6b`, binary SHA-256 `c930b47b33a4cafb3cf98b1c0cb7e3bd9805abcf67aceefe243daea091072f8e`, and reference archive SHA-256 `96389e8200320cc8acfbf60b8ed23e2d05941613af5b55824c36890113c6e659`.

I independently hashed and verified the final `output/soldershape-force-lab-r1.zip`. Its SHA-256 is `0b4ee985fc0bde510385e92656bfac7c8df92e73f3be4a4e69e5770e9fa63274`, with 128 members and 18,779,732 bytes. It remains prepared for quotation, not lab accepted, fabrication released or physically validated.

I read the actual final extraction receipt and all three subprocess logs in `output/force-r1-final-extracted`. Static verification accepted the same 20-request plan identity. The extracted 30 behavior controls passed in 1.347 seconds. The CAD readback passed with 16 neutral parts, modeled moving mass 40.39420566439091 mg and modeled deadweight 396.1318369786991 microNewtons. Its own result retains quote-stage status and unaccepted physical integration. I did not rerun the CAD verifier, which rewrites evidence, during this read-only review.

I independently imported the analyzer from that extracted root, asserted that its `ROOT` was the extracted directory and that `.engine` was absent, and successfully verified the actual final plan while both `engine_info()` and `solve()` raised on any call. The extracted analyzer has the same retained source SHA-256 as the checkout. This closes the former host-cache portability failure. It establishes engine-free static reading on this host, not fresh native computation on another operating system.

All seven source identities in the table remained unchanged at the final check. No material residual blocker was found within this bounded portability/package scope. No physical observation was acquired and no claim of physical validation is supported by these checks.
