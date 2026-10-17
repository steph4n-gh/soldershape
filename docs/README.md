# SolderShape documentation

Start with [the Board decision walkthrough](getting-started.md). Compare 40 and 56 nL at a 300 µm held gap, then change the gap to 330 µm and see why the numerical fixture outcome changes. Use the [model and validation reference](model-and-validation.md) to interpret the result. The [visual walkthrough and transcript](media/README.md) show the actual application.

For development, read [development and verification](development.md), [contributing](../CONTRIBUTING.md) and the [local runtime security boundary](../SECURITY.md). [Launch readiness](../launch/READINESS.md) identifies the public-release work.

## Task guides

| Goal | Guide |
| --- | --- |
| Follow a design decision on actual copper | [Board decision walkthrough](getting-started.md) |
| Inspect the board source and numerical binding | [Board explorer reference](../board_demo/APP.md) |
| Inspect a retained extreme example | [Misalignment example](../demo/README.md) |
| Assess the separate 220 and 270 µm clearance coupon | [Current pre-lab findings](../prelab/REPORT.md) |
| Commission a hot-force measurement | [Force-lab handoff](../force_lab/README.md) |
| Quote the separate height coupon | [Coupon handoff](../coupons/README.md) |

## Engineering record

Reports under `evidence`, `refinement`, `cohesion`, `expansion` and `refinement2` are dated development and validation records. Their test counts, ports and source hashes describe their recorded runs. They are not current installation instructions. Historical archives remain unchanged.

- [Numerical acceptance and upstream baseline](../ACCEPTANCE.md).
- [Frozen physical-data validation](../evidence/physical/validation-report.md).
- [Physical model root-cause work](../evidence/model-repair/report.md).
- [Current Board walkthrough and changed-gap verification](../decision_walkthrough/RESULTS.md).
- [Current coupon uncertainty and finite-pad investigation](../prelab/REPORT.md).
- [Conditional volume experiment](../evidence/design-comparison/report.md).
- [Connected workflow verification](../cohesion/RESULTS.md).
- [Readable review verification](../refinement2/RESULTS.md).
- [Current launch audit and verification](../launch/READINESS.md).

Credits, pin identities and component terms are in [THIRD_PARTY.md](../THIRD_PARTY.md).
