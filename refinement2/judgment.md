# Independent design judgment

Choose candidate A, with the smaller presentation and sign-handling details from B. The required product result is a readable review inside fresh numerical evidence ZIPs, covered by their existing manifest, and the same factual explanation in the app. B explicitly cannot satisfy that requirement and leaves CLI exports behind. Its browser-only artifact would be a second delivery convention without resolving the archive handoff.

| Criterion, 0 to 4 | A | B | Evidence |
| --- | ---: | ---: | --- |
| Usefulness | 4 | 3 | A produces the same readable artifact from browser and CLI. B improves the screen but introduces a separate HTML artifact. |
| Scientific fidelity | 3 | 4 | Both distinguish held gap from supported load. B is more explicit about force sign crossings and the genuine Board objective. A needs a Study exclusion and must not impose a fixture objective on every generic case. |
| Simplicity | 3 | 3 | A touches existing export and source identity owners. B touches fewer Python files but adds a parallel browser artifact and embedded ZIP handling. |
| Artifact integrity | 4 | 2 | A uses the existing manifest and archive reader. B's readable HTML is outside that manifest by design. |
| Total | 14 | 12 | A wins only after the safeguards below. |

## Minimal contract

Keep the pure semantic owner and escaped offline renderer in `artifacts.py`. This module already owns exact numerical delivery and belongs to the Board source profile. Do not add a new schema for editable cases, a framework, a browser ZIP writer or a second JavaScript prose engine.

```python
review_record(results, comparison=None, *, source="", board_selection=None) -> dict
review_html(review) -> bytes
make_bundle(results, source="", editable_case=None, comparison=None,
            *, board_selection=None) -> bytes
```

The return record is a derived presentation with one row per original result, exact canonical inputs and their hashes, condition, status, actual observations, retained failures or warnings, and physical qualification explicitly unqualified. It does not include mesh or native-output copies. The UI renderer receives this record and a selected index. It only creates text nodes and engineering-unit equivalents; it does not choose scientific conclusions.

The ordinary API can add a top-level `review`. `board.response_payload` can attach `review` to its local visible copy. **Leave `public_report`, `_report`, `board-report.json` and historical screen dictionaries unchanged.** `public_report` is called by `bundle_board` and the archive verifier relies on strict regenerated equality. Adding presentation there silently changes persisted protocol shape and breaks historical equality.

A source-bearing archive derives its own review from the actual bundled rows. Generate both review members only when `source` is nonempty, alongside the existing `source.kicad_mod`. This is an explicit source-bound brief contract. The internal source-free bundle remains raw numerical evidence. It does not accept caller-authored explanation text. Source-pad context comes from each row's footprint metadata. Board selection comes only from its trusted report. A copied Joint case has source-footprint identity, not Board binding.

## Required corrections and grafts

1. `study.bundle_study` calls `make_bundle(report["results"])`. Its rows include both `literal_rims` and `two_pad_cylinders`. The latter's volume includes metal-cylinder volume, its solved height includes metal thickness, and its mesh is an equivalent computational domain. An automatic generic brief must not describe those values as physical solder volume, physical gap or a literal solder mesh. The existing source-free call is the correct boundary: no single source footprint accompanies these multiple geometrical mappings. Generate the generic source-bound review only when `source` is nonempty. Every current user-facing Joint, Board and CLI solve call supplies its real source. Keep Study unchanged and retain its existing `decision.html` as the authoritative readable brief. This is smaller and safer than an extra flag or making the new generic owner understand Study corrections. Add a focused check that a Study export has no generic review and still retains the equivalent-domain labels.
2. Graft B's force-direction table and selected-snapshot behavior. At negative offset, a positive X force can restore alignment. A sign crossing must say restoring versus outward, not merely stronger magnitude. At zero offset, withhold a centering conclusion. An aligned supported-load pair may still support a factual solved-gap comparison even though the existing formal centering comparison is inconclusive. Label that distinction; do not change `calculate_comparison` or override its declared status.
3. Do not impose the held-gap fixture objective as a general production-quality rule. A genuine Board review can name the already declared fixture objective. A generic review can state actual held gap and force directions without inventing a universal volume preference. If sharing `screen_pair` is necessary, moving it unchanged into `artifacts.py` and importing it from `demo.py` avoids the cycle. If the new review only needs factual prose, leave that function where it is and avoid the relocation entirely.
4. Retain B's single accepted snapshot and selected-row discipline. On edit or stale response, clear review, exact recap and export with the same existing response invalidation. The review must never read a changed form and describe old forces.
5. Show engineering equivalents beside canonical units. Keep saved canonical numbers and exact input hashes unchanged. Blank raw drafts must remain unavailable, not become zero through numeric coercion.
6. Recordings stay immutable. A new API presentation may explain a verified recording, while its original download remains the old ZIP without the brief. Label that distinction and offer fresh computation. Do not regenerate canonical recordings to conceal it.

## Optional-member verification decision

Preserve the existing manifest hashing, path restrictions, member limits and canonical-result checks. Old bundles with neither review file remain accepted. If either new member is present, require both. The current manifest already detects a modified HTML member, so the core acceptance gate needs no new archive format.

Prefer one small helper that regenerates `review.json` and `review.html` from the normalized saved result list, optional saved source/comparison and optional Board selection, and compares the exact bytes after canonical input validation. It must be evidence-only and never run archived code or HTML. Board selection receives its real trust check in `verify_board`; generic reading must not claim trusted Board provenance merely because a similarly named member is present. Keep this optional-member helper separate from `public_report`. If it grows into new schema validation machinery, retain manifest verification plus pairing rather than expand this refinement into a protocol migration.

Capture `artifacts.py`'s source hash at module import and use that captured identity in Board's loaded-source map. Otherwise a previously imported artifact module followed by a disk edit and later Board import could claim new bytes for old loaded behavior. Restart the loopback service after the backend changes. Historical source sets stay unchanged.

## Concrete member-bound check

I constructed an actual in-memory bundle from seven repeated fully evidenced supported-load rows in `cohesion/evidence/custom-study.zip`, including their native height-solve evidence, source, editable case and comparison. It has 13 members per row and 96 members total. Adding `review.json` and `review.html` gives **98**, below the existing 100 limit. This was a structural capacity check, not a seven-point numerical sweep or physical validation. Do not relax the bound. Retain a final real seven-row export check after implementation.

## Acceptance evidence still needed

- Fresh default Board and corresponding Joint results agree in input identity, signed forces, unit equivalents and factual explanation.
- Supported-load, negative offset, zero offset, no reference, sign crossing, failure, not-converged and model-warning branches have literal behavior checks.
- Browser edits and pending responses cannot resurrect a stale review or download.
- Actual fresh Board and Joint downloads contain offline readable, manifest-hashed reviews matching canonical files. HTML-like pad names and errors render as literal text.
- Fresh archives pass the existing replay and Board verification; rehashed inconsistent optional reviews fail the chosen regeneration check if implemented.
- Old Board, demo and Study archives preserve their hashes and verification. The Study export remains correctly scoped without the generic review.

This recommendation changes interpretation and delivery, not calculation or physical qualification.
