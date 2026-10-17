# C220 and C270 uncertainty design

This is an independent design candidate grounded at `33666d32c92b6753925bb2fd29dc62ce5fed618b` on 2026-10-16. It is an explanation for the pre-lab phase. No production code, frozen evidence, or laboratory inputs were changed. The only calculations in this design pass are the existing standard-library Eq. 9 approximation. No native uncertainty campaign was run.

## Grounding

The current experiment compares custom two-copper-end coupons. Each cap has twenty 280 micrometer pads in a five-column, four-row array. The lower pads are 220 or 270 micrometers. One screened 320 micrometer Sn63Pb37 sphere supplies each joint. A free bare cap supplies the external load. These are the construction requirements in [the experiment specification](../../coupons/experiment.json), not measurements of manufactured parts.

The software separates incoming input records, a prospective prediction freeze, and later outcome records. `coupons/tools/analyze.py` owns unit conversion, model mappings, central native predictions, the analytical comparison, and scoring. It currently propagates uncertainty through a one-at-a-time analytical screen only. Its own output correctly says that this is not a native uncertainty interval. `soldershape/solver.py` owns load-controlled equilibrium, numerical checks, and a fresh fixed-gap reaction check. The fixed-gap result must balance the requested external load.

The existing model has circular pinned rims. It does not represent pad sidewalls, substrate obstacles, wetting hysteresis, a free cap's lateral equilibrium, or twenty interacting load-bearing joints. The literal model gives a pad-face gap. The two-pad-cylinder approximation adds both metal-cylinder volumes before solving and subtracts both metal heights afterward. Those hypothetical liquid cylinders must not acquire spurious upper copper gravity. The approximation already disables gravity. Actual solder gravity is a separate literal-rim check.

The load conversion is correct. With milligrams, `Fjoint_uN = cap_mass_mg * 9.80665 / 20`. The 14 mg planning cap implies 6.864655 micronewtons per joint. The cap mass includes finish and permanent marking. It excludes solder and flux. Flux load is a missing physical input unless quantified. Equal load at each joint remains an assumption. A flat-looking cap does not measure twenty equal joint reactions.

The incoming metal mass identifies mean liquid volume through `Vjoint_mm3 = kit_mass_mg / (20 * rho_liquid_g_cm3)`. The units match because one gram per cubic centimeter is one milligram per cubic millimeter. The nominal sphere geometry has volume 0.017157284679 cubic millimeters. Combining that geometric volume with the assumed density 8.5 gives a twenty-sphere kit mass of 2.916738395 mg. That last mass is a constructed planning value. It is not an incoming measurement.

The [published four-specimen comparison](../../evidence/model-repair/report.md) is a different problem. Its effective-volume mapping adds ONE lower copper cylinder of thickness 34 micrometers to 0.01745 cubic millimeters of solder. It subtracts 34 micrometers from the effective gap. Its load is approximately 4 micronewtons per joint. Applying that mapping to this coupon would silently omit its upper copper end and change its physical problem. Keep `published_table3` outside the coupon decision table.

## The decision has three different questions

1. Does C220 have a larger cap mean gap than C270 at the same declared process conditions?
2. Does either constructed coupon keep every finished pad-face gap at or above 185 micrometers after reflow?
3. Does a declared liquid-equilibrium model predict held-out molten geometry within the five micrometer error budget?

The nominal result already separates these questions. The archived native planning values are C220/C270 of 223.318802/207.521815 micrometers under literal rims and 178.203381/167.313878 under two cylinders. C220 is higher under both. Both arms pass the nominal 185 micrometer screen under literal rims and both fail it under two cylinders. This is a model-form uncertainty greater than the material sensitivity demonstrated so far. Do not merge the models into an averaged prediction or choose the model that passes.

The 185 micrometer requirement is deliberately a pad-face gap requirement in this experiment. It is not a generic PCB underbody-clearance rule. The measured practical acceptance is `whole_cap_minimum - expanded_U >= 185`. A modeled single-joint central gap does not establish that minimum. Unknown tilt, flatness, local volume differences, and hot-to-cold transformation prevent an unconditional simulated clearance pass.

For numerical screening, record `gap - 185` and its sign. Also record `C220_mean_gap - C270_mean_gap`. Compare the latter with the declared three micrometer paired measurement budget as an indication of resolvability. A simulated difference greater than three micrometers does not validate its physical sign. Do not subtract the five micrometer model error budget as though it were an established error bound. It is a future test criterion.

## A minimal research runner

Prefer one standalone coupon-specific runner and a declarative JSON scenario table over a new solver framework. Reuse `LoadSpec`, `solve`, `engine_info`, and the existing Eq. 9 comparison. Reuse the exact coupon conversion after testing it independently with literal expected values. Keep experimental outcome files out of the runner's interface.

The organizing data shape is one paired physical scenario. It contains common inputs once, arm-specific deviations separately, and a named physical boundary interpretation. Expanding that record produces two complete immutable native requests plus their output-reference conversion. The scenario identity is separate from the native request identity because several scenarios may intentionally reuse the same native computation.

A compact shape is sufficient.

```text
Scenario
  id
  domain = actual_coupon
  purpose = nominal | common_stress | opposed_stress | branch_control
  provenance = requested_spec | planning_assumption | unqualified_stress
  common
    gamma_N_m
    rho_liquid_g_cm3
    liquid_to_solid_volume_ratio
    lower_pad_bias_um
    upper_pad_bias_um
    finished_lower_metal_um
    finished_upper_metal_um
  arms
    C220 and C270
      lower_diameter_mm
      upper_diameter_mm
      cap_mass_mg
      metal_kit_mass_mg or sphere_diameter_um with explicit volume construction
      pre_offset_mm
  boundary = literal_rims | two_pad_cylinders | explicit_pad_obstacle
  expected_requests
```

Use either a metal-mass construction or a geometric-volume construction in one scenario. Never vary sphere volume, kit mass, and liquid density as independent versions of the same uncertainty. If a volume factor directly changes the derived liquid volume, label its source and do not silently apply density to it again. A scenario cannot simultaneously claim measured liquid density and reuse `liquid_volume_equal_solid_for_geometry_check_only` as a material fact.

The public research interface can remain one command that materializes requests, runs them, and writes receipts. A second command verifies the resulting directory offline. The runner needs no plugin registry, optimizer interface, worker service, probability library, database, or product settings. The alternative of extending the prospective `freeze` command is shorter initially but mixes invented stress cases into measured confirmatory inputs. Keep the exploratory campaign separate. A future genuinely measured freeze can use its results without importing synthetic outcomes.

The explicit obstacle model must have a different source identity and raw model receipt. Its request carries actual top and bottom copper heights and obstacle definitions. It must conserve actual liquid volume. Do not represent fictitious metal-cylinder volume as a verified obstacle model. Do not rename a free-contact numerical failure into an accepted wetting hypothesis.

## Declared ranges and their status

The following ranges are candidates for the campaign. None is a measured process distribution. Check source and numerical admissibility before native execution.

| Input | Candidate range | What supports the range | Coupling |
| --- | --- | --- | --- |
| Lower and upper pad diameters | Nominal plus or minus 5 micrometers. | The requested fabrication target, including measured uncertainty, in `experiment.json`. No fabricator acceptance exists yet. | Include a common lot bias and an opposed arm deviation. |
| Sphere diameter | 317.5 to 322.5 micrometers. | Requested screened acceptance band. Measurement plus or minus expanded uncertainty must lie within it. | Include shared lot extremes and opposite kit extremes. Individual sphere placement is a later within-cap check. |
| Geometric sphere volume | 0.976745129 to 1.023621082 times nominal. | Exact cube of the requested diameter ratios. This is solid geometry, not liquid-volume validation. | Derive it from diameter. Do not sample it again. |
| Liquid-volume stress | 0.95 to 1.05 times the declared central liquid volume. | Explicit unqualified stress already used for published screening. No production tolerance or coverage probability follows. | Run common and opposed changes separately. |
| Cap mass | 11.2 to 16.8 mg around 14 mg. | Explicit plus or minus 20 percent stress assumption. The actual clean caps must be weighed. | Common cap lot shift first. Opposed arm values test sorting or site bias. |
| Surface tension | 0.35, 0.40, 0.48, and 0.55 N/m. | Previously declared unqualified material stresses. A sourced molten-alloy value and uncertainty remain required. | Shared within the same alloy, flux, atmosphere, and run. An arm-specific gamma is a separate contamination hypothesis. |
| Density | 8.5 g/cm3 nominal, with an explicit plus or minus 5 percent stress if used. | Nominal is a planning assumption. The stress width is proposed, not measured. | Shared and coupled inversely to liquid volume when mass is fixed. |
| Finished metal heights | 30, 35, and 40 micrometers per end. | Explicit unqualified geometric stress around nominal copper. Nominal 35 micrometer copper excludes ENIG. Actual finished heights are unknown. | Shared lot bias plus separate top and bottom values. |
| Pre-reflow offset magnitude | 0, 5, and 10 micrometers. | Ten micrometers including uncertainty is the prospective input eligibility gate. | Common alignment bias and opposed arm offsets. Final measured offset is never a forward input. |
| Tilt and local gap variation | No unmeasured stochastic distribution. | The experiment's guarded three micrometer gap-range gate is an eligibility limit, not an anticipated distribution. | Test a specified rigid-plane geometry separately or retain it as a gap in minimum-clearance claims. |
| Hot-to-cold transformation | Unqualified. | No source or metrology currently identifies it. | Never silently equate liquid predictions to cooled acceptance measurements. |

A broad density stress and a broad independent liquid-volume stress should appear as alternative constructions, not an unexplained double penalty. The current no-gravity loaded shape depends strongly on volume and on load divided by gamma. Density then acts through the volume construction, not as a separate force term. Add solder gravity only as its own actual-volume control.

Do not label these ranges as tolerances of a deliverable board. Requested specifications describe what the lab must demonstrate. They are not evidence it can manufacture or measure to those specifications.

## Pair scenarios before spending native requests

Start with the six exact archived native planning requests. Preserve those nominal matches before adding physical models. Then use cheap Eq. 9 evaluation to select correlated common corners, opposite-arm corners, clearance crossings, and small predicted pair differences. Confirm those selected points natively. Random sampling alone will miss narrow reversals and does not prove an interval.

A bounded first campaign can use sixteen paired scenarios under two boundary interpretations, giving sixty-four native requests, plus six nominal reproductions and dedicated controls. Expand only where numerical failure, a near reversal, or a boundary-model disagreement changes the decision. The workflow's initial 100 to 250 request allowance is a ceiling to make the question decidable, not a target to fill. The explicit-pad obstacle campaign remains separately gated by volume, force balance, and unchanged numerical controls.

The paired stresses must include these cases.

- Shared volume, gamma, density, pad bias, and cap-lot changes. These can move both absolute gaps without erasing their difference.
- Opposite arm volume and pad-diameter biases. These represent a design comparison that cannot assume every systematic effect cancels.
- Shared errors in mass calibration or image scale. Apply the same latent error once rather than treating it as two independent draws.
- Upper-pad cap-lot deviations despite the common upper-pad drawing. Different physical caps can lie at opposite acceptance endpoints.
- A deliberately broad opposite-volume case. It must be labeled outside the screened sphere-volume domain if it exceeds that domain.
- Offset and actual solder-gravity cases. Retain the analytical comparator's omitted terms visibly rather than declaring a disagreement to be a solver defect.

A small Eq. 9 screen was run in this design pass with the current implementation. All values below are computed approximations, gravity off, 35 micrometers per metal end, zero offset, 14 mg cap mass, gamma 0.48 N/m, and the nominal geometric-volume assumption unless the case changes it. The two-cylinder output subtracts 70 micrometers after adding both cylinder volumes.

| Case | Literal C220 minus C270, micrometers | Two-cylinder C220 minus C270, micrometers |
| --- | ---: | ---: |
| Nominal. | 15.829403 | 10.931731 |
| Shared liquid-volume factor 0.95. | 15.903518 | 10.892380 |
| Shared liquid-volume factor 1.05. | 15.746438 | 10.960360 |
| Opposed screened sphere and pad endpoints. | 2.841090 | 0.874730 |
| Opposed plus or minus 5 percent arm-volume stress and pad endpoints. | -4.189806 | -5.209601 |

The opposed screened case assigns C220 lower/upper diameters 225/285 micrometers and ball diameter 317.5 micrometers. It assigns C270 265/275 micrometers and 322.5 micrometers. Both arm-specific pad endpoints are inside the requested geometric specification. Physical acceptance with nonzero measurement uncertainty would put measured central values inside those endpoints. This is a boundary stress, not a probability claim. Its small pair difference is below the requested three micrometer paired measurement budget. The broader case uses liquid-volume factors 0.95 for C220 and 1.05 for C270 with the same pad endpoints. It reverses the mathematical ranking. It is not justified by the screened sphere band alone.

These cases are immediate native confirmation candidates. The native nominal comparisons already show that Eq. 9 can be within 0.047 micrometers of the coupon calculation, but that old nominal agreement cannot substitute for running the new combined cases. Before native confirmation, treat every new result above as analytical screening only.

## Source identity, accounting, and negative controls

`LoadSpec.sha256` hashes canonical physical input. `engine_info()` checks the pinned engine source identity and binary hash. `coupons/tools/analyze.py` captures loaded code hashes and rejects changed source while freezing. Its prediction cache is in-process and keyed by native request. `tools/validate_loaded.py` additionally partitions persisted receipts by extraction, model, solver, and engine identity. Those are useful mechanisms to reuse, not evidence that a new runner's output is automatically protected.

Capture the runner, conversion and summary code, scenario bytes, model and solver code, generated native model or boundary source, and engine source/binary identities before execution. Include both calculation and interpretation code in the campaign identity. Check source bytes again before a completed report is written. Reusing receipts must verify the exact request, campaign identity, engine identity, and receipt hash. An input-only cache key is insufficient across code or physical-model changes. Failure and timeout receipts are first-class expected results.

A request table must enumerate every expected native computation before execution. Verification rejects missing rows, duplicates that hide a missing scenario, undeclared requests, modified receipt inputs, a stale boundary implementation, changed numerical gates, nonfinite values, and missing failed cases. Shared native requests may be computed once but every scenario-to-request mapping must remain accounted for. Record requested rows, unique solves, reused matching receipts, successes, failures, and deliberately skipped native controls separately.

Acceptance checks should cover the following behavior.

1. Reproduce all six archived planning requests and output-plane corrections. Each accepted request requires unchanged refinement gates, no model warning, and independently balanced load.
2. Recompute reported signs and extrema from verified receipts. Deliberately edit a conclusion and require rejection.
3. Remove or alter one failed receipt and require rejection. Do not let a successful-case filter improve robustness.
4. Change scenario bytes, conversion code, boundary source, a request field, or engine provenance and require a new identity or explicit rejection.
5. Verify exact unit controls. Doubling cap mass doubles requested external load. Twenty-sphere kit mass is divided by twenty. Copper volumes and output corrections are separate and use millimeters. Adding solder weight to the cap is a negative control.
6. Reverse the opposed arms and require the paired difference to change sign. Give both arms identical geometry and inputs and require a zero difference within unchanged numerical tolerances.
7. Test zero-load spherical agreement, unchanged gamma/load scaling, force-derivative convergence, and fresh replay of nominal and decision-critical cases.
8. Preserve a deliberately unattainable load or inadmissible obstacle case as a failed numerical result. A formula prediction never rescues that native row.
9. Keep published one-cylinder requests in a distinct domain. A verifier must reject their accidental inclusion in the actual-coupon decision rows.

## Which measurements decide the remaining uncertainty

Use the Eq. 9 loaded spherical calculation as the strongest simple comparator for the aligned, small-load regime. It is already essentially as accurate as the native optimizer against the published geometry table. The native optimizer must earn its extra work through offset, gravity, finite-pad boundary effects, or a detected nonlinear branch difference. Do not claim a product advantage for reproducing the formula more expensively.

Compute a sensitivity matrix whose outputs include both arm gaps, their difference, and at least one force or stiffness observable. Scale each input column by its declared perturbation. Report nearly parallel columns and small singular values as local identifiability warnings. The no-gravity equilibrium responds to load divided by gamma. A single loaded height cannot independently identify those two quantities. Volume, wettable geometry, and a height-reference correction can also imitate one another. Better fits to one height do not identify the mechanism.

Select the next measurement by the predicted separation between competing explanations relative to its demonstrated measurement uncertainty. Boundary models currently differ by roughly 40 to 45 micrometers at nominal inputs. Direct section images of contact-line location, top and bottom finished metal height, sidewall wetting, and the actual liquid plateau gap can discriminate that cause more directly than fitting gamma. Incoming kit mass, individual sphere sizes, and a sourced molten density constrain volume independently of final height. Weighing every cap identifies external load independently of height. Those measurements remove confounding before any force experiment.

For force qualification, vary external load or displacement at several points while observing actual joint gap at the same temperature. A zero-load height plus a local axial stiffness can distinguish an equilibrium-geometry shift from a force-scale error better than one loaded height. Lateral force and at least two small offsets test alignment stiffness independently. Fixture compliance, contact force from thermocouples, and thermal drift require measured corrections. Their parameters cannot be inferred solely from the solder response being evaluated.

For twenty unequal joints, rigid-cap mechanics is a separate comparator. A linear spring approximation uses each joint's unloaded height and Eq. 9 stiffness, then solves common cap height and two tilts from total normal force and two moment balances. This requires only a three-by-three linear system, actual sphere-to-joint placement, and pad positions. It is a useful future check if incoming sphere maps expose material within-cap variation. It must not turn twenty independent single-joint loaded heights into a claimed whole-cap minimum. Missing stiffness, cap bending, and wetting contact remain limitations of that approximation.

Finally, hot-to-cold behavior needs an independently established transformation or held-out hot observations. Cold measurements can settle which manufactured coupon gives more cooled clearance under its tested process. They cannot by themselves qualify liquid force predictions. Preserve the unresolved high-offset NIST discrepancy and all earlier negative evidence. No amount of internal mathematical consistency resolves unknown physical boundary conditions without observing them.

## Design choices shaped by principles

Model the Domain made the paired physical scenario the organizing record and kept published and actual-coupon domains separate. Laziness Protocol chose one coupon-specific research runner over a solver framework or an extension of the laboratory freeze. Explain the Number required shared and arm-specific cases, exact request accounting, an explicit analytical scope, and retention of negative results before a ranking or margin can be reported.
