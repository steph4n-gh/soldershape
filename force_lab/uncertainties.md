# Force uncertainty and decision limits

These are proposed engineering acceptance gates for an outside-lab quotation. They are not measured performance or a physical-validation result. The lab must replace allocations with traceable evidence and complete covariance.

## Discriminate the actual endpoints

At the historical example inputs, the 120 µm lateral forces are approximately -92.263 and -82.193 µN for 5 and 7 nL. The signed contrast is approximately +10.070 µN. The 7 nL normal prediction is approximately +7.619 µN. Actual material and geometry measurements require new predictions.

| Quantity | Proposed expanded uncertainty or guard | Basis |
| --- | --- | --- |
| Individual corrected force | `U ≤ 2 µN` | Needed before testing the small upward signal |
| Measured lateral contrast | `U ≤ 3 µN` | Independent individual `U=2` values combine to about 2.828 µN |
| Combined predicted and measured lateral contrast | Guard at most one-third of the frozen contrast magnitude | Historical example allows about 3.357 µN |
| Combined absolute normal comparison | Guard at most 3 µN | Both predicted and observed signs must remain resolved |
| Initial relative hot gap and offset | `U ≤ 0.5 µm` each | Starting target, tightened by native sensitivity |
| Unmodeled pad tilt | Magnitude at most 0.1° | A 200 µm pad then spans about 0.349 µm in height |
| Coordinate drift during the fixed dwell | At most 0.5 µm | Starting limit, tightened by the force budget |

The frozen analysis propagates standard input and force source components. Its current protocol uses expanded `U=2u` only with independently justified coverage. A small specimen count does not automatically justify `k=2`. If the justified factor is larger, revise and register the protocol before confirmation. [NIST expanded uncertainty guidance](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-6-expanded-uncertainty).

Covariance also crosses the input and force budgets. Use one source ID, `source_unit` and standard uncertainty for the same physical source in both files. Signed coefficients convert that source unit into each input or force unit. The residual propagates measured force minus predicted force before squaring. Opposite sensitivities can amplify error; cancellation is also possible. The metadata must independently justify unlinked-source independence. A repeated ID with inconsistent unit or uncertainty is rejected.

Before freezing and during confirmation, require absolute actual hot-rim transverse displacement plus its expanded uncertainty at most 0.5 µm. Record both numbers in the supplied fields. Missing transverse observations or a failed bound block the endpoint. This limits an unmodeled direction by apparatus policy; it does not qualify the effect of nonzero transverse displacement physically.

With two independent measured uncertainties of 2 µN, the historical lateral budget leaves only about 1.808 µN for predicted-contrast uncertainty before numerical allowances. A 3 µN normal guard with a 2 µN measurement leaves about 2.236 µN for prediction uncertainty. These calculations show why excellent force resolution alone is insufficient.

## Replace the example allocation

The following standard uncertainties are planning allowances only. Every row needs a certificate, controlled observation, or defensible model at the assembled pad.

| Measurement source | Example standard allowance in µN | Required evidence |
| --- | ---: | --- |
| Assembled transfer calibration | 0.35 | Traceable both-sign calibration and held-out checks |
| Hot zero and blank interpolation | 0.35 | Heat and purge controls over the full dwell |
| Within-specimen repeatability | 0.25 | Raw stationary traces and a fixed filtering rule |
| Residual cross-axis and torque response | 0.30 | Applied cross loads and moments in both indexed configurations |
| Tare and parasitic correction | 0.25 | Equivalent load-path blanks and dead-load accounting |
| Compliance correction | 0.30 | Measured assembled stiffness and actual-rim metrology |
| Other quantified terms | 0.20 | Explicit complete inventory of remaining material effects |

If independent, these example terms give expanded uncertainty about 1.536 µN at `k=2`. This arithmetic is not evidence that the apparatus achieves that number. A missing or unknown term cannot become zero. Correlated terms need covariance, not independent quadrature.

Include force-axis registration, gravity, sensor temperature, attachment hysteresis, electrical noise, electrostatic force, convection, cable loads, blank interpolation, and drift where they affect the result. Preserve a common calibration or blank bias across all affected specimens. Repeated frames do not reduce a common bias by the square root of the frame count.

## Propagate model-input uncertainty separately

Use the native planning command to inspect local force sensitivities. The two rim diameters are separate inputs. Include gap, offset, liquid volume, surface tension, and density. Convert standard input uncertainty through the local Jacobian and retain signed covariance between specimens and volume arms.

The generated one-source limits spend the entire remaining prediction budget on one input. They are not simultaneous manufacturing tolerances. The lab must allocate the budget across all inputs and include numerical allowances. Shared optical scale, material properties, and volume-density conversion can change the contrast differently from independent specimen variation.

A finite-difference force change can be smaller than the recorded numerical refinement change. Such a derivative does not establish a usable input tolerance. The verified planning table returns a null inferred limit for unresolved changes, including the nearly zero lateral density sensitivity, while preserving the raw Jacobian and receipts. Do not interpret a huge reciprocal sensitivity as a feasible physical tolerance.

The fresh 120 µm planning run gives the following one-source-at-a-time expanded limits for the 7 nL normal endpoint, assuming a 2 µN force measurement and no other input source. Gap is about 0.621 µm. Liquid volume is about 0.0458 nL, or 0.65% of 7 nL. Lower and upper rim diameters are about 2.073 and 2.066 µm. An offset-only full-budget calculation would extrapolate beyond this protocol's 2% local-input domain, so its inferred limit is withheld. The same domain guard withholds implausibly large material allowances. These local numerical limits exclude extra numerical guards and must not be combined as a full set of allowed tolerances. The liquid-volume requirement is a significant lab feasibility question.

The planning run also tests two unmeasured input budgets. With expanded diameter, gap, and offset uncertainties of 0.5 µm, volume uncertainty 0.1 nL, and 1% surface-tension and density uncertainty, the 7 nL normal guard is about 5.644 µN. It fails the 3 µN gate. A tighter candidate uses 0.25 µm for both diameters and gap, 0.5 µm offset, and 0.02 nL volume, with the same material uncertainties. Its local normal guard is about 2.452 µN. Its lateral-contrast guard is about 2.888 µN. These calculations include the recorded local numerical guards. Geometry and volume are independent between specimens, material inputs are shared, and the calculation assumes no benefit from specimen averaging. Passing this numerical budget screen does not demonstrate achievable lab performance.

At the example density of 9 g/cm³, a 0.02 nL volume uncertainty corresponds to 0.18 µg of mass. The candidate XPR2U balance advertises 0.1 µg readability and typical repeatability of 0.15 µg. Two times that repeatability already exceeds 0.18 µg before density, transfer loss, or differencing two weighings. The lab must demonstrate a better complete volume method or report the difficult normal endpoint as inconclusive. The balance's display increment is insufficient evidence. [Mettler Toledo XPR2U specifications](https://www.mt.com/us/en/home/products/Laboratory_Weighing_Solutions/microbalances/XPR2U.html).

`input_covariance.json` expresses each independent uncertainty source once, with its standard uncertainty and signed coefficients on affected fields. `calibration.json` uses the same source-component method for corrected force. Replace the template's independent entries when sharing is known. Do not count the same effect both as a shared source and an independent source.

The freeze recomputes native central predictions and local sensitivities at the measured inputs. Scoring uses first-order covariance and adds numerical-refinement and one-at-a-time nonlinearity allowances as conservative decision guards. This local screen is not a validated coverage interval, a bound on model discrepancy, or proof of behavior across a multidimensional input region.

## Check the mechanical scales

A nominal 20 × 1 mm fused-silica stalk has a room-temperature beam stiffness estimate of about 1,335 N/m in bending. A 124 µN transverse load then deflects it about 0.093 µm. A 0.5 mm stalk is sixteen times more compliant. Neither estimate includes the sensor, attachment, bond, cap, or thermal gradients.

The bare 1 mm stalk weighs about 34.6 mg, or 339 µN. The complete moving assembly must meet supplier-approved axial, cross-load, and moment limits in both orientations. A uniform 200 K temperature rise expands a 20 mm stalk by about 1.88 µm using the cited room-temperature material values. Actual hot-rim feedback is required. The design's thermal isolation length is not a temperature certificate. [Heraeus fused-silica material reference](https://www.heraeus-covantics.com/brands/clear-fused-quartz).

At 124 µN, 0.5% uncorrected cross-axis leakage is about 0.620 µN. A 0.1° force-axis error leaks about 0.216 µN. The apparatus must quantify both effects at the pad. Advertised sensor noise and stage repeatability do not include them.

## Interpret the result within its domain

Agreement is conditional on observed pinned circular contact lines, stable equilibrium, held hot coordinates, independent material inputs, adequate calibration, and complete uncertainty. A numerical or scope failure blocks the physical endpoint. A failed measurement gate produces an inconclusive result.

The absence of a statistically resolved discrepancy does not prove zero model error. Agreement of isolated hot bridges does not establish package-level self-alignment, cooling stress, long-term reliability, wetting chemistry, reflow dynamics, or production yield. A PCB design decision becomes supportable only when its measured process domain and decision margin survive the qualified uncertainty and discrepancy evidence.
