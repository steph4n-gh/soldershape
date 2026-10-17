# A matched pair of passive FR4 coupons for an outside lab

This candidate uses a custom 3 by 3 mm passive upper PCB and two lower PCB pad sizes. A lab assembles one measured solder sphere per joint. The experiment measures the effect of the lower pad size under one controlled process. It also tests whether either declared pinned-rim geometry convention predicts the resulting gap. It does not inherit a 185 micrometer pass result from the published package.

The user needs no equipment. The lab quotes fabrication, sphere handling, assembly, imaging, sectioning, and measurement as one package. The lab does not receive a request to approve the model or reproduce the old paper.

## Choose catalog spheres and one common upper partner

Use the same top coupon for both groups. Its outline is 3.000 by 3.000 mm. Its nominal finished board thickness is 0.600 mm. Its underside has 20 isolated, circular 0.280 mm copper pads on a 5 by 4 array at 0.500 mm pitch. Center the array at the cap center. Its pad centers span 2.000 by 1.500 mm. The cap has no vias, traces, pasted pads, attached weights, or components. Its back has no functional copper. Place a small orientation mark on its back without a copper mass. Let the lab identify each cap in a tray until assembly associates it with a lower-board specimen ID.

Use nominal 1 oz finished copper and ENIG on both upper and lower pads. Do not request OSP for the 220 micrometer pad. The [JLCPCB capability table](https://jlcpcb.com/capabilities/pcb-capabilities/) lists a 3 by 3 mm minimum rigid board at thicknesses of at least 0.6 mm. Its [BGA capability entry](https://jlcpcb.com/capabilities/pcb-) requires ENIG for pad diameters from 0.20 to 0.25 mm. These are capability examples. They are not an accepted quotation for this panel or a micron-level pad tolerance.

The upper coupon is a custom fabricated part. A PCB vendor or the assembly lab must quote its panelization, singulation, edge cleaning, and tray delivery. Do not call a bare 3 mm KiCad outline production panelization. Exclude soldered carrier tabs and temporary adhesive from the cap during reflow. The solder joints alone must support the cap. The lab weighs each bare cap after singulation and cleaning. A nominal FR4 density calculation suggests roughly 10 mg and roughly 5 micronewtons per joint. That estimate is only useful for selecting a balance. The model uses measured cap mass.

Use one lot of nominal 0.325 mm Sn63Pb37 spheres with no added solder paste. [EasySpheres lists catalog item 10-6337-13](https://www.easyspheres.com/sn63pb37-2/) with that metric size. The page also prints 0.013 inch, which is 0.3302 mm, and gives conflicting tolerance text. The lab must obtain a metric size distribution and a certificate of conformance before purchasing it. Independently measure the received lot. Do not copy the page's tolerance into the uncertainty budget. Availability, unit quantity, cost, and delivered diameter remain quote conditions.

This diameter is a practical choice near the old metal-volume scale. A 0.325 mm perfect sphere contains 0.0179741642 cubic millimeters. That is a room-temperature geometric volume. It is not the old paper's 0.01745 cubic millimeters and it is not automatically the liquid volume. A sphere actually measuring 0.3302 mm contains 0.0188508019 cubic millimeters. The difference is large enough to alter the clearance decision.

Use one traceable flux lot suitable for ball attachment and a lab-proposed eutectic SnPb reflow profile. The lab supplies the flux part number, technical data sheet, dispensed amount or repeatable dispensing method, cleaning method, and temperature profile before outcome prediction. Flux holds the spheres for placement. It contributes no declared metal. No rework, extra ball, paste addition, underfill, spacer, or contacting height fixture is allowed in the held-out assemblies.

If the 0.325 mm part cannot be obtained with identified dimensions, stop this revision. Revise the specification and regenerate predictions before assembly. A catalog 0.300 mm sphere is an acceptable future revision. It is not a silent substitution. The [Chip Quik datasheet](https://www.chipquik.com/datasheets/SMD2195.pdf) identifies SMD2165-25000 as a nominal 0.3 mm Sn63Pb37 product. It contains only 0.0141371669 cubic millimeters at that nominal diameter.

## Keep the lower-pad change isolated

Each lower unit is a 20 by 20 mm passive PCB with one array at its center. Group A has 0.220 mm circular copper pads. Group B has 0.270 mm circular copper pads. All other geometry, stackup, finish, mask color, material lot, handling, and assembly conditions are common.

Use a 1.600 mm nominal lower-board thickness and the same nominal 1 oz finished copper and ENIG process. Specify the two groups on the same manufacturing panel. Use high Tg FR4 for both upper and lower parts if the vendor can supply one identified laminate family. Do not claim identical material from an unspecified generic FR4 designation. The lab records the actual laminate, thickness, finish, copper thickness, ENIG thickness, and warpage for each lot.

Use one rectangular solder-mask window per array. The window spans 3.000 by 2.500 mm and is centered on the array. The copper pads are isolated islands. There are no traces, vias, planes, or exposed copper connections within the window. This retains a circular wettable copper boundary without relying on individual 320 to 380 micrometer mask openings or small dams. The mask edge lies well outside the pads. A gang opening does not cause copper islands to touch. Verify that the fabricator does not add thieving, test traces, or copper fill in the window.

Add three isolated optical fiducials outside the cap footprint and a readable lower specimen ID. Keep all fiducials and silkscreen outside the 3 mm cap outline and its inspection access. Add no drill hole or exposed conductor under the cap. A bare-board inspection witness array near the edge uses the same pad geometry and finish. It supplies accessible preassembly metrology. Its presence does not excuse measuring no actual assembly pads.

The package contains editable sources for A, B, and the top coupon. It also contains a lower manufacturing panel source with eight units of each group. One proposed panel is 100 by 100 mm with four rows of four 20 mm units, 2 mm route streets, and peripheral tooling rails. The fabricator must approve the tab and tooling design. Complete singulation occurs before assembly. The lab then randomizes individual units into reflow carrier positions. Fixed panel pad locations cannot confound group with reflow position.

## Declare the height planes and two separate hypotheses

The clearance requirement is at least 185 micrometers. Declare its physical reference as the minimum separation between the opposing finished wettable pad top planes over the 20 joints. Also measure the minimum laminate-to-laminate and mask-to-cap clearances. Do not exchange these values. The lab's full three-dimensional measurement determines the minimum. A section through one row alone cannot certify the minimum under the entire cap.

The nominal 35 micrometer copper thickness is not the finished wettable thickness. ENIG, intermetallic formation, pad edge shape, and sidewall wetting need direct measurement. The lab records each of the following planes in the section images:

1. The lower laminate surface at the pad base.
2. The lower finished pad top surface.
3. The actual lower contact-line height and radius.
4. The actual upper contact-line height and radius.
5. The upper finished pad top surface.
6. The upper laminate surface at the pad base.

Freeze two hypotheses before blind results. The first uses liquid solder volume directly and pins rims at the opposing pad tops. Its output is the pad-top gap. The second extends the published cylinder approximation explicitly to both pads. It adds both pad cylinders to liquid volume and subtracts both finished pad heights from the solved effective gap. This approximation does not put liquid inside copper. Do not select whichever hypothesis fits each held-out specimen.

For clarity, unloaded spherical calculations with nominal 0.325 mm spheres, room-temperature geometric volume, no finish thickness, and two nominal 35 micrometer pads give the following illustrative values. They are not the experiment's liquid predictions.

| Copper diameter on the lower board | Literal pad-top rims | Two-pad cylinder approximation |
| --- | ---: | ---: |
| 220 micrometers | 231.132 micrometers | 185.527 micrometers |
| 270 micrometers | 214.971 micrometers | 174.194 micrometers |

These values were computed with the existing `spherical_gap_mm()` function. The large difference between conventions is a decisive experimental question. This custom cap does not retain the paper's unreported thin upper metallization. A supported load, measured liquid-volume conversion, actual finished dimensions, and thermal geometry will change both rows. A lab plan that still quotes the old 201.774 and 190.681 micrometer predictions for these new boards is inconsistent.

Use sphere batch mass and a declared alloy liquid-density source at the observed reflow temperature to calculate liquid volume. Use measured sphere diameters and room-temperature volume as an independent mass and volume cross-check. Record the source, temperature, uncertainty, and phase of every density value. A room-temperature density cannot be labeled a liquid density. Do not fit shrinkage or a density conversion to held-out heights. If no credible liquid conversion can be identified, the physical pad-size result remains useful but absolute liquid-model qualification remains inconclusive.

The normal load request equals the measured bare upper-cap weight divided by 20. Do not add all solder weight to that load. The solver already includes the solder body's gravity when enabled. No fixture force is assumed to be zero unless the cap is visibly free of its placement head during reflow. A missing or nonwet joint does not justify retrospectively dividing the cap weight by a smaller number and calling the original prediction valid.

## Use a pilot followed by blinded assemblies

Quote 64 lower boards, split equally between A and B. Quote 80 top coupons. Quote one sphere lot with enough spheres for 1,280 joints, incoming inspection, process setup, and handling loss. A 10,000-sphere supplier minimum, if confirmed, exceeds this need. Do not order a second sphere lot to reduce leftovers.

Use 16 assemblies for the pilot, eight per group. The pilot establishes ball handling, wetting, microscopy, thermal profile, and the model's geometric applicability. Pilot images may choose one common primary geometry convention before the held-out run. No height-based parameter fit is necessary. If a material or process correction is fitted, state its fitted parameters and preserve these 16 assemblies as calibration data only.

Use 48 held-out assemblies, 24 per group. Split them across three independent reflow runs. Each run has eight of each group. Randomize group, carrier position, cap ID, and assembly order with a recorded seed. The statistician or project coordinator holds the group key and model predictions. The measurement operator receives coded IDs, not predicted heights or a promised direction. Copper diameter can reveal the group in sections, so describe this as masked outcome prediction rather than guaranteed operator blindness.

Each cap is one experimental unit. Its 20 joints share placement, cap weight, reflow history, and load. They are correlated measurements. Do not report 960 independent specimens. Preserve all 48 attempted assemblies and their defect status. Reflow run is a block in the pad-size analysis.

The equal-share single-joint model is eligible only when all 20 joints attach, no bridge forms, no substrate contact occurs, and the geometry gate passes. The geometry gate requires a declared offset limit of 25 micrometers, no evidence of a moving contact line onto the mask or laminate, and no more than 3 micrometers of pad-gap variation across the array after accounting for measured tilt. These limits are engineering choices and must be frozen before held-out assembly. They are not a claim that the native solver predicts load sharing or cap warpage. Assemblies outside the gate remain in the manufacturing-outcome and clearance tables. Their failure is not erased from the product decision.

## Quote metrology before committing to the run

The outside lab must demonstrate an expanded gap uncertainty of no more than 2 micrometers at approximately 200 micrometers. Target a coverage factor near two and report the actual budget. Pixel size and nominal CT voxel pitch are not uncertainty estimates. The expected pad-size signal is only about 6 to 16 micrometers across the relevant observations and models.

Use calibrated three-dimensional X-ray microscopy or equivalent dimensional metrology on every held-out assembly. It records local pad-to-pad gap, cap tilt, two-axis offset, voids, bridging, and the minimum declared clearance. A 3 mm region of interest inside a 20 mm board is the metrology target. The lab demonstrates access, contrast, segmentation, and dimensional error on the pilot before pricing the full run as qualified measurements.

Cross-section a predeclared subset to check the dimensional method and identify wetting. Use at least four pilot assemblies and 12 held-out assemblies. The held-out subset has two assemblies per group per run. Randomize which array row or column each section intersects. Include pad edges, both finish layers, and local laminate reference surfaces. Preserve a calibrated image of the section and its location relative to pad centers. A polished section that misses the pad center cannot supply an unbiased pad diameter.

Record incoming pad dimensions, edge roughness, finish thickness, cap mass, cap flatness, sphere size distribution, ball count, flux, and profile before unmasking outcomes. Record the cold height at 20 plus or minus 2 degrees C after a fixed cooling and dwell interval. Record that interval. A room-temperature section is a post-solidification observation. It does not directly observe a liquid equilibrium shape.

If the lab cannot demonstrate the three-dimensional uncertainty target, it may offer serial sections for mean gap. That changes the deliverable. The absolute minimum-clearance decision remains inconclusive unless the full assembly volume is inspected with sufficient accuracy. Do not convert one favorable section into a minimum-clearance pass.

## Freeze the prediction and score separately

Generate the primary input file from pre-outcome lot geometry, measured cap masses, the frozen volume conversion, nominal aligned placement, and the declared material scenarios. Do not feed final height, final offset, or section-derived contact line back into a primary forward request. Hash the input, model code, engine, and prediction outputs before the held-out height file is released.

After outcome release, an explanatory reconstruction may use measured offset and actual contact lines. Label it separately. It can identify a boundary-condition failure. It cannot replace a failed primary prediction.

Report both the native load-balanced model and the simple aligned load-corrected analytical comparator. For each, report group mean error, cap-level absolute errors, pad-size difference error, eligible fraction, and failed numerical cases. Report a run-blocked estimate of mean A minus B with a confidence interval. Keep the per-run differences visible. Three reflow runs do not establish a production yield distribution.

The primary pad-size finding is supported only if its uncertainty interval resolves the sign and its magnitude agrees with the frozen error budget. A clearance result is a separate statement. A specimen can pass 185 micrometers only if its measured minimum minus its measurement uncertainty exceeds 185 micrometers. No pilot sample establishes a manufacturing yield guarantee. If group differences depend on an excluded run, a selected mapping, or final-offset reconstruction, report that dependency.

## Keep the data shapes small

Use one experiment specification, separate input and outcome tables, and a frozen prediction record. The conceptual fields are:

```text
ExperimentSpec
    revision, units, random_seed
    lower_geometry[A | B], upper_geometry
    mask_window, copper_finish, laminate, panel_and_singulation
    sphere_part, alloy, volume_conversion, material_scenarios
    pilot_count, held_out_count, runs
    height_reference, geometry_gate, clearance_limit, uncertainty_limit
    exclusions, analysis_method, artifact_hashes

PhysicalInput
    specimen_id, role[pilot | held_out], run_id, carrier_position
    lower_board_id, cap_id, lot_ids
    measured_pad_geometry, finish_heights, cap_mass
    sphere_lot_mass_and_size, liquid_density_source, reflow_profile_id
    measurement_uncertainties, input_freeze_hash

Prediction
    specimen_id, hypothesis[literal_rims | two_pad_cylinders]
    model[native | aligned_formula], request_without_height
    body_volume_convention, output_height_conversion
    result_status, numerical_diagnostics, predicted_gap, source_hashes

Outcome
    specimen_id, local_joint_id, measurement_method, image_id
    pad_top_gap, laminate_gap, mask_clearance, offset_x, offset_y
    contact_line_heights, wetting_status, void_status
    cap_minimum_clearance, cap_tilt, uncertainty, operator, timestamp
    assembly_failure_reason
```

The prediction command rejects nonblank outcome columns. The scoring command rejects missing specimen IDs, duplicated local joint IDs, unknown units, and an input freeze made after the outcome file. Missing measurements remain missing. They are not zero-height observations or excluded successful units.

The generator reads only `ExperimentSpec`. It emits native KiCad boards, matching Gerbers, panel and assembly drawings, and a site map. A separate verifier reads the actual exported copper flashes and mask polygons. It checks pad counts, pad diameters, pitch, isolated copper, and the common mask window. The analysis reads physical inputs and frozen predictions before it opens outcomes. These boundaries prevent CAD details, future measurements, and model requests from becoming one mutable file.

## Stop conditions and quote questions

Stop fabrication release if the lab cannot accept the 220 micrometer ENIG geometry, deliver the custom top coupon, identify the sphere lot, preserve the common mask window, or record the finished pad dimensions. Obtain a revised drawing and rerun DFM when a vendor changes a geometry. Do not let automatic CAM repairs silently alter the experiment.

Stop after the pilot if wetting reaches the laminate or mask, the cap contacts a fixture, ball handling adds unmeasured metal, cap warpage defeats the gap gate, or dimensional metrology misses its uncertainty target. These outcomes are evidence about whether this coupon can test the model. They do not justify proceeding to 48 expensive held-out assemblies.

The lab quote must separately identify panelization and cap singulation, incoming dimensional measurements, sphere characterization, 16 pilot assemblies, three held-out reflow runs, 48 full-volume measurements, 16 total sections, raw image delivery, uncertainty analysis, retained samples, and data completion. The quote must state which steps it subcontracts. No vendor is contacted or part purchased by this design document.

## Architecture judgment

| Criterion | Score out of 4 | Reason |
| --- | ---: | --- |
| Identifiable physical inputs | 3 | Measured balls, caps, and pads identify most inputs. Liquid density and sidewall mapping still need a pilot gate. |
| Outside-lab fabrication and assembly | 3 | Standard rigid PCB and ENIG processes suffice, but 3 mm cap handling and 220 micrometer pads require explicit acceptance. |
| Metrology access | 2 | A three-dimensional minimum-clearance claim needs a qualified X-ray microscopy measurement. Sections alone answer a narrower question. |
| Isolated lower-pad change | 4 | One top coupon, one solder lot, matched lower fabrication, and randomized loose-board reflow positions isolate the intended change. |
| Number of custom processes | 3 | Two passive PCB designs and one custom PCB cap avoid a custom silicon die, metal deposition, and fitted weight fixture. |
| Total | 15 | The experiment is quote-ready after a lab accepts the gates. It is not yet manufacturing-qualified. |

Model the Domain changed the file plan. Physical inputs, predictions, and outcomes stay in separate records. Prove It Works changed the fabrication and metrology gates. The lab must measure actual dimensions and verify CT against sections. A native board file or a nominal voxel pitch is insufficient evidence.
