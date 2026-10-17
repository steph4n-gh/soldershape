# Quote request for the SolderShape pad-size coupon

Quote experiment `SS-C220-C270-R1` as a staged outside-laboratory study. The objective is to compare post-reflow pad-face gaps for 220 and 270 micrometer board pads under one controlled assembly process. A common cap has twenty 280 micrometer mating pads. Optional hot-state measurements address liquid-equilibrium predictions separately.

The requester has no laboratory equipment. Identify one responsible laboratory and any subcontractors. This file is a prepared request. It has not been sent. No supplier acceptance, price, stock, lead time, or test result is established.

## Scope and controlled items

Use [experiment.json](experiment.json), [BOM.csv](BOM.csv), [PROCUREMENT.md](PROCUREMENT.md), [PROCEDURE.md](PROCEDURE.md), [allocation.csv](allocation.csv), and the supplied native boards and fabrication exports. Quote any exception explicitly before work. Do not change geometry or material silently.

The job uses 12 four-site carriers and 48 custom caps. Each carrier is 40 by 40 by 1.6 mm with two 220 micrometer sites and two 270 micrometer sites in mirrored pairs. Each 3 by 3 by 0.8 mm cap has a 5 by 4 array at 0.5 mm pitch. Both types use isolated copper islands, a common 2.8 by 2.3 mm array-wide mask opening, nominal 35 micrometer copper excluding finish, and the same ENIG process. Caps require CNC routing and finished copper-to-edge clearance of at least 0.2 mm. Two 3.2 mm NPTH holes are on each carrier.

The files describe unit boards. Include production panel engineering, rails, tooling, fabrication DFM, clean singulation, inspection, and final CAM returns. Return measured pad diameters, finish heights, flatness, and actual cap thickness. Quote target pad-diameter tolerance of plus or minus 5 micrometers and state actual capability.

Request one lot of nominal 320 micrometer Indium Indalloy 106 Sn63Pb37 spheres. Supply at least 1,200 accepted spheres after custom grading or laboratory screening to 317.5 through 322.5 micrometers. Demonstrate expanded sphere-diameter uncertainty at or below 1 micrometer. State MOQ, raw quantity, expected grading yield, and lead time. Exact 320 micrometer supply is unconfirmed. Do not substitute another nominal size.

Apply an uncertainty guard band to sphere acceptance. Measured diameter minus U must be at least 317.5 micrometers and measured diameter plus U at most 322.5 micrometers. Preserve all screening readings and rejects. The flux dwell must accommodate placement metrology and the prospective prediction freeze before confirmation reflow.

Use one sphere per joint, flux only, and one reflow cycle. Quote TACFlux 020B as the flux candidate. No paste, cap-height spacers, adhesive, or contacting fixture may support a scored cap during the liquid hold. A separate instrumented assembly may establish the temperature profile. Propose a reproducible liquid plateau and document the actual thermal trace and atmosphere.

## Price these stages separately

| Item | Requested quantity or scope | Quote must identify |
| --- | --- | --- |
| DFM and method review | Unit CAD, final panel, assembly, and metrology plan. | Exceptions, accepted dimensions, responsible organizations, cost, and schedule. |
| Bare hardware | 12 carriers and 48 singulated caps. | Laminate grade, stackup, finish process, tolerances, panel drawings, incoming dimensional records, and rejects. |
| Spheres and flux | One controlled sphere lot, at least 1,200 accepted spheres, twenty-ball kits, and one flux lot. | Exact material identity, certificates, grading records, balance uncertainty, MOQ, handling allowance, and unused material return. |
| Thermal profile | One carrier and four dedicated caps. | Actual time-temperature trace, calibration, thermocouple positions, atmosphere, and evidence of a stable liquid hold. |
| Pilot assembly | Three carriers, twelve caps, three separate reflow runs, six matched pairs. | Placement and kit traceability, freedom to settle, defects, and process freeze. |
| Pilot measurement | Twelve whole-cap scans and six registered destructive sections. | Local and minimum-gap uncertainty, paired uncertainty, registration, wetting, warpage, offset, and prospective precision. |
| Confirmatory assembly | Six carriers, twenty-four caps, three separate reflow runs, twelve matched pairs. | Fixed allocation, fixed process, actual run records, and all attempted assemblies. |
| Confirmatory measurement | Twenty-four whole-cap scans and six registered destructive sections. | Frozen methods, raw images, all twenty joint gaps, both clearance datums, calibration, uncertainty, and failures. |
| Optional hot-state measurement | Separate feasibility pilot and held-out scope. | Noncontact method, molten plateau, coverage, uncertainty, thermal expansion treatment, and additional parts needed. |
| Materials and report return | All data, remaining parts, unused material, and practical remnants. | Electronic formats, shipping, retention period, and data ownership terms. |

The base order allocates one carrier and four caps to profiling, three carriers and twelve caps to pilots, six carriers and twenty-four caps to confirmation, and two carriers and eight caps to spares. Extra consumables required by an optional hot-state method need a separate quantity and allocation. Do not consume confirmation specimens to develop a method.

## Answer the decisive capability questions

- Can the proposed process preserve all twenty circular wetted boundaries and allow the cap to settle under its own measured mass?
- Can the method observe all twenty opposing finished pad faces throughout a cap and report a whole-cap minimum? State inaccessible regions.
- Can the laboratory demonstrate expanded local-gap uncertainty at or below 2 micrometers and paired-difference uncertainty at or below 3 micrometers at coverage factor 2? Supply the proposed uncertainty budget. Pixel or voxel pitch alone is insufficient.
- Can registered sections through specified rows check the three-dimensional method, finish heights, contact lines, and an orthogonal datum?
- Can the laboratory supply justified temperature-dependent liquid density and surface tension inputs with sources and uncertainties before confirmation outcomes?
- Can optional hot-state observation measure a stable liquid gap without attaching a force or height constraint to the cap?

The primary practical outcome is cold geometry at 20 plus or minus 2 degrees Celsius. A 185 micrometer pad-face gap is a declared study threshold. It is not automatically a mask-to-cap underbody requirement. Return both datums separately. Cold geometry alone cannot qualify an absolute liquid-equilibrium prediction.

## Return a decision record at each checkpoint

Before fabrication release, return accepted DFM, final panel and CAM, material identity, screening plan, profile plan, and metrology uncertainty plan. State unresolved conditions instead of treating the quote as acceptance of them.

After the pilot, return all raw results and a written feasibility and precision decision. Demonstrate the specified uncertainty and assess whether a 6 micrometer difference is resolvable. The pilot is not a powered qualification study. Stop or revise the sample count, process, or method before collecting held-out outcomes if precision is inadequate.

Before confirmation, return the frozen actual input sheet, sources, methods, allocation, analysis revision, and prospective prediction manifest. Keep confirmatory outcome heights and final offsets out of those inputs. Identify measurement blinding and its limits.

The final report must retain every attempted cap. Report bridge, nonwetting, placement, fixture, damage, missing-data, and model-boundary failures by specimen ID. Report each reflow run separately. Twenty joints under one cap are dependent observations. Twelve paired caps across three runs do not establish production yield or fatigue life.

Supply raw scan volumes or a documented lossless export, calibrated images, image metadata, section coordinates, segmentation settings, unrounded local measurements, uncertainty budgets, calibration records, thermal traces, balance logs, certificates, source references, software versions, and any excluded or missing records. Return human-readable summaries with the electronic data.
