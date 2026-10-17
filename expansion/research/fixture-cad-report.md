# Q1 fixture CAD completion

Implemented the selected scalar fixture geometry. All work is local. No lab was contacted, no component was ordered and no fabrication release is claimed.

## Delivered

- `force_lab/cad/spec.json` owns dimensions, materials, load estimates and explicit unreleased interfaces.
- `force_lab/cad/model.py` is the editable CadQuery source. Direct and tested transitive requirements are recorded beside it.
- `force_lab/tools/build_cad.py` generates four STEP assemblies for X/Z sensitive-axis configurations and 40/120 micrometer offsets. Each assembly contains 15 closed solids. There are 16 individual neutral STEP files.
- `force_lab/hardware/drawings` contains dimensioned SVG assembly, custom-part and joint-section sheets. Joint annotations were visually inspected and their initial overlap was corrected. Each upper rim endpoint is marked in the section.
- `force_lab/hardware/upper-cap-boundaries.dxf` and `lower-chip-boundaries.dxf` define actual 200 micrometer wettable circles and substrate/nonwet boundaries. They are engineering boundary layouts, not qualified process masks. No PCB copper post or unnecessary PCB fab workflow was introduced.
- `force_lab/hardware/README.md` documents assembly datums, reproducible commands, material assumptions, DXF layer semantics and release blockers.
- `force_lab/cad/evidence/verification.json` records actual neutral readback and geometry/load checks. `development-collision.json` preserves a reproducible negative control.

## Verification commands

```sh
python3.13 -m venv output/cad-env
output/cad-env/bin/python -m pip install -r force_lab/cad/requirements-lock.txt
output/cad-env/bin/python force_lab/tools/build_cad.py
output/cad-env/bin/python force_lab/tools/verify_cad.py
```

Verification passed on CadQuery 2.6.1 / OpenCascade 7.8.1.1.post1 with Python 3.13 on macOS arm64. It imports each actual STEP assembly and part, requires valid solids, compares source/neutral volume and bounds, rejects positive-volume interference, checks actual wet-face planes and pad-center offsets, audits DXF and island dimensions, and independently reads the base's ten cylindrical hole locations/radii plus the thermal pocket floor. It verifies 8 mm external optical apertures and narrow gap rays. It checks adjacency through the upper custom load path, with the vendor sensor attachment explicitly unresolved. It derives moving mass and moments from CAD volumes and centroids.

The negative control reinstates the rejected Z=16.7 mm shelf. Its actual 477 mm3 overlap with the X adapter is detected. The accepted shelf top is Z=26.7 mm and all four current assemblies have zero positive-volume part intersections. This is a development geometry result, not physical data.

## Measured digital results

| Quantity | Result |
|---|---:|
| Closed solids per neutral assembly | 15 |
| Neutral part files | 16 |
| Modeled moving mass | 40.3942057 mg |
| Remaining mass to 100 mg engineering target | 59.6057943 mg |
| Modeled carrier dead weight | 396.131837 microNewtons |
| Gravity moment at cool-tab center | 4.389771 microNewton meters |
| Worst gravity plus 124 microNewton normal-joint moment | 7.123971 microNewton meters |
| Rod-only transverse stiffness | 1334.563285 N/m |
| Rod-only deflection at 124 microNewtons | 0.0929143 micrometers |
| Uniform 200 K rod expansion | 1.880 micrometers |
| Conservative cap/lower-plane clearance at 0.1 degree tilt | 0.1471202 mm |
| Conservative rod/shield clearance at 0.1 degree tilt | 1.4607301 mm |

These are geometry and engineering calculations. They are not force calibration or physical validation. Bond/metallization densities are planning values. Actual attachment mass, compliance, thermal gradients, sensor response and dynamics remain unknown.

The illustrative 0.5 micrometer films are separate solids so wet faces remain exactly Z=0 and Z=0.150 mm. Consequently the lower substrate top is Z=-0.0005, upper substrate bottom Z=0.1505 and rod center Z=1.0005 mm. The lab must qualify and measure the actual film stack. The upper island is 0.350 mm behind the transparent cap's free positive-X edge.

## Limits and decisive next gate

The 2 mN sensor range alone cannot establish acceptability of approximately 7.124 microNewton meters of moment or the carrier's cross load. Supplier acceptance for custom attachment, moments, cross loads, temperature and overload margin is a real blocker. The indexed blank positions do not claim that an unnamed sensor tip reaches the tab. Actual sensor/stage/chamber/heater/bond/thin-film interfaces need accepted drawings before fabrication release.

An 8 mm empty optical cylinder cannot pass through the solid specimen faces. The model reserves two 8 mm external viewing apertures beyond the specimen and gap-level rays. It does not establish the full optical cone or full-rim pinning visibility. Through-glass complete-rim observation is a lab gate. No guide, thermocouple wire or shield may create a parallel upper load path.

Model the Domain put dimensions and unreleased interfaces in one specification. Build the Lever produced source-to-STEP/DXF/SVG generation and a rerunnable readback verifier. Prove It Works required actual neutral import, native hole/pocket inspection and a failing collision control before reporting digital completion.
