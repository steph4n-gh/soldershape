# Coupon architecture judgment

This is an independent judgment of the two completed design notes and the root's proposed revision. The reviewer inherits the parent model family. This is not a cross-family panel. No physical assembly or measurement has occurred.

The experiment should use the root's four-site carrier, one common 3 by 3 by 0.8 mm cap, and a screened 320 micrometer Sn63Pb37 sphere lot. Use Candidate B's separation of physical inputs, frozen predictions, and coded outcomes. Use Candidate A's common carrier and lower assembly count. The result is a staged laboratory comparison of new coupons. It does not reproduce the historical CSP.

## Rubric result

The scores apply the five criteria in `coupons/WORKFLOW.md`. Four is best. Unknown laboratory capability limits both candidates.

| Criterion | Candidate A | Candidate B | Root revision |
| --- | ---: | ---: | ---: |
| Identifiable physical inputs | 3 | 3 | 3 |
| Outside-lab fabrication and assembly | 3 | 3 | 3 |
| Metrology access | 2 | 2 | 2 |
| Isolation of the lower-pad change | 3 | 4 | 4 |
| Number of custom processes | 3 | 3 | 4 |
| Total | 14 | 15 | 16 |

Candidate B is the protocol base. Its eligibility rules, actual minimum-clearance requirement, and forward-prediction separation are stronger. Its 64 assemblies and 80 caps exceed the evidence needed for an initial outside-lab screen. Candidate A supplies the simpler carrier hardware. Its 0.6 mm cap and large board need correction. A four-site carrier is a useful compromise, provided the lab accepts microscope and CT access.

The root revision earns conditional acceptance for package generation. It does not earn fabrication release until the lab accepts DFM, material identification, assembly, and measurement uncertainty. A native CAD parse or clean DRC does not clear those gates.

## Choices to retain

Use one cap geometry and one upper pad diameter for both arms. Keep every lower pad an isolated circle. Use the same full-array mask opening on both arms and the cap. A gang opening avoids a narrow-mask-web fabrication dependency. Confirm that the top cap retains mask between the opening and the routed edge. Do not allow CAM changes to enlarge the pads or introduce exposed traces.

Use adjacent A and B sites as pairs. Mirror their positions between the two blocks of the carrier. Randomize carrier orientation, position, sphere-kit assignment, and placement order before each reflow. Preserve carrier and run IDs. Four sites on one carrier share temperature and board behavior. They are not four independent reflow experiments.

Use 0.8 mm cap thickness as the quote basis. The [JLCPCB dimensions page](https://jlcpcb.com/help/article/pcb-dimensions) currently gives a 3 by 3 mm FR4 minimum at thicknesses of at least 0.8 mm. Its separate capability statement mentions 0.6 mm. The conservative common interpretation avoids an unnecessary quote ambiguity. It does not establish acceptance of the actual panel or its singulation.

Use a custom quote for nominal 320 micrometer spheres. [Indium lists Sn37Pb spheres over an approximate manufacturable range that includes that diameter](https://www.indium.com/products/solder-spheres/). It does not list a confirmed stocked 320 micrometer part in this evidence. Candidate B's 325 micrometer catalog option mixes 0.325 mm and 0.013 inch descriptions. Grading and incoming measurement are necessary under either procurement route. The root's common screened lot is the cleaner specification.

Use measured cap mass. As a planning estimate, 3 by 3 by 0.8 mm FR4 at an assumed 1.85 milligrams per cubic millimeter weighs 13.32 mg. Twenty 280 micrometer pads with 35 micrometer copper add approximately 0.39 mg. The resulting estimate is about 6.7 micronewtons per joint. The old 4 micronewton load must not become a default for this cap. The assumed laminate density is not a measured input.

## Sample count and the pilot

The proposed 24 scored caps give 12 adjacent pairs. Two four-site carriers per run give four pairs in each of three runs. This is a reasonable initial screening count. Neither candidate provides measured cap or paired-difference variance, so neither supports a formal power claim.

The following calculation illustrates the cost of the smaller sample. It assumes independent paired differences with a standard deviation of 4 micrometers. It uses an ordinary two-sided paired Student interval. It does not describe observed variance or a clustered reflow process.

| Scored caps | Pairs | Hypothetical standard error in micrometers | Hypothetical 95 percent interval half-width in micrometers |
| --- | ---: | ---: | ---: |
| 24 | 12 | 1.155 | 2.541 |
| 36 | 18 | 0.943 | 1.989 |
| 48 | 24 | 0.816 | 1.689 |

The calculation is `t.ppf(0.975, pairs - 1) * 4 / sqrt(pairs)`. It was checked with local SciPy. The 24-cap plan loses about 28 percent precision against Candidate A's 36-cap plan under these assumptions. That loss does not make a 6 to 11 micrometer effect inherently unresolvable. Unknown run interactions and measurement uncertainty can still dominate the result.

Four pilot caps give two pairs in one run. That pilot can test ball handling, wetting, and metrology. It cannot establish process variance across reflow runs. Keep a prospective precision gate before scored assembly. Use more pilot blocks in separate runs when the first pilot leaves the variance unclear. Fix any expansion rule before scored outcomes are available.

The proposed quote for ten four-site carriers and forty caps can accommodate twelve pilot caps, twenty-four scored caps, and four spares. The initial four-cap pilot remains the first spending gate. The two additional pilot carriers are a priced contingency. Additional pilots and confirmatory runs need distinct IDs and cannot share outcomes.

Report every run's A-minus-B difference beside the pooled effect. Do not use twenty joints under a cap as twenty independent specimens. A confidence interval based on twelve pairs applies only under its stated assumptions. Three runs provide little evidence about future process variability. A sensitivity interval based on the three run effects is useful even when it is wide.

## Fix the physical hypothesis before scoring

Keep literal opposing pad-face rims as the fixed primary model hypothesis. Use actual liquid solder volume without imaginary copper volume. Retain the two-pad cylinder approximation as a named secondary hypothesis. Do not choose a model family from whichever pilot or scored height agrees best.

Pilot sections may establish whether the primary boundary is physically plausible. They may also make the primary model comparison ineligible. They must not silently exchange the primary and secondary hypotheses. If the contact line moves onto sidewalls, mask, or laminate, report the boundary mismatch. A useful cold pad-size comparison can survive a failed absolute model hypothesis.

The root's gravity-disabled primary model avoids the fictitious copper-liquid body weight in the secondary approximation. Keep the literal-rim body-gravity calculation as a separate sensitivity. Do not turn disagreement between these hypotheses into a fitted density or surface tension. Liquid-density conversion, actual finish height, and contact-line location remain identifiable inputs or explicit uncertainties.

Do not reuse the published one-pad volume correction. Both new coupons have substantial metal thickness. The [2004 paper](https://imapsjmep.org/article/39820.pdf) used a different upper body and reported a silicon CSP. Matching its array and pad diameter does not identify its upper metallization or make this coupon an exact replication.

## Separate the practical result from model qualification

The 185 micrometer threshold is a declared pad-face study threshold. It is not automatically a useful minimum underbody clearance. The actual mask-to-cap clearance also depends on both pad-metal heights and the lower mask surface. Report both datums. A real product decision requires the actual component's clearance requirement and reference surface.

Cold geometry can answer whether the 220 micrometer pads produce more usable clearance than the 270 micrometer pads under the tested assembly process. A cold section alone cannot score absolute molten-equilibrium accuracy. Keep cold comparative performance and liquid model agreement as separate result states.

Request hot-state metrology as a separate priced item. The pilot can establish that a supported cap reaches a stable, observable liquid-height plateau. A held-out liquid model score needs held-out hot-state observations or a separately justified thermal transformation. Without that capability, mark absolute molten-model qualification inconclusive. Do not relabel the cooled result as liquid validation.

The measurement method must demonstrate expanded gap uncertainty at or below 2 micrometers at the relevant dimensions. A voxel pitch or pixel size is insufficient. A full-cap minimum needs full-volume data or an independently demonstrated flatness bound. A single section can establish local gaps only. The carrier's physical size and copper contrast need a pilot test before a CT quote counts as accepted capability.

Kit mass identifies average deposited metal. A random sample of incoming spheres identifies a lot distribution. Neither alone identifies every joint's volume. Quantify how the measured lot distribution affects the cap prediction. Use tight grading or a conservative applicability bound when individual volume variation invalidates equal loading. Preserve failed assemblies in the practical clearance and yield records.

One local calculation explains why the shared lot is useful. For the unloaded literal-rim formula, changing the sphere diameter from 320 to 321 micrometers raises each predicted gap by about 1.25 micrometers. It changes the 220-minus-270 difference by only about 0.014 micrometers. The absolute prediction is more sensitive than the common-lot comparison. This calculation is a sensitivity illustration, not a liquid solder prediction.

## Required stop conditions

- Stop fabrication release if the lab cannot preserve and measure the 220 micrometer circles, custom cap outline, common mask opening, finish, and traceable sphere lot.
- Stop primary model scoring if wetting does not match the frozen boundary, cap warpage or tilt defeats equal loading, or an unrecorded fixture supports the cap.
- Stop minimum-clearance claims if metrology cannot observe the complete relevant volume with a stated uncertainty.
- Stop absolute liquid-model qualification if only cooled outcomes are available without an independently justified thermal transformation.
- Stop the pad-size recommendation if uncertainty does not resolve the group effect or if the conclusion depends on dropping a failed run.
- Stop a 185 micrometer pass claim if the measured minimum minus its uncertainty does not exceed the threshold.

Laziness Protocol changed the hardware choice to one four-site carrier and one cap. Explain the Number changed the sample-count claim to a staged screen with unknown process variance. Prove It Works changed the release gates to actual exported geometry, incoming dimensional measurements, and demonstrated metrology uncertainty.
