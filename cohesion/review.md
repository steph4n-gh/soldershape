# UI cohesion engineering review

Reviewed the working diff for the common shell, page drafts, direct case handoffs, resource routes and HTTP tests. This was a read-only application review. Root owns browser verification. No application file was changed by this reviewer.

## Findings

1. **P1. Initial edits can interrupt restoration and replace a saved source with an empty draft.** In the reviewed version, Joint details and Pad comparison leave numeric fields editable while bootstrap and saved-footprint imports are pending. Their single revision check rejects the whole restoration after any input event, including a harmless volume edit. The initial bootstrap then saves current state, whose footprint source is still empty. Running the actual `restoreDraft` functions with a delayed API reply returned `false` and left Joint source text empty, and Study source texts as `["", ""]`, while preserving the newly edited scalar. Joint's early revision-change branches also explicitly enabled draft saving. The smallest repair is to keep the setup surface inert until initial restoration settles, unlock it in `finally`, and enable draft writes only after a complete source state is installed. Root and the owning implementer are repairing this. Verify the final source and browser behavior before closing it.

2. **P2. Failed Study restoration leaves every recovery action disabled.** The reviewed bootstrap sets `state.phase = "loading"` before importing saved sources. If that request rejects, its outer catch reports failure but never returns phase to idle. Load planning example and Open study remain disabled despite a valid bootstrap token. Root added a final phase reset while this review was running. Confirm the final bootstrap always unlocks its setup surface and allows a saved-file or example recovery after a failed restore. A failed draft import should not relabel a healthy bootstrap as an unavailable local service.

3. **P2. A full browser store can make replacement impossible even after following the recovery instruction.** `keepPreviousDraft()` requires a second complete copy of the current Joint draft. If the browser quota is full, it returns false and blocks both a linked replacement and Open case. The notice says to save the current editable case before replacing it, but portable saving changes no browser keys, so the next attempt fails identically. I reproduced this using actual `ui.js` and `keepPreviousDraft()` under a 5 MiB storage mock with a 2.0 MB Joint draft and a 1.5 MB Study draft. The existing draft survives, but both first and second replacement attempts return false. Provide an explicit replacement-without-browser-backup recovery after the failed preservation attempt, with a clear durable-save instruction, or avoid requiring a duplicate full draft. Do not silently discard the existing draft.

## Checks that passed

- `python3 -m unittest tests.test_workspace_http -v` passed all four tests. The new Board case route returns the exact normalized selected-pad case without acquiring the native computation lock. It rejects a forged source hash and missing token. All fixed lab resources return the current local file bytes and expected MIME types.
- `git diff --check -- soldershape tests` passed at review time.
- An actual `ui.js` Node VM run delayed `/api/case`, then changed the current-input predicate before completing it. `openCase()` rejected with “Inputs changed while opening. Open the current case again.” It neither navigated nor stored a transfer.
- Quota failure leaves the existing stored draft intact. The unresolved issue is recovery, not overwrite during the failed write.
- Board drafts bind to board and extractor identities and restore raw input strings. Restored drafts suppress the initial recorded-force preview. Current numerical evidence is invalidated on edits.
- Study handoff uses the selected literal source pad and shared normal-load inputs. It explicitly excludes the equivalent-cylinder hypothesis. This avoids presenting effective geometry as the physical pad.
- The Physical test page distinguishes the 200 µm force experiment from the 400 µm board hypothesis and the separate 220 versus 270 µm gap experiment. It retains the failed initial uncertainty budget and pending physical qualification.

## Comment Sicko and deslop

There is one added code comment, in `ui.js` immediately before the `pageshow` handler. Keep it. It explains the non-obvious browser back/forward-cache behavior that motivates a reload. The code alone only shows the reload, not why it is necessary to avoid reviving old numerical evidence. There are no new suppressions, phase-narrating comments or constraint comments requiring an encoding offer. Suggested comment deletions = 0. Restored comments = 0. Review reruns = 0. No architecture change or application edit was made by this review.

The diff uses a small namespace, existing page scripts and fixed routes. A router, general file server or new persistence dependency is unnecessary. The relevant remaining work is the three concrete recovery cases above and root's actual browser exercise of the final artifact.

## Repair verification

The final read found initial setup locks, `finally` unlocks, draft-write readiness after successful source restoration, and removal of the unsafe early save branches. The quota repair preserves the prior draft and exposes an explicit Replace without browser backup action. That action rechecks the case, rejects a late edit or superseded offer, consumes an incoming handoff only after acceptance, and leaves the offer available if case checking fails.

`node cohesion/verify-ui-state.cjs` passed 14 of 14 boundary checks. The script executes the actual complete `ui.js`, `app.js` and `study.js` sources with a mocked DOM, fetch and browser storage. Its reproducible failure injections cover a full store, inaccessible storage, delayed case checks, delayed source imports, rejected imports and rejected bootstrap. The results and checked source hashes are in `cohesion/state-checks.json`. These checks verify runtime control flow and recovery state. They do not establish native browser inert behavior, rendering, downloaded-file delivery, native numerical correctness or physical accuracy. Root's separate browser audit remains necessary. No unresolved source-loss or quota-recovery finding remains in this read.
