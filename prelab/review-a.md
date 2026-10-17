# Independent pre-lab review A

Reviewed the implementation and recorded evidence against base `33666d32c92b6753925bb2fd29dc62ce5fed618b`. This review used the inherited parent model. It does not represent model diversity. Only this review file was written. Temporary tampering checks used disposable copies. The unfinished finite-pad adapter is excluded from this verdict.

## Findings

### 1. [P2 warning] Fresh replay does not verify the identity of fresh receipts

**Location.** `prelab/replay.py`, lines 21 to 50, especially `calculate` at lines 29 to 43.

**Finding.** The replay checks the engine once before launching workers. It then trusts each fresh receipt's status, gap and forces. It does not verify the fresh `input`, `input_sha256`, `producer_engine`, or result `engine`. It also does not repeat the calculation-source and engine checks after the workers finish. A binary or source change during replay can therefore produce receipts whose provenance contradicts the report's exact-engine statement while the numeric comparison still passes.

**Evidence.** I invoked the actual `replay()` function with `subprocess.run` replaced by a disposable worker stub. The stub copied each original native receipt to the fresh destination, changed the requested load to `12345`, changed `input_sha256` to 64 zeroes, and changed both producer and result binary identities to 64 ones. Gaps and forces were retained. The function returned `{"passed": true, "requests": 13, "expected_rejections": 1}`. By comparison, the campaign verifier rejects the same input or producer mutations even after their member hashes are updated.

**Suggested repair.** Apply the campaign's fresh receipt identity checks before comparing values. Recheck the calculation source and exact engine identity after all workers finish. Preserve any contradicting receipt and return a failed replay. Add a regression that changes a fresh input or engine identity while leaving its gap and forces identical.

## Checks completed

- `python3 -m unittest prelab.test_campaign prelab.test_rigid_cap -v` passed all 18 tests.
- `python3 prelab/campaign.py verify prelab/evidence/campaign` passed. It regenerated 64 scenario-arm-boundary rows and 61 distinct requests. It retained 60 accepted requests and one failed negative control.
- `python3 prelab/rigid_cap.py --verify` reproduced the archived source hashes and every analytical result.
- Three additional disposable campaign mutations were rejected. These were a rehashed receipt with the wrong load, a rehashed receipt with the wrong producer binary identity, and an undeclared extra member.
- I checked both capillary-boundary conversions. A 14 mg cap supplies `14 * 9.80665 / 20 = 6.864655` micronewtons per joint. A 320 micrometer sphere gives `0.01715728467880506` cubic millimeters. Both copper-cylinder volumes are added once, and their combined 70 micrometer height is subtracted once. The artificial envelope has gravity disabled.
- I checked the rigid-cap mechanics. The three unknowns are the cap-plane height and two slopes. Its stationarity equations balance vertical force and both moments. Multiplying stiffness in newtons per meter by displacement in micrometers gives micronewtons. The recorded signed reactions retain tensile joints. The one-percent deformation screen is explicitly unqualified.

## Scientific interpretation checked

The verified native evidence gives the nominal C220 advantage as 15.796987 micrometers under literal rims and 10.889505 micrometers under the two-cylinder interpretation. The opposed requested geometric endpoints reduce those differences to 2.816094 and 0.843119 micrometers. The wider, explicitly unqualified opposite-volume stress reverses the differences to -4.212552 and -5.238158 micrometers. These are scenario calculations. They are not interval guarantees, measured process tolerance or physical validation.

The nominal literal-rim and two-cylinder results lie on opposite sides of the 185 micrometer numerical screen. The report does not average these hypotheses or select the favorable one. The cross-boundary reversal is labeled as an unobserved wetting-state difference. The laboratory addendum asks for independent contact-line, metal-height, mass, material and whole-cap measurements before a confirmatory freeze.

The rigid-cap report labels all twelve cases analytical and records zero native solves. Its gradient construction tests the gap-range gate at twenty idealized joint sites. It does not claim the minimum over the whole cap or a cooled clearance. Its symmetric pattern's tensile reactions and failed applicability screen remain visible.

## Limits

This review did not rerun the native campaign or the thirteen native replay calculations. It inspected their actual compressed receipts and regenerated the campaign conclusions offline. The replay provenance finding limits the current replay command's acceptance semantics. It does not show that the existing numerical values are incorrect.

The parent is separately adding the identical/reversed request controls and preserving the six exact baseline requests, including the actual-liquid solder-gravity controls. Those additions are outside this snapshot. The finite-pad adapter and its force checks require their own completed review. Unknown wetting, material inputs, cap compliance, continuous uncertainty extrema, and hot-to-cold transformation remain physical qualification gaps.
