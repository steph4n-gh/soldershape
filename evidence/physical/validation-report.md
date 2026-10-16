# Frozen physical comparison

General absolute physical accuracy remains inconclusive. Raw force residuals are conditional on the declared mappings. Unresolved numerical cases, substrate intrusion, calibration dependence, and missing specimen and material information prevent a physical pass.

The primary source is [Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827), DOI `10.1115/1.1463732`, Figure 5. The measured joints remain pinned at circular pad perimeters.

The published flat-plane approximation uses measured interface separation as model gap and adds both 5 micrometer copper-pad slabs to solder volume. The literal rim mapping is a separate sensitivity. The uncorrected interface mapping is an intentionally wrong negative control.

Normal-force magnitude is diagnostic only. Figure 5 has no specimen-specific normal-load table. The 1.95 mN value belongs to a different set. No force-ratio validation is reported. The known downward applied load does require an upward joint reaction; that sign supplies a separate physical diagnostic.

## Central primary predictions

The observed shear center is the mean of the two readings of the same plotted load. Its bound is the union of their digitization intervals. Both alternative pairings at 112 micronewtons remain in the report.

| Pair | Phase | Observed shear µN | Numerical status | Shear at 0.48 N/m µN | Shear at published-fit 0.4 N/m µN | Held-out-calibrated shear µN |
|---|---|---:|---|---:|---:|---:|
| h1-x1 | calibration | 15.85 | refinement_checked | 8.1136 | 6.7613 | 11.2948 |
| h2-x2 | calibration | 48.00 | refinement_checked | 47.8015 | 39.8346 | 66.5439 |
| h3-x3 | calibration | 80.15 | refinement_checked | 43.5700 | 36.3083 | 60.6533 |
| h6-x6 | held_out | 144.25 | refinement_checked | 218.3267 | 181.9389 | 303.9305 |
| h4-x4 | held_out | 112.05 | refinement_checked | 175.7425 | 146.4521 | 244.6494 |
| h5-x5 | held_out | 112.00 | engine_error | inconclusive | inconclusive | inconclusive |
| h4-x5 | held_out | 112.00 | refinement_checked | 111.5589 | 92.9658 | 155.3001 |
| h5-x4 | held_out | 112.05 | engine_error | inconclusive | inconclusive | inconclusive |

The frozen low-force fit has status `fitted_on_calibration_only` and gamma `0.6682032821135863` N/m. Only h1-x1, h2-x2, and h3-x3 enter this zero-intercept fit. No high-force row enters calibration.

The published 0.4 N/m value was fitted to all physical data in the paper. Its agreement is calibration-dependent consistency. The inherited 0.48 N/m default is generic and uncalibrated for this process.

| Duplicate pairing | Material track | Available-row MAE µN | Available-row RMSE µN | Held-out MAE µN | Held-out RMSE µN | Scored central rows |
|---|---|---:|---:|---:|---:|---:|
| duplicate_pairing_1 | prior_default | 36.4568 | 46.7805 | 68.8846 | 69.0800 | 5/6 |
| duplicate_pairing_1 | published_fit | 26.6374 | 30.5788 | 36.0455 | 36.0829 | 5/6 |
| duplicate_pairing_1 | held_out | 66.9751 | 93.6218 | 146.1399 | 146.7659 | 5/6 |
| duplicate_pairing_2 | prior_default | 23.8066 | 37.1094 | 37.2589 | 52.3811 | 5/6 |
| duplicate_pairing_2 | published_fit | 23.5638 | 27.7638 | 28.3616 | 29.8560 | 5/6 |
| duplicate_pairing_2 | held_out | 49.1153 | 74.9900 | 101.4903 | 116.9888 | 5/6 |

Incomplete aggregate metrics describe only the scored subset. They do not establish agreement for the missing specimens.

## Held-out errors and sensitivity

Errors below use the single gamma fitted on the three low-force central rows. The eight corners vary the plotted height and offset bounds, digitization bounds, and solder volume by plus or minus 6 percent. Pad-slab volume stays fixed. These are nonstatistical sensitivities. No confidence coverage is claimed.

| Pair | Central error µN | Relative error % | Sampled geometry+volume extent µN | Observed interval overlap | Sensitivity status |
|---|---:|---:|---|---|---|
| h6-x6 | 159.6805 | 110.6970 | [212.4869, 417.2286] | None | inconclusive |
| h4-x4 | 132.5994 | 118.3395 | [63.8868, 411.7264] | None | inconclusive |
| h5-x5 | inconclusive | inconclusive | [16.5133, 218.9703] | None | inconclusive |
| h4-x5 | 43.3001 | 38.6608 | [76.8313, 228.685] | None | inconclusive |
| h5-x4 | inconclusive | inconclusive | [14.055, 399.4104] | None | inconclusive |

The h1-x1 lower offset error bar is clipped. Its missing bound is not replaced with a fabricated zero or a symmetric guess. Its complete geometry sensitivity remains inconclusive. Geometry-only and volume-only samples are reported separately in predictions.json. The 1.5 percent increase in both measured coordinates is a separate systematic scenario. It is not added as an independent random error or combined with a second shrinkage correction.

## Normal-load direction

Independent review identified this diagnostic after the frozen predictions. It changes no inputs, fitted parameters, or prespecified score. The weighted upper wafer applies a downward normal load, so the reaction on the upper pad must point upward. Every positive surface tension preserves the modeled force direction. At the central measured geometries, h4-x4 and h4-x5 predict downward reactions of 5675.29 and 6084.38 micronewtons at 1 N/m. Both are incompatible with that known load direction under the paper's equal per-joint interpretation. The conclusion holds under either duplicate pairing. It does not reject every uncertain geometry or volume. Missing normal-load magnitudes still prevent a force-magnitude or force-ratio score.

## Flat substrate constraints

The current model fixes the circular rims but does not constrain every side-surface vertex between the two solid planes. A numerically stable shape can therefore enter a solid substrate. Detected intrusion makes a physical comparison inconclusive under the paper's flat-substrate approximation. The raw conditional force residual is retained.

| Pair | Sampled plane status | Lower excursion µm | Upper excursion µm |
|---|---|---:|---:|
| h1-x1 | no_sampled_vertex_violation_detected | 0.0000 | 0.0000 |
| h2-x2 | no_sampled_vertex_violation_detected | 0.0000 | 0.0000 |
| h3-x3 | no_sampled_vertex_violation_detected | 0.0000 | 0.0000 |
| h6-x6 | violates_flat_substrate_planes | 0.2671 | 0.2671 |
| h4-x4 | no_sampled_vertex_violation_detected | 0.0000 | 0.0000 |
| h5-x5 | unavailable | inconclusive | inconclusive |
| h4-x5 | no_sampled_vertex_violation_detected | 0.0000 | 0.0000 |
| h5-x4 | unavailable | inconclusive | inconclusive |

The plane check uses a 1e-9 mm arithmetic tolerance. This is not a physical acceptance tolerance. It examines exported vertices and can detect intrusion. Absence of a sampled violation does not prove the continuous curved surface is admissible. Radial positions and example violating coordinates are stored with each result. No normal-force accuracy is inferred from local stability.

## Coverage and limits

Central numerical statuses are `{"engine_error": 15, "not_converged": 1, "refinement_checked": 8}`. Sensitivity numerical statuses are `{"engine_error": 38, "not_converged": 2, "refinement_checked": 68}`. The two-gamma public-solver check has status `numerically_checked`.

Aggregate errors use six specimens for each pairing assignment. The duplicate assignments are not pooled as four independent specimens. Complete paired results, all numerical failures, and each negative control remain in predictions.json and predictions.csv.

A sampled corner extent does not certify that the nonlinear function has no interior extremum. The calibration gamma's uncertainty is not propagated into the held-out extent. The low-force offset uncertainty is large. Same-process surface tension, individual ball volumes, specimen pairing, and molten geometry remain unidentified. Post-solidification geometry may differ from molten equilibrium.

Numerical convergence certifies the recorded local checks. It does not certify global minimum shape, solid-plane admissibility, physical pinning, or same-process material accuracy. A failed or substrate-intruding corner makes that sensitivity result inconclusive. A central failed calibration row prevents the held-out fit. The 144 micronewton point is retained.

## Reproduce

```sh
python3 tools/validate_physical.py --stage full --workers 2
```

The runner uses public solve calls. Receipts contain inputs, numerical levels, the mesh, model text, engine commands, stdout, stderr, and code and data hashes. Cache entries require the same physical input, solver code, model code, and engine binary. Use `--refresh` to repeat the computations. `--stage central` repeats only central mappings and the two-gamma scaling check.

The pre-repair comparison remains in prediction-receipts/baseline-predictions.json and baseline-validation-report.md. Its numerical failures are preserved. Early primary-case receipts retain the failed engine output.

Model the Domain changed each observation into one paired record with explicit uncertainty and pairing identity. Prove It Works changed validation into a public-solver replay with raw receipts. Explain the Number changed aggregate reporting into separate calibration, held-out, sensitivity, and numerical-status results.
