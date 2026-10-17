# Develop and verify SolderShape

Use Python 3.12 or newer and run from the repository root. Core application code uses the standard library. Native tests also need the engine built by `python3 tools/setup_engine.py`. Fixture CAD and printable lab documents have separate optional dependency files under `force_lab/cad` and `force_lab/tools`.

## Run checks

The full suite includes native solver checks and can take several minutes.

```sh
python3 -m unittest discover -s tests -v
node cohesion/verify-ui-state.cjs
```

The Node runner uses a mocked DOM and browser storage. It checks recovery and response invalidation. It does not prove real browser rendering, numerical field validity or a new physical result.

These checks do not require a native solve.

```sh
python3 -m unittest tests.test_boundaries tests.test_cases tests.test_web_inputs -v
python3 -m compileall -q soldershape tools
node --check soldershape/web/app.js
node --check soldershape/web/board.js
node --check soldershape/web/study.js
node --check soldershape/web/ui.js
```

The prepared GitHub Actions workflow runs this smaller boundary and syntax set. It has not been exercised on hosted CI before a repository is published. Native platform qualification remains a separate check.

## Reproduce a numerical comparison

```sh
python3 -m soldershape solve-case examples/centering-volume.soldershape.json --output output/comparison.zip
python3 -m soldershape replay output/comparison.zip
python3 -m soldershape solve-case examples/loaded-volume.soldershape.json --output output/loaded-volume.zip
python3 -m soldershape replay output/loaded-volume.zip
```

For a Board archive, use its verifier to retain selected-pad binding.

```sh
python3 tools/verify_board.py board_demo/data/default-comparison.zip --replay
```

The guided Board example also has a retained one-input experiment. Its offline check verifies both bound archives and confirms that only held gap changes from 300 to 330 µm.

```sh
python3 decision_walkthrough/verify.py
python3 tools/verify_board.py decision_walkthrough/evidence/gap-330-probe.zip --replay
```

These two sampled requests do not establish manufacturing tolerance or physical force accuracy. [Walkthrough verification](../decision_walkthrough/RESULTS.md) records the actual browser checks.

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

Start the service and open Board explorer. Compute the default pair, inspect the selected result and download both HTML and ZIP. Open the same case in Joint details. Confirm dimensions, reference and source context. Edit an input and confirm the old results and links clear. Open the supported-load example. Check each result row, a narrow window, keyboard access and the lab links.

Inspect downloaded bytes and replay at least one changed computation. Confirm failures remain failures. [Launch readiness](../launch/READINESS.md) records the actual run rather than treating this checklist as proof.
