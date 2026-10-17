# Procure the outside-lab coupon study

This package requests a quote for experiment `SS-C220-C270-R1`. No vendor has accepted the work. The files are prepared for quotation, not released for fabrication. Obtain written DFM, assembly, and metrology acceptance before ordering boards or starting the confirmatory batch.

Use [experiment.json](experiment.json) as the controlled geometry and experiment specification. Use [BOM.csv](BOM.csv) for quantities and [LAB_RFQ.md](LAB_RFQ.md) for the staged scope. The supplied KiCad and Gerber files describe unit boards. The fabricator owns the production panels, rails, tooling, routing, and singulation proposal.

## Request one laboratory owner

Ask one laboratory to manage board fabrication, graded spheres, assembly, thermal profiling, and measurement. The laboratory may subcontract. Require the name and responsibility of each subcontractor in the quote. A public service description does not establish acceptance of this coupon or its uncertainty requirement.

These organizations have relevant published services. Their ability to deliver this complete study remains unverified.

| Organization | Relevant published service | Capability to confirm in writing |
| --- | --- | --- |
| [BEST prototype rework](https://www.solder.net/pcb-rework-services/) and [BGA X-ray](https://www.solder.net/services/bga-x-ray-capabilities/) | Prototype assembly, BGA work, and inspection. | Custom loose-ball assembly, a freely settling 3 mm cap, traceable reflow, and dimensional gap metrology. |
| [University of Maryland CALCE](https://calce.umd.edu/services) and [failure analysis](https://calce.umd.edu/failure-analysis) | Custom testing, material characterization, three-dimensional X-ray, and sections. | Measurement lead, full-cap coverage, required uncertainty, outside assembly coordination, and optional hot-state observation. |
| [Elmet cross-sectional analysis](https://www.elmetlabs.com/cross-sectional-analysis) | Location-identified polished sections, optical microscopy, and electron microscopy. | Registered pad-center sections, uncertainty, full-volume measurement partner, and assembly support. |

## Order the controlled board construction

Order 12 carriers at 40 by 40 by 1.6 mm. Order 48 caps at 3 by 3 by 0.8 mm. Specify two-layer identified high-Tg FR4, nominal 35 micrometer copper, and the same ENIG process for both mating coupons. The copper nominal excludes nickel and gold. Request actual finished metal heights and their uncertainty. Do not treat the stackup nominal as a measurement of the wetted plane.

Both coupon types have isolated circular copper islands and one 2.8 by 2.3 mm mask opening around each array. No traces, vias, test connections, copper thieving, or mask webs may enter an array. The carrier has two 3.2 mm nonplated tooling holes. No electrical schematic or connectivity test is required for these isolated geometry coupons.

Require CNC routing for the caps. Do not use V-scoring. Require at least 0.2 mm finished pad-copper clearance to the routed edge. The nominal design clearance is 0.36 mm. Require the fabricator to accept pad diameters of 220, 270, and 280 micrometers with a target tolerance of plus or minus 5 micrometers. Measure actual diameters, roundness, edge quality, and top-surface height before assembly. A tolerance commitment does not replace those input measurements.

The [JLCPCB capability page](https://jlcpcb.com/capabilities/Capabilities?type=1) lists routed and V-cut copper-edge limits separately and requires ENIG for 0.20 to 0.25 mm BGA pads. Its [dimension guidance](https://jlcpcb.com/help/article/pcb-dimensions) gives a 3 by 3 mm FR4 minimum at thicknesses of at least 0.8 mm. Those published limits motivate the quote basis. They do not establish acceptance of this cap, its final panel, or its metrology access.

Obtain the final panel drawing and CAM output before release. Reject silent pad enlargement, mask encroachment, finish substitution, HASL, cap-thickness substitution, or extra metal. Singulate, deburr, clean, identify, and dry all caps before mass measurement. Place any cap identification on its outer face, outside the mating array. Include that marking in the bare-cap mass. Preserve the orientation datum.

## Request a graded sphere lot

Request nominal 320 micrometer Sn63Pb37 spheres from [Indium specialty solder spheres](https://www.indium.com/products/solder-spheres/), alloy identity Indalloy 106. The manufacturer lists this alloy and a manufacturable size range that includes the request. Exact diameter availability, grading, minimum order, cost, and delivery remain quote conditions. There is no confirmed stock part number in this package.

Request at least 1,200 accepted spheres after grading. The 48 allocated cap assemblies consume 960 spheres. The remaining 240 accepted spheres are a handling reserve. Supplier minimum quantities and screening rejects may require a larger incoming quantity. Price that incoming quantity separately from the count of accepted spheres.

Every accepted sphere must have its complete measured diameter uncertainty interval within 317.5 to 322.5 micrometers. Require expanded diameter uncertainty at or below 1 micrometer and a stated coverage factor. Use a custom grade or laboratory screening. The actual vendor tolerance is unverified and must be confirmed in the quote. Preserve the individual screening records, sphericity method, measurement temperature, lot distribution, composition certificate, storage history, and handling method.

Create labeled, clean kits of twenty accepted spheres. Weigh each kit as metal only, without flux. Record tare, net mass, uncertainty, and sphere IDs. Kits must remain identifiable through assembly. Record losses and replacements with their actual sphere IDs. Do not replace a dropped sphere from an unmeasured lot.

Do not substitute 300, 322, or 325 micrometer spheres under this revision. A size change requires a revised specification and prospective predictions before outcomes. A nominal 320 micrometer sphere has a calculated solid geometric volume of 0.0171573 cubic millimeters. This is not the measured liquid volume. The paper's 0.01745 cubic millimeter input is not a procurement target for this study.

## Identify flux and liquid material properties

Quote [Indium TACFlux 020B](https://www.indium.com/wp-content/uploads/2025/03/TACFlux-020B-PDS-98565-A4-R1-1.pdf) as the named flux candidate. Ask the assembler to confirm the exact product with the actual ENIG and SnPb alloy. Record product revision, lot, expiry, dose, atmosphere, and cleaning. Use flux only and one sphere per joint. Do not add solder paste.

Require a justified, temperature-dependent liquid-density source for the actual alloy. Record its equation or table, applicable temperature range, value at the measured liquid plateau, uncertainty, and exact source location. A solid-state nominal density or SolderShape's generic default is insufficient. Define the liquid surface tension and its uncertainty from a cited source or independent measurement. Account for the chosen flux and atmosphere. Freeze these material inputs before confirmatory outcomes. Do not fit them to confirmatory heights.

Compute average liquid solder volume per joint from net twenty-ball kit mass divided by twenty and liquid density. With kit mass in milligrams and density in grams per cubic centimeter, the result is cubic millimeters. Propagate kit-mass, density, and temperature uncertainty. The graded diameter records bound unequal volumes within each cap. No theoretical sphere volume replaces the kit mass.

## Stage the purchase and execution

1. Obtain written acceptance of DFM, materials, assembly freedom, metrology datums, and uncertainty budgets.
2. Authorize the bare boards, one graded sphere lot, profiling, and the three-run pilot as a first priced stage.
3. Review incoming dimensions, sphere records, cap masses, the thermal trace, pilot wetting, and demonstrated measurement uncertainty.
4. Review prospective precision for a 6 micrometer arm difference. If the pilot cannot resolve that difference, stop or revise the study before confirmatory outcomes.
5. Freeze actual confirmatory inputs, methods, predictions, analysis, and specimen allocation before acquiring confirmatory outcomes.
6. Authorize the separately quoted confirmatory assembly and measurement stage under the accepted revision.

The allocation reserves three carriers and twelve caps for pilot runs, six carriers and twenty-four caps for confirmatory runs, one carrier and four caps for profiling, and two carriers and eight caps as spares. A spare is a recorded replacement or contingency. It is not an opportunity to replace an unfavorable result.

Return unused materials, all remaining assemblies, destructive remnants when practical, and the complete electronic record. The package includes no order placement, laboratory booking, or outbound message.
