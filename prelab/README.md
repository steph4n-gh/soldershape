# Verify the coupon assumptions before a lab test

Read [the findings](REPORT.md), [the lab measurement addendum](LAB_ADDENDUM.md), and [the declared scenario protocol](protocol.json). The running workbench links the same findings from Physical test.

C220 has more nominal gap under either shared boundary hypothesis. Its ranking and the 185 micrometer clearance conclusion are conditional. Opposite arm variations can erase or reverse the advantage. No new physical observations were made.

## Run the checks

Use the repository root, Python 3.12 or newer and the pinned engine for fresh native calculations. The finite-pad adapter verifies unchanged production source against Git baseline `33666d3`, so its recomputation requires this checkout's history. Offline evidence verification does not execute the native engine or archived code.

```sh
python3 prelab/verify.py
python3 -m unittest prelab.test_campaign prelab.test_replay prelab.test_rigid_cap prelab.test_finite -v
python3 -m prelab.make_report
```

For fresh calculations, choose new output directories.

```sh
python3 tools/setup_engine.py
python3 prelab/campaign.py run output/prelab-campaign-new --workers 2
python3 prelab/campaign.py verify output/prelab-campaign-new
python3 prelab/replay.py output/prelab-campaign-new output/prelab-replay-new
python3 prelab/rigid_cap.py --verify
python3 -m prelab.run_finite output/prelab-finite-new
```

`rigid_cap.py --verify` recomputes the recorded analytical examples without native computation. Its command without `--verify` rebuilds that report. The native campaign records 64 scenario-arm-mapping rows, deduplicated into 60 ordinary requests and one deliberately excessive-load control. Each loaded request can launch more than one native process. These counts are logical requests, not process-launch counts.

The report generator reads the committed evidence paths. It does not silently replace them with results from a new output directory. Verification binds the scenario protocol, interpretation code, numerical source and engine identity. Changed source requires a new campaign. Exact stored floating-point comparisons have been exercised on this macOS Python 3.14 environment. Other platforms and Python versions remain unqualified.

## Keep the physical questions separate

`campaign.py` owns paired scenarios, request conversion, native receipts and regenerated conclusions. The record separates common changes from opposite arm deviations. Its sampled differences are not continuous bounds or measured probability distributions.

`finite.py` owns the isolated finite-copper experiment. `run_finite.py` repeats its settled fixed-gap and energy controls. Fixed prescribed wetting, disabled envelope gravity and no new copper contact are essential assumptions. C270 moving-height optimization remains failed. The penetrating control remains intrusive and not converged. The adapter is a research experiment, not a replacement public solver.

`rigid_cap.py` owns the reduced-order height and two-tilt calculation for twenty interacting vertical springs. Its ideal joint-site minima are not a measured whole-cap minimum. The sphere-gradient and tensile-reaction cases remain explicit stress constructions.

`verify.py` checks the raw evidence and recomputes conclusions. It never executes archived Python or Evolver commands. Hashes provide local integrity, not authentication, a trusted timestamp or physical accuracy. `package_evidence.py` archives generated directories with file hashes and the project notice.

## Preserved evidence

The six fresh baseline requests, final 61-request campaign, final 13-request replay and twelve analytical cap cases remain under `evidence`. `finite-pilot.tar.gz` preserves all 28 original isolated attempts, including failed adapter versions and exact source snapshots. `finite-confirmation.tar.gz` preserves a fresh run of the settled controls. Both include the project MIT notice. Their file manifests retain every original raw byte.

The initial and intermediate replay directories predate the strict metadata repair. They remain historical records. `replay-final` is authoritative for this phase. The first full campaign is also retained locally at `output/prelab-campaign-before-strict-engine`; all 60 accepted numeric results agree exactly with the recomputed campaign after the validation-only repair. The public numerical equations, board files, coupon protocol and historical archives are unchanged.

[WORKFLOW.md](WORKFLOW.md) defines the acceptance checks and stopping decision. [decisions.tsv](decisions.tsv) records decisions. [REVIEW.md](REVIEW.md) consolidates independent review and its limits. The [final acceptance review](final-review.md) records the executed checks.
