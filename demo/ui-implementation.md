# Extreme demo UI implementation

The page consumes the exact recorded experiment from `GET /api/demo`. Its data state is the immutable experiment plus one selected sample ID. Its separate camera state belongs to both native mesh views. The browser displays the server-owned screen headline and details. It does not score a design or request a solve.

The initial sample is the 120 µm comparison. The subtitle states the held gap and declared force objective before the model cards. The compression subtitle names both gaps and the fixed volume. Each card shows signed X and Z force, numerical status, held gap and offset before any detailed evidence. Discrete buttons select the recorded 40, 120 and 200 µm cases. The compression button selects a same-volume gap control and changes the card titles to the held gap. All seven records remain visible in the numerical table.

`mesh-view.js` extracts the existing workbench triangle drawing core. It preserves the original shading and optional mesh edges. It owns no DOM or camera. Both demo canvases use one camera, one center and one physical scale. Neither mesh is interpolated, animated, scaled independently or altered. Force arrows show sign only and say so on the canvas. Pointer, wheel and keyboard controls move the linked camera. Home and Reset view restore its original pose.

The footprint canvas draws actual imported pad positions and highlights only the selected joint and upper-pad offset. The text states that neighboring joints are not computed. A failed record draws no geometry. A model scope warning is amber even when numerical refinement passes. No state uses a green manufacturing approval treatment.

The selected editable case downloads as existing `soldershape.case.v1` JSON. The page instructs the user to open it in the original workbench and run a fresh Compare or Solve. The other download points to the actual native evidence archive. Its SHA-256 is visible. Recorded inspection does not require a local engine readiness check.

Experience First kept the first view about the engineering consequence and removed editing controls from the demonstration. Model the Domain kept recorded samples and server verdicts together, which prevents a second browser decision implementation. The selected design and root-owned contract provide the architecture sketch for this delegate.

Checks completed by this delegate.

- `node --check soldershape/web/demo.js` passes.
- `node --check soldershape/web/mesh-view.js` passes.
- `git diff --check` passes for the working tree at this checkpoint.

Actual browser interaction, route integration and downloaded artifact verification belong to the root verification pass. No native computation or physical validation ran in this UI delegate.
