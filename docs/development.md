# Develop and verify SolderShape

Use Python 3.12 or newer and run from the repository root. Core application code uses the standard library. Native tests also need the engine built by `python3 tools/setup_engine.py`. Fixture CAD and printable lab documents have separate optional dependency files under `force_lab/cad` and `force_lab/tools`.

## Run checks

The full suite includes native solver checks and can take several minutes.

```sh
mkdir -p output
python3 -m unittest discover -s tests -v
node cohesion/verify-ui-state.cjs output/development-ui-state-new.json
```

Use a new receipt filename for each run. The Node runner uses a mocked DOM and browser storage. It checks recovery and response invalidation. It does not prove real browser rendering, numerical field validity or a new physical result.

These checks do not require a native solve.

```sh
python3 -m unittest tests.test_boundaries tests.test_cases tests.test_web_inputs -v
python3 -m compileall -q soldershape tools
node --check soldershape/web/app.js
node --check soldershape/web/board.js
node --check soldershape/web/study.js
node --check soldershape/web/ui.js
node --check website/dist/site.js
```

The prepared GitHub Actions workflow runs this smaller boundary and syntax set, plus the pure request and finite-pad source checks from `prelab` and the offline two-gap walkthrough verifier. It has not been exercised on hosted CI before a repository is published. Native platform qualification remains a separate check.

## Reproduce a numerical comparison

Choose output filenames that do not already exist. These commands retain new evidence outside the historical record.

```sh
python3 -m soldershape solve-case examples/centering-volume.soldershape.json --output output/development-centering-new.zip
python3 -m soldershape replay output/development-centering-new.zip
python3 -m soldershape solve-case examples/loaded-volume.soldershape.json --output output/development-loaded-new.zip
python3 -m soldershape replay output/development-loaded-new.zip
```

For a Board archive, use its verifier to retain selected-pad binding.

```sh
python3 tools/verify_board.py board_demo/data/default-comparison.zip --replay
```

The guided Board decision walkthrough also has a retained one-input experiment. Its offline check verifies both bound archives and confirms that only held gap changes from 300 to 330 µm.

```sh
python3 decision_walkthrough/verify.py
python3 tools/verify_board.py decision_walkthrough/evidence/ui-gap-330.zip --replay
```

The offline verifier does not launch the engine. The replay command does. These two sampled requests do not establish manufacturing tolerance or physical force accuracy. [Walkthrough verification](../decision_walkthrough/RESULTS.md) records the actual browser checks.

CLI help lists the commands and flags.

```sh
python3 -m soldershape --help
python3 -m soldershape solve --help
python3 -m soldershape study --help
```

## Change the application

`soldershape/model.py` parses domain inputs and KiCad geometry. `solver.py` generates trusted native models, invokes the pinned engine and evaluates numerical checks. `artifacts.py` exports and verifies evidence. `board.py` binds a selected pad to the original board. `study.py` owns the distinct two-footprint and equivalent-domain study. `__main__.py` supplies CLI and local HTTP boundaries. The web directory contains the connected views and shared input-draft helpers.

Restart the service after Python source edits. Board export verifies loaded source identity against disk. Keep source settled while computing or testing evidence; a mismatch is a deliberate failure.

Preserve historical results. Write new experiments into a new output location rather than overwriting `evidence/physical` or an archived ZIP. Numerical, physical and presentation claims require different evidence. A passing build does not qualify force accuracy.

## Check a user workflow

Start the service and open Board explorer. Enter custom inputs, then explicitly load the U1/J16 worked example. Confirm that **Restore my previous inputs** returns the custom values and clears forces. Load the example again and compute the 300 µm pair. Confirm that only 40 nL meets the declared fixture rule. Choose **Try a 330 µm held gap** and confirm that both volumes now meet it.

Inspect each result's numerical status and the separate physical qualification. Distinguish the initial verified recording from a fresh native result. Expand the candidate inputs and download the readable HTML, editable case and board-bound ZIP. Edit one input and confirm that the current result and export links clear. Restore the example and recompute before the next download.

Follow the matching Lab link to `/lab#board-question`. Confirm that it describes the 400 µm board joint, the required adaptation of the 200 µm fixture, and the separate 220 versus 270 µm clearance coupon. Open the case in Joint details and check dimensions, reference and source context. Also check narrow layout, keyboard access and supported-load behavior.

Inspect the actual downloaded bytes and replay at least one changed computation. Write new verification receipts to `output` or a new evidence directory. Do not overwrite historical browser or numerical receipts. Confirm failures remain failures. [Launch readiness](../launch/READINESS.md) records the actual run rather than treating this checklist as proof.
