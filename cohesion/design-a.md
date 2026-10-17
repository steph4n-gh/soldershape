# Candidate A. One workbench with connected tasks

## Caller journey

A first-time user opens Board explorer, sees what the tool can answer today, selects U1/J16 and compares solder volumes. They choose Inspect this comparison, arrive at Joint workbench with the exact footprint, pad, two volumes and assumptions, edit an input and compute fresh results. They save the case or evidence. Test with a lab leads to the current force-test package and its open qualification gates. Returning to Board explorer restores its draft, without presenting its prior forces as current.

A user with their own footprint opens Joint workbench directly. Compare pad revisions is a separate task for two real footprint sources and a gap criterion. Worked example explains the force tradeoff and retained failures. Its Open this example action transfers the selected exact case to Joint workbench. Every task uses the same navigation and the same account of physical limits.

## Whole product structure

Keep existing routes. Use consistent labels and order everywhere. Board explorer `/board`, Joint workbench `/`, Pad comparison `/study`, Worked example `/demo`, Physical test `/lab`. Brand links to `/board`, the strongest guided entry. Mark only the current task with `aria-current="page"`. Use one common header and one short product promise. "Explore how one solder joint changes with your design assumptions. Save a reproducible comparison and prepare a physical test."

The current value is a traceable engineering question. The board supplies actual copper context. The native engine supplies conditional shape and force comparisons. Saved cases and evidence let another person inspect or reproduce them. The app does not currently approve pad designs or demonstrate accurate physical forces.

Do not combine all forms into one giant page. Their scientific contracts differ. Instead, make the boundaries understandable and useful through direct case handoff. Remove duplicate top-of-page lists of arbitrary other screens. Give each task one next action at its evidence/handoff area. Use a compact common qualification line, with detailed limitations retained near results.

## Visual system

Add `soldershape/web/workspace.css` and `workspace.js`. Load before each page script. A small static page registry owns navigation labels and hrefs. Shared CSS owns header, typography, focus, buttons, shared spacing, status badges and the compact purpose/qualification block. Existing page CSS retains grids, canvas dimensions, chart and data layouts. Resolve conflicting header and button selectors explicitly instead of adding increasingly specific overrides.

Use the Board explorer palette and type scale as the base. Label computed data Fresh computation, Verified recording, or Inputs only. Use amber for scope/qualification limits and red for actual failed operations. Keep exact provenance expandable rather than making hashes dominate the main path.

## Data shapes first

`PageDraft = {schema: "soldershape.browser-draft.v1", page, saved_at, source_identity?, inputs}`.
`inputs` contains exact input strings, checkboxes, selected pad indices and raw footprint text. It never contains tokens, numerical results, force labels, meshes or export ZIPs.
`CaseTransfer = {schema: "soldershape.case-transfer.v1", id, created_at, from, label, case, origin?}`.
`case` is the existing `soldershape.case.v1` value accepted by `/api/case`. `origin` is display context only. It cannot confer a verified board-bound export or alter solver parameters.
`PageDraft` lives in `sessionStorage` under one namespaced key per page. This preserves navigation/reload in the current tab and avoids cross-tab overwrite. Downloads remain the durable, portable save mechanism. Explain that distinction in the save area.

## Concrete functions and owners

`workspace.js` exposes `SolderShapeWorkspace.readDraft(page)`, `writeDraft(page, inputs, sourceIdentity)`, `discardDraft(page)`, `openCase(caseValue, origin)`, and `readTransfer(id)`. It validates schema, page, byte limits and basic field types, catches blocked/quota storage errors, and displays an explicit recovery notice. It owns no physics or page field IDs.
Each page owns its own `captureDraft()` and `restoreDraft(record)`. Its existing `invalidate()` writes the latest raw draft after inputs change. Input strings preserve temporarily empty or invalid numeric fields. Restore reuses `/api/import` to parse footprint text; it does not trust cached parsed geometry. Valid case transfers reuse `/api/case` before replacing the destination form.
`app.js` extracts the existing case-open application logic into `applyEditableCase(checkedCase, footprint)`. Both file upload and direct transfer call it. Incoming case uses `/?open=<id>` in the same tab. Keep the previous Joint workbench draft as one recoverable backup until the user chooses another case or clears it. Show "Opened from Board explorer. Previous draft retained. Restore previous draft." This prevents a useful direct action from silently destroying prior work.
`board.js` persists selected component UUID, pad index, process strings and component filter with `source.board_sha256` and extractor identity. Its Inspect this comparison action requests a validated editable case for the current draft, independently of whether native computation succeeded. Do not require another expensive solve to transfer inputs.
`demo.js` persists selected recorded offset/control and uses `sample.editable_case` for Open this example. The recording remains immutable. Opening it yields inputs with an explicit "Run again for fresh forces" status.
`study.js` persists its full existing scientific contract, including both footprints, evidence text, gap criterion, volume range and two-pad correction. Do not coerce a board volume comparison into a pad-revision study or fabricate the missing second source.

## Lab handoff

Add a small `/lab` HTML page using the common shell. Serve only a fixed allowlist of existing release files. Offer the force-lab ZIP, handbook PDF, RFQ and package verification instructions. Show Quote-ready / Lab accepted / Fabrication released / Physically validated as explicit states, with only Quote-ready true. Explain the current uncertainty failure and conditional tighter budget in plain language. Keep original 220 vs 270 height-coupon resources separately labeled. Do not imply the force fixture tests arbitrary Board explorer geometry.

Lab page links back to the selected question via browser draft when available, otherwise Board explorer. It should say "This package tests the 200 µm-pad force experiment. A different pad or alloy requires a new measured-input plan." Avoid a generic "Validate my board" action.

## Edge cases and safety

- Editing during a solve keeps existing revision guards. Draft writes must not restore a late result or export.
- Navigation or reload restores inputs only. The UI explicitly says fresh computation is required. Recorded default preview must never overwrite a restored or transferred draft.
- Restoring a Board explorer draft requires the exact current board/extractor identities. On mismatch keep its raw JSON available for download and explain why the default was loaded.
- A malformed/oversized/unknown-schema transfer is rejected without altering current inputs. Remove the transfer query only after successful application. Do not read arbitrary filesystem paths from the URL.
- Session storage unavailable still permits work, downloads and file-open. A direct handoff failure offers Save editable case rather than an empty destination.
- Back/forward, tab duplication and bfcache retain page-specific input identity. No saved force becomes current merely because navigation restores its DOM.
- Unsupported pads remain inspect-only. Draft restore or case transfer cannot promote support or recover an export for them.
- Existing solver source hashes and historical archives remain unchanged. New shared UI code does not edit computational contracts.

## Acceptance evidence

1. All five navigation items, brand links and concrete lab downloads work from each task. Current task state is correct at desktop and narrow width with keyboard focus visible.
2. Set Joint workbench volume to 0.0053 mm³. Navigate to Pad comparison, Board explorer and back. Reload. Exact value and source footprint survive, while forces and export are absent until recomputation.
3. Change a Board explorer pad and process values. Inspect this comparison transfers the exact lower source, selected pad, material, gap, offset and both volumes. A fresh native comparison matches the transfer inputs. Returning restores the board draft.
4. Select recorded 120 µm and a retained numerical failure. Each Open this example action loads its own exact case. Failure remains failure on recomputation and never becomes an accepted force preference.
5. Restore a study with evidence, nondefault volume range and correction values. All are exact. Invalid numeric draft values remain visible and block computation rather than silently becoming defaults.
6. Alter an input while native computation is pending. Late response cannot restore forces or downloads. Repeat after an invalid import and storage failure.
7. Download actual lab files and evidence from the running UI, inspect their contents and verify their recorded hashes. Show the current physical qualification state in the handoff.

Experience First changes the goal from matching colors to preserving the user's investigation. Model the Domain makes a draft, a validated transferable case and computed evidence distinct records.
