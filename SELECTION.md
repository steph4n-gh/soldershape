# Build SolderShape first

SolderShape merits a focused first version. This is a decision to invest in a useful prototype, not evidence of product-market fit. KnotForge remains a credible second candidate.

## Evidence behind the choice

| Criterion | SolderShape | KnotForge |
| --- | --- | --- |
| Practitioner decision | Compare how solder volume, pad sizes, gap, and placement offset change an individual molten joint's shape and force. | Produce a compact thick-tube knot with explicit contact and curvature diagnostics. |
| Strongest alternative | Surface Evolver already computes these quantities. Interface Equilibrator already has a capillary CAD interface. | KnotPlot already provides knot editing, a library, and OBJ/DXF export. Ridgerunner already supplies constrained tightening. |
| Defensible first advantage | Import a KiCad pad, run a deliberately restricted model, compare parameter sweeps, and export one reproducible case without learning Evolver scripting. | Make constrained optimization diagnostics accessible to a designer who specifically needs them. The obvious maker export workflow is already covered. |
| Local evidence | A headless upstream build runs. The BGA-4 force reproduces the published same-discretization value with relative difference about 2.66e-10. Refinement changes the force materially, so convergence must be visible. | Source inspection establishes a substantial constrained optimizer and dependency stack. Native bootstrap/configure failures are environment limitations, not a negative result about the algorithm. A bounded isolated baseline is recorded separately. |
| Unresolved value | The intended user may need thermal reflow, changing wetting boundaries, or failure/reliability predictions instead of equilibrium geometry. | The intended maker may prefer direct sculpting over a ropelength objective, and tight contacts complicate printable tube export. |

The difference is the connection between the computation and a design decision. A PCB designer already has a footprint and choices about pad geometry, solder volume, standoff, and offset. The first version can connect those inputs to an inspectable numerical result. This is a plausible workflow advantage inferred from the tools and models, not an observed customer result.

## Strongest counterargument

SolderShape might make an incomplete physical model easier to use. Copper pad dimensions alone do not determine the wetted boundary. Contact angles, solder mask, alloy, flux, oxide, temperature history, and component motion affect real reflow. A convenient equilibrium calculation can create false confidence if it suggests otherwise. The application must describe fully wetted, pinned circular boundaries and distinguish an upper-pad force at prescribed geometry from a prediction of assembly alignment.

## What would reverse the choice

Prefer KnotForge if a designer demonstrates a compact physical design that its contact/curvature controls enable more effectively than KnotPlot, with a separately verified export. Stop expanding SolderShape if PCB practitioners cannot identify a useful decision under its explicit equilibrium assumptions, or if it cannot reproduce reference forces and demonstrate stable trends under refinement. No full port is justified before those checks.

## Port decision

Reuse the pinned native Surface Evolver engine for the first version. Its reference behavior is already reproduced. A Rust rewrite creates a new numerical implementation to qualify without adding a demonstrated user capability. A browser-only C/WASM port also requires isolating a global parser, filesystem commands, and process/runtime assumptions. Revisit portability only after the working local workflow establishes a need.

Keep the original upstream archive and its source provenance in the local dependency cache. Do not commit or redistribute its binary/source as if every component has one public-domain license. The author's paper describes Surface Evolver as public domain, but the archive has separately credited components. The first version's setup downloads and builds it locally, and third-party notices record the remaining redistribution review.

## Sources inspected on 2026-10-16

- [Surface Evolver BGA model sequence](https://kenbrakke.com/evolver/bga/bga.htm).
- [Published BGA-4 force methods and refinement values](https://kenbrakke.com/evolver/bga/bga-4.htm).
- [BGA-7 lateral displacement model](https://kenbrakke.com/evolver/bga/bga-7.htm).
- [NIST solder modeling](https://www.ctcms.nist.gov/solder/).
- [Interface Equilibrator capabilities](https://www.interfaceequilibrator.com/index.html) and [commercial product status](https://www.interfaceequilibrator.com/products.html).
- [KnotPlot current platforms and export capabilities](https://knotplot.com/download/).
- [Ridgerunner upstream](https://github.com/designbynumbers/ridgerunner) and [author notes](https://jasoncantarella.com/wordpress/software/ridgerunner/).
- [Surface Evolver author's paper](https://www.kenbrakke.com/papers/downloads/SurfaceEvolver_ExpMath.pdf).

Detailed commands, provenance, failures, and numerical outputs remain in `.research/solder/REPORT.md` and `.research/knot/REPORT.md`.
