# Repair verification for the extreme demo

This is a fresh independent review of the repairs accepted from `review-a.md` and `review-b.md`. The reviewer inherited the parent model family. This is not cross-model agreement. The application was read-only. This review ran no native solver or browser simulation.

## Verdict

All three accepted findings are closed. No remaining blocker was reproduced in this review scope.

The canonical archive is `demo/data/stress-cases.zip`. Its SHA-256 is `914ef334f8850be64a1c5b325647c1d9bc6adf6acfdcac6a3d04920bd4f27f24`. It contains 71 members and seven normalized cases. Every listed member digest passes. The archived and local protocols match the recording identity. Both archived numerical sources match their declared digests and the current local sources.

## Cache provenance repair

`tools/build_demo.py` no longer has a cached-probe branch. Passing the removed `--from-probes` argument exits with code 2.

An isolated temporary-root control changed `model.py` before recording. The builder rejected the mismatch against its import-time digest before calling the mocked solver. No archive was written.

A second isolated control changed `solver.py` during the first mocked solve. All seven requests used retained result fixtures. The builder rejected the source drift after recording and before archive output. No native process ran and no archive was written. This verifies that ordinary disk-source drift cannot silently receive attribution for the retained numerical results through this builder.

The final recording reports fresh seven-case native computation. The independent checks establish consistency of its source identities and receipts. They do not attest adversarial execution integrity or physically validate those computations.

## Negative-control signature repair

`tools/verify_demo.py` preserves current failure evidence. It compares warning identity and wording, termination, and return code. It normalizes Hessian index counts only. The retained case records warning 1825 about a non-positive-definite Hessian, completed termination, and return code zero.

Cheap full-verifier controls supplied the unchanged six successful records and changed only the seventh failure receipt. The verifier rejected each of the following changes.

- An unrelated warning 9999.
- A timeout termination.
- A return code of 2.
- Different non-count wording under warning 1825.

The same Hessian warning with a changed negative-mode count remains an accepted reproduced failure. The accepted output still sets `all_cases_numerically_successful` to false. Reproducing the failed control does not relabel that control as a numerical success.

## Replay instruction repair

The actual manifest points to `python3 tools/verify_demo.py FILE.zip --replay`. Its adjacent text explicitly says the archive does not contain seven numerical successes. The dedicated verifier accepts a matching retained failure and rejects changed failure causes. The generic replay behavior remains unchanged.

`demo/native-replay.json` was complete when this review checked it. It names the canonical archive digest, sets `replayed` to true, contains seven verified checks, and retains physical qualification as unqualified. The first six cases have zero recorded force differences and matching exact engine identities. The seventh has matching normalized failure signatures and `expected_failure_reproduced` true. This review inspected that root-produced receipt. It did not independently repeat its native computations.

## Focused tests and scope claims

`python3 -m unittest discover -s tests -p test_demo.py -v` passed all eight tests. These cover the actual recording, source and request tampering, verified-byte snapshots, editable case roles, the read-only HTTP route, exact download identity, and unrelated warning rejection. The HTTP test emitted a cleanup ResourceWarning for its expected forbidden request. The test passed.

The protocol and inspected page code identify one isolated joint, an externally held gap, and recorded static equilibria. They do not claim coupled board behavior, package motion, capture range, bridge prediction, yield, or manufacturing qualification. The compression control changes gap at fixed volume and does not masquerade as another volume comparison. Scope and failed samples cannot obtain favorable force screens. The footprint is context for the selected joint.

The appended extreme framing, probe, and boundary trail rows point to retained evidence and make bounded numerical claims. They do not manufacture demand, a moat, or a physical pass. Final browser evidence and completed handoff rows remain the root agent's responsibility.

Prove It Works shaped this review. The checks inspect the actual canonical ZIP and exercise the repaired verifier with independent counterexamples, rather than relying only on passing unit tests or implementation descriptions.
