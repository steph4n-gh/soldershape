# A real board, one identified joint

Open `/board` to inspect the attributed ULX3S FPGA board and compare solder-volume hypotheses at one selected circular copper pad. The page links the actual component, pad identifier, net, board coordinates and local offset axis to two native Surface Evolver computations. The complete layout is context. Only the selected joint has a computed surface.

The initial U1 J16 comparison uses the source board's 400 µm lower copper pad. The 400 µm upper pad, 300 µm held gap, +240 µm offset, 40 versus 56 nL liquid volumes, 0.48 N/m surface tension and 9 g/cm³ density are hypothetical inputs. They are not measurements of the actual ULX3S package or assembly process. Replace them with independent process measurements before planning a physical confirmation.

A native numerical check is not physical validation. The previous force-validation failure remains unresolved. This model omits mask-defined wetting, contact-angle hysteresis, flux and oxide chemistry, neighboring joints, package mechanics, bridging and thermal transients. It cannot predict whole-package self-alignment or manufacturing yield.

The retained fresh native comparison gives these predictions under the hypothetical inputs above.

| Liquid volume | Lateral force | Normal force | Native mesh triangles |
| --- | ---: | ---: | ---: |
| 40 nL | −184.526 µN | −181.284 µN | 6,336 |
| 56 nL | −164.385 µN | +13.386 µN | 24,960 |

Both cases pass the existing refinement checks and have no pad-plane excursion warning. Extra liquid reduces lateral restoration and changes the normal force to upward in this held-gap comparison. This conclusion is conditional on the declared fixture objective and assumptions.

## Run

From `/Volumes/Storage/oct16project`:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8768
```

Open `http://127.0.0.1:8768/board`. Inspect a package and pad, change the geometry or process assumptions, and choose the fresh comparison action. Changes invalidate earlier results and downloads. Unsupported pads remain inspectable but cannot be computed. Front circular SMD copper pads still require independent confirmation of their actual wetting boundary.

The initial preview is a retained pair of fresh native calculations. Its recording identity and every exported member are verified before display. The fresh comparison action always runs the native engine again.

## Verify and reproduce

```sh
python3 tools/verify_board.py
python3 tools/verify_board.py board_demo/data/default-comparison.zip --replay
python3 -m unittest discover -s tests -p 'test_board*.py'
```

Run the same verifier against the ZIP actually downloaded from the browser. It checks the selected pad, source board and license, trusted extraction, editable case, normalized inputs, comparison, conditional screen, CSV and exact exported mesh. `--replay` regenerates both requests and compares new native forces, engine identity and model warnings. Archived executable text is evidence and is never executed.

The board extraction and its independent native inspection are separate from the force replay:

```sh
python3 board_demo/tools/extract.py
python3 board_demo/tools/verify_native.py
```

These commands use the pinned KiCad Docker image documented in the extraction receipt. They preserve the downloaded original source. The readback checks original-board geometry against the extracted context. Byte hashes alone cannot prove that extraction was geometrically correct.

To intentionally replace the hypothetical default recording with new native results:

```sh
python3 tools/verify_board.py --record
python3 tools/verify_board.py --replay
```

A changed numerical source requires a fresh Python process before recording. Keep previous negative results when changing a scientific hypothesis.

## Source and useful distinction

The original ULX3S board is pinned in `source/provenance.json` to [emard/ulx3s](https://github.com/emard/ulx3s). Its original modified MIT license and required logos remain with the source and drawing. This experiment is not endorsed by the board's authors.

KiCad remains the better general layout viewer. The existing SolderShape workbench provides the same isolated-joint physics. This page adds a source-bound handoff. A reviewer can locate the actual pad, see which process inputs are unknown, compare a concrete force hypothesis, and replay the exact board-bound evidence without transcribing coordinates or dimensions. No physical accuracy advantage or commercial moat is established by this demonstration. Independent prospective measurements remain the decisive gate.
