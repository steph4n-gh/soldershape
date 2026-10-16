# Frozen physical comparison

General absolute physical accuracy remains inconclusive. This comparison separates generic-default error, calibration-dependent published consistency, and a low-force-calibrated held-out test. Missing specimen and material information prevents a general physical pass.

The primary source is [Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827), DOI `10.1115/1.1463732`, Figure 5. The measured joints remain pinned at circular pad perimeters.

The published flat-plane approximation uses measured interface separation as model gap and adds both 5 micrometer copper-pad slabs to solder volume. The literal rim mapping is a separate sensitivity. The uncorrected interface mapping is an intentionally wrong negative control.

Normal force is diagnostic only. Figure 5 has no specimen-specific normal-load table. The 1.95 mN value belongs to a different set. No force-ratio validation is reported.

## Central primary predictions

The observed shear center is the mean of the two readings of the same plotted load. Its bound is the union of their digitization intervals. Both alternative pairings at 112 micronewtons remain in the report.

| Pair | Phase | Observed shear µN | Numerical status | Shear at 0.48 N/m µN | Shear at published-fit 0.4 N/m µN | Held-out-calibrated shear µN |
|---|---|---:|---|---:|---:|---:|
| h1-x1 | calibration | 15.85 | refinement_checked | 8.1136 | 6.7613 | inconclusive |
| h2-x2 | calibration | 48.00 | refinement_checked | 47.8014 | 39.8345 | inconclusive |
| h3-x3 | calibration | 80.15 | not_converged | inconclusive | inconclusive | inconclusive |
| h6-x6 | held_out | 144.25 | engine_error | inconclusive | inconclusive | inconclusive |
| h4-x4 | held_out | 112.05 | refinement_checked | 175.7425 | 146.4521 | inconclusive |
| h5-x5 | held_out | 112.00 | engine_error | inconclusive | inconclusive | inconclusive |
| h4-x5 | held_out | 112.00 | refinement_checked | 111.5589 | 92.9658 | inconclusive |
| h5-x4 | held_out | 112.05 | engine_error | inconclusive | inconclusive | inconclusive |

The frozen low-force fit has status `inconclusive` and gamma `None` N/m. Only h1-x1, h2-x2, and h3-x3 enter this zero-intercept fit. No high-force row enters calibration.

The published 0.4 N/m value was fitted to all physical data in the paper. Its agreement is calibration-dependent consistency. The inherited 0.48 N/m default is generic and uncalibrated for this process.

## Held-out errors and sensitivity

Errors below use the single gamma fitted on the three low-force central rows. The eight corners vary the plotted height and offset bounds, digitization bounds, and solder volume by plus or minus 6 percent. Pad-slab volume stays fixed. These are nonstatistical sensitivities. No confidence coverage is claimed.

| Pair | Central error µN | Relative error % | Sampled geometry+volume extent µN | Observed interval overlap | Sensitivity status |
|---|---:|---:|---|---|---|
| h6-x6 | inconclusive | inconclusive | not run | None | not run |
| h4-x4 | inconclusive | inconclusive | not run | None | not run |
| h5-x5 | inconclusive | inconclusive | not run | None | not run |
| h4-x5 | inconclusive | inconclusive | not run | None | not run |
| h5-x4 | inconclusive | inconclusive | not run | None | not run |

The h1-x1 lower offset error bar is clipped. Its missing bound is not replaced with a fabricated zero or a symmetric guess. Its complete geometry sensitivity remains inconclusive. Geometry-only and volume-only samples are reported separately in predictions.json. The 1.5 percent increase in both measured coordinates is a separate systematic scenario. It is not added as an independent random error or combined with a second shrinkage correction.

## Coverage and limits

Aggregate errors use six specimens for each pairing assignment. The duplicate assignments are not pooled as four independent specimens. Complete paired results, all numerical failures, and each negative control remain in predictions.json and predictions.csv.

A sampled corner extent does not certify that the nonlinear function has no interior extremum. The calibration gamma's uncertainty is not propagated into the held-out extent. The low-force offset uncertainty is large. Same-process surface tension, individual ball volumes, specimen pairing, and molten geometry remain unidentified. Post-solidification geometry may differ from molten equilibrium.

Numerical convergence certifies the recorded local checks. It does not certify global minimum shape, physical pinning, or same-process material accuracy. Any failed corner makes that sensitivity result inconclusive. Any central failed calibration row prevents the held-out fit. The 144 micronewton point is retained.

## Reproduce

```sh
python3 tools/validate_physical.py --stage full --workers 2
```

The runner uses public solve calls. Receipts contain inputs, numerical levels, the mesh, model text, engine commands, stdout, stderr, and code and data hashes. Cache entries require the same physical input, solver code, model code, and engine binary. Use `--refresh` to repeat the computations. `--stage central` repeats only central mappings and the two-gamma scaling check.

Model the Domain changed each observation into one paired record with explicit uncertainty and pairing identity. Prove It Works changed validation into a public-solver replay with raw receipts. Explain the Number changed aggregate reporting into separate calibration, held-out, sensitivity, and numerical-status results.
