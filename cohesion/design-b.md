# Candidate B. A board-led SolderShape.

## Caller journey.

1. Open Board explorer. See one plain promise. “Compare how solder amount changes the shape and forces of one joint. Save a question you can reproduce and test.”
2. Select the source component and circular pad. The board, selection identity and local offset direction stay visible. Unsupported pads remain inspectable and state why computation is unavailable.
3. Set reference and candidate solder amounts. Run the existing comparison. The first recording stays explicitly labeled as an example. Editing clears it before anything can be saved as current evidence.
4. Choose “Inspect this joint” beside the comparison. The exact candidate case and reference dimensions open in Joint details. A source strip says “Copied from ULX3S / U1 / pad …”. It links back to the saved board selection and explains that the editable copy is not board-bound evidence.
5. Edit one input, run Compare, inspect the actual mesh and forces, then save the editable case or numerical evidence. A persistent next step offers physical-test resources.
6. Return to Board explorer. Selection and all entered values survive. Current numerical results do not silently reappear as if recomputed.

People get a repeatable, narrow engineering question today. The app can reveal a surprising tradeoff, show its assumptions, retain numerical evidence and prepare a physical test. It cannot determine assembly yield or approve a board.

## One product, four roles.

| Navigation | Role and leading action |
| --- | --- |
| Board explorer | Guided main entry. Select an actual pad and compare solder amounts. |
| Joint details | Inspect or edit one case, compute a force comparison, or sweep offset. Import an own footprint here. |
| Pad comparison | Compare two actual footprint revisions against an explicit gap question. |
| Worked example | Learn the volume tradeoff and see retained scope and numerical failures. |

Use one header, brand destination, ordered navigation, current-page treatment, typography and action styling. Keep the board visual as the product anchor. Avoid another overview dashboard, repeated marketing cards or a new wizard.

Keep engine state in the same header position on editable tools. A recorded example says “Recorded calculation” in that position. Use one compact qualification message on every page. Expand supporting evidence only when requested.

## Routes and compatibility.

Make `/board` the named product home and brand destination. Keep `/` as Joint details and retain every current deep route. Change the CLI's displayed starting URL to `/board`, if needed. This avoids changing saved bookmarks, tests and the source-bound numerical routes merely to satisfy a hierarchy.

This is board-first through entry, order and action flow. A user importing their own footprint can still enter Joint details directly. The user does not need a board to use the solver.

The stronger but more disruptive variant would make `/` serve the board and move the workbench to `/joint`. It earns no extra user capability and complicates current tabs and links. Reject it.

## Core data and ownership.

Reuse `soldershape.case.v1` as the only cross-page numerical case. Keep `soldershape.study.v1` as a distinct two-revision experiment. Do not coerce a held-gap board case into a supported-load study.

Add one namespaced `SolderShapeUI` module in an IIFE. Existing top-level `$` and `state` bindings cannot be combined. Its shared records contain inputs and display context only.

```
Draft = { version: 1, savedAt, page, inputs }
Handoff = { version: 1, createdAt, case, origin: { label, href, kind } }
saveDraft(page, inputs) -> { ok, message? }
readDraft(page) -> inputs | null
openCase(case, origin) -> Promise<void>
consumeCase() -> Handoff | null
```

Use separate `sessionStorage` keys per page and a one-use handoff key. This preserves navigation and reload within the current tab without letting five open tabs overwrite each other. Storage size failures must produce a visible notice and leave Save available. No silent truncation, token storage, result blobs or archive persistence.

Persist raw input strings, including temporarily invalid edits. Restoring “0.” must not silently become a different value. Rebuild normalized cases only at the existing server boundary. Draft restoration clears results and requires a fresh solve.

For a handoff, normalize through `/api/case`, store the normalized case and origin, then navigate in the same tab. The destination validates it again, discards old results and applies it through the existing case-opening path. Consume only after successful application. A failed or expired handoff leaves the user's saved draft available.

Board handoff can use `report.editable_case` after the current comparison. Until then, the button says “Compute to inspect this comparison”. Demo uses `sample.editable_case`. Neither requires a download and re-upload.

Study handoff names the selected revision and pinned geometry mapping. Build its ordinary case from that exact study input snapshot and normal-load parameters. Do not hand off an equivalent-cylinder two-pad mesh as physical solder. If that path is not implemented faithfully, keep its limitation explicit rather than showing a misleading general Inspect link.

## Files and boundaries.

`web/ui.js` owns common chrome behavior, bounded draft storage and the one-use case handoff. `web/ui.css` owns shared header, navigation, status and next-step styling. Existing page scripts keep their domain logic, forms and numerical rendering.

`index.html` and `app.js` gain a source strip, common navigation, draft restore and a shared `applyCase` path for file and direct handoffs. The baseline reset bug disappears because bootstrap imports the unrelated example only when neither a valid handoff nor a saved draft exists.

`board.js` saves component UUID, pad index, raw comparison fields and optional search state. It restores after fetching the trusted board context, validates that selection against that context, and shows a clear fallback if the source board changed.

`study.js` saves both source texts, selected indices, evidence fields and raw form fields. `demo.js` saves selected recorded sample only. A draft from one page never overwrites another page's draft.

Add an allowlisted lab resource section shared in the footer or next-step strip. Expose the existing package, handbook and protocol via fixed server routes. Show exact package status and geometry. The 200 µm force fixture does not validate the board's 400 µm pad hypothesis. Do not auto-fill the force protocol from an arbitrary board case.

No solver changes, numerical schema changes, historical archive rewrites, new router, framework, account system or cloud persistence.

## Falsifiable completion gates.

- Each page has the same four navigation destinations, the correct current-page marker, a working brand link and accessible lab resources.
- Board selection to current comparison to Joint details preserves footprint bytes, selected pad, every parameter and reference volume exactly. Demo does likewise for each selectable case.
- Change workbench volume to 0.0053 mm³, visit Pad comparison, return and reload. It remains 0.0053. Reference state and imported footprint survive too.
- Navigate during an invalid edit and restore it unchanged. A storage denial is visible and does not prevent manual case save or calculation.
- A successful result becomes unavailable for export after any input change. In-flight stale results cannot reattach after navigation, restore or another handoff.
- Run the handed-off case in Joint details and verify the downloaded archive against its actual current inputs. Board-bound evidence remains downloadable separately.
- All visible internal links return the expected page or real artifact. Lab files have correct byte counts and recorded hashes. No fabricated lab acceptance or physical validation appears.

## Tradeoff.

This candidate prioritizes the board experience the user already likes and gives it a complete exit into useful work. It preserves the four tools rather than forcing incompatible experiments into one form. It loses against a single-workbench design if users primarily import their own footprints and almost never use the board example. Shared navigation and continuity still remain valuable in that case.
