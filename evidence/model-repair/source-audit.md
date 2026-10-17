# Source and measurement audit

Verdict is **ISSUES**. The frozen extraction preserves the actual experimental symbols and the published volume correction. It does not establish that the inverse calculations reproduce the paper's force-controlled model. There is a material discrepancy between the article's 5 micrometer copper layer and the downloadable example's 4 micrometer layer. Thin-joint force predictions amplify this difference.

## Overview

The source experiment applies a nearly constant compressive load to an eight-joint assembly, changes its tilt, then measures the solidified geometry. The published calculation predicts both height and offset from the applied force. SolderShape currently predicts a force from a prescribed height and offset. These are related problems, but replacing noisy measured geometry with exact constraints does not reproduce the original statistical comparison.

The primary publication is [Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827), DOI `10.1115/1.1463732`. I independently read all seven pages with pdfplumber and inspected the native Figure 5 raster and the rendered measurement diagrams. I read the original NIST ZIP archive's model, force functions, script, and parameter files. The current [NIST archive page](https://www.ctcms.nist.gov/solder/underfill/index.html) explicitly distinguishes force-controlled and displacement-controlled codes.

The PDF SHA256 is `4917aa35b4b804292826f8ce92b1f7c51eaed83e6f0777aeefb26195e7204990`. The original ZIP SHA256 is `fa1ceb86bd9f37214194370b809ee92e73614ed3c1c7b1e43a80460d759bfcc5`. Complete hashes, numbered source text, curve readings, load arithmetic, and four numerical receipts are in `.research/model-repair/source/`.

## Key concepts

The measured height is the separation between the two Si/Cu interfaces. It includes the copper layers. It is not the clear distance between the copper top surfaces. The paper replaces both raised copper disks with flat planes and adds their occupied volumes to the numerical body. Its positive volume correction is explicit on journal page 231, PDF page 5, lines 24 to 26 of the numbered extraction. The correct article mapping is therefore `gap=h` and `volume=Vs+2*pi*(d/2)^2*t`. The literal rim model uses `gap=h-2*t` and `volume=Vs`. These remain different geometries.

The article specifies diameter 0.64 mm and copper thickness 5 micrometers on journal page 228. Radius 0.32 mm in `force.fe` agrees with that diameter. For Figure 5, the article mapping gives volume 0.0118169908773 mm3. The 4 micrometer archive example gives 0.0111735927018 mm3. Neither correction has a sign or radius-versus-diameter error.

The Figure 5 measurements use nominal 10 mil balls and nominal volume 0.0086 mm3. The reported optical diameter checks are on solid balls. The paper does not state a separate molten-volume correction. It describes about 4.5 percent contraction on freezing and treats solidified dimensions as approximations to liquid dimensions. A physically consistent liquid-volume sensitivity would increase solder volume by `1/0.955`, before adding the unchanged copper volume. It must not be confused with multiplying only height and offset by 1.015. The assembly constrains contraction, so neither is an exact specimen correction.

## How it works

1. The paper divides total weight, including the upper silicon wafer, across eight joints. Equations 1 and 2 on journal page 229 give normal load `mg*cos(phi)/8` and shear `mg*sin(phi)/8`. Plotted shear is already per joint. The upward reaction balances the downward normal load.
2. Each plotted geometry averages three sectioned joints. Each lateral measurement also averages the two pad-edge readings. Feeding those averages into a nonlinear force law is not equal to averaging forces across the original joints.
3. The published model permits its contact line to move inside a pad, remain on the edge, or spread onto silicon. It includes the corresponding contact energies. In its Figure 5 force-controlled branch, the line remains at the perimeter. This does not prove that every noisy measured height and offset, imposed as exact constraints, lies on that admissible branch.
4. SolderShape fixes the line at the perimeter for every input. It must separately check plane penetration and whether local contact angles would require depinning. A stable Hessian alone does not supply either check.
5. Surface tension 0.4 N/m was fitted jointly to every experimental height and offset in Figures 4 to 7. Reproducing that curve is a code-consistency test. It does not independently validate the material scale. An inverse fit of a new gamma to three noisy geometry pairs can absorb geometry errors and damage the held-out prediction.

The frozen native-raster extraction is materially correct. The 144 micronewton experimental point has offset about 31 micrometers, including a lower error bar near 26 micrometers. The computed curve at the same force has offset about 14.1 micrometers. This outlier already disagrees visibly with the published best fit. It must remain visible. Two different heights and offsets at about 112 micronewtons cannot be uniquely paired from the raster.

## Source discrepancies and decisive probes

The archive model uses 4 micrometers at `force.fe` line 21. It uses gamma 0.45 N/m, volume 0.029 mm3, and active total mass 1.57 g. It is not a saved Figure 5 input. Its nearby commented total mass is 1.50 g. The `pev` script advances tilt in half-degree steps.

Under the explicit assumption that the experimental Figure 5 sequence uses tilts 0.5, 1.5, 2.5, 3.5, and 4.5 degrees, the observed loads imply total masses 1.483, 1.497, 1.500, 1.498, and 1.501 g. All expected shear loads for 1.50 g are within 0.2 micronewtons of the digitized centers. This suggests a normal load near 1.83 mN. It is an inference from a grid assumption, not recovered specimen metadata. The 1.95 mN value stated in the article applies explicitly to Figure 3. It must not be assigned to Figure 5 as fact.

The article's Figure 5 simulated height is about 34.4 to 34.7 micrometers. At a representative curve-like input of height 34.5 micrometers, offset 1.6 micrometers, and gamma 0.4 N/m, the unmodified public solver returned the following.

| Copper correction | Restoring shear, micronewtons | Upward normal reaction, micronewtons | Numerical check |
|---|---:|---:|---|
| 4 micrometers per pad | 18.3717 | 992.078 | refinement_checked |
| 5 micrometers per pad | 4.2323 | 7404.720 | refinement_checked |

At measured pair h3-x3, height 34.7 micrometers and offset 10.2 micrometers, changing only that correction gives the following.

| Copper correction | Restoring shear, micronewtons | Upward normal reaction, micronewtons | Numerical check |
|---|---:|---:|---|
| 4 micrometers per pad | 114.5640 | -194.470 | refinement_checked |
| 5 micrometers per pad | 36.3083 | 6878.092 | refinement_checked |

Four uncached public solver calls produced these values. The receipt and solver hashes are in `probe-summary.json`. These probes establish severe volume-reference sensitivity. They do not identify the article's exact curve inputs, and neither thickness may be selected merely because it fits an observation. A forward reproduction with declared normal load and the archive's full boundary conditions is the next discriminating test.

## Gotchas and corrections

The h4 central negative normal reaction rejects that exact geometry under an equal-volume, equal-load model. It does not reject every geometry within the plotted uncertainty or the original specimen with unknown volume and unequal local loads. Mean geometry and individual geometry must remain distinct.

The h6 inverse geometry exceeds the offset of the published computed branch by about 17 micrometers. Imposing it can require substrate wetting even though the published force-controlled curve remains pinned. Its detected plane intrusion is a physical admissibility failure, not a surface-tension calibration problem.

Preserve the frozen failed inverse comparison. Add a separately declared forward comparison against the digitized simulated curve first. Test 4 and 5 micrometer corrections, independently of experimental fitting. Compare both predicted height and predicted offset at declared compressive loads. Retain the inferred 1.50 g track as conditional until specimen metadata becomes available. After numerical consistency, compare experimental displacement intervals and preserve the h6 outlier.

Fix Root Causes changed the audit from adjusting gamma to checking reference planes, pad volume, load direction, and admissible boundaries. Explain the Number changed a source discrepancy into four public-solver probes with retained receipts. No product code or frozen validation evidence changed in this audit.
