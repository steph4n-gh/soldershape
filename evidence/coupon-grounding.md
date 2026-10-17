# Grounding the 220 versus 270 micrometer coupon

## Overview

The coupon can independently test a pad-size effect on post-reflow clearance. It cannot qualify restoring force without a separate measured force experiment. The present solver predicts an isolated liquid joint with circular, permanently pinned rims. It omits substrate contact, a wetting law, thermal history, and package load sharing.

The existing external campaign predicts 201.774 micrometers for the 220 micrometer board pad and 190.681 micrometers for the 270 micrometer board pad under its nominal assumptions. Their predicted difference is 11.094 micrometers. The source's two measured heights differ by only 6 micrometers. Those are different questions from proving that one new process clears 185 micrometers. The retained [repair report](model-repair/report.md) and [independent science review](model-repair/science-review.md) preserve that distinction.

## Key concepts

`JointSpec` prescribes the gap between the two model wetted planes. `LoadSpec` contains no height and prescribes a positive downward normal load per joint. `solve()` dispatches between them. `equilibrium.standoff_mm` is the computed model gap. `input` and `input_sha256` always describe the actual request, including a height-free loaded request.

`volume_mm3` is the modeled body volume. Ordinary product requests use the declared liquid solder volume and wetted-plane geometry. The published-data replay deliberately uses an additional geometric approximation. It adds the volume of one substrate copper cylinder and subtracts its thickness from the output height. That approximation does not describe liquid occupying copper. It must remain explicit in the coupon prediction record.

The 2004 comparison supplies 280 micrometer upper pads, total solder volume 0.01745 cubic millimeters, nominal 34 micrometer substrate copper, and approximately 4 micronewtons per joint. Its measured height is between bond pads. Upper metallization thickness and several process uncertainties are missing. These facts come from [Van Veen et al., printed pages 60 and 61](https://imapsjmep.org/article/39820.pdf).

## How it works

The loaded solver constructs an initial height from diameters and volume only. Native minimization varies the upper plane and surface under external load. A second fixed-gap solve independently checks the upward reaction at the computed height. The exported shape and reported forces come from that second solve. The native load-work force is a net residual, not the reported solder reaction.

An accepted numerical result has `status == "refinement_checked"`, `load_balance.status == "balanced"`, and an empty `model_warnings` list. The force residual tolerance is the greater of 0.01 micronewtons and twice the observed static force refinement change. That is a numerical engineering gate. It is not an experimental uncertainty or a physical accuracy claim. Native refinement, stationarity, volume, Hessian, and sampled pad-plane diagnostics remain in the result and archive.

The exact reusable Python entry point is:

```python
from soldershape.model import LoadSpec
from soldershape.solver import solve

request = LoadSpec(
    lower_diameter_mm=0.220,
    upper_diameter_mm=0.280,
    volume_mm3=measured_model_volume_mm3,
    offset_mm=measured_offset_mm,
    normal_load_uN=declared_per_joint_load_uN,
    surface_tension_n_m=declared_gamma_n_m,
    density_g_cm3=declared_density_g_cm3,
    gravity=True,
)
result = solve(request)
```

The variable names above deliberately require measured inputs or frozen assumptions. They are not runnable placeholder data. Preserve both failed and successful results. Score height only after interpreting the actual geometry convention. For a paper-style single-pad-cylinder replay, use `Vmodel = Vsolder + pi * (Dlower / 2)**2 * tlower`, then `hrim = equilibrium.standoff_mm - tlower`. A literal-rim request uses `Vsolder` directly and applies no cylinder subtraction. Do not combine those conventions.

For reproducible ZIP exports, create a circular-pad footprint and a separate parameter JSON for each board-pad geometry. Run `python3 -m soldershape solve <footprint.kicad_mod> --pad A1 --parameters <parameters.json> --output <result.zip>`. The parameters omit `lower_diameter_mm` because the selected footprint supplies it. Loaded parameters include `normal_load_uN` and omit `standoff_mm`. `python3 -m soldershape replay <result.zip>` recomputes the height from trusted inputs. Replay does not execute archived command text.

The existing paired comparison changes only upper-pad diameter and volume while holding the board pad fixed. It cannot express this lower-pad-size experiment as one reference pair. Use two independent requests. An analysis script can pair the resulting specimen groups without altering the product API.

For aligned, lightly loaded joints, the paper's loaded analytical approximation is the required simple comparator. `spherical_gap_mm()` gives the unloaded spherical gap. `tools/check_loaded_formula.py` shows the independently evaluated axial spring correction. The existing campaign finds almost no useful accuracy difference between that formula and the native solver. A coupon must report both predictions.

## Where things live

- [model.py](../soldershape/model.py) defines validated requests, the spherical seed, footprint import, and editable-case parsing.
- [solver.py](../soldershape/solver.py) defines native minimization, the independent reaction check, diagnostics, and failure evidence.
- [__main__.py](../soldershape/__main__.py) implements `solve`, `solve-case`, `replay`, and comparison restrictions.
- [validate_loaded.py](../tools/validate_loaded.py) preserves the frozen published-data replay and the explicit copper mapping.
- [check_loaded_formula.py](../tools/check_loaded_formula.py) evaluates the strongest simple aligned comparator.
- [independent-evidence.json](model-repair/independent-evidence.json) freezes the source extraction and missing metadata.

## Gotchas that the coupon must resolve

The outside lab needs a physical input sheet before it sees prediction errors. It must record actual pad diameters, finished wettable edge geometry, pad thicknesses, finish, mask opening, upper-pad construction, solder alloy and lot, metal volume, flux, placement, reflow profile, and assembly orientation. Copper thickness alone does not identify a wetted plane. A custom PCB cap exposes upper sidewalls that the old source does not quantify. Section images must identify which sidewalls wet and whether the contact line stays pinned.

Record total supported cap mass, attached masses, joint count, and center of mass. The equal-share load assumption is `Fjoint = mass_kg * 9.80665 * 1e6 / Njoints` in micronewtons. For 20 joints, the old 4 micronewton assumption corresponds to 8.1577 milligrams total supported mass. That calculated target is not a measured property of a new cap. Tilt, missing joints, uneven volumes, and warpage can invalidate equal sharing. Do not use a height constraint or contacting fixture during reflow if testing a load-controlled prediction.

A 300 micrometer solid sphere contains only 0.0141372 cubic millimeters. A sphere containing 0.01745 cubic millimeters has diameter 321.810 micrometers. These are geometric calculations. The previous target included printed metal as well as a ball. Wet paste volume includes flux and cannot be substituted for solder metal volume. The lab must account for ball size variation, added paste metal, and a declared conversion to liquid volume. It must retain that conversion's uncertainty.

Measure final lateral offset in two axes, cap tilt, pad-to-pad gap, and the minimum clearance relevant to the 185 micrometer requirement. Height above the PCB laminate, height above the mask, and gap between the two copper top surfaces are different measurements. A single off-center section can misstate pad diameter and joint outline. Identify the section plane and preserve calibrated images. Post-reflow solid geometry remains an indirect test of liquid equilibrium. Record solidification and thermal reference assumptions rather than fitting an unexplained shrink correction to held-out heights.

Use repeated independently assembled caps for uncertainty. Multiple joints under one cap share load, placement, and reflow history. Treat them as correlated observations rather than independent specimens. Randomize the two geometries across panel positions and reflow runs. Preserve failed bridges, nonwet joints, voids, and outliers with their specimen IDs.

Freeze the geometry convention, material assumptions, clearance rule, error budget, exclusions, and analysis before reading outcome heights. Generate predictions from pre-outcome physical inputs. Keep post-section measured-offset or wetting-informed reconstructions as explicitly separate explanatory analyses. If any control fits gamma or a volume correction, reserve different assemblies for the held-out check. Do not fit either pad group and claim both independent.

The primary result needs both absolute height error and the pad-size difference, with metrology uncertainty and assembly variation. A result that reproduces the ordering but misses minimum clearance does not establish the design decision. A result with uncertainty spanning the 185 micrometer boundary remains inconclusive. No finite pilot sample proves a production yield or fatigue claim.

Explain the Number required the 6 micrometer measured difference to remain beside the 11.094 micrometer predicted difference. Prove It Works required direct inspection of the request dispatch, independent reaction check, and comparison restriction before proposing reusable interfaces.
