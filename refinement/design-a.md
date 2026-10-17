# Candidate A. Extend the existing reference case

## Usage

An assembly process engineer imports a KiCad footprint with a 220 micrometer copper pad. The engineer records the proposed 270 micrometer lower diameter in a field beside the source diameter. The source remains unchanged. The interface calls this a proposed diameter revision and shows both dimensions. Saving a reference captures all three design variables. These are lower diameter, upper diameter, and liquid solder volume.

The engineer sets the supported normal load and a required pad-face gap of 185 micrometers. The engineer declares a volume scenario of plus and minus five percent. A separate geometry assumption can include both measured metal thicknesses. The browser sends one complete case to the existing compare operation. The service recomputes both native geometries and returns the decision review. The browser renders that review without deriving its own verdict.

The result says which designs exceed the requirement under the nominal model. It also lists the declared scenarios that reverse that conclusion. A reversal produces an inconclusive design decision and names the assumption that needs measurement. An unchanged scenario result says that the design is insensitive to these tested scenarios. It never says that the design is physically qualified.

The engineer downloads the editable case and reproducible bundle. A colleague can see the imported pad, the proposed revision, the shared conditions, the threshold, and every scenario. Existing replay recomputes the two actual native requests. A small review replay addition also regenerates the decision summary from the editable case. The archived analytical values do not become manufacturing evidence.

Real caller sketches follow.

```python
case = parse_case(json.loads(Path("pad-revision.json").read_text()))
results, comparison = calculate_comparison(case)
Path("pad-review.zip").write_bytes(
	make_bundle(results, case.footprint_text, case.to_dict(), comparison)
)
```

```javascript
const response = await api("/api/compare", editableCase());
renderComparison(response.comparison);
// renderComparison displays the service's status and reasons.
```

```sh
python3 -m soldershape replay pad-review.zip
```

## Problem and current ownership

The current `soldershape.case.v1` stores one source footprint and one selected pad. Its reference captures only upper diameter and volume. Both designs therefore share the selected lower diameter. Changing the selected pad also clears the reference. This prevents the browser from executing the actual 220 versus 270 micrometer lower-pad comparison.

`model.py` validates the footprint and editable case. `__main__.py` currently owns comparison policy, transport, and native dispatch. `artifacts.py` already exports each actual request, native receipt, mesh, editable case, and comparison. `app.js` already invalidates old results when inputs change and discards in-flight responses from obsolete revisions. These mechanisms are useful and should remain.

The current importer checks circular copper geometry but does not inspect mask margins or inherited board settings. Its displayed assertion that the copper edge is a pinned, fully wetted boundary is stronger than the parsed evidence. A native numerical pass cannot repair that inference.

## Data shape

The domain object is a case containing two proposed designs under one set of shared conditions. The imported pad supplies provenance. It does not silently constrain both proposed lower diameters to the same value. One service module owns the review policy.

The serialized v2 case has these fields.

```text
schema = soldershape.case.v2
footprint_text
pad_index
candidate = {lower_diameter_mm, upper_diameter_mm, volume_mm3}
baseline = null or {lower_diameter_mm, upper_diameter_mm, volume_mm3}
conditions = the existing material, offset, gravity, and vertical-condition fields
review = {
	required_pad_face_gap_mm = null or positive number,
	volume_fraction = number between 0 and 0.20,
	metal_thickness_mm = null or {lower, upper},
	copper_rim_evidence = null or nonempty text
}
```

The server derives the source footprint hash, selected source diameter, and every native request hash. A client cannot claim a different source hash. The design revision is the difference between source diameter and proposed diameter. No separate revision flag can disagree with those dimensions.

`conditions` accepts either prescribed gap or supported load, as the existing `JointSpec` and `LoadSpec` do. It contains neither diameter nor volume. A gap requirement on a prescribed-gap case does not count as a predicted-gap decision. The service returns an instruction to use supported load.

Sketch signatures follow. Bodies remain unimplemented until synthesis.

```python
@dataclass(frozen=True)
class Design:
	lower_diameter_mm: float
	upper_diameter_mm: float
	volume_mm3: float

@dataclass(frozen=True)
class ReviewSpec:
	required_pad_face_gap_mm: float | None
	volume_fraction: float
	metal_thickness_mm: tuple[float, float] | None
	copper_rim_evidence: str | None

@dataclass(frozen=True)
class Case:
	footprint_text: str
	pad_index: int
	candidate: Design
	baseline: Design | None
	conditions: dict
	review: ReviewSpec

def parse_case(data: object) -> Case:
	raise NotImplementedError

def calculate_comparison(case: Case) -> tuple[list[dict], dict]:
	raise NotImplementedError

def review_comparison(case: Case, results: list[dict]) -> dict:
	raise NotImplementedError
```

The existing Python domain has runtime-validated dataclasses. This candidate follows that convention. It does not add a model library or validation framework.

## Decision and sensitivity policy

`review_comparison` owns a small, explicit sequence of tests. The sequence gives one primary reason and preserves all supporting reasons.

1. Missing reference, threshold, or copper-rim evidence returns `incomplete` with the missing fields. No physical verdict appears.
2. Known mask-defined geometry is unsupported. A negative effective mask expansion cannot be overridden by a copper-rim declaration.
3. Any failed numerical check or model warning returns `inconclusive`. The service preserves both native result records.
4. A prescribed-gap input returns `inconclusive` for predicted clearance. Its force comparison remains available under its existing scope.
5. A supported-load result reports each nominal predicted pad-face gap and signed margin against the requirement. The criterion uses the declared nominal model.
6. The aligned small-load analytical screen evaluates nominal volume and the two declared volume scenarios. If metal thicknesses are supplied, it also evaluates the two-pad equivalent-volume hypothesis at each of those volumes. Those are named discrete scenarios, not a statistical interval or a guarantee over a continuous input range.
7. A scenario that changes either design's above-or-below result makes the design decision `inconclusive`. The response names volume or geometry mapping as the next measurement target. Otherwise the response says `screened_under_declared_scenarios` and repeats that process accuracy is unqualified.

The analytical screen uses the published spherical geometry and load correction already documented in `evidence/model-repair/science-review.md`. It must use identical diameter, load, volume, and geometry mapping to its comparison row. Do not label the unloaded sphere as the strongest comparator when the load correction is available.

The screen accepts zero lateral offset and a light-load regime. It rejects a predicted linear compression greater than one percent of the unloaded effective height. This one percent limit is a declared numerical screening convention. It is not a physically validated limit. Gravity-enabled native results can still appear, but the analytical screen explicitly excludes gravity and the review reports that mismatch. Nonzero offset returns `sensitivity_unavailable` and an actionable request for native scenario runs outside this narrow first version. Neither case receives an unchanged-assumptions decision.

The two-pad equivalent-volume calculation adds both pad-cylinder volumes and subtracts both thicknesses from the resulting effective gap. It is a competing approximation, not a correction known to be true. This first version does not add native mapped meshes. Such meshes contain an equivalent capillary domain and could be mistaken for actual solder volume. Native exports remain the exact literal-rim requests that produced them.

The service includes the following information in its returned review.

```text
status
qualification = process_accuracy_unqualified
required_pad_face_gap_mm
source_pad = {footprint_sha256, pad_index, identifier, diameter_mm}
designs = two records containing proposed dimensions and nominal native margins
scenarios = records containing design, method, volume scale, mapping, gap, margin
reversals = records containing design, scenario, and the changed criterion result
next_actions = concrete missing measurements or scope checks
```

No probability, yield, lifetime, assembly time, or monetary savings appear. No automatic recommendation follows from the smaller nominal native error.

## Mask boundary and traceability

Extend the footprint parse result with declared mask information from the footprint and selected pad. Explicit pad values override explicit footprint values. Preserve unknown inherited board settings as unknown. A standalone footprint cannot establish the board's final mask opening.

Reject an explicitly negative effective mask margin as a copper-rim input. Do not replace the copper diameter with the mask opening and keep the old pinned-copper interpretation. Require a nonempty evidence declaration for unknown inherited settings before comparison. The declaration should refer to the actual board mask opening or fabrication output. The UI shows that a declaration is user-supplied evidence, not independently verified geometry.

Keep unsupported pads visible with the rejection reason, as today. A saved reference survives edits to the proposed diameter. It is cleared when the imported footprint or source pad changes. This keeps the current one-source interaction and prevents stale source associations.

## Module map and minimum changes

- `model.py` owns `Case`, `Design`, `ReviewSpec`, mask metadata, and the sole v1 import migration. Its source request builder gains a validated proposed diameter argument. Ordinary CLI solves continue to use the source diameter by default.
- A new `decision.py` owns the analytical formula, scenario generation, eligibility rules, threshold comparisons, and actionable review reasons. Its pure review function does not access the HTTP request or browser state.
- `__main__.py` resolves both designs to native requests and invokes `decision.py` once. It moves the existing comparison policy into that owner rather than adding a second competing policy path.
- `artifacts.py` preserves its bundle structure. `comparison.json` becomes the complete decision record. Replay adds a regeneration check for a v2 comparison when an editable case is present. Native request replay remains unchanged for old bundles.
- `app.js` reads the proposed lower diameter and review fields. Its existing `invalidate()` owns stale result clearing for all new fields. Reference capture includes all three design values. The browser displays service reasons and never reimplements eligibility or thresholds.
- `index.html` replaces the current unconditional pinned-edge assertion with source geometry and boundary-evidence controls. It names the user job as a pad revision and gap-assumption review.

The public operation remains one compare call. It hides native dispatch, scenario policy, threshold tests, provenance generation, and artifact preparation. The user still supplies the design question and assumptions because the program cannot observe these facts.

## Reversible migration

Read both v1 and v2 at `parse_case`. Always emit v2. On v1 import, derive both lower diameters from the selected source pad. Copy the candidate upper diameter and volume from `parameters`. Copy the baseline's upper diameter and volume into the new reference. Put the remaining parameters into `conditions`. Initialize the requirement and boundary evidence as missing. Do not invent a decision criterion or claim that a historical case already had evidence.

The normalized case response includes a migration notice listing these defaults. Existing files are never rewritten in place. Existing native bundles remain replayable because their `input.json` format is unchanged. Existing single-joint and sweep routes retain their request shapes. Remove the v1 save path from the browser in the same change so there is only one new saved representation.

Case size does not double because one source footprint is retained. Keep the existing footprint size limit and derive a bounded full-case limit that accommodates the small review fields. Explicitly cap evidence text length. Do not lift the footprint size limit as an incidental migration change.

## Acceptance cases

1. Open a real circular-pad footprint at 220 micrometers. Save the reference, change the proposed lower diameter to 270 micrometers, and compare under the same load. Inspect the two actual native `input.json` files in the downloaded archive. They must contain 0.22 and 0.27 millimeters. Their source hash and source index must match. Their actual request hashes must differ.
2. Use the published aligned 220 versus 270 micrometer study assumptions, a 185 micrometer requirement, and a declared five percent volume scenario. The 270 micrometer design changes from above the nominal requirement to below it under the low-volume screen. The decision must be inconclusive and name volume as a measurement target. Verify analytical values independently against the existing frozen campaign. Do not derive expected values from the new helper.
3. Use the coupon's two-pad thickness scenario. If the geometry mapping reverses the criterion, preserve both named scenarios and return inconclusive. Never silently replace the literal-rim nominal result with the hypothesis that passes.
4. Import a circular copper pad with an explicit negative pad mask margin. Repeat with a negative footprint margin inherited by the pad. Both must reject the copper-rim comparison even if the user provides a declaration. A positive pad override must follow the explicit inheritance rule.
5. Import a footprint with no explicit mask settings. No comparison can claim known copper-rim applicability until evidence is recorded. The case export must preserve the evidence declaration and its user-supplied status.
6. Change the threshold, volume scenario, proposed diameter, metal thickness, or boundary evidence after computation. The result table and bundle download clear immediately. Change one of these during a running comparison. Its old response must be discarded.
7. Save and reopen v2. Candidate, reference, conditions, review, and source identity must round-trip. Open an unchanged v1 example. Its two native requests must match the old normalized inputs, while the new decision state remains incomplete until the missing review fields are supplied.
8. Download a real comparison bundle and run native replay from a fresh process. Regenerate the review and compare the scenario inputs, margins, reversal list, and source hashes. Alter a threshold without updating the archive manifest. Existing integrity verification must reject it.
9. Use nonzero offset, gravity, failed native geometry, missing boundary evidence, and prescribed gap as negative controls. Each must return its specific limitation. None can produce the unchanged-scenarios decision.

## Tradeoffs accepted

- We accept one imported source per case in exchange for a small extension to the current workflow. Different footprints require separate cases. Proposed diameter revisions remain explicit and auditable against the original source.
- We accept an analytical scenario screen in exchange for fast review without a second simulation campaign. The product labels its excluded physics and discrete scenarios directly.
- We accept conditional screening instead of a manufacturing recommendation because the physical validation campaign has not qualified the process model.
- We accept a user evidence declaration when board-level mask settings are unavailable. Known contradictory mask geometry remains a hard rejection.

## Alternatives considered

A separate study builder with arbitrary scenario lists would support more process variables. It exposes scenario orchestration and provenance linking to the caller. It duplicates the existing editable case and comparison workflow for this first useful job.

Two full footprint snapshots per case support arbitrary board revisions. They add independent pad selection and source replacement states, double source storage, and complicate old case migration. The current demonstrated comparison changes one circular lower diameter. Explicit revisions against one imported pad satisfy that requirement with fewer states.

Native solves at every scenario corner would avoid an analytical applicability boundary. They multiply runtime and produce many meshes for a question the existing aligned formula already answers. They should be added only for an evidenced nonzero-offset decision whose cost and useful distinction are demonstrated.

## Red flag screen

The browser owns edit state. The service owns policy. The solver owns numerical evidence. No module derives a second copy of the decision status. Scenario generation and decision evaluation stay together in `decision.py`. The compare operation is deep enough to complete the user's review in one call. The only compatibility branch is the input migration boundary. There is no generic scenario framework, plugin registry, persistence service, or material catalog.

## Synthesis decision

Pending the parent's independent candidate comparison. Candidate A proposes the existing reference-case workflow as the base and treats every new review input as part of the same editable case.

## Remaining risks and next step

Demand and willingness to pay remain unmeasured. A coherent review workflow does not establish a moat. Its testable potential value is that a colleague can reproduce why a pad revision is inconclusive and identify the missing measurement before ordering a board.

The scope of a copper-rim declaration must stay visible. It does not establish the wetting or contact-angle regime. The analytical screen's one percent compression convention needs comparison against retained native cases before it is enabled.

Start with v2 case normalization and the diameter provenance acceptance case. That change must pass before adding the decision display.

Model the Domain changed the shape from a partial baseline dictionary to two complete designs under shared conditions. Laziness Protocol kept one imported source and one service policy owner. Both principle leaves were read for this candidate.
