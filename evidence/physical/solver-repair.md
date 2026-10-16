# Thin bridge relaxation repair

The solver now uses energy-decreasing Newton line searches and 30 gradient iterations before each Newton block. This changes three command-list lines in `soldershape/solver.py`. It leaves all numerical acceptance thresholds and native warning rejection unchanged.

The data shape stays `JointSpec -> result`. The result still carries refinement levels, forces, a mesh, numerical diagnostics, the generated model and commands, and native output. No paper force measurement enters the relaxation commands.

## Defect and decisive experiments

The previous solver unconditionally took full Newton steps after only 5 or 10 gradient iterations. Surface Evolver explicitly documents that `hessian` takes the step even when its Hessian is indefinite. A positive Hessian also does not guarantee that a full step decreases the true nonlinear energy. The thin high-offset bridge reproduced destructive energy increases, negative final modes and an invalid mesh. The middle bridge missed the existing stationarity threshold.

The upstream remedy is `hessian_seek`. It searches both directions along the Newton direction and decreases energy whenever it moves. This guarantees a useful local step, not convergence or a global minimum. The unchanged final Hessian, volume, stationarity and refinement checks still decide whether a result passes.

| Candidate | High bridge | Middle bridge |
| --- | --- | --- |
| Original full Newton steps | Native error | Stationarity failure |
| Add `check_increase on` only | Rejected steps raise native warnings | Stationarity failure |
| Replace Newton with `hessian_seek` only | Stationarity failure | Stationarity failure |
| Guarded Newton and 30 gradient steps | Checks pass | Checks pass |
| `hessian_seek` and 30 gradient steps | Checks pass | Checks pass |

The line search with 30 gradient steps fixes both causes. It prevents destructive full steps and gives the surface enough relaxation before the Newton blocks. It avoids special cases for experimental dimensions and avoids relaxing the existing thresholds. The guarded alternative leaves full-step rejection as its recovery method and can discard useful partial steps.

Sources are the [Surface Evolver command reference](https://kenbrakke.com/evolver/html/commands.htm#hessian_seek) and [stability tutorial](https://kenbrakke.com/evolver/html/eigentut.htm).

## Measured numerical results

Both cases use 0.64 mm circular rims, 0.01181699087727595 mm3 volume, surface tension 1 N/m and no gravity. They are free pinned bridges. These numerical checks do not establish correspondence with solid PCB or silicon surfaces.

| Case | Gap mm | Offset mm | Lateral force uN | Negative final modes | Relative stationarity change | Force refinement change |
| --- | --- | --- | --- | --- | --- | --- |
| High bridge | 0.0351 | 0.0310 | -454.847309 | 0 | 2.36e-8 | 1.91e-5 |
| Middle bridge | 0.0347 | 0.0102 | -90.770808 | 0 | 2.70e-8 | 6.23e-5 |

The curved-volume residual is at most 2.87e-16. The flat mesh volume error is at most 0.0157 percent. Both cases pass the unchanged 1e-7 stationarity, 1 percent force refinement and 0.1 percent volume gates after the existing additional refinement attempt.

Fresh simulations at positive and negative offset or gap perturbations independently recomputed equilibrium energy. Their central energy derivatives agreed with the virtual-displacement forces within 1.18e-5 relative. This includes both cases, both force components, and two perturbation sizes for each component. This agreement checks numerical force extraction. It does not validate the material model against experiment.

Six of the eight central Figure 5 pairing candidates pass. Both candidates using the 34.2 um gap remain rejected. Linear initialization, 200 gradient iterations and a bounded native saddle-escape experiment did not produce an accepted solution. Their native warnings and final instability or insufficient stationarity remain in the report. These results do not prove that no stable bridge exists.

## Plane excursions and physical limits

For the six checked central meshes, all except the high bridge remain between the two pad planes to a tolerance of 1e-10 mm. The high bridge has minimum z -0.000267060695 mm and maximum z 0.035367060695 mm for a 0.0351 mm gap. It extends 0.267061 um beyond each plane.

Each plane excursion includes 228 export vertices. All are outside the corresponding 0.320 mm pad radius. Their radial positions are 0.320236 to 0.327234 mm. No excursion vertex is inside either pad. The model has no solid-substrate exclusion or wetting transition. This shape therefore needs a separate physical-regime assessment before comparison with a solid substrate. Positive stability of this free-bridge model does not remove that limitation.

## Reproduction

Run from the project root after building the pinned engine.

```sh
python3 tools/setup_engine.py
python3 -m unittest discover -s tests -v
python3 tools/verify.py
python3 evidence/physical/solver-repair.py
```

All 13 unit tests passed with no skips. This includes the new real-engine thin-bridge regression and fresh re-equilibrated energy comparisons in x and gap. The prior verification passed its 11 numerical cases, original upstream reference cases, export geometry checks and bundle replay. The standalone replay preserves the old command schedule as an explicit negative control and writes `output/solver-repair-replay.json`.

The detailed measured results, native warning excerpts, command hashes, initialization failures, plane excursions and derivative checks are in `solver-repair.json`. Large experiment receipts remain at their recorded local research paths. The standalone replay reproduces the central defect and repaired derivative checks without those paths.

The baseline solver SHA256 was `b1bfc098127c2e54db166807f957fb7457384cd9b6d06b6127d49ff652de4154`. The repaired solver SHA256 for these measurements is `07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98`. The engine identity is included in the JSON report. Measurements used the same pinned native binary and source archive. No upstream numerical code changed.

The principles applied were Fix Root Causes, which replaced unsafe Newton steps, Model the Domain, which retained the existing `JointSpec` and evidence result, and Prove It Works, which required fresh solves and energy derivative checks. Explain the Number kept numerical agreement separate from physical validation. Recorded elapsed times are single executions, not a performance comparison.
