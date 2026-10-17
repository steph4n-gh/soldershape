# Project notice packaging review

Reviewed 2026-10-16 against base `e89f071`, limited to the uncommitted changes in `soldershape/artifacts.py`, `tests/test_export_notices.py`, `tests/test_review.py` and `THIRD_PARTY.md`.

No actionable findings. `make_bundle` includes the exact root MIT notice in every new archive and hashes it in the existing file manifest. Its scope explicitly preserves user-input and third-party terms. `bundle_study` retains the inherited notice and scope while rebuilding its manifest, including for source-free calls that archive first-party calculation code. The new manifest field remains optional to the unchanged reader, preserving old-archive compatibility.

Verification on Python 3.14.4:

```sh
python3 -m unittest -v tests.test_export_notices tests.test_review.ReviewArchives.test_seven_fully_evidenced_loaded_rows_fit_existing_member_limit tests.test_review.ReviewArchives.test_old_archives_and_source_free_study_exports_remain_unchanged
```

All 8 tests passed in 9.496 seconds. They cover exact project notice bytes and scope, retained KiCad/board notices, arbitrary user sources, source-free Study output, manifest integrity, seven fully evidenced loaded rows at exactly 100 ZIP members, and historical archive compatibility. The reader still rejects more than 100 members. `git diff --check` passed, and `git diff --exit-code HEAD -- '*.zip'` confirmed that tracked historical ZIPs were unchanged. The diff changes no mathematical calculation code.

This focused review did not rerun the full suite, native solve/replay, browser checks or candidate build. It assesses the notice packaging behavior and the stated capacity/compatibility boundary; historical notice gaps remain documented in `launch/provenance-audit.md`.
