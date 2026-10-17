# Upstream comparison narrows the physical root cause

The current force calculation agrees with an independently represented NIST surface model at three matched inputs. The largest component difference is 0.012 percent. This rules out a large force-unit, pressure-sign, or cap-volume defect for these cases. It does not validate the physical boundary conditions or the experimental input reconstruction.

The original NIST procedure predicts displacement under an applied vector force. The previous SolderShape comparison instead prescribes the measured gap and offset, then computes the implied forces. The implied normal force changes by about 4,500 to 5,300 µN per µm near the conditional forward solutions below. A measured gap uncertainty near 1 µm therefore cannot support a precise inverse force claim for these thin joints.

## Matched geometry isolates the implementation

[NIST's code archive](https://www.ctcms.nist.gov/solder/underfill/underfill.zip) has SHA256 `fa1ceb86bd9f37214194370b809ee92e73614ed3c1c7b1e43a80460d759bfcc5`. The native executable is the existing pinned Surface Evolver 2.70a binary. Its hash is `c930b47b33a4cafb3cf98b1c0cb7e3bd9805abcf67aceefe243daea091072f8e`.

Both models use 0.64 mm pad diameters, 0.0086 mm³ solder, and two 5 µm pad slabs. The effective model volume is 0.0118169908773 mm³. Gravity is zero and surface tension is 1 N/m for this implementation comparison. The contact line stays fixed to each circular pad rim.

The NIST model represents only the free liquid surface as body facets. Its top-boundary content integral closes the volume. SolderShape closes the body with explicit zero-tension caps. The NIST `forcex` and `forcez` commands independently compute virtual-displacement energy differences with pressure correction. Their native force unit is mN. The table converts both outputs to µN.

| Case | Gap µm | Offset µm | NIST shear µN | SolderShape shear µN | NIST normal µN | SolderShape normal µN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| h2-x2 | 35.1 | 7.1 | -99.58032 | -99.58638 | 15616.5042 | 15616.4083 |
| h4-x4 | 37.2 | 15.1 | -366.12848 | -366.13016 | -5674.6099 | -5675.2873 |
| h6-x6 | 35.1 | 31.0 | -454.82567 | -454.84731 | 10805.9146 | 10805.7914 |

The three native replays have no warnings, zero negative Hessian eigenvalues at all three refinement levels, and less than 1 percent force change between the last two levels. All three native volume errors are below 1e-9 relative. These checks establish agreement between numerical implementations for the specified branch.

The negative normal force at h4-x4 also appears in the original NIST model. It does not arise from a SolderShape sign error. The prescribed geometry calls for a tensile load in this model. The h6-x6 native geometry extends about 0.265 µm beyond the solid planes. A stable unconstrained free surface can therefore be physically inadmissible. Positive Hessian eigenvalues do not certify solid-body exclusion.

The frozen SolderShape comparison uses solver SHA256 `07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98`. The [machine-readable record](upstream-diagnosis.json) pins the source, binary, script, and comparison inputs.

## The forward experiment keeps load and material fixed

The paper's specimen-specific normal loads remain unavailable. This experiment declares a source-derived load scenario rather than presenting that scenario as measured provenance. The scenario uses the source-commented mass of 0.0015 kg, tilt of 4.5 degrees, and eight joints. The resulting per-joint normal load is 1831.8356 µN and shear load is 144.1686 µN.

The surface tension is the paper's fitted 0.4 N/m in both runs. Neither surface tension nor solder volume changes to fit the last observation. One run uses the archive's 4 µm pad thickness. The other uses the paper's 5 µm thickness. The 0.0086 mm³ solder volume stays fixed.

A bounded two-variable Newton wrapper balances the original NIST surface's reaction forces against those declared loads. Every function evaluation relaxes and refines the original pinned native model. The wrapper stops below 0.1 percent relative force residual.

| Pad thickness | Predicted gap µm | Predicted offset µm | Final normal residual µN | Final shear residual µN | Sampled contact-angle range |
| --- | ---: | ---: | ---: | ---: | --- |
| 4 µm | 34.32317 | 13.60407 | 0.00793 | 0.000522 | 91.52 to 138.44 degrees |
| 5 µm | 36.24863 | 14.45387 | 0.0853 | 0.00587 | 92.17 to 139.14 degrees |

Both final native meshes stay between the solid planes at sampled vertices. Their sampled contact angles lie inside the source's 4 to 150 degree pinning range. The angles use adjacent triangles from a flattened export. They do not bound the curved elements.

Changing the pad thickness from 4 to 5 µm changes the predicted gap by 1.92545 µm and the predicted offset by 0.84980 µm under the same load. The forward offset changes much less than an inverse force evaluated at an uncertain measured gap.

The [published last experimental point](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=853827) has measured offset 31.0 µm and a plotted interval of 26.1 to 36.1 µm in the [frozen digitization](../physical/nist-extraction.json). Both conditional forward predictions remain below that interval. Correct load conditioning does not make this observation agree with the fitted model. The unknown specimen-specific normal load prevents treating this scenario alone as a decisive statistical rejection of the physical law.

## The distributed forward algorithm needs its own checks

The downloaded archive is an example for the larger 0.029 mm³ geometry. Its `bracketz.cmd` prevents a gap below 0.06 mm with this statement.

```text
if(hgt+mv<0.06)then mv:=0.06-hgt;
```

The unmodified example cannot reach Figure 5 gaps near 0.035 mm. Two diagnostic replays replace only that sample-specific floor with 0.0001 mm and set the declared material and load inputs above. They preserve the original `evolve` procedure and its free contact line.

The 4 µm replay times out after 90 seconds. Its last progress rows approach a 34.35 µm gap and 13.55 µm offset, close to the independent pinned balance. It does not finish its declared convergence loop, so it remains a failed replay.

The 5 µm replay reports completion at a 0.25917 µm gap and 159.575 µm offset. It also reports mesh-deletion warnings and substantial contact-line spreading. This collapsed result is rejected. An upstream routine reaching its final print statement does not establish a physical solution.

The raw negative results remain in [compressed receipts](upstream-receipts.json.gz). The archive also contains the three matched fixed-displacement replays and the two final force-balanced replays. Every receipt includes the generated model, commands, and native output. The successful cases also include the exported vertices and triangles.

## What this changes in the product

`JointSpec` owns dimensions, volume, and material inputs. `soldershape/solver.py` generates the trusted numeric model, runs the pinned engine, and derives forces. Native geometry and numerical checks belong in that computation result. The UI and comparison rules consume that result.

The evidence supports keeping the native solver and the current pressure-corrected force formula. A broad replacement wetting model is not yet justified. The immediate model boundary needs to reject solid-plane excursions and invalid contact conditions before a comparison can treat a stable surface as useful solder geometry.

A force-controlled comparison should solve for displacement under declared loads when the assembly is free to move vertically. A fixture-controlled comparison may prescribe gap. The product must state which condition a design decision uses. The two conditions cannot share an unlabeled physical accuracy claim.

Fix Root Causes changed this investigation into a same-input comparison against the original numerical representation. Model the Domain changed the forward experiment into explicit load, displacement, and boundary-condition records. Explain the Number changed the interpretation of the 303.93 µN held-out result. That value includes a low-force fitted surface tension near 0.6682 N/m. At the paper's 0.4 N/m, the same prescribed h6-x6 geometry predicts about 181.94 µN. The physical plane violation remains in either scaling.

The standalone replay command is `python3 evidence/model-repair/upstream-replay.py`. It downloads the source archive only if the pinned local copy is missing. It writes a fresh native receipt for each solve in `.research/model-repair/upstream-replay`. The implementation-only command is `python3 evidence/model-repair/upstream-replay.py --fixed-only`.
