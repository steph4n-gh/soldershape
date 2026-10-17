# Comment review

Reviewed the refinement changes against `f2cfd9b` on 2026-10-16. The review includes the new study service, browser, tests, footprint mask repair, coupon freeze repair, and command integration. This reviewer made no application edits.

## Actionable findings

1. Remove the guessed API variants in `soldershape/web/study.js`.

   At line 227, `data.study || data` accepts an undocumented wrapper. The actual `/api/study/example` handler at `soldershape/__main__.py:140` returns the study directly. Pass `data` to `applyStudy`.

   At lines 421-427, the bootstrap chain accepts `data.engine_ready`, `engine.available`, `engine.version` as readiness, and `data.engine_error`. These are alternative contracts that this repository does not produce. The handler at `soldershape/__main__.py:134` always places `engine_info()` under `engine`. All three returns from `engine_info()` at `soldershape/solver.py:33` include a Boolean `ready`. Read `data.engine.ready` and `data.engine.error` directly. A missing or malformed service response should reach the existing request failure path rather than appear ready because it has a version string.

   At line 414, `state.response.bundle_filename || "soldershape-study.zip"` adds another fallback to a field always supplied by `/api/study` at `soldershape/__main__.py:189`. Use the returned filename directly.

   These are our own interfaces. There is no external compatibility constraint requiring the alternatives. No broader abstraction is needed.

2. Delete two redundant descriptive docstrings.

   `soldershape/study.py:1` restates the module's responsibility. The schema constants and public operations already expose that responsibility.

   `tests/test_study.py:23` restates `synthetic_native`. Its returned engine identity and raw evidence already say `synthetic-test-double` and `SYNTHETIC TEST DOUBLE`. Keep those executable evidence labels. They distinguish synthetic tests from actual native calculations.

## Checks and scoped keeps

Python tokenization found zero comment tokens in the new study module and new study tests. The only comment token in the modified Python files is the existing executable shebang in `coupons/tools/analyze.py:1`. It predates this refinement and is outside the changed lines.

The browser JavaScript, CSS, and HTML contain no comment blocks. The scoped files contain no `noqa`, type-ignore, TypeScript suppression, ESLint-disable, coverage pragma, or safety suppression. No imperative constraint comments need an encoding offer. No phase-narrating comments were found.

The existing module docstrings in `soldershape/__main__.py`, `soldershape/model.py`, and `coupons/tools/analyze.py` are unchanged. They were not treated as new findings.

The UI qualification, mask-scope, finite-sample, and synthetic-evidence strings are product data or visible explanations. They are not comments. Their wording carries distinctions that the study needs, so this review does not request their deletion.

## Observed interface proof

A fresh in-process `Server` bound to an ephemeral loopback port returned these keys through real HTTP requests.

- `/api/bootstrap` returned `application`, `engine`, `example`, and `token`. Its `engine` object included `ready` and `version`. No top-level `engine_ready` or `engine_error` existed.
- `/api/study/example` returned the raw `soldershape.study.v1` document. Its keys included `reference`, `candidate`, and `parameters`. No `study` wrapper existed.

The probe started and closed its own server. It did not use or restart the user's running workbench.

## Disposition

Deletion count is zero because this assignment is report-only. No comments were restored. No rerun or architect sketch was needed. There are no correctness or safety suppressions to remove. The two findings above remain open for the root agent to accept or reject. No other comment constraints remain open.

## Root disposition

Accepted both findings. Removed the two unused descriptive docstrings and replaced the guessed API variants with the actual response contract. No comments were restored. No suppressions, constraint encodings, or unresolved comment findings remain. These were direct deletions and did not need another architecture sketch.
