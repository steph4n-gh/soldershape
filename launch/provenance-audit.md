# Public-release provenance audit

Reviewed on 2026-10-16 against commit `79170fc6cb339ef787a029c02892d92829724203`. This report records source notices and packaging observations. It does not grant a project license or establish legal clearance.

## Release decision

The repository has useful upstream provenance, pinned inputs, and explicit physical limitations. It has no top-level `LICENSE`, `COPYING`, or other license grant for SolderShape's own code, documentation, images, or hardware designs. An owner-selected license and its scope are a prerequisite for calling the project open source. Do not infer a license from the upstream engine or the included examples.

A recorded demonstration page can use a narrower distribution set. Keep the original Board archive unchanged, accompany it with its original notice and attribution, and identify any new review as a separate presentation. The public page must preserve the numerical and physical qualifications. The local Python service is not a public hosted-compute deployment.

## Included third-party material

| Material | Exact local source | Verified evidence and release treatment |
| --- | --- | --- |
| Surface Evolver engine | `tools/setup_engine.py`, ignored `.engine/` | Setup downloads two hash-pinned upstream archives and builds locally. No tracked C files, C headers, engine binary, or source tarball were found. No tracked ZIP contains these files. Keep this separation for an initial source release. |
| Evolver BGA model methods | `soldershape/solver.py`, generated `model.fe` files in evidence ZIPs | The model and virtual-work force procedure follow Brakke's BGA examples. `THIRD_PARTY.md` already credits the source. Preserve that attribution in public explanations and evidence wrappers. Generated model files are not the entire upstream C program. |
| KiCad BGA-36 library footprint | `examples/BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD.kicad_mod` | Its SHA-256 matches `examples/provenance.json`, pinned to commit `7ebfa6b23cc292a56f751b7b5f4a0e12eeef69dd`. The original notice is `examples/KICAD-LICENSE.md`. Credit the KiCad library contributors and retain the CC-BY-SA 4.0 notice with its electronic-design exception. |
| ULX3S board | `board_demo/source/ulx3s.kicad_pcb`, `README.md`, `LICENSE.md` | All three byte hashes match `board_demo/source/provenance.json`, pinned to commit `6a92cec6b177191c5b0f80e260013a1f8ec147dd`. Its modified MIT notice includes a separate logo-preservation condition. Keep the exact license, original board, full native front silkscreen, and EMARD attribution. |
| ULX3S-derived atlas and extracted footprints | `board_demo/assets/board.svg`, `board_demo/assets/footprints.pretty/`, `board_demo/context.json` | Native extraction and readback are documented in `board_demo/NATIVE.md`. These remain derived board material. A new project license must not replace the board's original notice. The UI already links the board source and license. |
| Coupon boards and force fixture | `coupons/tools/build_boards.py`, `coupons/hardware/`, `force_lab/cad/model.py`, `force_lab/hardware/` | The sources construct the geometry. They do not import vendor CAD. No vendor datasheet PDF or third-party interpreter is tracked. The project's own hardware and drawing license is still unspecified. These artifacts remain quote-stage concepts with unreleased interfaces. |
| Published physical data extraction | `evidence/physical/source.json`, `nist-extraction.json`, `nist-extraction.md` | The paper's URL, PDF identity, approximate digitization, ambiguity, and limits are recorded. The source PDF and extracted raster remain ignored. No PDF is tracked. Keep the paper citation and avoid presenting reconstructed points as newly measured observations. |
| Product screenshots | `cohesion/*.png`, `refinement2/*.png`, other evidence images | These are documented as application captures. No stock-photo distribution was found in the tracked inventory. A launch capture containing ULX3S still needs its board attribution and original graphical context. This audit did not visually inspect every historical screenshot. |

The [current KiCad library page](https://www.kicad.org/libraries/license/) distinguishes electronic designs from redistributed library collections. The [pinned library notice](https://raw.githubusercontent.com/KiCad/kicad-footprints/7ebfa6b23cc292a56f751b7b5f4a0e12eeef69dd/LICENSE.md) matches the included notice. Redistribution as a library collection retains the stated license and attribution requirements. Do not apply the electronic-design exception indiscriminately to copied standalone library files.

The [pinned ULX3S license](https://raw.githubusercontent.com/emard/ulx3s/6a92cec6b177191c5b0f80e260013a1f8ec147dd/LICENSE.md) requires its notice to accompany copies or substantial portions. It also requires the EMARD, RADIONA, and FER logotypes to remain unmodified and visible at their original top-silkscreen locations, shapes, and sizes. Use an intact full-board view for the launch material, retain its notice nearby, and avoid endorsement claims. This report does not assert that an arbitrary crop satisfies that condition.

Brakke's [Surface Evolver paper, section 12](https://www.kenbrakke.com/papers/downloads/SurfaceEvolver_ExpMath.pdf) describes the program as public domain. The actual downloaded `src/sdrv.c` separately credits Tamar Schlick, copyright 1990. `src/ytab.c` and `src/ytab.h` carry GNU Bison notices and a generated-parser exception. The existing `THIRD_PARTY.md` accurately avoids treating every source line as cleared public domain. Keep local download/build setup rather than bundling the binary before a complete component review. The [BGA tutorial](https://kenbrakke.com/evolver/bga/bga.htm), [BGA-4 force method](https://kenbrakke.com/evolver/bga/bga-4.htm), and [BGA-7 offset model](https://kenbrakke.com/evolver/bga/bga-7.htm) are the relevant computational credits.

## Standalone evidence notice gaps

Eight tracked generic ZIPs contain the byte-identical KiCad example footprint, SHA-256 `71284db92e3b91db34a94fefdd45f8d0677c64ec0ad08a8fbec1431109925d48`, without an internal license notice.

- `cohesion/evidence/offset-sweep.zip`
- `evidence/design-comparison/existing-0.006.zip`
- `evidence/design-comparison/gravity-controls.zip`
- `evidence/design-comparison/less-0.005.zip`
- `evidence/design-comparison/more-0.007.zip`
- `refinement2/evidence/failed-single.zip`
- `refinement2/evidence/loaded-comparison.zip`
- `refinement2/evidence/offset-sweep.zip`

Two other generic ZIPs contain the extracted ULX3S U1 footprint, SHA-256 `14b691bcc05e1c93fa1ae8aeb70361e646a4f4ffba255ebd4b9002ae0ba2160a`, without the Board notice.

- `cohesion/evidence/board-to-joint-comparison.zip`
- `refinement2/evidence/joint-comparison.zip`

This is a standalone packaging gap. The complete repository already includes both notices. Preserve the historical ZIP bytes and their recorded hashes. Do not advertise those bare generic ZIPs as independent public downloads. A new outer package can retain the original ZIP unchanged and add the appropriate original notice, source attribution, exact provenance, and an explanation of the inner archive. Hash every new wrapper member. That approach makes the notices travel with the distributed copy and preserves the historical evidence identity. It is a proposed packaging correction, not an assurance that every downstream use satisfies all license conditions.

The recorded Board ZIPs already contain `BOARD-LICENSE.md` and board provenance. `demo/data/stress-cases.zip` already contains `KICAD-LICENSE.md`, `THIRD_PARTY.md`, and footprint provenance. A public Board demonstration wrapper should retain these existing notices and identify the new review separately. Link the wrapper as the downloadable unit.

The generic runtime exporter, `soldershape/artifacts.py:make_bundle`, does not attach origin notices. New Board-to-Joint exports therefore lose the Board notice even though the input bytes remain identifiable. Before publishing a runtime release, attach notices when a source matches known bundled provenance, including the ULX3S extraction. Do not assign a license to arbitrary user-uploaded footprints. This can be a bounded follow-up and does not require changing old archives.

## Small remaining corrections

1. Obtain the owner's project-license choice and specify its scope. Keep third-party exceptions explicit. An unapproved MIT draft is not a license grant.
2. Include the selected license in all newly built release and lab packages. `force_lab/tools/package_lab.py` currently includes `LICENSE` only if it exists. `coupons/tools/package_lab.py` currently omits it entirely. Preserve old package bytes.
3. Add a short media inventory with capture date, application commit, scenario, and any included board attribution. There is no tracked video. Use real product capture rather than simulated output if a walkthrough is added.
4. Keep the narrower claim used by the application. One selected joint is calculated. The full PCB is context. Force accuracy remains physically unqualified, and lab fixtures are not fabrication releases.
5. In `THIRD_PARTY.md`, prefer "This package is not a ULX3S fabrication release" over "no manufacture ... is authorized by this work." The former describes the engineering status without appearing to override the upstream hardware permission.

## Audit method

The inventory used `git ls-files`, source-header searches, source-manifest SHA-256 checks, and member inspection of all 16 tracked ZIPs. No ZIP or historical file was rewritten. The checked inventory had no tracked C file, C header, PDF, shared library, executable, MP4, or MOV. Ignored local dependencies and generated handoff packages were distinguished from tracked release material. Official upstream pages were read on the audit date. This audit did not perform a full license analysis of the ignored native-engine component tree or a visual review of every media file.
