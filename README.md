# SolderShape

Compare solder-joint assumptions at an actual KiCad pad. Inspect the predicted equilibrium shape and forces, then keep the exact inputs and numerical evidence for a physical test.

**Research preview. Physical force accuracy is unqualified.** The full board supplies context. Only the selected isolated joint is calculated.

![SolderShape inspecting an actual ULX3S pad](docs/media/board-explorer.png)

The example board is ULX3S by EMARD and its contributors. Its original silkscreen and [modified MIT notice](board_demo/source/LICENSE.md) are retained. The board authors do not endorse this solder comparison.

## Run locally

Requirements are Python 3.12 or newer, a C compiler, `make`, and a modern browser. The application uses Python's standard library. Setup downloads and builds the hash-pinned native Surface Evolver engine. Internet access is needed for that first setup.

From this source directory, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8765
```

Open [Board explorer](http://127.0.0.1:8765/board). On macOS, you can also double-click `Start SolderShape.command`. This checkout was exercised on Apple Silicon macOS with Python 3.14 and Apple clang 21. Other systems remain unqualified. A separate Node.js runtime is useful for development checks, not application use. A raw Git clone omits prebuilt lab ZIPs and the handbook PDF. The complete release candidate includes those optional files; the core Board comparison works without them.

[Start with one complete comparison](docs/getting-started.md). [Watch the 24-second visual walkthrough](docs/media/walkthrough.mp4), assembled from actual application captures. A [text transcript](docs/media/README.md) covers the same steps.

## What you can do

- Select a real board pad or import a circular copper SMD pad from a KiCad footprint.
- Compare upper-pad diameter or liquid solder volume under shared conditions.
- Prescribe the gap, or solve the gap under a supported downward load per joint.
- Sweep prescribed offsets and inspect each native mesh, force and numerical status.
- Save input-only cases. Export readable HTML, CSV, OBJ, STL and the native numerical receipts together.
- Plan a pad revision or an outside-lab measurement using the separate study and fixture materials.

The default Board example asks whether 40% more solder improves a held-gap force tradeoff. At its hypothetical inputs, 56 nL produces weaker lateral restoration and an upward separating force compared with 40 nL. This is an inspectable model comparison, not a manufacturing recommendation. [Inspect the result and its limits](docs/model-and-validation.md).

## What is established

The application uses the existing Surface Evolver numerical engine. Its contribution is the KiCad-to-comparison-to-evidence workflow. Numerical refinement and replay checks assess consistency. Published physical comparisons include unresolved force discrepancies and model limits. No process-specific accuracy, package self-alignment, bridging, yield or reliability is established.

The [validation reference](docs/model-and-validation.md) separates numerical agreement, published-data comparisons and unperformed physical tests. [Developer checks](docs/development.md) explain how to reproduce the evidence. Engineering reports retain failed cases and historical source identities.

The [current pre-lab investigation](prelab/REPORT.md) tests the actual 220 versus 270 µm coupon under combined input changes and prescribed wetting hypotheses. It retains ranking reversals and finite-pad solver failures. Its [measurement addendum](prelab/LAB_ADDENDUM.md) identifies the observations needed before either design can receive a clearance qualification.

## Documentation

[Documentation index](docs/README.md) points to the user guide, model reference, CLI and verification commands, and the engineering record. [CONTRIBUTING.md](CONTRIBUTING.md) describes useful contributions. [SECURITY.md](SECURITY.md) describes the local-only runtime boundary and pre-launch reporting status. [Launch readiness](launch/READINESS.md) records what is complete and what still needs a public release.

## License and credit

SolderShape's original code, documentation and project-authored design files use the [MIT license](LICENSE). Third-party material retains its own terms. The bundled KiCad library footprint uses CC-BY-SA 4.0 with an electronic-design exception. ULX3S uses its modified MIT notice. The native engine is downloaded and built locally; its binary and source archive are not redistributed here. See [THIRD_PARTY.md](THIRD_PARTY.md).

The lab and coupon artifacts are test-planning material. Their license does not establish fabrication readiness or physical validation.
