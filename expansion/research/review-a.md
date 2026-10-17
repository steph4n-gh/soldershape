# Independent engineering review A

Reviewed the user attachment, workflow, selected design contract, four-concept judgment, Comment Sicko report, force protocol, procedure, uncertainty discussion, BOM, RFQ, analyzer, tests, editable CAD and neutral exports. This was a fresh read-only same-family review. No application, protocol, CAD or test source was changed.

Analyzer source reviewed and exercised has SHA-256 `0eab74f303f57ff5c47d92a0bca978cebd3323cc638b69d92a41e508a1274707`. Findings below apply to that exact source. CAD owners were still editing while this review ran, so CAD checks are a bounded intermediate snapshot, not final release verification.

## Findings requiring repair

### A1. Shared sources across force and input budgets lose their covariance

Priority 1. `force_lab/tools/analyze.py:210-213`, `:414`, and `:418-420` parse two source sets separately and combine their variances as independent. The same physical uncertainty source ID can occur in both files without reconciliation. The procedure explicitly asks for shared temperature, geometry and calibration sources. A corrected measured force and the predicted force can therefore depend on the same source, with opposite sensitivities. Their residual uncertainty then exceeds the independent quadrature result.

Executed this synthetic counterexample using the existing test fixture. No physical observations were invented or acquired.

```python
from force_lab.tests.test_analysis import ProspectiveForceBehavior
from force_lab.tools import analyze as a
c = ProspectiveForceBehavior('test_synthetic_exact_forces_support_only_declared_endpoints')
c.setUp()
try:
    p = c.source / 'input_covariance.json'
    d = a.read_json(p.read_bytes())
    d['components'].append({
        'id': 'shared-temperature', 'standard_u': 1,
        'evidence': 'SYNTHETIC common temperature source, u=1 K',
        'coefficients': {r['specimen_id']+'.volume_mm3': -.00002
                         for r in c.assignments}})
    a.write_json(p, d)
    p = c.source / 'calibration.json'
    d = a.read_json(p.read_bytes())
    d['components'] = [{
        'id': 'shared-temperature', 'standard_u': 1,
        'evidence': 'SYNTHETIC same temperature source, +1 uN/K',
        'coefficients': {r['specimen_id']: 1 for r in c.assignments}}]
    a.write_json(p, d)
    c.freeze()
    report = a.score(c.freeze_path, c.outcomes(), c.root/'score', c.sha)
    normal = [x for x in report['endpoints'] if x['kind']=='mean_normal_force'][-1]
    print(report['overall_status'], normal['combined_decision_guard_uN'])
finally:
    c.tearDown()
```

Observed `supports_declared_force_endpoints_only` and normal guard `2.8285300710346983` µN. The synthetic normal volume Jacobian is 50,000 µN/mm³. The residual coefficient for the one shared source is `1 - 50000*(-0.00002) = 2 µN/K`, giving expanded uncertainty 4 µN before numerical allowance. The actual combined guard therefore fails the declared 3 µN gate. The source does not average down because it is common to all specimens.

Repair at the source boundary. Either represent joint named source coefficients and calculate measured-minus-predicted weights before squaring, or reject this experiment format whenever cross-domain independence cannot be independently established. If IDs are merged, inconsistent units or standard uncertainties for one ID must be rejected. Fix both individual residuals and aggregate endpoint guards. Keep marginal input and measurement uncertainties for their separate precision gates. Add controls for shared positive, negative and cancelling sensitivities.

### A2. Plan verification accepts false decision targets and budget conclusions

Priority 2. `force_lab/tools/analyze.py:528-552` verifies listed receipt bytes, central forces and some Jacobians, but does not independently derive the planning targets or scenario conclusions. It does not verify that sensitivity qualification flags match receipts either. A false decision conclusion can pass the advertised planning verification.

Executed reproduction:

```python
from force_lab.tools import analyze as a
from pathlib import Path
import tempfile, shutil, json
with tempfile.TemporaryDirectory() as d:
    p = Path(d)/'plan'
    shutil.copytree('force_lab/planning/native-120', p)
    f = p/'plan.json'
    report = json.loads(f.read_text())
    report['planning_targets']['lateral_contrast_uN'] = 99999999
    report['planning_budget_scenarios']['initial_budget_negative_control']['normal_gate_passes_local_screen'] = True
    f.write_text(json.dumps(report))
    print(a.verify_plan(p))
```

Observed success status `PLANNING_BYTES_AND_JACOBIANS_VERIFIED_NOT_PHYSICAL_VALIDATION`, despite the overwritten contrast and false pass for a known failed allocation. The modified plan SHA was `c894f0bac691b617499593347e874c3971cb3b7db04d4ec71ecc14fc39646d78`; unmodified plan SHA was `6229192b5f7b20919beda0532dcf010d54b0259a2b9f8b94b4b05d464332110d`.

Centralize the pure derivation of qualification flags, sensitivities, targets and scenario results from the bound raw requests/receipts and protocol, then require exact equality during verification. Verify expected request perturbations, schemas, statuses and complete member sets as well as the arithmetic. This can reuse existing native receipts if their original source identity is preserved and the new derivation step records its own identity. Do not relabel old receipts as computations from revised code.

### A3. Confirmation scoring cannot bound transverse misalignment

Priority 2. `OUTCOME_COLUMNS` at `force_lab/tools/analyze.py:25` and coordinate checks at `:403-410` only consume x offset and gap. The model and allocation assume zero transverse displacement, while the raw-record procedure correctly asks for transverse offset. There is no frozen y target/uncertainty or actual y observation in the scoring contract. A bridge displaced 40 µm in y can still be scored against the x-only request.

Executed a synthetic control with every `measurement_evidence` reference explicitly stating `y_offset_mm=0.040`, all existing numeric columns unchanged. The existing exact-force control still returned `supports_declared_force_endpoints_only`. The issue is the missing numeric boundary, not an expectation that evidence text should be parsed.

Smallest repair is a prospectively declared near-zero transverse alignment gate. Add independently observed transverse offset and expanded uncertainty, require a conservative bound such as `abs(y)+U_y <= 0.5 µm` if justified by the local force budget, and mark missing or failed observations inconclusive. Include the transverse bound in frozen commissioning evidence and actual outcome checks. A new two-dimensional solver interface is unnecessary for this protocol. The gate must be described as an apparatus-domain bound, not proof that an arbitrary y displacement is equivalent to the current x force.

## Checks that passed

`python3 -m unittest force_lab.tests.test_analysis -v` passed all 14 tests in 0.615 s. These synthetic tests cover blank input rejection, prospective outcome rejection, same-byte snapshots, shared bias within one budget, registered-digest tampering, force sign inversion, missing wetting/stability, duplicate specimens, opposing block biases, geometry drift and missing uncertainty. They do not address A1-A3.

`python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120` passed for the unmodified 20-request planning record. Its claim is numerical integrity, not physical validation.

Using the pinned local CadQuery environment, independently reimported all four assembly STEP files. Each contained 15 valid solids. The actual lower island top was z=0 and upper island bottom z=0.150 mm. Distances along island, cap, hot bond, stalk, cool bond and cool tab were zero within 1.4e-15 mm. The missing sensor interface, accepted thermal performance and full contact-line visibility remain explicit laboratory gates, so they are not falsely presented as established capability.

The CAD model snapshot had SHA `25c6f9137bb5a1107d008a7121e6d9c0020d4535d87aa1b338e60fb699c58896`. A hardware manifest check caught the actively edited `build_cad.py` differing from its recorded digest. This is not a separate defect while its owner is still regenerating artifacts, but the final package must run and pass the complete final-source CAD verifier after edits stop.

## Scope and disposition

The existing published-data failure and physical customer demand remain unqualified. The quote-stage language, prohibition on fabrication release, independent specimen allocation, retained failures, separate scalar axes, supplier moment limits, actual-rim metrology and material-input independence are appropriate bounds. A prospective hash is correctly described as local integrity rather than an external timestamp. No lab was contacted and no purchase or physical test was performed.

A1-A3 require implementation repair and fresh independent verification before the local handoff can be called complete. This report does not assess the browser implementation or establish cross-model agreement.
