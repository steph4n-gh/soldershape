# Study page implementation

The pad revision page is ready for the root agent's live browser checks at `/study`.

`study.html` defines a complete study form and server-owned result views. `study.css` gives it the existing workbench's colors, copper and teal revision cues, readable tables, and a responsive layout. `study.js` owns the editable input state, revision number, current operation, and result for that revision. `index.html` now links to the pad revision study and states that its existing reference compares upper-pad diameter and volume using one board pad.

The page loads the controlled planning example after bootstrap. Each revision has an independent footprint import, selected pad, actual copper diameter, persistent short source hash, full hash disclosure, and a required boundary evidence declaration. It does not infer resolved mask/CAM or wetting from a supported footprint.

Shared inputs include a supported normal load, liquid volume, upper diameter, material values, offset, and gravity. The criterion has a separate source declaration. The volume fraction is explicitly a finite three-point screen. The optional two-pad hypothesis requires finished-metal values and evidence. The server enforces its gravity restriction.

The browser displays the server's decision headline, reasons, next actions, scope, native nominal values, analytical Eq. 9 values, numerical differences, and volume samples. It computes no verdict. Physical qualification is always visibly unqualified. It offers normalized editable JSON through `/api/study/case` and a native evidence ZIP returned by `/api/study`.

Every form edit increments the revision and clears the result and download immediately. An asynchronous study, save, import, or open response applies only when its submitted revision remains current. Editing during a native computation keeps the request pending but discards its eventual result. The user can rerun after that request finishes.

## Control IDs

- `example-button` loads `/api/study/example`.
- `study-file` opens editable JSON. `save-study-button` downloads normalized editable JSON.
- `reference-file` and `candidate-file` import separate KiCad sources through `/api/import`.
- `reference-pad` and `candidate-pad` select source pads. Their `-diameter`, `-identity`, and `-hash` elements display actual geometry and identity.
- `reference-evidence` and `candidate-evidence` hold the independent boundary declarations.
- Shared numeric IDs are `upper_diameter_mm`, `volume_mm3`, `normal_load_uN`, `offset_mm`, `surface_tension_n_m`, and `density_g_cm3`. `gravity` is the shared checkbox.
- `gap-requirement`, `requirement-source`, and `volume-fraction` define the question and finite screen.
- `two-pad-enabled`, `lower-metal`, `upper-metal`, and `two-pad-evidence` define the optional geometry hypothesis.
- `input-evidence` records shared provenance. `run-study-button` submits `study-form`.
- `decision-heading`, `decision-state`, `decision-reasons`, `decision-actions`, `nominal-body`, `samples-body`, and `scope-list` display the server report.
- `download-study-button` downloads the returned ZIP. `study-digest` displays the normalized study hash.

## Checks performed

Node syntax validation passed for `study.js`. The HTML has 63 unique element IDs. All 22 label targets and all 28 static JavaScript element references exist. `git diff --check` passed for the owned files. The new files contain no long-dash characters.

The initial attempt to inspect the old port 8765 through CUA was blocked by the browser before any interaction. The root agent then supplied the new port 8766 and requested sole ownership of live browser verification. No browser result is claimed here.

Model the Domain changed the state shape to one draft and a result tied to a revision. The stale-response rule lives in the shared invalidation operation. The page uses plain JavaScript and one stylesheet with no new dependencies.
