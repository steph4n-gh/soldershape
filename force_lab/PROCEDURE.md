# Build, commission, and run the force test

Use the current templates and analyzer together. Measure relative transverse hot-rim displacement and its expanded uncertainty before the freeze and in each confirmation outcome. Require `abs(y) + U_y <= 0.5 µm`. Missing values or an exceeded bound make the endpoint inconclusive. The target is nominally zero transverse displacement. This apparatus policy does not establish physical accuracy for a nonzero transverse offset.

Reconcile shared uncertainty source IDs across `input_covariance.json` and `calibration.json`. Supply matching `source_unit` and standard uncertainty for each shared physical source, signed coefficients, and independent evidence that unlinked sources are independent. Do not put one temperature or calibration source under two different names. The residual calculation includes shared prediction/measurement covariance.

Use this procedure after the lab accepts the integration and issues approved fabrication drawings. The supplied reference CAD is for quotation. Stop at any failed gate. Keep the raw result and the reason for stopping.

## Establish the specimen and coordinate system

1. Assign a stable ID to every upper carrier, lower chip, solder preform, calibration, assembly attempt, and image set. Keep commissioning IDs separate from the 48 IDs in `allocation.csv`.
2. Prepare the nominal 200 µm circular wettable islands using the lab-approved thin-film stack and nonwetting surround. Record the finished diameter, roundness, film height, roughness, and boundary images. Reject tall exposed post sidewalls or an unmeasurable wetting perimeter.
3. Inspect the transparent upper cap and lower chip. Register optical fiducials to each actual metal rim. Measure the rim planes rather than the glass faces. Include the deposited metal height in the gap.
4. Define the lower rim center as `(0, 0, 0)`. Define the upper rim center as `(offset, 0, gap)`. Positive x offset is 40 or 120 µm. Positive z points upward. Gravity points downward.
5. Define the reported force as the solder's force on the upper rim. Positive x force acts along positive x. Positive z force separates the upper pad upward. A restoring x force for positive offset is negative.

Do not infer the force sign from a stage command. Moving the lower stage in negative x can create a positive relative upper-rim offset. Register the actual rims and apply a known force at the upper pad.

## Assemble the isolated load path

1. Use the approved custom attachment to connect the silica stalk and upper cap to the cool scalar force head. Record all moving masses and the center of gravity. Check full preload and overload limits before applying tare.
2. Mount the lower chip and heater independently. Keep their clamps, heater leads, thermocouples, shields, and purge lines clear of the upper force-bearing carrier.
3. Confirm that the upper pad has exactly one mechanical load path to ground through the stalk, approved attachment, and sensor. Inspect the complete coarse and fine motion envelope for unintended contact.
4. Position the upper and lower wettable planes horizontally. In both indexed axis configurations, keep the bridge and gravity orientation unchanged. Reconfigure the cool sensor adapter between specimen blocks while cold.
5. Measure compliance in the sensed and unsensed directions. Include sensor, attachment, stalk, cap bond, and lower support. Do not treat a beam calculation as an assembled measurement.
6. Install the approved chamber and noncontact thermal shields. Measure sensor-body temperature during a full thermal run. Use independently supported pad-adjacent temperature probes or validated optical thermometry.
7. Establish two calibrated side views and the upper-rim view through the transparent cap. Demonstrate that the full contact boundary can be observed or bounded. Two clear silhouettes alone do not prove that a hidden section remains pinned.
8. Set coarse travel windows around each target offset. Use fine feedback to hold the actual rim positions. Do not attempt a 0 to 120 µm scan on a 100 µm fine stage without coarse indexing.

The vertical load from the bare nominal stalk is about 339 µN before the cap and attachment. In lateral mode this becomes a cross load. Supplier approval must cover both indexed configurations. Taring removes a readout offset, not the mechanical preload.

## Qualify the measurement before solder confirmation

1. Calibrate force in both signs through the assembled upper carrier over the expected range. Include small forces near the 7.6 µN example endpoint and loads near 150 µN. Use a traceable transfer method with adequate uncertainty.
2. Apply representative orthogonal forces and moments. Measure the axis response, residual cross-axis response, hysteresis, and compliance in each indexed configuration. Verify force sign at the actual pad.
3. Verify calibration using force points withheld from the fit. Record pre-test and post-test checks. Stop if drift or a changed attachment invalidates the calibration.
4. Run the entire motion sequence without a solder bridge. Repeat with heat off and on, then purge off and on. Keep raw force, rim coordinates, sensor temperature, local temperatures, and controller commands synchronized.
5. Quantify settling, drift, convection, cable forces, electrostatic effects, and the uncertainty of all blank corrections. A blank with a removed cap or changed load path is not equivalent.
6. Demonstrate corrected individual-force expanded uncertainty at most 2 µN and observed-volume-contrast uncertainty at most 3 µN. Include shared biases and covariance. Unknown terms cannot be zero.
7. Demonstrate initial hot relative-coordinate expanded uncertainty at most 0.5 µm, tilt at most 0.1°, and coordinate drift at most 0.5 µm during the scoring dwell. Tighten these targets when the native input-sensitivity budget requires it.
8. Select a fixed motion rate, dwell, sampling rate, filtering rule, stability rule, and blank interpolation from commissioning data. Include approach reversal and a slower sequence. Register the final rules before confirmation.

The proposed stability criterion must resolve the uncertainty budget within a fixed maximum dwell. The lab must set and document that maximum before confirmation. If the force or rims continue drifting, preserve the trace and classify the method as inconclusive. Do not extend a dwell until it happens to agree.

The current analysis requires justified coverage factor `k=2`. If effective degrees of freedom require a larger factor, revise and register the protocol before confirmation. Do not enter `2` by convention.

## Qualify material inputs and wetting

1. Identify the alloy batch, composition, liquidus, temperature, atmosphere, oxide-removal method, and handling history. Obtain chamber acceptance for the actual chemistry.
2. Establish liquid density and surface tension independently at the chosen temperature and atmosphere. Include method evidence and uncertainty. Do not fit either value to the confirmation force outcomes.
3. Determine transferred liquid metal volume independently. Convert measured cold mass or geometry using the actual liquid density. Account for residue, metal-film dissolution, oxidation, and transfer loss.
4. Demonstrate stable wetting on sacrificial bridges. Confirm that both contact lines remain at the measured circular rims during the target motion and dwell.
5. Commission the 40 µm lateral endpoint first. Commission the larger normal-force signals on separate specimens before attempting the 7 nL, 120 µm upward-sign endpoint.
6. Preserve reverse approaches, slower-motion results, thermal cycles, failed wetting, and hysteresis. Define an explicit out-of-domain rule when either contact line depins, remains hidden, or wets a sidewall.

The modeled interface is solder against gas. Flux can introduce another interface, residue force, and an altered contact boundary. An unqualified flux process cannot be repaired by entering a convenient surface tension. Nitrogen alone does not prove that oxides are absent.

## Freeze inputs before confirmation forces

1. Generate a new input directory using the command in `README.md`. Retain the fixed 48-specimen allocation and its volume order within each pair.
2. Independently measure the geometry and liquid-volume inputs for every allocated specimen. For gap and offset, use a geometry-only hot registration with the force outcome channel sealed or blinded. A cold-stage setpoint is insufficient.
3. Record the input measurement time, evidence location, and uncertainty source components. Include shared optical scale, temperature, material, and calibration biases once with their signed coefficients.
4. Complete the commissioning and coverage evidence. Keep `outcomes-template.csv` blank and separate. Do not create `outcomes.csv` in the input directory.
5. Run `freeze` into a new directory. Review numerical failures and scope warnings. Register the exact returned manifest SHA-256 independently with the lab before acquiring confirmation force outcomes.
6. If a specimen is reheated or remounted after registration, verify the actual hot gap, offset, temperature, volume stability, and wetting history against the frozen inputs. A departure outside the declared uncertainty or a changed process makes that specimen inconclusive.

The current protocol freezes all 48 input records together. Sequential hot registration and later remounting may be cumbersome. Quote this work explicitly, including thermal-history effects. A block-by-block freeze or a new process needs a revised protocol before confirmation. Do not silently substitute nominal geometry for the required independent measurements.

## Acquire independent confirmation outcomes

1. Use three independent preparation blocks. Within each block, follow the recorded randomized volume order for each axis, offset, and replicate pair.
2. Prepare one new bridge for each allocated specimen. A pair contains separate 5 and 7 nL bridges. Keep x and z specimens separate. Do not reuse a bridge to increase the sample count.
3. Record the pre-run no-bridge blank and calibration check. Establish the qualified thermal condition and verified actual hot coordinates.
4. Execute the frozen motion and dwell sequence. Acquire raw force, rim coordinates, local and sensor-body temperatures, and all contact-line views with a common time reference.
5. Apply only the frozen calibration, correction, filtering, and dwell-selection rules. Record corrected force with its evidence references. Preserve the raw time series and correction calculations.
6. Verify both pinned contact lines, stable force, actual gap and offset, temperature, tilt, and dwell drift. Record failed and unobserved conditions explicitly.
7. Repeat the post-run blank and calibration check. If the bracket, attachment, optical calibration, chemistry, or temperature changes, stop and assess the freeze before proceeding.
8. Fill a new outcome file after the freeze. Use the statuses `measured`, `measurement_missing`, `assembly_failed`, or `out_of_domain`. Keep a reason for every allocated specimen in the lab disposition log.
9. Run `verify` and `score` with the independently registered digest. Return the score with the complete raw package. Preserve disagreements and inconclusive endpoints.

The primary lateral contrast is `Fx(7 nL) - Fx(5 nL)`. With two negative restoring forces, it also equals the 5 minus 7 nL restoring-magnitude contrast. The old 120 µm example contrast is about +10.070 µN. The physical test uses newly frozen values at measured inputs.

## Keep a complete raw record

Use `templates/raw-timeseries.csv`, `templates/transfer-calibration.csv`, and `templates/hot-blanks.csv` as blank starting points. Record the following channels or their documented equivalents in a time-indexed CSV. Preserve the acquisition software's original files too.

| Field group | Required content |
| --- | --- |
| Identity | Specimen, block, axis, pair, process, carrier, calibration, blank, and freeze digest |
| Time | UTC start, monotonic time, sample interval, dropped samples, and image frame timestamps |
| Force | Raw signal and units, calibrated force, blank correction, corrected upper-rim force, filter, and uncertainty record |
| Geometry | Both rim coordinates, relative gap and x offset, transverse offset, tilt, uncertainty, and feedback command |
| Thermal | Both pad-adjacent temperatures, sensor-body temperature, heater state, purge state, and flow |
| Boundary | Raw images, rim overlays, pinning assessment, liquid-volume evidence, residue, and post-run inspection |
| Disposition | Assembly and measurement status, fixed dwell window, drift, reversal response, deviations, and exclusion reason |

The analyzer's summary CSV does not replace these raw records. Link each `measurement_evidence`, `wetting_evidence`, and `stability_evidence` value to the retained files.

## Stop or reduce the question

Stop confirmation if the approved load path changes, the sensor exceeds a rated limit, calibration fails, either rim is unobservable, or the force budget fails. Classify failed physical boundaries as out of domain. Classify insufficient measurement capability as inconclusive. A qualified discrepancy with the frozen prediction is evidence against the model in that domain.

If only the small 120 µm contrast fails, quote lateral-only 40 µm commissioning as the smaller experiment. Keep the 120 µm normal sign unresolved. Run 200 µm offset and 60 µm compressed-gap diagnostics separately, with their original warning and failure expectations retained.
