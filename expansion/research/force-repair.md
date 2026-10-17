# Force analysis repair and verification

This repair addresses A1-A3 in `review-a.md`. It supersedes the earlier force-analysis implementation report where the contracts changed. No physical force observations were acquired. The shipped physical templates remain blank.

## Joint uncertainty sources

Input and corrected-force budgets now name the same physical source with one ID, source unit, standard uncertainty and signed coefficients. Reusing an ID with a different unit or standard uncertainty rejects the freeze. Differently named sources require an explicit independence assertion and supporting metadata evidence. Unknown cross-domain covariance cannot silently become independent quadrature.

Endpoint and individual residual guards now combine each source's measured-minus-predicted coefficient before squaring. Marginal input and measurement uncertainties remain visible and their capability gates remain active. A common systematic term does not shrink with specimen count.

The reviewer's synthetic common-temperature counterexample now has residual expanded U about 4.000002 µN and fails the 3 µN normal precision gate. The same signed 1 µN/K coefficient in both prediction and corrected force cancels in the residual while each marginal U remains about 2 µN. Its residual U about 0.004082 µN comes from the remaining independent synthetic input terms. These are software controls, not physical measurements.

## Planning decisions and numerical limits

Planning generation and verification share one pure derivation. Verification reconstructs the exact expected requests from the frozen protocol, reads their raw receipts, checks the complete receipt/source member set and identities, then recomputes every case, Jacobian, qualification flag, resolution flag, target, one-source limit and budget conclusion. Rewritten valid JSON containing a false contrast, false budget pass, altered sensitivity step or false qualification now fails.

The two force changes defining each derivative are compared with their saved numerical-refinement changes. Unresolved derivatives remain in the raw Jacobian but cannot create allowable input limits. Algebraic budget crossings outside the registered 2 percent input-U domain also yield null. Thus all density limits are null. The normal density change is resolved locally, but its algebraic 65 g/cm³ crossing exceeds the 0.18 g/cm³ domain. Its lateral changes are numerically unresolved. The normal offset-only crossing at 5.532 µm is also null because it exceeds the 2.4 µm domain. These limits cannot be advertised as tolerances.

Twenty native requests were rerun after the final analyzer change. The original pre-review package remains unchanged at `output/force-plan-pre-review`. An intermediate pre-domain-clamp package remains at `output/force-plan-pre-domain-limit`. Both are local ignored evidence. The shipped final planning record is `force_lab/planning/native-120` and includes exact current source snapshots.

The original numerical forces and budget conclusions are unchanged. At 120 µm, 5/7 nL produce lateral forces -92.26328365/-82.19306382 µN. Their signed contrast is +10.07021982 µN. The 7 nL normal force is +7.61948089 µN. The initial unmeasured budget gives normal guard 5.64430438 µN and fails. The tighter unmeasured candidate gives normal guard 2.45238424 µN and passes the local screen. Neither is a demonstrated instrument capability.

## Transverse alignment

Frozen inputs now require actual relative y and positive expanded uncertainty. Confirmation outcomes require independently observed actual y and expanded uncertainty. Both must satisfy `abs(y) + U_y <= 0.0005 mm` with justified k=2 coverage. A missing frozen value rejects freezing. Missing or excessive confirmation values are inconclusive. A synthetic 40 µm y displacement can no longer pass an x-only comparison.

This is an initial apparatus-domain policy for the unmodeled direction. It does not establish physical accuracy at the bound, add a two-dimensional force model, or replace physical qualification. Tighten it prospectively if commissioning finds a consequential transverse effect.

Protocol and freeze schemas are revision 2. Blank templates and `ANALYSIS.md` describe the new source and y fields. The original height-coupon, stress-demo records, `soldershape/model.py` and `soldershape/solver.py` were not edited.

## Reproduce

Run from the repository root.

```sh
python3 -m unittest force_lab.tests.test_analysis -v
python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120
python3 force_lab/tools/analyze.py plan output/force-plan-independent-replay
```

All 24 behavior controls passed. They include shared-source amplification and cancellation, conflicting units and standard uncertainties, unknown independence, missing or excessive frozen/observed y, edited planning conclusions and out-of-domain extrapolation. Raw test output is `output/force-analysis-final-tests.txt`. Final planning verification is `output/force-plan-final-verification.json`.

Final identities are:

- Analyzer SHA-256 `06c97695dfa123a3467625a9de4c480475ed2c119a3377bc3fa448eb5d9989c6`.
- Protocol SHA-256 `3320633962e270b1258c30a8f7ab013bc53f81359080507b54092f8eaefb6276`.
- Final plan SHA-256 `ec22a9e77533c694757cc486aaa17ae5a6eee345ea189212a3429c7184ab25eb`.

Verification returned `PLANNING_BYTES_AND_DECISIONS_VERIFIED_NOT_PHYSICAL_VALIDATION` for all 20 requests. No lab was contacted, no purchase made and no physical outcome fabricated.

Model the Domain shaped the unified physical-source identity. Fix Root Causes moved covariance into the residual calculation. Explain the Number removed unresolved and out-of-domain tolerance claims. Prove It Works required fresh native receipts and executable failure controls. Test Behavior, Not Implementation shaped the false-pass and inconclusive-result checks.
