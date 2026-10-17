# Portable verification of the force experiment

The first extracted outside-lab package failed `verify-plan` without the local engine cache. The preserved negative check is `expansion/extracted-check-1.log`. The cause was a static verifier comparing the archived producer identity with `engine_info()` on the receiving host. That also bound verification to absolute build-command paths and a particular compiled binary.

Static verification and frozen scoring now use the recorded engine identity. They do not call `engine_info()` or `solve()`. Every completed raw receipt must contain exactly the engine identity archived in its plan or registered freeze. A contradictory identity rejects the record. Failed attempts lacking an engine identity remain negative evidence. Matching current analyzer, model and solver source, exact receipt bytes, complete member sets, registered freeze digest, and current protocol/allocation guards remain required. `verify-plan` explicitly reports `native_replay_performed: false`.

Fresh `plan` and `freeze` still perform native computation and record the actual producer. This repair adds no engine redistribution, generic execution mode, numerical-model change or physical observation. Source hashes and archived provenance establish local integrity, not independent authentication or an external timestamp.

Six behavior controls cover absent-engine plan verification, absent-engine registered verification/scoring, contradictory archived producer identities, retained failed no-engine attempts, completed receipts missing identity, and unchanged rejection of stale source/protocol identities. The absent-engine controls assert that neither engine lookup nor native execution occurs. All 30 force-analysis controls passed in 1.387 seconds. Their synthetic observations are test data only; physical templates remain blank.

The previous 20-request plan is preserved intact at `output/force-plan-pre-portability`. Twenty fresh native requests generated the replacement at `force_lab/planning/native-120`. A separate copied-root check at `output/force-portability-no-engine` confirmed `engine_info().ready == false` and verified all 20 recorded requests without an engine cache. Its receipt is `output/force-portability-no-engine-verification.txt`. Static verification is `output/force-plan-portable-verification.json`; test output is `output/force-portability-tests.txt`.

Final identities:

- Analyzer SHA-256 `2613c2d36a4732555b6f423371066a5e80549ad81e0d8f89e200f899ec6acd02`.
- Protocol SHA-256 `3320633962e270b1258c30a8f7ab013bc53f81359080507b54092f8eaefb6276`.
- Native plan SHA-256 `928978bb11345a7167bd5a1944f89d80edbf7d819cbc147b8b27e016f25c4a1b`.

Run from the extracted package root:

```sh
python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120
python3 -m unittest force_lab.tests.test_analysis -v
```

For an independently registered physical freeze, the existing `verify` and `score` commands are also static and portable. Fresh native reproduction requires `python3 tools/setup_engine.py` followed by `plan` or `freeze` into a new directory. No physical freeze exists yet because commissioning and independently measured physical inputs remain outstanding.
