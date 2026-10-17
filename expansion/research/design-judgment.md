# Independent design judgment

Read all four complete candidates, `metrology.md`, `design-brief.md`, `architecture.md`, `WORKFLOW.md`, and the downloaded board provenance. This is a fresh same-family review of proposed designs. It ran no computation or physical experiment. Scores assess the proposals against this request, not completed capability.

## Rubric and selection

Each criterion is 0 to 4. Usefulness means a consequential user decision and, for the board, convincing actual complexity. Credibility means correct model boundaries and honest metrology. Simplicity means the fewest new concepts and unqualified interfaces. Verification means concrete independent checks rather than appearance.

| Candidate | Usefulness | Credibility | Simplicity | Verification | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixture A, indexed scalar sensor and vertical rod | 3 | 2 | 3 | 3 | 11 |
| Fixture B, simultaneous two-axis head and transparent cap | 4 | 2 | 2 | 3 | 11 |
| Board A, attributed ULX3S atlas | 4 | 3 | 4 | 4 | 15 |
| Board B, new passive qualification panel | 3 | 3 | 2 | 3 | 11 |

Choose Fixture A's staged scalar measurement as the base, with Fixture B's transparent horizontal cap and explicit optical access as a conditional graft. Choose Board A. Neither decision authorizes fabrication, establishes sensor compatibility, or resolves the existing physical-validation failure.

## Fixture choice and graft

A smaller-range cool sensor and a lateral-first commissioning milestone are the least expensive route to a decisive measurement. Simultaneous vector sensing is valuable, but there is no demonstrated whole-system accuracy advantage here. Its extra calibration and moment response should be purchased only when a lab can supply evidence, not inferred from 0.1 µN noise. Both candidates correctly preserve horizontal rims and gravity along negative solver z.

The vertical rod end in A hides the upper contact line. That is a scientific failure mode, not a cosmetic inconvenience. Graft B's small horizontal transparent cap, thin wettable island, nonwetting annulus, and dimensioned optical corridors. A horizontal remote stalk can support that cap while the sensitive scalar axis is indexed between independent x and z runs. Do not rotate the joint with the sensor. Do not add a guide, temperature lead, or other contact that bypasses the cell.

This graft is conditional. Through-glass viewing does not by itself prove the complete metal/liquid boundary is visible. CAD must show the island setback and viewing rays, and the lab must demonstrate complete-rim pinning or a justified complete-rim observation method. If the wetting boundary remains hidden, stop that geometry. Two attractive silhouettes cannot certify the unseen circumference.

The horizontal stalk adds a moment question absent from a simple force-range comparison. A 20 mm by 1 mm silica rod weighs approximately 339 µN and applies about 3.39 µN m at its supported end; a 2 by 2 by 0.3 mm silica cap adds about 0.52 µN m at 20 mm. A 124 µN transverse joint force adds about 2.48 µN m. These are engineering estimates, not sensor ratings. The supplier must accept total moment, cross load, attachment, preload, temperature, and overload margin in both scalar orientations. A ±2 mN force range alone establishes none of those limits.

Use a cool sensor/stage adapter blank, not invented vendor mounting holes. Fully dimension the custom internal assembly and show unresolved sensor, chamber, heater, bond, and thin-film interfaces conspicuously. This is a quote package until a lab supplies accepted interface revisions. A solid adapter blank is permissible only if no report calls it a finished universal instrument adapter.

Retain B's explicit cross-axis/moment calibration, time-synchronized coordinate/force records, and covariance requirements. In the scalar implementation, separate x and z specimens and blocks must remain separate statistical populations. Never imply a measured vector from different joints.

## Fixture contract before implementation

1. One machine-readable specification controls CAD, drawings, calculation dimensions, and specimen targets. Verify closed solids, actual pad planes, 150 µm nominal gap, 40/120 µm offsets, clear optical/motion envelopes, and a single upper-pad force path. Reimport neutral CAD and compare dimensions and solid counts with the source build.
2. Keep rated force, moment, cross-load, body temperature, attachment, and all vendor mating interfaces explicitly unresolved until accepted. No silent substitution of range or resolution for calibrated accuracy. Quantify the full moving load, including gravity and cable/attachment effects.
3. Actual hot rim gap and offset must be independently registered and held. Fine-stage travel cannot be assumed to span zero to 120 µm. Thermal expansion and assembled compliance enter metrology; encoder coordinates alone fail the contract.
4. Native sensitivity runs must set final geometry/material tolerances. Report local derivatives as local estimates, not global uncertainty bounds. If the chosen uncertainty envelope crosses numerical failure, depinning, plane excursion, or a force-sign change, retain that negative result and make the endpoint inconclusive.
5. Distinguish planning values from physical-process inputs. The old 0.48 N/m and 9 g/cm3 values may support an identified numerical planning freeze. A confirmatory physical freeze requires independent actual-alloy, temperature, volume, geometry, uncertainty, and calibration evidence before outcomes. Unknown terms cannot become zero, and fitting confirmation forces cannot repair the freeze.
6. Require assembled transfer calibration, both signs, representative cross loads/moments, hot no-bridge blanks, stable rim coordinates, reversals, and slower-motion checks. Preserve failures and missing specimens in the denominator. Expanded U at most 2 µN per force and the declared contrast/input gates are proposed contractual requirements, not demonstrated performance.
7. Commission x at 40 µm, then 120 µm. Commission z separately at 40 µm before the small 7 nL/120 µm sign. Keep 200 µm-offset and 60 µm-gap diagnostics outside the primary acceptance population.
8. If full integration misses its gate, deliver the failed budget and the lateral-only 40 µm experiment as the cheaper bounded alternative. Do not turn a large-signal result into validation of the small upward sign, simultaneous vector, self-alignment, or assembly yield.

## Board choice and graft

The actual ULX3S source already supplies meaningful routed complexity without inventing a new passive panel or maintaining more CAM. Its U1 circular pads are a valid route into the existing isolated-joint model. The board view earns its interface only through exact source-to-case identity and an end-to-end lab-bound comparison. KiCad remains the stronger general board viewer; SolderShape's narrow gain is an immediately reproducible force hypothesis attached to an identified real pad.

Graft Board B's visible unsupported-family discovery, local-axis truth, proposed-versus-existing distinction, specimen/hypothesis handoff, and strict stale-result invalidation. Do not graft its four-region panel, new board generation, extra CAM, or mixed height/force scores. Keep the existing height study a separate workflow.

Use Board A's flat composition around `make_bundle()`, following the existing study pattern. Include two selected native cases, source board/license, exact extracted footprint, selection/context, and manifest under the existing case/member/size limits. There is no demonstrated reason to invent a nested numerical-archive format or raise limits. Native readback verifies extraction; hashes only bind bytes.

The doubled example geometry is an explicit hypothetical process at an actual 400 µm copper pad. Fresh native calculations are mandatory. Scaling old forces is invalid because gravity changes relative importance. Actual upper pad, standoff, material, volume, mask and wetting remain unknown. Show those unknowns next to the editable inputs before computation, not only in a report footer.

## Board contract before implementation

1. Deterministic native extraction binds the pinned original board, source license, native KiCad version, footprint identity, pad order/identifier, copper size, net, position, rotation, and board bounds. Independently read back U1 J16, one rotated component, and one unsupported rectangular or through-hole pad.
2. Preserve all original source bytes and the modified-MIT notice. Native SVG must preserve required original logos at their actual locations, shapes, and sizes; the board view must keep the original silkscreen available and visible. Attribute the project and pinned revision without implying its authors endorse the experiment.
3. The server resolves selection from trusted extraction and derives lower diameter from the exact standalone footprint. Reject forged board, component, pad, footprint, and mapping identities. Inspect-only back-side parts until their mirror/rotation transform is independently verified.
4. A complete browser workflow selects a real package and pad, inspects its context and local axes, changes a material or geometry assumption, performs two fresh native solves, displays exact meshes and signed forces, and downloads a board-bound archive. Unsupported selection disables computation; a detected numerical or scope failure blocks preference.
5. Changing selection or inputs invalidates result and export immediately, including while computation is pending. Late responses cannot revive stale evidence. One solved joint never implies that all displayed pads were solved or that forces can be summed across the package.
6. Verify the actual browser download against displayed selection, normalized request, force, vertices/triangles, and source identity. Replay it natively. Deliberately altered board, pad, footprint, and case mappings must fail verification. Keep replay agreement separate from physical agreement.
7. The default 400 µm comparison must pass fresh numerical/scope checks or be openly revised with the failed trial retained. Preserve the historical 200 µm archive and all old workbench/study/demo behavior. No numerical model change is justified merely to make the new default look good.

## Evidence that would reverse these choices

Choose the two-axis head if a lab already owns it and demonstrates the assembled hot uncertainty and interface gates at the required loads. Reject the transparent-cap scalar graft if attachment moments, wetting visibility, or thermal drift cannot be bounded. Choose the passive panel only if the actual-board extraction cannot bind a supported pad reliably or the full board obscures the useful selected-joint workflow. None of these alternatives earns a claim of physical validation without held-out physical observations.
