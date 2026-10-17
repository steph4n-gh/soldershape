# Follow a Board design decision

Use an actual ULX3S pad to compare two solder amounts, change one assumption, and save a test candidate with its numerical evidence. The process inputs are hypothetical. A successful calculation does not qualify them for manufacturing.

The question is whether adding solder helps a displaced joint restore laterally without pushing upward while a fixture holds its gap. A freely supported package needs a different objective because upward force can support its weight.

## Start the local workbench

Install Python 3.12 or newer, a C compiler and `make`. On macOS, Apple's command line developer tools provide the compiler and `make`. The initial engine setup needs internet access and builds pinned upstream source.

From the extracted source directory, run these commands.

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8765
```

The setup prints `ready: true` in its JSON result. The service prints its local address. Open `http://127.0.0.1:8765/board`. The header reports Surface Evolver as ready. Keep the terminal running. Stop it with Ctrl+C when finished.

If port 8765 is occupied, choose another port with `--port`. Use that same port in your browser. The macOS launcher reuses an identified SolderShape service and leaves another application alone.

A raw Git clone does not include the ignored prebuilt lab ZIPs and handbook PDF. The complete release candidate includes them. They are optional for this Board workflow. See the force-lab and coupon build guides if you need to regenerate them.

## Load the worked example

1. Choose **Load U1 / J16 worked example**. This selects actual U1/J16 lower copper, 400 µm in diameter. All other joints remain unsolved.
2. Follow **2. Declare the assumptions**. Confirm an upper pad diameter of **400 µm**, a held gap of **300 µm**, and a local +X offset of **240 µm**.
3. Confirm reference liquid volume **40 nL** and candidate liquid volume **56 nL**.
4. Confirm surface tension **0.48 N/m**, liquid density **9 g/cm³**, and gravity enabled. These are example values, not a calibrated alloy recommendation.
5. Choose **Compute selected comparison**. Wait for the native computation to complete, then follow **3. Read the result**.

Loading the example clears prior forces. The app keeps one prior input snapshot. **Restore my previous inputs** returns that snapshot and clears forces again. Reloading a saved browser draft preserves your inputs instead of silently loading the example.

A first visit can show a verified native recording of the initial hypothesis. Read the origin label beside the meshes. A recording is evidence from an earlier run. **Compute selected comparison** produces a fresh result for the shown inputs.

## Read the first outcome

At the 300 µm held gap, the retained native computation gives these forces on the upper pad.

| Quantity | 40 nL reference | 56 nL candidate |
| --- | ---: | ---: |
| X force | −184.526 µN | −164.385 µN |
| Z force | −181.284 µN | +13.386 µN |

Negative X opposes this positive offset. Positive Z points away from the board. Under the declared fixture objective, only 40 nL meets the numerical rule. The 56 nL candidate pushes upward. This outcome does not select a production volume.

Read the trust statements beside the result. The lower copper is identified from the board. Treating it as a pinned hot wettable rim is an assumption. Numerical checks assess the calculation. Physical force accuracy remains unqualified.

## Change the assumption that changes the answer

1. Follow **2. Declare the assumptions**.
2. Choose **Try a 330 µm held gap**. The action changes only the gap and computes both volumes again.
3. Follow **3. Read the result**. Confirm that the current inputs now show **330 µm**.

The retained native computation gives the following forces.

| Quantity | 40 nL reference | 56 nL candidate |
| --- | ---: | ---: |
| X force | −169.063 µN | −170.455 µN |
| Z force | −227.390 µN | −82.276 µN |

Both volumes now restore laterally and pull downward. Changing the gap removes the original upward-force reason to exclude 56 nL from this numerical screen. These two sampled hypotheses do not establish manufacturing tolerance, a physical error bound, or the best production volume.

You can also edit an assumption directly. Every edit clears the prior current result and its download links. Compute again before interpreting or exporting the changed inputs. Loading the worked example again returns to the 300 µm hypothesis.

## Keep a candidate and its evidence

1. Expand **Candidate result and inputs**. Read the force directions, declared dimensions and numerical status.
2. Choose **Save review HTML**. The readable file keeps the exact result and assumptions. Its evidence links refer to files in the extracted accompanying ZIP.
3. Follow **4. Decide what to measure**.
4. Choose **Download board-bound evidence**. The archive keeps the original board, selected-pad mapping, both native meshes, review, inputs and numerical receipts together.
5. Choose **Save editable case** for an input-only copy.

Browser-tab drafts preserve inputs across navigation and reload. Save the editable case for a durable copy. **Inspect this joint** opens the current candidate dimensions and reference in Joint details. Joint details edits mm and mm³ and also shows µm and nL. The candidate volume is 0.056 mm³, which is 56 nL. The copied case needs a fresh calculation there. Board-bound evidence stays in Board explorer.

The [walkthrough experiment](../decision_walkthrough/RESULTS.md) retains both outcomes and the browser verification. Its [330 µm native archive](../decision_walkthrough/evidence/gap-330-probe.zip) preserves the one-input change.

## Prepare the matching measurement

Choose **Prepare a test for this board question**. The link opens the **Physical test** section for this 400 µm board joint at `/lab#board-question`.

Keep the exported case and evidence with the test request. Ask the lab to identify the hot wettable rims, upper-pad geometry, liquid volume, held gap, offset, alloy, temperature, density and surface tension. The lab must qualify the force uncertainty and fixture before checking hot force versus displacement.

The existing 200 µm force fixture needs adaptation and qualification for this 400 µm joint. The separate 220 versus 270 µm coupon asks about supported component clearance against a 185 µm target. Its pad ranking does not validate this board example's forces.

## Replay the evidence

From the repository root, verify the downloaded Board ZIP. Replace this example filename with its actual path.

```sh
python3 tools/verify_board.py /path/to/soldershape-board-comparison.zip --replay
```

The output reports integrity, selected-pad binding and numerical replay. `passed: true` establishes agreement within the declared checks on that engine. It does not establish physical accuracy. See [model and validation](model-and-validation.md) before using a prediction to plan a physical decision.
