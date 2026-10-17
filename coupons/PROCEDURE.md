# Run the 220 versus 270 micrometer pad comparison

Run experiment `SS-C220-C270-R1` under the controlled [experiment.json](experiment.json) revision. This procedure is for an outside assembly and measurement laboratory. It does not assume equipment owned by the requester. Read [PROCUREMENT.md](PROCUREMENT.md) and obtain written DFM, material, assembly, and metrology acceptance before fabrication release.

## Establish the comparison and its limits

Compare the cooled pad-face gap produced by two lower pad diameters. Arm C220 has 220 micrometer lower pads. Arm C270 has 270 micrometer lower pads. Both arms use the same twenty-pad cap, material lots, finish, flux, sphere grade, and process. Each cap is an experimental unit. Adjacent C220 and C270 caps form a pair. Each reflow run is a shared block.

The primary practical outcome is the post-reflow gap between opposing finished pad top faces at 20 plus or minus 2 degrees Celsius. Record the cap mean, minimum, and maximum across all twenty pad pairs. Record mask-to-cap underbody clearance separately. The declared 185 micrometer threshold applies only to the pad-face gap. It is not a product-specific underbody requirement.

Keep cooled clearance evidence separate from liquid-model accuracy. For absolute liquid prediction, obtain held-out hot-state measurements or justify a thermal transformation independently. Do not infer a molten gap by fitting shrinkage to the held-out cooled heights.

## Preserve identities and the allocation

1. Archive the supplied package and its manifest before work. Record the accepted experiment revision.
2. Assign the printed carrier identity, site identity, cap identity, and sphere-kit identity from [allocation.csv](allocation.csv).
3. Preserve the seed 220270 allocation. Use its carrier rotation and placement order. Each confirmation run contains one carrier at 0 degrees and one at 90 degrees. Record actual oven position and loading order before each run. This balances an external oven-frame diagonal effect. Arm identity remains tied to a carrier-site diagonal, so a fabrication effect specific to those sites remains a limitation.
4. Keep profile, pilot, confirmation, and spare identities separate. Do not move a pilot cap into confirmation.
5. Select the destructive specimens before examining outcome heights. Select one cap from each arm in each pilot run and each confirmation run. Record their IDs before measurement.
6. Give the measurement analyst coded specimen IDs without prediction values. Retain the allocation key with a separate coordinator. Record that pad geometry may reveal the arm in images.

Use three pilot carriers in separate runs P1 through P3. These supply twelve caps and six pairs. Use six confirmation carriers in separate runs R1 through R3, two carriers per run. These supply twenty-four attempted caps and twelve pairs, with four pairs per run. One carrier with four caps is dedicated to profiling. Two carriers and eight caps are spares. A replacement requires its reason and timing in the deviation log. Preserve the original failed attempt.

## Measure the incoming physical inputs

1. Inspect final CAM and routed dimensions. Verify the array counts, circular pad diameters, full mask openings, absence of exposed traces, and at least 0.2 mm finished cap pad-copper clearance to the routed edge.
2. Identify the actual laminate grade, layer stackup, finish process, and fabrication lot. Record actual carrier and cap thicknesses.
3. Measure pad diameter, roundness, top-surface height, mask height, roughness, and flatness on representative sites of each arm and cap lot. Record site coverage and within-site variation. Reject an input summary that hides variation beyond its uncertainty.
4. Measure the finished lower and upper metal heights separately. Include copper, nickel, and gold in the finished height. Retain constituent measurements when available. Nominal 35 micrometer copper excludes ENIG.
5. Weigh every clean, singulated bare cap, including finish and permanent identification. Exclude solder and flux. Record calibration, tare, repeatability, temperature, expanded uncertainty, and raw readings.
6. Screen every accepted sphere to 317.5 through 322.5 micrometers. Demonstrate expanded diameter uncertainty at or below 1 micrometer. Require measured diameter minus its expanded uncertainty to be at least 317.5 micrometers and diameter plus its expanded uncertainty to be at most 322.5 micrometers. Preserve individual measurements, sphericity, screening temperature, and the common-lot distribution.
7. Weigh each clean twenty-sphere kit as metal only. Preserve kit tare, net mass, expanded uncertainty, and the identities of its twenty spheres.
8. Record alloy and flux certificates, lots, expiry, storage, and handling. Define the liquid-density and surface-tension sources and their uncertainty before outcomes. The complete frozen temperature interval must be above the 183 degree Celsius Sn63Pb37 liquidus.

Measure input uncertainties rather than copying instrument resolution. Choose balance capability so propagated cap-load and liquid-volume uncertainty fit the declared 5 micrometer height-error budget. If the available balance or material-density source cannot meet that budget, stop model scoring or revise the method before confirmation.

Record the temperature of every incoming dimensional measurement. For a molten prediction, declare the thermal expansion treatment for pad diameters, metal heights, and laminate geometry between that temperature and the liquid plateau. Cite the material data and propagate its uncertainty. Keep an uncorrected geometry calculation as a labeled sensitivity if expansion data are insufficient. Do not infer the expansion correction from held-out heights.

Use `Fjoint_uN = bare_cap_mass_mg * 9.80665 / 20`. This is the equal-load approximation for a freely supported cap. Do not add sphere mass to this external cap load. Solder body gravity is a separate model term. Record flux dose and any residue mass that may affect load. Quantify those effects or mark the load assumption ineligible.

Use `Vliquid_mm3 = twenty_ball_kit_mass_mg / (20 * liquid_density_g_cm3)` at the measured liquid plateau. Use a temperature-dependent density relation for the actual alloy. Record its applicable range, exact source, temperature, and uncertainty. The paper's 0.01745 cubic millimeter input and a solid-state density default do not identify this kit's liquid volume.

Kit mass identifies an average volume. It does not prove equal volume at every joint. Propagate the screened sphere distribution into a sensitivity bound. Preserve individual sphere-to-joint placement when the handling method permits it.

## Demonstrate the assembly process on the pilot

1. Use the dedicated profile carrier and caps to develop the proposed single-cycle SnPb profile. Record thermocouple locations, calibration, actual trace, atmosphere, ramp, time above liquidus, peak, and liquid plateau stability.
2. Keep thermocouples and contact measurement fixtures off scored caps. Instrumented profile assemblies never enter the scored cohorts.
3. Apply a controlled amount of the accepted flux. Place one accepted sphere at each of twenty joints. Add no solder paste.
4. Place caps using the frozen order. Keep F.SilkS outward and B.Cu mating downward. Align the L mark on the cap outer face with the carrier A1 corner. The rectangular five-column, four-row grid must match the carrier grid before rotating the complete carrier. A 90-degree cap rotation relative to its site is invalid. Measure the pre-reflow lateral offset in both axes with uncertainty. Require the magnitude plus its uncertainty to be at most 10 micrometers for the prospective single-joint comparison.
5. Withdraw any contacting placement aid before the liquid hold. Support the carrier only. Use no cap spacers, adhesive, contact-height fixture, or clamp.
6. Reflow each pilot carrier in its own run. Record its actual profile, oven position, atmosphere, and deviations. Use one reflow cycle per scored assembly.
7. Let each assembly cool under the documented process. Do not mechanically straighten a tilted cap or rework an unfavorable joint.
8. Inspect all attempted caps for missing joints, nonwetting, bridges, damage, and abnormal offset. Photograph the assembly and preserve the raw inspection records.

Treat a cap disturbed by a fixture, rework, extra solder, or an unrecorded replacement as a failed attempt. Retain it in practical-clearance records and the attempt denominator. It may be ineligible for the isolated-joint model comparison.

## Prove the measurement method on pilot parts

Use a calibrated full-volume three-dimensional method that resolves the opposing finished pad faces of all twenty joints. Supply the local-gap uncertainty budget at the relevant material contrast and geometry. Expanded uncertainty must be at or below 2 micrometers per local gap at coverage factor 2. Expanded uncertainty of a C220-minus-C270 paired difference must be at or below 3 micrometers. Preserve covariance assumptions for shared calibration errors.

Include scale calibration, repeat scans or repositioning, segmentation threshold sensitivity, pad-face definition, reconstruction effects, registration, beam hardening or optical distortion, temperature, and operator repeatability in the budget. A small pixel or voxel does not demonstrate dimensional accuracy. Use a traceable reference artifact and independent registered sections to test the relevant measurement chain.

Register the section plane to specified rows through pad centers. Image the cut location before polishing and retain coordinates relative to the coupon orientation. Verify the diameter, opposing pad faces, finish heights, solder sidewall wetting, contact-line location, and local gap. Use an orthogonal section or independently calibrated orthogonal datum to check tilt and plane registration. Quantify section obliquity, polishing removal, edge rounding, and preparation effects.

Scan all twelve pilot caps before destruction. Section six pilot caps, one from each arm per run. A center section measures local gaps only. It does not prove the minimum beneath the full cap. If complete twenty-joint coverage is unavailable, report measured local gaps and mark whole-cap minimum clearance inconclusive.

For every measurable cap, return the twenty local gaps and their uncertainties, mean, minimum, maximum, gap range, fitted plane, tilt, in-plane offset, warpage, wetting observations, void observations, and measurement temperature. Preserve the original volumes, images, segmentation, and calibration records. State which apparent pad edge defines each diameter and wetted rim.

## Decide whether the pilot permits confirmation

Require evidence that assembly and metrology can meet the controlled geometry, wetting, uncertainty, and input gates. Estimate the observed paired variation within each pilot run. Assess prospective precision for a 6 micrometer arm difference with run effects retained. The pilot has six pairs across three runs. It is a feasibility and precision study, not a known-power or production-yield study.

Stop or prepare a new revision before confirmation if the expected 6 micrometer difference is not resolvable. Do the same if metrology cannot achieve the specified uncertainty or cannot observe the full cap. Fix any change to sample count, process, fixture, measurement, or analysis before held-out outcomes. Do not let pilot agreement select the primary model family.

The pilot must qualify the maximum placement-and-flux-to-reflow dwell. Include time for all placement measurements, data transfer, native calculations, manifest review, and oven scheduling. If the flux cannot tolerate that dwell, revise the process before confirmation. Do not replace actual offsets with nominal zero to shorten the freeze.

## Freeze predictions before confirmation outcomes

Use the repository's `coupons/tools/analyze.py` commands and generated templates. Follow its current `--help` for exact arguments. Keep measured inputs, laboratory metadata, and outcome files separate. Leave outcomes blank until the prediction manifest is frozen. Archive the manifest, actual input files, source hashes, solver receipts, material sources, uncertainty choices, and UTC freeze time.

Run these commands from the repository root. Replace `lab-data` with a new working directory. Fill the generated input and metadata files from laboratory evidence before running `freeze`. Do not run `freeze` with blank templates.

```sh
python3 coupons/tools/analyze.py templates --output lab-data
python3 coupons/tools/analyze.py freeze --inputs lab-data/inputs.csv --metadata lab-data/metadata.json --output lab-data/frozen
python3 coupons/tools/analyze.py score --freeze lab-data/frozen --outcomes lab-data/outcomes.csv --output lab-data/report.json
```

Run `score` after recording outcomes. Preserve the original frozen directory. Keep raw laboratory data and signed input records beside the machine-readable files. A software freeze records the data supplied to it. It does not establish that the laboratory measured those data correctly.

Complete room-temperature placement and offset metrology for all twenty-four confirmation caps before the freeze. Keep them under the pilot-qualified dwell conditions. Use actual incoming measurements and the accepted pilot process to predict each confirmation cap. Do not supply confirmatory gap, final offset, or observed wetting to a prospective prediction. Keep any later outcome-informed reconstruction in a separately labeled explanatory analysis.

Freeze these three computations without choosing among them from the better fit.

- The primary literal-rim model uses measured liquid solder volume and the opposing pad faces directly. Disable solder gravity in this declared approximation.
- The fixed secondary approximation adds both pad-cylinder volumes. Use `Vmodel = Vsolder + pi * (Dlower/2)^2 * tlower + pi * (Dupper/2)^2 * tupper`. Convert its output to pad-face gap with `hrim = hmodel - tlower - tupper`. Use millimeters consistently. Disable gravity for this approximation so fictitious copper-cylinder liquid mass does not enter the load.
- The separate gravity sensitivity uses literal rims and actual solder body gravity. Do not add upper copper mass again to the already measured cap mass.

Retain the aligned analytical load-corrected formula as the simple comparator. Record its assumptions and predictions beside the native computation. Compare performance without claiming that more computation is automatically better.

An accepted numerical request needs refinement checks, balanced load, and no model warnings. Numerical agreement is not a measurement of physical accuracy. Material uncertainty and geometry sensitivity still apply to a numerically accepted prediction.

## Assemble and measure confirmation without tuning

1. Verify the frozen input manifest before any confirmation outcome acquisition.
2. Reflow the already placed and measured carriers in each of R1, R2, and R3 under the accepted profile and dwell limit. Record actual run traces and positions. No confirmation reflow begins before the completed prospective freeze.
3. Retain all twenty-four attempts. Record defect and missing-data states without replacing the original records.
4. Measure the twenty-four cooled caps with the frozen whole-volume method at 20 plus or minus 2 degrees Celsius.
5. Scan before destruction. Section the six preselected confirmation caps, one from each arm per run, using the accepted registered method.
6. Preserve all raw data and complete the outcome sheet without changing prospective input values.
7. Score the frozen predictions and analysis. Label any later exploratory revision separately.

Optional hot-state observations require a separately accepted method. Confirm a stable observable liquid plateau without a cap-contact force. Record actual temperature, uncertainty, datums, time stability, thermal expansion, and coverage. Cite hot_method_evidence in metadata. Every observed hot temperature uncertainty interval must lie inside the frozen plateau interval and above the alloy liquidus. Develop that method on extra or profile specimens before using held-out caps.

## Apply eligibility and decision rules

Report practical-clearance and model-comparison states separately. Keep every attempted cap in the practical record. An isolated-joint model comparison requires all twenty joints to be wetted, no bridge, no contacting support, measured final offset plus its uncertainty at or below 25 micrometers, and a cap gap range at or below 3 micrometers. Record the uncertainty of the gap range. Use max minus min plus their two expanded uncertainties as a conservative guard. A smaller directly measured range uncertainty requires a cited covariance budget. Record wetted_joints, wetting_boundary_status, and wetting_evidence explicitly. A clean defect field does not prove all twenty joints are wetted. Also require the observed contact line to match the frozen boundary hypothesis for model scoring. A failed boundary or equal-loading assumption is an applicability failure, not permission to fit a new gamma.

For each cap, claim the declared pad-face threshold only when the complete measured minimum minus its expanded uncertainty is at least 185 micrometers. Otherwise report a failure or an inconclusive threshold result as the evidence warrants. Do not substitute a mean for the minimum. Do not call the threshold a mask-to-cap pass.

Report each adjacent C220-minus-C270 pair, each run's mean difference, and the pooled descriptive difference. Report the three run effects beside any pooled interval. Preserve the analysis assumptions. A paired calculation that treats twelve pairs as independent does not establish future-run variability. The 480 local joints in confirmation are not 480 independent experiments.

Support a pad-size decision only if measurement uncertainty, run variation, defects, and missing data do not reverse the group conclusion. A result that reproduces the ordering but misses the minimum-clearance criterion does not support that clearance choice. A result that depends on dropping one unfavorable run remains inconclusive.

For absolute liquid-model scoring, use held-out molten observations with their uncertainty. The supplied scorer accepts direct molten observations only. An independently justified transformation requires its own prospective analysis revision. Retain the declared 5 micrometer model height-error budget. Cooled geometry can support a conditional process comparison while absolute molten-model qualification remains inconclusive. No outcome here establishes restoring-force accuracy, fatigue, electrical reliability, or production yield.

## Return the complete record

Return the accepted specification and panel CAM, material certificates, actual inputs, allocation and deviations, sphere and kit records, bare-cap mass logs, all thermal traces, calibration and uncertainty budgets, raw measurement volumes, calibrated images, section coordinates, local gap tables, prediction manifest and receipts, scored report, and all failed or missing states. Return remaining specimens, unused materials, and practical section remnants.

Keep unmeasured outcomes empty. Do not replace an absent laboratory result with a planning prediction or synthetic test result.
