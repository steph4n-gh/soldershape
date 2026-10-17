# Review A

Reviewed the extreme demo against base `ffe314f`. This is an independent pass in the same parent model family. No native simulation or browser run was performed by this reviewer.

## Findings

### 1. [warning] Cached native results can be stamped with Python source that did not compute them

**Location**. `tools/build_demo.py:36-44` and `59-85`.

**Finding**. `--from-probes` checks the native binary and normalized request, then binds the retained results to the currently loaded `model.py` and `solver.py`. The two probe ZIP files do not retain those Python identities. A later source edit therefore changes the claimed calculation provenance without recomputing or proving the cached source identity.

**Evidence**. A cheap isolated counterexample copied both actual probe ZIPs to a temporary package, appended a comment to both Python source copies, and supplied their new hashes as the loaded identities. `build_demo.main()` accepted `--from-probes`, produced an accepted seven-case archive, and recorded those new hashes as `calculation_code_sha256`. The original native computations necessarily preceded those edited files. The current real recording copies do match the current repository files, so this does not establish wrong current numerical values. It establishes that the reproducible builder can make an unsupported provenance claim.

**Suggestion**. Remove the one-time cached builder path after obtaining the final fresh recording, or capture and verify source identity when each probe is computed. Label a packaging snapshot separately if that is the intended meaning.

### 2. [warning] A different failure cause is accepted as reproduction of the compressed control

**Location**. `tools/verify_demo.py:49-56`.

**Finding**. The verifier discards `SolverError.evidence` and accepts any failure with the same generic human-readable error. That error groups native numerical and command warnings. It does not identify the retained failure cause.

**Evidence**. The actual compressed receipt records completed exit zero, repeated Hessian warning 1825, and seven negative eigenvalues at the final level. A cheap counterexample returned the unchanged six successful records and raised the same generic error for the compressed request with fabricated `WARNING 9999: An unrelated command warning` evidence. The verifier completed successfully and reported `expected_failure_reproduced=true` and `verified=true` for that different failure. This is not a false claim of numerical success, because the report explicitly sets `all_cases_numerically_successful=false`. It is a false claim of reproducing the retained negative control.

**Suggestion**. Preserve the new failure receipt and compare a narrow normalized failure signature, including termination, return code and stable warning identity. Report only matching failure status when the cause is not established.

### 3. [warning] The evidence ZIP gives a replay command that rejects its deliberate failed case

**Location**. `tools/build_demo.py:63-74` retains the generic `manifest.replay` from `make_bundle`.

**Finding**. The archive instructs the reader to run `python3 -m soldershape replay FILE.zip`. The existing generic replay unconditionally marks a retained solver failure as failed replay, even when that same expected failure is reproduced. The seven-case demo therefore cannot pass the command embedded in its own evidence package.

**Evidence**. `soldershape.__main__.replay` catches a `SolverError` and appends `passed=false` before considering the prior failed status. This path applies to the deliberately failed seventh request. The new dedicated verifier handles retained failures separately, but the ZIP does not point to it.

**Suggestion**. Set the demo manifest replay instruction to the dedicated verifier and make its expected-failure semantics explicit. Do not weaken the generic replay to call every failure successful.

## Verification and remaining evidence

All seven current `test_demo.py` tests passed in this review. The actual archive has 71 members and seven normalized cases. Each successful result has raw native receipts and actual mesh geometry. The 200 micrometer scope warning and compressed numerical failure both block favorable screens. The paired editable cases retain shared geometry and the selected two volumes. The gap control correctly has no volume-comparison baseline. No invented board-wide or physically qualified behavior was found in the inspected UI and protocol.

The appended `extreme-probe` and `extreme-boundary` decision rows agree with the actual probe logs. They are bounded computational evidence, not physical validation. Their timestamps are shared framing timestamps, so final native and browser verification should receive their own completed rows. At review time `demo/native-replay.json` still described an older archive and `replayed=false`. The root reported the fresh replay in progress. This is pending evidence, not a failure finding until the final receipts are written.
