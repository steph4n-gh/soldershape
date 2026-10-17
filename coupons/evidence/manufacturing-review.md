# Review the outside-laboratory manufacturing package

This independent review checked the unit CAD, actual fabrication exports, experiment specification, allocation, bill of materials, procurement instructions, procedure, and quote request. It did not contact a supplier or establish fabrication acceptance. The README and printable handoff were still being prepared and are outside this review snapshot.

## Findings to resolve before handoff

### P1. State the cap orientation explicitly

`PROCEDURE.md` asks for the frozen orientation, but `allocation.csv` supplies only carrier rotation. The cap has a square outline and a rectangular five-column, four-row pad array. Turning a cap 90 degrees relative to its site changes the pad centers and prevents their intended alignment. The native cap has its pads on B.Cu and an L-shaped datum on F.SilkS, so the files contain enough information to give an unambiguous instruction.

Specify that F.SilkS faces outward and B.Cu faces the carrier. Align the outer-face L corner to the carrier's A1 corner in a common top view. Keep the cap and site axes aligned before rotating the entire carrier for its oven orientation. Include a common-view assembly drawing. Do not mirror bottom-layer CAM manually.

### P2. A 180-degree rotation preserves the arm diagonal

The carrier fixes C220 at S01 and S04 and C270 at S02 and S03. The current allocation alternates carrier rotations of 0 and 180 degrees. Both angles preserve the C220 diagonal in an external oven coordinate frame. Thus a reproducible diagonal oven pattern can remain confounded with pad diameter. The mirrored horizontal pairs already cancel a first-order horizontal gradient, but they do not cancel every spatial pattern.

Balance 0 and 90 degree carrier orientations within each confirmatory run, or use an equivalent allocation that exchanges the diagonals. Give the cap-orientation instruction above independently of carrier orientation. A physical effect tied to the carrier's own fixed sites still remains inseparable from arm without a second carrier layout that exchanges the pad diameters. State that limitation if retaining one carrier layout. This coupon can support a conditional comparison under the specified construction and process.

### P2. Define the sphere-screening uncertainty decision rule

The procurement instructions require accepted diameters from 317.5 through 322.5 micrometers and expanded diameter uncertainty at or below 1 micrometer. They do not state whether the acceptance interval applies to the measured center or the uncertainty interval. Those interpretations permit different physical size distributions.

For a guarded acceptance rule, require measured diameter minus its expanded uncertainty to be at least 317.5 micrometers and measured diameter plus its expanded uncertainty to be at most 322.5 micrometers. Otherwise state the chosen acceptance rule and include the expanded possible diameter range in the unequal-volume sensitivity. Twenty-ball mass controls average volume, but it does not remove volume differences between joints.

## Checks against the actual files

`python3 coupons/tools/verify_boards.py` completed successfully. It parsed the actual exported Gerber and drill files and read the KiCad DRC reports. It reported the following geometry digest.

`9015bd4a21b7a26b3b89d791e19c4d54c504a6e759faf402d01f85bec561eb96`

- The carrier outline is 40 by 40 mm. It has forty 220 micrometer pads, forty 270 micrometer pads, three 1 mm fiducials, four common array mask windows, and two 3.2 mm nonplated holes. Its opposite copper layer is empty.
- The cap outline is 3 by 3 mm. It has twenty 280 micrometer pads on B.Cu at 0.5 mm pitch, one 2.8 by 2.3 mm mask window, no holes, and no opposite-side copper. Direct inspection of the native file and Gerbers confirmed the array and layer assignment.
- The arrays contain isolated copper flashes and no tracks. The cap's nearest nominal pad-to-outline distance is 0.36 mm. The smallest mask-opening margin around an outer 280 micrometer pad is 0.26 mm.
- Both supplied DRC reports contain zero violations and zero unconnected items. These reports and the export checks verify the supplied files. They do not verify a fabricator's eventual panel or CAM changes.
- The allocation has 48 unique caps. Confirmation has 24 caps, twelve per arm, twelve matched pairs, and eight caps in each of three runs. The twenty joints under one cap are correctly treated as dependent observations.

The cap's L-shaped orientation datum is present on the outer silkscreen. Its nominal stroke margin to an edge is 0.175 mm. Require the final panel and singulation process to preserve that datum or supply a documented replacement datum before measurement.

## Manufacturing conditions that are already stated correctly

The unit files do not specify a production panel. The procurement instructions assign panel engineering, tooling, clean CNC singulation, and final CAM approval to the fabricator. This is appropriate for a quote package. A 3 mm cap is a small routed part and the laboratory still needs a specific accepted handling and singulation method.

The package distinguishes nominal copper thickness from finished copper plus nickel and gold. It requests incoming measurements and forbids silent pad enlargement, mask encroachment, added metal, and finish substitution. It also requires at least 0.2 mm finished pad-copper clearance to the cap's routed edge. The 0.36 mm nominal margin does not guarantee that finished clearance under every routing tolerance. The stated incoming check and written DFM acceptance are necessary.

The common mask opening exposes the complete pad rim without connecting traces. ENIG can be specified for isolated islands without adding an electrical bus to the delivered coupons. The package still requires evidence of the actual wetted boundary. The exposed copper sidewalls must not be assumed to match a pinned top-rim model solely because the CAD pads are circular.

The measured bare cap mass includes its finish and marking. Solder is excluded from the external cap load. The procedure forbids contacting support, spacers, adhesive, and measurement leads on scored caps during the molten hold. It reserves separate parts for contact thermal profiling.

The parts list explicitly marks exact 320 micrometer sphere supply as unconfirmed. It supplies no invented stock number, price, MOQ, lead time, or turnkey laboratory capability. Its counts cover 48 allocated twenty-ball kits plus twelve kit equivalents of accepted handling spares.

The metrology request distinguishes pad-face gap from mask-to-cap underbody clearance. It requires all twenty joints for a whole-cap minimum, calibrated uncertainty rather than voxel pitch, and registered sections before claiming the method works. It treats hot-state observation as a separate unverified option. Cold geometry alone does not qualify liquid equilibrium. These conditions are strict but appropriate to quote before spending on confirmation.

## Primary-source check

The [JLCPCB capability page](https://jlcpcb.com/capabilities/Capabilities?type=1) lists 3 by 3 mm as an FR4 minimum and recommends panelization for small parts. It distinguishes routed copper-edge clearance of at least 0.2 mm from V-cut clearance of at least 0.4 mm. It requires ENIG for 0.20 to 0.25 mm BGA pads. Its regular routing dimension tolerance is plus or minus 0.2 mm. These published limits support requesting a DFM review. They do not confirm this design's finished clearance, pad tolerance, panel, or assembly acceptance.

The [Indium sphere page](https://www.indium.com/products/solder-spheres/) lists Sn37Pb Indalloy 106 within its specialty-sphere capabilities. This does not establish an available 320 micrometer grade or the requested screening tolerance. The package correctly leaves those as quote conditions.

## Snapshot and verdict

The reviewed `experiment.json` SHA-256 was `7e8110f1a2cba1fa1be57443030fe698df2538b4d45a54b0e89c0e5d13342fb7`. The reviewed `allocation.csv` SHA-256 was `aa77271194f5e29d2d4c4c9d5bde62eaba3a356fb5c6d41497c96b8f850d8f4c`.

Resolve the orientation, external-position balance, and sphere acceptance rule before handing the finished package to a laboratory. No additional fatal CAD defect was found in this snapshot. The result remains a staged quote and pilot package. It is not a fabrication release or a claim that the laboratory can meet the proposed measurement uncertainty.

The Prove It Works principle changed this review's method. The review ran the export checker and inspected actual CAM coordinates instead of inferring manufacturability from the generator or a successful build.
