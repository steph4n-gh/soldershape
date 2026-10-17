# Rigid-cap mechanics for the coupon

This is a bounded analytical check of the actual five-column, four-row, 0.5 mm pitch array. It tests whether independent equal-load joint heights can establish the twenty-joint cap's gap. They cannot establish that result when the joint volumes differ.

## Mechanical model

Each `SpringJoint` stores its pad position, unloaded pad-face gap, unloaded computational-domain height, and axial stiffness. The existing analytical comparator supplies the spherical height and published Eq. 9 stiffness. No native engine solve runs.

The unknown cap plane is `g_i = H + a*x_i + b*y_i`. Every joint exerts `R_i = k_i*(h0_i - g_i)`. A positive reaction supports the cap. A negative reaction is tensile and remains in the calculation. Micrometers times newtons per meter gives micronewtons.

The rigid plane minimizes the quadratic spring energy plus the applied load potential. Its stationarity equations require total vertical force, moment about x, and moment about y to balance. The implementation solves the resulting three by three system with normalized coordinates and partial-pivot elimination. A collinear array cannot identify both tilts and is rejected.

The 14 mg planning cap gives 137.2931 micronewtons of total load under the declared gravity. Its center of mass is at the array center. Uniform 320 micrometer spheres are the nominal control. The gradient increases the sphere diameter linearly from 317.5 to 322.5 micrometers across the five columns. A separate reflection-symmetric placement assigns 322.5 micrometers to both outer rows and 317.5 micrometers to both inner rows. That case has ten high-volume and ten low-volume joints.

The two boundary interpretations remain separate. Literal rims use the sphere volume directly. Two pad cylinders add the nominal lower and upper metal-cylinder volumes, then subtract 35 micrometers per end from the height. Those are alternative boundary assumptions. Neither is a measured physical contact state.

## What the check can settle

For uniform joints and a centered load, both tilts vanish and each joint carries exactly one twentieth of the cap load. This must reproduce the existing equal-load Eq. 9 value. For equal stiffnesses with unloaded heights on an exact plane, the cap inherits that plane's tilt. A uniform load then shifts its height by `load / total_stiffness` without changing tilt. Tests require those literal results, axis permutation invariance, force and moment balance, singular-geometry rejection, and retention of tensile reactions.

The result records every local gap, reaction, deformation, and independent equal-load estimate. It compares the raw computed joint-site range with the experiment's three micrometer range gate. The comparison cannot apply that physical gate. The requested endpoints have no measurement uncertainty allowance here, and the construction is not measured fabrication capability.

An absolute deformation below one percent of unloaded computational height is a declared engineering applicability screen. It is unqualified. A case outside the screen remains in the evidence. Passing the screen does not bound analytical error, and negative reactions do not establish stable wetting under extension.

## Computed result

The run has twelve cap cases and 240 analytical joint evaluations. It performs no native solve. The largest absolute force residual is below `4e-12` micronewtons. Both moment residuals are also below `4e-12` micronewton millimeters. Those are floating-point mechanical closure checks, not physical accuracy.

| Placement | Boundary | C220 joint-site gap range, micrometers | C270 joint-site gap range, micrometers | Tilt angle, degrees | Tensile joints per cap |
| --- | --- | ---: | ---: | --- | ---: |
| Uniform 320 micrometer spheres | Literal rims | 0 | 0 | 0 | 0 |
| Uniform 320 micrometer spheres | Two cylinders | 0 | 0 | 0 | 0 |
| Left-to-right gradient | Literal rims | 6.154546 | 6.228511 | 0.176314 and 0.178433 | 0 |
| Left-to-right gradient | Two cylinders | 5.375453 | 5.343823 | 0.153995 and 0.153089 | 0 |
| Symmetric outer rows high | Literal rims | 0 | 0 | 0 | 10 |
| Symmetric outer rows high | Two cylinders | 0 | 0 | 0 | 10 |

All gradient cases remain below the declared one-percent deformation screen. Their predicted joint-site ranges exceed three micrometers. The requested sphere geometry band alone therefore does not logically ensure the experiment's gap-range gate, even under this rigid-cap approximation. The finding does not assert how often such a gradient occurs. It identifies the spatial volume map as a measurement or assembly-control requirement.

The symmetric cases stay flat because their moment imbalances cancel. Their ten low-volume joints enter tension. Their largest absolute deformations are 1.75 to 2.08 percent of unloaded computational height, so they fall outside the declared applicability screen. Independent equal-load gaps instead suggest 5.34 to 6.23 micrometers of height range for the same symmetric inputs. The coupled model shows why this independent-joint interpretation is mechanically inconsistent. Its flat result is not a qualified prediction of stable molten shape.

## Falsifiable limitations

The calculation assumes a perfectly rigid cap and a flat carrier. It omits cap bending, local upper-pad rotation effects, lateral forces, and intrinsic joint moments. A measured nonplanar cap displacement field would reject this mechanical model. Measured local gap and placement maps can test the predicted tilt and its sign. Load-displacement measurements at the molten plateau can test the stiffness rather than inferring it from a final height.

The prescribed volume map is not a process distribution. Incoming sphere-to-joint registration, individual sphere metrology with uncertainty, and molten density constrain the actual volume map independently of the gap result. A centered cap load is also an assumption. Each cap's mass, center of mass, and any fixture contact must be identified independently.

Contact-line locations and finished metal heights require section or equivalent metrology. Flux forces, wetting hysteresis, and tensile contact stability are not determined by linear springs. The result covers twenty idealized joint sites. It does not establish an actual whole-cap minimum or laminate clearance. Simultaneous hot gap measurements are required to qualify the liquid model. Cooled gaps additionally require an identified hot-to-cold transformation.

## Design choices

Model the Domain made `SpringJoint` the only mechanical input record and kept the cap solution separate from its sphere-volume construction. Explain the Number required per-joint reactions, force and moment residuals, and the one-percent screen beside the gap range. Prove It Works required literal mechanics tests and an offline recomputation that checks source hashes and all recorded values.

The runner is `python3 prelab/rigid_cap.py`. The independent replay command is `python3 prelab/rigid_cap.py --verify`. The focused tests are `python3 -m unittest prelab.test_rigid_cap -v`. All commands run at the repository root. The only generated result is `prelab/evidence/rigid-cap.json`.
