# Coupon freeze and scoring repairs

The refinement audit found a completed freeze that could contradict its archived inputs. It also found a scoring crash and an unenforced input uncertainty stop condition. The repairs below concern software evidence. They add no physical observations.

## Before and after

Each regression uses the existing explicitly synthetic input and outcome fixtures. Its solver double does not provide physical or numerical validation.

| Counterexample | Before repair | After repair |
| --- | --- | --- |
| Change source cap mass after validation. | The accepted archive records 28 mg. The prediction uses 14 mg and a 6.864655 micronewton joint load. | The archive retains the exact validated 14 mg snapshot. The source worksheet can change to 28 mg without changing that snapshot or its requests. |
| Change source surface tension after validation. | The accepted archive records 0.96 N/m. The prediction uses 0.48 N/m. | The archive and prediction both retain 0.48 N/m. |
| Submit temperature and uncertainty as JSON numeric strings. | Freeze completes. Score raises a float-minus-string `TypeError`. | Score validates and normalizes the archived metadata before use. |
| Set the 2.9 mg solder kit's expanded uncertainty to 1.4 mg. | The retained analytical screen exceeds 80 micrometers. Score still reports central model agreement. | The coarse input uncertainty screen fails. Liquid model agreement is inconclusive. Measured clearance and paired process comparisons remain available. |
| Change experiment, allocation, or prediction code during validation. | The old checks start too late to reject every change between validation and archive creation. | No completed manifest is written. Partial native receipts remain available. |

The first four regressions were run before the repair. The CSV and metadata tests failed on archived values of 28 and 0.96. The numeric-string test raised the stated `TypeError`. The uncertainty test returned `consistent_at_frozen_inputs` instead of `inconclusive`.

## Data ownership and implementation

The authoritative data shape is a map from four archive filenames to immutable `bytes`. Freeze reads inputs, metadata, experiment, and allocation once. The CSV and JSON parsers consume those bytes. Validation and prediction use the resulting values. Archive creation writes those same bytes.

A temporary-file snapshot was considered. The in-memory map avoids another copy step and a temporary directory for four small files. No lock or transaction framework is needed.

`validate_inputs` now receives parsed rows and the validated snapshot allocation. It no longer opens a mutable source path or reloads allocation. The code hash baseline now precedes input validation. Existing final code, experiment, and allocation consistency checks remain in place.

Score validates the archived raw metadata again. This preserves the submitted source evidence while applying the same numeric normalization that freeze uses.

Score exposes `coarse_input_uncertainty_screen_gate` and the retained `analytical_input_sensitivity` for each measured phase. The screen must fit the declared height error budget before a molten model can receive central agreement. Passing this screen is necessary but insufficient. It omits interactions, offset, copper mapping, correlations, and native uncertainty propagation. It does not qualify a physical model.

## Verification

Run the repaired analysis tests from the repository root.

```sh
python3 -m unittest coupons.tests.test_analysis -v
```

Measured result is 27 passing tests. The definition-change test covers experiment and allocation separately. The code-change test rejects a source edit during validation. Existing blank-input, native-failure, cold-only, wetting, temperature, uncertainty, offset, and missing-outcome checks still pass.

Run all coupon checks.

```sh
python3 -m unittest discover -s coupons/tests -v
git diff --check
```

Measured result is 31 passing tests and no whitespace errors. The four additional checks inspect actual fabrication exports and reject deliberately changed geometry.

The repaired freeze also ran the real native engine on the explicitly synthetic fixture. Its 24 cap inputs required six distinct cached native requests. Every returned model had `refinement_checked` status. The two primary literal gaps were 222.564175400651 and 206.757858066418 micrometers. `verify_freeze` accepted the archive.

Synthetic outcomes set to those calculated central values scored `consistent_at_frozen_inputs`. This checks native execution, archive integrity, numeric-string normalization, and the scorer together. It is not a physical observation or an accuracy result. The temporary fixture and its native receipts were removed after the check.

Reproduce the native replay with this command. It requires the configured native engine.

```sh
python3 - <<'PY'
from unittest.mock import patch
from coupons.tests.test_analysis import AnalysisChecks, analysis

fixture = AnalysisChecks()
fixture.setUp()
try:
    fixture.metadata.update(temperature_C='210', temperature_U_C='2')
    analysis.write_json(fixture.meta_path, fixture.metadata)
    with patch.object(analysis, 'utc_now', return_value=fixture.frozen_time):
        manifest = analysis.freeze(fixture.input_path, fixture.meta_path, fixture.output)
    analysis.verify_freeze(fixture.output)
    predictions = analysis.read_json(fixture.output / 'predictions.json')['caps']
    gaps = {cap['cap_id']: cap['models'][0]['predicted_pad_face_gap_um'] for cap in predictions}
    rows = fixture.outcomes()
    for row in rows:
        gap = gaps[row['cap_id']]
        row.update(mean_gap_um=gap, min_gap_um=gap-.5, max_gap_um=gap+.5,
                   measurement_evidence='SYNTHETIC CENTRAL OUTCOME. NOT PHYSICAL DATA.')
    report = fixture.score(rows)
    assert manifest['distinct_native_requests'] == 6
    assert all(model['native_status'] == 'refinement_checked' for cap in predictions for model in cap['models'])
    assert report['liquid_model_verdict'] == 'consistent_at_frozen_inputs'
    print('Six native requests checked. Synthetic score checked. No physical data supplied.')
finally:
    fixture.doCleanups()
PY
```

The source identities below were recorded in that replay.

| File | SHA-256 |
| --- | --- |
| `coupons/tools/analyze.py` | `86b24addcd85c8cb4e51bba32b390be283bfa6c648cbe8ccde3e7fae031c5a53` |
| `soldershape/model.py` | `68078a203ceb17be387300e2149a675a1f95d4010d252d9be97fc133b05dcedc` |
| `soldershape/solver.py` | `31e551899bbd040ad78aa2e2daf489a9fa3d2295df9db3f63e90149ff631c702` |
| Native engine binary | `c930b47b33a4cafb3cf98b1c0cb7e3bd9805abcf67aceefe243daea091072f8e` |

Model the Domain changed ownership to one bytes snapshot. Fix Root Causes removed the validation-to-copy race instead of adding a timing delay. Prove It Works required failing counterexamples before repair and checks against archived values afterward.
