# Board explorer UI

The board explorer is a dedicated page in `soldershape/web/board.html`, `board.js` and `board.css`. It uses the actual native ULX3S front copper and complete original silkscreen at `/board.svg`. Original board and license downloads remain available before computation.

The data shape separates immutable source context, selected component UUID and pad index, editable process request, revision, pending request and accepted result. Every selection or process-input edit increments the revision and removes both meshes, force values, result identity and export URLs. A response from a prior revision cannot restore them. Native computation remains locked until its pending request ends, while all inputs and selections remain editable.

The complete board has component hit regions, a native component selector and a searchable list. Duplicate zero-pad graphics use UUID identity in the browser and remain inspectable. The linked inset uses normalized actual pad positions. Its dropdown, pointer selection and arrow keys select individual pads. Board overlays use the explicitly extracted local +X vector and native board-coordinate bounds. Back-side, rectangular and graphic selections remain inspect-only and clear old results.

The process controls declare hypothetical upper pad, gap, offset, two liquid volumes, surface tension, density and gravity. The source determines the lower copper diameter. Both result cards use the existing `SolderMesh.drawSurface` function with actual native vertices and triangles, one camera and the same physical scale. Force arrows show direction only. The server supplies the conditional objective and numerical or scope blockers.

The page can show a verified initial recording if the backend advertises it. It labels that recording and always offers a fresh native computation. No request copies one computed mesh across other pads. No board or package force sum, risk color, yield or motion prediction appears. Unresolved published-data force validation and missing independent process measurements remain visible.

Static verification passed. Node accepted the JavaScript syntax. The HTML has 65 unique IDs and all 40 static JavaScript DOM references exist. Native context was inspected directly and matches the expected field names, counts and U1 J16 identity. Root owns the actual browser workflow, downloaded archive checks and screenshot verification.

Model the Domain changed the state representation so accepted numerical evidence has a distinct owner and revision. Experience First changed the page scope to one full board, one selectable pad and one complete comparison, with unsupported selections explained rather than hidden. No new browser dependencies or numerical implementation were added.
