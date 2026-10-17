# Follow a design question through Board explorer

Board explorer now starts with a concrete process decision on actual ULX3S copper. Compare 40 and 56 nL on U1 pad J16, then change the held gap and see whether the declared fixture outcome changes. Use this comparison to choose a test candidate. The process assumptions and force accuracy remain unqualified.

## The complete workflow

1. Identify the actual source pad. Its lower copper diameter is 400 µm. All other joints remain unsolved.
2. Load the worked example explicitly. A single prior input snapshot lets the visitor return to their own work. Reloading a saved draft never replaces it with the example.
3. Compute the two volumes. The shared server review and screen supply every numerical conclusion. Each card shows its server-provided fixture outcome.
4. Try a 330 µm held gap. The action changes only gap and uses the ordinary native computation. Prior results and exports clear immediately.
5. Save the exact case, readable review and board-bound evidence. The Board-specific Lab link identifies the missing measurements and required fixture adaptation.

Ordinary section links connect the existing page. No additional wizard, endpoint, package, numerical model or result lifecycle was introduced. One owner changed the coupled application files after two isolated sketches and an independent cross-judge. Root owned evidence and browser verification.

## What the changed assumption demonstrates

Both cases use 400 µm upper and lower circular boundaries, +240 µm offset, surface tension 0.48 N/m, density 9 g/cm³ and gravity. These are example inputs, not identified properties of an assembled ULX3S joint. The fixture objective requires lateral restoration without upward separation at a held gap. A free package needs a different weight-support objective.

| Held gap | 40 nL X force | 40 nL Z force | 56 nL X force | 56 nL Z force | Numerical fixture outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| 300 µm | −184.526 µN | −181.284 µN | −164.385 µN | +13.386 µN | Only 40 nL meets the rule |
| 330 µm | −169.063 µN | −227.390 µN | −170.455 µN | −82.276 µN | Both volumes meet the rule |

The gap change removes the original upward-force reason to exclude 56 nL from this numerical screen. Two sampled hypotheses do not establish manufacturing tolerance, a physical error bound or a preferred production volume.

The [offline experiment verifier](verify.py) checks bound archives and the one-input change. The original browser probe, fresh post-change 300 µm and 330 µm exports, and exact standalone HTML are retained under [evidence](evidence). Fresh native replay of the exported 330 µm pair produced zero X and Z force differences with matching engine identities.

## Verification

The [browser receipt](evidence/browser-checks.json) summarizes executed CUA interactions and their limits. It records saved custom inputs across reload, repeated example loading, original snapshot restoration, fresh baseline computation, changed-gap computation, cleared pending results, rejected late responses, inspect-only selection, actual downloads, section links, Lab navigation, the separate coupon report, and editable-case transfer into Joint details.

The 390 by 844 pixel layout had no document horizontal overflow. All four walkthrough links remained visible. The Lab anchor also fit the narrow viewport. The temporary viewport override was reset. A fresh tab distinguished the initial recording from a later fresh native result. Its per-volume outcomes changed from reference-only to both meeting the rule.

Thirty focused Python tests pass. Fourteen existing shared UI boundary checks pass in a mocked runtime. Those mocked checks cover shared storage and handoff code, not the new board rendering. Actual browser checks cover the new board path. JavaScript syntax and diff whitespace checks pass. Numerical failure and unavailable-engine behavior were reviewed in source and existing software tests. They were not separately induced on the running user service.

One redundant verifier docstring was removed after [comment review](comment-review.md). The existing shared UI check initially wrote its default historical receipt. Root preserved that fresh result separately, restored the exact baseline receipt, and reran the check with an explicit new output path. No historical evidence remains changed.

An optional browser history-back check interrupted the CUA runtime. Root resumed from the actual tab state and completed the handoff through visible links. The browser receipt summarizes earlier observations from the tool record. It is not an automated browser replay, external attestation or physical certificate.

## Reproduce

From the repository root, use the existing running service at `http://127.0.0.1:8769/board`. To start a separate local service, use an available port.

```sh
python3 -m soldershape serve --port 8765
python3 decision_walkthrough/verify.py
python3 tools/verify_board.py decision_walkthrough/evidence/ui-gap-330.zip --replay
python3 -m unittest tests.test_board tests.test_review tests.test_web_inputs tests.test_workspace_http -v
mkdir -p output
node cohesion/verify-ui-state.cjs output/decision-shared-ui-state.json
node --check soldershape/web/board.js
```

Fresh native computation requires the existing pinned engine. If it is absent, build it with `python3 tools/setup_engine.py`. The offline experiment verifier does not launch native computation.

## Physical limits and remaining work

The Lab handoff asks for independent hot wetting boundaries, upper-pad geometry, liquid volume, held gap and offset, alloy, temperature, material properties and measured force versus displacement. The current 200 µm fixture needs adaptation and qualification for the 400 µm board-joint question.

The 220 versus 270 µm coupon asks a separate loaded-height question about supported component clearance. Its 185 µm target and ranking do not validate this board's forces. The app now states why that coupon exists and links its conditional findings without transferring its claims to the board.

Production numerical source, historical board recording, coupon protocol and pre-lab evidence remain unchanged. [Preserved source identities](evidence/preserved-source.json) record the selected baseline files. No deployment, public launch, lab communication, fabrication or physical measurement occurred.

Experience First kept the story beside the actual board and controls. Model the Domain kept one accepted-result lifecycle and one prior-input snapshot. Laziness Protocol reused server conclusions, native computation and exports. Prove It Works required actual browser execution and downloaded evidence. Explain the Number kept the sampled gap effect separate from process uncertainty and physical accuracy.

The [decision trail](decisions.tsv), [design synthesis](synthesis.md) and [independent review](final-review.md) describe the choices and acceptance limits. Review uses the configured inherited parent model. It is not model diversity or external scientific peer review.
