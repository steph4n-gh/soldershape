# Candidate B: simultaneous cool two-axis force head

## Caller workflow

The lab mounts a commercially calibrated two-axis sensor outside a small hot chamber and attaches one thermally isolated upper-pad carrier. A separately supported XYZ stage holds the lower pad. With both pads horizontal, the stage establishes a 150 µm hot rim gap and 40 or 120 µm lateral offset. The lab records Fx, Fz, both rim coordinates, pad tilt and temperature concurrently. Every held-out specimen supplies both force components, without re-indexing the force head between axes.

Quote this as a custom integration requiring supplier approval, hot-blank commissioning and a measured uncertainty budget. The candidate is not build-ready merely because the sensor is commercial. Run 40 µm large-signal commissioning before the 120 µm small-sign endpoint. Keep 200 µm offset and 60 µm compressed gap as separate diagnostics.

## Core record and interfaces

```text
ForceRun {
  specimen_id, run_block, process_id, calibration_id,
  board_pad_id, upper_carrier_id, cold_metrology_id,
  target: {diameter_um: 200, gap_um: 150, volume_nl: 5|7,
           offset_x_um: 40|120, gravity_axis: "-z"},
  frozen_prediction_digest,
  observations: {time_s, raw_fx_uN, raw_fz_uN,
    lower_rim_xyz_um, upper_rim_xyz_um, tilt_xy_deg,
    lower_temperature_C, upper_temperature_C, sensor_body_temperature_C,
    contact_line_images, zero_control_id},
  corrections: {axis_response_matrix_id, thermal_blank_id,
    covariance_id, calibrated_uncertainty_budget_id},
  status: "commissioning"|"confirmation"|"out_of_domain"|"inconclusive"
}
```

`commission_fixture(config, blanks, calibration) -> CommissioningReport` must reject missing uncertainty terms or an unstable hot zero. `freeze_force_protocol(inputs, measured_process, calibration) -> FrozenPredictions` consumes independent input measurements before held-out force data. `score_forces(frozen, observations) -> ConditionalAgreementReport` retains raw vector samples and covariance; it never fills missing observations or retunes gamma to the force outcome. Reuse existing `JointSpec`, native solver and digest patterns. Keep the new force record separate from the height-coupon experiment.

## Physical architecture and dimensional envelope

Use an Oxford/FemtoTools FT-S20,000-2Axis as the quoted candidate. The manufacturer brochure lists ±20,000 µN per axis and 100 nN noise at 10 Hz. It does not establish the custom attachment's calibrated uncertainty, stiffness, permissible moment, body-temperature limit or hot integration. Obtain those values before finalizing its adapter. [NMT04 manufacturer brochure](https://143319969.fs1.hubspotusercontent-eu1.net/hubfs/143319969/PDFs/Brochures/FT-NMT04_Brochure.pdf).

A proposed 20 mm long, 1 mm diameter fused-silica stalk extends horizontally from the cool head. Its hot end carries a small horizontal transparent coupon whose lower face contains a thin, measured 200 µm wettable island and nonwetting surround. A separate horizontal lower coupon carries the opposing island. The complete pad pair remains horizontal with gravity along negative z. The stalk transmits x mostly axially and z by bending; no secondary hot-end support touches the moving carrier.

Proposed custom geometry is a 2 × 2 × 0.3 mm transparent upper coupon and a 5 × 5 × 0.5 mm lower coupon. These are design envelopes, not qualified thin-film fabrication specifications. Put the upper wettable island near the free coupon edge to expose the liquid outline. Dimension its setback and the optical ray paths in CAD before choosing the final microscope. Observe the lower outline directly and the upper rim through the transparent carrier where metal allows. A hidden or ambiguously wetted rim invalidates the pinned-rim test.

Use the manufacturer-approved sensor attachment at the cool end. The package may provide a dimensioned stalk clamp and chamber-independent breadboard, but must leave the sensor bolt pattern and attachment insert as a separately released vendor-specific interface. Do not draw guessed vendor holes or claim compatibility from a rendering.

A cool coarse XYZ stage must reach the 120 µm offset; a fine scanner provides local correction. The PI P-611.3S closed-loop travel is only 100 µm per axis, so it cannot alone span zero to 120 µm. Its internal encoder does not measure stalk bending or hot expansion. [PI specification](https://www.pi-usa.us/en/products/piezo-flexure-nanopositioners/xyz-piezo-flexure-nanopositioning-stages/p-6113-nanocube-xyz-piezo-stage-201700/).

Use a lab-designed radiant or conductive microheater with independent support, purge enclosure and optical access. A stock Linkam HFS600E-PB4 has a 22 mm sample area and electrical probes; its page does not establish this stalk insertion, force isolation or side-view access. Either obtain accepted custom integration drawings or use a chamber built by the selected lab. Argon/nitrogen are candidate purge gases; Linkam explicitly forbids helium/hydrogen in its stages. Chemistry remains a supplier/lab acceptance item. [Linkam stage](https://www.linkam.co.uk/hfs600e-pb4), [stage support](https://www.linkam.co.uk/support/stages/general).

Keep two calibrated side-view optical paths approximately orthogonal, with fiducials registered to both actual rims. A cool interferometer can improve carrier motion measurement, but cannot replace rim registration or prove hot-window accuracy. Sensor leads, thermocouples, purge plumbing and heater supports must not create a parallel force path. Measure pad-adjacent temperature with independently supported probes or validated optical thermometry; do not attach an uncharacterized spring-like wire to the force-bearing carrier.

## Mechanics and uncertainty implications

For the proposed silica stalk, room-temperature E = 72.5 GPa gives transverse stiffness about 1,335 N/m. A 124 µN load bends it about 0.093 µm. Its roughly 34.6 mg mass creates a 339 µN vertical preload, well inside the nominal 20 mN force range, before other carrier and sensor loads. These estimates omit clamps, bonds, sensor compliance and moments. A 200 K uniform rise lengthens it about 1.88 µm. Local hot rim metrology and correction therefore remain mandatory. [Heraeus material properties](https://www.heraeus-covantics.com/brands/clear-fused-quartz).

At the repository's example inputs, the 120 µm lateral difference is 10.070 µN and the small upward prediction is 7.619 µN. Two-axis 0.1 µN advertised noise does not disqualify this candidate, but is only a small part of the measurement budget. The decisive unknowns are assembled accuracy, cross-axis/moment correction, hot zero, carrier temperature gradients, rim position and wetting.

Use the same proposed gates as Candidate A: individual corrected-force expanded U ≤ 2 µN; measured lateral-contrast U ≤ 3 µN; combined measured/predicted contrast U ≤ 3.357 µN; combined absolute normal U ≤ 3 µN. Coverage factor and covariance must be justified. Two components from the same specimen share geometry, calibration and time-dependent nuisance terms. Preserve this covariance instead of treating paired measurements as independent. Gamma 0.48 N/m and density 9 g/cm³ are example inputs, so independently characterize the actual alloy/temperature and recompute the frozen predictions.

A simultaneous two-axis sensor improves pairing and observes cross-axis behavior during the same equilibrium. It also adds an inseparable vector calibration matrix and torque sensitivity. Full-scale range is ten times the ±2 mN candidate; there is no evidence that comparable calibrated absolute accuracy follows from the noise specification. The lab must quote uncertainty near 10–150 µN, not only percent full scale or best-case repeatability.

## Smallest decisive commissioning

1. Obtain written supplier limits for a custom stalk and representative axial, transverse and moment loads. No hardware order is justified from the public brochure alone.
2. On the proposed assembled carrier at room temperature, apply traceable ±x and ±z forces covering approximately 0–150 µN, plus representative moment and cross-axis loads. Fit the response matrix using commissioning data; verify on held-out force points. Confirm resolution and range without confusing them with accuracy.
3. Run the same no-bridge stage sequence with heat and purge separately off/on, then together at the intended temperature. Record both axes, sensor temperature and actual rim coordinates through full dwell times and reversals. Quantify correlated zero drift and thermal settling. Reject U > 2 µN, hidden load paths, or nonstationary blanks.
4. Establish two-rim gap/offset expanded U initially ≤ 0.5 µm and tilt ≤ 0.1°, then tighten from actual native force sensitivities. Demonstrate closed-loop correction at 40 and 120 µm offsets with both force channels live. Do not servo force to the predicted value.
5. Demonstrate stable pinned contact lines and independently measured liquid volume/material inputs on sacrificial commissioning specimens. Run 40 µm large signals. Freeze the actual-process predictions and all exclusion rules before held-out confirmation.
6. Allocate 5 and 7 nL specimens across at least three independent assembly blocks and randomized order. Each specimen is one independent joint; repeated frames and repeated displacements are within-specimen observations, not new replication. Preserve unstable, depinned and missing cases in the disposition table.

## Comparison and choice

| Criterion | Simultaneous two-axis candidate | Cool ±2 mN indexed single-axis candidate |
| --- | --- | --- |
| Main advantage | Fx/Fz share the actual equilibrium, thermal history and volume; no re-index drift between components. | Smaller-range commercial head, simpler scalar calibration, lateral-only first milestone. |
| Main liability | Two-axis calibration, torque behavior, custom mounting and quoted low-force accuracy remain unestablished. | Separate axes require independent specimens and blocks; between-axis variability cannot be removed by pairing. |
| Geometry control | Still requires external actual-rim metrology and no bypass support. | Same requirement; indexing must preserve horizontal joint orientation. |
| Honest first result | A commissioned vector measurement, if both uncertainty budgets pass. | A commissioned lateral result, with normal force deferred if required. |
| Expansion pressure | Greater temptation to purchase a broad microtester before proving hot accuracy. | Easier to limit the first quote to one decisive force direction. |

Prefer the indexed single-axis design for the first RFQ unless a lab already owns the two-axis head and can demonstrate the complete hot-carrier U ≤ 2 µN gate. Graft this candidate's paired vector recording and cross-axis matrix requirements into the primary design where useful. A 40 µm lateral-only fallback is cheaper if normal force remains unresolved; it does not validate the 120 µm upward sign.

A custom optical flexure or weighing balance is a further alternative, but it creates a new force transducer requiring traceable hot calibration, parasitic-motion control and drift characterization. The Mettler XPR2U's 0.1 µg readability is promising for a normal-force cross-check, not a ready lateral/hot fixture. It should not replace a documented commercial force head without an existing lab capability. [Mettler product specification](https://www.mt.com/us/en/home/products/Laboratory_Weighing_Solutions/microbalances/XPR2U.html).

## Strongest counterexample and status boundaries

If a supplier will not approve the 20 mm stalk or the lab observes temperature-dependent cross-axis/moment coupling above the uncertainty budget, simultaneous sensing becomes an expensive source of ambiguity. A beautiful CAD assembly and 0.1 µN noise specification cannot rescue it. Conversely, a lab with an already commissioned vector head can make this candidate less risky and more informative than building an indexing adapter.

This design can become quote-ready after CAD, drawings, protocol and uncertainty allocations agree. It becomes lab-accepted only on written integration acceptance, fabrication-released only on approved supplier-specific interfaces, and physically validated only after independent held-out observations pass the frozen method. No such acceptance, calibration or physical data is claimed here.
