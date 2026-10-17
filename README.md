# SolderShape

Review a PCB pad revision under explicit solder-joint assumptions. Version 0.4 compares two imported footprints, shows conditional gap margins and sampled assumption reversals, and exports a replayable decision brief. The local workbench also inspects individual equilibrium shapes and upper-pad forces using the pinned native Surface Evolver engine.

SolderShape was selected over KnotForge because it connects an existing PCB-design input to a specific parameter-comparison workflow. [SELECTION.md](SELECTION.md) records the alternatives, evidence, counterargument, and reversal condition. Practitioner demand remains untested.

## Explore a real complex board and commission a force test

The [ULX3S board explorer](http://127.0.0.1:8768/board) connects an attributed routed board to an actual selected pad and two native joint calculations. Its 235 components and 1177 pads supply engineering context. Only the selected isolated joint is computed. Unknown package geometry, liquid volume, gap and material remain explicit hypothetical inputs. Change an input, compute afresh, and export the original board, exact pad mapping, native meshes and raw receipts together. [Board instructions](board_demo/APP.md) explain the comparison and numerical replay.

The separate [force-lab handoff](force_lab/README.md) matches the earlier 200 µm stress experiment. It includes editable mechanical CAD, four STEP configurations, thin-film DXF artwork, drawings, staged RFQ, instrumentation/BOM, calibration and uncertainty procedures, 48 independent specimens, blank data and prospective analysis. The native planning study demonstrates a failed initial uncertainty budget and a tighter unmeasured candidate. It does not establish lab capability. Sensor moments, complete rim visibility, wetting and hot metrology remain commissioning gates. No lab acceptance, fabrication release or physical validation is claimed.

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8768
python3 tools/verify_board.py board_demo/data/browser-comparison.zip --replay
python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120
```

[Completion evidence](expansion/RESULTS.md) records the actual browser workflow, artifact checks, independent repairs and exact commands. [Product end-state](expansion/PRODUCT-ENDSTATE.md) bounds further investment around a measured operating domain and practitioner value. The solver remains unchanged. A Rust/WASM port, coupled package simulation and new physics have not earned their complexity.

## Run the workbench

For an immediate visual example, open [the misalignment stress demo](http://127.0.0.1:8765/demo) after starting the service. It compares exact native meshes for 5 and 7 nL solder at large placement offsets, preserves a substrate-plane limit and a numerical failure, and exports editable inputs. [Demo instructions](demo/README.md) and [computed results](demo/RESULTS.md) explain its conditional scope. Recorded inspection does not require a compiled engine.

Requirements are Python 3.12 or newer, a C compiler, `make`, and a modern browser. Setup needs an internet connection to download two hash-pinned upstream archives. Computation and the browser interface work offline afterward. This checkout was qualified on Apple Silicon macOS with Python 3.14 and Apple clang 21. Other platforms remain unqualified.

From the project directory, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve
```

On macOS, you can also double-click `Start SolderShape.command`. It sets up a missing engine and opens the local workbench. Launching again reopens an existing SolderShape service. A port used by another application is left alone.

Open [the local workbench](http://127.0.0.1:8765). Load the example footprint or import a `.kicad_mod`, select a circular copper pad, change the joint parameters, and compute. The example contains 36 circular 0.2 mm pads at 0.4 mm pitch. Set the upper package-pad diameter independently.

Use **Save editable case** to keep the footprint, selected pad, all inputs, and optional reference dimensions in JSON. **Open case** restores inputs and clears old computed results. Invalid files leave the current draft intact. The editable case and its formatted representation are limited to 2.1 MB.

Use **Use current design as reference**, then change upper-pad diameter or solder volume and choose **Compare reference and candidate**. Both designs compute afresh at the current board pad, vertical condition, offset, surface tension, density, and gravity setting. Choose **Prescribed gap** for a fixture-held joint or **Supported normal load** to solve height from the downward load carried by one joint. Do not supply both constraints. The table shows the changed dimensions, each solved gap, and both forces. An aligned load comparison reports a height difference without claiming centering force. A centering-force delta requires checked numerical results, a nonzero offset, and no detected pad-plane excursion. Changing a selected board pad clears the reference. Use the separate design-study workflow below to compare two board-footprint revisions.

Sweep offset to compare lateral restoring force. Positive lateral force acts toward positive local x on the upper pad. Positive vertical force acts upward. The result shows the actual solved mesh, numerical checks, and an export bundle. Changing any input clears old results and downloads.

Stop the server with Ctrl+C. It binds to `127.0.0.1` and has no account or cloud service.

## Review a pad revision before commissioning a test

Open [Compare pad revisions](http://127.0.0.1:8765/study). Import a reference footprint and a candidate footprint independently. Each lower diameter comes from its own selected copper pad. Enter common upper-pad geometry, liquid volume and supported load. State the required pad-face gap and its source. Record input provenance and the user-supplied evidence for each circular wetting boundary.

Load the coupon planning example to inspect the actual 220 versus 270 micrometer question. It contains artificial planning inputs, not measurements. With the optional two-pad effective-volume hypothesis, literal rims predict gaps above the declared 185 micrometer threshold while the competing approximation predicts gaps below it. The correct report is assumption-sensitive. It requests boundary and metal-height measurements instead of approving a pad.

The study runs two nominal native cases, or four with the explicit two-pad approximation. It shows the published analytical comparator beside them. The three declared volume points are an analytical sampled sensitivity. They are not a native uncertainty interval or a guarantee between samples. The analytical screen requires zero offset, gravity off and linear compression at most one percent of unloaded height. This cutoff is software policy, not a physical accuracy bound. Nominal agreement does not validate the endpoint samples.

Save and reopen the editable study. Download its source footprints, native receipts and meshes, sampled CSV, normalized inputs, and static decision brief in one hashed ZIP. The two-pad mesh is an equivalent computational domain that includes metal-cylinder volume. It is not a measured solder surface. Every edit clears the old report and export. Replay regenerates the native requests and analytical decision.

```sh
python3 -m soldershape study examples/coupon-planning.study.json --output output/pad-review.zip
python3 -m soldershape replay output/pad-review.zip
python3 tools/verify_study.py output/pad-review.zip
```

The [refinement results](refinement/REVIEW.md), [accuracy audit](refinement/accuracy-audit.md), [current alternatives](refinement/alternatives.md), and [product rationale](refinement/POSITIONING.md) state what is demonstrated and what remains a hypothesis. There is no proven solver, accuracy, customer, or data moat. The current useful difference is an auditable design-to-test workflow. Following supported package guidance or using the aligned analytical formula is often sufficient.

A footprint import rejects a declared solder-mask opening smaller than the copper pad. It cannot resolve board-level rules, drawn mask openings or final CAM. A boundary evidence declaration remains a user-supplied assumption. Numerical acceptance does not verify actual wetting, package load sharing, cooled clearance or manufacturing readiness.

## Predict height under a supported load

Open `examples/loaded-volume.soldershape.json` and choose **Compare reference and candidate**. At a 4 µN downward load, the reference volume of 0.006 mm³ predicts a 0.141986 mm gap. Reducing volume to 0.005 mm³ predicts 0.125400 mm. Both forces are checked in a fresh fixed-gap computation after the native height optimization. The input file contains no measured or prescribed height. Each sweep offset solves its own height.

```sh
python3 -m soldershape solve-case examples/loaded-volume.soldershape.json --output output/loaded-volume.zip
python3 -m soldershape replay output/loaded-volume.zip
```

The archive separates the prescribed request from `equilibrium`. Standalone root model and command files reproduce the final fixed-gap check. `load-height/` contains the native height model and logs. Replay solves height again from the request. The numerical residual tolerance is reported and is not a physical confidence interval. Final heights must be between 0.02 and 10 mm. Native trial heights are unbounded, and failed branches remain failures.

The [physical root-cause report](evidence/model-repair/report.md) evaluates an independent published four-pad standoff experiment without fitting surface tension or using measured heights as inputs. It distinguishes preliminary clearance screening from process qualification. The original force-validation failure remains unresolved.

## Try the complete fixed-gap comparison

Open `examples/centering-volume.soldershape.json` through **Open case**, then choose **Compare reference and candidate**. The reference uses 0.006 mm³ and the candidate uses 0.005 mm³ at 0.2 mm wetted diameters, a prescribed 0.15 mm gap, and a 0.02 mm offset. Select each row to inspect its mesh. **Download results** includes both cases, their independent geometry and solver evidence, the editable case, and `comparison.json`.

The nominal candidate increases modeled restoring force from 19.633 to 20.364 µN and changes vertical force from −43.776 to −128.771 µN. This is a conditional comparison, not a production recommendation. The [design experiment](evidence/design-comparison/report.md) evaluates five declared volume samples per candidate across an illustrative ±10% range. Under its explicit fixture-held rule requiring no separating force, 0.005 mm³ is the selected tested option. The 0.006 and 0.007 options produce separating force in some samples. A volume-equivalent sheared-cylinder approximation misses that sign change. The experiment checks sample points, not every value in a continuous tolerance interval. The cylinder changes the wetted radius and is a cheap approximation, not the strongest same-boundary alternative. SolderShape uses the same numerical engine as native Surface Evolver; its advantage is the KiCad-to-comparison workflow and reproducible export.

Run the same editable case from the terminal:

```sh
python3 -m soldershape solve-case examples/centering-volume.soldershape.json --output output/comparison.zip
python3 -m soldershape replay output/comparison.zip
```

## Run a reproducible case

```sh
python3 -m soldershape pads examples/BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD.kicad_mod
python3 -m soldershape solve examples/BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD.kicad_mod --pad A1 --parameters examples/parameters.json --output output/joint.zip
python3 -m soldershape replay output/joint.zip
```

Add `--offsets=-0.04,-0.02,0,0.02,0.04` to compute an independent five-point sweep. Each row retains its own model, logs, and geometry. A failed row remains in the export. The solve command exits with code 1 when any row fails a numerical check, and with code 2 for an invalid request.

Replay accepts at most 40 MB compressed, 160 MB uncompressed, 100 members, and seven cases. The ZIP contains a CSV, original footprint, normalized inputs, result JSON, engine provenance, generated Evolver model and commands, raw output, and OBJ and STL meshes in millimeters. `manifest.json` hashes every member. STL has no formal unit field, so the filename and manifest explicitly say millimeters. Replay verifies bundle integrity and regenerates trusted models from validated numeric inputs. It never executes scripts read from the archive. Replay reports whether engine source and executable hashes match and compares forces within its declared tolerance; it does not promise cross-platform bitwise equality.

## Verify the result

```sh
python3 tools/verify.py
python3 -m unittest discover -s tests -v
python3 tools/validate_loaded.py
python3 tools/check_loaded_formula.py
python3 tools/verify_loaded_archive.py
```

The numerical check runs the author's published BGA force example, an analytic cylinder, opposite placement offsets, surface-tension scaling, a solder-volume comparison, unequal pad diameters, mesh checks, ZIP integrity, and a full export/replay operation. Load-controlled checks additionally verify independent normal reaction, unloaded sphere agreement, geometric scaling, optimizer derivative and initialization sensitivity, and retained failures. Its measured output is [evidence/acceptance.json](evidence/acceptance.json). The reference script and raw output are beside it. [ACCEPTANCE.md](ACCEPTANCE.md) defines the checks before implementation.

The completed browser workflow is recorded in [evidence/browser-workflow.json](evidence/browser-workflow.json), with a [screenshot of the actual computed result](evidence/workbench.jpg). [Independent review](evidence/review.md) found and verified the repair of a failed-case replay defect. The original release passed 12 boundary tests. The expanded suite covers editable cases, launcher reuse, pad-plane warnings, independent force derivatives, and load-controlled computation and replay. A separate [inert archive check](evidence/inert-archive-replay.json) confirms that replay ignores archived command text and recomputes trusted numeric inputs.

The default 0.2 mm pad, 0.15 mm standoff, 0.006 mm³ volume, and 0.02 mm offset produce about −19.63 µN lateral force and −43.78 µN vertical force on the upper pad in this model. At the same gap and offset, changing volume from 0.005 to 0.007 mm³ changes vertical force from about −128.77 to +43.54 µN. These computed comparisons illustrate model sensitivity. They do not establish which geometry is best for an actual assembly.

## Understand the limits

The model has one connected joint between parallel circular pads. Both circular rims are pinned and fully wetted. The footprint's selected copper diameter supplies the lower wetted diameter as an explicit assumption. Solder-mask apertures, contact-angle motion, neighboring joints, component tilt, and free lateral component motion are not modeled. Load control solves only the isolated joint's vertical equilibrium under a prescribed per-joint load. It does not calculate package tilt or the load carried by each joint. Offset follows the selected pad's local x direction. Rectangular, oval, custom, and through-hole pads remain visible but cannot be solved as circles.

The gap is the separation of wetted pad planes. Ordinary volume input is liquid solder excluding pad metal. The published benchmark uses a documented paper-specific effective-volume transformation; the product does not silently apply it to user designs. The curved surface can extend beyond the pad planes because substrate obstacles are not modeled. Detected vertex excursions produce a separate model-scope warning and block a comparison verdict. The vertex check does not certify continuous-surface clearance.

Inputs use millimeters, cubic millimeters, N/m, and g/cm³. The native model uses cgs units. The application converts forces from dynes to micronewtons. The material defaults of 0.48 N/m and 9 g/cm³ follow the upstream example class and are not a calibrated recommendation for a modern alloy. The footprint does not determine solder volume or final standoff. Supply liquid solder volume and either the gap or the downward load carried by this joint.

`refinement_checked` means the declared volume, force-refinement, energy-change, local-Hessian, and tessellation checks passed. It is not proof of a unique or globally minimal equilibrium. The diagnostic records each threshold and the normalization used near zero force. A bounded extra refinement can resolve a sensitive case; it does not turn every failed geometry into a qualified result. `not_converged` and `failed` retain their evidence.

The curved numerical mesh supplies forces. A further subdivision and conversion to flat triangles supplies display and export geometry. The export's volume discrepancy is reported separately. Representative acceptance meshes receive a proper transverse triangle-intersection check. Coplanar overlaps and tangential contacts are not certified, and arbitrary exported geometries do not receive a complete mesh-validity proof.

Published physical data was tested in this release. General physical accuracy did not pass qualification. The [frozen report](evidence/physical/validation-report.md) preserves all observations, calibration tracks, ambiguous pairings, failed runs, and substrate-plane excursions. No new physical solder sample or manufacturing outcome was tested here. This tool does not predict viscosity, flux or oxide chemistry, temperature history, dynamic alignment time, intermetallics, cooled-joint stress, fatigue, electrical reliability, or manufacturing yield. Use it for an inspectable equilibrium comparison under its stated assumptions.

## Physical benchmark and reproducibility

[Josell et al. (2002)](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) provides a pinned circular-pad subset. Geometry was measured after solidification. The paper's 0.4 N/m surface tension was fitted to its plotted data, so agreement at that value cannot establish independent physical accuracy. Specimen-specific normal loads, ball volumes and some height/offset pairings are unavailable.

The frozen campaign made 133 computation calls. Six of eight primary pairing alternatives passed numerical checks; two remained unstable. Of 108 sensitivity calls, 68 passed, 38 produced engine errors, and two remained unconverged. Every combined eight-corner sensitivity envelope is incomplete. A held-out 144.25 µN observation has a raw prediction of 303.93 µN after fitting one surface-tension scale only on three lower-load centers. Its mesh also extends 0.267 µm beyond each flat substrate plane. Two other central geometries predict the wrong normal reaction direction under either ambiguous pairing. These are retained negative results, not a physical pass.

The solver repair replaces unconditional Newton steps with energy-decreasing line searches and more gradient relaxation. Existing numerical thresholds remain unchanged. Independent equilibrium-energy derivatives agree with extracted forces within 1.18e-5 relative. See [the repair evidence](evidence/physical/solver-repair.md).

```sh
python3 tools/check_digitization.py
python3 tools/compare_designs.py --solver-sha256 c7bcfcc2c5f24e6e783540b3fcabc45a8d15308ded887aca2ae41442ddf4c8a6 --output output/design-comparison-refinement
```

Matching raw receipts are cached by input, source and engine identities. The physical campaign above is historical and remains bound to its recorded sources. It was not rerun during version 0.4 refinement. `tools/validate_physical.py --stage full --workers 2` reruns it on the current source and writes into `evidence/physical`; use an isolated copy to preserve the frozen record. Add `--refresh` to recompute rather than reuse matching receipts. See [PRODUCT_RELEASE.md](PRODUCT_RELEASE.md) for the earlier completion checks and [PHYSICAL_VALIDATION.md](PHYSICAL_VALIDATION.md) for the frozen workflow. A realistic next physical qualification requires identified specimen/process inputs and a supported treatment of substrate contact. New interface features cannot resolve those missing measurements.

## Project record

The [outside-lab coupon package](coupons/README.md) supplies editable boards, Gerbers, a parts and services list, blank measurement sheets, a staged RFQ, and prospective analysis for a physical 220 versus 270 micrometer pad comparison. It is prepared for a quote and pilot. No physical coupons have been ordered or measured.

- [IMPLEMENTATION.md](IMPLEMENTATION.md) records the data model, interface, and architecture choice.
- [WORKFLOW.md](WORKFLOW.md) records the selected playbook and completion checks.
- [decisions.tsv](decisions.tsv) records decisions and evidence.
- [evidence/solder-feasibility.md](evidence/solder-feasibility.md) and [evidence/knot-feasibility.md](evidence/knot-feasibility.md) preserve both investigations.
- [THIRD_PARTY.md](THIRD_PARTY.md) records source provenance and distribution limits.

The `.research` directory holds the original bounded investigation and failed experiments. It is intentionally excluded from Git. The application and its fresh setup do not depend on it. `.engine` holds the locally downloaded and compiled engine and is also excluded from Git.
