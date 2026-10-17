# Independent coupon science review

The first review requires changes before the analysis is ready for an outside laboratory. Three executable counterexamples pass the current liquid-model gate without the physical evidence required by the procedure. One sequencing ambiguity also needs a procedural correction. These are prospective analysis defects. They are not new physical results or a change to the earlier negative physical evidence.

This is an independent reviewer in the same inherited model family as the implementation. It is not a review across different model families. The review reads the actual experiment, allocation, blank worksheets, procedure, analysis code, tests, and solver load path. It changes only this report.

## Reviewed snapshot and executable evidence

The repository base is `3f6ff5c2246a3f62c37f9cab4bd59bc4679d4f79`.

| File | SHA-256 at the initial audit |
| --- | --- |
| `coupons/tools/analyze.py` | `92d80bd829bfa725d886d3cf6ed82f1cdf03c53b2c535c3776d4dda5a8fab7de` |
| `coupons/tests/test_analysis.py` | `623a3b2b8c3900c59ca710e3ee30bb56a29a21114c206b0fd132e50e24068b38` |
| `coupons/experiment.json` | `7e8110f1a2cba1fa1be57443030fe698df2538b4d45a54b0e89c0e5d13342fb7` |
| `coupons/PROCEDURE.md` | `96bf7b4ca29a747b9be9e09e312256e41606474607a8556af3fa8a736cf2ff14` |

`python3 -m unittest discover -s coupons/tests -v` passed all twelve tests. These tests use labeled synthetic native results. The review also instantiated their fixture and scored three modifications through the actual `freeze` and `score` functions. All three returned `liquid_model_verdict=consistent_at_frozen_inputs` and `geometry_gate=true`.

| Synthetic counterexample | Measured behavior | Required behavior |
| --- | --- | --- |
| No contact-line or wetting observation fields. `defects=none`. | The liquid model is consistent. | Model comparison remains inconclusive until the lab explicitly observes all twenty wetted interfaces and the declared boundary condition. |
| The observed maximum minus minimum is 3 micrometers. Both endpoint expanded uncertainties are 2 micrometers. | The geometry gate passes. | The range gate accounts for uncertainty. The conservative upper range is 7 micrometers and fails the declared 3 micrometer gate. |
| Frozen material temperature is 20 degrees Celsius. Every row labeled `molten` is measured at 20 degrees Celsius. | The liquid model is consistent. | Sn63Pb37 observations below its liquidus cannot qualify a liquid equilibrium model. |

## Findings

### P1. Require an observed wetting and boundary-condition state

At initial `analyze.py` lines 412 through 438, `geometry_ok` infers physical eligibility from `defects=none`. The outcome schema cannot record whether all twenty joints wet their declared rims, or whether the contact line follows the frozen boundary hypothesis. Procedure line 116 explicitly requires both observations. A generic defect absence is insufficient for either.

Add an explicit observed state and an evidence reference. Distinguish a matched boundary, a failed boundary, and an unobserved boundary. Gate model agreement on a matched observed boundary. Do not let a blank observation or a generic `none` imply that match. Keep observed clearance usable when its independent coverage and uncertainty requirements pass. Preserve sidewall wetting as a possible falsifier of the literal-rim approximation. Do not select the secondary geometry because it fits a held-out height better.

### P1. Include uncertainty in the cap gap-range gate

Initial `analyze.py` line 417 compares only `max_gap_um - min_gap_um` with 3 micrometers. The procedure requests uncertainty for the range, but the schema has no separate range uncertainty. Minima and maxima can each have up to 2 micrometers expanded uncertainty. A reported range of 3 can therefore satisfy the code while its conservative upper range is 7.

The smallest correction uses `max_gap - min_gap + max_gap_U + min_gap_U <= 3`. A separate correlated range uncertainty is also valid if the lab supplies and justifies it prospectively. A central-value range alone does not establish the near-parallel geometry used for equal loading.

### P1. Establish liquid-state eligibility instead of trusting a phase label

Initial metadata validation accepts every positive `temperature_C`. Initial outcome scoring checks only overlap with that frozen temperature. The executable counterexample sets both to 20 degrees Celsius and qualifies every row labeled `molten`.

Declare the alloy liquidus and require the lower bound of a molten temperature observation to exceed it. Also require explicit evidence of a stable liquid plateau and a qualified hot measurement method. Keep the observed interval within the material-source and frozen-method range. A large temperature uncertainty must not turn an observation outside the accepted plateau into an eligible result. The procedure already calls for plateau stability, thermal expansion treatment, and hot measurement qualification. Record those attestations beside the outcomes or frozen metadata so the scorer cannot silently bypass them.

### P2. Place and measure before freezing, then qualify the waiting time

The freeze requires each confirmation cap's measured pre-reflow offset. The confirmation procedure presently describes assembly after the freeze. A lab cannot obtain that actual incoming offset before placement.

State the sequence explicitly. Place the confirmation caps at room temperature and measure their offsets before freezing. Do not reflow them until the completed freeze is archived. Qualify the maximum placement and flux-to-reflow dwell on the pilot, including prediction computation and the time until R3. Otherwise the lab may substitute nominal offsets, or hold fluxed parts outside the accepted process. Preserve failed attempts and changes in a new revision.

## Checks that support the current design

The kit-mass conversion is correct. One gram per cubic centimeter equals one milligram per cubic millimeter, so `kit_mass_mg / 20 / liquid_density_g_cm3` gives liquid volume per joint in cubic millimeters. The external load conversion is also correct. `cap_mass_mg * 9.80665 / 20` gives micronewtons per joint. It excludes solder mass. The separate literal-rim gravity calculation accounts for solder body gravity.

The secondary mapping adds both measured pad-cylinder volumes and subtracts both metal heights from the solved plane separation. Its gravity is disabled, so fictitious liquid within the upper metal cylinder does not add a second gravitational load. This remains an approximation, fixed before outcomes. It is not a validated physical correction.

The code preserves twenty-four attempted confirmation caps, with twelve pairs across three runs. Twenty joints do not become twenty independent specimens. A direction verdict requires all four pairs in every run and the same guarded sign in all three runs. The report makes no population confidence interval or production-yield claim. Failed and missing caps prevent a complete direction verdict and remain in the denominator.

Cold-only outcomes leave the top-level liquid verdict inconclusive. Model error and threshold clearance are separate decisions. The threshold uses a measured whole-cap minimum and its uncertainty. A partial section cannot pass it. The earlier published physical failures remain outside this experiment and are not overwritten.

Blank inputs and unqualified pilot metadata fail before native computation. The freeze preserves the actual inputs, source hashes, solver receipts, specification, allocation, and completion time. Scoring rejects edited frozen inputs and changed prediction code. These checks document the supplied sequence. They cannot prove an operator never viewed outcomes or verify a laboratory certificate by themselves.

The native load solver already rejects numerical warnings and sampled pad-plane excursions before it returns a balanced accepted result. The coupon script does not need a duplicate independent warning system for that existing call path.

## Remaining limits even after the fixes

The outcome comparison remains conditional on the frozen central inputs. The analytical sensitivity screen does not propagate uncertainty through the native solver. Strongly agreeing central values do not qualify uncertain density, surface tension, load sharing, or the copper mapping. Individual sphere variation and residue load require the procedure's input sensitivity evidence. A nearly parallel cap is not a direct measurement of equal force at every joint.

All future claims must identify the tested coupon construction, alloy, process, phase, and measurement coverage. A useful cooled pad-size comparison can precede liquid-model qualification. This coupon does not validate restoring forces, fatigue, electrical reliability, or manufacturing yield.

Prove It Works changed this review from an inspection of passing tests to executable counterexamples against the scorer. The reviewer ran the actual freeze and score functions and retained the synthetic nature of their outputs. The package is not ready for release until those counterexamples fail safely and the placement sequence is explicit.
