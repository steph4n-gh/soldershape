# SolderShape

Compare the equilibrium shape and upper-pad forces of a single molten BGA solder joint, starting from a KiCad footprint. This first version runs locally with the pinned native Surface Evolver engine. It does not contain a Rust or WASM solver rewrite.

SolderShape was selected over KnotForge because it connects an existing PCB-design input to a specific parameter-comparison workflow. [SELECTION.md](SELECTION.md) records the alternatives, evidence, counterargument, and reversal condition. Practitioner demand remains untested.

## Run the workbench

Requirements are Python 3.12 or newer, a C compiler, `make`, and a modern browser. Setup needs an internet connection to download two hash-pinned upstream archives. Computation and the browser interface work offline afterward. This checkout was qualified on Apple Silicon macOS with Python 3.14 and Apple clang 21. Other platforms remain unqualified.

From the project directory, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve
```

Open [the local workbench](http://127.0.0.1:8765). Load the example footprint or import a `.kicad_mod`, select a circular copper pad, change the joint parameters, and compute. The example contains 36 circular 0.2 mm pads at 0.4 mm pitch. Set the upper package-pad diameter independently.

Sweep offset to compare lateral restoring force. Positive lateral force acts toward positive local x on the upper pad. Positive vertical force acts upward. The result shows the actual solved mesh, numerical checks, and an export bundle. Changing any input clears old results and downloads.

Stop the server with Ctrl+C. It binds to `127.0.0.1` and has no account or cloud service.

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

The completed browser workflow is recorded in [evidence/browser-workflow.json](evidence/browser-workflow.json), with a [screenshot of the actual computed result](evidence/workbench.jpg). [Independent review](evidence/review.md) found and verified the repair of a failed-case replay defect. All 12 boundary tests pass. A separate [inert archive check](evidence/inert-archive-replay.json) confirms that replay ignores archived command text and recomputes trusted numeric inputs.

The default 0.2 mm pad, 0.15 mm standoff, 0.006 mm³ volume, and 0.02 mm offset produce about −19.63 µN lateral force and −43.78 µN vertical force on the upper pad in this model. At the same gap and offset, changing volume from 0.005 to 0.007 mm³ changes vertical force from about −128.77 to +43.54 µN. These computed comparisons illustrate model sensitivity. They do not establish which geometry is best for an actual assembly.

## Understand the limits

The model has one connected joint between parallel circular pads. Both circular rims are pinned and fully wetted. The footprint's selected copper diameter supplies the lower wetted diameter as an explicit assumption. Solder-mask apertures, contact-angle motion, neighboring joints, component tilt, and free component motion are not modeled. Offset follows the selected pad's local x direction. Rectangular, oval, custom, and through-hole pads remain visible but cannot be solved as circles.

Inputs use millimeters, cubic millimeters, N/m, and g/cm³. The native model uses cgs units. The application converts forces from dynes to micronewtons. The material defaults of 0.48 N/m and 9 g/cm³ follow the upstream example class and are not a calibrated recommendation for a modern alloy. The footprint does not determine solder volume or final standoff; you supply them.

`refinement_checked` means the declared volume, force-refinement, energy-change, local-Hessian, and tessellation checks passed. It is not proof of a unique or globally minimal equilibrium. The diagnostic records each threshold and the normalization used near zero force. A bounded extra refinement can resolve a sensitive case; it does not turn every failed geometry into a qualified result. `not_converged` and `failed` retain their evidence.

The curved numerical mesh supplies forces. A further subdivision and conversion to flat triangles supplies display and export geometry. The export's volume discrepancy is reported separately. Representative acceptance meshes receive a proper transverse triangle-intersection check. Coplanar overlaps and tangential contacts are not certified, and arbitrary exported geometries do not receive a complete mesh-validity proof.

No physical solder sample, reflow process, or manufacturing outcome was tested. This tool does not predict viscosity, flux or oxide chemistry, temperature history, dynamic alignment time, intermetallics, cooled-joint stress, fatigue, electrical reliability, or manufacturing yield. Use it for an inspectable equilibrium comparison under its stated assumptions.

## Project record

- [IMPLEMENTATION.md](IMPLEMENTATION.md) records the data model, interface, and architecture choice.
- [WORKFLOW.md](WORKFLOW.md) records the selected playbook and completion checks.
- [decisions.tsv](decisions.tsv) records decisions and evidence.
- [evidence/solder-feasibility.md](evidence/solder-feasibility.md) and [evidence/knot-feasibility.md](evidence/knot-feasibility.md) preserve both investigations.
- [THIRD_PARTY.md](THIRD_PARTY.md) records source provenance and distribution limits.

The `.research` directory holds the original bounded investigation and failed experiments. It is intentionally excluded from Git. The application and its fresh setup do not depend on it. `.engine` holds the locally downloaded and compiled engine and is also excluded from Git.
