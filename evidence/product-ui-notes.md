# Editable cases and design comparison UI

The UI keeps one current candidate and an optional reference containing only upper pad diameter and solder volume. Model the Domain shaped this choice: reference forces are never saved in editable input state. Both designs are recomputed using the current board pad, gap, offset, material, and gravity setting. Laziness Protocol kept the existing result viewer, immutable responses, and revision checks instead of adding another candidate form or saved-result store.

The changed files are `soldershape/web/index.html`, `app.js`, and `style.css`.

## Behavior

- Save editable case sends the draft to `/api/case` and downloads normalized JSON. It can run without a ready solver engine.
- Open case checks the file size, parses JSON, and validates through `/api/case` before applying any input changes. Invalid input preserves the current draft and computed results.
- A valid opened case restores the exact pad, every parameter, gravity, and optional reference dimensions. It clears computed results and downloads. It invalidates a computation already in flight.
- Parameter changes retain reference dimensions. A new footprint or a different selected pad clears them.
- Compare sends the complete editable case to `/api/compare`. It displays separate Reference and Candidate rows with upper diameter and solder volume. The existing row selector controls the mesh viewer. The offset chart is hidden for a design comparison.
- Raw computed forces remain visible with each row's numerical status. A derived delta appears only for a checked, nonzero-offset comparison. An inconclusive comparison displays its reason and retains the numerical evidence.
- The page separates numerical qualification from physical accuracy. The gap and volume helpers define their geometry reference, and the default surface tension is explicitly an example value.
- Model warnings appear alongside numerical warnings with a `Model scope:` prefix. The volume helper permits a curved surface to extend beyond the wetted pad planes; substrate obstacles require a separate clearance check.

## Checks performed

`node --check soldershape/web/app.js` passed. An HTML parser found 66 unique DOM IDs; all 56 literal JavaScript ID references resolve. The JavaScript contains no `innerHTML`. `git diff --check -- soldershape/web` passed.

A temporary Node VM harness executed the actual event handlers with a minimal DOM and mocked API boundary. It passed reference isolation after candidate edits, invalid-open preservation, exact case restoration, normalized JSON download contents, raw forces for an inconclusive comparison, checked delta rendering, comparison table and chart state, late computation response discard after opening a case, and reference reset on pad change. This verifies state behavior, not browser layout or the numerical engine.

The coordinating agent owns running-browser verification against the real backend. Its checks should cover file chooser downloads and imports, responsive layout, reference and candidate computation, inconclusive results, result ZIP contents, and the absence of console errors. The physical benchmark notice says the benchmark is under review and should be reconciled with the final scientific report before release.
