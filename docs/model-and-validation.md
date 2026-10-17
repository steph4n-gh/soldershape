# Model and validation status

SolderShape is a local equilibrium workbench around the native Surface Evolver engine. Its useful result is an inspectable comparison tied to a KiCad pad and reproducible inputs. Practitioner demand and a defensible commercial advantage remain untested.

## Model domain

The model has one connected isolated solder joint between parallel, fully wetted, pinned circular rims. The selected copper diameter supplies the lower wetting boundary as an explicit assumption. The upper diameter, liquid solder volume, material, offset and vertical condition are supplied independently.

The gap separates the two wetted pad planes. Ordinary volume means liquid solder excluding pad metal. Positive X follows the local offset axis. Positive Z points from the board toward the upper pad. At nonzero offset, restoring force is `-sign(offset) × X force`. Positive restoring force points toward alignment.

A prescribed gap represents an externally held fixture. A supported normal load instead solves the isolated joint's gap under the stated downward per-joint load. Package weight distribution, tilt and neighboring joints require an external calculation. Upward load support is expected in a checked supported-load result.

Rectangular, oval, custom and through-hole pads remain visible but are not solved as circles. A declared mask opening smaller than copper is rejected. Board-level mask rules, final CAM and actual wettable boundaries remain unresolved.

## Evidence categories

| Evidence | What it establishes | Limit |
| --- | --- | --- |
| Upstream BGA and analytic reference cases | Numerical agreement against specified references | Not a newly measured solder joint |
| `refinement_checked` | Declared volume, force-refinement, energy, local-Hessian and tessellation gates passed | Not a unique or global equilibrium proof |
| Native replay | Trusted requests regenerate agreeing forces and, for load control, gap | Not physical validation or a digital signature |
| Published physical-data campaign | Recorded residuals, missing inputs, mappings, sensitivities and failures | General force accuracy did not pass qualification |
| Published four-pad standoff comparison | Limited forward comparison under explicit paper-specific boundary and metal-volume assumptions | Not transferable process calibration or force qualification |
| Force fixture and height coupon | Quote-stage designs, prospective procedures and blank data templates | No fabricated specimen, accepted lab capability or measured result |

The [frozen physical campaign](../evidence/physical/validation-report.md) retains ambiguous pairings, failed solves, force discrepancies and substrate-plane excursions. The [root-cause report](../evidence/model-repair/report.md) retains the separate standoff investigation. Neither is a claim that the application predicts an actual assembly's forces accurately.

The [pre-lab coupon investigation](../prelab/REPORT.md) adds native combined-input stress cases, a prescribed-wetting finite-copper experiment and a reduced-order twenty-joint cap calculation. It retains reversed rankings, a native moving-height failure and a penetrating obstacle control that remains unconverged. Neither pad choice has a qualified 185 µm whole-cap clearance pass. The [measurement addendum](../prelab/LAB_ADDENDUM.md) identifies the observations needed to decide the physical boundary and volume.

## What remains outside the model

The application does not predict thermal reflow history, wetting chemistry, oxide or flux behavior, viscosity, alignment time, capture range, bridging, neighboring-joint coupling, cooled stress, fatigue, electrical reliability or manufacturing yield.

The curved surface can extend beyond the pad planes because substrate obstacles are absent. Detected vertex excursions produce a model warning and block a comparison preference. That vertex check does not certify continuous-surface clearance. The exported flat triangle mesh has its own reported volume discrepancy. Arbitrary exports do not receive a complete self-intersection proof.

The default material values are upstream example values, not a recommendation for a modern alloy. A physical comparison needs measured wettable rims, volume, hot geometry, material and boundary conditions. The 200 µm force fixture does not validate the default 400 µm Board case. The 220 versus 270 µm height coupon is a separate experiment.

## Result and archive interpretation

Failed rows retain errors without invented forces or solved gaps. Unchecked or model-limited results block comparative conclusions. A zero offset does not establish a lateral restoration preference. Sweeps contain independent static equilibria and do not simulate motion.

Editable case files contain inputs. Evidence ZIPs retain results, engine identity, models, logs, meshes and a SHA-256 manifest. New source-bearing ordinary ZIPs also contain a readable review. Known exact bundled footprint sources retain their original notice. Arbitrary user sources are not assigned a third-party license. A user remains responsible for permission to redistribute their own inputs.

Historical records and their missing standalone notice companions are described in the [provenance audit](../launch/provenance-audit.md). The public example package keeps the original inner ZIP unchanged and includes explicit notices. Public distributions must keep those notices together.

The two-footprint study retains its own decision brief and explicit equivalent-domain hypothesis. Its sampled analytical sensitivity is not a native uncertainty interval or a guarantee between samples.
