# Native local workbench

## Architecture decision

Use candidate A's Python standard-library loopback service and offline browser assets. Use candidate B's immutable result bundles and explicit failed sweep rows. An independent design review preferred this shape because interactive pad selection and parameter editing are acceptance requirements. Both candidates rejected a full port for first delivery.

The service has no database, framework, accounts, CDN, or persistent result cache. Each solver process owns a temporary directory. Setup downloads and verifies upstream source into `.engine`, which is excluded from version control. The local source and executable identities are both recorded. This corrects candidate A's original bundled-source suggestion.

The public data shape is a validated frozen `JointSpec`. `model.py` owns KiCad parsing and millimeter inputs. `solver.py` owns unit conversion, trusted model generation, native computation, diagnostics, and mesh extraction. `artifacts.py` creates exports and safely replays normalized inputs. `__main__.py` owns CLI and HTTP translation. Browser assets render the returned mesh and invalidate results on every input change.

## Shared response contract

`solve(spec)` returns a JSON-serializable dictionary with the following keys. Numerical values use the units in their names.

```json
{
  "input": {"lower_diameter_mm": 0.2, "upper_diameter_mm": 0.2, "standoff_mm": 0.15, "volume_mm3": 0.006, "offset_mm": 0.02, "surface_tension_n_m": 0.48, "density_g_cm3": 9.0, "gravity": true},
  "input_sha256": "canonical-input-digest",
  "status": "refinement_checked",
  "forces": {"x_uN": -1.0, "z_uN": 1.0},
  "diagnostics": {"volume_relative_error": 0.0, "force_change_relative": 0.001, "negative_eigenvalues": 0, "mesh_volume_error_relative": 0.0002, "warnings": []},
  "levels": [{"level": 0, "facets": 432, "force_x_uN": -1.0, "force_z_uN": 1.0, "energy_erg": 1.0, "volume_mm3": 0.006, "volume_relative_error": 0.0, "negative_eigenvalues": 0}],
  "mesh": {"vertices_mm": [[0.0, 0.0, 0.0]], "triangles": [[0, 1, 2]]},
  "mesh_checks": {"closed": true, "volume_mm3": 0.006, "triangles": 6336},
  "engine": {"version": "2.70a", "source_sha256": "digest", "binary_sha256": "digest"},
  "evidence": {"model_fe": "trusted generated model", "commands": "trusted generated script", "stdout": "raw output", "stderr": "raw errors"}
}
```

These numbers illustrate the schema. They are not measured results. Missing numerical results are errors, never placeholders. An otherwise completed solve that misses a check has status `not_converged` and explicit warnings. A failed sweep row has its normalized `input`, `input_sha256`, `status: failed`, `error`, and any captured engine evidence.

## Browser API

- `GET /api/bootstrap` returns `token`, `example` with `filename` and `text`, and engine readiness. Only loopback Host is accepted.
- `POST /api/import` accepts `{ "footprint_text": "..." }` and returns `{ "footprint": { "name": "...", "sha256": "...", "pads": [...] } }`.
- `POST /api/solve` accepts `{ "footprint_text": "...", "pad_index": 0, "parameters": { ... } }`. Parameters are all `JointSpec` fields except `lower_diameter_mm`, which comes from the selected pad.
- `POST /api/sweep` accepts the solve body plus `offsets_mm`, a list of at most seven finite offsets. Every point computes independently. It returns failed rows as well as solved rows.
- Solve and sweep return `{ "results": [...], "bundle_base64": "...", "bundle_filename": "soldershape-case.zip" }`. Each successful result also has `footprint` provenance. ZIP bytes come from these accepted results, not later form state.
- Errors return non-2xx JSON `{ "error": "plain reason" }`. JSON POSTs require `X-SolderShape-Token`, exact content type, bounded body length, expected Host, and matching Origin when present. No CORS. One computation runs at a time.

The frontend owns `footprint_text`, selected pad index, physical form values, and an input revision. Any edit clears the displayed result and disables downloads. Obsolete asynchronous responses are ignored. Pad labels enter DOM text only.

## Verification policy

Capture quadratic forces, volume, refinement changes, energy stationarity, and local Hessian sign before export. Refine the curved mesh once and convert to linear elements for display and export. Report tessellation volume error separately. A refinement check does not establish global minimality, unique equilibrium, physical accuracy, or manufacture readiness.

Archive replay checks member hashes and sizes, parses normalized JSON inputs, and generates the current trusted templates. It never executes archived Evolver scripts. Representative mesh self-intersections receive a separate independent check during acceptance.

## Editable cases and controlled comparison

The release design compared two whole shapes. Two editable candidates would duplicate form ownership and invalidation. A frozen solved baseline would preserve an earlier operating point and require rules for differing gaps, offsets and materials. The selected smaller shape stores only the reference upper diameter and volume beside the current editor. Both designs always use the current shared conditions and compute afresh. There is no saved-result database.

```json
{
  "schema": "soldershape.case.v1",
  "footprint_text": "original KiCad text",
  "pad_index": 0,
  "parameters": {"upper_diameter_mm": 0.2, "standoff_mm": 0.15, "volume_mm3": 0.005, "offset_mm": 0.02, "surface_tension_n_m": 0.48, "density_g_cm3": 9, "gravity": true},
  "baseline": {"upper_diameter_mm": 0.2, "volume_mm3": 0.006}
}
```

`baseline` may be null. `parse_case(data)` in `model.py` validates the exact input-only shape through the existing footprint and joint validators. `normalize_case(data)` at the transport boundary checks that formatted saved JSON fits the same 2.1 MB limit used by Open case. No engine code, force claims or file paths are accepted in this format.

`POST /api/case` takes this object and returns normalized `case` and imported `footprint`. It does not run the solver. The browser applies it only after complete validation and only if the draft revision is unchanged. Opening a case clears computed results. A rejected file preserves the current draft and result.

`POST /api/compare` takes the same object and requires a reference. `calculate_comparison(case)` calls the existing public calculation path for Reference and Candidate. Each row keeps its own status, model, evidence, mesh and input digest. The response includes `comparison` with both designs and conditional deltas. A failed numerical check, zero offset, or detected pad-plane excursion suppresses the centering comparison verdict. Raw computed forces and failures remain inspectable. Ordinary solve/sweep also accept optional `baseline` so their exports preserve the editable draft.

`make_bundle(results, source, editable_case, comparison)` reuses the existing archive format and adds hashed `editable-case.json` and `comparison.json` when supplied. Replay continues to regenerate trusted numeric inputs. The browser does not send previously computed forces back for acceptance.

The engine now uses energy-decreasing `hessian_seek` steps and more bounded gradient relaxation. Numerical thresholds and strict native-warning rejection are unchanged. A separate product diagnostic reports sampled mesh excursions beyond the pad planes. It does not turn local numerical checks into physical clearance certification. The physical runner retains its own exact paper-specific plane and load-direction diagnostics.

The standard-library server and existing numerical engine remain the entire runtime. Case files, comparisons and launcher reuse add no dependency, service or persistent shared state. This is the Laziness Protocol choice. Separate input-only case state and computed immutable evidence are the Model the Domain choice.
