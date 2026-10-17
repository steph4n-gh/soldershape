# Study implementation contract

The selected design is refinement/design.md. Keep this wire shape exact so browser and service can be implemented independently. All writes are disjoint.

```json
{
  "schema": "soldershape.study.v1",
  "reference": {"footprint_text": "...", "pad_index": 0, "boundary_evidence": "user-supplied evidence or planning assumption"},
  "candidate": {"footprint_text": "...", "pad_index": 0, "boundary_evidence": "user-supplied evidence or planning assumption"},
  "parameters": {"upper_diameter_mm": 0.28, "volume_mm3": 0.01715728467880506, "normal_load_uN": 6.864655, "offset_mm": 0, "surface_tension_n_m": 0.48, "density_g_cm3": 8.5, "gravity": false},
  "requirement": {"pad_face_gap_um": 185, "source": "declared study question, not production rule"},
  "volume_fraction": 0.05,
  "two_pad": {"lower_metal_um": 35, "upper_metal_um": 35, "evidence": "planning only, finished metal must be measured"},
  "input_evidence": "Artificial coupon planning assumptions. Not measured physical inputs."
}
```

`two_pad` may be null. Each arm's lower diameter always comes from its own footprint. Shared parameters follow LoadSpec excluding lower_diameter_mm. No prescribed-gap study in this narrow workflow. volume_fraction 0 through0.20. The optional two-pad approximation requires gravity off. Evidence/source fields are nonempty strings with reasonable length bounds. Native calculations remain allowed with nonzero offset or gravity when otherwise supported, but no analytical scenario conclusion is eligible then.

Backend public operations in soldershape/study.py.

- `read_study(data)` returns a normalized JSON-safe dictionary or raises InputError.
- `run_study(data)` normalizes, computes2or4nominalnativecases and returns a JSON-safe report.
- `bundle_study(report)` returns bytes for the original native bundle plus study inputs, both footprint sources, static report, samples.csv and hashes.
- `replay_study(path)` verifies integrity and regenerated request identity, recomputes native and analytical reports, and returns JSON-safe {passed:bool,...}.

Report shape.

- schema soldershape.study-report.v1, study normalized input, study_sha256.
- physical_qualification always unqualified.
- results list of native result records, each carrying design Reference or Candidate and mapping literal_rims or two_pad_cylinders. Preserve input, hash, mesh/evidence/failure and footprint metadata. Add pad_face_gap_um for converted output or null.
- decision {status, headline, reasons:list[str], next_actions:list[str]}. statuses assumption_sensitive, screened_samples, sensitivity_unavailable, numerical_failure, model_scope_inconclusive. No winner or production approval.
- samples list of {design,mapping,volume_mm3,method,gap_um,margin_um,eligible,reason}. method analytical_eq9. Include nominal and both declared volume points.
- nominal list of {design,mapping,lower_diameter_mm,native_gap_um,analytical_gap_um,native_minus_analytical_um,margin_um,status}.
- scope list of plain-language limits including finite samples, analytical applicability, unverified wetting, pad-face datum, equal isolated-joint load and no manufacturing qualification.

The backend may add fields without changing these. It owns policy and all display text for decision reasons. Browser only renders reports. Native negative controls are clearly labeled synthetic tests.

Root owns __main__.py API and CLI. POST /api/study/case returns {study:normalized}. POST /api/study returns {report,bundle_base64,bundle_filename}. Existing /api/import returns footprint data. GET /api/bootstrap supplies token and engine. GET /api/study/example supplies the controlled planning input. GET /study serves study.html. All use existing token, loopback policy and computation lock. Study body limit4.3MB, each footprint2MB. Existing routes keep their bounds.

Browser study.js owns one editable study plus a revision counter. Every edit invalidates result and download. A late response may apply only to the submitted revision. Save/open JSON uses normalized document via /api/study/case. User can import reference and candidate footprints independently through /api/import. Keep older case JSON in existing force viewer with no migration needed.
