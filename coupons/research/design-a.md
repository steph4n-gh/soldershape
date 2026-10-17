# Candidate A. Matched FR4 cap and board coupons

This candidate uses two ordinary PCB fabrication jobs and a custom sphere assembly at an outside lab. The two board pad diameters are the only deliberate difference between the groups. It tests the effect of that pad change in a new process. It does not reproduce the 2004 CSP, which used a different upper body and an incompletely specified metallization.

The main weakness is the thickness of both copper pads. The old paper's one-pad correction cannot be carried into this assembly. The design makes that difference measurable and keeps it in the prediction record.

## Physical construction

Use a 3.0 by 3.0 mm FR4 cap, nominally 0.6 mm thick. Its underside has 20 circular copper pads. Five columns and four rows have a 0.5 mm pitch. Every upper pad has a 0.280 mm copper diameter. The center of the array is the center of the cap. This leaves 0.36 mm between the outside pad edge and the closest nominal cap edge.

Request 35 micrometer finished copper and ENIG on both mating boards. Use one material and finish lot for all lower boards. Use one lot for the caps. The cap has no traces, vias, ground plane, or upper-side copper. Its opposite side has a printed orientation mark. Any balance mark or supplier panel code must remain outside the finished cap. Weigh the finished, clean cap after depanelization. Do not infer its supported load from a catalogue laminate density.

The lower board has the same 5 by 4 array at each assembly site. Group X uses 0.220 mm copper pads. Group Y uses 0.270 mm copper pads. All pads are isolated copper circles. No trace can draw solder away from a circle. Each array has a single 2.8 by 2.3 mm rectangular solder-mask opening. This opening is identical for both groups. It avoids a requirement for narrow mask webs between adjacent pads. The upper cap uses the same opening on its mating side. The opening remains inside the cap outline.

Use an 80 by 50 mm, 1.6 mm thick lower board with 12 independent cap sites. Put the centers at x coordinates 10, 30, 50, and 70 mm and y coordinates 10, 25, and 40 mm. This gives space for a side-view microscope and local reference marks. Add three ordinary global fiducials outside the sites. Keep silkscreen, exposed copper reference marks, and identification text outside a 5 mm square around each array. The lab can place and inspect each cap without another component blocking a view.

The lower board has no electrical function. This choice removes traces, solder-mask-defined necks, and daisy-chain continuity as confounders. X-ray and section inspection establish whether each joint formed. A later electrical reliability experiment would need a different coupon.

The cap outline and panelization require a fabricator quote. JLCPCB's [capability page](https://jlcpcb.com/capabilities/pcb-capabilities/) lists a 3 by 3 mm minimum for FR4 at thicknesses of at least 0.6 mm. Its separate [dimensions page](https://jlcpcb.com/help/article/pcb-dimensions) gives a 0.8 mm thickness condition. The lab must obtain written acceptance of 3 by 3 by 0.6 mm caps, finished pad diameters, mask window, and depanelization before ordering. A thicker cap is an allowed redesign before the freeze. It is not a silent substitution after predictions have been recorded.

## Solder and assembly

Request Sn63Pb37 spheres with a nominal 0.320 mm diameter from one traceable lot. Use flux without added metal. Do not use paste or HASL. A 0.320 mm solid sphere has a calculated volume of 0.0171573 cubic millimeters. This is close to the paper's total metal volume, but it is not the paper's 0.01745 cubic millimeters.

[Indium lists Sn37Pb spheres](https://www.indium.com/products/solder-spheres/) over a diameter range that includes 0.320 mm. This supports a request for a quote. It does not establish stock or a sufficiently tight tolerance. The [sphere data sheet](https://www.indium.com/wp-content/uploads/2025/01/Specialty-Solder-Spheres-PDS-97549-A4-R9.pdf) gives a standard diameter tolerance of 25 micrometers in this size range. That tolerance cannot be ignored in a height experiment with a 6 to 11 micrometer comparison signal.

Ask the supplier for a tighter graded lot. Independently measure a random sample of at least 100 incoming spheres. Record each measured diameter and roundness. Prepare numbered kits of 20 spheres. Weigh each kit before flux application with an expanded mass uncertainty of at most 0.02 mg. Reject a kit that loses a sphere or gains unrecorded metal. Retain the lot distribution to estimate variation between joints within one cap.

The lab places one sphere on each lower pad in tack flux and then places the cap. A ball-positioning tool may be used before cap placement. Remove the tool before reflow. No jig, spacer, adhesive, clamp, probe, or thermocouple may support or press on a scored cap during its liquid interval. The normal load comes from the cap's measured weight. The solder's own gravity is handled separately in the model.

Use a supplier-recommended flux and a recorded Sn63Pb37 reflow profile. Freeze the profile after the pilot. Measure the profile on a separate dummy cap and board, not on a scored cap. Record actual peak temperature, time above liquidus, heating and cooling rates, atmosphere, and local board temperature differences. A second reflow is a separate process deviation. Preserve that specimen rather than silently replacing its record.

Clean according to the flux supplier's procedure before final mass and dimensional measurements. Retain the flux product number, lot, dispensed amount or application method, and cleaning details. A generic description such as "no-clean flux" does not identify a wetting condition.

## Independent units and blocking

Use four pilot caps, two per pad group. Pilot caps qualify assembly and metrology. They do not contribute to the held-out height score. Use 36 scored caps, with 18 per group. Three independent reflow runs each contain six caps per group on one lower board. The 20 joints under one cap are correlated observations. A cap is the experimental unit.

Create three lower-board variants. Within each variant, assign one X and one Y site to each of six adjacent position pairs. Use a frozen random seed to randomize left and right assignments within each pair. Reverse or randomize the placement order within each run. Randomize top-cap selection and sphere-kit assignment without regard to group. Keep the board, site, cap, sphere kit, and reflow run linked in the specimen map.

Fabricate at least 48 caps and one spare copy of each lower-board variant. Four caps are for the pilot, 36 are for the primary comparison, and eight are spares. Order at least 1,200 acceptable spheres, subject to the supplier's package quantity. A replacement cap gets a new specimen ID. The original failure stays in the assembly-yield record.

Eighteen caps per group is a pilot-scale choice, not a power calculation from known process variance. For independent cap standard deviations of 4 micrometers, the calculated standard error of a difference of two group means would be 1.33 micrometers. The process standard deviation is unknown. Use the pilot only to assess whether the planned precision can resolve a 6 micrometer difference. If it cannot, amend the sample count before assembling the scored batch or report the result as inconclusive.

The measurement operator may infer the group from a section. Claim only coded outcome capture, not perfect physical blinding. The model analyst freezes the requests before receiving scored height outcomes. The measurement file contains specimen IDs and observations. The arm-key file remains separate until the prediction manifest has been written.

## Reference planes and the two-sided copper correction

Define the lower laminate surface as z equals zero. The lower pad top is at its measured finished metal thickness, `t_lower`. The cap's lower laminate surface is at `H`. Its pad top facing the solder is at `H - t_upper`. The rim-to-rim gap is therefore `h_rim = H - t_lower - t_upper`. Mask thickness does not enter this definition.

Record three different clearances. The primary study height is the pad-face gap, `h_rim`. The cap-body clearance is the minimum distance between the lower face of the cap laminate and the lower board's mask or laminate. The under-cap clearance for a real component depends on that component's height and the local keepout. A study threshold of 185 micrometers applies to `h_rim` only. It is not automatically a real component's clearance requirement.

Sections must locate the solder contact line at each end. A literal-rim model uses measured solder liquid volume and reports the solver gap directly. A full-sidewall envelope adds both pad cylinders to the model volume and subtracts both thicknesses from the computed gap. Freeze the primary mapping from pilot wetting observations before reading scored outcomes. Retain the other mapping as a sensitivity. A partially wetted sidewall, a finish ledge, a de-pinned contact line, or an inconsistent contact perimeter invalidates both simple mappings as a primary absolute-height validation.

For full sidewall wetting, define `V_lower = pi * D_lower**2 * t_lower / 4` and `V_upper = pi * D_upper**2 * t_upper / 4`. The envelope volume is `V_liquid + V_lower + V_upper`. Its extra upper cylinder also has fictitious gravity. With model gravity enabled, use a per-joint external load of `m_cap * g / 20 - rho_liquid * V_upper * g`, with consistent units. The lower extra cylinder has a fixed gravitational energy. The upper correction prevents its fictitious liquid weight from being counted in addition to the measured cap weight. Preserve the uncorrected and gravity-disabled results as controls.

This choice has a visible consequence. An aligned unloaded spherical calculation with a 0.320 mm sphere predicts literal-rim gaps of 224.92 and 208.68 micrometers for the two lower pads. With two 35 micrometer pad cylinders, its calculated rim gaps are 180.09 and 168.79 micrometers. These values are geometry checks, not coupon predictions. They show why the previous one-pad result cannot be used to promise 185 micrometers of clearance for this construction.

Use a cited liquid density at the actual reflow temperature to convert solder mass to liquid volume. Supplier room-temperature density is insufficient. Keep the density source, temperature, uncertainty, and alloy composition in the input freeze. Record metal dissolved from the finish as a bounded uncertainty. Do not fit an unexplained volume multiplier to held-out heights. The nominal 0.320 mm sphere volume is a solid geometry value, not a liquid-volume measurement.

## Metrology and phase

The absolute model target is liquid equilibrium. The ordinary output of an assembly lab is solid geometry at room temperature. Keep those outcomes separate.

Request calibrated, perpendicular side-view images during the pilot's liquid hold if the lab has a suitable hot stage. Record temperature and time with each image. A final plateau in visible height is evidence of a repeatable geometry. It does not prove equilibrium or establish all interior joint loads. Do not add a height constraint to obtain a clearer image.

For all scored caps, request a noncontact profile before sectioning. Measure the upper cap plane and the adjacent lower board plane from two orthogonal views or a three-dimensional profiler. Include upper-cap thickness measurements and actual reference marks. The result must distinguish cap tilt from average gap. Require an expanded uncertainty of at most 2 micrometers for a reported gap and at most 3 micrometers for the paired group difference. A microscope's pixel size or a CT voxel size is not an uncertainty statement.

Request centerline metallographic sections of at least three caps per group across the three runs. Locate the plane using X-ray before cutting. A cut through one selected row samples five joints and does not establish the minimum across all 20 joints. Capture pad dimensions, copper and finish thicknesses, wetting lines, local gaps, voids, intermetallic layers, and preparation damage. Retain original calibrated images.

Use calibrated micro-CT on at least one cap per group per run if the optical plane reconstruction cannot bound local warpage or the minimum gap. The lab must demonstrate the gap uncertainty with a representative artifact. If it cannot do so, restrict the reported clearance result to the measured locations. Do not label an unobserved whole-cap minimum as measured.

Record final lateral offsets in both axes, rotation, tilt, visible defects, and evidence of missing joints. These observations support a secondary reconstruction. The primary prediction uses pre-outcome placement and geometry assumptions. A post-section reconstruction may use observed offset and wetting, but it cannot replace the primary score.

If the lab only offers room-temperature sections, the study can validate the comparative post-reflow clearance within an explicit thermal uncertainty. It cannot by itself establish absolute accuracy of liquid equilibrium. Quote the hot-stage pilot as a separate line item so that this limitation is visible before purchase.

## Frozen analysis and decision

Prepare a separate loaded request for each lower diameter. The application reference-pair feature holds the lower pad fixed and cannot express this experiment. Use the existing `LoadSpec` entry point without changing the product API.

Freeze the model code hashes, solver binary hash, nominal input distribution, copper mapping, density and surface-tension sources, specimen assignment, exclusions, and scoring rules before the scored outcomes are released. Store both the native solver and the load-corrected spherical baseline predictions. A baseline that makes the same design decision at lower cost is a successful finding about scope, not a failed experiment.

The primary comparisons are the run-blocked difference in cap mean gap, the absolute mean gap error for each group, and the minimum-gap result at the actual measured locations. Preserve within-cap and between-cap variation separately. Do not use 720 joints as 720 independent samples. Report a confidence interval for the group effect and a metrology uncertainty beside it.

The study threshold is 185 micrometers. Prefer a pad geometry for further development only when its measured clearance and uncertainty satisfy that threshold under the declared process. A mean above the threshold does not establish every cap or a production yield. If both arms fail, keep that result. If uncertainty spans the boundary, make no clearance recommendation.

Reject the simple model as an absolute-height tool for this construction if the pilot shows unstable or inconsistent contact boundaries. Reject the frozen physical prediction if the held-out errors exceed the predeclared combined input and metrology bounds. If the predicted pad-size ordering reverses in the held-out data, stop a pad-size recommendation until the cause is resolved. Do not choose a different copper mapping, density, gamma, or shrink correction after seeing those outcomes.

## Data shapes

Use one experiment specification with explicit units. Unknown measurements remain null. They never inherit a nominal default during scoring.

```text
ExperimentSpec
  experiment_id, revision, random_seed
  geometry
    lower_board_outline_mm, cap_outline_mm, array_columns, array_rows
    pitch_mm, upper_pad_diameter_mm, lower_pad_diameters_mm
    mask_window_mm, nominal_finished_copper_um, nominal_cap_thickness_mm
  material
    alloy_composition, sphere_nominal_diameter_um, finish
    liquid_density_source, liquid_density_g_cm3, liquid_density_uncertainty
    gamma_source, gamma_n_m, gamma_uncertainty
  geometry_convention
    primary_mapping, alternate_mapping, wetting_qualification_record
  sampling
    pilot_caps_per_arm, scored_caps_per_arm, runs, sites_per_run
  measurements
    height_reference_planes, measurement_temperature_c
    maximum_gap_expanded_uncertainty_um, minimum_locations
  scoring
    threshold_rim_gap_um, exclusions, block_effect_method
  provenance
    solver_hashes, generator_hash, spec_hash, prediction_manifest_hash

SpecimenInput
  specimen_id, run_id, lower_board_serial, site_id, cap_serial
  arm_code, sphere_kit_id, solder_lot, flux_lot, profile_id
  cap_mass_mg, cap_mass_uncertainty_mg, sphere_kit_mass_mg
  actual_pad_geometry, actual_metal_thicknesses, pre_outcome_offset_assumption
  measurement_sources, input_freeze_time

Outcome
  specimen_id, observation_status, disposition_reason
  measurement_temperature_c, height_planes, gap_measurements_um
  cap_tilt, offset_xy_mm, rotation_deg, wetting_observations
  voids, nonwet_joints, bridges, warpage, image_paths
  instrument_id, calibration_id, expanded_uncertainty_um
  primary_or_explanatory, assessor_id, observation_time
```

Use `observation_status` values of `measured`, `not_measurable`, `assembly_failure`, and `missing`. An assembly failure is not a measured height of zero. No height belongs in `SpecimenInput` for a loaded prediction.

## Tool boundaries

```text
read_spec(path) -> ExperimentSpec
  Parse units, required fields, and mutually exclusive geometry mappings.

assign_sites(spec) -> SiteMap
  Deterministically balance the groups within each run and position pair.

generate_boards(spec, site_map, destination) -> SourceFiles
  Write only native editable board geometry and drawings.

verify_fabrication(spec, source_files, exports) -> VerificationReport
  Parse the actual KiCad files and independent Gerber apertures.
  Check counts, diameters, spacing, mask window, outlines, and absence of traces.

freeze_predictions(spec, specimen_inputs) -> PredictionManifest
  Reject missing required physical inputs.
  Create separate lower-pad loaded requests.
  Store native and analytical results, failed solves, and input hashes.

score_outcomes(frozen_manifest, outcomes) -> AnalysisReport
  Reject placeholder outcomes, ID mismatches, and a changed primary mapping.
  Compute cap-level and run-blocked results.
  Preserve unmeasurable and failed assemblies in their own denominators.
```

These are boundaries for one deterministic script and one small analysis script. They do not justify a coupon framework or a product database.

## Quote gates and changes

The outside lab quote must cover cap panel fabrication and depanelization, lower-board DFM, sphere supply and screening, traceable kit weighing, four pilot assemblies, 36 scored assemblies, dummy profile measurements, optical gap metrology, selected X-ray and sections, retained raw images, and uncertainty statements. Request optional hot-stage pilot imaging and calibrated CT separately. Ask the lab to identify any subcontracted process.

Stop before fabrication if the fab cannot preserve the circular finished pads, if the cap outline needs an unreviewed change, or if the lab proposes solder paste or a spacer. Stop before scored assembly if the pilot cannot establish the contact geometry or measurement precision. If the supplied alloy, finish, thickness, sphere diameter, or cap mass differs from the specification, update the physical input record and regenerate predictions before outcomes. A change that alters the comparison requires a new protocol revision and a new freeze.

The strongest argument against this candidate is that ordinary thick PCB pads introduce a measurable wetting and reference-plane problem that may dominate a small height difference. Its advantage is that the hardware resembles a practical PCB assembly and uses two standard fabrication processes. The correct fallback is a thinner, explicitly characterized metallization on a custom upper coupon, or a narrower claim about measured comparative clearance. It is not an unexplained correction fitted to the held-out result.

Model the Domain required separate input and outcome records, so measured height cannot leak into the loaded request. Explain the Number required the two-sided copper calculation and cap-level sample count, so nominal paper heights and joint counts cannot be mistaken for evidence. Prove It Works required actual fabrication geometry checks and a lab uncertainty demonstration, so a DRC pass or instrument resolution alone cannot release the experiment.

## Source verification correction

The data-sheet URL cited above returned HTTP 404 during root verification. Its claimed standard 25 micrometer tolerance is unverified and is not used in the final procurement specification. Obtain the actual quoted grade and preserve the guard-banded screening evidence. The manufacturer sphere page supports the alloy and size-range quote basis only.
