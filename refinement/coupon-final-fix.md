# Exact-byte coupon provenance repairs

The final refinement review found two remaining provenance failures in the coupon tools. A focused inspection also found a second read of verified prediction files. These repairs concern software evidence. They add no physical measurements or solver accuracy evidence.

## Reproduced failures

Three new regression tests ran before the repair. They failed with six reported failures because one test checks four archive files separately.

| Counterexample | Before repair | After repair |
| --- | --- | --- |
| Replace the outcome CSV after parsing. The first cap changes from 200 to 300 micrometers. | The report retains the observed 200 micrometers but records the replacement file's digest. | The report retains 200 micrometers and hashes the exact bytes parsed. The replacement file has a different digest. |
| Change an archived input or metadata file after prediction. | Freeze writes a completed manifest whose hashes accept the changed archive. Predictions still use the original inputs. | Freeze rejects completion. No manifest exists. Partial native receipts remain. |
| Change both the archived and live experiment or allocation files after prediction. | The old equality check accepts both changed copies. | Freeze compares the archived bytes with the original snapshot and rejects completion. |
| Change `predictions.json` immediately after the verifier reads its original bytes. | Score rereads the changed predictions and reports disagreement. | Score uses the verified bytes and retains the original synthetic agreement. |

The native solver is a test double in these regressions. Its receipts identify the fixture as synthetic. No native runs were started for this repair.

## Data ownership

The scorer now has two immutable inputs. One is the verified freeze snapshot, a map from archive filenames to `bytes`. The other is the outcome CSV captured as `bytes` once. JSON and CSV parsers consume those values. The report hashes those same values.

`frozen_snapshot` verifies each archived file's digest when it reads that file. It returns the verified bytes and the exact manifest bytes. Score uses this snapshot for experiment, metadata, input, allocation, and prediction data. It no longer rereads verified files or takes scoring assignments from the live allocation.

`verify_freeze` retains its existing manifest return value for callers. Its verification uses the same snapshot reader.

Freeze records each original snapshot digest in the manifest it prepares. Immediately before writing a completed manifest, it compares all four archived snapshots with their original bytes. An archive change prevents completion and preserves receipts.

The outcome report also records the source path and the digest's scope. The digest identifies the bytes parsed for that report. It does not prove that the local source file never changed, establish who recorded a measurement, or replace an external preregistration timestamp.

An alternative was to verify paths and reopen them for each parse. That retained the read race. Capturing bytes once keeps parsing and hashing bound to one value without file locks or a transaction framework.

## Verification

Run the three focused regressions.

```sh
python3 -m unittest \
  coupons.tests.test_analysis.AnalysisChecks.test_score_hashes_the_exact_outcome_bytes_it_parses \
  coupons.tests.test_analysis.AnalysisChecks.test_archived_snapshot_changes_during_native_work_prevent_completed_freeze \
  coupons.tests.test_analysis.AnalysisChecks.test_score_uses_the_verified_prediction_bytes_when_archive_changes_after_read -v
```

Measured result after repair is three passing tests. The archive mutation test covers inputs, metadata, experiment, and allocation separately.

Run all coupon checks.

```sh
python3 -m unittest discover -s coupons/tests -v
git diff --check
```

Measured result is 34 passing tests and no whitespace errors. Thirty tests cover analysis behavior. Four tests inspect the actual fabrication exports and reject changed geometry.

Model the Domain made the authoritative scorer inputs immutable byte values. Fix Root Causes removed the repeated reads that disconnected content from digests. Prove It Works required failing counterexamples before repair and exact report-value checks afterward.
