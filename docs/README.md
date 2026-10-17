# SolderShape documentation

Start with [one complete Board comparison](getting-started.md). Use the [model and validation reference](model-and-validation.md) to interpret the result. The [visual walkthrough and transcript](media/README.md) show the actual application.

For development, read [development and verification](development.md), [contributing](../CONTRIBUTING.md) and the [local runtime security boundary](../SECURITY.md). [Launch readiness](../launch/READINESS.md) identifies the public-release work.

## Task guides

| Goal | Guide |
| --- | --- |
| Compare one joint on an actual board | [Board explorer](../board_demo/APP.md) |
| Inspect a retained extreme example | [Misalignment example](../demo/README.md) |
| Compare the 220 and 270 µm pad hypothesis | [Pad study and physical root cause](../PHYSICAL_ROOT_CAUSE.md) |
| Commission a hot-force measurement | [Force-lab handoff](../force_lab/README.md) |
| Quote the separate height coupon | [Coupon handoff](../coupons/README.md) |

## Engineering record

Reports under `evidence`, `refinement`, `cohesion`, `expansion` and `refinement2` are dated development and validation records. Their test counts, ports and source hashes describe their recorded runs. They are not current installation instructions. Historical archives remain unchanged.

- [Numerical acceptance and upstream baseline](../ACCEPTANCE.md).
- [Frozen physical-data validation](../evidence/physical/validation-report.md).
- [Physical model root-cause work](../evidence/model-repair/report.md).
- [Current coupon uncertainty and finite-pad investigation](../prelab/REPORT.md).
- [Conditional volume experiment](../evidence/design-comparison/report.md).
- [Connected workflow verification](../cohesion/RESULTS.md).
- [Readable review verification](../refinement2/RESULTS.md).
- [Current launch audit and verification](../launch/READINESS.md).

Credits, pin identities and component terms are in [THIRD_PARTY.md](../THIRD_PARTY.md).
