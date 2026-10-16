# Independent scientific review

The published-data campaign does not qualify physical accuracy. Its final inconclusive verdict is supported. The repaired solver supports inspectable, conditional equilibrium calculations within its declared pinned-rim model. This review accepts that limited description and the fixture-held volume example. It does not accept a manufacturing recommendation or superiority claim over a qualified calculation with the same boundary conditions.

This was a fresh scientific review of the source, extraction, protocol, runner, raw receipts, repair evidence, and design comparison. It used the same model family as the implementation work. It did not modify product code or experimental inputs. The only file written by this reviewer is this report.

## Findings and disposition

1. P1, resolved. Missing normal-load magnitudes do not erase the known normal-load direction. Under the paper's equal per-joint load interpretation, the downward weight requires an upward joint reaction. Both central alternatives using the 37.2 micrometer height predict the opposite direction. At 1 N/m, h4-x4 gives -5675.2873 micronewtons and h4-x5 gives -6084.3769 micronewtons. Every positive surface tension preserves these signs. The runner now records `incompatible_normal_load_direction_at_sampled_geometry`, retains the raw shear residuals, and labels this diagnostic as added after prediction. The report correctly avoids rejecting every uncertain geometry or volume.
2. P2, resolved. Some volume-only corner extents originally showed observed-force overlap while including a corner with the incompatible normal direction. The final runner records `incompatible_normal_direction_cases`, makes those physical comparisons inconclusive, and preserves the raw sampled extent. I checked h4-x4 and h4-x5. Each now identifies its `volume-0.94` corner and reports no qualified overlap conclusion.
3. P2, bounded claim. The sheared-cylinder calculation preserves volume but changes wetted radius. Its disagreement with the pinned-rim result is an informative boundary-condition example. It does not establish superiority over the strongest same-boundary alternative. Direct native Surface Evolver is the numerical engine here. Product value comes from footprint import, controlled comparisons, diagnostics, and replayable exports. A comparative scientific advantage remains unmeasured.

There is no remaining scientific reporting blocker for a local exploratory release with the final scope labels. Physical qualification remains open.

## Primary-source and protocol checks

I inspected the original Figure 5 raster and the paper's experimental and modeling sections. The six height symbols and six offset symbols are retained. The two possible pairings at approximately 112 micronewtons remain explicit. The last large offset and the first clipped error bar are preserved. The source uses per-joint forces. Its height spans Si/Cu interfaces. Its flat-plane approximation adds both pad volumes. Figure 5 remains pinned; spreading subsets are outside this model. The paper fitted 0.4 N/m to all plotted data. It supplies no specimen-specific Figure 5 normal-load table. These facts support the declared mapping and calibration labels. [Josell et al., 2002](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827).

The primary mapping uses 0.01181699087727595 cubic millimeters and the measured interface gap. The literal copper-rim mapping is a separate approximation. The uncorrected mapping remains an explicit negative control. The ordinary workbench asks for liquid solder volume excluding pad metal and the distance between wetted planes. It does not silently apply the paper-specific correction.

I recomputed the zero-intercept fit from h1-x1, h2-x2, and h3-x3. It is 0.6682032821135863 N/m. No held-out row enters that fit. Its value is a descriptive fit to uncertain geometry, not an independent material measurement. The fitted-scale held-out center of 303.9305 micronewtons versus 144.25 observed is a conditional negative result. The shape also intrudes through the substrate planes. That point cannot establish valid physical force accuracy even if its force residual were small.

The plotted bounds and digitization bounds are not identified as confidence intervals. The volume and solidification scenarios are sensitivities. The report explicitly states that calibration uncertainty is not propagated, corners do not certify interior extrema, and post-solidification dimensions need not equal molten dimensions. All combined eight-corner physical sensitivity results are inconclusive. There is no uncertainty-qualified physical pass to report.

## Numerical evidence checked independently

I opened every current physical gzip receipt referenced by the report, including failures. All 133 compressed receipt hashes, normalized input hashes, input records, and numerical statuses matched. Recomputed calibration matched exactly. The campaign has eight checked central mapping calls out of 24, including six of eight primary pairing alternatives. It has 68 checked sensitivity calls out of 108. The separate surface-tension scaling call accounts for the 133rd reference. Raw failures remain present.

I also made four fresh public-solver calls without using the receipt cache.

| Fresh check | Measured result |
| --- | --- |
| Central h4-x4 at gap 0.0372 mm and offset 0.0151 mm | `refinement_checked`; Fx = -366.1301609965 micronewtons; Fz = -5675.2873041907 micronewtons. |
| h4-x4 at gap plus and minus 0.000005 mm | Both `refinement_checked`; energies 0.7847794027993474 and 0.7842118762434207 erg. |
| Independent normal energy derivative | Fz = -5675.2655592673 micronewtons; relative difference 3.8315e-6 from the central virtual-displacement force. |
| Nominal 0.005 cubic millimeter design | `refinement_checked`; Fx = -20.3642885194 micronewtons; Fz = -128.7709517295 micronewtons. |

The normal sign defect is therefore a property of the conditional shape calculation, not a reversed report label or a stale cached force. The fresh central h4-x4 input SHA256 is `596a01bb24a00c7b1c40817c3620dabf9217a88a6a4e706a4638d6266f82160e`. Its decimal gap differs by one floating-point rounding step from the receipt's generated gap, with corresponding force differences below 1e-8 relative.

The repair replaces unconditional Newton steps with line searches and additional gradient relaxation. It leaves acceptance thresholds unchanged. The official command documentation supports this choice. A line search can decrease energy without establishing convergence, and final numerical checks remain necessary. The retained failures at the 34.2 micrometer height prevent a claim that this repair solves every thin bridge. [Surface Evolver command reference](https://kenbrakke.com/evolver/html/commands.htm#hessian_seek).

## Design comparison and product scope

The design experiment uses a prescribed 0.15 mm gap, 0.02 mm offset, circular 0.2 mm rims, and an explicit requirement against separating force. It evaluates five volume samples for each of three nominal volumes. The 0.005 cubic millimeter candidate satisfies the declared sampled rule. The other two candidates develop positive axial force in some samples. The nominal 0.005 result also agrees with my fresh solve.

This demonstrates an executable decision under supplied assumptions. The plus or minus 10 percent range is illustrative, not measured process capability. The footprint does not establish ball volume. The pitch-cell screen is not a bridge-formation model. A different fixture requirement can select differently. Neither this experiment nor the physical campaign qualifies this distinct design geometry.

The final interface separates numerical checks from physical accuracy, states the negative published-data outcome, defines its volume and gap conventions, and warns about plane excursions. Comparison code declines a qualified comparison when a plane warning occurs. These are appropriate limits for this local product. No contact-line transition, solid-substrate obstacle, whole-package load balance, or manufacturing process has been validated. Absence of a sampled plane violation is not a continuous-surface or contact-angle certificate.

Prove It Works required raw receipt checks and fresh public solves. Explain the Number required separate numerical coverage, calibration, physical compatibility, and sampled design conclusions. Those principles changed the review from accepting successful solves to checking what the reported numbers establish.

## Reviewed file identities

The following hashes identify the reviewed snapshot. Later documentation or interface changes require their own review. The numerical core remained at the hash below throughout this review.

| File | SHA256 |
| --- | --- |
| `.research/physical/sources/nist2002.pdf` | `4917aa35b4b804292826f8ce92b1f7c51eaed83e6f0777aeefb26195e7204990` |
| `.research/physical/nist-extraction/Im5.png` | `f3924c0644fd3795c7444d46c5f887fed60fa19cd6a117321e7c0d269178a09f` |
| `soldershape/solver.py` | `07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98` |
| `tools/validate_physical.py` | `c7cd97eeb08103ce2953aca4460cc9a8f7723f3951139ae376bd0c775791a69d` |
| `evidence/physical/protocol.json` | `6071faced970e1b6f9dc5f7dc0c35dad9dd15432de4855ab1889991e69a6dc8f` |
| `evidence/physical/nist-extraction.json` | `c9d27bbb23a70c9ecff211d63a054399da1037eb2f105885183f54bc2ca6220e` |
| `evidence/physical/predictions.json` | `e3b2416de22fe1a45fca3cbf23518d94382b3938a772dedc491bd4242997644f` |
| `evidence/physical/validation-report.md` | `0fdf8c79774382bfffddaabbf279f271fe8066761685221268b83a4a7f278c90` |
| `evidence/physical/solver-repair.json` | `51365c93a87c33212811e59dfb0f40bc13f08d74b7a89d3ab713511e76ade3a8` |
| `evidence/physical/solver-repair.md` | `695637b7324b71aec509b1e7eaa1551e682e03efb0ce8fa5e6c7d955cb53ebd3` |
| `evidence/physical/solver-repair.py` | `323699bd2897ba18c31be66c70977cef7f94cae67895f96b759afc5366e6f9e5` |
| `tools/compare_designs.py` | `21c049acd190621621bda59ee68b4cb6072844c7f6326d0e45058cdb8c188365` |
| `examples/design-comparison.json` | `68af2c4166e0a0f2eb29535997b0a58b429744d195f42d7b81a3317e1700fa91` |
| `evidence/design-comparison/comparison.json` | `c6aa9239551ffead5d91f0041877b7a7922984e19fa5b7df5f9e2340b1ceeedc` |
| `evidence/design-comparison/report.md` | `6075eda50e88649042e9f9ce716940954889c353c5cc2e5d7e3ee2d02b19cdbb` |
| `soldershape/__main__.py` | `3870de483dc43e660b49dd1a6e20f8fd08cac96d73095834f0cd326639327739` |
| `soldershape/web/index.html` | `5c34894793191f72d0b12ac46f1ecc26ae9b49a9eefe0777b92a122db5d78d95` |
| `README.md` | `04e166a0576640261b171001b27370cbb3982355aac013a288ade766645b1e2f` |
| `soldershape/model.py` | `3eef0883253f051c75cc5e67641924ec48f31eef17efd9b5ba265115269b3e91` |
| `soldershape/artifacts.py` | `a819b4cc21cf5fc6864d87f6506d1a41c973f14107264dc2d5300e9ad26b3666` |
| `.engine/provenance.json` | `87d8d486bb81e6b4c53b1bf4e49955ae7c2e57c01261fe4384915ea9f196fcc5` |
| `.engine/src/evolver` | `c930b47b33a4cafb3cf98b1c0cb7e3bd9805abcf67aceefe243daea091072f8e` |
