# Adversarial review B

Reviewed the extreme demo against base `ffe314f`. This reviewer uses the same parent model family. This is not evidence of model diversity. Source review and cheap isolated controls were performed. No native simulation or browser session was run by this reviewer.

## Findings

### 1. Warning. Reusing probes can misattribute old computation to changed Python sources.

**Location.** `tools/build_demo.py`, the `--from-probes` branch and `identities` construction.

**Finding.** The cache checks the native engine binary but the old probe files do not identify the Python model and solver source used to create them. The builder then records the currently imported Python source hashes alongside those old results. A changed Python wrapper with an unchanged native engine can receive credit for results it never computed.

**Reproduction.** In an isolated temporary copy, retained the actual two probe archives and appended a replacement `solve` definition to the copied solver source. That replacement unconditionally raises `RuntimeError`. Supplied its digest as the builder's fresh import-time solver identity and ran the cache branch. No native code ran. The builder and `read_demo` accepted the archive and returned the old 120 µm reference lateral force of `-92.263283646421 µN` under the changed solver digest `97003803ae52453e1f8bf084fac4af1cef499bbe7fba21f8a9aeb9870382244e`. The original source digest was `c7bcfcc2c5f24e6e783540b3fcabc45a8d15308ded887aca2ae41442ddf4c8a6`.

This reproduces misattribution by the cache path. It does not show that the actual current probe values are incorrect. Their numerical source files appear unchanged from the actual probe run.

**Suggested repair.** Remove cache reuse and record the seven cases freshly. Check loaded numerical source identities before and after the recording. Alternatively, preserve Python source identities when probes are first calculated and require an exact match before reuse. The first option removes a branch and fits this bounded demo.

Root accepted this finding and chose to remove `--from-probes`. Final regeneration and replay were still pending when this review was written.

### 2. Warning. The archive advertises a replay command that cannot pass its expected failure.

**Location.** `tools/build_demo.py`, inherited `manifest["replay"]` from `make_bundle`.

**Finding.** The archive advertises `python3 -m soldershape replay FILE.zip`. Generic replay intentionally reports failure whenever the current solve fails, including a reproduced failure. The compressed demo case is deliberately retained as a failed solve. Therefore that advertised command cannot yield a passing replay for the complete demonstration.

**Evidence.** `soldershape/__main__.py` catches `SolverError` inside `replay`, appends `passed=False`, and continues. The retained compressed case reports `failed`. The demo-specific verifier already handles this correctly as an explicitly expected reproduced failure while returning `all_cases_numerically_successful=False`.

**Suggested repair.** Set this archive's replay instruction to `python3 tools/verify_demo.py FILE.zip --replay`. State that reproducing the failed control verifies retention of negative evidence and does not make that case a numerical success.

## Executed checks

- `python3 -m unittest discover -s tests -p test_demo.py -v` passed all seven tests. These exercise the actual retained native recording, editable-case inputs, tamper controls, snapshot behavior, the read-only HTTP route, and matching download bytes.
- `python3 tools/verify_demo.py` passed without native execution. It inspected seven retained cases and reported the expected pair statuses of conditional comparison, conditional comparison, outside model scope, and numerical failure. Its reported archive digest was `8853757f6ab2b3aceb461e08616ead1ed8c60a9af96199f3eb328adef38db0f6`.
- Inspected the actual protocol, raw probe summaries, exported result diagnostics, archive source copies, and reader pairing. At 120 µm the retained positive axial candidate force is `7.619480890674879 µN`; its last refinement component change is `0.0003259244725963839 µN`. This is evidence of numerical consistency, not physical accuracy. At 200 µm the larger-volume surface exceeds both pad planes and its preference is blocked. The compressed case has no mesh or displayed force result.

## Decision trail and scope

The three appended extreme rows in `decisions.tsv` point to actual workflow and probe artifacts. The six first probe records support the stated direction contrast at 40, 80, and 120 µm. The boundary log supports the later scope warning and failed compressed solve. These rows do not claim physical qualification or demand evidence. No unsupported evidence claim was found in those appended rows.

The title asks whether more solder helps, but the adjacent fixture objective and qualifications bound the answer to a declared numerical screen. The source is an actual KiCad footprint used as geometric context. Neighbor joints are not represented as computed. Discrete samples do not imply interpolation or motion. These limits are present in both protocol data and the page.

No further correctness, security, or structural finding was reproduced in the reviewed scope. Final UI layout, the new fresh native recording, and its replay remain the root agent's verification responsibility.
