# SolderShape feasibility

## Overview

Proceed with a narrow engineering exploration tool using the existing native Surface Evolver engine. The numerical feasibility gate passed. A Rust/WASM rewrite has not earned its cost. Useful first behavior is importing circular KiCad BGA pads, choosing an opposing circular pad, standoff, molten volume and lateral displacement, then comparing equilibrium geometry and capillary restoring force with reproducible exports. Do not call this a validated reflow-process predictor.

NIST's solder group documents equilibrium-shape modeling as a useful electronic-packaging task. Its FY2001 report describes measured lateral and normal offsets versus shear force for 0.35 mm pads and approximately 0.0023 mm³ Pb63Sn37 solder, with Surface Evolver predictions consistent with the experiment. This supports the physical class of use. We have not reproduced those physical measurements or established demand from present-day KiCad users.

The strongest alternatives are Surface Evolver with its own BGA scripts, SE-FIT and Interface Equilibrator. SE-FIT already wraps Surface Evolver with predefined geometries, parameter sweeps and stability tools, so those features are not novel. Its official site says it is Windows/.NET and no longer actively developed. Interface Equilibrator provides a Windows CAD GUI, arbitrary solid geometry, wetting and stability analysis. Its full academic license is free. Its current products page says commercial products are unavailable because commercial activities have been interrupted. A small, inspectable, locally runnable KiCad-to-comparison workflow is a plausible distinction. It does not establish a large market or superior solver.

## Key concepts

- The body has a fixed molten-solder volume. Free facets contribute surface energy. The model also includes gravity.
- Each wetted contact rim is pinned to a circle. This assumes complete coverage of a specified circular wetted area. It is not a prediction of changing wetting chemistry or a freely moving contact line.
- Capillary force is the negative derivative of energy with respect to offset or height. Upstream `xzforce.cmd` corrects virtual-deformation energy by pressure times volume error. Reading force from a coarse rim alone is explicitly unreliable in the author's BGA tutorial.
- Mesh refinement and element order affect force estimates more than the volume constraint residual. A tiny volume residual alone does not establish accuracy.
- The model uses cgs. One cm is 10 mm, one cm³ is 1000 mm³, one dyne is 0.01 mN, and 480 dyn/cm is 0.48 N/m.

## How it works

The upstream `.fe` file defines vertices, edges, oriented facets, pad constraints, material values, and the constrained body. `gogo` alternates gradient steps and refinements, then takes two Hessian steps. Extra refinements followed by gradient/Hessian steps test convergence. `eigenprobe 0` counts negative directions in the configured Hessian. All our test configurations had zero negative eigenvalues. This is a local numerical check, not a global-minimum proof.

A practical interactive solver can use quadratic mode (`M 2`) with two or three refinement levels. Capture energy, pressure-corrected forces, volume residual, and negative eigenvalue count before export. Export with `r; linear; recalc` and then emit full-precision vertices and oriented triangle indices. The extra quadratic refinement makes curved midside points into corners before conversion. The export's flat volume must be reported separately from the curved solver volume.

Tested mesh command follows. The command is written as one block so redirecting it writes only the records.

```text
{ foreach vertex vv do printf "VERTEX %d %.17g %.17g %.17g\n",vv.id,vv.x,vv.y,vv.z; foreach facet ff do printf "TRIANGLE %d %d %d %d\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id; } >>> "mesh.txt"
```

The program exits zero after some invalid commands. Therefore wrappers must reject runtime `ERROR` or `WARNING` messages, missing tagged results, nonfinite output, bad volume residual, negative Hessian eigenvalues, or a failed convergence threshold. A bounded timeout and mesh-count limit are also necessary.

## Measurements

Official bga-4 linear variational-force references and our reproduction, in dynes:

| Mesh stage | Official | This run |
|---|---:|---:|
| `gogo` | 24.583607839182264 | 24.583607832649193 |
| Next refinement | 18.668111551491222 | 18.668470969158250 |
| Next refinement | 17.195067593386000 | 17.195149428617071 |

The first reference agrees within 2.66e-10 relative. The other two agree within 2e-5 and 5e-6 relative. Official quadratic references are 16.729909603674571 and 16.705446803680104. Reproduction gives 16.721753548929485 and 16.704776364773750, within 0.049% and 0.0041% respectively. These are numerical comparisons, not experimental validation.

For a generated case with diameter 0.5 mm, gap 0.3 mm, offset 0.05 mm, volume 1.3 times the initial cylinder and tension 0.48 N/m:

| Mode / facets | Horizontal dyne | Vertical dyne |
|---|---:|---:|
| Linear / 432 | -5.38712448 | 10.79505521 |
| Linear / 6336 | -5.52129245 | 8.92312287 |
| Linear / 24960 | -5.52803586 | 8.82973690 |
| Linear / 99072 | -5.52972229 | 8.80637455 |
| Quadratic / 432 | -5.52995027 | 8.80360205 |
| Quadratic / 1632 | -5.53026383 | 8.79887927 |
| Quadratic / 6336 | -5.53028319 | 8.79860110 |

Linear 24960-facet forces differ from the quadratic 6336-facet comparison by 0.041% horizontal and 0.354% vertical. The quadratic 1632-to-6336 change is about 0.0032% vertical. Relative volume residuals were below 3.54e-16. Quadratic 6336-facet export through `r; linear` produced 12482 vertices and 24960 triangles. All 37440 undirected edges had two incident facets. Signed export volume was 7.656008597614084e-5 cm³ versus solver volume 7.657632093125124e-5 cm³, a 0.021201% deficit.

A spherical-segment zero-gravity check has a near-zero expected force. Linear 6336 facets yielded 0.4858136 dyne while quadratic 1632 facets yielded 0.00098608 dyne. This shows why a relative force tolerance needs an absolute tolerance near zero. An earlier invalid `G := 0` command is preserved in `sphere-invalid.out`; it did not disable gravity and is explicitly excluded from qualification.

The upstream lateral test returned restoring force against positive and negative offsets. It also showed a small symmetry bias after shifting the already-evolved mesh. Use fresh symmetric baselines or report absolute tolerances, rather than promising exact zero.

## Where things live

- `bootstrap.sh` downloads/verifies archives and compiles the native engine. It links a separate no-op graphics-title shim because the upstream headless target has a missing symbol.
- `src/` is extracted Surface Evolver 2.70 source. Numerical source files are unmodified.
- `bga/` contains official BGA inputs and command files, plus generated test data.
- `baseline.cmd`, `quadratic.cmd`, `sphere.cmd`, `sphere-quad.cmd`, `lateral.cmd`, and matching `.out` files contain reproducible commands and raw receipts.
- `run-gates.py`, `realistic.json`, and `realistic.out` record the realistic linear refinement study.
- `quad-export.cmd`, `quad-export.out`, and `bga/quad-export.mesh` contain the quadratic-to-flat experiment.
- `verify.py` checks source-force agreement, error logs, convergence, finite vertices, closed mesh and export-volume discrepancy.

Reproduce everything from this directory with `bash replay.sh`. The native build command is `make -C src -j4 CC='cc -O2 -std=gnu89 -w' CFLAGS=-DGENERIC GRAPH=nulgraph.o GRAPHLIB=../headless-title.o`. Run an existing case with `(cd bga && ../src/evolver bga-4.fe < ../baseline.cmd)`.

## Gotchas and remaining uncertainty

The current native archive is version 2.70, dated August 25, 2013. The author's own paper says the program is public domain. There is no unified license file in this archive. `src/sdrv.c` separately credits copyright 1990 Tamar Schlick for sparse-solver modifications. The generated Bison parser includes GPL text with an explicit unrestricted-output exception. Preserve those notices and review these component origins before redistribution. Do not represent every line of the distribution as independently cleared public domain. Local evaluation does not need a new port.

No tests here establish viscosity, dynamic self-alignment time, thermal reflow, oxidation, intermetallic growth, solder-mask wetting, metallurgy, final cooled shape, fatigue or manufacturing yield. Equal circular pads have numerical reference coverage. Unequal radii, realistic modern alloy parameters, unsupported KiCad pad types and extreme necking need explicit product limits and their own convergence checks. No claim of first-of-its-kind software is supported.

## Source provenance

Retrieved on October 16, 2026. Hashes are saved in `SHA256SUMS`.

- [Surface Evolver official source and install instructions](https://kenbrakke.com/evolver/evolver.html).
- [Surface Evolver 2.70 source archive](https://kenbrakke.com/evolver/downloads/evolver-2.70.tar.gz). SHA-256 `be7d60d9eb690f1fb124e2ecc12237a7a35be1935bfa5e92be3fe912207a3b6b`.
- [Official BGA examples archive](https://kenbrakke.com/evolver/downloads/bga-files.zip). SHA-256 `96389e8200320cc8acfbf60b8ed23e2d05941613af5b55824c36890113c6e659`.
- [BGA model sequence](https://kenbrakke.com/evolver/bga/bga.htm) and [force-method and convergence reference](https://kenbrakke.com/evolver/bga/bga-4.htm).
- [Author's Surface Evolver paper, availability in section 12](https://www.kenbrakke.com/papers/downloads/SurfaceEvolver_ExpMath.pdf). Saved locally.
- [NIST solder group](https://www.ctcms.nist.gov/solder/).
- [NIST FY2001 report, restoring-force experiment](https://www.govinfo.gov/content/pkg/GOVPUB-C13-3eb23f90b734538e3f6155970d824798/pdf/GOVPUB-C13-3eb23f90b734538e3f6155970d824798.pdf).
- [Interface Equilibrator capabilities](https://www.interfaceequilibrator.com/) and [current products/licensing](https://www.interfaceequilibrator.com/products.html).
- [SE-FIT capabilities](https://www.se-fit.com/about/) and [download/current-maintenance statements](https://www.se-fit.com/downloads/).
