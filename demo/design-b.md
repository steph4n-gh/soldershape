# The misaligned joint comparison

## Problem

A process engineer should see a consequential question before seeing a form. The existing footprint workbench can solve the question, but its controls require the reader to construct the experiment first. This design opens a focused recorded comparison and keeps the current workbench as the place to change physical assumptions.

The first question is "Does 40% more solder help a joint displaced by 120 µm?" The subtitle states the conditions. Both pads are 200 µm, their prescribed gap is 150 µm, and the surrounding footprint pitch is 400 µm. The nominal comparison is 5 versus 7 nL. The conditional objective requires lateral restoration without an upward separating force. These are planning inputs for an isolated joint.

## Usage

An engineer opens `/demo`. Two exact native meshes and their force arrows appear immediately at the recorded 120 µm sample. The reader can select the independently solved 40, 80 and 120 µm samples, rotate both views together, inspect their numerical checks and export the evidence. No solver must be installed to inspect retained results. No live computation is implied by moving between samples.

The page offers "Open these inputs in the workbench" by downloading the existing editable case. The adjacent instructions tell the reader to use the existing Open case control. This small amount of friction earns its place because the demo has no second experiment editor.

The renderer and the endpoint have small caller interfaces.

```python
# The local server reads the retained native archive through this one operation.
document = read_demo(ROOT / "output/extreme-probe.zip")
self.respond(200, document)

# A maintainer regenerates the same bounded experiment using the existing runner.
# python3 demo/probe.py
# python3 -m soldershape replay output/extreme-probe.zip
```

```javascript
const demo = await api("/api/demo");
selectSample(demo.samples.at(-1).offset_mm);
drawJoint(leftCanvas, selected.reference, sharedCamera);
drawJoint(rightCanvas, selected.candidate, sharedCamera);
```

## Shape

The data shape is a table of independently solved offsets. Every row contains its two retained results and an interpretation derived from those results. The existing `JointSpec` and result dictionaries remain the numerical contract. The new domain record owns pairing, eligibility, labels and source identity. It never owns a second copy of a mesh or force formula.

```python
@dataclass(frozen=True)
class RecordedSample:
    offset_mm: float
    reference: dict
    candidate: dict
    interpretation: dict

@dataclass(frozen=True)
class RecordedDemo:
    source_sha256: str
    footprint: dict
    reference_volume_mm3: float
    candidate_volume_mm3: float
    samples: tuple[RecordedSample, ...]
    archive_sha256: str
    recorded: Literal[True]
    physical_qualification: Literal["unqualified"]

def read_demo(archive: Path) -> RecordedDemo:
    raise NotImplementedError

def interpret_pair(reference: dict, candidate: dict) -> dict:
    raise NotImplementedError
```

`read_demo` calls existing `read_bundle` before exposing anything. It reads the footprint from that same hashed archive. It requires exactly two volumes, one shared selected pad, unique volume/offset pairs and consistent shared geometry/material. Pairing uses normalized request values. It does not parse design labels. No valid reference may silently substitute for a missing or failed candidate.

`interpret_pair` returns `eligible`, `numerically_unresolved`, `outside_model_scope`, or `incomplete_pair`. Only checked meshes with no scope warning receive force comparisons. Each eligible result has a restoring-force value, the signed vertical force and the declared no-upward-force screen. Failed results retain their error and receipt link. Neither an unknown point nor a scope warning receives a favorable result.

```javascript
function selectSample(offsetMm) { throw new Error("not implemented"); }
function renderDemo(demo, offsetMm) { throw new Error("not implemented"); }
function drawJoint(canvas, result, camera) { throw new Error("not implemented"); }
```

The selection is one offset key, not an animation time or a free slider value. A fixed array of button labels derives from the validated sample table. Both mesh views and all visible values derive from that selected row. One shared camera contains yaw, elevation and zoom. There is no request-in-flight state because the page is a recorded inspector.

## Module map

- `demo/probe.py` remains the bounded native runner. It writes the archive only through `make_bundle`. Preserve the six original probe cases and their errors.
- `soldershape/demo.py` contains the archive boundary and pair interpretation. Its public operation is `read_demo`. It derives identity and display data from one archive.
- `soldershape/__main__.py` adds `/demo`, its static assets, `/api/demo` and a fixed allowlisted archive download. It never serves an arbitrary path supplied in a URL.
- `soldershape/web/demo.html`, `demo.css` and `demo.js` own this one comparison page. They do not copy numerical decisions into JavaScript.
- `soldershape/web/mesh-view.js` receives the existing exact-triangle drawing code once. Both the workbench and demo call `drawJoint`. Keep DOM queries and blank-state prose in their caller. The renderer accepts only a result, camera and drawing options.

This renderer move is the only change to the old workbench beyond its demo navigation link. Preserve its force chart and case workflow. If moving the renderer requires broader state refactoring, keep the renderer local to the demo for this iteration and record that bounded duplication instead of rebuilding the workbench.

## Interaction

The first viewport has the question, an explicit "Recorded native computation" badge and two equal-size joint views. The smaller volume is warm copper. The larger volume is cool blue. Both use the same geometric scale, camera and force-arrow scale. Force magnitudes have units and signed vertical direction. Arrows must not imply motion speed.

The 120 µm result already has a useful contrast in `demo/probe.log`. The 5 nL joint has approximately 92.263 µN of lateral restoration and 89.981 µN downward force. The 7 nL joint has approximately 82.193 µN restoration and 7.619 µN upward force. These are recorded numerical results under the declared fixed-gap model. They do not establish a production volume choice.

A small plan view shows the actual 36-pad footprint and highlights the selected pad. Its caption says "Footprint context. Only the highlighted joint is solved." Neighboring pads have no repeated solder meshes. A scale marker shows 400 µm pitch and the selected upper-pad displacement. The page does not fabricate a PCB stackup or suggest the source footprint is a completed board design.

Below the meshes, three discrete offset buttons select both results together. A compact table always displays every retained offset and the force-sign outcomes. No interpolated line passes through unsolved offsets. A new bounded failure, if retained, receives an explicit unresolved row rather than disappearing.

The export control downloads the original archive that supplied the visible data. It includes the exact solved meshes, normalized requests, source footprint and native receipts. A separate editable-case download contains the selected offset and both volume choices using the existing case baseline. An expanded checks panel exposes refinement, volume error, topology, model warnings, engine identity and input hashes. All cells derive from retained results.

## Why this shape

Experience First makes the contrast visible before exposing input controls. The engineer first understands the conditional tradeoff. The maintainer inherits a read-only inspector rather than another numerical workbench.

Model the Domain changes the core state to a paired sample keyed by offset. It prevents the left mesh, right force values and selected export from representing different experiments.

Laziness Protocol keeps the existing solver, export and replay paths. A simple archive reader hides integrity validation and pair consistency behind one operation. The browser receives display-ready records and exact meshes. It never coordinates solver stages or recreates acceptance rules.

## Alternatives considered

1. Add a dramatic preset to the current workbench. This reuses every control and renderer with the fewest files. It still exposes a general experiment editor before the reader understands the question. The first view cannot compare both exact meshes simultaneously without restructuring the existing page.
2. Build a board-wide interactive simulator. This is visually stronger, but exposes unresolved package coupling, neighboring joints, clearances and thermal process assumptions. The current isolated-joint engine cannot hide that complexity truthfully. It loses on capability and credibility.
3. This focused recorded comparison keeps inspect, compare and export in one page. It accepts six fixed samples in exchange for an immediate result with complete receipts. Customization belongs to the established workbench.

## Analytical comparison and limits

Van Veen Eq. 9 is the stronger simple substitute for aligned light-load height calculations. It does not answer the nonzero-offset force-direction question shown here. Explain that distinction beside a link to the retained comparison report. Do not claim all analytical models fail.

The retained volume-equivalent-cylinder comparison can appear in the expanded explanation. It changes an effective radius instead of preserving the pinned circular rims. Its contrasting decision is evidence about that specific approximation and declared screen. It is not a physical validation of the native result.

The interpretation is conditional on fully wetted pinned rims, fixed 150 µm gap and the stated material. There is no alignment time, placement yield, bridge probability, array solve, free package motion, reflow history or physical qualification. Mesh self-intersections remain unchecked. Increasing displacement only earns a new sample if the native and model-scope checks remain explicit.

## Verification

Before calling the demo complete, exercise the real page at every retained offset. Confirm the displayed input hashes, forces and mesh triangle counts match the downloaded archive. Download the selected editable case, reopen it in the existing workbench and verify both volume choices and shared conditions.

Replay the actual downloaded archive using `python3 -m soldershape replay FILE.zip`. Report numerical equivalence separately from exact engine provenance. Check a deliberately tampered archive fails integrity validation. Check a fabricated failed candidate produces an unresolved pair with no favorable banner or hidden row.

The browser should show the first result without a solver request. Network inspection must confirm a page reload only reads recorded evidence. A screenshot must include the recorded badge, selected offset, signed forces and single-joint context. Test renderer parity in the old workbench after extraction.

## Open risks and synthesis

Could a reader mistake the held gap for a naturally obtained package standoff? Put "Gap held at 150 µm" directly beside the comparison rather than only in expanded assumptions.

Could an engineer infer the lower solder volume is qualified? Name the outcome "Passes the declared numerical screen" and keep "Physical qualification unavailable" next to it.

The arena lead owns the final synthesis. This candidate recommends the focused inspector as the base. Graft the current workbench's exact-mesh camera behavior and existing case export. Reject a second editor and any repeated array mesh.

## Next implementation step

Implement `read_demo` against the existing six-case archive and verify its normalized pair table before drawing the page.
