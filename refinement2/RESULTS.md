# Result interpretation and portable review

This pass improves the existing Board-to-Joint investigation. An engineer can inspect a real pad, understand the conditional comparison, and hand a colleague the assumptions and numerical observations in a readable file. The product remains an equilibrium investigation and physical-test planning workbench. Practitioner demand, a defensible commercial moat and physical force accuracy remain unqualified.

## Delivered behavior

The result explanation appears before geometry. It distinguishes a held gap from a supported normal load, explains the force direction for the selected offset, and withholds a preference for failed, unchecked or model-limited rows. A comparison keeps its aggregate facts and an expandable selected result with its own observations and inputs. Selecting another row changes that snapshot. No production optimum is claimed.

Joint fields display live µm and nL equivalents alongside mm and mm³. The actual Board handoff retained 400 µm diameters, 300 µm gap, 240 µm offset and 40/56 nL reference/candidate volumes. Empty fields display `Unavailable`; zero offset displays `0 µm`. Board's numeric limits now match the canonical model boundary and explain the first invalid field. Invalid raw drafts stay available for correction.

One backend review record supplies the screen and the script-free standalone HTML. New ordinary source-bearing evidence ZIPs hash `review.json` and `review.html` alongside the inputs, meshes and native receipts. The separately downloaded HTML is byte-identical to the ZIP member. It includes exact values and isolated-equilibrium, pinned circular rim assumptions. Evidence links are explicitly labeled as files in the extracted accompanying ZIP. Study retains its existing decision brief and equivalent-domain semantics. Historical archives remain unchanged.

The application keeps its existing input drafts, handoff, recovery, export and invalidation paths. There is no new framework, solver, dependency, persistence schema or simulation capability. `screen_pair` moved unchanged into the existing artifact module so both the Board report and readable review share the declared fixture objective.

## Acceptance evidence

| Check defined before implementation | Observed result |
| --- | --- |
| Clear Board comparison under its declared fixture objective | Fresh 40/56 nL comparison reports that less solder meets the objective and more solder pushes upward. Reference X/Z forces are −184.526/−181.284 µN. Candidate X/Z forces are −164.385/+13.386 µN. These are computed observations under hypothetical process inputs. |
| Same case recognizable in Joint details | Actual Inspect this joint handoff preserves canonical dimensions, reference, source context and all µm/nL equivalents. It transfers inputs and requires fresh computation. |
| Supported-load semantics | Fresh 4 µN, 6/5 nL comparison predicts 141.986/125.400 µm gaps. The candidate gap is 16.5857 µm smaller. Both rows explain that upward solder force balances the declared downward load within numerical tolerance. No held-gap fixture rule is applied. |
| Negative, zero and positive offset | A fresh five-point sweep at 200 µm pads, 300 µm held gap and 5 nL covers −20, −10, 0, +10, +20 µm. Endpoints report X forces +5.74541/−5.74541 µN and positive restoring force toward alignment. The selected zero row withholds a lateral restoration comparison. All five rows pass numerical checks. |
| Retain numerical failure | Fresh 200 µm pads, 60 µm held gap, 40 µm offset and 7 nL returns `failed`. The review retains the engine error and supplies no force or solved gap. The failed archive remains readable. |
| Invalid values do not become computations | Board retains a saved 1 µm diameter, marks it invalid, explains the 50 µm minimum and disables Compute/Inspect. Joint blank volume displays `Unavailable`, marks the field invalid and browser validation blocks submission with `Please fill out this field.` Joint retains its existing form-validation interaction. |
| Edits invalidate claims and exports | Editing a computed Joint case clears the review, disables result/review exports and removes the generated link. Editing during computation produces an explicit obsolete-response discard after completion. |
| Selected facts and keyboard access | Enter opens the selected result. Selecting Candidate changes the supported-load snapshot from 6 nL/141.986 µm to 5 nL/125.400 µm. A focused renderer check also covers a synthetic force-direction crossing and null-review clearing. |
| Narrow layout | At a temporary 390 × 844 viewport the Board page reports 375 px document width, a 301 px review area and a 301 px export button. Expanded content remains within the page. The viewport override was reset to the original 1280 px width. |
| Actual downloadable evidence | Five UI downloads contain 12 saved rows, including one failure. All manifests, canonical review bindings and relative evidence targets pass [artifact checks](artifact-checks.json). Direct Board and Joint HTML downloads match their ZIP members exactly. No external assets or executable elements occur in these briefs. |
| Native numerical replay | [Joint replay](replay-joint.json), [Board replay](replay-board.json) and [loaded replay](replay-loaded.json) each pass both rows with zero force difference. Loaded replay also has zero gap difference. Engine source and binary identities match. This is local numerical agreement, not physical validation. |
| Historical and scientific stability | Model, solver, Study, three historical native archives, force-lab ZIP/PDF and refined coupon ZIP retain their exact prior bytes. Their identities are in artifact-checks.json. |

The fresh full suite passes **94 tests** in [tests-full.txt](tests-full.txt). The existing mocked browser/storage boundary runner passes **14 checks** in [state-checks.json](state-checks.json). Those 14 checks do not replace real browser use or establish numeric field validity. New tests cover meaning, failure suppression, scope, escaping, optional member pairing, manifest tampering, canonical force tampering, source-bound API/ZIP agreement, renderer longevity, historical compatibility and the Study exclusion. Seven fully evidenced loaded rows fit in 98 archive members under the unchanged 100-member limit. That capacity test repeats one evidenced row; it does not claim seven independent native solves.

[Independent review](review.md) found two P2 issues and verified both repairs. Comparisons initially omitted selected-row directional observations. Separately saved HTML initially lacked an explanation of its relative evidence links. Both findings remain recorded with resolution evidence. The reviewer used the inherited model, so this is an independent execution/context review, not a cross-model consensus claim.

## Reproduce

From the repository root, use the existing pinned engine.

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8769
```

Open `http://127.0.0.1:8769/board`, compute the default selected comparison, expand the selected result, and download the review and evidence. Inspect the same joint in Joint details. Use Open case with `examples/loaded-volume.soldershape.json` and compare to reproduce the supported-load example.

```sh
python3 -m unittest discover -s tests -v
node cohesion/verify-ui-state.cjs refinement2/state-checks.json
python3 refinement2/verify_artifacts.py
python3 -m soldershape replay refinement2/evidence/joint-comparison.zip
python3 -m soldershape replay refinement2/evidence/loaded-comparison.zip
python3 tools/verify_board.py refinement2/evidence/board-comparison.zip --replay
```

The artifact checker verifies the committed UI downloads and byte preservation against `11379f8`. It does not run new simulations. Replay regenerates trusted requests and does not execute archived scripts or HTML.

## Preserved negatives and limits

The browser's file-URL policy blocked opening the standalone HTML directly. No workaround was attempted. The brief received structural, escaping, canonical-value, resource and actual-download equality checks, but this pass does not claim an offline visual-rendering check. [Board screenshot](board-review.png), [narrow screenshot](board-narrow.png) and [loaded screenshot](loaded-review.png) show the actual application.

The first input-boundary test and the initial 1 µm browser/server disagreement are preserved in [test-input-baseline.txt](test-input-baseline.txt). An initial mocked boundary run failed because the test DOM did not expose the standard `validity` property. Adding that property to the mock restored its 14 checks without relaxing assertions; the original failure remains in [state-checks-initial-failure.json](state-checks-initial-failure.json). The first full test run overlapped a review-renderer source edit and correctly tripped the loaded-source identity guard in the Board HTTP test. Its [failure log](tests-source-edit-failure.txt) remains. Restarting the test process after source settled produced the passing full-suite record. Neither incident was hidden or repaired by weakening source verification.

The staged whitespace check reported one trailing space in the raw first-failure log, emitted by unittest before its failure detail. That diagnostic remains byte-preserved. `git diff --check 11379f8 HEAD -- . ':(exclude)refinement2/test-input-baseline.txt'` passes for the remaining change. No source formatting or lint exception was added.

Manifest hashes establish internal integrity, not an independent signature. Review readers bind canonical inputs, status, force, solved geometry and context to numerical records without regenerating prose or CSS. A later wording or style edit therefore does not make existing evidence unreadable. Producer tests establish current interpretation correctness.

This work adds no physical measurement or physical validation. Published-data force failures remain unresolved. The existing force fixture tests 200 µm joints, while the Board example assumes 400 µm joints. Neither establishes package motion, yield, reliability or a manufacturing volume recommendation. Further physics investment depends on measured process inputs and the commissioned physical test.

## Choices that kept the pass bounded

Experience First put the interpretation before meshes and kept detailed input identity expandable. Model the Domain made one review record own the meaning shared by both screens and exports. Laziness Protocol reused existing export/invalidation paths and kept Study's existing brief. Prove It Works required actual downloads, native replay, retained failure and browser interaction before completion. [Design judgment](judgment.md) and the append-only [decision trail](decisions-log.tsv) retain the tradeoffs.
