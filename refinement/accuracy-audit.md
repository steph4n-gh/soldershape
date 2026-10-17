# Accuracy audit for the refinement phase

This audit starts from local commit `f2cfd9b`. It inspects the numerical model, published physical evidence, browser comparison semantics, coupon planning calculations, and the actual freeze and score functions. It changes only this report. The review uses the inherited model family. It is not a review across model families.

The product can explain assumptions and help design a discriminating experiment. It cannot yet approve a pad design. The strongest accuracy limitation is the mapping from a manufactured joint to a pinned-rim calculation. Numerical refinement is much smaller than that uncertainty. The existing external experiment also does not establish a meaningful accuracy advantage over the simple loaded analytical calculation.

## Consequential findings

### P1. A completed freeze can disagree with its own archived inputs

`coupons/tools/analyze.py` validates input CSV rows before creating the output directory. It subsequently copies the original CSV and JSON files, then calculates predictions from the earlier in-memory values. There is no comparison between the copied inputs and the values actually used for prediction. The code checks changes to prediction source, experiment, and allocation, but not this input race.

A synthetic modification at the copy boundary changed every cap mass from 14 to 28 mg. The actual freeze function completed. `verify_freeze` accepted its manifest. The archived CSV reported 28 mg while the prediction request still contained a 6.864655 micronewton load from 14 mg. The correct load derived from the archived mass is 13.729310 micronewtons.

This is an input-provenance defect. It is not physical data or a physical-model failure. A user can encounter it if a laboratory edits a worksheet while predictions are being prepared.

Copy or read a single immutable input snapshot first. Validate and calculate from that snapshot. Preserve the literal source evidence and the normalized authoritative values. Check that a completed freeze's requests derive from its archived inputs. Reject an intervening input change or make its exclusion from the completed snapshot explicit.

### P2. Accepted numeric-string metadata causes scoring to crash

`validate_metadata` accepts JSON strings `"210"` and `"2"` for temperature and its uncertainty. It normalizes them in memory. Freeze copies the original metadata instead of the normalized values. Score reloads that original metadata without normalization. Its temperature gate then subtracts a string from a float.

A synthetic fixture completed a freeze with those two strings. The actual score function raised `TypeError` with `unsupported operand type(s) for -: 'float' and 'str'`.

Either reject nonnumeric JSON values at the boundary, or retain and use normalized metadata throughout. Revalidating frozen metadata before scoring is also a small direct correction. Keep the raw submitted metadata if normalizing its representation.

### P1 capability gap. The declared input-uncertainty budget does not gate model scoring

The procedure requires input measurement capability that fits the five micrometer height budget. The executable scorer assesses central predictions and measurement uncertainty. It does not use the retained input sensitivity when determining model agreement.

A deliberately extreme synthetic input uses a 2.9 mg sphere-kit mass and expanded uncertainty of 1.4 mg. Freeze accepts it. The analytical sensitivity screen totals 80.514034 micrometers. Score still returns `liquid_model_verdict=consistent_at_frozen_inputs` when synthetic outcomes equal the central predictions.

That label states its central-input scope accurately. The report also explicitly disclaims propagated input uncertainty. This is therefore not a fabricated native confidence interval. It is a gap between the procedure's stop condition and executable eligibility. A high-level product verdict must not promote this central result to physical qualification.

At minimum, report an explicit input-uncertainty eligibility state. Fail that state when a declared conservative screen already exceeds the budget. Passing the analytical screen cannot certify native uncertainty because it omits interactions, offset, copper mapping, and correlations. A complete native uncertainty claim still requires an appropriate prospective sensitivity protocol.

## Does the proposed PCB decision survive?

Only the directional hypothesis survives both of the current coupon geometry interpretations. A minimum-clearance approval does not.

The retained planning artifact contains these actual native results. Their artificial planning assumptions are not laboratory inputs.

| Geometry hypothesis | C220 gap, micrometers | C270 gap, micrometers | C220 minus C270 | Nominal 185 micrometer criterion |
| --- | ---: | ---: | ---: | --- |
| Literal opposing rims | 223.318802 | 207.521815 | 15.796987 | Both above. |
| Two finite pad cylinders | 178.203381 | 167.313878 | 10.889503 | Both below. |

The change of geometry interpretation moves C220 by 45.115420 micrometers and C270 by 40.207937 micrometers. These are alternative physical idealizations. They are not statistical endpoints. They are far larger than the 0.0464 micrometer maximum gravity-off native versus analytical difference in this planning example.

The prior published-assembly study is a different construction. Its native 220 minus 270 difference is 11.093768 micrometers. The reported measured difference is 6 micrometers. It supports the direction in those observations. Missing source uncertainties and process details prevent a general error bound. The earlier q220 low-volume margin cannot be transferred to a custom cap with thick metal at both ends.

The reference in the main workbench also has narrower semantics than the coupon comparison. `model.parse_case` stores only reference upper diameter and volume. `__main__.calculate_comparison` uses the same selected lower board pad for both designs. The UI clears a reference after changing the selected board pad. It does not yet perform a controlled comparison of lower 220 and 270 micrometer pad designs. The README states this limitation correctly. Product claims should preserve it until the workflow changes.

## What is numerically trustworthy?

A fresh native q220 calculation reproduces the retained published-mapping result. It uses 0.22 and 0.28 mm opposing diameters, 0.01874245121768684 cubic millimeters effective volume, zero offset, 4 micronewtons external normal load, 0.48 N/m surface tension, and gravity disabled. Subtracting the declared 34 micrometer lower-cylinder correction gives 201.774372061389 micrometers.

The result is `refinement_checked`. The independent fixed-gap upward reaction is 3.999067319166 micronewtons. Its balance residual is minus 0.000932680834 micronewtons. The sampled plane excursion is zero. The independent Eq. 9 value is 201.800979849825 micrometers. Native minus analytical is minus 0.026607788436 micrometers.

This confirms a numerical replay of the specified idealization. It does not introduce an additional physical observation. The request hash is `8edd709762ff3661798cbb10c7043050524a1cb2dfe7e82c59e4ba750cbcd11d`.

The load path has a useful existing safeguard. It solves height without supplying measured height, then computes a fresh fixed-gap force balance. Failed native solves and sampled substrate-plane excursions do not receive an accepted loaded result. The finite-difference derivative and initialization checks are bounded checks on retained cases. They are not certification for every accepted parameter combination or proof of a global equilibrium.

## What is physically supported?

The [Van Veen, Vandevelde and Beyne paper](https://imapsjmep.org/article/39820.pdf) identifies screen-printed solder plus balls, a 34 micrometer NSMD lower copper pad, and an approximate 4 micronewton load. Its reference calculation adds one pad cylinder and subtracts its height. Table 3 supplies cooled cross-section heights. The paper explains the small-pad mismatch using possible misalignment. It does not identify the missing specimen uncertainties needed for this project's process qualification. The two-pad coupon construction is a new experiment.

The evidence supports the recorded four-point trend under the declared approximation. The native mean absolute discrepancy of 3.40248 micrometers and independent loaded analytical discrepancy of 3.43619 micrometers do not demonstrate a meaningful native advantage. The source's rounded loaded analytical column gives 2.825 micrometers. Its assumptions do not justify silently replacing this project's declared material input.

The [Josell et al. force experiment](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) remains a negative qualification result. The archived forward scenarios predict about 14 micrometers offset against a measured 31 micrometers under an inferred load. Matching upstream code does not resolve that physical discrepancy. No new physical sample was measured in this audit.

## Reproduce the two boundary defects and the uncertainty limit

Run this at the audited source revision. It uses the existing explicitly synthetic test fixture. It writes only temporary fixture directories. It does not call the native engine or fabricate physical observations.

```sh
python3 - <<'PY'
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

module = importlib.util.spec_from_file_location('audit_fixture', 'coupons/tests/test_analysis.py')
checks = importlib.util.module_from_spec(module)
module.loader.exec_module(checks)

def run(case):
    fixture = checks.AnalysisChecks()
    fixture.setUp()
    try:
        case(fixture)
    finally:
        fixture.doCleanups()

def changed_input(fixture):
    analysis = checks.analysis
    original = analysis.shutil.copyfile
    def copy(source, destination, *args, **kwargs):
        if Path(source) == fixture.input_path:
            for row in fixture.inputs:
                row['cap_mass_mg'] = 28
            fixture.write_csv(fixture.input_path, analysis.INPUT_COLUMNS, fixture.inputs)
        return original(source, destination, *args, **kwargs)
    with patch.object(analysis.shutil, 'copyfile', side_effect=copy):
        fixture.freeze()
    analysis.verify_freeze(fixture.output)
    saved = analysis.read_csv(fixture.output / 'inputs.csv')[0]
    request = analysis.read_json(fixture.output / 'predictions.json')['caps'][0]['models'][0]['request']
    print(json.dumps({'case': 'synthetic copy-boundary input change', 'archived_cap_mass_mg': saved['cap_mass_mg'], 'prediction_load_uN': request['normal_load_uN']}))

def numeric_strings(fixture):
    fixture.metadata.update(temperature_C='210', temperature_U_C='2')
    checks.analysis.write_json(fixture.meta_path, fixture.metadata)
    fixture.freeze()
    try:
        fixture.score(fixture.outcomes())
    except Exception as error:
        print(json.dumps({'case': 'synthetic numeric-string metadata', 'exception': type(error).__name__, 'message': str(error)}))

def input_uncertainty(fixture):
    for row in fixture.inputs:
        row['solder_kit_mass_U_mg'] = 1.4
    fixture.write_csv(fixture.input_path, checks.analysis.INPUT_COLUMNS, fixture.inputs)
    fixture.freeze()
    predictions = checks.analysis.read_json(fixture.output / 'predictions.json')
    report = fixture.score(fixture.outcomes())
    print(json.dumps({'case': 'synthetic excessive input uncertainty', 'screen_um': predictions['caps'][0]['analytical_input_sensitivity']['sum_abs_shifts_um'], 'verdict': report['liquid_model_verdict']}))

for case in (changed_input, numeric_strings, input_uncertainty):
    run(case)
PY
```

The native replay uses the public solver directly.

```sh
python3 - <<'PY'
import math
from soldershape.model import LoadSpec
from soldershape.solver import solve
request = LoadSpec(.22, .28, .01745 + math.pi * (.22 / 2)**2 * .034, 0, 4, gravity=False)
result = solve(request)
print(result['status'])
print(1000 * result['equilibrium']['standoff_mm'] - 34)
print(result['load_balance']['residual_uN'])
PY
```

## Audit identities and refinement priorities

| Artifact | SHA-256 at audit |
| --- | --- |
| `coupons/tools/analyze.py` | `c653cd2d4812837bcecc63fca386b5a6bf8b40a3f62cd8d9c724560161144683` |
| `soldershape/model.py` | `022b5187838be94d1535ffbc8132d35ee69b9c9263521e5d62c872b17a072a4a` |
| `soldershape/solver.py` | `31e551899bbd040ad78aa2e2daf489a9fa3d2295df9db3f63e90149ff631c702` |
| Native engine binary | `c930b47b33a4cafb3cf98b1c0cb7e3bd9805abcf67aceefe243daea091072f8e` |
| `evidence/model-repair/loaded-physical-results.json` | `a7b684b560021988fb464b4851fa1c232efc29d5ab3912a37e2ef2cbe0990a47` |
| `coupons/evidence/planning/plan.json` | `cbfd80822cd1c5a5be632e4cace60ca01ccf3b294d54d73c2983e9da9676c181` |

First repair snapshot integrity and normalized input handling. Encode the uncertainty stop condition before presenting a qualified decision. Keep the geometry alternatives visible beside every clearance conclusion. Use the analytical baseline wherever it reaches the same decision. A general optimizer earns its complexity only when it changes a useful decision beyond that baseline and survives independent physical checks.

Prove It Works changed this audit from inspection to three actual freeze and score counterexamples and one fresh native replay. Explain the Number kept numerical tolerances, central discrepancies, geometry hypotheses, and physical uncertainty distinct. Neither principle permits treating a passing build or a synthetic fixture as a physical success.
