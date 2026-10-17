# Independent adversarial review B

Intent is to tighten accuracy and deliver a useful two-footprint decision-to-test workflow. Physical qualification, solver superiority and a proven commercial moat remain outside the demonstrated evidence. This review uses the configured inherited model. It is not independent across model families. The reviewed work starts at `f2cfd9b`.

## Findings

### 1. Warning. Native and analytical nominal answers can straddle the criterion while the decision says unchanged

Location is `soldershape/study.py:156` through `soldershape/study.py:178`.

The nominal agreement tolerance can accept a discrepancy that reverses the actual question. `_decision` then classifies the criterion only from analytical sample margins. It does not include the native nominal margins. An unchanged-samples conclusion can therefore coexist with a different native nominal answer.

This was reproduced with actual retained native computation. Open `output/refined-pad-review.zip`, read `study-report.json`, retain its first two literal-rim results, set `two_pad` to null and `volume_fraction` to zero, and change the criterion to 223.33 micrometers. `_report(read_study(study), results)` returns `screened_samples`. The Reference native gap is 223.31880160132934 micrometers. Its margin is minus 0.01119839867067 micrometers. The analytical gap is 223.34907200981604 micrometers. All three Reference analytical samples have a positive 0.01907200981603 micrometer margin. The 0.03027040848670 micrometer discrepancy passes the generic nominal agreement check.

The root cause is using a general method-agreement tolerance as sufficient permission for a threshold interpretation. This is a conditional decision defect, not a demonstrated physical accuracy failure. Include native nominal threshold answers in the decision. Also treat insufficient separation near the stated numerical comparison tolerance as unresolved instead of an unchanged conclusion. The selected design judgment explicitly called for an unresolved interpretation near the criterion.

### 2. Warning. A completed freeze can still seal altered archived inputs

Location is `coupons/tools/analyze.py:295` through `coupons/tools/analyze.py:310`.

The immutable source snapshot corrects edits to the source worksheets after their read. The files written into the freeze directory remain mutable during native computation. The completed manifest hashes their eventual contents without comparing archived `inputs.csv` and `metadata.json` back to the authoritative snapshot. Existing final checks cover source code, experiment and allocation, but omit these two archived files.

A synthetic counterexample used the actual `AnalysisChecks` fixture and its explicitly synthetic native double. A wrapper around `generate_predictions` changed the newly archived `inputs.csv` cap masses from 14 to 28 mg after calculation and before manifest creation. `freeze` completed. `verify_freeze` returned successfully. Archived mass was 28 mg. The retained request load remained 6.864655 micronewtons. Deriving the request from that archive gives 13.729310 micronewtons.

This requires an edit in the output directory during freeze rather than an edit to the ordinary input worksheet. It is a narrower concurrency boundary than the repaired source race. Check all four archived snapshot files against their authoritative bytes before completing the manifest. Derive those manifest digests from the snapshot. A changed archive should leave partial receipts without a completed, internally contradictory freeze.

### 3. Warning. The standalone decision brief omits the values that define its assumptions

Location is `soldershape/study.py:243` through `soldershape/study.py:268`.

The static brief includes lower diameters, calculated gaps, sample volumes, requirement, declarations and source hashes. It omits the upper diameter, normal load, surface tension, density, offset, gravity flag and both finite-metal thicknesses. It also omits the two-pad evidence declaration. A colleague reading only the advertised printable brief cannot see the physical values behind the conditional result or the 35 plus 35 micrometer mapping that reverses this example.

The actual exported `decision.html` contains neither `6.864655` nor `0.48` nor `0.28`, despite these being the declared load, surface tension and upper diameter. There is no parameter table or metal-thickness declaration in the HTML construction. The complete values do remain available in the accompanying JSON. This is a handoff completeness gap rather than lost archive data.

Render the normalized common parameters and optional finite-metal inputs, with units and their evidence declaration, in the static brief. This reuses existing study data. It does not require another model or UI control.

### 4. Warning. Study provenance does not identify the Python model or decision implementation

Location is `soldershape/study.py:286` through `soldershape/study.py:291` and `soldershape/study.py:335` through `soldershape/study.py:345`.

The actual study manifest identifies the application and hashes archive members. Per-result engine metadata identifies the upstream source and compiled binary. Raw generated Evolver models and commands are retained. Neither the manifest nor the report records source hashes for `soldershape/model.py`, `soldershape/solver.py` or `soldershape/study.py`. The selected design judgment explicitly required model and solver source hashes.

Replay's `exact_engine_provenance` is accurately limited to the upstream engine. It must not be interpreted as complete application provenance. A changed Python model generator or force extraction path can retain the same upstream hashes. A later implementation cannot identify the original Python revision from this archive alone.

Add a compact application-source identity record to the study artifact and distinguish matching application identity from numerical equivalence. Preserve numerical replay across changes. Do not execute archived source. Source identity records are evidence rather than an authentication mechanism.

## Decision-trail and claim audit

The five recent `decisions.tsv` rows describe a started refinement, rejected solver moat, selected design, mask repair and coupon repair. Their cited files exist. The design score is B18 versus A15 in `refinement/design-judgment.md`. The recent coupon test count refers to software fixtures and fabrication checks. It supplies no physical observations. The broad wording about authoritative snapshots needs the boundary correction in finding 2 before claiming immunity to edits in the freeze directory.

`refinement/POSITIONING.md` explicitly identifies customer value as a hypothesis. It claims no current customers, paid outcome, lab relationship, proprietary dataset, exclusive solver or durable moat. Its proposed five-practitioner gate is labeled a proposed business rule. No contrary customer evidence was found in this review. The current physical limitations and simpler analytical alternative are retained. No new claim of physical qualification was found.

The artifacts support a narrow design-to-test workflow hypothesis. They do not establish that a practitioner saves an iteration or that an external lab can achieve the proposed metrology. The default 185 micrometer example remains assumption-sensitive under the actual retained native results. Neither pad becomes manufacturing-safe from this software review.

## Verification scope

Inspected the current study backend, browser state and rendering, HTTP and CLI integration, importer change, coupon snapshot and scoring changes, existing archive reader, relevant focused tests, native study archive and decision trail. Reproduced findings 1 and 2 with the actual report constructor and freeze verifier respectively. Inspected exported static HTML and manifest for findings 3 and 4. No product or test code was changed. No external messages, physical experiments or competitor software runs occurred.
