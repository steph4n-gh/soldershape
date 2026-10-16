# SolderShape

Compare the equilibrium shape and upper-pad forces of a single molten BGA solder joint, starting from a KiCad footprint. Version 0.2 runs locally with the pinned native Surface Evolver engine. It does not contain a Rust or WASM solver rewrite.

SolderShape was selected over KnotForge because it connects an existing PCB-design input to a specific parameter-comparison workflow. [SELECTION.md](SELECTION.md) records the alternatives, evidence, counterargument, and reversal condition. Practitioner demand remains untested.

## Run the workbench

Requirements are Python 3.12 or newer, a C compiler, `make`, and a modern browser. Setup needs an internet connection to download two hash-pinned upstream archives. Computation and the browser interface work offline afterward. This checkout was qualified on Apple Silicon macOS with Python 3.14 and Apple clang 21. Other platforms remain unqualified.

From the project directory, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve
```

On macOS, you can also double-click `Start SolderShape.command`. It sets up a missing engine and opens the local workbench. Launching again reopens an existing SolderShape service. A port used by another application is left alone.

Open [the local workbench](http://127.0.0.1:8765). Load the example footprint or import a `.kicad_mod`, select a circular copper pad, change the joint parameters, and compute. The example contains 36 circular 0.2 mm pads at 0.4 mm pitch. Set the upper package-pad diameter independently.

Use **Save editable case** to keep the footprint, selected pad, all inputs, and optional reference dimensions in JSON. **Open case** restores inputs and clears old computed results. Invalid files leave the current draft intact. The editable case and its formatted representation are limited to 2.1 MB.

Use **Use current design as reference**, then change upper-pad diameter or solder volume and choose **Compare reference and candidate**. Both designs compute afresh at the current board pad, gap, offset, surface tension, density, and gravity setting. The table shows the exact changed dimensions and both forces. A centering-force delta requires checked numerical results, a nonzero offset, and no detected pad-plane excursion. Changing a selected board pad clears the reference. Comparing board-footprint revisions is outside this workflow.

Sweep offset to compare lateral restoring force. Positive lateral force acts toward positive local x on the upper pad. Positive vertical force acts upward. The result shows the actual solved mesh, numerical checks, and an export bundle. Changing any input clears old results and downloads.

Stop the server with Ctrl+C. It binds to `127.0.0.1` and has no account or cloud service.

## Try the complete comparison

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

The ZIP contains a CSV, original footprint, normalized inputs, result JSON, engine provenance, generated Evolver model and commands, raw output, and OBJ and STL meshes in millimeters. `manifest.json` hashes every member. STL has no formal unit field, so the filename and manifest explicitly say millimeters. Replay verifies bundle integrity and regenerates trusted models from validated numeric inputs. It never executes scripts read from the archive. Replay reports whether engine source and executable hashes match and compares forces within its declared tolerance; it does not promise cross-platform bitwise equality.

## Verify the result

```sh
python3 tools/verify.py
python3 -m unittest discover -s tests -v
```

The numerical check runs the author's published BGA force example, an analytic cylinder, opposite placement offsets, surface-tension scaling, a solder-volume comparison, unequal pad diameters, mesh checks, ZIP integrity, and a full export/replay operation. Its measured output is [evidence/acceptance.json](evidence/acceptance.json). The reference script and raw output are beside it. [ACCEPTANCE.md](ACCEPTANCE.md) defines the checks before implementation.

The completed browser workflow is recorded in [evidence/browser-workflow.json](evidence/browser-workflow.json), with a [screenshot of the actual computed result](evidence/workbench.jpg). [Independent review](evidence/review.md) found and verified the repair of a failed-case replay defect. The original release passed 12 boundary tests. The expanded suite now has 24 tests, including editable-case boundaries, launcher reuse, pad-plane warning behavior, and an independent force-derivative regression. A separate [inert archive check](evidence/inert-archive-replay.json) confirms that replay ignores archived command text and recomputes trusted numeric inputs.

The default 0.2 mm pad, 0.15 mm standoff, 0.006 mm³ volume, and 0.02 mm offset produce about −19.63 µN lateral force and −43.78 µN vertical force on the upper pad in this model. At the same gap and offset, changing volume from 0.005 to 0.007 mm³ changes vertical force from about −128.77 to +43.54 µN. These computed comparisons illustrate model sensitivity. They do not establish which geometry is best for an actual assembly.

## Understand the limits

The model has one connected joint between parallel circular pads. Both circular rims are pinned and fully wetted. The footprint's selected copper diameter supplies the lower wetted diameter as an explicit assumption. Solder-mask apertures, contact-angle motion, neighboring joints, component tilt, and free component motion are not modeled. Offset follows the selected pad's local x direction. Rectangular, oval, custom, and through-hole pads remain visible but cannot be solved as circles.

The gap is the separation of wetted pad planes. Ordinary volume input is liquid solder excluding pad metal. The published benchmark uses a documented paper-specific effective-volume transformation; the product does not silently apply it to user designs. The curved surface can extend beyond the pad planes because substrate obstacles are not modeled. Detected vertex excursions produce a separate model-scope warning and block a comparison verdict. The vertex check does not certify continuous-surface clearance.

Inputs use millimeters, cubic millimeters, N/m, and g/cm³. The native model uses cgs units. The application converts forces from dynes to micronewtons. The material defaults of 0.48 N/m and 9 g/cm³ follow the upstream example class and are not a calibrated recommendation for a modern alloy. The footprint does not determine solder volume or final standoff; you supply them.

`refinement_checked` means the declared volume, force-refinement, energy-change, local-Hessian, and tessellation checks passed. It is not proof of a unique or globally minimal equilibrium. The diagnostic records each threshold and the normalization used near zero force. A bounded extra refinement can resolve a sensitive case; it does not turn every failed geometry into a qualified result. `not_converged` and `failed` retain their evidence.

The curved numerical mesh supplies forces. A further subdivision and conversion to flat triangles supplies display and export geometry. The export's volume discrepancy is reported separately. Representative acceptance meshes receive a proper transverse triangle-intersection check. Coplanar overlaps and tangential contacts are not certified, and arbitrary exported geometries do not receive a complete mesh-validity proof.

Published physical data was tested in this release. General physical accuracy did not pass qualification. The [frozen report](evidence/physical/validation-report.md) preserves all observations, calibration tracks, ambiguous pairings, failed runs, and substrate-plane excursions. No new physical solder sample or manufacturing outcome was tested here. This tool does not predict viscosity, flux or oxide chemistry, temperature history, dynamic alignment time, intermetallics, cooled-joint stress, fatigue, electrical reliability, or manufacturing yield. Use it for an inspectable equilibrium comparison under its stated assumptions.

## Physical benchmark and reproducibility

[Josell et al. (2002)](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) provides a pinned circular-pad subset. Geometry was measured after solidification. The paper's 0.4 N/m surface tension was fitted to its plotted data, so agreement at that value cannot establish independent physical accuracy. Specimen-specific normal loads, ball volumes and some height/offset pairings are unavailable.

The frozen campaign made 133 computation calls. Six of eight primary pairing alternatives passed numerical checks; two remained unstable. Of 108 sensitivity calls, 68 passed, 38 produced engine errors, and two remained unconverged. Every combined eight-corner sensitivity envelope is incomplete. A held-out 144.25 µN observation has a raw prediction of 303.93 µN after fitting one surface-tension scale only on three lower-load centers. Its mesh also extends 0.267 µm beyond each flat substrate plane. Two other central geometries predict the wrong normal reaction direction under either ambiguous pairing. These are retained negative results, not a physical pass.

The solver repair replaces unconditional Newton steps with energy-decreasing line searches and more gradient relaxation. Existing numerical thresholds remain unchanged. Independent equilibrium-energy derivatives agree with extracted forces within 1.18e-5 relative. See [the repair evidence](evidence/physical/solver-repair.md).

```sh
python3 tools/check_digitization.py
python3 tools/validate_physical.py --stage full --workers 2
python3 tools/compare_designs.py --solver-sha256 07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98
```

Matching raw receipts are cached by input, source and engine identities. Add `--refresh` to the physical runner to recompute rather than reuse matching receipts. See [PRODUCT_RELEASE.md](PRODUCT_RELEASE.md) for completion checks and [PHYSICAL_VALIDATION.md](PHYSICAL_VALIDATION.md) for the frozen workflow. A realistic next physical qualification requires identified specimen/process inputs and a supported treatment of substrate contact. New interface features cannot resolve those missing measurements.

## Project record

- [IMPLEMENTATION.md](IMPLEMENTATION.md) records the data model, interface, and architecture choice.
- [WORKFLOW.md](WORKFLOW.md) records the selected playbook and completion checks.
- [decisions.tsv](decisions.tsv) records decisions and evidence.
- [evidence/solder-feasibility.md](evidence/solder-feasibility.md) and [evidence/knot-feasibility.md](evidence/knot-feasibility.md) preserve both investigations.
- [THIRD_PARTY.md](THIRD_PARTY.md) records source provenance and distribution limits.

The `.research` directory holds the original bounded investigation and failed experiments. It is intentionally excluded from Git. The application and its fresh setup do not depend on it. `.engine` holds the locally downloaded and compiled engine and is also excluded from Git.
