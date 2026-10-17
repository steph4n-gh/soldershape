# Selected design contract

Root accepts the independent judgment in research/design-judgment.md. The four candidates were read in full. The fixture uses A's staged scalar commissioning and B's horizontal transparent cap, subject to the full load and moment acceptance gate. The board uses A's actual ULX3S source with B's explicit unsupported selection and invalidation behavior. There is no additional physical model or board solver.

## Board interface

`board_demo/context.json` is `soldershape.board-context.v1`. It contains `source` (repository, commit, board_sha256, license_sha256), `extraction` (kicad_version, extractor_sha256), `bounds_mm` [left, top, width, height], `svg` (file, sha256, bounds_mm in native board coordinates), and `components`.

Each component contains `reference`, `value`, `uuid`, `side`, `board_position_mm`, `rotation_deg`, `bounds_mm`, `footprint_file`, `footprint_sha256`, `local_x_board` [dx,dy], and `pads`. Each pad contains `index` matching the normalized standalone footprint importer, `identifier`, `net`, `local_xy_mm`, `board_xy_mm`, `size_mm`, `shape`, `supported`, and `unsupported_reason`. The extractor verifies importer order, rather than assuming iterator order. Back-side pads are inspect-only. Every retained generated file has an exact digest in `board_demo/manifest.json`. Source files stay unmodified. A native independent readback checks the original-to-extracted correspondence.

`GET /api/board` returns `{context, default_request}`. `GET /board.svg` serves the native copper/silkscreen/outline SVG with fixed-path routing. No browser parser is added.

`POST /api/board/compare` accepts `{schema:"soldershape.board-request.v1", board_sha256, reference, pad_index, parameters, baseline}`. Parameters and baseline use the existing fixed-gap case keys. The server resolves the source pad and coordinates from the trusted context and rejects unsupported pads, wrong source identity and extra keys. Lower diameter is never a client field. Initial values are upper_diameter_mm=.4, standoff_mm=.3, volume_mm3=.056, offset_mm=.24, surface_tension_n_m=.48, density_g_cm3=9, gravity=true. Baseline changes volume_mm3=.040 and upper_diameter_mm=.4. These are explicitly hypothetical process inputs, not actual ULX3S assembly measurements. Default pad is U1 J16 if present, else an identified supported pad.

The response is `{report:{schema, selection, editable_case, results, comparison, screen, physical_qualification}, bundle_base64, bundle_filename}`. `screen` reuses the existing conditional force objective. Selection includes source/footprint hashes, component UUID/reference, pad index/identifier/net/positions, and local +X board vector. Export uses the existing flat numerical ZIP plus board-selection.json, board-context.json, original board and license, extraction receipt and computation source. Keep current archive limits. `python3 tools/verify_board.py ARCHIVE [--replay]` verifies binding and optionally reruns native cases.

UI owners use only this contract. All input/selection edits invalidate results and exports, including responses arriving after edits. The original full front silkscreen remains visible. The atlas does not color unsolved joints by risk, tile a solved mesh, sum package forces or imply self-alignment/yield.

## Force fixture interface

`force_lab/cad/spec.json` owns custom dimensions and quote-stage interfaces. The joint lower wettable face is z=0 and upper wettable face z=.150 mm. Both islands have nominal .200 mm diameter. Upper transparent cap is 2×2×.3 mm, carried by a horizontal 20×1 mm silica stalk. Show a noncontact optical corridor and complete load path to an unresolved cool sensor attachment. Separate x/z configurations index the sensor adapter while the joint stays horizontal. Custom base/bracket holes are internal fixture patterns, never invented vendor patterns. CAD, STEP, DXF and drawings must agree and be reimported/inspected. Sensor, bond, heater, thin-film process and chamber interfaces block fabrication release until accepted.

The separate force analyzer owns protocol, allocation, blank independent inputs/calibration/covariance/outcomes, native planning sensitivities, prospective freeze and later scoring. It preserves the original coupon scorer. Physical confirmation requires independent measured inputs, hot commissioning, and observed stable pinned boundaries. Planning values are not physical measurements.
