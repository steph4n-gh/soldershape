# Independent science review of the load-controlled repair

The repair supports a conditional pad-clearance screen and a sensible coupon choice. It does not qualify manufacturing advice or solder-joint forces. The native computation now answers the right vertical boundary-condition question. Most of the demonstrated aligned clearance decision is available from the paper's much simpler loaded analytical model.

This review read the primary PDFs, model and solver code, frozen extraction and forward protocol, source audit, upstream diagnosis, load-solver experiments, axisymmetric check, and all 31 campaign receipts. It changed no source or experimental data. This is an independent review by another agent using the inherited model family, not a cross-family review.

## The root-cause account needs a precise limit

The evidence rules out a large implementation defect in the old prescribed-gap forces for the tested cases. Different representations of the same NIST surface agree within 0.012 percent. The independent meridional calculation approaches the same aligned forces under mesh refinement. Both are numerical checks of a common physical idealization.

The old experimental comparison had an ill-conditioned inverse problem. It treated measured mean gap and offset as exact prescribed constraints. The source instead predicts those displacements under imposed load. That difference matters because the reconstructed thin-joint normal reaction changes by thousands of micronewtons for a micrometer of height. Fitting gamma to three inverse observations can absorb geometry error. A low fit residual does not identify the material value.

The source and archive also describe different input cases. The paper specifies two 5 micrometer copper layers. The example contains two 4 micrometer layers and a height floor for a larger solder volume. Those differences explain why the downloaded example is not an exact saved Figure 5 baseline. They do not establish that the paper's thickness is wrong. The forward tests correctly preserve both interpretations instead of choosing the better fit.

The root cause of the last NIST physical outlier remains unknown. The conditional forward replays predict 13.60 or 14.45 micrometers of offset against the measured center of 31.0 and the plotted interval of 26.1 to 36.1. The normal load scenario is inferred rather than specimen metadata. The source's gamma was fitted to the experiment. Neither run is an independent force validation. These distinctions follow directly from the [Josell paper](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) and the retained replays.

Calling the repair "the physical failures fixed" would overstate the result. The repaired issues are the evaluation method, source-case identification, and missing vertical load condition. The remaining measured discrepancy is preserved.

## The independent campaign has no measured-height leakage

The frozen extraction hash is `febf6be52f0531e79ffc33b553ec8d79cc802bfc54a76438c3a7ce34e10c91d9`. The campaign result reviewed here has SHA256 `e20e2ba3a50246b9516ac00c4df13c5be02c770e0eeb0503957e33332bb888ed`.

Each request contains volume, diameters, offset, load, and declared material assumptions. No request contains `standoff_mm`. Every recorded seed exactly matches a fresh `spherical_gap_mm` calculation from its request geometry. Experimental heights enter only the scoring rows. Every receipt hash matches its report row. This tests both code and artifacts rather than relying on the protocol's stated intent.

The one 34 micrometer substrate-cylinder correction matches the [Van Veen paper's reference-plane approximation](https://imapsjmep.org/article/39820.pdf). Subtracting that same thickness after solving reports the distance between the bond pads. Using the literal solder volume with the rim gap is a separate model geometry. It must not be presented as a statistical uncertainty interval or silently combined with the published correction.

All 31 rows report `refinement_checked`, balanced load, zero negative native Hessian counts, and no sampled plane warnings. The largest independently verified load residual is 0.001082 micronewtons. The numerical tolerances range from 0.010000 to 0.021631 micronewtons. The largest native height-refinement change is 0.001643 micrometers. Those tolerances are engineering checks rather than certified numerical error bounds or experimental confidence intervals.

A fresh public q270 solve during this review reproduced rim height 190.680604 micrometers and upward reaction 4.00032579 micronewtons. Its request hash is `b2dfb18b790843bf27dece1be15f65d5a7d8d686925d8cca68c326d50652330d`. The solver hash is `31e551899bbd040ad78aa2e2daf489a9fa3d2295df9db3f63e90149ff631c702`. The fresh reaction is computed in a second fixed-gap solve, so the native optimizer's load-work term cannot hide an unbalanced reported reaction.

## The external result supports geometry trends

The following values use gamma 0.48 N/m, gravity off, 4 micronewtons per joint, and the published copper approximation. Measured values are the Table 3 evaluation labels.

| Substrate diameter, micrometers | Measured rim height | Native prediction | Signed error | Unloaded sphere | Loaded analytical baseline |
|---:|---:|---:|---:|---:|---:|
| 170 | 204 | 211.11195 | +7.11195 | 212.44657 | 211.22044 |
| 220 | 198 | 201.77437 | +3.77437 | 202.79007 | 201.80098 |
| 270 | 192 | 190.68060 | -1.31940 | 191.46091 | 190.68456 |
| 320 | 177 | 178.40420 | +1.40420 | 179.01122 | 178.40789 |

All height columns are in micrometers. Native mean absolute error is 3.40248 micrometers. The unloaded sphere gives 3.94674 and the independently evaluated loaded analytical model gives 3.43619. The paper's tabulated loaded analytical predictions give 2.825, although their material assumptions are not fully identified. This evidence shows no meaningful native accuracy advantage for aligned, lightly loaded joints.

The native model preserves all four measured heights' order. It predicts a q270-to-q320 decrease of 12.27640 micrometers against the measured 15. Gamma stress from 0.35 to 0.55 N/m changes each primary height by only 0.30 to 0.66 micrometers. Small sensitivity to this chosen interval does not supply a measured gamma interval or validate the force scale.

At q170, using the independently reported approximate 60 micrometer offset predicts 208.17631 micrometers. The absolute error falls from 7.11195 to 4.17631. That is a useful indication that offset can matter. It does not reproduce the publication's offset-specific native value of 205 micrometers. The remaining difference is unresolved, and "approximately 60" has no reported uncertainty. Neither the offset nor volume may be adjusted to eliminate that difference.

## The strongest simple baseline reaches the same practical decision

I visually checked equation 9 on printed page 58 and evaluated it without fitting native results. Let `k` be the spherical effective gap in millimeters, `p` and `q` the pad radii, `j=(k*k+p*p+q*q)/(p*p+q*q)`, and `u=p*q/(p*p+q*q)`.

```python
Kz = gamma*(4*math.pi/5)*j*(j*(j+4)+10*u*u)/(j*j-4*u*u)**1.5
rim_height_um = 1000*(k-.034) - normal_load_uN/Kz
```

`Kz` is in N/m. A micronewton divided by N/m gives micrometers. The formula is the paper's small-load spring correction. It is not a new solver or a fit to the campaign.

The declared 185 micrometer clearance produces these volume-stress bounds at gamma 0.48.

| Substrate diameter | Native at -5% solder | Native at +5% solder | Loaded analytical at -5% | Loaded analytical at +5% |
|---:|---:|---:|---:|---:|
| 220 | 195.37752 | 207.95592 | 195.40196 | 207.98540 |
| 270 | 184.35186 | 196.81068 | 184.35487 | 196.81570 |
| 320 | 172.21478 | 184.41733 | 172.21791 | 184.42160 |

The justified action is to carry q220 into a controlled coupon comparison. Its minimum declared scenario is 10.37752 micrometers above the requirement. That is a conditional design-screen margin. It is not a manufacturing lower confidence bound.

q270 passes nominally but fails the declared -5% volume scenario. It must not be recommended as robust to that scenario. q320 is below the requirement even in the +5% scenario. Its proximity to the boundary does not prove every actual assembly fails. All three conclusions are reproduced by the loaded analytical baseline to within 0.03 micrometers for q220 and within 0.006 for q270 and q320.

The unloaded sphere alone gives 185.09366 at q270 minus 5% and 185.05702 at q320 plus 5%. It therefore makes different binary classifications within 0.1 micrometers of the boundary. The claim that every sphere result gives the same classification would be false. The proper small-load correction removes that apparent advantage of native computation. Those submicrometer differences are also much smaller than the observed external physical residuals.

Gamma variation and volume variation were tested separately, not as a complete Cartesian set. The +/-5% volumes are declared stresses, not measured manufacturing tolerances. No reported process distribution or confidence level permits combining those scenarios into a yield claim. The literal-rim alternative can cross the clearance boundary because it describes a materially different geometry. That sensitivity reinforces the need to identify the actual wetted reference planes and sidewalls before applying the screen to a new process.

## Investment verdict and next falsifier

SolderShape can help an engineer frame a pad-height tradeoff, reject an insufficient nominal margin, and choose a more conservative geometry for physical testing. This independent series supports that bounded use. It does not support qualified process signoff, assembly yield, self-alignment force accuracy, or fatigue life.

Native 3D computation earns its place as a way to inspect offset geometry, large-load behavior, contact diagnostics, and exportable shapes. This campaign demonstrates that ability and a directionally useful offset correction. It has not demonstrated superior physical accuracy over the loaded analytical baseline. For the evidenced aligned clearance task, Occam's Razor favors the formula. Keep the native engine for cases the formula cannot represent, with the remaining physical limits visible.

The smallest decisive next experiment is a same-process q220 versus q270 coupon at the intended volume, alloy, flux, and reflow profile. Measure the deposited volume, pad geometry, wetted planes, package load, final stand-off distribution, and measurement uncertainty. Freeze the 185 micrometer rule before observing the results. Calibrate at most a designated control, then predict the other geometry without fitting. Continue product qualification only if its independent clearance prediction survives the actual uncertainty. A measured force experiment is separately required before claiming accurate restoring forces.

Fix Root Causes kept implementation agreement separate from the unresolved physical outlier. Explain the Number required every reported campaign count, receipt identity, and numerical tolerance to be inspected. Occam's Razor changed the practical comparator from an unloaded sphere to the published loaded analytical correction.

## Integration note after review

The integrating agent made the campaign report serialization deterministic after a cache-only rerun changed nested dictionary key order. The final sorted-key report SHA256 is `a7b684b560021988fb464b4851fa1c232efc29d5ab3912a37e2ef2cbe0990a47`. The earlier hash above identifies the first fresh-run serialization. No numerical value, input, protocol, or native receipt changed. All 31 stored receipt digests remain the ones audited in this review.
