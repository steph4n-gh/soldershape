# Candidate A: remote axial silica carrier, indexed cool single-axis sensing

Status: design candidate for quotation and commissioning. Not vendor accepted, fabrication released, or physically validated. This report proposes interfaces; it does not implement them.

## Caller and artifact use

A lab opens `fixture.step` and the dimensioned drawing, replaces the expressly blank sensor/stage mounting interfaces with its approved hardware, and quotes the hot blank and calibration gate before specimens. The scientific owner freezes material and geometry inputs, runs native predictions, and issues specimen IDs. The lab returns observations with instrument evidence and images. The scorer reports axis-specific agreement, rejection, or inconclusive status. It never turns a successful x result into a z validation.

Proposed artifact entry points: `force_fixture/tools/build_cad.py`, `force_fixture/tools/verify_cad.py`, `force_fixture/tools/analyze.py freeze INPUTS METADATA OUT`, `... score FROZEN OUTCOMES OUT`. These are proposed commands, not existing tools.

## One core record

`ForceRun = {specimen_id, independent_reflow_id, block_id, axis: x|z, geometry_input_id, material_input_id, calibration_id, carrier_id, measured_rim_coordinates, force_observation, uncertainty_terms, evidence_files}`.

Geometry has actual lower/upper rim diameter, hot gap, signed x offset, volume and tilt with units, uncertainties and covariance. Material has independently measured alloy, temperature, surface tension and density. Calibration identifies sign, sensitivity, cross-axis matrix, assembled-carrier compliance, hot-blank correction and coverage rationale. Outcome is absent in the prospective freeze. Shared calibration uncertainty remains shared. No force fitting changes a frozen input.

Separate records identify CAD revision, lab-approved mounting revision and sensor rated limits. An unfilled limit blocks machining release, not document preparation.

## Architecture and physical datum

Use one approximately ±2 mN cool commercial sensor with one vertical fused-silica load carrier. The solder bridge always lies between horizontal circular rims. Gravity remains negative z. The upper rim is on the lower polished end of the vertical carrier; its face points down. The lower rim is on a fixed heated chip facing up. The only force-bearing path from the upper pad to ground is carrier, approved tip attachment and sensor. No pad thermocouple, cable, second guide or clamp contacts the moving carrier.

For x, orient the sensor's sensitive axis horizontally. For z, index the cool sensor bracket so its sensitive axis is vertical, using a separate upper carrier and independent specimens. A lab-approved attachment changes between indexed positions; the rod and both pad faces remain vertical/horizontal respectively. Do not tip the whole hot joint. Indexing is between runs, not while molten.

Lower rim center is `(0,0,0)` and upper rim center `(offset,0,gap)`. Nominal gap is 0.150 mm. Nominal offsets are 0.040 and 0.120 mm. Both physical pads are nominal diameter 0.200 mm. Actual hot values and material inputs determine the frozen predictions.

## Dimensioned concept suitable for neutral CAD

| Part | Candidate dimensions and interface | Release condition |
|---|---|---|
| Upper carrier | Fused silica, diameter 1.00 mm, free length 20.00 mm, polished face normal to rod axis. Lower end at z=0.150 mm. | Measure diameter, straightness, face normal, metallized boundary and actual assembled stiffness. |
| Upper wettable island | Diameter 0.200 mm on the rod end, surrounded by nonwetting material out to the 1 mm face. Thin deposited metal, no exposed tall post sidewall. | Lab selects and measures an alloy-compatible metallization, thickness, dissolution and nonwetting process. Nominal drawing is a boundary target, not a proven process. |
| Lower chip | 10 × 10 × 0.50 mm polished fused silica or alumina, one 0.200 mm wettable island at center. | Record actual substrate, finish, island thickness, nonwetting surround and hot coplanarity. |
| Lower thermal carrier | 24 × 24 × 3 mm alumina plate; central 10.2 × 10.2 mm shallow locating pocket, depth 0.20 mm; two external low-force hold-down fingers. | Lab heater mating face and thermal uniformity accepted. No finger over the viewing region or upper load path. |
| Cool base | 80 × 80 × 8 mm aluminum tooling plate with four M4 clearance holes on a 60 mm square. | These are internal fixture holes only, not a vendor stage pattern. Lab supplies a separate stage adapter. |
| Cool upright | 40 × 10 × 60 mm bracket with orthogonal reference faces and two M4 clearance holes 20 mm apart per face. | Sensor-specific plate stays a solid 30 × 30 × 3 mm blank until approved envelope, holes, tip and cable routing are supplied. |
| Radiation shields | Fixed thin reflective plates at approximately z=5 and 12 mm, each with diameter 4 mm noncontact aperture. | Confirm full coarse/fine motion and misalignment cannot touch the 1 mm carrier; shield neither obscures side views nor grounds its load. |
| Chamber | Lab enclosure around lower heater and bridge, with opposing x windows plus orthogonal y access. | No promise that a stock Linkam chamber accepts this drawing. Lab may quote an existing custom hot-stage chamber. |

The base mounting plane and sensor bracket are cool external structure. A separate insulating pedestal positions the lower thermal carrier at the joint datum. Its length and heater interfaces are lab-defined because the chosen chamber determines them. Do not issue fixed bulkhead holes before chamber selection.

The complete sensor-borne moving mass, including carrier and attachment, should be no more than 100 mg as a design target. Its weight is about 0.981 mN. A ±2 mN sensor still needs measured preload, both force signs and overload margin. The bare rod is about 34.6 mg, or 0.339 mN. Taring does not remove this load. In x mode the same weight is a cross-axis load and must satisfy the supplier's limit. No force-bearing counterweight is assumed.

The upper carrier end bonds to a lab/supplier-approved cool microtab. A lightweight adhesive bond or mechanical termination is a quote item, with no invented tip hole pattern. The bond stays cool, away from the solder atmosphere. A chunky commercial rod clamp would likely violate mass and compliance goals. If the sensor supplier rejects a custom attachment, this architecture fails before machining.

## Positioning, access and operation

Mount the cool sensor on a coarse XYZ positioner plus fine XYZ stage. The lower chip is fixed for each axis block. Use coarse indexing to center the fine range on each target offset. A nominal 100 µm fine scanner can cover 40 to 120 µm if centered at 80 µm, but cannot additionally reach zero in that same range. No command may rely on advertised 100 µm travel to execute a 0 to 120 µm scan. Use separate indexed windows with local coordinate registration.

Use two calibrated side views near the pad planes, along x and y. Reserve a clear optical corridor of at least 8 mm diameter around z≈0.15 mm on both sides. The rod's 1 mm body obscures top viewing. Therefore angled views and a prequalified contact-line reconstruction are required. Both rims must be observable enough to establish full pinning. If hidden portions cannot be bounded, classify that specimen as outside domain rather than infer pinning from one silhouette.

Hot relative coordinates come from pad-rim images, or fiducials registered to those rims. Stage encoders and mirrors on the carrier alone do not prove the gap. Servo slow correction to maintain actual rim coordinates, with a noncontact thermal shield. Log raw coordinates and forces together. Two near-pad fixed thermocouples and sacrificial temperature-mapping specimens establish local temperature without adding a moving lead.

Use a gas and oxide-control process explicitly accepted by the chamber owner and alloy expert. Nitrogen alone does not prove clean molten solder. Flux chemistry can change the modeled interface. No hydrogen or formic-acid capability is assumed. Independently establish the selected molten alloy's density, surface tension and wetting stability before freezing force predictions.

## Sources versus engineering unknowns

The component basis is the primary-source evidence in `metrology.md`: Oxford FT-S2,000 force range/resolution, PI P-611.3S travel, Heraeus fused-silica properties, Linkam gas restrictions and attocube temperature limitations. Those sources establish candidate capabilities, not integrated hot accuracy. The CAD's internal base/bracket dimensions are engineering choices, not manufacturer specifications.

The 20 mm × 1 mm rod has estimated transverse stiffness 1335 N/m and bends about 0.093 µm under 124 µN. These room-temperature beam estimates exclude sensor, bond and thermal effects. The rod's approximately 1.88 µm uniform expansion over 200 K already exceeds an initial 0.5 µm coordinate target. Local hot-rim feedback is necessary. A measured thermal model and sensor-body temperature record decide whether 20 mm isolation is adequate; length alone does not certify it.

## Before-code and commissioning gates

1. Neutral CAD must contain closed solids with the stated pad planes, 0.150 mm nominal gap, 0.040/0.120 mm offsets, no upper load bypass and collision-free motion. Sensor and chamber blanks must be conspicuously unresolved interfaces. Keep fabrication status quote-ready.
2. Lab and sensor supplier accept the tip attachment, mass, cross-axis load, overload margin and cool-body temperature. A rejected interface is a hard stop for this carrier, not a reason to silently change the experiment.
3. Perform assembled-carrier transfer calibration in both force signs and representative cross loads/torques. Verify sign at the pad. Quantify the axis response matrix, hysteresis and compliance in each indexed orientation.
4. Run bridge-free hot blanks through each motion, with heat and purge controls. Measure drift, convection, cable effects, electromagnetic/electrostatic effects and temperature gradients. Require corrected individual force expanded uncertainty U≤2 µN and measured 5/7 nL contrast U≤3 µN. Unknown terms cannot be zero.
5. Set final geometry/material uncertainty limits using native sensitivity runs. Initial targets are U≤0.5 µm relative rim coordinates, ≤0.1° tilt and ≤0.5 µm coordinate drift per dwell, but these do not override the force budget. Require combined predicted/observed lateral contrast U≤3.357 µN and combined normal U≤3 µN for the declared endpoints.
6. Commission x at 40 µm first, then 120 µm. Commission z at 40 µm on separate specimens before attempting the small positive 7 nL/120 µm endpoint. Preserve unsuccessful blocks and all missing specimens in the denominator. Plan independent reflows and randomize volume order within axis blocks.
7. Each dwell must show stable force and actual rim coordinates; include approach reversals and slower motion. Pinning, gap, material and stability failures classify the result as out of domain or method inconclusive. Numerical agreement is not physical validation without these gates.

## Strongest counterexample and alternative

The bridge's concealed upper contact line may depin on an oxide/metal transition while the two side silhouettes still look pinned. This can produce a repeatable force that disagrees with the model for the right reason, or agrees accidentally. A second major failure is a rejected microtab attachment or cross-axis load rating. Those cannot be repaired with more averaging.

If contact-line visibility defeats the 1 mm rod end, the cheapest decisive alternative is a smaller transparent cap on a shaped carrier with independent optical access, quoted as a new boundary design and requalified mechanically. If integrated U misses the 120 µm contrast gate, retain a lateral-only 40 µm commissioning experiment and report the small-sign endpoint inconclusive. A purpose-built hot two-axis flexure is a separate, costlier architecture, not an automatic extension of this one.
