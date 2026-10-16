# Physical scope audit

This audit compares the inherited fixed-rim model with the physical experiment. It does not digitize figures or report a new physical pass. Its proposed force-ratio check was subsequently excluded by the frozen protocol because Figure 5 specimen-specific normal loads are unavailable. The final validation report governs the executed checks.

## Model and experiment

`JointSpec` stores circular wetted diameters, liquid volume, rim separation, lateral offset, and material values. `solver._model` fixes both circular rims and minimizes the side-surface energy at fixed volume. Pressure-corrected virtual displacements produce the force on the upper pad. The model has no contact-line motion. See `soldershape/model.py` lines 14 to 23 and `soldershape/solver.py` lines 45 to 84 at inherited commit `fc384a0`.

[Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827), DOI `10.1115/1.1463732`, describes Sn63-Pb37 with flux at 210 ± 10 °C. Eight joints share the applied mass load. Geometry is measured after solidification. Pads are 5 µm thick. Stand-off spans the Si/Cu interfaces. The paper adds both pad volumes to its flat model. Figure 5 remains pinned. Figure 4 spreads beyond about 65 µN. Figure 6 always spreads. Figure 7 spreads beyond about 20 µN. The smallest balls have substantial volume scatter. Surface tension 0.4 N/m and silicon contact angle 150° were fitted to every plotted displacement. Independent silicon-angle measurement was 149 ± 3° at stated 2σ. See printed pages 228 to 232.

The current model is directly relevant to the pinned subset. It is physically incompatible with spreading points even when a fixed-rim equilibrium converges. A green numerical status cannot certify the contact-line assumption.

## Correct comparison and signs

The experiment applies loads and measures displacement. SolderShape accepts displacement and returns forces. These are comparable in either of two ways.

1. Evaluate forces at each measured offset and stand-off, then compare the full vector with the measured load. Propagate uncertainty in both measured coordinates. A force residual at an uncertain geometry has uncertainty in both components.
2. Solve for offset and stand-off whose force vector balances the known applied load, then compare the predicted coordinates with the measured coordinates. Preserve any failed outer solve. This uses the existing solver without inventing a wetting model.

For a positive measured offset, the joint's lateral reaction should be negative. Positive compression by the applied weight requires a positive upward joint reaction. Compare `-force_x_uN` with the positive shear-load magnitude and `force_z_uN` with the positive normal-load magnitude. Do not compare absolute values blindly, because a wrong force direction is a failure.

The paper's loads follow `FN = m*g*cos(phi)/8` and `FL = m*g*sin(phi)/8`. Mass includes the upper wafer. Figure labels already express force per joint. Do not divide plotted forces by eight again. The tantalum mass alone does not determine the normal force. The upper wafer matters. The paper reports approximately 1.95 mN per joint and a 0.03 mN stated 2σ uncertainty for the cross-section set. Any use of that value for the complete Figure 5 set must state the shared-load assumption if the exact specimen masses are unavailable.

Disable gravity for this comparison. This matches the paper and makes surface-tension scaling exact within numerical tolerance.

## The two pad mappings are different models

For equal pad diameter `d`, pad thickness `t = 0.005 mm`, solder volume `Vs`, and measured Si-interface separation `Hs`, the published approximation is:

```text
h_model = Hs
V_model = Vs + 2*pi*(d/2)^2*t
```

The literal fixed-Cu-rim interpretation is:

```text
h_model = Hs - 2*t
V_model = Vs
```

Use the published mapping to reproduce the paper's approximation. Use the literal mapping as a prespecified physical-geometry sensitivity. Do not describe these as algebraically equivalent. The first includes artificial bridge material within the two pad slabs and allows the capillary side surface to extend across their thickness. The second ends the side surface at the copper rims.

For Figure 5, `d = 0.64 mm` and `Vs = 0.0086 mm³`. The two slabs total `0.003216990877 mm³`. The published model volume is `0.011816990877 mm³`. Omitting that correction changes the intended bridge volume by 37.4% of the solder volume. Correcting both volume and stand-off at once would double-correct the geometry.

## Calibration and a surface-tension-free control

Using the paper's fitted 0.4 N/m against Figure 5 is calibration-dependent physical consistency. It is not an independent determination of absolute force accuracy. The subset itself participated in selecting this fitted value. The independent silicon contact-angle measurement does not fix this leakage. In the pinned subset, contact angle has no role in the energy derivative while the line remains pinned.

Without gravity, `E = gamma*A` and the wetted pad-area energy is constant. Equilibrium shape at a specified volume and fixed rims is independent of gamma. Both force components scale with gamma. Therefore `-Fx/Fz` is independent of gamma where `Fz > 0`. Compare that ratio with `FL/FN`, or compare their arctangents. This is a useful independent check of capillary geometry and force direction. It does not validate absolute force scale. Verify the cancellation by running at two gamma values before relying on it.

Freeze all measured points and uncertainty rules before inspecting this ratio's residuals. Keep a separate absolute-force comparison at the inherited default 0.48 N/m. Keep the fitted 0.4 N/m result beside it with its calibration label. Do not tune gamma, volume, or stand-off to eliminate individual residuals.

## An acceptance band that can be interpreted

Do not use an arbitrary percentage of force as a physical acceptance band. Thin bridges can be highly sensitive to stand-off and volume. The existing 1% refinement test measures numerical stability and does not define physical accuracy.

For coordinate prediction, score the residual against each plotted measurement interval plus an explicit digitization interval. Keep these in micrometers. Do not call the plot's uncertainty bars 2σ unless the paper explicitly identifies them that way. Report pointwise interval overlap and maximum normalized residual. Report all points, including the high-force lateral-offset outlier visible in Figure 5.

For force-vector prediction, propagate each point's offset and height intervals through the solver. Propagate ball-volume uncertainty separately. A box of allowed inputs is a sensitivity envelope, not automatically a 95% confidence region. Jointly varying uncertain inputs to find agreement is not a new point estimate.

The large-ball mean diameter differs from nominal by at most 5 µm, with individual RMS scatter at most 5 µm. These are different sources of uncertainty. For a 254 µm ball, 5 µm changes volume by about 6% to first order. Preserve nominal-volume and independently justified volume-sensitivity runs. Do not replace this with the much larger vendor tolerance or reduce the uncertainty by an assumed square-root-of-eight averaging without documenting independent-ball sampling and equal load sharing.

Solidification is another systematic sensitivity. The paper gives about 4.5% volume shrinkage, corresponding to about 1.5% isotropic linear shrinkage. The experiment measured restrained chip displacements, so those numbers do not justify multiplying all observed offsets and heights by 1.015 automatically. Run an explicit molten-volume sensitivity and report its effect. Do not add both full volume expansion and full coordinate expansion as independent random errors.

Report three possible outcomes. A consistent surface-tension-free ratio supports this pinned geometric regime. A fitted-gamma absolute comparison supports consistency with the published calibration. Uncertain material scale or incompatible contact conditions leave broader physical accuracy inconclusive. An interval failure remains a failure under its declared mapping.

## Independent primary source checked

[Howell, Megaridis, and McNallan, 2004](https://doi.org/10.1016/j.ijheatfluidflow.2003.10.003) measured dynamic surface tension of eutectic Sn-Pb jets under controlled oxygen. The primary publisher record specifies millisecond surface ages and strong oxygen effects. That is a different interface history from fluxed joints reflowed for seconds. It supports an interface-condition caveat, not an exact gamma replacement.

[Schwaneke, Falke, and Miller, 1978](https://stacks.cdc.gov/view/cdc/219922/cdc_219922_DS1.pdf) measured tin-lead surface tensions with a maximum-bubble-pressure method under purified helium. Their Table II gives temperature-dependent fits and standard errors. Compositions are atomic percent. A mass-percent composition cannot be selected from that table by matching the number 63. Different atmosphere, composition interpolation, and temperature prevent using its table as a same-condition solder-flux calibration. This source was inspected as a control and was not used to fit the Josell measurements.

The bounded source search did not identify an independent measurement of gamma for this exact solder, Actiec 2 flux, reflow history, and interface. The gamma-free force-direction control is the minimal useful repair.

## Minimal repairs before a broader product claim

- Record whether input stand-off is rim-to-rim or substrate-to-substrate. The existing `JointSpec` value is a rim-plane distance. Explain any paper-specific transformation in the validation runner.
- Record whether volume is actual liquid solder or the published solder-plus-pad approximation. Keep the correction out of ordinary user inputs.
- Exclude spreading points from a pinned-physics score and preserve them in the excluded-data record.
- Distinguish fitted physical consistency, geometry-only physical evidence, and independently calibrated absolute prediction in every reported verdict.
- Keep the published post-solidification and nominal-ball limitations with the quantitative comparison.

Prove It Works changed the proposed evidence from a successful numerical solve to a measurement-to-model comparison. Explain the Number changed the scoring from raw relative force error to uncertainty propagation and a material-scale-free control. Both leaf skill files were read during this audit.
