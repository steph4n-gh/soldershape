# Independent finite-pad and replay review

The finite-pad conclusions are supported within their declared prescribed-wetting scope. No actionable finite-pad correctness finding was identified. One remaining replay identity omission is proven below. This review used the inherited parent model. It is an independent review, not model diversity. Only this file was written.

The reviewed baseline is `33666d32c92b6753925bb2fd29dc62ce5fed618b`. Current `soldershape/model.py` and `soldershape/solver.py` are byte-identical to that baseline. The reviewed finite adapter SHA-256 is `b3c2e5e2a7210e73d9ea1d15e62daeb4547399d90e5352b3cc976574a384a811`.

## Finding

### P2. A fresh accepted replay can omit its result engine identity

`prelab/replay.py::validate_fresh` validates the result engine only when `result.get("engine")` is truthy. Removing the entire `engine` field therefore skips the check. `prelab/campaign.py::load_results` contains the same conditional.

I exercised the actual `replay()` function with a disposable replacement worker. It copied each archived receipt to its fresh destination, removed only `engine`, and retained the original input, producer identity, status, gap and forces. The function returned `{"passed": true, "requests": 13, "expected_rejections": 1}`. This shows that accepted calculations do not currently require their native result identity. It does not show that the recorded native calculations used a wrong engine.

Require the result engine source and binary identities for an accepted native calculation. Rejected calculations may need distinct handling if an upstream failure genuinely has no native result. Add removal or empty-object damage to the existing end-to-end forgery regression. The completed repair already rejects changed input, input hash, producer binary and result binary. All four existing cases passed in this review.

## Independent calculations

I counted 28 isolated pilot requests and verified every file in each receipt inventory against its recorded hash. I then verified all 161 members and all source identities of the completed `output/prelab-finite-confirmation/report.json`. That fresh confirmation includes four eligible nominal fixed-gap cases and two ineligible penetrating controls.

I recomputed normal reactions from the raw `SS_LEVEL` energy records. I did not use the summarized reaction values. The conversion is `-50 * (E_plus_erg - E_minus_erg) / delta_mm` in micronewtons. One erg per millimeter is 100 micronewtons. The factor of two comes from the central difference.

| Arm | Displacement, µm | Penultimate reaction, µN | Final reaction, µN |
| --- | ---: | ---: | ---: |
| C220 | 0.5 | 6.867139558 | 6.866894055 |
| C220 | 0.25 | 6.865634639 | 6.865391119 |
| C270 | 0.5 | 6.868126397 | 6.867768667 |
| C270 | 0.25 | 6.865913351 | 6.865557447 |

Across these four values, C220 has a 0.001748439 µN spread and a maximum residual of 0.002484558 µN against the prescribed 6.864655 µN load. C270 has a 0.002568950 µN spread and a maximum residual of 0.003471397 µN. Both fit the declared 0.01 µN numerical engineering tolerance. The fresh confirmation reproduces these raw-energy results exactly. This checks two difference steps and two internal mesh refinements. It is not a physical force error bound.

For every displaced full-wetting energy job, I independently recovered the envelope target volume from its native model. Subtracting `pi * (r_lower² * depth_lower + r_upper² * depth_upper)` returns the original requested liquid volume to less than `1e-16 mm³`. The gap correction subtracts both wetting depths once. Gravity is disabled, so the envelope does not assign liquid weight to phantom copper volume. The external potential `W * H` differs from `W * h` by a constant.

The current eligible C220 loaded pilot gives 178.203436202 µm. The archived mapping gives 178.203381224 µm. Their difference is 0.000054978 µm. This is an implementation control under the same fixed boundary assumption. C270 optimizing-height failures retain native overconstraint and internal topology errors. Its successful fixed-gap geometry and independent relaxed-energy balance distinguish a moving-height optimizer failure from evidence of physical impossibility. No replacement loaded rootfinder is qualified here.

## Geometry and physical interpretation

The adapter applies finite-solid inequalities to free facets and their connecting edges. Refinement inherits them. Zero-tension closure caps and the bare load vertex are not treated as liquid-air interface. The obstacle expressions exclude copper and supporting substrates in the stated envelope coordinates. The dimensions of both arguments to each `maximum` are length. Their nonsmooth seam remains a numerical limitation.

I independently reconstructed the quadratic patches from raw vertex, edge-midpoint and facet records. I evaluated all fifteen barycentric samples per facet for the decisive C270 extra-refinement case and both penetrating controls. The independently recovered counts and residuals match the recorded diagnostics.

| Case | Curved facets | Samples | Penetrating samples | Worst copper residual, µm |
| --- | ---: | ---: | ---: | ---: |
| C270 full wetting, extra refinement | 24,576 | 368,640 | 0 | -0.000063058 |
| Penetrating control without obstacles | 6,144 | 92,160 | 24,390 | -7.615680231 |
| Penetrating control with obstacles | 24,576 | 368,640 | 2,670 | -2.460725160 |

The constrained penetrating control remains not converged and physically ineligible. It is not described as a successful exclusion solve. The diagnostics detect substantial curved-facet penetration even though native vertex constraints were applied. A separate extra refinement resolves the nominal sub-nanometer rim interpolation failure without loosening its tolerance. Prescribed rim samples are excluded from new-contact counts by boundary topology. Rim samples still contribute to penetration checks.

For fixed depths and no new wall contact, wetted face and sidewall areas are constant. Omitting their constant solid-liquid energy does not change height or offset derivatives. This does not identify an equilibrium contact angle or a real contact-line state. New wall contact changes that energy bookkeeping. The adapter rejects such samples from physical eligibility. Its inherited affine force command is not accepted as independent evidence for an active-contact calculation. Fresh relaxed-energy derivatives use moved upper obstacles and are accepted only when every displaced solve remains numerically acceptable and has no detected new contact or intrusion.

Fifteen points per quadratic facet do not certify continuous clearance. The implementation states this explicitly. It also does not certify self-intersection freedom, a globally minimal energy state, an interval bound over uncertainty, real wetting, or physical agreement. The nominal fixed-gap controls should remain labeled imposed geometries rather than independent loaded-height predictions.

## Tests and replay

`python3 -m unittest prelab.test_finite prelab.test_replay -v` passed eight tests. No test was skipped. The tests cover exact volume bookkeeping, invalid depths and artificial-envelope gravity, obstacle assignment, curved-patch penetration, prescribed rims, export before flattening, reaction units and sign, and the four original identity forgeries.

I verified hashes of every receipt in `prelab/evidence/replay-identity-checked/report.json`. Its thirteen fresh native replay rows include twelve accepted calculations and one expected rejection. All accepted gap and force differences are exactly zero. I did not launch another native campaign or another finite solve because the root's fresh confirmation had completed and its actual raw data could be checked directly.

There are no scoped source comments or correctness suppressions in the reviewed adapter or replay files. The regression's explicit missing-campaign skip was inactive because the native evidence exists.

Prove It Works changed this review by requiring raw native energies, patch records, inventory hashes and the actual replay function. Explain the Number changed it by reporting step and mesh spread, load residual, sampling limits and the numerical tolerance separately from physical accuracy.

## Remaining measurements

The lab still needs actual hot wetting extent, finished metal geometry, deposited liquid volume, relevant material properties, cap load sharing and tilt, and hot-to-cold behavior. The finite calculation strengthens a conditional boundary-model check. It does not close those physical qualification gaps or justify a production clearance pass.
