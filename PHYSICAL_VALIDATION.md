# Physical-data validation and a bounded design comparison

## Frame

The inherited version at `fc384a0` has numerical and browser qualification. Its open gate is agreement with physical solder-joint measurements. This work adds no unrelated features.

Done means a reproducible comparison with published physical data, an explicit pass/fail/inconclusive verdict under a frozen protocol, a useful pad/volume/placement comparison tied to a declared design objective, and repair of demonstrated modeling or reporting gaps. Numerical agreement with an upstream model cannot substitute for physical data. A negative or inconclusive physical result remains visible.

Scope is one fully specified primary experiment plus one independent source or control where accessible, one focused comparison, necessary model/validation repairs, and a fresh independent review. Physical tests use published measured geometry and loads, not simulated curves relabeled as measurements. No parameter is fitted to the evaluation points. Published fitted parameters are labeled as calibration-dependent and assessed separately from independently reported values.

## Playbook

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

## Designed units

- [x] Inspect complete primary paper pages and figures. Extract material, temperature, dimensions, volume, pad geometry, loads, sample size, uncertainty, and wetting regime. Preserve source URLs and hashes.
- [x] Map each measurement to the current model. Separate supported pinned-contact points from contact-line spreading or other incompatible conditions.
- [x] Freeze data, uncertainty treatment, parameter provenance, and acceptance criteria before computing predictions. Preserve exclusions and avoid fitted-to-test-data validation.
- [x] Run the unmodified baseline against the frozen comparison. Inspect mismatches and their physical or numerical causes.
- [x] Make the smallest demonstrated repairs. Keep the original negative result and rerun the frozen comparison.
- [x] Demonstrate one stated PCB design decision with a strong simple alternative, realistic parameter uncertainty, and limits on what the comparison establishes.
- [x] Independently review the scientific interpretation and implementation. Verify the running interface and exports for any product changes.

## Throughput checkpoint

First settle the physical-data mapping. Do not implement a general thermal or wetting solver, a new frontend mode, or an engine port to make the experiment fit. If the published data cannot identify a prediction within its uncertainty, report that limitation rather than manufacture a successful validation.

## Final gate

The physical accuracy gate did not pass. The frozen report retains 133 computation calls, all failed cases, both duplicate pairings, raw force residuals and incomplete sensitivities. Its broad verdict is inconclusive because specimen/process inputs and supported substrate interactions remain unidentified. A large held-out central miss and two incompatible central normal-force directions are explicit negative results. The normal-direction diagnostic was added after independent review and is labeled as such; the frozen protocol and fit were not changed.

The numerical repair changes three command-list lines to use energy-decreasing Newton line searches with additional gradient relaxation. Independent equilibrium-energy derivatives, prior analytic checks and the native reference pass. Stable meshes that extend beyond the pad planes now produce a product scope warning. Unsupported geometries remain failures or inconclusive comparisons.

The user subsequently authorized completion of the local product workflow. That work is separately framed in `PRODUCT_RELEASE.md`. It adds editable input files and a controlled design comparison, without changing physics to force agreement with the paper. The simple cylinder alternative exposes boundary-condition sensitivity; it is not a qualified same-boundary competitor. Native Surface Evolver remains the numerical baseline, with identical underlying computation. The product benefit is a direct KiCad, comparison and reproducible-export workflow.

See `evidence/physical/validation-report.md`, `evidence/physical/independent-review.md`, `evidence/design-comparison/report.md`, and `evidence/product-browser.json`. `python3 tools/check_digitization.py` recalculates every recorded manual pixel reading without research dependencies. Its optional `--pdf PATH` verifies primary-source identity; it does not claim an independent redigitization.
