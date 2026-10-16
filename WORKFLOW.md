# Project selection and first usable version

## Assumptions and finish condition

The intended users are PCB/package designers evaluating molten solder joint geometry, or makers designing knot-based physical objects. The objective is a useful local engineering or design tool with a defensible computational advantage. Market demand and physical manufacturing validation remain unproven unless direct evidence establishes them.

Done means either a documented rejection of both proposals, or a reasoned selection plus a runnable application, one complete import-to-computation-to-export workflow, reproducible numerical checks against upstream or analytic references, setup instructions, and explicit limitations. A build alone does not pass.

Scope is two bounded feasibility investigations, one architecture decision, one application, and one end-to-end acceptance pass. Check the upstream algorithms and existing products before porting. Use numerical reference and constraint checks for scientific claims and direct UI/CLI operation for usability claims. No public deployment or paid services are needed.

## Playbook

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

## Designed units

- [x] Inspect current alternatives, upstream implementation, licensing and reference cases for each proposal. Keep investigations in separate directories.
- [x] Reproduce a solder reference and evaluate knot feasibility with saved evidence. Preserve failed checks.
- [x] Select a project using practical value and demonstrated feasibility. State the strongest counterargument and reversal condition.
- [x] Compare a thin upstream integration with a focused new implementation. Record the smallest justified data model and interface.
- [x] Define concrete acceptance checks and capture the numerical baseline before product implementation.
- [x] Implement one complete user workflow, then run it and inspect its exported files.
- [x] Independently review the result, repair material findings, and finish setup and limitation documentation.

## Throughput checkpoint

Investigate the two upstream systems independently. Product implementation begins only after selection and acceptance criteria. The initial scope excludes a full Rust/WASM rewrite, thermal reflow chemistry, frictional rope dynamics, global-optimum claims, and physical certification. Expand only when a demonstrated user workflow needs it.

## Final qualification

The public numerical verification passed 11 generated numerical cases, the published BGA reference, representative mesh crossing checks, and artifact replay. All 12 boundary and local HTTP tests pass. Browser QA imported the real footprint through a file chooser, changed pad and parameters, computed a joint, discarded an obsolete response after an in-flight edit, computed a five-point sweep, selected a mesh, downloaded its ZIP, and inspected its actual contents. Evidence is in `evidence/acceptance.json`, `evidence/browser-workflow.json`, and `evidence/review.md`.

Independent review found one replay failure-handling defect. It is fixed and has a focused regression check. No material review findings remain open. Review used the configured inherited model, so no different-model-family review is claimed. A complete physical-validation or customer-demand check remains outside this release's qualification.

Opening a pull request is skipped because this new local repository has no remote and publication was not requested.
