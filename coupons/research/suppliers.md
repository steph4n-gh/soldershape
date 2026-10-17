# Supplier evidence for the 220 µm and 270 µm coupon

Checked on 2026-10-16. These are published capabilities and catalog identities. No vendor has accepted this job. No quote, purchase, assembly booking, or measurement booking has been made. Stock pages can change.

## Preferred procurement route

Use the custom top coupon in the fabrication package. Ask one assembly laboratory to manage the bare boards, lot-controlled spheres, flux, fixture, thermal profiling, and metrology subcontract. This avoids assuming that a commercial dummy BGA has a 280 µm upper pad or a known mass. A 20-joint, 0.5 mm pitch assembly needs measured top-coupon mass, rather than an assumed 4 µN load per joint.

For the first quote, request one ball per joint and flux only. Request nominal 320 µm Sn63Pb37 spheres from Indium, with the actual lot diameter distribution and certificate. A 322 µm quote is an alternative if reproducing the paper's nominal total metal volume is essential. Neither exact custom diameter has a verified catalog part number or confirmed availability. Freeze the selected size and model inputs before the laboratory measures the assembled heights. Do not substitute a different diameter silently.

The sphere calculation gives these values. It assumes a sphere at the diameter measurement temperature. Liquid-volume expansion requires its own declared treatment.

| Diameter | Calculated sphere volume | Difference from 0.01745 mm³ |
| --- | --- | --- |
| 300 µm | 0.01413716694 mm³ | −18.985% |
| 304.8 µm, exactly 0.012 inch | 0.01482666620 mm³ | −15.033% |
| 320 µm | 0.01715728468 mm³ | −1.677% |
| 322 µm | 0.01748099857 mm³ | +0.178% |

The equivalent spherical diameter for 0.01745 mm³ is 321.80956 µm. The calculation is `V = π d³ / 6`. Equal loading of 20 joints at 4 µN requires a supported mass of 8.15773 mg, using standard gravity. The real load includes the supported top coupon, attached material, and any fixture force. Equal division among 20 joints is an approximation that tilt and warpage can invalidate.

## Solder and flux references

| Supplier and identity | Verified published fact | Procurement condition |
| --- | --- | --- |
| [Indium specialty solder spheres](https://www.indium.com/products/solder-spheres/), Indalloy 106 | The manufacturer lists Sn37Pb, also called 63Sn, with a 183 °C melting point and an approximate 102–1270 µm manufacturable range. It provides a quote route. | Request 320 µm nominal, or the separately priced 322 µm alternative. Ask for composition, diameter distribution, sphericity, measurement temperature, oxide handling, lot traceability, minimum quantity, and lead time. The published range does not guarantee either exact size. |
| [Chip Quik solder spheres](https://www.chipquik.com/store/index.php?cPath=1101), `SMD2165-25000` | The manufacturer lists 25,000 Sn63Pb37 spheres and labels the diameter both 0.012 inch and 0.3 mm. The page displayed “In Stock” at this check. The [manufacturer datasheet](https://www.chipquik.com/datasheets/SMD2185.pdf) identifies the same part. | This is a procureable catalog fallback for a redesigned 300 µm experiment. The two nominal units differ by 4.8 µm. Confirm the controlled diameter and measure the lot. Do not use the paper's 0.01745 mm³ input for these balls. |
| [Indium TACFlux 020B product datasheet](https://www.indium.com/wp-content/uploads/2025/03/TACFlux-020B-PDS-98565-A4-R1-1.pdf), `TACFlux 020B` | The manufacturer describes a no-clean SnPb-compatible ROL0 flux. It lists 10 cc and 30 cc syringes and 100 g jars. Air and nitrogen are listed reflow atmospheres. | This is a named quote candidate. Ask the assembler to confirm this exact flux with the selected finish and alloy. Record lot, expiry, application amount, atmosphere, cleaning, and profile. Its maximum-temperature rating is not the coupon's reflow recipe. |

The experiment needs metered solder metal volume. Solder paste contains flux. Paste volume is not solder metal volume. Avoid compensating a small ball with paste unless the laboratory can report deposited metal volume and its uncertainty per assembly. Both pad variants must use one solder lot and the same process.

## Dummy component comparison

[Practical Components CABGA](https://www.practicalcomponents.com/home/print-view.cfm?prid=1008&type=pkg) lists `A-CABGA40-.5mm-5mm`. It has 40 joints, 0.5 mm pitch, a 5 mm body, and an 8 by 8 perimeter matrix. The same page lists a 36-joint full-array part at 0.8 mm pitch. This source does not establish a 20-joint, 0.5 mm pitch part with 280 µm upper pads. Upper-pad geometry, ball metallurgy for a particular ordered variant, mass, and availability require a drawing and quote. The custom coupon therefore remains the controlled experiment. No commercial dummy part belongs in the primary BOM without a geometry revision and new predictions.

## Bare-board fabrication constraints

| Primary source | Verified published fact | Consequence for this job |
| --- | --- | --- |
| [JLCPCB rigid PCB capabilities](https://jlcpcb.com/capabilities/Capabilities?type=1) | The page lists a 3 by 3 mm FR4 minimum at thicknesses of at least 0.6 mm. Thinner boards require manual review. It explicitly requires ENIG for 0.20–0.25 mm BGA pads. | A 3 by 2.5 mm top coupon needs written custom or panel acceptance. A 220 µm OSP pad also needs written acceptance. A common ENIG finish is a practical quote basis, but it changes the process from the historical paper. Do not accept HASL. |
| [Eurocircuits soldermask guidance](https://www.eurocircuits.com/technical-guidelines/pcb-design-guidelines/soldermask/) | The supplier states a 0.40 mm minimum soldermask opening. Its DI guidance lists a 30 µm mask annular ring and a 75 µm minimum mask segment. | Small individual mask windows cannot be assumed universally standard. A common array-wide opening removes that dependency if the board design permits it. Require an unchanged copper diameter and no mask encroachment. Obtain the final CAM files. |

Pad diameter is the independent variable. Standard trace-width tolerances do not establish an adequate pad-diameter tolerance for this experiment. Request measured diameter, roundness, top-metal height, finish thickness, and flatness on representative incoming coupons. Record the laboratory's actual uncertainty. Reject automatic CAM pad enlargement or mask conversion. Ask the fabricator to quote panel rails, fiducials, top-coupon singulation, and clean edges before accepting a final panel layout.

## Outside laboratories to ask for a quote

| Organization | Verified published service | Capability still requiring confirmation |
| --- | --- | --- |
| [BEST prototype rework services](https://www.solder.net/pcb-rework-services/) and [BGA X-ray inspection](https://www.solder.net/services/bga-x-ray-capabilities/) | BEST advertises prototype runs, fine-pitch BGA work, reballing, and outsourced BGA X-ray inspection. Its inspection list includes voids, pitch, circularity, and wetting. | Confirm placement of loose 320 µm SnPb spheres on custom 20-joint coupons. Request a thermal profile and calibrated gap metrology. The advertised X-ray spot size does not establish height accuracy or three-dimensional dimensional uncertainty. |
| [University of Maryland CALCE test services](https://calce.umd.edu/services) and [failure analysis](https://calce.umd.edu/failure-analysis) | CALCE offers custom testing and material characterization. It lists three-dimensional X-ray imaging and microsectioning. | Ask whether it can act as the measurement lead, accept externally assembled coupons, and measure the specified gap and warpage. In-situ molten-height measurement, accuracy, cost, lead time, and assembly support are unconfirmed. |
| [Elmet cross-sectional analysis](https://www.elmetlabs.com/cross-sectional-analysis) | The laboratory describes polished cross-sections with optical or electron microscopy. It supplies a report and images that identify targeted BGA locations. | Ask for center-plane registration, pad heights, wetting extent, and gap measurements with a stated calibration and uncertainty. Assembly and hot-state measurements are unconfirmed. |

No source above confirms a complete turnkey job with calibrated molten-height measurement. Quote that capability explicitly. Room-temperature cross-sections measure the solid joint after cooling. They cannot, by themselves, validate liquid equilibrium geometry. Ask for separate prices for assembly, incoming metrology, hot-state gap measurement, post-cool inspection, and destructive sections. This allows the operator to see whether the decisive measurement is available before paying for the full batch.

## Information the quote must return

- Identify the fabricator, assembly process owner, and measurement laboratory.
- Confirm copper dimensions and the identical finish on both pad variants.
- Identify the exact solder alloy, diameter, lot, certificate, and measured volume uncertainty.
- Identify the exact flux and the documented reflow atmosphere and profile.
- Confirm that top coupons remain free to settle vertically during the molten hold.
- State each metrology method, datum, calibration artifact, resolution, expanded uncertainty, and measurement temperature.
- Separate molten measurements from cooled measurements and destructive measurements.
- Supply raw images, raw measurements, thermal traces, excluded assemblies, and exclusion reasons.
- Quote panelization, singulation, pilot acceptance, remaining assemblies, and destructive sample preparation separately.

Prove It Works shaped the procurement condition. A catalog range and a small X-ray spot do not count as acceptance of the actual coupon or measurement accuracy. Source facts are linked and mirrored in `suppliers.json`. The sphere volumes and supported mass were recomputed from their formulas.
