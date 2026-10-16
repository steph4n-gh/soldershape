# Independent implementation review

Reviewed on October 16, 2026 by a separate agent instance using the configured inherited model. This is an independent reading and reproduction, not a review across different model families.

## Disposition

No material correctness finding remains open in the reviewed implementation. One replay failure-handling defect was reproduced and repaired during review.

The evidence supports a local numerical prototype for comparing single-joint equilibria under the declared pinned, fully wetted circular-pad assumptions. It does not establish physical accuracy, practitioner demand, manufacturing readiness, global equilibrium minimality, or the commercially ideal project. The selection document labels the workflow advantage as an inference and keeps its counterargument and reversal conditions visible.

## Finding and repair

P2, resolved. The original `soldershape/__main__.py` replay loop called `solve(spec)` outside a per-row failure handler. Replaying a bundle with an input that failed again raised an uncaught `SolverError`, emitted no JSON report, and skipped later cases. A repeated failure was therefore harder to inspect than the original exported failed row.

The reproduction created a two-row failed bundle with the public `make_bundle` function and made the solver boundary raise `SolverError("same upstream failure")`. Before repair, replay propagated the exception and produced zero report bytes. This reproduction tests error handling at the solver boundary. It is not an additional physical or numerical solver experiment.

The repaired replay loop records each current failure, preserves its error text, continues through the remaining rows, and returns a failing exit code. The new `test_replay_reports_each_failed_case_and_continues` checks both solver calls, both reported rows, and the nonzero outcome. Review also inspected the added saved-result validation in `artifacts.py` for object types, declared status, required forces, and finite numerical force values.

## Scope and checks

Read `soldershape/model.py`, `solver.py`, `artifacts.py`, `__main__.py`, all browser assets, `tools/setup_engine.py`, `tools/verify.py`, and `tests/test_boundaries.py`. Read the README, acceptance criteria, architecture record, selection rationale, third-party provenance, workflow, decision log, numerical acceptance report, and solver development record. The research directory and upstream engine source were outside this review's scope.

- Ran `python3 -m unittest discover -s tests -v` after the replay repair. All 12 tests passed, including the failure-replay regression and real HTTP import and origin checks.
- Opened both acceptance ZIPs with `read_bundle`. The sweep contains five cases and the single-case export contains one. The sweep SHA-256 matches `evidence/acceptance.json` and every archive member passes its manifest hash check.
- Reviewed the cgs conversions and force signs. Millimeter coordinates become centimeters, cubic millimeters become cubic centimeters, N/m becomes dyn/cm, and dynes become micronewtons. The derivative calculation retains the pressure correction needed by the fixed-volume virtual displacement.
- Read the stored published-reference, analytic cylinder, mirrored-offset, tension-scaling, volume, unequal-pad, mesh, and replay evidence. The reported acceptance tolerances agree with the checks in `tools/verify.py`. This reviewer did not rerun that complete numerical suite.
- Confirmed that the earlier unequal-pad `not_converged` result remains in `evidence/solver-development.json`, alongside the subsequent bounded refinement result. The successful refinement does not erase the failed initial check.
- Reviewed result invalidation, asynchronous revision checks, immutable response data, result-row selection, and download construction. Geometry and archive bytes come from the accepted response. Changes to the physical inputs clear that response. The parent's separate live browser exercise is not represented here as this reviewer's direct observation.
- Reviewed replay generation. Archive scripts remain evidence. Replay parses bounded normalized numerical inputs and calls the application's current trusted model generator. It does not execute archived Evolver commands or extract archive paths.

## Comment review

Applied the Comment Sicko perspective without deleting scientific provenance or changing application code. No scoped lint, type, or security suppression was found. No misleading constraint comment or comment-protected workaround requires a change. The generated mesh unit declaration and source/derivation provenance are useful metadata. Comment deletions and restorations are both zero.

## Remaining qualification limits

The implementation deliberately reports its runtime mesh checks separately from the representative transverse-intersection checks. Closed, oriented, nondegenerate geometry is not a complete self-intersection or printability certificate. The README states that boundary clearly.

KnotForge's build experiment did not qualify its tightening or export behavior. The project record presents that as an uncompleted numerical gate rather than evidence that Ridgerunner is an inferior optimizer. SolderShape's better local reference evidence justifies this bounded first implementation. Further investment still depends on a practitioner identifying a useful decision within its physical assumptions.
