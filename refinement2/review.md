# Independent refinement review

Reviewed the working diff against `11379f8`, including the new review tests, `WORKFLOW.md`, `judgment.md`, and the no-comments instructions. This was a source and focused execution audit. No browser interaction, native solver experiment, physical validation or application edit was performed by this reviewer.

Two actionable findings were found. Root accepted both and the current owners repaired them. The focused source and execution recheck below closes both findings. No review findings remain open; root's browser and native integration gates are separate.

## P2: Comparison presentation omits the directional explanation

At the reviewed version, `soldershape/web/ui.js:105` chooses aggregate presentation for every comparison. Lines 106–109 render `review.headline` and `review.facts`, while the selected row contributes only its input snapshot and warnings. Every `row.headline` and `row.facts` entry is discarded for comparisons.

This matters most in generic Joint details. The backend's generic aggregate facts contain numerical deltas, such as `Candidate minus reference restoring force -11 µN.`, while the per-row facts correctly explain a negative-offset sign crossing as reference `8 µN (toward alignment)` and candidate `-3 µN (away from alignment)`. Those explanations never reach the comparison screen. The user still has to decode signed differences to understand the outcome, contrary to this refinement's primary acceptance check. A Board comparison's fixture headline helps its special case but does not repair generic comparisons.

Small repair: present the existing selected-row headline and facts inside the result snapshot, keeping the aggregate above it. The frontend should not recreate force or preference rules.

## P2: Separately saved HTML presents missing adjacent evidence as working links

At the reviewed version, `soldershape/artifacts.py:255`–260 always emits relative links to each case's input and result JSON, the CSV, source footprint and manifest. Both review download handlers save only the HTML. Opening that single file elsewhere leaves no adjacent `case-00`, `results.csv`, `source.kicad_mod` or `manifest.json`; the links fail without any explanation.

Small repair: keep one identical HTML artifact for the API and ZIP, but explicitly state that its relative evidence links work when opened from the extracted accompanying evidence ZIP. Explain that the separately saved HTML retains exact inputs and numerical observations in its own expandable sections. A second renderer or embedded archive is unnecessary.

## Resolution recheck

The UI finding is closed. The current `renderReview` appends the existing selected-row headline and facts to the expandable `result and inputs` section for comparisons. It preserves aggregate facts and does not implement scientific rules in JavaScript. A focused Node VM check ran the actual renderer function with a small mocked DOM and synthetic review record. Selecting reference included `8 µN (toward alignment)` and excluded the candidate observation; selecting candidate included `-3 µN (away from alignment)` and excluded the reference observation. The aggregate `-11 µN` delta remained visible. Rendering no review removed both old observations. This is a renderer behavior check, not a browser or native computation check.

The offline link finding is closed. The current HTML places the standalone-file explanation immediately below its main heading, before the qualification and outcome. Each evidence link group is explicitly labeled as within the extracted accompanying evidence ZIP. Exact canonical values remain embedded in each row's expandable section. The conventions also state the isolated equilibrium and fully wetted pinned circular-rim assumptions. No alternate HTML generation path was added.

The focused HTML escaping/standalone explanation test and renderer-longevity archive test were rerun after the artifact repair and both passed in **0.630 seconds**. `git diff --check 11379f8` passed again after both owners' repairs. No second broad review pass was performed.

## Checks and conclusions

`python3 -m unittest tests.test_review tests.test_review_http tests.test_web_inputs -v` passed **20 tests in 13.688 seconds**. The tests cover negative offset and lateral sign crossing, aligned supported load, zero-offset held gap, failed and unchecked rows, model limits, single/sweep identity, escaping, optional review pairing, manifest integrity, canonical force binding, renderer changes, current historical archives, the Study exclusion, member capacity and API/ZIP equality. API tests reuse saved numerical rows through a patched solver, and the seven-row capacity check repeats one evidenced row. They do not establish seven new solves or physical accuracy.

Independent inspection confirmed:

- `-sign(offset) * X force` correctly changes interpretation for negative offset. Zero offset withholds a lateral restoration conclusion.
- Supported load and held gap have different explanations. A checked supported-load row may expect upward load support, while the Board fixture objective applies only to its nonzero-offset held-gap pair.
- Failed rows retain errors without exporting invented forces or solved gaps. Unchecked and model-limited rows block comparative conclusions.
- New reviews are created only for source-bearing ordinary bundles. Study remains unchanged and retains its own `decision.html` for the equivalent-domain interpretation.
- The reader requires both optional review members, verifies canonical saved rows and existing manifest hashes, and does not regenerate HTML during reading. Current CSS or quantity-format changes therefore do not invalidate an existing archive. Manifest hashing supplies integrity, not an independent signature or physical validation.
- Board HTTP presentation is top-level and leaves the persisted report shape unchanged. Verified historical recordings expose an on-screen review without claiming their unchanged ZIP contains the new brief.
- New UI exports use the exact server-authored HTML. Existing response invalidation clears the shared review owner and export state; unit cues use `valueAsNumber`, leaving empty values unavailable.
- `git diff --check 11379f8` passed.

The real browser, native replay and downloaded-artifact checks in `WORKFLOW.md` remain root's integration gates. In particular, root must verify the selected row's explanation and the offline link instructions in the running artifact.

## Scoped no-comments and simplicity pass

No added suppression, lint bypass, `type: ignore`, TypeScript suppression, constraint comment or workaround comment was found in the diff. The unchanged page-cache comment is outside the changed lines. New function docstrings describe the public operation rather than encoding an unenforced exception. Deletions **0**, restorations **0**, rejected reports **0**, architect reshapes **0**, encoding offers **0**, unenforced comment constraints **0**. This reviewer made no application edits.

The shared backend record plus one DOM renderer is proportionate to the requirement. Keeping Study's existing brief and historical report protocol avoids an unnecessary migration. No further abstraction is warranted by the reviewed change.
