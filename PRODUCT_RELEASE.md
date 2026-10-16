# Local engineering workbench completion

The user authorized a complete product after the physical validation work began. This release finishes the supported circular-pad equilibrium workflow. It does not expand the physics to dynamic reflow or moving contact lines.

## Playbook

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

## Architecture steps

- [x] Ground
- [x] Sketch
- [x] Agree
- [x] Implement
- [x] Scrap. Skipped because the chosen shape remained sufficient during implementation.

## Acceptance before implementation

1. Previously failing thin reference joints pass the existing numerical gates after a general relaxation repair. Preserve the original failed runs. Verify independent force derivatives and the existing analytic and upstream references.
2. Finish the frozen physical-data protocol. Report all observations, ambiguous pairings, exclusions, parameter calibration, uncertainty, and failures. Do not turn calibration-dependent agreement into general physical validation.
3. Demonstrate a declared PCB comparison with a simple analytic baseline, volume sensitivity, reproducible inputs and usable exported geometry. Keep rejected choices visible.
4. Save and reopen a bounded, editable input-only case file containing its footprint, selected pad, parameters and optional comparison baseline. Opening a file cannot execute code or present archived numbers as a fresh solve. Invalid input leaves the current draft intact.
5. Compare two upper-pad/volume designs at the same selected board pad, gap, offset and material settings. Compute both through the public solver. Show changed inputs, both forces, numerical status and model limits. Export both cases with independent meshes and exact inputs.
6. State what the gap and volume refer to. Separate numerical checks from physical accuracy in the running interface and exported record.
7. Drive the actual browser through save, edit, open, compare, select geometry and export. Inspect the downloaded files. Recheck stale-response handling and failure messages. Run proportionate CLI, HTTP and numerical verification.
8. Review the scientific conclusions and product changes independently. Repair material findings, document launch and verification commands, and leave the running local workbench usable.

## Throughput checkpoint

The solver repair, physical campaign and product design are separate writable slices. Expensive physical sensitivities wait for a frozen repaired solver. Compare two input-only case shapes before implementation. Reuse the current importer, public solver and evidence ZIP. No account system, persistent job service, engine port or new solver framework is needed.

## Delivered scope and evidence

The local exploratory workflow is complete. It imports circular KiCad pads, solves and sweeps, saves and reopens editable inputs, compares two upper-pad/volume designs under shared conditions, selects each solved mesh, and exports exact evidence and geometry. `Start SolderShape.command` provides a macOS launch path. It checks the Python version, sets up a missing engine, and reopens a verified existing workbench without replacing another service.

The numerical repair regression passes for the two previously failing reference bridges. Other unstable paper cases remain explicitly unsupported; no acceptance threshold was weakened. All 24 tests pass. Existing upstream, analytic, mesh and replay qualification passes. The actual browser archive replay reproduces both forces exactly on the recorded engine. Boundary review reproduced and repaired saved-file size and relaunch defects. A narrow-window check exposed page overflow from an absolutely positioned table header. The header is now visible, scroll containment is explicit, and measured page width equals the 375 CSS-pixel content viewport. Design labels stay visible during horizontal table scrolling.

The physical accuracy gate did not pass. Missing inputs, central force discrepancies, wrong normal-force directions, substrate-plane excursions and incomplete sensitivities remain documented. The interface and exported manifest distinguish numerical checks from material/process accuracy. No manufacturing readiness claim is made. Broad physical qualification requires identified specimen/process data and a supported substrate-contact model.

The physical and product reviews are in `evidence/physical/independent-review.md` and `evidence/product-review.md`. Browser proof, actual archive hashes and force values are in `evidence/product-browser.json`. The final views are `evidence/product-workbench.jpg`, `evidence/product-scope-warning.jpg`, and `evidence/product-narrow.jpg`. Reproduction commands and final runtime source hashes are in `evidence/product-verification.json`.

Model the Domain kept saved inputs separate from immutable computation evidence. Laziness Protocol reused the importer, native solver and ZIP path without adding runtime dependencies. Prove It Works required real file chooser operations, native force checks, downloaded archive inspection and replay. Explain the Number kept the physical residuals, missing inputs and failed uncertainty samples beside every claim.
