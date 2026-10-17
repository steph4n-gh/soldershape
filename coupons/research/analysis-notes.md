# Prospective coupon analysis

The data shapes keep incoming measurements, frozen predictions and confirmatory outcomes in separate files. `inputs.csv` contains all 24 allocated confirmatory cap IDs. Each row records the clean bare-cap mass, the mass of its twenty clean solder spheres, actual mean lower and upper pad diameters, both finished metal thicknesses and the pre-outcome placement offset. Each quantity has its measured expanded uncertainty. One evidence reference can identify the corresponding calibrated measurement report. `metadata.json` records the alloy, flux, frozen profile, molten temperature, liquid density, surface tension and their sources. `hot_method_evidence` cites the separately qualified molten-state measurement method. It may remain null for a cold-only experiment. Blank cells and JSON null mean missing information. They are never material defaults.

`outcomes.csv` records cap-level post-reflow measurements. An optional second row for the same cap can record `phase=molten`. The twenty joints are dependent measurements within one cap. Their mean, minimum and maximum must come from the stated measurement coverage. A whole-cap minimum requires `full_volume_3d=true` and `joints_measured=20`. A partial section cannot establish that minimum. `defects=none` means that the lab inspected and found none. A blank defect entry is not equivalent.

`wetted_joints` records how many joints the lab observed wetting both opposing pad interfaces. It is blank when unobserved. A numeric count requires a `wetting_evidence` reference. `wetting_boundary_status` has three possible values. `matches_frozen` records observed wetting and contact-line boundaries consistent with the frozen model at all twenty joints. `fails` records an observed boundary mismatch. `unobserved` records that the contact-line boundary has not been established. Both observed statuses require evidence. A claimed match requires twenty observed wetted joints. Absence of a defect flag never proves wetting or pinning.

The gap-range gate includes uncertainty. With blank `range_U_um`, the guarded range is `max_gap_um - min_gap_um + min_gap_U_um + max_gap_U_um`. The lab may instead supply `range_U_um` with its correlated uncertainty calculation in `range_uncertainty_evidence`. A supplied budget without that evidence is rejected. The guarded range must be at most 3 micrometers. The script never invents independent minimum and maximum errors.

The optional `pair_difference_U_um` field records a lab-calculated expanded uncertainty for that pair's mean-gap difference. Both cap rows in a pair must repeat that value and cite its uncertainty budget in `pair_uncertainty_evidence`. Otherwise the script conservatively sums the two cap uncertainties. It never assumes independence or divides uncertainty by the square root of twenty. Pair uncertainty must meet the declared 3 micrometer gate.

The script reads the 24 confirmatory rows from `allocation.csv` using `role=confirmatory`. It verifies twelve within-run C220/C270 pairs across three runs. It verifies that the incoming pad diameters and their uncertainties remain within the declared target tolerance. Pilot qualification must be true and cite evidence before freezing. This is an operator attestation of the separate pilot requirements. The script does not independently interpret the lab's pilot report.

The frozen temperature interval is `temperature_C +/- temperature_U_C`. Its lower endpoint must be strictly above the Sn63Pb37 liquidus of 183 degrees C recorded in the experiment specification. The observed molten temperature interval must lie wholly inside that frozen interval and remain strictly above the liquidus. Merely overlapping the intervals is insufficient. Cold measurements use the same containment rule against 20 +/- 2 degrees C. Every uncertainty is an expanded uncertainty at coverage factor two. These interval guards assume no statistical independence. A missing hot-method reference prevents hot clearance, paired process direction and model verdicts while the cold workflow remains usable.

## Frozen calculations

For twenty spheres of total mass in milligrams, the liquid volume per joint in cubic millimeters is `solder_kit_mass_mg / 20 / liquid_density_g_cm3`. The numerical units match because one gram per cubic centimeter equals one milligram per cubic millimeter. The external normal load per joint in micronewtons is `clean_bare_cap_mass_mg * 9.80665 / 20`. Solder weight is excluded from this external load.

The primary literal-rim model uses that solder volume and predicts the distance between the opposing finished pad faces. The secondary two-pad-cylinder approximation adds both measured pad-cylinder volumes before solving, then subtracts both finished metal thicknesses from its calculated plane separation. Both hypotheses are fixed prospectively. Their numerical agreement with outcomes is reported separately. The pilot cannot select whichever hypothesis fits better.

Both models omit solder gravity as declared. A separate literal-rim calculation includes solder gravity. The secondary geometry does not receive a gravity correction for fictitious liquid inside the upper copper pad. Every distinct native request is solved and retained as a compressed receipt. A failed solve remains failed. The independent Eq. 9 analytical result never replaces a failed native result.

The Eq. 9 comparison uses the aligned, small-load formula from [Van Veen et al. 2004](https://imapsjmep.org/article/39820.pdf). It omits offset and gravity. One-at-a-time shifts of measured cap mass, sphere-kit mass, pad diameters, liquid density and surface tension form an analytical sensitivity screen. Their summed magnitude is not a native prediction interval. It omits interaction terms, correlations, offset and copper-mapping uncertainty. Central native agreement does not qualify those uncertainties.

The completed freeze preserves literal inputs and metadata, experiment and allocation copies, native receipts, predictions, SHA-256 hashes of those files, model and solver source hashes, engine provenance, and its UTC completion time. It rejects changes to code, specification or allocation during freezing. The score command verifies those hashes and rejects current specification, allocation or prediction-code changes. Confirmatory outcome timestamps must follow the completed freeze. Timestamp checks and hashes document the declared sequence. They do not prove that an operator never viewed outcomes.

## Decisions and limits

The 185 micrometer clearance assessment uses the observed whole-cap minimum and its expanded uncertainty. A cap is above the guard band only when `observed_minimum - U >= 185`. It is below the guard band when `observed_minimum + U < 185`. All other cases remain inconclusive. Defects and geometry-gate failures remain visible in each attempted cap's record. They are not silently excluded from the attempted count.

The comparative direction uses cap-level paired mean gaps, with four pairs per run. All three run means must have the same guarded sign. Each run's uncertainty uses the mean of its pair budgets conservatively, without assuming independent errors. Missing caps, defects, incomplete coverage, unobserved or incomplete wetting, excessive offset, excessive guarded gap variation or failed metrology gates prevent a complete direction verdict. An observed or unestablished contact-line boundary can leave the empirical process comparison usable when all twenty joints are observed wetted. The report retains each run's effect and each missing or failed attempt. It supplies no population confidence interval or production yield estimate.

Absolute central-model comparison requires qualified molten-state measurements, full coverage, at most 2 micrometers expanded gap uncertainty, twenty observed wetted joints, observed contact-line boundaries that match the frozen model, no observed defects, at most 25 micrometers offset including uncertainty, at most 3 micrometers guarded gap range and the recorded temperature gate. The frozen and observed offset uncertainty intervals must also overlap. The freely settling cap is not a simulated lateral-force balance. Offset drift or a boundary mismatch can make model comparison inconclusive while the observed cold clearance remains usable. Final measured offsets never become replacement prediction inputs.

The five micrometer height budget has three outcomes. Central prediction and measurement are consistent when absolute discrepancy plus measurement uncertainty fits inside the budget. They disagree when discrepancy minus measurement uncertainty exceeds the budget. Otherwise the result is inconclusive. These are conditional statements at the frozen inputs. Input uncertainty has not been propagated through the native solver. Cold agreement alone always leaves the liquid-model verdict inconclusive. Molten agreement does not establish lateral self-alignment dynamics, load sharing, yield or fatigue reliability.

## Executable checks

Run these commands from the repository root. Use a new output directory for each planning or frozen run.

```sh
python3 -m unittest discover -s coupons/tests -v
python3 coupons/tools/analyze.py templates --output output/lab-worksheets
python3 tools/setup_engine.py
python3 coupons/tools/analyze.py plan --output output/coupon-planning
python3 coupons/tools/analyze.py freeze --inputs output/lab-worksheets/inputs.csv --metadata output/lab-worksheets/metadata.json --output output/coupon-freeze
python3 coupons/tools/analyze.py score --freeze output/coupon-freeze --outcomes output/lab-worksheets/outcomes.csv --output output/coupon-score.json
```

The freeze command intentionally rejects the blank worksheets. Fill them from incoming metrology and the qualified pilot before running it. Preserve the frozen directory before collecting confirmatory outcomes. The templates contain no physical observations.

Twenty-one synthetic tests passed after the independent science review. They cover guarded positive direction, a twenty micrometer negative discrepancy, cold-only inconclusiveness, missing and failed attempts, duplicate and unknown IDs, outcome leakage into inputs, input tampering, absent uncertainty, partial-section minima, offset drift and failed native computation. The review repairs add explicit wetting observations, boundary mismatches, missing hot-method qualification, uncertainty-expanded range failures, a cited correlated range budget, and frozen or observed temperature intervals that cannot qualify a molten measurement. Test doubles are labeled synthetic. They are not experimental data.

A separate actual native planning run completed all six requests with refinement checks and independent load balance. At the explicit planning assumptions, the C220 literal and two-pad predictions were 223.3188 and 178.2034 micrometers. C270 gave 207.5218 and 167.3139 micrometers. Literal-rim gravity sensitivity gave 223.1293 and 207.3995 micrometers. The largest gravity-off native versus analytical discrepancy was 0.0464 micrometers. These are numerical planning results. They expose a large geometry-hypothesis difference and do not promise an 185 micrometer physical clearance pass.

Model the Domain kept the inputs, prediction freeze and outcome phases distinct. Prove It Works required the six actual native planning requests and the negative scoring controls. Occam's Razor kept this analysis in one standard-library script and reused the existing solver.
