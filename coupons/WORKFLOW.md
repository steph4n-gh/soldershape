# Outside-lab coupon preparation

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

Done means an internally consistent, editable PCB and fabrication export package for a 220 versus 270 micrometer pad comparison, a procurable material/part specification, a lab-executable randomized assembly/metrology protocol, and a replayable prediction and analysis path. Physical outcomes must remain blank. The user has no lab equipment and wants to send the package to an external lab. No supplier contact, purchase, fabrication release or fabricated physical result is authorized by this task.

The scope is one comparison, two substrate pad diameters, one controlled upper coupon/component and solder alloy. It includes assembly spares and staged gate checks. All experimental units, geometry reference planes, actual liquid-volume assumptions and per-joint loads must be identified before outcome scoring. The existing application's two-value reference comparison cannot compare lower-pad revisions, so use separate validated requests without changing the product.

## Designed units

- [x] Ground the model and measurement assumptions against current sources and source code.
- [x] Compare two complete fixture/coupon architectures. Judge fabrication feasibility, input identifiability, measurement access, confound control and simplicity before selecting one.
- [x] Freeze the chosen geometry, sample count, measurement definitions, blinding, exclusions and decision gates in one experiment specification.
- [x] Generate native editable KiCad boards, Gerbers, drill outputs, assembly drawings and machine-readable site maps from that specification. Run actual KiCad parsing/DRC and verify exported geometry independently.
- [x] Verify supplier part specifications and prepare a quote-ready BOM and lab scope of work. Quote-only items and unknown availability remain explicit.
- [x] Prepare the measurement worksheets, model-input freeze and analysis script. Test a declared synthetic pass, deliberate model failure and invalid/missing-data controls without presenting simulated data as measurements.
- [x] Independently review fabrication, assembly and inference. Resolve defects, package a manifest and provide the concrete lab handoff.

## Acceptance checks before implementation

The board source and actual Gerber geometry must contain the declared counts and pad diameters. Mask openings must be NSMD with declared dimensions, and trace wetting or vias must not change the circular joint boundary. The component/cap must be physically orderable or specified as a custom fabrication with panelization responsibility stated. Solder sphere diameter and metal volume cannot be confused with total deposited volume. The protocol must identify post-solidification height versus liquid-equilibrium predictions, two-sided pad metal, mass/load sharing, offsets, tilt, flatness, voids and wetting. Metrology uncertainty must be smaller than the expected 6 to 11 micrometer comparison signal. Manufacturing readiness remains conditional on the lab's DFM and metrology capability acceptance, not a DRC result alone.

## Throughput checkpoint

Resolve the top coupon, solder volume and measurement access first. Build one deterministic board generator and check it with the actual KiCad CLI before replicating sites. Use separate files for supplier research and candidate designs. Root owns final specification, board generation and packaging. Independent reviews cover manufacturing geometry and experimental inference. Do not build a general coupon CAD framework, add thermal physics or modify the running SolderShape workbench.

## Architecture rubric

Score each candidate from 0 to 4 for identifiable physical inputs, credible outside-lab fabrication/assembly, metrology access, ability to isolate the lower-pad change, and total number of custom processes. The highest score is a recommendation, not a substitute for root inspection. No design may claim that a custom assembly automatically reproduces the paper or that 220 micrometer pads will satisfy 185 micrometer clearance.

## Completed evidence

The final source and manufacturing files pass actual KiCad 10.0.6 parsing and DRC, independent Gerber/drill checks, three deliberate corrupted-export controls, and twenty-one synthetic analysis checks. Six actual native planning requests passed accepted refinement and independent load balance. Blank physical inputs cannot complete a freeze. Physical outcomes remain blank. The eight-page printable guide was rendered and inspected. The final archive is checked again after extraction, without the local engine cache.

Independent same-family reviews found false passes for missing wetting evidence, unguarded gap range and a room-temperature molten label. The repaired scorer rejects or marks those cases inconclusive. Original reports and their negative reproductions remain in evidence/. The final review records accepted repairs and remaining physical assumptions.
