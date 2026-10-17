# Quote a matching molten-joint force test

This package lets an outside lab quote, build, commission, and run a test of SolderShape's isolated-joint force predictions. The proposed fixture holds two horizontal, circular wettable rims while a cool microforce sensor measures one reaction component. Separate specimens measure lateral and normal force.

The package is quote-ready. No lab has accepted the integration. Supplier-specific interfaces, the wetting process, and the assembled uncertainty budget remain unresolved. Fabrication release and physical validation are false. Do not purchase or fabricate from the reference geometry alone.

## Start with the staged quote

Read `RFQ.md` for the requested work and return format. Use `BOM.csv` for candidate parts and custom work. Use `PROCEDURE.md` for commissioning and confirmation. Use `uncertainties.md` for the numerical targets and their limits. `ANALYSIS.md` describes the exact input files and scorer.

The editable fixture source, neutral exports, and drawings describe an integration concept. The lab must accept its sensor attachment, thermal isolation, chamber access, load limits, and optical views before releasing supplier-specific drawings. The reference lower chip is 10 × 10 × 0.5 mm. The transparent upper cap is 2 × 2 × 0.3 mm on a horizontal fused-silica stalk, nominally 20 mm long and 1 mm in diameter. The upper pad center is 0.35 mm from the free cap edge. `cad/spec.json` controls these reference dimensions. Its 0.5 µm metal film and bond solids are illustrative envelopes that require process qualification. The supplier-approved attachment controls the final sensor interface.

## Keep the scientific question fixed

| Boundary or endpoint | Planned value |
| --- | --- |
| Lower and upper wettable rim diameter | 200 µm each, measured after processing |
| Hot gap between wettable planes | 150 µm, actively held from actual-rim metrology |
| Liquid metal volumes | 5 and 7 nL, independently measured |
| Lateral offsets | 40 and 120 µm |
| Primary comparison | Lateral restoring-force contrast at 120 µm |
| Difficult endpoint | Normal force and its sign for 7 nL at 120 µm |
| Commissioning endpoints | Larger signals at 40 µm |
| Separate diagnostics | 200 µm offset and 60 µm compressed gap |

The 200 µm-offset case has a retained model-scope warning. The compressed case has a retained numerical failure. Neither belongs in confirmatory scoring or a successful-force demonstration.

This experiment matches the original 200 µm stress-demo geometry. It does not validate the separate 400 µm-pad hypotheses in the ULX3S board demonstration. The earlier 220 versus 270 µm height coupon remains a separate experiment with its original protocol.

The old demo uses surface tension 0.48 N/m and density 9 g/cm³. Those are unqualified example inputs. They do not identify an alloy or temperature. Characterize the lab's actual alloy, temperature, atmosphere, liquid density, surface tension, and wetting boundary independently. Then freeze new predictions before acquiring confirmation force outcomes. Agreement with a rerun of the old numerical example is numerical agreement only.

## Separate three kinds of evidence

The native solver receipts test numerical repeatability and geometry checks. Hot blanks, transfer calibrations, images, and rim metrology test whether the apparatus measures the modeled boundary. Independent held-out bridge measurements test whether the model agrees with that physical boundary. A useful board-design recommendation needs all three plus evidence that its geometry and process fall within the tested domain.

The confirmation allocation contains 48 independent bridges. It spans three preparation blocks, two sensing axes, two offsets, two volume targets, and two paired replicates per block. Each volume member is a different bridge. A reversal, video frame, repeated dwell, or second axis on the same specimen is not another independent specimen. Commissioning and spare specimens are additional.

Measure transverse displacement from the actual hot rims before the freeze and during confirmation. The absolute transverse displacement plus its expanded uncertainty must not exceed 0.5 µm. This is an apparatus alignment policy for the unmodeled direction, not a demonstrated physical accuracy bound.

Identify each uncertainty source by ID, source unit, standard uncertainty and signed coefficients. A source affecting both physical inputs and corrected force must use the same ID, unit and standard uncertainty in both budgets. The scorer propagates the measured-minus-predicted residual with that covariance. Independently justify the independence of differently named sources in metadata. Unknown covariance cannot be treated as zero.

## Prepare the data workflow

Run commands from `/Volumes/Storage/oct16project`, or from the root of the extracted lab package. Python 3.12 or newer, a C compiler, `make`, and network access are required for the first native-engine setup. The setup script verifies the upstream source and builds the pinned engine. Computation works offline afterward. This checkout was exercised on Apple Silicon macOS; other hosts require their own environment check. Each output path must be new.

```sh
python3 tools/setup_engine.py
python3 force_lab/tools/analyze.py templates output/force-lab-inputs
python3 force_lab/tools/analyze.py plan output/force-lab-planning
```

The planning run uses example inputs. It makes no physical-validation claim. Complete the generated input and commissioning files using independent observations. Keep `outcomes-template.csv` blank. Do not create `outcomes.csv` in the input directory before the freeze.

Verify the retained numerical planning evidence with `python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120`. Rebuilding editable CAD requires the separate environment and commands in `cad/BUILD.md`. Rebuilding the printable handbook requires `python3 -m pip install -r force_lab/tools/requirements-docs.txt` and `python3 force_lab/tools/build_handbook.py`.

```sh
python3 force_lab/tools/analyze.py freeze output/force-lab-inputs output/force-lab-freeze
```

Register the returned manifest SHA-256 with the independent lab before confirmation force measurements. Substitute that exact digest for `REGISTERED_SHA256` below.

```sh
python3 force_lab/tools/analyze.py verify output/force-lab-freeze --manifest-sha256 REGISTERED_SHA256
python3 force_lab/tools/analyze.py score output/force-lab-freeze output/force-lab-outcomes.csv output/force-lab-score --manifest-sha256 REGISTERED_SHA256
```

The hash binds supplied bytes. It is not an external timestamp or proof that no one saw outcomes. A changed process requires a new freeze and new confirmation specimens. Missing specimens, failed assembly, depinning, numerical failure, or inadequate uncertainty remain visible. They cannot become passing data through exclusion or refitting.

Build and verify the portable handoff from the project root with these commands.

```sh
python3 force_lab/tools/package_lab.py build output/soldershape-force-lab-r1.zip
python3 force_lab/tools/package_lab.py verify output/soldershape-force-lab-r1.zip
```

## Report the actual status

| Status | Required evidence | Current status |
| --- | --- | --- |
| Quote-ready | Consistent geometry, protocol, BOM, blanks, analysis, and explicit unknown interfaces | Prepared for quotation |
| Lab accepted | Written capability and interface acceptance, including supplier limits | Not accepted |
| Fabrication released | Approved final drawings, materials, tolerances, and interfaces | Not released |
| Commissioned | Traceable assembled calibration, hot blanks, complete uncertainty budget, and observable stable rims | Not demonstrated |
| Physically tested | Raw independent held-out observations and frozen analysis | No observations acquired |
| Useful for PCB release | Tested process domain and a specific design decision whose margin survives uncertainty | Not established |

If the small 120 µm contrast cannot be resolved, commission a lateral-only 40 µm test first. That result can test substantial restoring force and boundary behavior. It cannot validate the small upward sign, simultaneous force vectors, free package alignment, or assembly yield.
