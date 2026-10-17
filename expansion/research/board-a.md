# Candidate A: real-board solder decision atlas

## Caller usage first

Open `/board`. The complete, attributed ULX3S layout fills the left two-thirds of the screen. Search `U1`, or click the highlighted FPGA package. Its actual circular pad array opens in a linked detail inset. Select pad `J16` and see `SDRAM_D0`, source copper diameter 400 µm, actual board position, package-local axes, and the source revision. The complete 235-footprint layout remains visible as context; only the selected joint has computation evidence.

The initial question is “At a held gap and offset, how does extra liquid solder change the lateral restoring and vertical separating forces?” The right panel contrasts two liquid volumes. The initial 400 µm opposing pad, 300 µm held gap, +240 µm offset, and 40 versus 56 nL are explicitly illustrative assumptions scaled from the earlier 200 µm experiment. They are not the assembled ULX3S geometry, measured paste transfer, or a production recommendation. The board supplies the lower copper pad, not these unknown process inputs.

Choose `Compute selected comparison`. Two fresh native solves produce actual meshes and signed forces. One shared camera and physical scale allow direct comparison. The visible conclusion is conditional on the declared held-gap fixture objective and blocks on numerical failure or model warnings. Change gap, offset, upper diameter, or either volume, and the previous result/export immediately disappears. Unsupported package/pad selections remain inspectable with a concrete reason and disabled computation.

Download one board-bound evidence archive. It contains the original board and license, derived selection record, exact extracted standalone footprint, editable case, two native results/meshes, raw receipts, and hashes. A command replays those two cases and checks that the selected source geometry still matches the recorded board extraction. Reopen the editable case in the existing workbench when a full board view adds no value.

## Core data shape and ownership

`BoardContext` is immutable derived geometry around the existing case, not a new simulation request.

```text
BoardContext {
  schema: soldershape.board-context.v1,
  source: {repository, commit, board_sha256, license_sha256},
  extraction: {KiCad_version, extractor_sha256, geometry_sha256},
  bounds_mm: [left, top, width, height],
  components: [{reference, value, footprint_name, uuid, side,
                board_position_mm, rotation_deg, bounds_mm,
                footprint_sha256, pads:[{index, identifier, net,
                   local_xy_mm, board_xy_mm, size_mm, shape,
                   supported, unsupported_reason}]}]
}
BoardSelection {
  board_sha256, geometry_sha256, component_reference,
  component_uuid, footprint_sha256, pad_index, pad_identifier,
  board_xy_mm, local_offset_axis_board_xy
}
BoardRun {schema, selection, editable_case, results, comparison}
```

Fresh native KiCad inspection reports 235 footprints, 5365 track objects, and U1 with 381 circular 0.4 mm copper pads plus eight unnumbered rectangular features. This already gives a useful supported package and an inspectable unsupported contrast. Use native KiCad once in a deterministic extraction command, not a new browser KiCad parser. Export the original board's front copper, front silkscreen, and outline as native SVG, and extract standalone footprints from the same loaded object. Render the original silkscreen logos unmodified and visible with their source coordinates. Retain all raw source/license bytes. Pad order in the standalone footprint must be checked against native pad identities; never assume two independent iterators agree.

World coordinates come from KiCad's actual pad positions. The inset uses the standalone footprint's normalized local coordinates. Store the explicit package-local +X to board transform and test a rotated footprint so arrows cannot silently invert when moving between views. Mirrored back-side parts need a verified transform; otherwise inspect-only in version one. Board-level mask rules and actual wetting stay unresolved even when a circular copper pad passes the footprint importer.

## Signatures and modules

```text
board_demo/tools/extract.py
  extract(source_board: Path, output_dir: Path) -> BoardContext
  verify_native(context: Path, source_board: Path) -> receipt
soldershape/board.py
  read_board(directory=board_demo) -> verified BoardContext
  board_case(context, selection, parameters, baseline) -> existing Case
  run_board(request) -> BoardRun
  bundle_board(run) -> bytes
  replay_board(path) -> replay report
GET /api/board -> verified context and initial draft only
GET /board/assets/{fixed-name} -> explicit static allowlist
POST /api/board/compare -> selected identities + editable assumptions
soldershape/web/board.{html,css,js}
  state {context, selection, draft, revision, phase, response}
```

The server resolves the selection against trusted local extraction, derives the lower pad from the exact footprint, normalizes the existing case, and calls the existing `calculate_comparison`. Do not trust client-supplied lower diameter, coordinates, nets, or source hashes. Reuse the same session token, origin check, and computation lock. Keep defaults, transforms, report generation, and archive composition in `board.py`; the browser displays the normalized server result.

Compose `make_bundle()` the same way `bundle_study()` does. Add one `board-selection.json`, source board, license, extraction manifest, and extraction receipt under the existing 100-member and size limits. Two computed cases easily fit the seven-case limit. The reader must validate every included byte and cross-check selection, footprint hash, selected pad, case inputs, and result provenance. Hashes alone do not prove extraction correctness. Native readback verification supplies the independent bridge from the original board to the derived selection.

Existing `parse_case`, `request_from_footprint`, `calculate_comparison`, `make_bundle`, `read_bundle`, `JointSpec`, and shared `SolderMesh.drawSurface` remain unchanged if possible. Preserve the original `/demo`, `/study`, numerical source, and retained recordings. Use a dedicated board CLI command, not a new generic workflow framework.

## Visual design and useful distinction

The first screen is a real dense PCB, not a repeated BGA texture. Native copper traces/vias, actual silkscreen labels, and package locations supply recognizable engineering complexity. A muted green/dark board, copper accent, selected package halo, thin leader to the pad inset, and two luminous native surfaces make the scale transition clear. A persistent “1 selected joint computed” badge prevents whole-board inference. The supported/unsupported breakdown is derived, never a risk heatmap.

The useful output is a traceable hypothesis attached to an actual board pad: the force tradeoff under explicit geometry/material assumptions, with an exact replayable mesh and evidence. A KiCad layout view already supplies superior routing/manufacturing context; the existing single-joint workbench already computes the same physics. This atlas earns its extra interface only if a user can locate a real joint, see which inputs are still missing, change one relevant process assumption, and hand the exact board-bound comparison to the lab without transcription.

## Strongest whole alternative and counterexample

A purpose-designed validation panel with several deliberately supported circular footprints provides cleaner known boundaries and more independent comparative decisions. It loses the recognizable density and real project context of ULX3S. Prefer that alternative if almost all actual board pads are unsupported, if the board view obscures the process-input uncertainty, or if extracted footprint geometry cannot be independently reconciled with native coordinates.

An FPGA assembly engineer asking “Will this 381-ball package self-align or bridge?” is a decisive counterexample. This isolated held-gap model cannot answer. The UI must say so before computation, and never sum one joint's force across a BGA or turn a scalar scope check into package yield. The inherited failure of physical force validation remains visible regardless of a successful numerical replay.

## Before-code acceptance gates

1. Native KiCad extraction of the pinned unmodified board yields repeatable component/pad counts, source hashes, and bounds; verify U1 `J16` is circular 0.4 mm and its named net/position match original source. Check one rotated component and one unsupported rectangular/through-hole pad.
2. The complete original front silkscreen, including required logos, remains visible and unchanged. Show source attribution, commit, license, and inspectable source download.
3. The initial selected comparison passes fresh native numerical checks and has no model warning, or the default is revised openly with the negative result retained. No recorded 200 µm result can masquerade as a 400 µm board-pad calculation.
4. In the actual browser, select the real package/pad, change volume or gap, compute two fresh meshes, and download the actual archive. The archive's selected-pad identity, normalized request, forces, triangles, and board source agree with displayed values.
5. Editing any selection/assumption during a pending run invalidates its result and export. A stale response cannot restore them. An unsupported selection cannot submit a numerical request.
6. A fresh replay of the downloaded archive reproduces the numerical comparison; wrong board hash, pad identity, footprint, or case mapping is rejected. Retain native board readback evidence separately from ordinary archive byte verification.
7. Complete workflow uses keyboard-accessible selection/search, responsive layout, readable units, explicit hypothetical inputs, and distinct numerical/physical status. Existing workbench, study, original demo, and old archives continue to function.
