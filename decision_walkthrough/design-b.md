# Candidate B. A compact decision navigator

## Problem

The board already computes a traceable comparison, but readers must connect its inputs, force directions, limits, and lab work themselves. A four-step navigator can make that decision visible while retaining the board and its current computation. The board is real. The assembly conditions are hypotheses. The 220 versus 270 µm coupon is a separate loaded-height experiment.

This sketch follows `grounding.md`, `board.html`, `board.js`, `board.py`, `docs/getting-started.md`, and `prelab/REPORT.md`. It changes no production files or physical computation.

## Usage

At the top of Board explorer, the reader sees "A real board. One decision to test." The question is "At this held gap and offset, does more liquid solder improve restoration without pushing the upper pad away?" The objective belongs to the held fixture. A freely floating package needs a different objective because upward force can support its weight.

Four ordinary buttons select `1. Choose the question`, `2. Read the evidence`, `3. Change an assumption`, and `4. Plan the measurement`. A single compact panel changes below the buttons. The existing board, editable fields, review, and meshes stay on the page. Each panel has a link that scrolls to its existing workspace section. No field or result is hidden by a step.

On a first visit without a restored draft, step one names the default U1, pad J16, SDRAM_D0, and source copper diameter. All values come from the current selection and request. The existing initial recording may load with its present "Verified native recording" label.

For a restored draft, the navigator says "Your saved inputs are restored. Continue with this comparison, or load the worked example." It never resets the draft during load. The explicit button says "Load U1 / J16 worked example". Adjacent copy says "Replaces the current inputs in this tab. You can return to them during this visit." The button captures one input-only snapshot, then applies `data.default_request`. A "Return to previous inputs" button restores the snapshot and clears every current result. It does not restore stale meshes or downloads.

The three principal call sites are these.

```js
// Loading chooses only the explanation, never different physical inputs.
renderWalkthrough("question");
// The explicit example button captures the current draft, then applies the server default.
loadWorkedExample();
// The experiment button edits the existing gap field and submits its existing form.
runGapExperiment();
```

Step two asks "Which choice meets this fixture objective?" It displays the existing shared review headline and accepted `report.screen` outcome. It derives volumes, force directions, and differences from that same accepted response. It never embeds the recorded force numbers in copy. The baseline recording should explain that 40 nL restores laterally with downward Z force while 56 nL restores laterally with upward Z force. Those words must change when the response changes.

Step three says "Test one assumption before trusting the choice." For the exact worked example, "Try a 330 µm held gap and compute" changes only gap from 300 to 330 µm, invalidates the current result, and uses `comparison-form.requestSubmit()`. The two volumes remain 40 and 56 nL. It makes no claim about the new force directions until a fresh native result returns. The panel then displays the shared review for the new gap and says "This is one sampled comparison. It is not a manufacturing tolerance or uncertainty bound." The fields remain available for volume and offset experiments. The parent has verified this experiment through the actual browser and retained `evidence/gap-330-probe.zip`.

For custom inputs, step three instead says "Edit one assumption below, then compute again." Do not silently impose 330 µm on another pad or request. Its action focuses the held-gap input. Returning to the worked example requires the explicit example button.

Step four says "Keep the question, measure the missing boundaries." Its actions reuse Save review HTML, Download board-bound evidence, Save editable case, and the existing Lab link. Next to that link, say "The current 200 µm force fixture needs a matching 400 µm specimen design before it can test this worked example." Link the coupon findings separately under "Another decision. 220 versus 270 µm clearance coupon." State "Its height results do not qualify this board's forces."

## Shape

Keep one small navigator object inside the existing `board.js` state. Model the Domain makes the selected explanation explicit without adding another computation lifecycle.

```js
// Sketch notation. The existing BoardRequest and draft storage formats remain private.
Walkthrough = {
	step: "question" | "evidence" | "assumption" | "measurement",
	previousInputs: null | InputSnapshot
};
InputSnapshot = {component_uuid, pad_index, search, values, gravity};
function renderWalkthrough(step = state.walkthrough.step) { throw Error("not implemented"); }
function applyBoardInputs(request) { throw Error("not implemented"); }
function loadWorkedExample() { throw Error("not implemented"); }
function restorePreviousInputs() { throw Error("not implemented"); }
function runGapExperiment() { throw Error("not implemented"); }
```

`renderWalkthrough` owns the four buttons, `aria-current="step"`, a visible "Step N of 4" label, panel text, and focusable links. Selecting a step changes no physical input and sends no request. Keep the selected panel in ordinary document flow. Avoid tab roles that would require a separate keyboard model.

`applyBoardInputs` reuses the existing form mappings, selection rendering, `readDraft()`, `invalidate()`, and `saveDraft()`. Its input is the existing normalized board request from `/api/board`, not a second constant dictionary. `previousInputs` is one snapshot for an explicit return action. Repeated example loading keeps the original snapshot instead of replacing it with another example. Restoring consumes that snapshot. The current draft remains the only persisted draft.

`runGapExperiment` is available only when the current canonical request exactly matches the worked example. It writes `held-gap` as 330, calls the existing read and invalidation path once, then submits the existing form. No new endpoint, solver mode, archive schema, or scenario recording is necessary.

`renderResults()` calls `renderWalkthrough()` after every accepted response or invalidation. The navigator reads the existing response and never stores a second result. Minimize Reader Load keeps current assumptions and evidence in one place. Laziness Protocol reuses `screen_pair()` and the shared review instead of building a browser-side decision engine.

## Invariants and blocked states

- The live review owns numerical conclusions. Navigator copy cannot name a preferred volume before a current accepted response exists.
- Any input edit clears all result-dependent navigator copy with the existing results and exports. `revision` continues to reject late responses. Editing during a run shows "Inputs changed. Compute again for the current question."
- An unsupported selection shows "Inspect-only pad. Choose a supported circular front pad to compute." Evidence and measurement steps remain readable. All native experiment actions remain disabled.
- An unavailable engine retains the clearly labeled recording if it matches the default request. It disables the experiment and explains how to obtain a fresh computation.
- Native failure or model warnings show the existing blocked screen and warnings. The navigator offers no winner and no successful completion marker.
- Native refinement and replay establish numerical consistency for the stated model. They never establish physical force accuracy, package movement, bridging, or yield.

## Exact trust and lab copy

"What we can check now. The selected lower copper comes from the identified KiCad board. The current forces and meshes belong to these exact inputs. Native refinement checks and replay test numerical consistency."

"What can change the answer. Liquid volume, hot gap and offset, opposing pad, wettable contact lines, alloy, temperature, and surface tension. This page can compare declared inputs. It has not established a physical error bound or a production recommendation."

"What the lab must establish. Measure the finished copper and mask openings, both hot contact lines, upper pad, liquid volume, hot gap and offset, and material properties at temperature. Measure reaction forces at several controlled displacements. A cold section needs a measured hot-to-cold relation."

## Tradeoffs and alternatives

We accept one small explanation state and an input snapshot in exchange for a guided path that returns users to their own work. Explanations do not gate ordinary board exploration. The navigator adds no mandatory wizard or completion persistence.

An inline narrative would expose everything at once with less state. It loses here because the reader must keep the current question and next action in mind while crossing a long page. A separate wizard would hide more visual complexity, but would duplicate selection and result ownership and separate the decision from the actual board. A scenario library would need new receipts and source maintenance without proving more than the current editable computation.

## Acceptance verification

Drive the actual browser from a clean tab. Identify U1 / J16 and 400 µm source copper. Read the recording label and objective. Compute the exact default. Assert the navigator agrees with the shared review and that both original numerical outputs remain unchanged.

Run the 330 µm experiment. Verify the posted request changes only held gap. Wait for native acceptance. Assert every displayed force and conclusion comes from that response, with no numerical claim about the change before acceptance. Save review and ZIP, then replay the ZIP with `tools/verify_board.py --replay`.

Restore a custom draft, reload, and confirm the navigator leaves every field untouched. Explicitly load the example and return to the prior inputs. Verify both transitions clear results and downloads. During a pending run, change the offset and confirm a late result cannot repopulate the navigator.

Use an inspect-only pad, native failure, warning result, and unavailable engine. Verify each state names the blockage, never shows a winner, and preserves the measurement guidance. Check all four step buttons by keyboard and mobile layout. Check the Lab and separate coupon links.

## Synthesis decision and next step

Candidate B is independent and awaits the parent comparison. First implement only the navigator markup and its rendering against existing state. Then add the explicit example transition and native gap experiment. A new uncertainty scenario is unnecessary until this complete workflow passes its browser and replay checks.
