# Physical model repair and design qualification

## Frame

The user requested root-cause repair of the physical failures and continued work until the usefulness for real PCB decisions is known. Start from `dccbcf6`. Preserve the earlier frozen protocol and negative receipts. No new interface features are needed to answer this question.

Done means a causal explanation of the major discrepancies, any demonstrated model or data repair implemented, fresh numerical and physical checks, and a supported or rejected PCB decision with explicit operating conditions. Numerical convergence alone is insufficient. An unsupported physical-accuracy claim is a failure even when the code runs.

The initial premise to challenge is that the previous free pinned bridge, nominal ball volume, and digitized Figure 5 coordinates represent the same physical system as the published calculation. Distinguish extraction mistakes, reference-plane mistakes, discretization/branch failures, missing solid/wetting boundaries, and missing experimental inputs. Do not tune one parameter per observation to make the data agree.

## Playbook

- [x] Read the Principles section of the poteto-mode skill.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

## Designed units

- [x] Re-read the primary experiment and its original implementation independently. Check every dimension and load convention against the figures and source.
- [x] Reproduce a failing specimen and build a case census separating numerical, force-direction, solid-contact, and measured-force discrepancies.
- [x] Compare the existing model with a direct upstream calculation and a structurally independent capillary calculation. Use identical physical inputs before attributing differences to physics.
- [x] Freeze decisive experiments for the leading causes. Test the smallest competing model repairs before changing the product.
- [x] Implement demonstrated repairs and preserve old outputs. Run focused analytic, upstream and physical checks without weakening the old numerical gates.
- [x] Seek an independent physical source with sufficiently identified inputs. Keep calibrated agreement separate from independent prediction and unsupported regimes.
- [x] Test a real PCB design question within the evidenced regime, including material, volume and gap uncertainty and a same-boundary baseline. A merely illustrative fixture rule does not qualify manufacturing value.
- [x] Independently review the conclusions and changes. Exercise affected public computation/export behavior and document the supported decision or explicit stop condition.

## Verification gates

1. A repaired calculation must preserve input, code, engine and model identity and report failures. New agreement cannot come from excluded measurements, per-point parameter fitting or looser numerical thresholds.
2. Direct upstream and independent calculations must agree within declared discretization error for identical supported boundary conditions. Any disagreement is investigated before physical scoring.
3. Physical comparisons must use known force directions, reported uncertainty and matching geometry references. Unknown normal magnitudes cannot be invented. A material value calibrated on the evaluation set cannot count as independent validation.
4. A PCB decision needs an explicit design objective, physically admissible solutions, a practical competing calculation and a conclusion that survives the stated uncertainties. Missing evidence produces a bounded verdict, not an automatic pass.

## Throughput checkpoint

Use three separate investigation outputs for source/data interpretation, upstream model behavior, and independent physical evidence. Root owns synthesis and product edits. Run only small decisive cases until a cause is established. Keep all new work under `evidence/model-repair` and `.research/model-repair` until an accepted repair is identified. Avoid another large sensitivity campaign over a model that does not yet reproduce its baseline.

## Investigation coverage

- [x] Frame. Three slices, each with its own output and a concrete falsifier.
- [x] Fan out.
- [x] Aggregate.
- [x] Report.

## Completed verdict

The fixed-gap force code agrees with the original NIST representation and an independent axisymmetric minimizer. The evaluation used an ill-conditioned inverse problem and mismatched archived case defaults. A height-free load request now solves the needed forward boundary condition, with a mandatory independent reaction check. Native derivative and initialization defects were repaired without weakening gates.

All 31 frozen forward scenarios passed numerical checks. Four external physical heights have 1.32 to 7.11 µm nominal discrepancies. The original high-offset force experiment remains unexplained. Physical qualification has not passed. A conditional 185 µm clearance comparison selects q220 for coupon testing and rejects a robust q270 choice under the declared low-volume stress. The paper's load-corrected analytical formula reaches the same decisions within 0.11 µm nominally. Occam's Razor favors that formula for aligned low-load designs. The native model remains a transparent inspection tool, not a demonstrated physical-accuracy improvement.

Independent science and product reviews are in `evidence/model-repair`. The public browser comparison, five-point loaded sweep, editable case and exported-input replay were exercised against the running artifact. Exact measurements, commands and remaining physical stop conditions are in `evidence/model-repair/report.md`. The earlier frozen data and negative study remain unchanged.

The comment review found no added comments or suppressions. Proposed deletion of old module docstrings was rejected as unrelated churn during a frozen numerical campaign. Deslop kept the two physical request shapes and one native engine. No new runtime dependencies, thermal simulator, generic optimizer framework, or engine port was added.
