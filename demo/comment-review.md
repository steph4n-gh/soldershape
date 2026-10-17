# Extreme demo comment review

Reviewed the application diff against `ffe314f` and the new demo files. Application and test files were read only. No native simulations were run.

## Finding

One small deletion is justified. `tests/test_demo.py:2` imports `io`, but no expression references that name. A Python AST scan confirmed it is the only unused import in `soldershape/demo.py`, `tools/build_demo.py`, `tools/verify_demo.py`, and `tests/test_demo.py`. Delete that import. This does not block the demo.

## Comments and suppressions

The new demo Python, JavaScript, HTML, CSS, verification tool, build tool, and test files contain no source comments, lint suppressions, type suppressions, or constraint comments. The scoped changes to `__main__.py` and `app.js` add none.

Deletion count is zero. Restored comments, reruns, constraint keeps, encoding offers, and unenforced constraints are zero. No architecture sketch is required for the unused import.

## API shapes and lifecycle

No new guessed API fallback was found. `resultGeometry` chooses the recorded equilibrium when present and the recorded request for a failed fixed-gap solve. The failed case intentionally has no mesh or force fields. The optional force access in the view preserves that distinction. The HTTP route reports verification errors instead of inventing substitute data.

The inherited `app.js` engine-readiness fallback chain is unchanged by this diff. It is outside this extraction review.

`mesh-view.js` extracts the existing triangle drawing implementation without adding a second copy. The demo owns a linked camera and one scheduled animation frame for its two canvases. The workbench owns its independent camera and chart redraw. Their different camera bounds and view composition make a new general lifecycle abstraction unnecessary here. `renderExperiment` runs once after the single fetch, so its append operations do not require repeated-render cleanup under the implemented lifecycle.

Laziness Protocol shaped the review. Retain the small mesh extraction and delete the unused import. Do not introduce a generic camera framework to remove a few similar event handlers.

No release-blocking comment, suppression, guessed API, or lifecycle finding was identified in the requested scope. This is a static review of those concerns. It does not establish physical validity or replace the running-browser verification.

Root accepted and deleted the one unused import. One deletion, no restored comments or suppressions, no rerun or additional architecture needed. No constraint remains open.
