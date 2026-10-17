# Load-controlled equilibrium repair

The solver now distinguishes a prescribed wetted-plane gap from a prescribed downward normal load. A `LoadSpec` has geometry, solder volume, offset, material assumptions and per-joint load. It contains no measured height or user-selected optimizer seed. `JointSpec` preserves the existing fixed-gap meaning. This applies Model the Domain by making simultaneous load and gap constraints invalid.

`solve(LoadSpec)` minimizes joint energy plus the potential of the downward load while height and surface shape vary together. The load is attached to a bare vertex constrained to the moving upper plane. The bare vertex contributes no exported solid geometry. The seed comes only from the monotone spherical-segment volume equation.

`V = pi*h*(a*a+b*b)/2 + pi*h**3/6`.

The equation gives the aligned, gravity-free, unloaded spherical geometry under the pinned-rim model. It serves only as an initialization for loaded, offset or gravity-enabled cases. No paper's measured height enters this calculation.

## Acceptance contract

Native free-height results must pass the existing volume, energy stationarity, final Hessian, force refinement and mesh-volume gates. The Hessian now includes the free height degree of freedom. Native height refinement must be at most `max(0.00001 mm, 0.0001*height)`. The upper rim and bare vertex must agree with the reported height within the existing plane tolerance. A detected surface excursion beyond the wetted planes rejects a loaded equilibrium.

Every accepted candidate undergoes a fresh public fixed-gap solve at the computed height. The exported mesh and reported capillary-plus-gravity forces come from this second solve. It must pass the original numerical gates and sampled plane checks. Its upward reaction must match the prescribed downward load within `max(0.01 uN, 2*observed static z-force refinement change)`. This is an engineering numerical tolerance. It is not a physical confidence interval or a certified numerical error bound.

Top-level `input` and its hash always describe the prescribed request. `equilibrium` contains the checked fixed-gap output. Failed loaded requests retain their exact replayable inputs and evidence without an accepted mesh, force or computed equilibrium. `load_balance` records the seed, native delta, native refinement levels, independently verified residual, tolerance and termination.

Execution retains the native timeout and output-size bounds. Each native stage permits the original single additional refinement attempt. Accepted final heights must remain within the existing 0.02 to 10 mm gap domain. Native trial heights have no hard bounds. A locally stable final Hessian does not prove global uniqueness or branch continuation.

## Root causes found during implementation

The native engine's default optimizing-parameter delta produced a plausible height while its net load residual worsened to about -10.37 uN under refinement. Small energy changes and zero negative eigenvalues alone did not establish load balance. That negative architectural experiment is retained in `load-solver.json` with its actual model, commands and logs.

The implementation uses `pdelta = 5e-6 * seed_height_cm`. This rule was chosen from the native derivative scale, independently of physical measurements. A separate fresh fixed-gap reaction provides a mandatory check against a misleading native candidate.

Using the existing 30 gradient steps on each of the first two loaded meshes failed the 60 um offset case from its geometry-derived seed. An early coupled Hessian was indefinite. The solver rejected the warning, even though later reported levels had Hessian index zero. The failed run is retained. Increasing those two initial loaded relaxations to 150 gradient steps removes that warning and produces checked force balance. Fixed-gap commands and acceptance thresholds remain unchanged. No warning was suppressed.

## Measured numerical checks

The retained numerical experiment uses lower and upper diameters 0.27 and 0.28 mm, volume 0.019396687887796915 mm3, surface tension 0.48 N/m, no gravity and a 4 uN load. Geometric scaling multiplies diameters and height by the scale, volume by its cube and load by the scale.

| Geometry scale | Nominal effective gap in mm | Independent normal reaction in uN | Maximum normalized-height spread under half/double delta in mm |
| --- | ---: | ---: | ---: |
| 0.5 | 0.1123402952 | 2.0001968913 | 1.003e-9 |
| 1 | 0.2246806036 | 4.0003257923 | 1.264e-9 |
| 2 | 0.4493611722 | 8.0008324363 | 1.419e-9 |

All nine combinations of those scales and delta factors 0.5, 1 and 2 passed native numerical gates, sampled pad-plane checks and independent fixed-gap load balance. The largest absolute force residual was 0.000838 uN. These measurements qualify the tested submillimeter slice. They do not qualify every accepted input dimension from 0.05 to 10 mm.

For a 0.17 mm lower pad, 0.28 mm upper pad and 0.06 mm offset, starts at 0.9 and 1.1 times the geometry-only spherical seed produced effective gaps 0.2421762240 and 0.2421762899 mm. The difference was 6.588e-8 mm. Their independent reactions were 4.0003037473 and 4.0001204079 uN. This tests initialization sensitivity for one offset branch without using a measured height.

With default density 9 g/cm3 and gravity enabled, the 0.27/0.28 mm case produced effective gap 0.2245110506 mm and independent reaction 4.0003156591 uN against 4 uN. The unchanged default-gravity workflow therefore passes the same numerical balance checks.

The regression checks also verify agreement with the unloaded spherical formula, closed exported geometry, exact request hashes, rejection of mixed physical constraints and retained failure for a 100000 uN unattainable-load test. This applies Prove It Works by checking the public result and independently re-equilibrated reaction rather than accepting a native reported height.

Run from the repository root.

```sh
python3 -m unittest discover -s tests -p test_load_solver.py -v
```

The derivative and start perturbations are part of that test target. Complete numerical receipts, native commands, logs, negative experiments and source hashes are in `load-solver.json`.

## Physical boundary

This repair answers the previously missing physical question of height under a specified load. It adds no contact-angle law, substrate obstacles, package tilt or load redistribution, reflow kinetics, friction or dynamic settling. Sampled exported vertices do not certify continuous-surface clearance or absence of self-intersection. Numerical load balance alone does not establish agreement with a physical soldering process. The independent published-data campaign must decide whether the predicted standoffs and design differences survive measured process uncertainty and comparison with the simple spherical baseline.
