# Candidate A. One backend review for the screen and saved evidence

## Problem

A person can calculate and export a case, but must interpret signed forces and explain the archive themselves. The Board screen already has a declared fixture objective. Joint details also supports a different experiment that solves a gap under a downward load. The new explanation must preserve that distinction and travel with the exact numerical snapshot. Historical archives and their regenerated reports must stay valid.

## Usage, written before the types

A Board user sees the actual selected pad and a compact result explanation. Opening the case in Joint details and recomputing yields the same physical interpretation under the same inputs. The review says what changed, what stayed fixed, and which measurement would settle the question. Saving evidence includes an offline HTML review that a colleague can read without SolderShape.

A supported-load user instead sees the solved gap and its change under the declared load. Upward solder force is expected when balancing a downward load. This review does not apply the Board fixture objective. Selecting an offset sweep row selects that row's explanation and input identity. Editing clears the review with the existing results.

The application calls the following small interface. These are sketches rather than proposed bodies.

```python
# Generic solve, sweep and comparison API, after existing normalization and solve.
review = review_record(results, comparison=comparison, source=case["footprint_text"])
bundle = make_bundle(results, case["footprint_text"], case, comparison)
self.respond(200, {"results": results, "comparison": comparison,
                   "review": review, "bundle_base64": encode(bundle), ...})

# Board response. The persisted board-report.v1 shape does not change.
visible = public_report(report)
visible["review"] = review_record(report["results"],
    comparison=report["comparison"], source=report["editable_case"]["footprint_text"],
    board_selection=report["selection"])

# Inside bundle_board, use the existing generic bundle assembly.
make_bundle(report["results"], case["footprint_text"], case,
            report["comparison"], board_selection=report["selection"])

# Existing CLI call sites remain source compatible.
make_bundle(results, source, editable_case, comparison)
```

The screen renders the returned explanation rather than recalculating meanings in JavaScript.

```javascript
// app.js selected row, existing immutable response and resultIndex.
SolderShapeUI.renderReview(node, state.response.review, state.resultIndex);

// board.js, whole comparison and its candidate row.
SolderShapeUI.renderReview(node, response.report.review, 1);
```

## Shape

Keep the owner in `artifacts.py`. It already owns delivery of exact numerical evidence and is in the existing Board code-source identity. Two pure functions add one concept without adding a package, source-profile migration or dependency. Rendering and review derivation are separate functions because one owns semantics and one owns HTML escaping. Both consume the same review record.

```python
def review_record(results, comparison=None, *, source="", board_selection=None) -> dict:
    raise NotImplementedError

def review_html(review) -> bytes:
    raise NotImplementedError

def make_bundle(results, source="", editable_case=None, comparison=None,
                *, board_selection=None) -> bytes:
    raise NotImplementedError
```

`make_bundle` always derives `review.json` and `review.html` from its exact result list. It accepts no caller-authored review or HTML. The ordinary response derives the same pure record from the same immutable list, source bytes and trusted selection. Two inexpensive evaluations of one pure function are preferable to passing an independently editable interpretation through every call site. The record is not a new editable case format.

The record's data shape follows the dominant access patterns.

```text
Review
  schema = soldershape.review.v1
  operation = single | comparison | sweep
  physical_qualification = unqualified
  context
    footprint name and selected pad from result.footprint
    source_footprint_sha256 when nonempty source was supplied
    board_selection or absent
    starting-point provenance is never upgraded to board binding
  rows[]
    index, role, input_sha256
    condition = held_gap | supported_load
    input = exact canonical result.input
    equilibrium = exact canonical result.equilibrium when present
    numerical_status = refinement_checked | not_converged | failed
    model_warnings[], error or absent
    observables
      force_x_uN, force_z_uN when actually present
      gap_mm when actually available
      restoring_force_uN or null at zero offset
      load residual and tolerance only for a supported-load row
    headline, explanation[], measurement_next[]
  comparison or absent
    status = available | blocked
    reason or absent
    headline, explanation[]
    deltas only when valid under the existing comparison contract
  convention[]
  assumptions[]
  replay_instructions[]
```

Do not copy meshes, evidence blobs or entire native outputs into the record. Each row points to the exact input digest and the corresponding `case-NN` files. A brief's force is a predicted number even when numerically checked. `physical_qualification` is always unqualified in this scope.

Canonical numbers remain mm, mm³ and µN. The presentation shows a compact process-unit equivalent, such as `40 nL (0.04 mm³)` and `300 µm (0.3 mm)`. Never infer a missing input from the current form. Canonical JSON stays full precision. Display rounding is declared, and the HTML contains an exact-input table or embedded escaped JSON text for inspection. Raw errors and source names use HTML escaping. No scripts, external assets, fetches or active hyperlinks to arbitrary source text are required.

### One owner for interpretation

Move the current `screen_pair` implementation into `artifacts.py` unchanged and import it from `demo.py`. Board and Worked example retain exactly their current historical screen dictionaries. This avoids the `artifacts -> demo -> artifacts` import cycle and gives the review owner access to the existing held-gap objective without copying its rules. `demo.screen_pair` remains available by import for current callers. The archival `board-report.json` keeps the old screen and its original shape.

`review_record` can reuse that fixture screen for checked, nonzero-offset, held-gap comparisons. It must add explicit zero-offset handling before invoking the fixture rule. It must never call the fixture rule for supported-load results. For a historical recorded zero-offset screen, display that screen as its archived declaration and clearly use the new review's no-centering-comparison statement as the current explanation. Do not silently rewrite the stored report.

The following semantics live only in the Python review owner.

| Situation | Explanation and permitted numbers |
| --- | --- |
| Checked held-gap comparison | State the held gap. Compare restoring force and vertical force. Describe any sign change. The declared fixture objective is conditional and does not select production solder volume. |
| Checked supported-load comparison | State the downward load. Compare solved gaps. Explain upward force balances that load. A nonzero-offset lateral contrast can be secondary. |
| Negative offset | Restoration equals `-sign(offset) * Fx`. Positive means toward alignment. A raw positive X force can therefore be restoring. |
| Zero offset | No lateral restoration comparison. A supported-load gap comparison can still be available. A held-gap pair can show its observed forces without a centering preference. |
| Failed row | State the retained error. No fabricated force, equilibrium gap or mesh. Do not substitute zero for an absent number. |
| Not converged | Retain any returned numbers as unqualified numerical output. Withhold comparative conclusion. |
| Model warning | Keep the warning and actual observations. Withhold a volume preference even if numerical checks passed. |
| Single result or no reference | Describe that result and its condition. Do not invent a baseline, delta or winner. |
| Sweep | Each selected row carries its own offset, digest and explanation. No blanket optimum or tolerance-window claim. A failed row cannot inherit a neighboring row's forces. |

Existing `comparison.status`, its delta, and its reason remain authoritative for whether a formal comparison is available. The review describes them rather than implementing a second comparison gate. A held-gap fixture screen is a separately named, declared objective. It is not a universal quality score.

## File map and migration

- `artifacts.py` owns the review record, offline HTML and the relocated unchanged held-gap fixture function. `make_bundle` adds the two files before manifest hashing.
- `demo.py` imports `screen_pair` from its new owner. Historical outputs must compare equal before and after relocation.
- `__main__.py` adds a `review` field to current response payloads. CLI output gains the brief through the unchanged `make_bundle` call.
- `board.py` adds the review only to the visible API projection, passes trusted selection into bundle assembly, and verifies optional new review files against regenerated bytes. The serialized `public_report` and `_report` stay unchanged so strict historical equality still holds.
- `web/ui.js` owns a small text-only renderer. It receives the record and selected index. It contains no force-sign, gate or recommendation logic.
- `web/app.js` and `web/board.js` mount the result block beside the current force output and clear it with existing response invalidation. Both keep their tables and numerical diagnostics.
- `web/index.html`, `web/board.html` and the shared stylesheet provide one readable mount and modest styles.

`board.py` already fingerprints `artifacts.py`, `demo.py` and `__main__.py`. Keeping the new owner in `artifacts.py` means the source set does not change. Capture this module's loaded-source digest, in the same way `model.py` and `solver.py` already do, so importing `board.py` after editing an already-imported artifact module cannot falsely bind stale loaded code to new disk bytes. Update `LOADED_CODE_SHA256` from that captured artifact digest. Restart the server after backend edits.

New Board archives retain the review-producing source in their existing `calculation-source` members. Historical recordings validate their archived source hashes. Never update canonical recordings, manifests or ZIPs to current code merely to make the UI appear current. `response_payload` may attach a newly derived presentation to a verified old report while the original downloadable ZIP remains byte-identical and lacks a brief. The UI should identify that recorded download and offer fresh computation for a new brief.

## Archive integrity and verification

`make_bundle` inserts `review.json` and the exact UTF-8 `review.html` bytes before constructing `manifest.files`. There is no self-referential HTML hash inside HTML. The existing manifest is the authority for the HTML SHA-256. Both files travel with JSON, CSV, source and native evidence. HTML contains literal relative references to those fixed archive members and the existing replay command. Board uses `python3 tools/verify_board.py FILE.zip --replay`; ordinary results use `python3 -m soldershape replay FILE.zip`.

Keep `read_bundle`'s size, count, path, status, manifest and input checks intact. Old archives without review files stay accepted. New archives require both review members together. A small optional verification helper can compare their regenerated record and HTML bytes after canonical result validation, taking source and Board selection from the trusted archive checks. Do not execute archived scripts or embedded HTML during replay.

The member bound needs a concrete check. A seven-point sweep currently uses many native files. Confirm two extra members stay below 100 before accepting this design. Do not relax the existing resource limits merely to fit presentation.

## Gates before implementation is accepted

1. Open the Board 40/56 nL case in Joint details. Recompute. Both reviews retain 400 µm upper diameter, 300 µm gap, 240 µm offset and exact canonical values. Their fixture statements agree with the actual force signs.
2. Run the aligned supported-load example. Its explanation discusses a solved gap and upward load support without the held-gap no-upward-force rule.
3. Exercise a negative-offset pair, zero-offset pair, no-reference solve, three-row sweep, failed row, not-converged row and scope-warning row. Assert literal expected statements and exact row identities. Selection changes the visible snapshot and explanation together.
4. Edit a single field after computing. The prior review, force result and export vanish together. Restore a draft and require fresh calculation.
5. Download real Board and ordinary result ZIPs from the browser. Open extracted `review.html` offline. Compare every presented quantity and status with canonical result JSON and CSV. Recompute the HTML SHA-256 and match the manifest.
6. Use source names and error text containing `<img>` or `<script>` in focused tests. They render as literal text. No resource is fetched and no script executes.
7. Run existing generic replay and Board verification on new archives, plus old recorded archives. Preserve the original archive SHA-256 values. Demonstrate a tampered HTML member fails manifest verification.
8. Preserve numerical agreement separately from physical qualification. No review calls the model physically validated or production ready.

## Tradeoffs accepted

- We accept a somewhat larger evidence module in exchange for one semantic owner and no new tracked-source profile or import cycle.
- We accept server-generated explanation text in exchange for the screen and offline brief agreeing exactly. Localization is outside current requirements.
- We accept no readable brief inside immutable older downloads. A current preview can explain them, and a new computation produces the new artifact.
- We accept displaying rounded engineering equivalents alongside canonical numbers. The exact inputs remain available and are never reconstructed from displayed values.

## Alternatives considered

A browser-only interpretation and HTML exporter would avoid backend edits, but would force Python/CLI exports and browser displays to own the same scientific rules independently. Its shallow API hides formatting while exposing every caller to sign conventions and result gates.

A new `review.py` module would name the owner well, but adding it to `board.CODE_FILES` would require handling old and new exact source-file sets in the archive verifier. It earns its own file if the owner grows substantially. It does not earn that migration for the current compact record and HTML.

## Synthesis decision

Pending the parent arena's comparison against candidate B.

## Open questions and risks

Can the optional new review members fit every seven-row archive within the existing 100-member bound? Settle this with an actual bundle. Can the three main result states remain visibly distinct in the compact card without hiding existing diagnostics? Settle this in the running UI. Neither question needs a preference checkpoint.

## Next implementation step

Build the pure review record and its literal behavior checks against existing canonical results, then integrate the same record into generic and Board responses before adding the browser renderer.

Model the Domain made the row's condition and numerical status explicit. Boundary Discipline kept parsing and HTML escaping at their boundaries. Laziness Protocol kept the current schemas, source-profile set, routes and replay tools.
