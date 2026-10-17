# Board explorer decision walkthrough grounding

## Overview

The board explorer can already answer a bounded engineering question with traceable computation. On an actual ULX3S copper pad, does increasing liquid solder from 40 to 56 nL improve lateral restoration while avoiding upward separation at a held gap? The board supplies the lower copper shape. The assembly conditions are hypothetical inputs. No current result selects a production solder volume.

The smallest useful change is a guided explanation inside the existing board page. It can connect the source selection, objective, current comparison, sensitivity experiments, and lab handoff. The explorer already has native computation, editable cases, readable reviews, and reproducible ZIP exports. A new solver or navigation flow is unnecessary.

## Key concepts

- `soldershape.board-request.v1` identifies one board hash, component reference, and pad index. Its `parameters` describe the candidate. Its `baseline` contains reference upper diameter and volume.
- `board_case()` derives the lower pad from the trusted extracted footprint. The browser cannot override the lower diameter. Board comparison uses a held wetted-plane gap. It rejects supported-load requests.
- `soldershape.board-report.v1` contains the normalized request, exact source selection, both results, the numerical comparison, and the conditional fixture screen. Its physical qualification remains `unqualified`.
- Browser state has one draft and one accepted response. A revision counter separates an edited draft from a pending computation. Every input or source selection edit clears results and export URLs.
- The declared objective requires a force toward alignment and no upward separating force. A free package may require upward force to support its weight. The held-gap screen is therefore an explicit test objective rather than a universal solder-quality rule.

## How it works

`GET /api/board` calls `read_board()` and `default_request()`. The trusted context binds the original board, extracted footprints, SVG, extraction code, and native KiCad readback by hashes. The context has 235 components, 1,177 pads, 5,365 track objects, and 381 supported pads. Support means a front circular pad can supply the current boundary hypothesis. Other pads remain inspect-only.

The default selects U1, the `LFE5U-85F-6BG381C`, pad J16, net SDRAM_D0. J16 is index 173. Its actual lower copper diameter is 400 µm. Its board position is 142.88, 86.6 mm. Its local position is 4.4, -1.2 mm. The source commit is `6a92cec6b177191c5b0f80e260013a1f8ec147dd` in EMARD's ULX3S repository. The declared 50 µm pad mask margin does not identify the finished hot wettable rim.

The process hypothesis supplies a 400 µm upper pad, 300 µm held gap, +240 µm local X offset, surface tension 0.48 N/m, density 9 g/cm³, and gravity along model negative Z. The reference has 40 nL liquid volume. The candidate has 56 nL. Both upper diameters remain equal in the current UI.

The initial recording contains two checked native calculations for those exact inputs. The 40 nL result has X force -184.526381 µN and Z force -181.283879 µN. The 56 nL result has X force -164.385473 µN and Z force +13.385898 µN. Increasing volume by 40 percent reduces restoring force by 20.140908 µN and changes the vertical force from downward to upward. Both meshes pass the existing numerical and model-scope checks. This supports a conditional hypothesis to test. It does not establish force accuracy in the physical ULX3S assembly.

`POST /api/board/compare` calls `run_board()`, which captures calculation source identities, normalizes the source selection, and calls `calculate_comparison()`. That function solves the reference and candidate. `_report()` binds their exact canonical inputs back to the selected board. `screen_pair()` returns the conditional outcome. `response_payload()` also generates a shared readable review through `review_record()`.

`bundle_board()` exports the source board, footprint, selection, both native results, meshes, review, and calculation source. `verify_board()` regenerates the selection and conclusions. Optional native replay compares forces and requires matching engine identities. Historical recording source is preserved. Changing current code does not justify rewriting the old recording.

In the browser, `load()` restores a matching tab draft if one exists. Otherwise it accepts the verified initial recording. `compute()` records the current revision. `acceptResponse()` rejects a stale revision or mismatched selected source pad. `invalidate()` clears current conclusions and downloads. `exportCase()` can open the selected hypothesis in Joint details without computing it first.

The smallest integration choices are these.

1. Extend `board.html` with a short named decision, explicit trust levels, and links to sensitivity inputs and lab needs. Reuse the existing result and export state. This explains the question but alone does not demonstrate how a changed assumption alters the answer.
2. Add a small table of named scenarios derived from verified native receipts. Selecting a scenario applies its exact inputs and either clears the prior response or accepts a matching verified recording. Render conclusions from the same `screen_pair()` and `review_record()` functions. Label untested variation as an experiment to run. This demonstrates a change in the answer with bounded added code.
3. Reuse the existing editable fields for a guided native sensitivity run. Any changed input must clear old results. A returned result must remain tied to the current scenario and revision. This adds no new domain layer, but requires live computation for the changed example.

Options 2 and 3 can share a small scenario list. Avoid a generic workflow engine or separate app. Keep scenario display labels outside the canonical physical input dictionaries. If scenario receipts are added, bind the scenario request and source identity rather than displaying hard-coded force values.

## Where things live

- `soldershape/board.py` owns trusted board extraction, default inputs, source selection, report construction, recording integrity, export, and replay.
- `soldershape/web/board.html` owns the board view, process inputs, result review, paired meshes, and lab handoff.
- `soldershape/web/board.js` owns draft persistence, source selection, invalidation, request revisions, native compute, exports, and linked mesh cameras.
- `soldershape/__main__.py` serves the board routes. It owns the computation lock and `calculate_comparison()`.
- `soldershape/artifacts.py` owns `screen_pair()`, `review_record()`, readable HTML, shared archive contents, and review verification. `demo.py` imports the same screen function.
- `board_demo/context.json`, `manifest.json`, `native-verification.json`, and `source/` preserve the trusted extraction. `recording.json` binds `data/default-comparison.zip`.
- `tests/test_board.py` checks the actual selection, source binding, exact default forces, unsupported pads, request identity, native failures, and resealed archive tampering. `tests/test_review.py` checks force meanings, sign changes, zero offset, loaded comparisons, and shared readable evidence. `tests/test_web_inputs.py` checks browser ranges against canonical inputs. `tests/test_workspace_http.py` checks handoff routes.
- `prelab/REPORT.md` and `prelab/LAB_ADDENDUM.md` explain the separate 220 versus 270 µm height coupon and its unresolved measurements.

## Gotchas

The 220 and 270 µm coupon diameters do not belong to the selected ULX3S pad. The coupon has 280 µm upper pads, twenty joints, an assumed cap mass, and a loaded gap question. Its 185 µm target and calculated ranking cannot appear as qualification for the board's 400 µm isolated joint. The existing 200 µm force fixture also does not validate the 400 µm board example.

The coupon can still teach why independent wetting and volume data matter. Its nominal C220 advantage is 15.797 µm for top-rim pinning and 10.890 µm for the full-sidewall hypothesis. Opposite requested geometry endpoints reduce those differences to 2.816 and 0.843 µm. A broader, unqualified volume stress reverses the ranking. Keep that evidence in a clearly separate coupon explanation or a labeled linked example.

The board explorer has not yet established an uncertainty bound for the 40 versus 56 nL comparison. Candidate changes to gap, offset, volume, and wettable diameter need actual native receipts before the UI claims they change the answer. A coupon sensitivity result is not evidence for those board force changes.

What can be trusted now is source pad identity, canonical input conversion, native numerical checks, current-result invalidation, and archive replay under the stated pinned circular-rim model. Neither a refinement status nor a small replay difference supplies a physical error bound. Nearby joints and copper traces remain unsolved context. The model does not simulate whole-package movement, neighboring contact, bridging, thermal reflow, or yield.

The board-specific lab handoff should request the finished copper and mask geometry, both hot contact lines, actual upper pad, independently measured liquid volume, hot held gap and offset, material properties at temperature, and reaction forces at several displacements. A height coupon result cannot qualify lateral forces. Cold sections do not establish molten boundaries without a measured hot-to-cold relation.

This grounding is based on current source and retained evidence inspection. It ran no native jobs and made no product edits.
