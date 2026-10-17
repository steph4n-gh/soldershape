# A decision study beside the joint viewer

## Usage from the engineer's view

The starting page asks which board revision to investigate before paying for a coupon run. The engineer opens **Compare pad revisions**. The existing geometry and force workbench remains available through **Inspect one joint**.

1. Import a reference footprint and select its lower copper pad.
2. Import a candidate footprint and select its lower copper pad. Both source files remain in the study.
3. Enter common upper-pad diameter, liquid solder volume, supported load, offset, surface tension, and density. Enter a required pad-face gap and the source of that requirement.
4. Declare a finite solder-volume screen. The first version uses nominal volume and two explicitly entered endpoint volumes. These points do not establish a continuous tolerance bound.
5. Confirm the literal circular-rim hypothesis. Optionally add the named two-pad effective-volume approximation with measured pad thicknesses. The form labels that approximation as a hypothesis under test.
6. Run the study. Read nominal native results first. Read the analytical comparison and declared sample table next. If an assumption changes the threshold outcome, read which measurement would resolve it.
7. Download the study archive. Give a colleague the input document, source footprints, human-readable decision report, sample table, and native evidence.

For the current coupon, the reference lower pad is 220 micrometers and the candidate lower pad is 270 micrometers. The requirement is 185 micrometers between pad faces. The report must identify that literal rims and the two-pad approximation give different threshold outcomes. It must not promise that the smaller pad passes the real assembly requirement.

The caller imports one study and runs one operation.

```python
from soldershape.study import read_study, run_study

study = read_study(json.loads(Path("pad-revisions.study.json").read_text()))
report = run_study(study)
assert report.decision.kind == "assumption_sensitive"
```

The browser submits the same input document. The server returns the complete accepted report and its archive. The browser renders report fields and does not recalculate a verdict.

```javascript
const accepted = await api("/api/study", editor.study);
if (editor.revision === submittedRevision) showStudy(accepted);
```

A legacy editable case opens through the same import operation. A case with a baseline becomes two arms with the same footprint and distinct upper-pad or volume inputs. A case without a baseline supplies the reference arm and leaves the candidate incomplete. Migration never invents a second board revision or a gap requirement.

```python
draft = read_study(legacy_case)
assert draft.requirement is None
assert draft.origin.schema == "soldershape.case.v1"
```

## Problem and existing constraints

The current product organizes work around one footprint, one parameter editor, and a reference containing only upper diameter and volume. `calculate_comparison` explicitly applies the current lower pad to both arms. That structure cannot represent the intended 220 versus 270 micrometer board revision study.

Expanding that reference inside the force viewer would make the existing editor own two meanings. The force chart compares an operating point. The proposed study compares candidate decisions under declared assumptions. This candidate gives the latter one input document and one owner.

`model.py` already owns validated `JointSpec`, `LoadSpec`, footprint parsing, and input hashes. `solver.py` owns the native solve and trusted generated models. `artifacts.py` owns inert archived inputs and hashed evidence. Those responsibilities remain intact. `study.py` owns the new decision policy.

## Shape and module ownership

The public domain model starts with the study. Raw JSON and HTTP objects remain at the import boundary. The following is a type sketch rather than implementation.

```python
@dataclass(frozen=True)
class FootprintPad:
    text: str
    pad_index: int
    # The reader derives the source hash, copper diameter, and mask classification.

@dataclass(frozen=True)
class Design:
    name: str
    lower_pad: FootprintPad
    upper_diameter_mm: float
    nominal_liquid_volume_mm3: float

@dataclass(frozen=True)
class SharedCondition:
    normal_load_uN: float
    offset_mm: float
    surface_tension_n_m: float
    density_g_cm3: float
    gravity: bool
    evidence_notes: str

@dataclass(frozen=True)
class GapRequirement:
    pad_face_gap_um: float
    source: str

@dataclass(frozen=True)
class VolumeSamples:
    reference_mm3: tuple[float, float, float]
    candidate_mm3: tuple[float, float, float]

@dataclass(frozen=True)
class LiteralRims:
    kind: Literal["literal_rims"] = "literal_rims"

@dataclass(frozen=True)
class TwoPadApproximation:
    lower_thickness_um: float
    upper_thickness_um: float
    evidence: str
    kind: Literal["two_pad_approximation"] = "two_pad_approximation"

GeometryHypothesis = LiteralRims | TwoPadApproximation

@dataclass(frozen=True)
class Study:
    reference: Design
    candidate: Design
    condition: SharedCondition
    requirement: GapRequirement
    samples: VolumeSamples
    hypotheses: tuple[GeometryHypothesis, ...]

@dataclass(frozen=True)
class StudyDraft:
    # Missing requirement or candidate is permitted only in an editable draft.
    document: dict
    missing_fields: tuple[str, ...]
    origin: ImportOrigin

@dataclass(frozen=True)
class StudyReport:
    study: Study
    study_sha256: str
    native_cases: tuple[NativeCase, ...]
    analytical_samples: tuple[AnalyticalSample, ...]
    decision: Decision

def read_study(data: object) -> StudyDraft:
    raise NotImplementedError

def run_study(draft: StudyDraft) -> StudyReport:
    raise NotImplementedError
```

The domain module has two public operations. `read_study` accepts a current document or a legacy editable case. `run_study` refuses an incomplete draft. This avoids a public series of parse, normalize, migrate, prepare, judge, and finalize operations that the caller must coordinate.

`study.py` owns normalization, migration, study hashing, hypothesis transforms, analytical eligibility, sample evaluation, and decision reasons. It calls the existing public solver directly. One read of that file explains what a study means. Model and engine mechanics remain behind their existing interfaces.

`__main__.py` adds `/api/study` and `study FILE --output ARCHIVE`. It handles transport, body limits, computation locking, and exit codes. It does not assign recommendation states.

`web/study.html` and `web/study.js` own the focused document editor and report rendering. The existing force viewer receives a navigation link. This adds a small page rather than adding study booleans and a second footprint to the current thousand-line `app.js`.

`artifacts.py` accepts study metadata and two source footprints through one optional study argument. The archive reader recognizes that document but continues to regenerate trusted native inputs. Ordinary old archives remain readable.

## Boundaries that prevent plausible wrong studies

Every arm stores its original footprint and selected pad. The lower diameter always derives from that arm's imported copper geometry. It is never an independently editable number that can disagree with a displayed footprint.

`import_footprint` must expose copper-rim eligibility separately from circular shape support. A negative effective solder-mask margin, a mask opening smaller than copper, or an unresolvable custom mask definition prevents the study from treating that pad as a pinned copper rim. A larger simple mask opening can establish geometric clearance but cannot establish physical wetting or pinning. The user still declares the model assumption.

The parser must consider inherited footprint mask settings and per-pad overrides. A pad-level margin cannot be interpreted without its footprint defaults. If the footprint does not contain enough information to resolve the effective opening, the study reports unknown geometry and requires independent evidence. A `.kicad_mod` import cannot infer the final board's project settings.

The required gap has an explicit name and a source. The first version evaluates pad-face separation. It never substitutes package underbody clearance, mask clearance, or an IPC assembly acceptance criterion.

The study digest includes both source texts, selected pads, all declared sample points, the criterion, and each hypothesis. Any edit clears the report and archive immediately. An asynchronous response can populate the page only if its submitted revision remains current.

The archive contains exactly the report that the page renders. Export never reads later form values. Result replay never executes archived command text.

## Native computation and the analytical baseline

Run native Surface Evolver for the nominal volume of each arm under each declared hypothesis. Literal rims alone require two native cases. The optional approximation requires four. This stays within the current seven-case archive bound. Every nominal row keeps actual mesh, native logs, refinement status, normal-force balance, and model warnings.

For the two-pad hypothesis, add the declared lower and upper cylindrical pad volumes to the computational volume. Subtract both thicknesses from the effective solved height to obtain the reported pad-face gap. This is a paper-inspired approximation and does not represent real liquid inside metal. Permit it only with gravity disabled. That restriction avoids silently assigning gravitational body force to fictitious solder inside upper copper. A later physically justified force correction would need separate evidence.

Place the published Eq. 9 spring correction in one pure helper behind `study.py`. Reuse `spherical_gap_mm` for the unloaded shape. For analytical rows, show the exact formula, source, applicability tests, and the nominal difference from native computation.

The formula is an aligned, small-load approximation. Require zero offset, gravity disabled, positive stiffness, and a declared numerical small-load screen. A provisional screen such as spring displacement below five percent of unloaded height is an implementation policy, not a published accuracy bound. Store that policy in the report. Outside it, report analytical results unavailable. Native nominal computation remains available.

Evaluate the three declared volume points per arm with the formula only when it is eligible. The UI labels these rows **Analytical sampled sensitivity**. It must not mix them into the native mesh table or call their extrema a physical interval. If sample-screen policy is not supported by nominal native agreement, suppress its threshold interpretation and show the discrepancy.

The nominal native comparison remains useful outside the analytical screen. The report then says that volume sensitivity was not evaluated. It cannot claim that the decision survived the volume range.

The report identifies a conditional advantage, not manufacturing approval. It has explicit states for numerical failure, unsupported model scope, assumption sensitivity, insufficient separation, and a nominal conditional margin. Each inconclusive state names the missing evidence and preserves the actual numbers.

## Exports and replay

`study.json` is the normalized editable input document. It contains no computed mesh, measured outcome, or engine commands.

`decision.json` records the study digest, state, threshold, nominal margins, tested sample extrema, disagreements between hypotheses, and exact reasons. It states that physical process accuracy remains unqualified.

`decision.html` is a static printable report. It uses only escaped text and local inline styling. It contains no executable script. A lab can inspect the comparison without starting SolderShape.

`samples.csv` records arm, hypothesis, liquid volume, calculation method, gap, threshold difference, eligibility, and limitations. Failure rows remain rows.

`footprints/reference.kicad_mod` and `footprints/candidate.kicad_mod` preserve both imported designs. Native cases use the existing per-case evidence format. The manifest hashes every member.

Replay verifies hashes, normalizes `study.json`, regenerates the native requests, recomputes every nominal native result, and recomputes the analytical table. It compares the new report state and margins within declared numerical tolerance. It never trusts a stored conclusion as an input.

## Acceptance checks

1. Open a current 220 versus 270 micrometer study. Verify distinct lower diameters, both footprint hashes, a common upper pad, and the explicit 185 micrometer requirement. Complete actual native computations and inspect both meshes.
2. Add the two-pad approximation using the coupon's planning inputs. Require an assumption-sensitive state when the threshold outcomes differ. Show the planning-only provenance beside those inputs. Do not count this as physical validation.
3. Submit a circular copper pad with a smaller effective mask aperture. Require an unsupported-boundary result before any native process starts. Repeat with inherited footprint mask margin and a per-pad override.
4. Open a legacy case with an upper-pad or volume baseline. Verify both arms preserve the old parameters and source. Require entry of a gap criterion before the new study can run.
5. Change the requirement or either source while a computation is pending. Verify old results, nominal margins, and downloads clear. Verify the late response is discarded.
6. Download, extract, and replay the actual archive in a clean temporary directory. Verify both original footprint hashes, all native requests, the static report, and the decision state. Tamper with one footprint and require integrity rejection.
7. Give the formula an offset, gravity, or a large load. Require explicit ineligibility. Native nominal results cannot silently become a tolerance study.
8. Force one native arm to fail. Keep that failed arm in the archive and require an inconclusive report. A successful other arm cannot determine a winner.

## Tradeoffs accepted

- We accept a separate browser page in exchange for a complete study editor that does not overload the force-viewer state.
- We accept a three-point analytical screen in exchange for a bounded first implementation. The screen cannot certify every value between endpoints.
- We accept a gravity-off restriction on the optional effective-volume hypothesis in exchange for avoiding an unjustified upper-metal force correction.
- We accept a new study document in exchange for direct ownership of two footprint revisions and their criterion. The legacy importer is the only migration boundary.
- We accept an inconclusive outcome when geometry or evidence cannot resolve the decision. The product still identifies the experiment worth buying.

## Alternatives considered

Expanding the force viewer's saved reference to a full second case exposes study conditions, per-arm geometry, and decision rules inside a UI organized around forces and offsets. That adds less HTML, but makes the user coordinate which fields are shared and which belong to the reference. The separate study document hides those choices behind one submission.

A general scenario matrix lets users add arbitrary materials, criteria, hypotheses, and joint counts. It hides loop mechanics but exposes too much experimental design. The current demonstrated task needs two revisions, one gap criterion, and a finite volume screen.

A formula-only spreadsheet is the strongest cheap competitor for the aligned coupon. It wins if the user only needs nominal aligned height. SolderShape earns its added work only if both imported revisions, explicit assumption reversals, native nonzero-offset checks, and an independently replayable report reduce lab or colleague handoff work. That advantage remains a product hypothesis.

## Synthesis decision

The parent will compare this candidate with the independent candidate. No other candidate was read for this design.

## Risks and next implementation step

The two-pad approximation may deserve only a lab-study appendix rather than a main product control. A customer may value a spreadsheet more than a native solver. Physical validation and practitioner demand remain unresolved by this design.

Start with `study.py` and a 220 versus 270 micrometer fixture. Prove the input document, hypothesis reversal, and archive replay before adding the browser editor.

Model the Domain changed the organizing structure to one study containing both revision inputs and one criterion. Laziness Protocol kept the runtime to the existing local server and native solver. Prove It Works required real nominal native cases and extracted archive replay.
