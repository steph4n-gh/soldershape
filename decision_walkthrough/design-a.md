# Candidate A. An inline decision story

## Usage

A visitor opens Board explorer and reads "Would adding solder help this misaligned joint?" above the actual ULX3S board. The adjacent sentence names the choice. "Compare 40 and 56 nL at one actual U1 pad. Seek a restoring sideways force without an upward separating force while a fixture holds the gap."

The page keeps its board, inputs, meshes, review and downloads in their current order. Four short explanations sit beside the relevant material. There is no next button or hidden stage.

1. "Use the U1 / J16 worked example" selects the pad and fills the server's default request. The visitor sees 400 µm source copper, an assumed 400 µm upper pad, 300 µm held gap, +240 µm offset, 40 versus 56 nL, 0.48 N/m, 9 g/cm³ and gravity enabled. The action does not compute automatically.
2. "Compute selected comparison" runs the existing native comparison. Its current readable review explains the force signs. A visible note says "A checked calculation supports this conditional comparison. Physical force accuracy remains unqualified."
3. "Try a 330 µm held gap" changes only the held gap for both volumes and submits the same comparison form. The previous result disappears immediately. The new response determines whether each case pulls down or pushes up. No promise appears before that response.
4. "Prepare a test for this question" reaches Lab with the matching dimension distinction visible. Existing evidence and case downloads stay beside the result.

For a restored draft, the page says "Your saved inputs are restored. The worked example will replace these inputs only when you choose it." It never silently restores the example over that draft. The explicit load action offers "Restore my previous inputs" through a transient snapshot. No automatic file download is needed.

Call sites remain in the existing board script.

```js
load() // retain clone(data.default_request) as the one worked-example input source
loadWorkedExample() // capture previous input snapshot, apply example, invalidate
tryHeldGap(330) // require worked-example inputs, edit held gap, invalidate, requestSubmit
renderResults() // existing review plus renderDecisionContext from accepted current response
```

## Problem

The explorer already has the computation and evidence workflow. Its visitor must infer why the force tradeoff matters and how it relates to the 220 versus 270 µm coupon. These are separate experiments. A new wizard would compete with the current order and need another progress state to track edits. An inline story can explain the existing workflow at the point where each decision is made.

The board supplies only the lower copper geometry. U1 / J16 is actual source copper. The upper pad and process inputs remain hypotheses. This is a rehearsal of a design question on real board geometry, not an assertion about the assembled ULX3S package.

## Shape

Keep all input and result ownership in `board.js`. Add no endpoint, numerical model or general walkthrough module. Use the existing `state.revision`, `invalidate`, `acceptResponse`, `renderResults` and `compute` path.

```js
// Sketch records, not new runtime classes.
WorkedExample = { request } // server default_request, retained before draft restoration
InputSnapshot = { component_uuid, pad_index, search, values, gravity }
DecisionContext = {
  source: "recorded" | "fresh" | "none",
  state: "current" | "draft" | "unsupported" | "failed",
  exampleGeometry: boolean,
  nextAction: string
}
state.workedExample = null
state.previousInputs = null
function captureInputs() { throw new Error("not implemented"); }
function applyInputs(snapshot) { throw new Error("not implemented"); }
function loadWorkedExample() { throw new Error("not implemented"); }
function tryHeldGap(micrometers) { throw new Error("not implemented"); }
function decisionContext(state) { throw new Error("not implemented"); }
function renderDecisionContext(context) { throw new Error("not implemented"); }
```

`InputSnapshot` reuses the existing draft fields and storage representation. Consolidate their capture and application with `saveDraft` and `restoreDraft`; do not create a parallel schema. `previousInputs` exists only for the explicit reversible replacement action and is not another current draft.

`decisionContext` derives lifecycle from existing state. It never stores a second current/stale flag. `exampleGeometry` compares the selected source pad and normalized inputs with the retained server example. Held gap may be 300 or 330 µm. The 330 µm shortcut stays disabled outside those example inputs and while the engine is running. Other comparisons retain manual editing and computation.

The rendered conclusion remains the existing server `review` and `report.screen`. Do not reimplement force-sign rules or write a second headline based on recorded values. The story provides context, qualification and a next action. Result numbers and conditional conclusions come only from the accepted response.

Keep `board.html` responsible for the explanatory copy and anchors, `board.css` for its layout and `board.js` for context rendering. Existing `board.py` already identifies the request, source pad and scope. It needs no new logic. The interface hides draft replacement and invalidation behind two user actions, without exposing a second computation API.

## Invariants

- An accepted response must still match revision, source board and selected pad. Input edits clear its force story and downloads through `invalidate`.
- Failed, incomplete or out-of-scope results show their existing failure review. They never receive an affirmative design recommendation.
- A verified recording says "Recorded native result" beside its review. Only a fresh response says "Fresh native computation".
- The 330 µm action passes through the ordinary form validation and native request. It cannot supply precomputed forces.
- Loading the example is explicit and reversible. Reloading a restored draft never replaces it with the example.
- Numerical agreement and physical force accuracy have separate labels. No whole-board, clearance, bridging or yield conclusion appears.

## Exact contextual copy

At selection, use "Start with one source pad. Every other pad remains unsolved. The copper diameter comes from the board. The wettable boundary still needs measurement."

At inputs, use "What might change the answer? Liquid volume, actual wettable rims, upper pad, held gap, offset and material values. Try a 330 µm held gap, then compute again. This experiment changes one assumption; it does not bound manufacturing uncertainty."

Below the existing result review, use "What can you trust here? These forces and meshes belong to the shown inputs and source pad. Refinement checks and replay test numerical consistency. The force values still need a physical test."

At the Lab handoff, use "What must the lab measure? Hot wettable boundaries, solder volume, upper pad, gap, offset and material conditions. Then measure hot force versus displacement. The existing 200 µm fixture needs adaptation before it tests this 400 µm board joint."

Below that, link "Why 220 versus 270 µm?" to `/lab/prelab.html` and explain "That separate twenty-joint coupon asks which lower pad diameter preserves component clearance. Its ranking depends on wetting and solder quantity. It does not validate this board's forces."

## Synthesis decision

Candidate only. Parent owns comparison and final synthesis.

## Tradeoffs accepted

- We accept a longer scrolling page in exchange for board, assumptions and conclusions remaining visible together.
- We accept one deliberate 330 µm held-gap trial in exchange for a reproducible one-variable experiment without adding sweeps, history or uncertainty infrastructure.
- We accept a hypothetical held-gap fixture objective in exchange for an honest useful question on actual source geometry. It cannot select a production assembly process yet.

## Alternatives considered

A step navigator would hide page sections behind progress and require rules for backwards edits, restored drafts and failed calculations. It hides visual density but exposes extra workflow state. The inline design uses the explorer's existing computation lifecycle.

A second hardcoded result summary would make the example easy to narrate but create independent force-sign policy. Existing review owns that interpretation and remains the only conclusion source.

## Open questions and risks

Will visitors mistake the held-gap objective for a free package's behavior? Put the fixture requirement in the question, input block and result qualification.

Can the visitor see why a changed gap matters? Root's actual native UI check found the candidate vertical force changes sign between 300 and 330 µm. The shipped conclusion must still come from each accepted live response. The trial label states its input change rather than promising a reversal.

## Verification and next implementation step

Drive the real board page with a saved nondefault draft, load the example, restore previous inputs, load again and compute. Verify the two default forces against the actual response. Run the 330 µm trial and verify its inputs and review from the new response. Edit offset during computation, select an unsupported pad and simulate an unavailable engine. Each must clear or block the conclusion. Follow Lab and coupon links, inspect all three dimension labels, and download/replay the board evidence. Repeat the narrative and actions at a narrow viewport.

Begin by consolidating input snapshot capture/application inside `board.js`, then place the inline copy around the existing sections.

Model the Domain keeps one result lifecycle. Laziness Protocol reuses the existing review and native comparison. Prove It Works requires real browser and native evidence before the narration earns its wording.
