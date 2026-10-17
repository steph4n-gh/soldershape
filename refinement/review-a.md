# Adversarial review A

The review used the inherited parent model. It is independent review within the same model family. It does not provide cross-model agreement.

The reviewed intent is a useful comparison of two actual footprint revisions that leads to a justified test. The implementation must preserve negative physical evidence. It must not imply qualified predictions, a superior solver, or a demonstrated moat.

## Findings

### 1. Warning. A native and analytical threshold contradiction can receive an unchanged-samples conclusion

The affected code is `soldershape/study.py` at lines 156 through 178. `_decision` checks an absolute native-to-analytical gap tolerance. It then uses only analytical samples to decide whether the criterion changes sides. It never checks whether the native and analytical nominal results themselves give opposite criterion answers.

I reproduced this with the actual results already stored in `output/refined-pad-review.zip`. I set `two_pad` to null, `volume_fraction` to zero, and the criterion to 223.33 micrometers. I supplied the archived native results to `run_study` by request hash. This reused actual recorded native computation. It was not a fresh native run or a physical measurement.

The Reference native gap is 223.31880160132934 micrometers. Its native margin is negative 0.01119839867067185 micrometers. The analytical gap is 223.34907200981604 micrometers. Its analytical margin is positive 0.019072009816028412 micrometers. The report still returns `screened_samples` with the headline `The criterion and ordering stay unchanged at the sampled points.`

The physical qualification warning prevents a manufacturing approval claim. It does not resolve the contradictory numerical answer inside the study. A threshold between the two methods cannot be treated as resolved merely because their absolute discrepancy is small.

Compare the native and analytical nominal criterion signs before an unchanged-samples result. Withhold that result when the methods disagree about the declared question. Report the numerical ambiguity explicitly. The same check should cover opposite native and analytical ordering of the two revisions.

### 2. Warning. The readable decision brief omits the conditions needed to interpret its result

The affected code is `soldershape/study.py` at lines 243 through 268. `_decision_html` prints the criterion, provenance text, footprint hashes, calculated gaps, and sample volumes. It omits the shared upper diameter, normal load, offset, surface tension, density, gravity setting, volume fraction, and both finished-metal thicknesses. It also omits the two-pad evidence declaration.

I read the actual `decision.html` in `output/refined-pad-review.zip`. The load value and the exact two-pad evidence declaration are absent. The report's two-pad rows therefore show a threshold reversal without identifying the 35 micrometer lower and upper metal assumptions that cause it.

The inputs remain recoverable from `study.json`. That does not satisfy the promised readable brief for an engineer who needs to inspect the conditions and controlling assumptions. Add the normalized shared inputs with units and the optional geometry hypothesis with its thicknesses and evidence. Include native numerical status or failure details per row so an unavailable result also remains interpretable in the brief.

### 3. Warning. The scoring outcome hash can identify different data from the data actually scored

The affected code is `coupons/tools/analyze.py` in `score`. The outcomes are read through `outcome_rows` near line 435. The report later hashes the live outcomes path near line 536. The score and its hash do not share one immutable byte snapshot.

I reproduced this using `coupons/tests/test_analysis.py` and its explicitly synthetic fixtures. After the scorer parsed 200 micrometer outcomes, a test hook rewrote the worksheet with 300 micrometer outcomes just before `sha(outcomes)`. The returned score retained an observed mean of 200 micrometers and `consistent_at_frozen_inputs`. Its `outcomes_sha256` matched the rewritten 300 micrometer file.

This is the outcome-side version of the input snapshot inconsistency repaired in this change. An operator who edits a worksheet during scoring can receive an audit record whose cited source bytes cannot reproduce its result.

Read the outcome bytes once. Parse and hash those same bytes. Preserve the bytes with the score or clearly state that the score identifies a snapshot whose source path may subsequently change. A later edit to the source path must not change the report's recorded snapshot identity.

## Checks and limits

`python3 -m unittest tests.test_study tests.test_study_http -q` passed all 14 tests during this review. The three counterexamples above ran locally. The coupon counterexample used synthetic inputs and outcomes only. No physical measurements, commercial competitor tests, or customer observations were made. Root owns actual browser verification.

I found no additional security or structural blocker in the inspected changes. I did not modify product code or tests.
