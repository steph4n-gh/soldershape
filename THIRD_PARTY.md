# Third-party provenance

## Surface Evolver

The local setup downloads [Surface Evolver 2.70](https://kenbrakke.com/evolver/downloads/evolver-2.70.tar.gz), SHA-256 `be7d60d9eb690f1fb124e2ecc12237a7a35be1935bfa5e92be3fe912207a3b6b`, and the [official BGA examples](https://kenbrakke.com/evolver/downloads/bga-files.zip), SHA-256 `96389e8200320cc8acfbf60b8ed23e2d05941613af5b55824c36890113c6e659`.

Ken Brakke's [Surface Evolver paper](https://www.kenbrakke.com/papers/downloads/SurfaceEvolver_ExpMath.pdf) describes the program as public domain. The source archive has no single comprehensive license file. `src/sdrv.c` separately credits copyright 1990 Tamar Schlick for sparse-solver modifications. The generated Bison parser has a skeleton exception. Preserve all upstream notices and complete a component review before redistributing source or binary. No claim that every source line is cleared as public domain is made here.

Source archives, extracted files, build outputs, and the executable remain in the local ignored `.engine` cache. They are not vendored in the tracked project. Setup retains a one-line no-op graphics-title callback needed by the generic headless target. It does not modify numerical source. `.engine/provenance.json` records the patch, compiler, commands, source hash, and locally built executable hash.

The generated joint model and force calculations follow the documented [BGA model sequence](https://kenbrakke.com/evolver/bga/bga.htm), particularly [BGA-4's pressure-corrected virtual-work force methods](https://kenbrakke.com/evolver/bga/bga-4.htm) and [BGA-7's lateral displacement model](https://kenbrakke.com/evolver/bga/bga-7.htm). Credit these upstream sources when describing the computation. The application is an interface and workflow around this numerical work.

## KiCad example footprint

The included BGA-36 footprint comes from the KiCad community's `kicad-footprints` repository at commit `7ebfa6b23cc292a56f751b7b5f4a0e12eeef69dd`. Its original filename and bytes are preserved. `examples/provenance.json` contains the exact raw URL and SHA-256.

KiCad libraries use CC-BY-SA 4.0 with an electronic-design exception. The original license and exception are included in `examples/KICAD-LICENSE.md`. Attribution is to the KiCad library contributors. SolderShape does not claim authorship of that footprint or recommend it for manufacture.

## KnotForge investigation

Ridgerunner was inspected as an alternative. It is not part of the runtime or bundled product. Its core files state GPL-3.0-or-later, with inconsistent older package metadata. Bundled example-knot provenance also needs review before redistribution. The dependency build failures and source hashes are retained in `evidence/knot-build-experiment.md` and `evidence/knot-feasibility.md`.

## ULX3S board context

The board atlas uses the unmodified [EMARD ULX3S hardware source](https://github.com/emard/ulx3s) at commit `6a92cec6b177191c5b0f80e260013a1f8ec147dd`. Exact source URLs, byte counts and SHA-256 values are in `board_demo/source/provenance.json`. The original board, README and license bytes remain under `board_demo/source/`.

Its modified MIT notice credits EMARD, copyright 2016-2018. It additionally requires the EMARD, RADIONA and FER logotypes to remain visible and unmodified in their original top-silkscreen locations, shapes and sizes. The atlas retains the complete native front silkscreen and the original source. Its original notice accompanies board-bound exports. The board authors do not endorse the hypothetical solder comparison, and no manufacture of this board is authorized by this work.

The force fixture uses separately pinned CadQuery and document-generation dependencies only to create local engineering artifacts. Their distributions and transitive notices remain in the local environment. No third-party interpreter, CAD kernel or vendor hardware drawing is redistributed in the handoff. Candidate instrument specifications are attributed to primary sources in `expansion/research/metrology.md` and `force_lab/BOM.csv`; unresolved interfaces are engineering placeholders rather than vendor-certified compatibility.
