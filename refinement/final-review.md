# Independent final refinement review

This review uses a fresh reviewer with the inherited parent model. It is independent within one model family. It does not establish agreement across model families. The base is `f2cfd9b`. Physical observations and customer interviews remain absent.

## Verification recorded before the final repair round

The criterion-straddle regression now returns `assumption_sensitive`. The 223.33 micrometer control retains an actual native reference gap below the criterion and an analytical result above it. Small absolute method agreement no longer resolves that threshold answer.

The static brief now lists the shared upper diameter, volume, load, offset, surface tension, density, gravity setting, sample fraction, both finished-metal thicknesses, and two-pad evidence declaration.

The coupon scorer parses and hashes one outcome byte snapshot. A source edit after parsing no longer changes its recorded identity. Freeze compares all four archived inputs with the original byte snapshots before writing its completed manifest. A changed archive retains partial receipts but cannot complete. Scoring also consumes the verified prediction bytes instead of reopening the path after verification.

The following independent command passed 21 tests after the final repairs. Its numerical doubles are labeled synthetic. It does not supply physical observations.

```sh
python3 -m unittest tests.test_study tests.test_study_http \
  coupons.tests.test_analysis.AnalysisChecks.test_score_hashes_the_exact_outcome_bytes_it_parses \
  coupons.tests.test_analysis.AnalysisChecks.test_archived_snapshot_changes_during_native_work_prevent_completed_freeze \
  coupons.tests.test_analysis.AnalysisChecks.test_score_uses_the_verified_prediction_bytes_when_archive_changes_after_read -v
```

`python3 -m unittest discover -s coupons/tests -v` separately passed all 34 coupon checks. Four checks inspect actual fabrication exports and reject deliberately changed geometry. `git diff --check` passed at this snapshot.

## Additional findings reproduced and repaired in this review

### Imported calculation code can disagree with archived source identity

The study hashes its source files from disk before and after calculation. A long-lived process can have imported those files earlier. An edit before the request changes the files while leaving the loaded Python functions unchanged.

An isolated package copy reproduced the defect without changing this workspace or running the native solver. The probe imported `soldershape.study`, changed the copied on-disk `SMALL_LOAD_FRACTION` from `.01` to `.02`, and reused the actual retained native result rows. Both `run_study` and `bundle_study` completed. The executing policy and reported analytical policy remained `.01`. The archived `calculation-source/study.py` declared `.02`. Its altered digest matched the report's claimed calculation-source identity.

The repair records each calculation module's source identity when that module loads. A study rejects disk source that differs from the loaded identity before starting its solve. It checks again after calculation and before export. The isolated-process regression passes for changes to each of `model.py`, `solver.py`, and `study.py`. Source hashes are integrity evidence. They are not authentication or proof against runtime monkeypatching.

### Native and analytical ordering can disagree while the result says unchanged

The criterion-straddle repair checks each arm against the declared threshold. It does not check whether the methods rank the two revisions in opposite directions.

A synthetic policy control used supported diameters `.2200` and `.2201` millimeters. Its native doubles differ from the formula by minus and plus `.1` micrometers respectively. The reference native gap was `223.24907200981605` micrometers. The candidate native gap was `223.41987299626325` micrometers. The analytical values were `223.34907200981604` and `223.31987299626326` micrometers. Both methods cleared the 185 micrometer criterion and passed the nominal agreement check. The report returned `screened_samples` despite opposite ordering. This is a decision-policy counterexample. It does not demonstrate native error on a physical specimen.

The repair compares native and analytical ordering within each hypothesis before reporting unchanged ordering. The same synthetic control now returns `assumption_sensitive`. The static brief also gained per-row numerical status and retained error messages.

## Replay semantics

A synthetic portability control retained a benign archived model-source byte difference and correctly updated its recorded hash. Fresh native doubles returned different engine identities with equivalent numbers. Replay returned `passed=true`, `verification_kind=numerical_equivalence`, `exact_engine_provenance=false`, `calculation_source_matches=false`, and `physical_qualification=unqualified`. Archive integrity still passed. This separates numerical equivalence from exact engine or application provenance. Archived calculation source remains inert and does not execute.

## Claim and trail checks

`refinement/POSITIONING.md` and `README.md` distinguish implemented workflow from demonstrated customer value. They claim no physical qualification, customer adoption, proprietary dataset, exclusive solver, or durable moat. The five-practitioner gate is a proposed investment rule. It is not a completed market study. The stronger analytical substitute and failed physical comparison remain visible.

All recent five `decisions.tsv` evidence paths resolve. All local links checked in `README.md`, `refinement/POSITIONING.md`, and `refinement/alternatives.md` resolve.

The primary sources were reopened during this review. The [upstream BGA index](https://kenbrakke.com/evolver/bga/bga.htm) explicitly lists load-controlled height, substrate barriers, lateral movement, tilt, and contact-angle examples. The [published paper](https://imapsjmep.org/article/39820.pdf) contains the unloaded spherical geometry and Eq. 9 stiffness comparator. The [Interface Equilibrator availability page](https://www.interfaceequilibrator.com/products.html) currently states that commercial products are unavailable and offers academic and trial licenses. These checks support the limited comparison. They do not establish that a competitor lacks a similar PCB workflow.

Prove It Works changed the review from accepting repair summaries to running the counterexamples and reading actual export bytes. No new native simulations, physical tests, vendor messages, purchases, or publication occurred in this review.

## Final artifact snapshot

No remaining software blocker was found in the inspected scope after the repairs. Physical qualification, practitioner demand, and a defensible measured operating domain remain unproven. Those limits require external evidence. This software review cannot clear them.

The refreshed `output/refined-pad-review.zip` has 63 members. The manifest names exactly its other 62 members. Every member digest passes. All three archived calculation sources match their report identities and current working-tree bytes.

| Artifact | SHA-256 |
| --- | --- |
| `output/refined-pad-review.zip` | `7a4c5025ef30daf2c83c1b0336f595bff2f97aaa9e00f0020070d7d23ece87da` |
| `soldershape/model.py` | `543720e8a6999896410aaf22651846c71b4f4736923ffe0ada0767ce35619657` |
| `soldershape/solver.py` | `c7bcfcc2c5f24e6e783540b3fcabc45a8d15308ded887aca2ae41442ddf4c8a6` |
| `soldershape/study.py` | `d60bde9448b523bc9b1bb6e59903974af5fa7f37252e9b12fd3ec598b2f76590` |
| `coupons/tools/analyze.py` | `1281e084bea82541b7b783506fa90acf6ae07f06c9b07bd3d7417063320cc45e` |

The four retained native rows all have `refinement_checked` status. Their pad-face gaps are `223.31880160132934`, `207.52181485954353`, `178.20338122353706`, and `167.31387797077113` micrometers. The order is reference literal, candidate literal, reference two-pad, and candidate two-pad. The archive returns `assumption_sensitive` and physical qualification `unqualified`. Its readable brief contains the shared load and materials, both finished-metal heights, and numerical status.

The root owns fresh native replay and real browser verification. This reviewer did not repeat those expensive native simulations or claim a separate browser run. The original R1 handoff remains historical. `coupons/REFINEMENT_NOTES.md` directs users to the separately named refined handoff and preserves old completed freezes.
