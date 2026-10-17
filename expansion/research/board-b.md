# Candidate B: an instrumented assembly qualification panel

## Caller usage first

A process engineer opens `/board`, sees a complete KiCad qualification panel, and chooses the 200 µm circular-pad cell. They select its identified A1 joint, compare 5 and 7 nL at a 150 µm held gap and 120 µm local-X offset, and inspect the actual native meshes and signed force difference. They change offset to 40 µm, run again, and export the selected comparison plus the source-board identity and lab specimen mapping. The claim is a prospective, isolated-joint experiment; the board is a proposed passive test article, with no electrical-function or assembly-yield claim.

The meaningful decision is whether a solder-volume change merits a controlled force experiment at a declared geometry. Conditional force evidence can reject an obviously unsuitable hypothesis before a lab spends time. It cannot select a production assembly recipe until physical validation succeeds.

## Core data and ownership

```text
BoardContext {
  schema: "soldershape.board-context.v1",
  source_sha256, generator_sha256, kicad_version,
  fabrication_status: "design-only",
  view: {svg_sha256, board_bounds_mm},
  cells: [{id, function, reference, footprint_sha256,
    board_origin_mm, rotation_deg,
    pads: [{index, identifier, local_mm, board_mm,
      shape, copper_size_mm, mask_aperture_mm, supported, reason}]}]
}
BoardSelection {board_sha256, cell_id, reference, pad_index,
  local_offset_axis: "+X", case: soldershape.case.v1}
BoardResult {selection_sha256, results, comparison, numerical_bundle_sha256}
```

The board manifest owns coordinates, fabricated-intent geometry, site identity, and scope. The existing case owns physics. The experiment protocol owns prospective specimen allocation. Repeated board pads never become repeated solved joints by implication.

Signatures and module map:

```text
board_demo/tools/build_panel.py: generate_panel(spec) -> native board + SVG + manifest
soldershape/board.py: read_context(path) -> verified BoardContext
soldershape/board.py: selected_case(context, selection) -> existing normalized case
soldershape/board.py: bundle_context(context, selection, numerical_zip) -> context ZIP
Handler GET /api/board -> compact verified context
Handler POST /api/board/case -> selected case, normalized selection
Handler POST /api/board/compare -> existing calculate_comparison + contextual export
web/board.html, board.js, board.css -> board atlas and selected-joint comparison
```

Reuse `parse_case`, `calculate_comparison`, `make_bundle`, and `SolderMesh`. Contextual export contains the numerical ZIP unchanged, preserving its replay and member limits. No new solver, generic board parser, WebGL engine, or plugin architecture is needed.

## Whole design

Build a passive 100 × 80 mm panel with four visibly distinct regions and a restrained drawing style. It is a designed test article, explicitly not an assembled commercial product.

1. Primary force-validation region: four independent 6 × 6 circular arrays at 200 µm pad diameter and 500 µm pitch. One individually addressed site maps to the force fixture. Regions identify nominal 5 and 7 nL process hypotheses; actual volume is measured, never inferred from a visual label.
2. Pad-design region: circular arrays at 220 and 270 µm tied to the existing height-coupon decision. It links out to the current loaded-height study, preserving that study's scientific contract. It does not mix height and fixed-gap force scores.
3. Scale region: one 400 µm circular array, disabled until a fresh native case is computed. It illustrates that a copied 200 µm result is not valid at another scale.
4. Exclusion region: rectangular QFN and rounded-rectangle passive footprints, rendered with clear unsupported status. They make model boundaries discoverable through actual geometry, not a buried disclaimer.

Include real fiducials, local-axis marks, board-edge dimensions, cell IDs, and inspection references. Use a common mask window only where it matches the intended pinned copper rims; export the actual mask artwork and keep final fabrication/wetting unknown. Copper routing is unnecessary for the passive physics. Adding decorative traces would create impressive-looking complexity with no experiment value and is rejected.

The board's visual complexity comes from independently selectable cells, accurate positions, mask/layer controls, linked detailed pad views, and visible test traceability. It does not come from invented circuits, fake hot spots, or thousands of repeated meshes.

## Interface and behavior

The initial viewport presents the complete panel on the left and the active joint on the right. A persistent source strip shows “Proposed qualification panel”, source hash, selected cell, and qualification state. Region buttons and a searchable pad list provide keyboard access alongside direct selection.

Clicking a cell zooms to its package and shows the pad's actual copper and mask boundaries. Clicking a supported pad opens the existing fixed-gap inputs. The local offset arrow is transformed with the cell rotation; the force result remains labeled in local coordinates. Unsupported pads show the exact reason and never inherit a previous result.

A prominent “Compute selected joint” action runs both comparison arms afresh. Reference and candidate meshes use the same physical scale and the actual shared renderer. Numerical diagnostics, scope warnings, and physical-unqualified status remain separate. A compact conditional finding describes only the requested force tradeoff. There is no board-wide score.

Editing any input, changing the selected cell, or selecting a new pad immediately invalidates the old finding and disables evidence export until computation finishes. A revision counter discards late responses. Recorded baseline data, if offered, appears as a separately labeled preview and cannot masquerade as the selected panel result.

The exported handoff includes source `.kicad_pcb`, native SVG, manifest, exact selected footprint, editable case, computation ZIP, scoped human report, and matching experiment IDs. It keeps the design-only/fabrication-release/physical-validation states explicit.

## Why it could win

This approach makes every displayed geometry ours to inspect, dimension, export, and eventually test. Known mask artwork and one-to-one fixture IDs reduce ambiguity. The first impressive interaction leads directly to a falsifiable lab question. It also avoids importing a functional board whose real package, solder volume, upper-pad geometry, mask, and standoff are unknown.

Its strongest existing alternative is KiCad plus a Surface Evolver expert's hand-built model and a spreadsheet. SolderShape improves the narrow handoff: a user selects a real pad, makes one controlled comparison, sees the exact computed shape, and exports a reproducible lab-bound dossier without rebuilding the model manually. General board inspection is already better served by KiCad; there is no claim of replacing it.

## Strongest argument against this candidate

A large passive panel is still synthetic context. It can look like a dressed-up version of the current coupon and does not demonstrate value on a board an engineer already cares about. It adds board design, CAM checks, and artifact maintenance without improving physical prediction. The requirement asks for a complex board; sparse passive copper is less compelling than an actual routed FPGA board. Increasing pad count would not fix that weakness.

The pinned ULX3S source is therefore a formidable competing design. Fresh native inspection supplied by the parent found 235 footprints, 5,365 tracks, and U1 with 381 circular 400 µm pads plus eight unnumbered rectangular features. It offers real package placement, routed topology, legitimate design complexity, and open provenance immediately. If a native extractor can bind one actual circular pad to a fresh case while exposing unknown mask and process inputs, it likely deserves selection over this panel. Preserve its modified-MIT notice and required visible original silkscreen logos.

## Before-code falsifiers and acceptance

- Extract native KiCad cell geometry and verify copper diameter, local/world transform, pad identity, and exact footprint bytes independently. A hand-entered scene with no native correspondence fails.
- Prove one source pad becomes the normalized lower diameter in `JointSpec`. A client-supplied diameter that can diverge from the source fails.
- Native computation at the primary geometry must produce a checked result or retain a clear failure. Existing recordings are not sufficient evidence for the new board identity.
- Changing 120 to 40 µm offset must invalidate the prior result, run a new normalized request, and produce a different request hash and actual force/mesh evidence.
- Rotating a cell 90° must rotate its board arrow correctly while preserving declared local force axes. Do not rotate gravity or silently reinterpret solver X as board X.
- Selecting a rectangular footprint must disable computation and exports rather than display the previous circular-pad force.
- Actual browser download must contain the selected board/pad/case identity, pass manifest verification, and replay the embedded numerical ZIP with the existing CLI.
- Exported native board and SVG must agree on site count, board bounds, diameter, and selected position; a native readback checks these independently.
- Show all four regions and their distinct status at a normal desktop viewport. If the complete-board view adds no useful path beyond the existing footprint selector, stop and use the actual ULX3S atlas.
- No acceptance criterion calls this panel production-ready, physically validated, electrically functional, or a whole-board simulation.

## Selection recommendation

Keep this as the independent alternative and graft its strongest ideas into whichever design wins: explicit proposed-versus-existing geometry, unsupported-family discovery, local-axis truth, result invalidation, and exact lab-bound exports. Choose it only if direct experimental traceability is more valuable than the user's demand for a genuinely complex existing board. On the current brief, the actual ULX3S route is likely stronger provided source-to-case binding and license-preserving rendering pass. Its 400 µm pads need fresh native cases. A doubled nominal stress scenario (400 µm assumed upper rim, 300 µm gap, 40 versus 56 nL, 240 µm offset) is a hypothesis, not a scaled copy of the old forces: gravity and unknown process inputs prevent claiming similarity without solving. Keep those assumptions explicit and separate from the 200 µm physical fixture protocol.
