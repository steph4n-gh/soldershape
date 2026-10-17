# Demo wire and rendering contract

Root owns demo.py, recording tool/protocol/data, __main__.py, existing app.js and old index.html. UI delegate owns only web/demo.html, demo.css, demo.js and mesh-view.js. No shared source writes.

GET /api/demo returns exactly the following top-level fields.

- title and question strings, recorded true, physical_qualification "unqualified".
- archive {url:"/demo/evidence.zip", sha256:string, case_count:7}.
- footprint is existing import_footprint result with pads and sha256.
- selected_pad_index:0, pitch_mm:.4.
- assumptions array of strings, baseline string.
- samples array of {id,label,kind,reference,candidate,screen,editable_case}. id is offset-40, offset-120, offset-200 or compressed. kind is volume_comparison or compression_control.
- reference and candidate are actual existing native result dictionaries, including input, equilibrium when available, status, forces when available, exact mesh when available, diagnostics, mesh_checks, input_sha256, model_warnings, engine. Failed case has error and no mesh/forces. These records contain no raw solver text in the browser response. Raw evidence is in original archive.
- screen {status,headline,details,reference_rule_met,candidate_rule_met}. status conditional_comparison, outside_model_scope or numerical_failure. rule_met values boolean or null. Only conditional_comparison may express a force preference. details array strings.
- editable_case is existing soldershape.case.v1 JSON with original footprint_text,pad_index,parameters,baseline. For volume samples reference5nL and candidate7nL. For compressed control, single7nL60um case with baseline null.

Use /demo/evidence.zip for actual archive download. Create a Blob for selected editable_case JSON, instruct Open case in existing workbench, then fresh Compare or Solve. No second editor or live solver request from the demo. Add navigation to / and /study. Do not show engine readiness as a requirement for recorded inspection.

Default selected sample offset-120. Both views show native meshes at equal physical scale with linked orbit/zoom. Desktop first viewport shows the question, recorded badge, held gap, selected offset and signed forces with model status. Show an actual footprint plan context with selectedpad and offset, not36procedural solder joints. State only the highlighted joint is modeled. Support keyboard-accessible discrete buttons and readable native table. Always retain outside-scope and failed rows. Show compressed control as same volume with gap change, never misleading volume labels.

mesh-view.js is a non-module deferred script exposing window.SolderMesh.drawSurface(ctx,mesh,project,standoffMm,wireframe). Copy only the existing exact triangle drawing core, with same shading and optional mesh edges, out of app.js. project maps3Dvertex to[x,y,depth]. Root will replace that core in the old viewer with this call and add its script tag. UI owns context,pad boundaries,force arrows,labels,camera. No new dependencies. Never modify mesh vertices to animate or exaggerate them.
