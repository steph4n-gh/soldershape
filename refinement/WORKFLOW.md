# Accuracy and product refinement

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

Done means a fresh audit of the current product and evidence, a primary-source comparison with current alternatives, an explicit target user and decision, implemented repairs to consequential accuracy and workflow gaps, and one demonstrated end-to-end user workflow whose decision survives negative controls. Any defensibility claim must identify what exists today, what a competitor could copy, and what still requires customer or physical evidence. A supported conclusion that no moat exists yet is acceptable.

Scope is the local SolderShape application, its documented numerical and physical claims, and its coupon-to-evidence workflow. Preserve previous negative results and the released R1 coupon package. No fabrication, supplier messages, purchases, deployments, or invented customer evidence. Use the existing engine and standard-library service. New abstractions or dependencies require a demonstrated need.

## Frame and acceptance before edits

1. Inspect actual source, existing results, browser workflow and strongest analytical baseline. Reproduce consequential defects before repairs.
2. Verify current alternatives and identify who faces a recurring decision SolderShape can improve. Distinguish observed evidence from inferred demand.
3. Compare two structurally distinct designs for the smallest useful refinement. Select using accuracy, decision usefulness, ease of review and maintenance cost.
4. Implement a complete workflow for the selected decision with explicit inputs, assumptions, blocked states and reproducible exports. Define its concrete acceptance checks before code.
5. Test the real API and browser, preserve deliberate failure cases, and independently challenge the decision and positioning. Run relevant existing checks after changes.
6. Record measured before-and-after behavior, remaining physical and commercial uncertainty, exact commands, and a local commit.

## Throughput checkpoint

Root owns specification, product integration and final claims. Three read-only slices inspect architecture, scientific correctness and market alternatives. Separate output paths prevent shared writes. Later implementation delegates receive disjoint source files only after a selected design. One focused verification tool must replay the useful workflow. Avoid broad cosmetic churn, a solver rewrite, generic material libraries, accounts, billing and new deployment infrastructure.

## Coverage

| Slice | Output | Gate |
| --- | --- | --- |
| Architecture and present workflow | architecture.md | Real file/function ownership and user blockers. |
| Accuracy and evidence | accuracy-audit.md | Reproduced consequential gaps and bounded claims. |
| Alternatives and user value | alternatives.md | Current primary sources, strongest substitute and falsifier. |
| Design selection | design.md | Two whole approaches, explicit data shape and acceptance contract. |
| Final independent review | final-review.md | Actual workflow and negative controls, no unsupported moat claim. |

## Completed evidence

The acceptance checks in design.md pass. The final application suite passed 52 tests, including actual native equilibrium checks. The coupon suite passed 34 checks. Real browser import, edit, asynchronous invalidation, save/reopen, native computation and ZIP download are recorded in browser-workflow.json. A fresh four-case native replay and archive tamper control passed through tools/verify_study.py, with receipts in study-replay.json. An extracted refined lab archive passed its integrity, geometry and all 34 coupon checks. Original R1 geometry and historical physical failures remain unchanged.

The independent final review found no remaining software blocker within its inspected scope. Reviewers inherited the parent model, so their agreement is not evidence across model families. REVIEW.md gives results and exact replay commands. POSITIONING.md records the proposed practitioner gate. No physical measurement, customer interview or proven moat was produced.
