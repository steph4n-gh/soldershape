# Fresh review of the repaired laboratory package

The reviewed package is suitable for an outside-laboratory quote and a staged pilot. No blocking defect remains from the earlier manufacturing and science reviews. This is not a fabrication release, proof of laboratory capability, or a physical validation result.

This review used a fresh agent in the same inherited model family as the implementation. It is independent work within that family. It is not a review across different model families. The reviewer changed only this report. The repository base was `3f6ff5c2246a3f62c37f9cab4bd59bc4679d4f79`.

## Reproduce the checks

`python3 -m unittest discover -s coupons/tests -v` passed all 25 tests. Twenty-one checks exercise the prospective analysis and four exercise delivered CAM, including altered exports that must fail. Analysis fixtures explicitly use synthetic solver results. They are not native or laboratory data.

The reviewer independently recreated the earlier three false-pass examples through the actual `freeze` and `score` functions. Each used a fresh temporary directory and the labeled synthetic fixture only to avoid substituting a native solve for a data-validation check.

| Earlier false pass | Current measured result |
| --- | --- |
| No wetting or contact-line observations, with generic `defects=none`. | An explicit `unobserved` state with no wetted-joint count leaves the liquid verdict inconclusive and fails the geometry gate. Direct measured clearance remains separate. |
| Maximum minus minimum is 3 micrometers, with 2 micrometers expanded uncertainty at each endpoint. | The guarded range is 7 micrometers. The geometry gate fails and the liquid verdict is inconclusive. |
| Both the frozen material temperature and rows labeled molten are at 20 degrees Celsius. | The freeze raises `DataError` because its entire temperature interval must exceed the declared 183 degree liquidus. It creates no freeze directory. |

The reviewer also removed the hot-method evidence. Hot clearance, hot process direction, and liquid-model agreement then remain inconclusive. The cold workflow remains available. Current code requires observed molten temperature intervals to fit wholly inside the frozen interval. Large uncertainty cannot create eligibility through interval overlap.

The code requires an observed wetting count and evidence. A claimed matching boundary requires twenty wetted joints. An observed or unobserved contact-line boundary can leave the empirical comparison usable when all twenty joints are observed wetted. It cannot qualify the primary liquid model. A supplied correlated range budget requires its evidence reference. These rules preserve applicability failures without turning them into a successful model fit.

## Check actual manufacturing outputs

The reviewer ran the current Gerber and drill verifier against a temporary copy of the actual delivered files. This preserved the read-only scope. Both DRC reports contain zero violations. The resulting geometry digest is `9015bd4a21b7a26b3b89d791e19c4d54c504a6e759faf402d01f85bec561eb96`.

The carrier has eighty isolated joint pads, three fiducials, four common array mask windows, two 3.2 mm nonplated holes, and a 40 by 40 mm outline. Forty joint pads are 220 micrometers and forty are 270 micrometers. The cap has twenty 280 micrometer B.Cu pads, one common mask window, no holes, and a 3 by 3 mm outline. Both opposite copper layers are empty. The delivered mask windows are 2.8 by 2.3 mm. The checker confirms actual coordinates and apertures rather than trusting the CAD generator.

The final allocation has one 0 degree carrier and one 90 degree carrier in each of R1, R2, and R3. Each orientation accounts for four caps per run. This exchanges the arm diagonals in the external oven frame. The procedure explicitly retains the carrier-site fabrication confound as a limitation.

The cap-orientation instruction now agrees with the native layers and drawing source. F.SilkS faces outward, B.Cu faces the carrier, and the L corner aligns with carrier A1 in a common top view. The rectangular grids align before the whole carrier is rotated. The drawing reads the actual Gerber geometry and explicitly presents the cap through its outer face in the same top-view axes. Bottom CAM is not manually mirrored.

Sphere acceptance now guards the entire measured interval inside 317.5 to 322.5 micrometers, with expanded diameter uncertainty at most 1 micrometer. Procurement and the RFQ state the same rule. Exact supply and screening yield remain quote conditions. The package does not claim stock or a proven tolerance grade.

The procedure now places all confirmation caps and measures their actual offsets before freezing predictions. Confirmation reflow occurs after the completed freeze. Pilot qualification must include the complete placement and flux dwell through data transfer, computation, review, and scheduling. Nominal zero offsets cannot replace the actual measurements.

## Inspect retained native receipts

The retained planning report contains six distinct requests. The reviewer decompressed every referenced receipt and verified its request hash, accepted refinement status, balanced load, and conversion to the reported pad-face gap.

| Arm | Literal rims, gravity off | Two-pad cylinders, gravity off | Literal rims, gravity on |
| --- | --- | --- | --- |
| C220 | 223.318802 micrometers | 178.203381 micrometers | 223.129283 micrometers |
| C270 | 207.521815 micrometers | 167.313878 micrometers | 207.399461 micrometers |

The planning report is labeled `NOT_FROZEN_NOT_PHYSICAL_DATA`. Its artificial assumptions do not establish a laboratory prediction. In particular, the literal and secondary approximations put both arms on opposite sides of the study threshold. This remains a question for the experiment. No prior physical negative result was removed or recast as a success.

## Snapshot hashes

Paths in this table are relative to `coupons/`. Hashes identify the reviewed files before final packaging. The final archive manifest must identify its own complete contents.

| File | SHA-256 |
| --- | --- |
| `experiment.json` | `37032dfbc39ea9eae3e970be1e0de074f60095355ee55307cf19f774f67de3ed` |
| `allocation.csv` | `4592fad81013c715ce3c3420beb04ac730828a086942929185b3614a0b12f300` |
| `tools/analyze.py` | `c653cd2d4812837bcecc63fca386b5a6bf8b40a3f62cd8d9c724560161144683` |
| `tests/test_analysis.py` | `80fb70e628ec6dbea199b7a787494b5b3980d817fe76782294b3c9455ad661a6` |
| `tools/build_boards.py` | `c05b2449a3123fff3f77cb791efcdd4c80361af25823bfd6b1fd854d7d493e0f` |
| `tools/verify_boards.py` | `8fc9632c98e9cdbbea95f43daf144748e4d405b26035c4f9e8bb95482aaa1ff0` |
| `tools/make_lab_pdf.py` | `1b1ad4e0b232a4d8fa1e620be00d5ddf4f2fe07646ed313be41594e902ca165b` |
| `PROCEDURE.md` | `1a52884a920135a75ecfe4d2cf0a658fb15c33fef039c10cfd5396c31afc7ae8` |
| `PROCUREMENT.md` | `e82474eef4d8f9d2b2e2789e347c8108b917db8069fbdc28a3a4f1e26f7cf6e8` |
| `LAB_RFQ.md` | `7c052f2d83a4fd2373b0bd1d6e521c0239bc63b86468978f2959320ae4e8ea0d` |
| `BOM.csv` | `ff8387e71fa94c356b0609ff150d885ddea46ea9b56f261dd9cef550c18ae874` |
| `hardware/carrier.kicad_pcb` | `9976208a4eccc9283be8ffb97ab59692ff616cf91db48a98f28a62d219f37369` |
| `hardware/cap.kicad_pcb` | `bb44eff41333166c46d8cc448e45040745bb9ea4ce6b1efad5326ba9c81655f6` |
| `evidence/fabrication-verification.json` | `ab9d8a48967a8cd01a67fcdde8e98799726feec5ff2c52a0b6d8700fc79b526c` |
| `evidence/planning/plan.json` | `cbfd80822cd1c5a5be632e4cace60ca01ccf3b294d54d73c2983e9da9676c181` |

## Conditions on the verdict

The laboratory still has to accept DFM, exact materials, free-settling assembly, panel handling, and the required measurement uncertainty. Its pilot can fail. A cap-specific incoming mass and kit mass are necessary. Equal joint loading, contact-line geometry, thermal expansion, material inputs, and native input uncertainty remain physical assumptions to test or bound. The current scorer reports consistency at frozen central inputs. It does not propagate a native prediction interval or prove the laboratory's certificates.

Cold results can support the stated coupon and process comparison. They cannot qualify liquid equilibrium. Hot observations require the separately qualified method, plateau, uncertainty, and boundary evidence. Neither path validates restoring forces, electrical reliability, fatigue, production yield, or a general pad-size rule. The current fixed-site carrier design also limits causal separation of pad diameter from a carrier-site fabrication effect.

Prove It Works changed this review from a reading of passing tests to executable prior counterexamples, direct CAM checks, and decompressed native receipts. The final regenerated PDF still requires visual inspection by the root agent. This review inspected its drawing source and orientation semantics, not its final rendered pages.
