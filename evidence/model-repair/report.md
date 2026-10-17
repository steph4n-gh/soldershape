# Physical model repair and PCB design verdict

SolderShape can support conditional standoff screening and the design of a physical coupon test. It cannot yet approve a PCB land pattern or predict self-alignment forces with qualified process accuracy. For aligned, lightly loaded circular joints, the paper's simple load-corrected analytical calculation is as useful as the full native solver in the tested regime. A Rust or WASM optimizer port has not earned its complexity.

This investigation starts from `dccbcf6` and preserves the earlier frozen inverse-force study. The new independent extraction and protocol were frozen before the new public load solver was scored. In the independent four-specimen campaign, no measured height enters a forward request or optimizer seed. No gamma was fitted to the new observations.

## The earlier failure was not a force-sign bug

Three identical-input comparisons with the original NIST implementation agree within 0.012% per force component. The negative normal reaction in one central geometry and the substrate-plane intrusion in the high-offset geometry also occur upstream. An independent axisymmetric area/volume minimizer agrees with the fixed-gap native reaction within 0.035% on an ordinary bridge and within 0.020% on a thin bridge. Its 24, 48 and 96 segment refinements and full native numerical diagnostics are retained. These are numerical checks, not physical validation.

The published experiment and archived defaults do not identify one exact baseline. [Josell et al. 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) state 5 µm pad thickness; the downloadable NIST example uses 4 µm. The original search script also has a 60 µm lower height floor, which excludes Figure 5 heights near 35 µm until adapted. These are documented case differences. We did not silently replace the paper's pad thickness with a value that fits better.

The inverse force calculation is extremely sensitive to geometry. Changing each pad slab from 5 to 4 µm at one declared height and offset changes predicted normal reaction by 6.41 mN. The paper's digitized mean height and offset, nominal solid-ball volume, and unknown specimen-specific normal load do not identify liquid geometry sufficiently for a clean inverse force test. Evaluating a nonlinear force at mean geometry also need not equal the mean force. Fitting gamma to uncertain inverse geometries amplified the earlier discrepancy. Those original results remain in `evidence/physical`, without a revised fit or relaxed gate.

The isolated pinned surface can intrude past a substrate plane at a forced displacement. The model has no substrate-contact or contact-line motion law. Such geometries are outside a justified PCB interpretation even when the numerical surface is locally stable. Shared diagnostics now reach all solver callers. Loaded solutions with a detected excursion fail rather than receive an accepted mesh.

## The physical discrepancy still matters

The original pinned NIST model was also run forward under an explicitly inferred common load, using the archived 1.5 g mass and the measured-force series' tilt pattern. That load is plausible, not verified specimen metadata. At approximately 144.17 µN lateral and 1831.84 µN normal load, it predicts:

| Pad slab approximation | Interface gap, µm | Offset, µm |
| --- | ---: | ---: |
| Two 4 µm slabs | 34.323 | 13.604 |
| Two 5 µm slabs | 36.249 | 14.454 |

Both native solutions pass the recorded refinement, volume, Hessian and sampled-plane checks. The measured final offset is 31 µm with a reported span of 26.1 to 36.1 µm. The published computed curve is itself near 14 µm. Correct conditioning removes the forced-shape intrusion but does not make the high-offset measurement agree. Two original free-contact control runs failed, one by timeout and one by collapse. They remain in the raw receipts.

This establishes a limit rather than a new contact model. The source does not provide enough specimen and process information to decide whether wetting, liquid-volume change, load redistribution, solidification, or another omitted effect causes the remaining miss. It does not justify claiming validated alignment force, settling time, assembly yield, or fatigue life.

## The implemented model repair

The product now has two distinct physical requests. A prescribed-gap request retains its old meaning. A supported-load request contains no height. Native optimization varies the upper plane and surface together under the downward per-joint load. The start comes from diameters and volume only. Every accepted height receives a fresh fixed-gap solve that independently checks the upward reaction. Reported geometry and forces come from that second solve.

The native default derivative delta produced a plausible height with a wrong balance residual. A scale-aware delta and an independent reaction check fix this demonstrated numerical gap. More initial gradient relaxation fixes a transient indefinite Hessian in the offset start. No warning or acceptance threshold was weakened. Eleven derivative/initialization perturbations passed. Half and double geometry, zero-load spherical agreement, default gravity, an additional gamma/load scaling control, and a rejected unattainable load have separate numerical receipts.

Input hashes still identify the actual request. `equilibrium` stores the accepted computed gap. Failed loaded requests preserve evidence without inventing height, forces, or mesh. Native height and independent static model/commands/logs are separate ZIP members. Replay solves height again from validated inputs and does not execute archived command text. A real seven-row loaded archive exposed a size-limit mismatch; the uncompressed reader bound was raised from 120 to 160 MB after measuring its 128.52 MB size. The 40 MB compressed and 100-member limits remain.

## Independent measured geometry

[Van Veen, Vandevelde and Beyne 2004, Table 3](https://imapsjmep.org/article/39820.pdf) report four physical CSP standoffs with 280 µm upper pads, substrate pads from 170 to 320 µm, total solder volume 0.01745 mm³ and an approximate 4 µN load per joint. These are post-reflow cross-sections, not in-situ liquid shapes. Flux, temperature, exact liquid volume, offsets for three rows, and measurement uncertainty are missing.

The primary replay follows the paper's effective-volume approximation. Add ONE substrate copper cylinder of thickness 34 µm to volume and subtract 34 µm from solved effective height. This does not represent liquid solder inside actual copper. It is not silently applied to ordinary user designs. A literal-rim interpretation is a separate control, not combined with this correction.

All lengths in the following table are µm. Gamma is assumed 0.48 N/m, gravity is disabled and offset is assumed zero. Material stress runs at 0.35, 0.4 and 0.55 N/m are not measured confidence intervals.

| Substrate pad diameter | Measured rim height | Native load-balanced height | Prediction minus measurement | Unloaded sphere |
| --- | ---: | ---: | ---: | ---: |
| 170 | 204 | 211.112 | +7.112 | 212.447 |
| 220 | 198 | 201.774 | +3.774 | 202.790 |
| 270 | 192 | 190.681 | -1.319 | 191.461 |
| 320 | 177 | 178.404 | +1.404 | 179.011 |

All 16 primary material scenarios passed the unchanged numerical gates and independent load check. All 31 runs including mapping, gravity, offset and volume controls passed. The largest absolute reaction residual was 0.001082 µN. This is a numerical result, not a physical precision claim.

The nominal mean absolute height discrepancy is 3.402 µm, compared with 3.947 µm for the unloaded sphere. Both predict the full measured pad-diameter ordering. Native q270 minus q320 is 12.276 µm; the measured difference is 15 µm. The reported approximate 60 µm q170 offset lowers the separate prediction from 211.112 to 208.176 µm against measured 204 µm. It is retained alongside the aligned result, not substituted into the primary score. The publication's offset-specific native value is 205 µm, which this approximate-offset replay also does not reproduce. That residual remains unresolved.

The literal-rim control produces 239.451, 226.217, 210.266 and 192.367 µm. The material scenarios move primary heights by less than 0.66 µm across the declared range. Gravity at assumed density 9 g/cm³ lowers nominal heights by 0.12 to 0.34 µm. Neither adjustment explains all physical discrepancies. Geometry mapping and unknown process inputs dominate this comparison.

The strongest simple comparator is the paper's Eq. 9 axial spring correction around the unloaded sphere. Independent primary-source review calculates 211.220, 201.801, 190.685 and 178.408 µm at the same gamma and load. These differ from the native results by at most 0.109 µm. The independent loaded formula has a 3.436 µm nominal mean absolute discrepancy, essentially the native value of 3.402 µm. The formula therefore answers this aligned low-load design question without a general surface optimizer. The paper's own rounded analytical loaded column has a 2.825 µm mean absolute discrepancy, smaller than our native nominal discrepancy. We have not demonstrated superior physical accuracy over the analytical method.

## A useful PCB decision, with its stop condition

Consider this declared design requirement for the published assembly: at least 185 µm rim clearance. Nominally q270 predicts 190.681 µm and q320 predicts 178.404 µm. The corresponding measured heights are 192 and 177 µm. This supports screening the larger pad out of the nominal clearance design.

A nominal q270 choice is fragile under the declared solder-volume stress. These are three tested volume points per design, not a continuous tolerance proof and not a measured process distribution.

| Substrate pad | Height at −5% solder volume | Nominal height | Height at +5% solder volume | Interpretation for 185 µm clearance |
| --- | ---: | ---: | ---: | --- |
| 220 µm | 195.378 | 201.774 | 207.956 | Best tested candidate for a coupon |
| 270 µm | 184.352 | 190.681 | 196.811 | Nominal pass reverses at low volume |
| 320 µm | 172.215 | 178.404 | 184.417 | All three tested points fall below the requirement |

The unloaded sphere alone gives 185.094 µm at q270 low volume and 185.057 µm at q320 high volume. It would label those marginal points differently. The properly load-corrected analytical baseline gives 184.355 and 184.422 µm and agrees with the native decisions. These submicrometer distinctions are much smaller than the observed physical discrepancies. They cannot establish manufacturing safety.

Select q220 for the next physical coupon experiment under these assumptions. Do not release a board on this evidence alone. The source supplies no process uncertainty with which to qualify its 10.378 µm low-volume clearance margin. The volume, offset, pinning and copper geometry assumptions can change a prediction. Missing uncertainty is not a zero-error bound, and the model correction cannot be inferred from an imported copper footprint alone.

The next decisive evidence is a same-process coupon comparing q220 and q270 at measured deposited solder volumes and actual pad dimensions. Record alloy, flux, reflow temperature, pad sidewall wetting, package tilt, per-joint load assumptions and repeated post-reflow gap measurements. Predeclare the clearance and acceptable prediction-error budget. Keep separate specimens for fitting material parameters and checking predictions. A reliable force claim additionally needs measured displacement/load with identified specimen inputs. Until then, stop expanding physical accuracy claims and do not build a thermal or wetting simulator to explain an unidentified residual.

## Reproduce the evidence

From the repository root:

```sh
python3 tools/setup_engine.py
python3 -m unittest discover -s tests -v
python3 tools/verify.py
python3 tools/validate_loaded.py
python3 tools/validate_loaded.py --refresh
python3 tools/check_loaded_formula.py
python3 tools/verify_loaded_archive.py
python3 evidence/model-repair/upstream-replay.py
python3 -m soldershape solve-case examples/loaded-volume.soldershape.json --output output/loaded-volume.zip
python3 -m soldershape replay output/loaded-volume.zip
python3 -m soldershape serve
```

The first loaded validation command reads identity-matched tracked receipts when available. `--refresh` recomputes all 31 native cases. The independent axisymmetric research check requires NumPy and SciPy; it is not a product dependency. Run `python3 tools/check_capillary_baseline.py` in an environment containing those libraries. The retained run used SciPy 1.17.1.

`source-audit`, `upstream-diagnosis`, `independent-evidence`, `load-solver`, `loaded-physical-results`, `product-review` and `science-review` retain source hashes, inputs, numeric results, alternatives and limits. `loaded-receipts/` and `upstream-receipts.json.gz` preserve full native receipts. `forward-protocol.md` preserves the preprediction criteria. Older negative reports remain unchanged.
