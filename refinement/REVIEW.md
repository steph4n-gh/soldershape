# Refinement result

SolderShape now completes one specific job for a packaging or assembly process engineer. Compare two actual board-pad revisions, expose the assumptions that could reverse the result, and hand a colleague or lab a reproducible study. It is useful for deciding what to measure before selecting a pad. It cannot approve that selection for manufacture.

There is no demonstrated moat. The engine and aligned analytical formula are existing work. The implemented advantage is a joined footprint-to-test workflow. Its defensibility would depend on independently useful, prospectively measured process evidence and repeatable laboratory execution. No customer demand, saved production iteration, exclusive dataset or lab relationship is claimed. [POSITIONING.md](POSITIONING.md) defines the proposed five-practitioner investment gate and stop conditions. [alternatives.md](alternatives.md) compares primary sources and states when simpler methods win.

## What changed

The new study keeps each imported footprint and pad identity. It requires a named pad-face requirement, common conditions and input/boundary declarations. Two or four actual native solves sit beside the independent published analytical comparator. Three volume samples per revision and mapping expose finite sensitivity without claiming an interval or manufacturing yield. Save/reopen, a static brief, CSV, native receipts and labeled geometry are included in one hashed archive. No engine rewrite or added dependency was needed.

| Reproduced defect | Repair and retained check |
| --- | --- |
| A declared smaller mask opening still allowed a copper-rim model. | Reject explicit negative inherited or local margins. Actual browser rejection and regression cases pass. Unknown board/CAM rules remain unresolved. |
| Native and analytical values could straddle a criterion or rank revisions differently while reporting unchanged results. | Both contradictions now return assumption_sensitive. Counterexamples remain in the focused tests and review reports. |
| A readable brief omitted the conditions defining its results. | Include load, geometry, material inputs, both metal heights, evidence, numerical status and failures. |
| Source files could change after import while their new hashes labeled old executing code. | Capture import-time identities and reject changes before computation, after computation and before export. Archived source stays inert. |
| Coupon validation, archive creation and scoring could consume different worksheet bytes. | Validate, predict, archive, score and hash immutable byte snapshots. Reject changed frozen outputs before sealing. |
| Numeric-string metadata crashed scoring. Excessive declared input uncertainty still allowed agreement. | Normalize metadata and enforce the existing coarse five-micrometer input sensitivity screen. It is necessary, not a native uncertainty qualification. |
| New example files changed the default fixture through directory ordering. | Select the original example by its provenance metadata. Preserve the failed integration run in product-tests-default-fixture-failure.log. |

## Actual planning result

These are artificial coupon inputs, not physical observations. Upper diameter is 280 micrometers, liquid volume 0.01715728467880506 cubic millimeters, supported per-joint load 6.864655 micronewtons, tension 0.48 N/m, offset zero and gravity off. The optional equivalent-domain approximation adds 35 micrometers of metal at each pad, then subtracts their total height from the solved domain. Both models are unqualified for physical predictions.

| Lower pad | Literal-rim native gap | Two-pad approximation gap |
| --- | --- | --- |
| 220 micrometers | 223.318802 micrometers | 178.203381 micrometers |
| 270 micrometers | 207.521815 micrometers | 167.313878 micrometers |

All four native rows passed their numerical checks. Maximum nominal difference from Eq. 9 was 0.0464 micrometers. That is agreement between computations, not measured physical accuracy or superiority over a spreadsheet. The declared 185 micrometer pad-face criterion changes sides under the geometry hypothesis for both revisions. The correct action is to measure finished metal, volume and wetted boundaries in a controlled pilot. Neither revision receives physical approval. A pad-face criterion does not measure package clearance above solder mask.

## Verification and delivery

The application passed 52 tests in product-tests.log. The coupon package passed 34 checks in coupon-tests.log. The browser completed separate imports, save/reopen, four native cases and download. Editing a pending request prevented its late result from restoring an export. An explicitly smaller mask opening disabled unsupported computation. See [browser-workflow.json](browser-workflow.json) and [decision-review.png](decision-review.png).

The actual browser archive is `output/refined-pad-review.zip`. Its SHA-256 is `7a4c5025ef30daf2c83c1b0336f595bff2f97aaa9e00f0020070d7d23ece87da`. Its exact 63-member file set and all 62 listed member digests matched the manifest. A fresh four-case native replay passed with matching engine and calculation-source identities. A deliberately edited sample table was rejected. [study-replay.json](study-replay.json) retains exact values and checks.

The corrected lab handoff is `output/soldershape-coupon-r1-refined.zip`. Its SHA-256 is `f20c7e9cb70bb400c3ad2a6fbb97c088757a39f5ecdd9db3f6bf4683e16bb1ea`. It contains the repaired analyzer with unchanged fabrication geometry. An extracted copy passed all 83 member hashes, the board geometry verifier and 34 coupon checks. [extracted-lab-checks.json](extracted-lab-checks.json) retains the subprocess outputs. The original R1 archive remains historical and unchanged.

From the repository root, reproduce the new study and verify its actual exported computation.

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8766
```

Open http://127.0.0.1:8766/study. In another terminal, run the CLI workflow or replay the supplied artifact.

```sh
python3 -m soldershape study examples/coupon-planning.study.json --output output/pad-review.zip
python3 tools/verify_study.py output/pad-review.zip --replay
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s coupons/tests -v
python3 coupons/tools/package_lab.py --verify output/soldershape-coupon-r1-refined.zip
python3 coupons/tools/verify_boards.py
```

The saved browser study uses separately entered planning declarations, so its study hash differs from the bundled example's hash. Its numerical inputs and results are the same. Physical campaign reports predate this refinement and retain their original source identities. No new physical samples were measured. The old force-validation failure remains unresolved.

[final-review.md](final-review.md) records fresh independent counterexamples and their repairs. Review used the inherited model family. No software blocker remained within the reviewed scope. Physical operating-domain qualification and practitioner demand are the main unresolved risks. The most useful next work is the controlled lab pilot and practitioner gate, rather than broadening simulation features.

Model the Domain led to one study owning both source revisions and a server-owned decision. Experience First led to one complete import-to-brief workflow. Build the Lever and Prove It Works led to a rerunnable artifact verifier and real browser/native checks. Explain the Number kept numerical agreement, finite sensitivity and physical uncertainty separate. Sequence Work into Verifiable Units kept the first failures and each repair reviewable.
