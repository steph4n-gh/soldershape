# Fresh repair verification

This is a fresh same-family verification of the accepted A1, A2, A3 and B1 findings. It is not a second implementation pass, physical validation or cross-model agreement. No solver, application, protocol, CAD or test source was edited. I read both independent reviews, Comment Sicko's report, the force-analysis and final force-repair reports, board-backend report, fixture-CAD report, current scoring code and controls. The final regenerated native planning record was independently verified after its owner stopped editing.

## Findings verified as repaired

### A1. Input and measured-force covariance

The scorer projects the signed measured-minus-predicted coefficient for each named source before squaring. It requires consistent source units and standard uncertainties across both domains, with independent evidence for unlinked-source independence. Marginal measurement and input uncertainties remain visible and their separate gates still apply.

I executed a new end-to-end synthetic control with a shared source named `independent-review-thermal`, standard uncertainty 1 K, corrected-force coefficient 0.75 microNewtons/K and volume coefficient either -0.000015 or +0.000015 mm3/K. These are synthetic verification values, not measurements. The synthetic volume Jacobian is 50,000 microNewtons/mm3.

| Control | Hand-derived shared residual coefficient | Actual expanded residual U | Actual outcome |
|---|---:|---:|---|
| Opposing sensitivities | 1.5 microNewtons/K | 3.000002777787604 microNewtons | Inconclusive at the 3 microNewton normal guard |
| Matching sensitivities | 0 microNewtons/K | 0.004082491076944705 microNewtons | Agreement within declared guard |

The small nonzero cancellation result is the retained independent input variance. Both values agree with a separate hand calculation including that variance. Marginal measurement U remains 1.5 microNewtons in both cases. The amplifying combined guard is 3.000102777787604 microNewtons after its numerical allowance. A repeated source ID with `K` in one file and `Kelvin` in the other rejects freezing rather than assuming equivalent units.

### A3. Unmodeled transverse alignment

Both frozen input and outcome schemas now require numerical transverse displacement and expanded uncertainty. The protocol bounds `abs(y) + U_y` by 0.0005 mm. An independent control with every observed y field missing becomes inconclusive. A control at y=0.00051 mm and U_y=0.00001 mm also becomes inconclusive. The final behavior suite rejects missing frozen U_y and excessive frozen displacement. This is explicitly an apparatus-domain policy for an unmodeled direction, not proof of physical accuracy at that bound.

### A2. Derived planning decisions and numerical scope

Final `verify-plan` independently accepts all 20 expected native requests and rederives sensitivities, qualification, targets, scenarios and member completeness. Final plan SHA-256 is `ec22a9e77533c694757cc486aaa17ae5a6eee345ea189212a3429c7184ab25eb`. Protocol SHA-256 is `3320633962e270b1258c30a8f7ab013bc53f81359080507b54092f8eaefb6276`.

I copied that final directory to a temporary location and separately rewrote its lateral target to 99,999,999, made its failed initial normal allocation claim success, changed the central case eligibility flag, and inserted the rejected 0.005532 mm offset tolerance. Each valid JSON rewrite was rejected because the conclusions differed from raw receipts. The final record independently confirms that the density normal derivative is resolved while all three density allowable-limit fields remain null. Its extrapolated crossing is outside the registered 0.18 g/cm3 relative-U domain. The 0.005532 mm offset crossing is likewise null outside its 0.0024 mm domain. These are bounded numerical interpretations, not measured tolerances.

### B1. Volume-order wording

I read the two actual native results in the final default board archive and passed them to the screen in reverse order. Reference rule is false, candidate rule is true, and the headline correctly says that less solder meets the declared objective. An equal-volume control with a different opposing diameter uses Reference/Candidate wording. A downward-force control with zero lateral restoration no longer says that the failed case pushes upward. No numerical solver change was needed.

## Executed checks

The current final analyzer source is `06c97695dfa123a3467625a9de4c480475ed2c119a3377bc3fa448eb5d9989c6`. Its 24 force behavior controls pass in 1.103 seconds. The current board suite passes all 10 controls in 6.799 seconds. The three accepted narrative module docstrings are absent. `git diff --check` passed.

Both actual board archives verify their binding, selected source copper, requests, meshes and conclusion. Default archive SHA-256 is `1b87dca00de964b62cce902e071dad063b2f935f79d340817ff9e810bfff9604`. The actual browser download is `board_demo/data/browser-comparison.zip`, SHA-256 `598e1bb2aa8b573ec8eeed8fd2cd54528c325f5ec589b07b58af8479244ff7b2`. Both bind original board SHA-256 `1172f7b0fc262422bab01c62fb4dc84f16d9f1ea8902dc6fe2da859bba9035fc`, commit `6a92cec6b177191c5b0f80e260013a1f8ec147dd`, U1 J16, SDRAM_D0, diameter 0.4 mm, local position [4.4,-1.2] mm and board position [142.88,86.6] mm. I did not rerun the native engine or use the shared browser during this review. Root owns those separate receipts.

The existing CAD verifier passed against hardware manifest `a547d1f5e4bb1e599eb99d7dfc3cf46d18355f0a5eaf60fb8d30bf22197872ff`. This tool rewrites its deterministic evidence files; I notified root rather than concealing that behavior. No product source was changed. The current CAD evidence SHA-256 is `d4c695b242a3927434833bc1eee277b7fd11e6ab43d9d70c908b4658b11082c6`.

A separate read-only CadQuery script imported all four actual STEP assemblies. Each is valid and contains 15 solids. It independently imported the individual load-path STEP parts and found actual lower and upper wet faces at z=0 and z=0.150 mm. The distances along upper island, cap, hot bond, stalk, cool bond and cool tab are zero within 1.02e-13 mm. The source and handoff explicitly leave the final sensor attachment unresolved. The 40.3942057 mg modeled carrier, 396.131837 microNewton deadweight and 7.1239706 microNewton-meter worst planned moment remain supplier acceptance requirements. A nominal 2 mN axial range is not represented as proof of moment or cross-load compatibility.

## Negative verification attempts retained

An initial observer assertion incorrectly expected complete cancellation to eliminate independent input variance. The actual retained variance was correct; the hand calculation was corrected and the independent controls passed. A subsequent attempt to copy the planning directory overlapped its owner's regeneration and found no `plan.json`. No result was accepted from that partial directory. The earlier stable 20-request plan verified, but that superseded identity is not the final source qualification.

## Scope and final disposition

No new physical observation was acquired. Numerical agreement, neutral geometry and archive integrity do not resolve hot sensor accuracy, full-rim visibility, process chemistry, specimen independence or customer value. The documents correctly retain quote-stage status, false fabrication/physical-validation flags and the original published-data and stress-demo negative results. This verification does not inspect the rendered handbook or shared browser; those remain root's separate checks.

All four accepted review findings are repaired in the source and actual artifacts checked here. No material residual blocker was found within that bounded repair scope. The final analyzer source identity remained unchanged after the checks.
