# Board decision walkthrough

## Feature checklist

- [x] `how` over the affected subsystem.
- [x] `architect` for parallel design exploration.
- [x] Write the throughput checkpoint as four todo items.
- [x] Delegate code-writing to a subagent using the configured feature model.
- [x] Verify on the matching surface.
- [x] Rebase into small, ordered commits. Stack follow-ups. One coherent local feature commit is sufficient. No branch rewrite is needed in this clean checkout.
- [x] If the design is contested, `interrogate` before shipping. Skip because root and the cross-judge agree and no design dispute remains. Independent final review still ran.
- [x] Run Opening a PR. Skip public PR creation because this checkout has no remote and the request is local application work.

## Architecture checklist

- [x] Ground.
- [x] Sketch.
- [x] Agree. Proceed under the user's local-work authorization.
- [x] Implement.
- [x] Scrap. No redesign was needed. The inline shape fits the existing explorer and its result lifecycle.

## Design comparison

- [x] Frame.
- [x] Fan out.
- [x] Cross-judge.
- [x] Pick.
- [x] Graft.
- [x] Verify.

## Throughput checkpoint

- Blocking first steps. Inspect the actual board workflow and recorded inputs, then choose a design that cannot mix the ULX3S force example with the separate clearance coupon.
- Independent workstreams. Two isolated design sketches and a cross-judge precede one owner of application changes. Root owns browser verification and evidence.
- Shared mutable state. The existing board state remains the sole owner of selected inputs and results. Sketches have separate files. No concurrent application writers.
- Smallest safe decomposition. One implementation owner keeps the guided example, result explanation and stale-result handling coherent. Reuse existing computation, export and Lab routes.

## Acceptance checks

1. The first board view explains who the comparison helps and the concrete choice it tests.
2. One action opens a reproducible example on an actual source pad and identifies all assumed process inputs.
3. Visible results explain the practical tradeoff and distinguish numerical evidence from physical qualification.
4. An input or pad change cannot leave a guided conclusion attached to stale results.
5. A visitor can identify what changes the answer and reach the matching lab requirements without confusing the 400 micrometer board joint, 200 micrometer force fixture and 220 versus 270 micrometer height coupon.
6. Existing selection, native computation, editable cases and evidence exports continue to work.
7. Desktop and narrow-screen browser checks verify the actual running application and preserve screenshots. Focused existing checks pass.

## Design rubric

Score each candidate from zero to five for decision clarity, truthful evidence boundaries, coherent interaction, reuse of existing ownership, and verifiability. Prefer fewer concepts when scores tie. No numerical solver or frozen evidence changes are in scope.

## Completion

The executed workflow and measured sample are recorded in [RESULTS.md](RESULTS.md). [Final review](final-review.md) found no actionable issue in the declared scope. Thirty focused Python tests and fourteen existing shared mocked UI checks pass. Actual browser checks cover the new board workflow. The 330 micrometer archive replays with zero force differences. No new physical qualification, public deployment or fixture fabrication is claimed.

All work stays in the existing local checkout so its running service can serve the reviewed files. Isolated design artifacts use separate files. This request does not need a second repository checkout or public pull request.
