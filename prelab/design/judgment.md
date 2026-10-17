# Pre-lab design judgment

Use the uncertainty candidate as the base. Add the finite-pad experiment as a separately gated research calculation. The proposed sixteen paired scenarios under two boundary interpretations are a decisive first screen. They do not qualify either arm for physical clearance.

This read-only judgment compares [boundary.md](boundary.md) and [uncertainty.md](uncertainty.md) against source commit `33666d32c92b6753925bb2fd29dc62ce5fed618b`. Only this judgment file was written. Scores assess the designs, not implementation or physical accuracy. Five is strongest on each criterion.

| Criterion | Boundary | Uncertainty | Evidence for the distinction |
| --- | ---: | ---: | --- |
| Physical consistency, actual liquid volume, and contact energy | 5 | 4 | Boundary derives the envelope volume, forbids fictitious cylinder gravity, and excludes new wall contact from physical interpretation. Uncertainty requires these conditions but does not implement their geometry. |
| Identifiable assumptions and bounded claims | 5 | 5 | Both separate requested inputs, planning assumptions, physical observations, and unqualified stress cases. Both retain hot-to-cold and multi-joint gaps. |
| Smallest replayable implementation with source identity | 4 | 5 | The paired runner reuses the production solver without altering it. The finite-pad child adapter adds several geometry and reaction checks that must earn their cost. |
| Decisive paired uncertainty cases with honest scope | 3 | 5 | Uncertainty names shared errors, opposed arm deviations, near-zero differences, reversals, and exact accounting. Boundary provides wetting-state comparisons but a less complete sampling design. |
| Preservation of production and prior evidence | 5 | 5 | Both isolate research behavior and preserve historical negative results. |
| Total | 22 | 24 | Equal weights. This is a design-selection aid, not a numerical benchmark. |

## Evidence checked

`coupons/experiment.json` specifies twenty joints, 220 or 270 micrometer lower pads, 280 micrometer upper pads, a 185 micrometer finished-pad-face requirement, and separate hot-state quotation. Its three micrometer pair budget is a measurement target. It is not a proven model error bound.

`coupons/tools/analyze.py::request` divides kit mass and cap weight by twenty. Its `two_pad_cylinders` path adds both cylinder volumes and returns both heights as the output correction. `analytical` omits offset and gravity by its own scope statement. `coupons/evidence/planning/plan.json` explicitly labels its sphere-to-liquid volume equality as a planning geometry assumption.

A fresh read-only Python calculation using `analytical` reproduced the uncertainty design's nominal pair differences of 15.829402939 and 10.931730870 micrometers. It also reproduced the opposed screened endpoint differences of 2.841089630 and 0.874730339 micrometers. These are analytical checks. No new native uncertainty solve was run by this judge.

`soldershape/solver.py::_model` includes zero-tension closure caps and a separate bare load vertex. Its force commands apply affine virtual deformations. `_solve_with_levels` computes these forces before extracting its flattened mesh. `solve_loaded` performs a fresh fixed-gap reaction check but uses the same generated model and force implementation. This reuse is safe only within the assumptions stated below.

## Exact grafts required

1. Keep the paired physical scenario and declared request table from uncertainty. Keep actual-coupon and published one-cylinder cases in different domains. Derive each native request and output-plane correction from one conversion. Separate geometric sphere-volume construction from measured-mass construction.
2. Keep all six nominal requests byte-identical to their archived physical inputs. Recompute their numerical results without importing the old receipts as fresh evidence. Keep failures in the expected request table and in the verifier's regenerated conclusion.
3. Add `FinitePadRequest` and the boundary design's envelope identity. Record `liquid_volume_mm3`, `envelope_volume_mm3`, each copper contribution, envelope height, and opposing-face gap separately. Disable gravity in this first envelope experiment.
4. Use a subprocess for each finite-pad request. Keep generator replacements inside that child. Check that each textual insertion matched exactly once. Save the actual generated model and commands, adapter bytes, production-source identities, and engine identities. Do not change production solver globals in the parent or the running web app.
5. Test zero depth, full depth, at least one partial depth, and a penetrating unconstrained control. Apply obstacle constraints to free facets and edges so refinement inherits them. Exempt envelope closure caps and the bare load vertex from free-interface intrusion tests.
6. Preserve all original numerical thresholds. Interleave gradient steps with constrained Hessian steps. Record contact activity and constraint residuals before and after displaced calculations. An active-contact or failed-release result stays in the record but cannot establish physical wetting behavior.
7. Compute independent relaxed energy derivatives at two displacement sizes and an extra mesh level. Use fixed-gap solves without the external load potential. Move the upper contact circle and upper obstacle together. Compare the upward reaction with the applied downward load. Preserve one-sided results at contact transitions.
8. Run the opposed screened endpoints, broad opposed-volume reversal, shared extremes, reversed-arm control, and identical-arm control. Select remaining cases through the inexpensive analytical screen. Report sampled ranges and signs, with no interval or probability guarantee.
9. Retain minimum whole-cap clearance as unqualified unless a separate rigid-cap mechanics calculation and its inputs support it. A single-joint equilibrium height cannot establish the minimum across twenty unequal joints or a cooled cap.

## Equations and reuse hazards

The stated identities `H = h + dL + dU` and `Venv = VL + pi*rL^2*dL + pi*rU^2*dU` are correct for the declared envelope containing those solid portions. They cease to describe actual liquid volume if the computed envelope cuts through a copper cylinder or creates an unaccounted wetted region. The volume equation is bookkeeping under a geometric condition, not evidence of wetting.

The full-depth maximum constraints have consistent length units and exclude the intended finite cylinders when paired with the substrate planes. Partial depth requires the partial-depth planes stated in the boundary candidate. Reusing `z >= 0` and `H-z >= 0` at partial depth would silently replace the real substrate locations. The nonsmooth maximum seam and finite sampling of quadratic facets remain numerical limitations.

The fixed-depth wetting-energy terms are constant with respect to gap and offset only while wetted copper area stays fixed. New wall contact changes that condition. Giving that area liquid-vapor tension is not a complete copper wetting model. A favorable load-balance result cannot repair the omitted contact energy.

The energy-difference reaction has the correct sign when `E*` contains capillary energy at fixed liquid volume. Using the loaded solve's `total_energy` would also differentiate `W*H` and give the net force near zero. The derivative must use unloaded fixed-gap energy. Its comparison target is the applied load.

Do not treat the existing affine `do_zforce` or `do_xforce` as independent physical reactions with an active solid constraint. They can violate the obstacle during virtual deformation or omit moving-contact work. Existing status fields may remain diagnostic, but the research eligibility field must reject active-contact physical interpretation even if production refinement gates pass. For inactive obstacles, retain a clearance check sufficient to cover the virtual displacement before relying on the bare force check.

The child adapter must not bypass parser failures, warning checks, Hessian checks, or force-refinement checks to obtain an accepted row. If safe adaptation requires that many overrides, keep the obstacle experiment as a negative result or use a small direct native runner.

Sixty-four expanded `LoadSpec` requests are not necessarily sixty-four Evolver process launches. Each loaded solve includes at least a height optimization and a separate fixed-gap check. Adaptive refinement, direct energy derivatives, and replay add launches. Record scenario rows, unique requests, reused receipts, native processes, and successful or failed outcomes separately. Do not fill the campaign allowance with redundant cases merely to reach a target count.

## Decision and limits

The base is ready to implement after the listed grafts. The obstacle calculation is an experiment until its controls pass. Do not make completion of a broad finite-pad campaign a prerequisite for reporting a decisive uncertainty reversal or an unresolved boundary dependence.

Laziness Protocol selected one coupon-specific runner instead of a new model framework. Model the Domain selected paired physical scenarios and separate liquid and envelope quantities. Explain the Number required exact request accounting and analytical labels on the screened pair differences. These principles were read in full during this judgment.
