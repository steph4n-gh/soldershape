# Independent cohesion judgment

Both candidates solve the actual problem through shared navigation, preserved input drafts and exact case handoff. Neither needs a router, a combined mega-form or changes to numerical schemas. I read both complete designs, both HTML prototypes, and the relevant board-case, HTTP, workbench bootstrap, study-apply and board-compute source.

| Criterion, 0 to 4 | A | B |
| --- | ---: | ---: |
| Flow continuity | 4 | 3 |
| Scientific and data fidelity | 4 | 4 |
| Simplicity | 3 | 4 |
| Accessible verification | 3 | 3 |
| Total | 14 | 14 |

Choose B as the presentation base. Its board-led hierarchy gives the existing impressive board view a concrete purpose and a clear next action. Preserve `/` as the workbench and make the brand and launcher lead to `/board`. Changing the root route adds compatibility work without helping the user. Use the existing board palette and shared task navigation, rather than introducing a separate overview.

Graft four material pieces from A.

1. Inspect a valid board draft before computing it. The existing `board_case()` already validates trusted board identity, selected supported pad, exact extracted footprint, held-gap parameters and baseline. Add a small `/api/board/case` operation returning its normalized case and selection. This reuses the existing boundary and avoids an expensive prerequisite solve or trusting a client-invented lower diameter. An editable handoff must be available even after a numerical failure. Keep computed evidence separately gated on the current response.
2. Keep one recoverable prior workbench draft when a direct case handoff replaces it. A one-use transfer alone otherwise introduces a new form of lost work. Do not make a general history system.
3. Bind restored board drafts to source and extractor identities. Restore raw input strings, including invalid values, and clear results. Never let the initial recorded preview replace a restored draft.
4. Provide a small explicit Physical test destination, reachable through the same five-item navigation everywhere. This is easier to find and verify than varying footer resources. Serve only fixed existing release files. State the actual fixture geometry and open qualification gates beside its downloads.

## Concrete integration contract

- One IIFE namespace owns chrome, bounded per-page session storage and case transfer. Page scripts continue to own their forms, raw draft capture and domain logic. Do not merge scripts with colliding top-level `$` and `state` declarations.
- Canonical task order is Board explorer, Joint details, Pad comparison, Worked example, Physical test. Keep existing URLs. Exactly one current-page marker and one product promise appear on every page. Use a skip link and visible keyboard focus.
- The promise is a reproducible comparison of one joint under declared assumptions, with numerical evidence and a path to a physical test. Do not imply validated forces, production pad approval, full-board simulation or yield prediction.
- Handoffs use the existing `soldershape.case.v1`, normalized through server validation and applied through the existing file-open path. Board selection metadata is context only and cannot confer board-bound evidence after editing. Demo uses the selected sample's existing editable case.
- Study drafts retain the entire two-source scientific contract. A literal-rim revision may open in Joint details with its exact source and normal-load inputs. Do not transfer an equivalent-cylinder hypothesis as a physical mesh or manufacture a second pad source from a board volume comparison.
- Save raw inputs only. No session token, numerical result, mesh or archive is persisted. Restore requires fresh computation, regardless of navigation or reload. Storage failure must be visible and leave portable save available.
- Fix the existing board Compute enablement to check engine readiness. The current code checks token, support, pending work and form validity but not the engine state.
- Keep archive bytes and solver source unchanged. Editing `__main__.py` changes a source-bound calculation identity, so final verification requires a freshly started service rather than an already loaded server.

## Decisive acceptance

Drive the real browser through board draft to Joint details, calculate and download; return to the board with exact inputs retained. Repeat worked-example handoff and an unchanged invalid input across navigation/reload. Confirm edits remove evidence exports, unsupported selection remains blocked, current markers and all five destinations work at desktop and narrow width, and lab downloads match the existing release hashes. Keyboard reachability and visible focus must be checked on the finished UI; neither static prototype establishes accessibility.
