# Independent review B

No actionable findings in the reviewed scope. This is an independent pass using the inherited model. It is not a claim of model diversity. Production `soldershape/model.py` and `soldershape/solver.py` were read for context and remain unchanged.

## Scope and checks

Reviewed `prelab/campaign.py`, `protocol.json`, `replay.py`, `test_campaign.py`, `rigid_cap.py`, `test_rigid_cap.py`, actual campaign and replay receipts, the rigid-cap result, and `LAB_ADDENDUM.md`. `finite.py` and its numerical geometry are excluded because that work was still finishing. The final combined product report and UI are also outside this pass.

Executed `python3 -m unittest prelab.test_campaign prelab.test_rigid_cap -v`. All eighteen tests passed. The tests exercised the actual completed campaign, rehashed false conclusions, deletion of a failed receipt, unit conversions, literal rigid-body results, force and moment closure, tensile reaction retention, and prescribed sphere maps.

Executed `python3 prelab/rigid_cap.py --verify`. Recorded source hashes and all recomputed mechanics matched. Independently checked all thirteen actual replay receipts against their archived requests, producer engine records, report receipt hashes, and campaign-manifest identity. Their inputs, statuses, accepted native gaps and force components matched exactly. This pass verified those existing fresh receipts. It did not rerun the native engine itself.

Initially questioned whether the campaign omitted the two gravity baseline cases. Inspection of `output/prelab-baseline/plan.json` and all six native receipts resolved that concern. The fresh baseline plan matches the historical planning plan, and each exact baseline request, accepted gap and force component matches its historical counterpart. The no-gravity scenario campaign is separate from those six controls. The root agent is packaging that baseline evidence with a standalone verifier.

## Interpretation limits checked

The nominal native C220 advantage is 15.796987 micrometers for rim pinning and 10.889505 micrometers for the two-cylinder interpretation. The opposed requested endpoints reduce it to 2.816094 and 0.843119 micrometers. The wider opposed liquid-volume construction reverses it to -4.212552 and -5.238158 micrometers. These values were read and regenerated through the actual campaign verifier. They describe the declared points, not a continuous-domain robustness result.

The protocol correctly identifies requested pad and sphere endpoints as requested specifications. It does not claim demonstrated fabrication capability or a process distribution. The wider liquid-volume stress is explicitly separate from screened sphere geometry. It neither samples the same volume uncertainty twice nor presents its reversal as a measured process failure. The raw paired differences below three micrometers support a resolvability warning. They do not establish an uncertainty interval or physical sign.

The two boundary interpretations can change the 185 micrometer numerical clearance sign. The addendum correctly requires independent observation of molten contact conditions and finished metal geometry. It does not fit contact depth to final height and reuse that fit as validation. The independent equal-load calculations cannot establish whole-cap minimum clearance. The rigid-cap example identifies that limitation while retaining its linear-spring, flat-carrier, rigid-cap, fixed-wetting and no-lateral-coupling assumptions. Its deformation screen is explicitly unqualified. Prescribed endpoint maps and tensile reactions remain numerical stress constructions.

The rejected 10,000 micronewton control has an actual native numerical or command error and `load_balance.termination = engine_failure`. It demonstrates failure retention and rejection by the acceptance gate. It does not demonstrate physical nonexistence of an equilibrium. The root agent confirmed that the final report will preserve that narrower statement. Replay currently checks recurrence of rejection rather than recurrence of the same failure mechanism. No physical conclusion should depend on that mechanism.

The local hash manifest detects accidental member changes and independently reconstructs conclusions from retained receipts. It is not a trusted signature or proof against a coherent rewrite of all evidence. Its declared scope states that limitation. Accepted archived results still provide numerical consistency only. No new molten contact, volume, thermal transformation, force or cooled-clearance measurements exist.

## Comment review

No actionable comment findings. The five scoped Python files contain no inline comments, suppression comments, TODOs or FIXME workarounds. Four contain one short module-purpose docstring. No code or comment deletion was made. No constraint encoding offer is needed.

## Principles that changed this pass

Prove It Works required reading and checking actual receipt bytes, source identities and literal mechanics instead of accepting report summaries. Explain the Number kept numerical ordering, requested specifications, unqualified stress points, measurement budgets and physical validation as separate claims.
