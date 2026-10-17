# Compare one selected joint

This guide produces a two-volume comparison at an actual ULX3S pad, a readable review and a reproducible evidence archive. The process inputs are hypothetical. A successful calculation does not qualify them for manufacturing.

## Start the local workbench

Install Python 3.12 or newer, a C compiler and `make`. On macOS, Apple's command line developer tools provide the compiler and `make`. The initial engine setup needs internet access and builds a pinned upstream source archive.

From the extracted source directory, run these commands.

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8765
```

The setup prints `ready: true` in its JSON result. The service prints its local address. Open `http://127.0.0.1:8765/board`. The header reports Surface Evolver as ready. Keep the terminal running. Stop it with Ctrl+C when finished.

If port 8765 is occupied, choose another port with `--port`. Use that same port in your browser. The launcher reuses an identified SolderShape service and leaves another application alone.

A raw Git clone does not include the ignored prebuilt lab ZIPs and handbook PDF. The complete release candidate includes them. They are optional for this Board workflow. See the force-lab and coupon build guides if you need to regenerate them.

## Declare the comparison

1. Select component **U1** and pad **J16**. The source copper diameter is 400 µm. Other pads supply board context and remain unsolved.
2. Enter upper pad diameter **400 µm**, held gap **300 µm** and local X offset **240 µm**.
3. Enter reference liquid volume **40 nL** and candidate liquid volume **56 nL**.
4. Use surface tension **0.48 N/m**, density **9 g/cm³** and gravity enabled to reproduce this example. These example material values are not a calibrated alloy recommendation.
5. Choose **Compute selected comparison**. Wait for the native computation to complete.

The recorded engine produces the following predictions.

| Quantity | Reference | Candidate |
| --- | --- | --- |
| Liquid volume | 40 nL | 56 nL |
| X force on upper pad | −184.526 µN | −164.385 µN |
| Z force on upper pad | −181.284 µN | +13.386 µN |

Negative X opposes this positive offset. Positive Z points upward. Under this declared fixture objective, less solder meets the rule requiring restoration without an upward separating force. More solder pushes upward. This result does not select a production volume.

## Inspect and keep the result

1. Expand **Candidate result and inputs**. Read the force directions, declared dimensions and numerical status.
2. Choose **Save review HTML**. The file keeps exact values and assumptions without requiring the application. Its evidence links refer to files in the extracted accompanying ZIP.
3. Choose **Download board-bound evidence**. This archive keeps the original board, pad mapping, two native meshes, review, inputs and numerical receipts together.
4. Choose **Save editable case** for an input-only copy. Choose **Inspect this joint** to open those exact dimensions and reference in Joint details.

Joint details edits mm and mm³ and also shows µm and nL. The candidate volume is 0.056 mm³, which is 56 nL. The copied input needs a fresh calculation. Board-bound evidence stays in Board explorer.

Editing an assumption removes the old current result and download links. Browser-tab drafts preserve inputs across navigation and reload. Save a case file for a durable copy.

## Replay the evidence

From this repository root, verify your downloaded Board ZIP. Replace the example filename with its actual path.

```sh
python3 tools/verify_board.py /path/to/soldershape-board-comparison.zip --replay
```

The output reports integrity, selected-pad binding and numerical replay. `passed: true` establishes agreement within the declared checks on that engine. It does not establish physical accuracy.

To examine the supported-load question, use **Open case** in Joint details with `examples/loaded-volume.soldershape.json`. Choose **Compare reference and candidate**. At 4 µN downward load per joint, the 6 and 5 nL volumes predict approximately 141.986 and 125.400 µm gaps. Upward force is expected because it supports that load.

See [model and validation](model-and-validation.md) before using a prediction to plan a physical decision.
