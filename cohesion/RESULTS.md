# One connected SolderShape

The running app is at http://127.0.0.1:8769/board. It provides one investigation path: select a real pad, compare declared assumptions, inspect the exact case, retain inputs and numerical evidence, and prepare a physical test. The five destinations use the same navigation, current-page marker, product promise and qualification language.

## What a user gets today

A PCB or assembly engineer can ask how changing solder amount, upper-pad diameter or lower-pad revision changes an isolated joint's predicted shape, force or supported-load gap. The useful output is a reproducible comparison with its source geometry, assumptions, numerical receipts and a concrete measurement plan. It can expose an assumption-sensitive choice or a force-sign tradeoff before ordering a test. Practitioner demand and physical force accuracy remain unqualified. The app cannot approve production pads, simulate a complete assembly or predict yield.

The board remains the guided entry. Joint details owns editable cases, mesh inspection and offset sweeps. Pad comparison owns the distinct two-source, normal-load study. Worked example teaches the conditional tradeoff and retains scope limits and failure. Physical test exposes the existing quote-ready package. A router, new framework, account system and numerical port were unnecessary.

## Repaired continuity

- The same five destinations and brand destination appear everywhere. The launcher opens Board explorer. Existing deep routes remain valid.
- Board drafts open directly in Joint details before computation using trusted extracted source bytes. Demo opens its selected exact case. Either study revision opens its literal source and normal-load inputs. Equivalent-cylinder geometry is excluded from that handoff.
- Each tab retains raw inputs, source text, selections, references and study evidence across navigation/reload. Numerical results, meshes, ZIPs and tokens are not draft data. Restored inputs require fresh computation.
- Linked/file replacements preserve one prior joint draft. If browser quota prevents a backup, the current work survives and the user gets an explicit replacement-without-backup action. Failed imports unlock recovery controls and preserve the saved source.
- Setup stays inert while initial restoration runs. Edits during normal computation remain allowed and reject late responses. Unsupported board pads remain inspect-only. Compute also checks engine readiness.
- Generated files have a visible download link. Editing inputs clears this link and current numerical evidence. This also provides a usable fallback for browsers that do not save a programmatically clicked temporary anchor.
- Physical test offers seven fixed downloads. It distinguishes the 200 µm force experiment, the board's 400 µm hypothesis, and the separate 220 vs 270 µm height coupon.

## Acceptance evidence

| Check | Observed result |
| --- | --- |
| Shared navigation | All five destinations clicked; exactly one current marker on each. All 15 distinct internal linked routes returned HTTP 200. |
| Desktop and 390 px layout | No page-wide horizontal overflow on all five tasks. Navigation scrolls within its own row. Keyboard focus reaches Physical test; skip link focuses main content. |
| Joint draft | 0.0053 mm³ survives navigation and reload. An empty volume survives and returns through Restore previous draft. Forces remain absent until recomputation. |
| Board draft | Changed offset 231 µm and candidate 53 nL survive return. A blank gap survives navigation/reload and blocks computation. Restored drafts do not acquire the default recording. |
| Board-to-joint transfer | Exact 400 µm source pad J16, 231 µm offset, 300 µm gap, 40 nL reference and 53 nL candidate open directly. Previous blank joint draft remains recoverable. |
| Fresh detailed export | Candidate subsequently edited to 52 nL. Actual downloaded comparison contains reference/candidate Fx −180.966732 / −170.267644 µN and Fz −185.364662 / −34.314311 µN. Both numerically checked. |
| Board-bound export | Actual fresh 40/53 nL board archive passes integrity, source-pad binding and native replay. Both X/Z force differences are 0 µN; engine identity matches. |
| Pad study | Custom 186 µm criterion, ±4% sample fraction and 32 µm lower metal survive navigation. Four native cases pass numerical checks. Downloaded study and editable JSON agree. Both literal revisions open with the correct 220/270 µm lower pad and 6.864655 µN supported load. |
| Offset workflow | Portable case reopened through the file picker. Five offsets −0.02, −0.01, 0, 0.01, 0.02 mm compute and export with checked results. Editing during another sweep rejects its eventual response. |
| Invalid input/source | Malformed case leaves the current 220 µm footprint and 0.0051 mm³ input intact. Unsupported source pad X disables Compute, Inspect, case save and evidence export. |
| Recorded controls | All four selectors exercised. The 200 µm offset retains its scope limit. The 60 µm compressed case transfers correctly, recomputes to Failed and displays no force. Selected example survives navigation. |
| Portable files | Joint case, study and standalone footprint imported through actual file choosers. Generated comparison/study/sweep/board archives and editable files downloaded through visible links. |
| Lab resources | All seven UI download targets retrieved; byte counts and SHA-256 values match the existing releases. No physical validation or lab acceptance claimed. |

`navigation.json`, `narrow-navigation.json`, `links.json`, `downloads.json`, screenshots and the `evidence/` archives retain the concrete run. The fresh final app shows the default 40/56 nL comparison at 240 µm offset. Its candidate's predicted positive normal force remains explicitly conditional.

## Verification

From the repository root:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8769
```

If this session's service is already running, open its URL directly. Older running services were preserved; use the 8769 URL for this build.

```sh
python3 -m unittest discover -s tests -v
node cohesion/verify-ui-state.cjs
python3 cohesion/verify_artifacts.py
python3 tools/verify_board.py cohesion/evidence/current-board.zip --replay
```

- Final Python suite: **74/74 passed**, 106.604 s. `test-results-verified.txt` retains output. This includes four new real HTTP checks for the shell, exact pre-compute board case, authorization/source rejection and fixed resource bytes.
- Actual-script Node VM boundary checks: **14/14 passed**. `state-checks.json` records exact script hashes. Mocked DOM/storage/fetch tests cover storage denial/quota, stale transfers, explicit replacement, startup import failure and lock release. These are not browser interaction or physical-validation proof.
- `artifact-checks.json` verifies 11 downloaded generic native cases, the separate two-case board binding, study source/code identities, exact editable inputs and prior-release integrity. The board replay receipt records numerical equivalence only.
- JS syntax and source whitespace checks passed. `integrity.json` confirms unchanged model, solver, study engine, historical recordings, force planning and lab release identities.

## Negative results and remaining limits

The baseline reset a 0.0053 mm³ input to 0.006 after a simple round trip. Review also found startup source loss, a locked Study recovery path and a quota recovery dead end. These are repaired and covered by the fault checks. The first two Python runs retained stale expectations for the old launcher destination and old page title. Those expectations were updated to the intended behavior; both negative logs remain beside the final passing run.

The specialized `tools/verify_study.py` checks the original planning example's fixed heights. It rejects the custom study with 32 µm metal because its reference heights assume 35 µm. That rejection is appropriate for that verifier; the custom archive instead passes input, source, code, manifest and numerical-status checks in `verify_artifacts.py`. No physical claim follows from either check.

Browser session storage is not durable project storage. Users must save editable files before closing a tab. The app currently supplies one attributed board context and supports circular pinned rims; it does not import arbitrary complete boards. The prepared force kit is quote-ready, with lab acceptance, fabrication release and physical validation pending. The historical published-force discrepancy remains unresolved.

## Design choices

Experience First made continuity of the investigation the priority. Model the Domain separated raw drafts, validated cases and computed evidence. Laziness Protocol kept existing routes and numerical formats behind a small shared shell. Prove It Works required actual browser interactions, native computation and inspection of downloaded bytes. Independent candidate judgment and repair review are retained in `judgment.md` and `review.md`.
