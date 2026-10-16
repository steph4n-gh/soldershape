# Acceptance checks before implementation

These checks define the first useful release. They do not establish market demand, manufacturing reliability, or agreement with measured solder joints.

## Selection checks

- Reproduce an official BGA force example using a pinned upstream Surface Evolver build. Compare its printed force and refinement trend with the author's published values. Inspect model assumptions and code license.
- Inspect Ridgerunner's actual source, licensing, dependencies, numerical constraints, and reference cases. Attempt a bounded local baseline. Distinguish build accessibility from algorithm quality.
- Compare each proposed workflow with current primary documentation for the strongest practical alternatives. Record a counterargument and reversal condition.

## SolderShape checks if selected

1. Import a real KiCad circular BGA footprint and preserve pad identifiers, positions, dimensions, and units. Reject malformed or unsupported selected pads explicitly. Model the selected circular copper pad as a fully wetted boundary and disclose that assumption.
2. Compute a three-dimensional constant-volume equilibrium using the pinned native engine, with configurable upper pad diameter, standoff, solder volume, lateral offset, surface tension, and density. Display the actual solver mesh and both lateral and vertical force on the upper pad.
3. Match the published BGA force example within 0.1 percent under its specified discretization. For an analytic no-gravity cylindrical bridge, obtain volume error below 0.1 percent and vertical force within 2 percent of minus pi times radius times surface tension. The offset-zero lateral force must be negligible relative to capillary force scale.
4. Refine a representative solder configuration. Record relative force change, volume residual, and solver termination. Do not present unconverged results as converged. Opposite offsets must produce opposite lateral restoring forces within 3 percent of their magnitude. Increasing the surface tension must scale no-gravity forces accordingly within 2 percent.
5. Run a bounded parameter sweep that produces independently computed rows. Export CSV, a valid closed triangle mesh, and a reproducible bundle containing the precise model, input parameters, raw solver output, engine provenance, and results. Exported geometry must match the displayed result and use millimeters.
6. Drive the running application through import, selection, changed parameters, solve, sweep, and export. Open the exported artifacts and verify their contents. A changed input must invalidate the displayed result until recomputed.
7. A fresh local setup must build or locate the pinned engine without depending on research directories. Runtime needs no account, API key, CDN, or internet connection. Bind the local service to loopback and accept only the declared JSON operation schema.

## KnotForge checks if selected

Use at least an unknot, a trefoil, and one harder reference knot. Compare ropelength and active constraints with upstream output, preserve thickness and curvature constraints through tightening, and separately validate a closed oriented export mesh for degeneracy and self-intersection. Physical printability and global minimality remain unverified without their own evidence.
