# Candidate A. A guided extreme case inside the existing workbench

## Usage first

Open `/?demo=alignment`. The first screen asks, “At 30% of pitch misplacement, does more solder help the joint restore without pushing the upper pad away?” It identifies the example as a 36-pad KiCad footprint with a prescribed 150 µm pad-face gap. It immediately shows the two actual native meshes, the lateral and vertical forces, and “Recorded computation. Physical accuracy unqualified.”

Select the discrete 40, 80 or 120 µm offset button. Both designs change together. The selection does not interpolate or animate the geometry. Rotate the linked cameras, inspect numerical receipts, then download the comparison ZIP. Choose “Edit these inputs” to enter the existing workbench with the selected case and its reference. A new solve uses the existing compare button and invalidates the recorded result immediately.

Representative caller usage is the contract.

```python
# A recording maintainer creates three checked two-design bundles.
record_alignment_demo(Path("demo/alignment.json"), Path("evidence/alignment-demo"))

# A local handler returns one verified recorded comparison.
view = read_alignment_demo(Path("evidence/alignment-demo"), offset_um=120)

# CLI replay remains the installed trusted engine pathway.
# python3 -m soldershape replay evidence/alignment-demo/offset-120.zip
```

```javascript
// The existing application owns the viewer and its editing lifecycle.
const demonstration = await loadAlignmentDemo(120);
showRecordedComparison(demonstration);
openEditableCase(demonstration.editableCase);
```

## Problem

The current pad-height study is careful but does not make nonlinear geometry immediately visible. The fixed-gap engine already supports an emotionally clearer consequence. At the six retained probe points, 5 nL provides stronger lateral restoring force and pulls the upper pad downward. At the same conditions, 7 nL still restores laterally but pushes upward. The demonstration should make this conditional difference inspectable without presenting a capillary calculation as a qualified PCB recommendation.

## Shape

The organizing data shape is one immutable demonstration with a finite set of independently computed comparisons. The reference and candidate share the same footprint, selected circular lower pad, upper diameter, material, prescribed gap and offset. Only volume differs. These invariants belong in the recorder and validated demo reader rather than browser conditionals, per Model the Domain and Boundary Discipline.

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

@dataclass(frozen=True)
class AlignmentPoint:
    offset_um: int
    bundle_name: str
    bundle_sha256: str

@dataclass(frozen=True)
class AlignmentDemo:
    title: str
    question: str
    footprint_name: str
    pitch_um: int
    points: tuple[AlignmentPoint, ...]
    physical_qualification: Literal["unqualified"]

def record_alignment_demo(protocol: Path, output: Path) -> AlignmentDemo:
    raise NotImplementedError

def read_alignment_demo(directory: Path, offset_um: int) -> dict:
    raise NotImplementedError

def verify_alignment_demo(directory: Path, *, replay: bool = False) -> dict:
    raise NotImplementedError
```

These return shapes use the existing normalized case and result structures internally. The public recorder hides the ordering, shared-condition checks, native execution and bundle generation. The reader hides archive integrity and semantic matching. There is no new simulation interface or alternative replay protocol.

```typescript
type DemoSelection = {
  kind: "recorded";
  offsetUm: number;
  response: ExistingComparisonResponse;
  editableCase: ExistingEditableCase;
  sourceBundleUrl: string;
};

type DisplayMode =
  | {kind: "workbench"}
  | {kind: "demo"; selected: DemoSelection};

function loadAlignmentDemo(offsetUm: number): Promise<DemoSelection> {
  throw new Error("not implemented");
}

function showRecordedComparison(selection: DemoSelection): void {
  throw new Error("not implemented");
}

function drawSolvedMesh(canvas: HTMLCanvasElement, result: ExistingResult,
                        camera: ExistingCamera): void {
  throw new Error("not implemented");
}
```

`DisplayMode` has one owner in `app.js`. Selecting a recorded point replaces the complete immutable comparison. Editing inputs leaves demo mode and clears both result and download. No separate “recorded” booleans survive after the transition. A late recording response cannot overwrite a newer offset selection or edited workbench. Existing revision guards already supply this behavior and should own it for both modes.

The exact native mesh renderer is extracted from the existing `drawModel` body only as far as required to accept a canvas and result. The current single-model view calls it once. Demo mode calls it for the reference and candidate with linked camera values. It draws returned vertices and triangles rather than deforming a procedural cylinder. Both panels include scale bars and the actual volume and offset.

The footprint remains a small contextual plan view beside the result. One pad is highlighted. Neighbor outlines are labeled “Footprint context. Neighbors not solved.” No full-array mesh duplication or package animation is needed. The geometry assumptions occupy one compact permanently visible line below the meshes.

## Module map

- `demo/alignment.json` owns the frozen protocol and user question. It declares all common geometry, the two volumes, allowed offsets, and the conditional acceptance rule.
- `tools/record_alignment_demo.py` owns the narrow recorder, reader verification and command entry point. It reuses existing request construction, solver, comparison policy and `make_bundle`. It emits three standard comparison ZIPs plus one small index manifest. Build the Lever makes the demonstration reproducible rather than a hand-assembled showcase.
- `soldershape/__main__.py` serves the trusted demo manifest and bundles through a narrow read-only local route. It does not execute archived code or expose arbitrary files.
- `soldershape/web/index.html`, `style.css` and `app.js` own the guided view and its entry into the workbench. They reuse existing controls, result checks, camera and export handling. A new dependency or general gallery layer is unnecessary under Laziness Protocol.

The caller follows at most recorder, existing comparison/solver, and existing artifact writer. No new domain hierarchy is introduced.

## Concrete interaction and consequence

The 120 µm point opens by default because it is an observed 30% pitch displacement, not the software offset limit. The measured 5 nL point has lateral force −92.263 µN and vertical force −89.981 µN. The measured 7 nL point has lateral force −82.193 µN and vertical force +7.619 µN. Numeric badges state the force directions explicitly. Signed arrows are diagrams of computed force direction, not trajectories or times.

The visible rule reads “Prefer lateral restoration without an upward separating force at this prescribed gap.” Both designs restore, but only 5 nL meets that rule at this point. This rule is an illustrative fixture objective. It does not select a production solder amount. The 40 and 80 µm samples show the same qualitative result with separate exact receipts. A compact table keeps every sampled force and status visible, including any additional failed point the root probe justifies.

An “Aligned formula” disclosure explains the strongest simpler alternative. Van Veen Eq. 9 is useful for aligned light-load height screening and remains the better tool for that question. It does not answer the sideways force and axial-force tradeoff of a fixed-gap tilted joint. A volume-equivalent cylinder may be drawn only as an explicitly labeled analytical comparison if its existing baseline is retained with exact formula inputs. It never replaces either native mesh.

## Numerical limits and replay

Every point retains normalized requests, result JSON, exact native geometry, checks, raw model/commands/output, source footprint, editable comparison, CSV and existing hashed manifest. A green marker requires the existing numerical classification and no model-scope warnings. Failed cases remain selectable with their failure receipts and cannot receive the preference badge. Self-intersections remain unchecked. Local equilibrium, pinned rims and fixed volume do not establish physical accuracy or global uniqueness.

The whole comparison download is the original verified two-result ZIP, not a reconstructed browser export. Its standard `replay` command recomputes both cases with the trusted installed engine. A separate three-bundle manifest supports verifying the complete presentation and all offsets. Exact engine provenance and numerical equivalence remain separately reported. The recorded badge does not change to “live” merely because an archive passes integrity checks.

## Alternatives considered

1. A separate `/demo` application with a bespoke two-mesh viewer hides distracting workbench fields and enables a stronger visual first impression. It loses here because the next interaction requires a second editable-case implementation or a handoff contract between two result owners. Sharing only a mesh helper still duplicates invalidation and export state. Its extra interface depth does not earn that lifecycle cost for one demonstration.
2. A static report with prerecorded screenshots and three ZIP links is the smallest implementation. It loses because engineers cannot inspect the solved surfaces or move directly from a sample to a trustworthy edited comparison. It is a useful fallback if native mesh rendering cannot remain responsive.
3. A general board simulator with all 36 joints moving together would be visually extreme. It fails the scientific contract because the current engine solves one independent joint and contains no coupled package motion or wetting dynamics.

## Tradeoffs accepted

- We accept three discrete offsets in exchange for instant exact native results and no implication of simulated motion.
- We accept a focused mode in the existing workbench in exchange for reusing the already tested editing, failure and export lifecycle.
- We accept a proposed process objective in exchange for a concrete falsifiable design question. No customer demand or manufacturing benefit is inferred.

## Verification and risks

The recorder must reject any disagreement between protocol, case and result input hashes. The verifier must check all six cases, reproduce all six through trusted replay when requested, and detect one deliberately changed archived force. Browser verification must inspect both exact meshes, choose all offsets, download and inspect the actual ZIP, enter editing mode, and prove results clear after an edit. The first viewport must show the question, recorded status, both force directions and physical limit without opening a disclosure.

The main integration risk is exposing global-state dependencies while extracting the existing renderer. Keep the extraction narrow and test the ordinary workbench camera and export after the change. If that extraction grows beyond a small parameterization, retain the existing single-mesh renderer with explicit reference/candidate buttons rather than building a new rendering framework.

## Next implementation step

Generate one standard 120 µm two-result comparison bundle from the declared protocol, verify it through the existing reader, then wire that immutable response into the current workbench before adding the other two points.

## Synthesis decision

Pending the root judge. This candidate deliberately favors one owner for demo viewing and editable computation over a separate polished application.
