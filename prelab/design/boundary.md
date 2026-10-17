# Finite copper and wetting boundary design

This is a design candidate grounded at commit `33666d32c92b6753925bb2fd29dc62ce5fed618b`. It changes no product source or historical evidence. The intended reader is the engineer deciding which pre-lab calculations can support the C220 versus C270 coupon choice.

## Grounding

`JointSpec` in `soldershape/model.py` describes prescribed pad-face gap. `LoadSpec` describes prescribed normal load and contains no gap. Both describe circular pinned contact lines, volume, offset, surface tension, density, and a gravity switch. The public request has no copper thickness, sidewall wetting, contact angle, or substrate geometry.

`soldershape/solver.py::_model` builds a six-sided seed in centimeters. Two zero-tension cap facets close its volume. The lateral facets carry surface tension. The circular rims are fixed. The native model uses quadratic elements after `M 2`. Body pressure is the volume multiplier. Force commands use a pressure-corrected virtual energy derivative.

For a `LoadSpec`, height is an optimizing parameter. A bare vertex adds the external load potential. `solve_loaded` first minimizes shape and height together. It then performs a separate fixed-gap solve and checks the upward reaction against the applied load. Existing gates cover refinement, volume, stationarity, Hessian index, mesh volume, sampled plane excursion, and this second load check. These gates establish numerical consistency for a local branch. They do not establish correct wetting, solid exclusion over entire curved facets, or physical accuracy.

`coupons/tools/analyze.py::request` converts solder kit mass to per-joint liquid volume using a supplied liquid density. It converts measured cap mass to an equal load per joint. Its `literal_rims` mapping uses the solder volume directly. Its `two_pad_cylinders` mapping adds both copper cylinder volumes, solves between their bases, and subtracts both thicknesses from the solved height. The second mapping has no explicit copper obstacle. It is not presently a qualified physical boundary model.

The actual coupon has 20 joints, a 280 µm upper pad, lower pads of 220 or 270 µm, nominal 35 µm metal at both ends, and a 320 µm sphere. The large mask window is remote from each pad. The planning cap mass is 14 mg, giving 6.864655 µN per joint under equal sharing. These are planning assumptions. The paper comparison instead uses 4 µN, 0.01745 mm³ solder, and one 34 µm substrate cylinder. The paper's mapping must remain separate.

The existing six coupon planning receipts contain the decisive nominal sensitivity.

| Assumed boundary | C220 gap, µm | C270 gap, µm | C220 advantage, µm |
| --- | ---: | ---: | ---: |
| Top-rim pinning, no gravity | 223.318802 | 207.521815 | 15.796987 |
| Two copper cylinders, no gravity | 178.203381 | 167.313878 | 10.889503 |
| Top-rim pinning, gravity | 223.129283 | 207.399461 | 15.729822 |

The first pair exceeds the 185 µm requirement. Both cylinder-mapped values fall below it. Thus nominal absolute clearance is already boundary dependent. If the arms are allowed different wetting states, C220 in the cylinder case is 29.318434 µm below C270 with top-rim pinning. This cross-case comparison does not prove different real wetting. It proves that a shared-boundary assumption matters to the design ranking.

Sources are `coupons/experiment.json`, `coupons/evidence/planning/plan.json`, and `evidence/model-repair/report.md`. The model-repair report also retains a published offset discrepancy and failed free-contact replays. No new boundary may be described as explaining those failures without a separate forward comparison.

## Two representations

The first representation uses the actual liquid domain. It includes the free liquid surface, explicit wetted copper surfaces with solid-liquid energy, finite copper solids, substrate obstacles, and a movable contact line. Its energy is

\[
E=\gamma A_{LV}+(\gamma_{SL}-\gamma_{SV})A_{SL}+\rho g\int_{V_L}z\,dV+Wh.
\]

An equilibrium contact angle imposes `gamma_SL - gamma_SV = -gamma*cos(theta)`. Pinning and hysteresis need an admissible contact-line range or a history law. The existing input evidence does not identify those material and process conditions. This representation also needs topology handling at the pad edge. It adds too many unmeasured inputs for the first decisive experiment.

The second representation uses a closed envelope containing liquid plus a known portion of each copper cylinder. It keeps prescribed circular contact lines and adds explicit solid exclusion. Wetted sidewall depth is a declared boundary hypothesis. It does not infer depth from observed gap or fit it to improve agreement. The envelope is the smaller credible first experiment because it can test whether the existing volume approximation is geometrically admissible before adding a contact-angle law.

## Chosen finite-pad experiment

Let the lower and upper radii be `rL` and `rU`. Let their metal thicknesses be `tL` and `tU`. Let prescribed wetting depths be `dL` and `dU`, each between zero and its metal thickness. The physical gap `h` is measured between opposing finished pad faces. Offset `s` translates the upper pad along x.

Choose envelope coordinates with the lower contact circle at `z=0` and the upper contact circle at `z=H`. Then

\[
H=h+d_L+d_U,
\qquad
V_{env}=V_L+\pi r_L^2d_L+\pi r_U^2d_U.
\]

The lower copper occupies `dL-tL <= z <= dL`, with `x²+y² <= rL²`. The upper copper occupies `H-dU <= z <= H-dU+tU`, with `(x-s)²+y² <= rU²`. Substrate planes are `z=dL-tL` and `z=H-dU+tU`. At full sidewall wetting, the contact circles coincide with those substrate planes. At zero depth, this reduces to top-rim contact geometry.

For the full-wetting test, require the free envelope to satisfy

\[
z\ge0,\quad H-z\ge0,
\]
\[
\max\left(z-t_L,\frac{x^2+y^2-r_L^2}{2r_L}\right)\ge0,
\]
\[
\max\left(H-t_U-z,\frac{(x-s)^2+y^2-r_U^2}{2r_U}\right)\ge0.
\]

These inequalities exclude the finite cylinders and the supporting substrates. Scaling the radial term by `2*r` gives each argument length units. `maximum(a,b)` is Evolver's expression syntax. The maximum is nonsmooth where the arguments agree. That seam is a numerical risk to test, not a reason to smooth the obstacle and silently change its geometry.

For partial depths, replace the lower obstacle's first argument by `z-dL` and the upper obstacle's first argument by `H-dU-z`. Use the actual substrate planes stated above. Preserve the pinned contact circles. A partial-depth result also needs to reject new wall contact beyond the prescribed wetted region. Otherwise the fixed wetted-area assumption has changed.

Apply constraints to the free facets and edges as well as their vertices so refinements inherit them. A zero-tension cap passes through its corresponding copper interior by design. It is an envelope closure, not a liquid-air facet. Never count those caps as copper intrusion. Keep the bare load vertex separate from free-interface contact checks.

Evolver supports one-sided constraints. Its documentation says Hessian moves do not check whether an active one-sided constraint should release. Interleave gradient steps with Hessian steps. A positive constrained Hessian alone cannot establish the correct active set. Check the constraint values, release behavior, and displaced controls independently. [Constraints and boundaries](https://kenbrakke.com/evolver/html/constrnt.htm).

### Exact scope of the envelope energy

When both wetted depths stay fixed and the free surface does not create new wall contact, the wetted sidewall area is constant. Its omitted contribution is

\[
-\gamma\cos\theta_L\,2\pi r_Ld_L
-\gamma\cos\theta_U\,2\pi r_Ud_U.
\]

This constant does not change a derivative with respect to `h` or `s`. The cylinder-volume identity is exact bookkeeping for this restricted geometry if the envelope contains the stated cylinder portions and its free surface stays outside copper. It does not establish that either fixed contact line occurs in the assembly.

If an obstacle becomes active over new interface area, keeping that area at liquid-vapor tension is generally the wrong wetting energy. Such a result can test geometric exclusion but cannot receive a physical wetting interpretation. Retain it as an active-contact stress result or reject physical eligibility. An independent force derivative cannot repair a missing energy term. [Evolver's contact-angle derivation](https://kenbrakke.com/evolver/workshop/html/day2.htm).

Keep gravity disabled in the envelope experiment. Assigning liquid density to the full envelope includes fictitious copper-volume weight. The upper phantom volume would add a false height derivative of `rho*g*pi*rU²*dU`. Correct gravity would require subtracting both phantom cylinder potentials. That subtraction is unnecessary for this first experiment because a separate literal-rim gravity control already measures the size of that effect. [Evolver gravitational energy](https://kenbrakke.com/evolver/html/energies.htm).

The cap load potential can use `W*H`. Its difference from `W*h` is the constant `W*(dL+dU)`. The supported cap mass excludes solder mass, as in the existing coupon specification.

### Force calculation

For fixed volume and prescribed depths, compute fresh relaxed capillary energy at `H-delta` and `H+delta`. Move the upper copper obstacle with `H`. The upward normal reaction is

\[
F_z\simeq-\frac{E^*(H+\delta)-E^*(H-\delta)}{2\delta}.
\]

Repeat at half delta and one extra mesh level. Offset reactions similarly move the upper circle and its copper obstacle together. This independently checks the loaded solution. Do not reuse the bare model's affine virtual deformation when a solid constraint is active. Such a deformation can move vertices through copper and omit work associated with the moving obstacle.

Direct energy differences need a step large enough to exceed minimization noise and small enough to converge. Preserve all displaced solves. At a contact transition, report one-sided derivatives and the branch change. Do not average that transition into an apparently precise force.

## Data shape and ownership

Keep the experiment in `prelab/`, separate from public `JointSpec`, historical coupon predictions, and the released solver. The caller uses one explicit request.

```python
request = FinitePadRequest(
	liquid=LoadSpec(..., gravity=False),
	lower_metal_mm=0.035,
	upper_metal_mm=0.035,
	lower_wetting_depth_mm=0.035,
	upper_wetting_depth_mm=0.035,
)
result = solve_finite_pad(request, receipt_directory)
```

The proposed structures and signatures are

```python
@dataclass(frozen=True)
class FinitePadRequest:
	liquid: LoadSpec
	lower_metal_mm: float
	upper_metal_mm: float
	lower_wetting_depth_mm: float
	upper_wetting_depth_mm: float

def envelope_spec(request: FinitePadRequest) -> LoadSpec: ...
def native_model(request: FinitePadRequest, gap_mm: float | None) -> str: ...
def solve_finite_pad(request: FinitePadRequest, directory: Path) -> dict: ...
def verify_receipt(directory: Path) -> dict: ...
```

Validate finite values, positive metal thickness, depths in range, and disabled gravity at the outer request boundary. The request hash covers liquid inputs, metal dimensions, depths, boundary representation, and version. The result distinguishes liquid volume, envelope volume, envelope height, face gap, contact activity, numeric status, and physical eligibility. A failed run has no accepted face gap. Every request retains model text, commands, native logs, engine identity, source identities, and file hashes.

Do not add a model plugin system or a second production solver API. Model the Domain changed the sketch by separating liquid geometry, finite copper geometry, and the boundary hypothesis. Laziness Protocol changed the scope by keeping one research calculation path and the existing production interfaces.

The smallest adapter can run each finite-pad request in its own Python subprocess. That process imports the pinned production solver, obtains its trusted generated model, and inserts the finite-pad constraints with checked single replacements. The process may replace the generator callable locally to reuse the existing native execution and numerical checks. It must record the adapter hash and generated model rather than identify the result as an unchanged production solve. The parent process and running web app retain their original imports. Each child exits after its receipt is complete. This contains research behavior without a production API refactor or concurrent shared configuration.

Keep all original acceptance thresholds. Add gradient iterations between Hessian calls for this constrained path. If the experiment requires repeatedly overriding unrelated parser or acceptance behavior, reject the adapter approach and keep a small direct native runner instead. Isolation does not justify reusing the bare reaction formula for active-contact physical interpretation.

## Acceptance controls

1. Reproduce all six existing coupon planning requests without altering them. Compare actual coupon values separately from the four-row published case.
2. At zero depth with inactive obstacles, agree with the existing literal-rim native result within observed force and height refinement differences. At full depth with inactive obstacles, agree with the existing cylinder mapping. Agreement verifies implementation, not wetting truth.
3. Verify envelope volume minus both cylinder portions equals the requested liquid volume. Preserve actual solid thickness and contact depth separately.
4. Use a positive negative-control geometry that penetrates a finite copper slab in the unconstrained model. The new model must exclude that geometry or fail. A constraint that never activates in any control is untested.
5. Retain the existing volume, stationarity, refinement, Hessian, output-size, and timeout gates. Add constraint-residual and contact-activity records. Do not weaken an existing gate to make an obstacle run succeed.
6. Check fresh energy-derivative reactions and applied-load balance at two deltas and an extra refinement. Preserve failures and nonunique starts. If the active-contact energy is unimplemented, exclude active-contact runs from physical decision claims.
7. Sample the curved free facets for copper and substrate intrusion before flattening. State that finite samples do not prove continuous clearance. If continuous exclusion becomes decision-critical, bound quadratic patches by subdivision or retain the uncertainty instead of claiming certification.
8. Test shared wetting hypotheses and arm-specific combinations. Keep scenario samples distinct from interval bounds or measured probability distributions.

## What this can decide

The experiment can establish whether finite-pad geometry is compatible with a chosen fixed wetting state. It can show how much an absolute clearance or relative ranking changes under stated states. It can falsify an obstacle implementation with a penetrating control. It cannot identify the actual sidewall wetting state from nominal dimensions, or turn numerical agreement into a physical error budget.

The outside lab still needs measured finished pad geometry, actual deposited solder mass, liquid density at the plateau, wetting extent at both ends, and hot gap. Cold sections alone do not identify hot equilibrium. The existing cold cross-section comparison remains useful but cannot separate wetting error from thermal contraction or solidification effects.

The equal per-joint load assumption also remains conditional. Unequal local volumes and cap tilt couple the 20 joints. A future rigid-cap calculation would solve one height and two tilt angles with total force and two moment balances. An isolated-joint scenario is insufficient to qualify the minimum gap across a cap. The present campaign should report that gap rather than implying multi-joint qualification.

For aligned low-load cases, keep the analytical spherical-gap and spring correction as a comparator. The existing published-data report finds essentially the same accuracy as the native solver. Finite copper alone does not justify a more general optimizer or a Rust port. [The source paper's volume correction and physical comparison](https://imapsjmep.org/article/39820.pdf).

The useful result is a conditional recommendation with the missing measurement named. If C220 wins only when both arms share a wetting state, report that dependence. If both arms cross 185 µm when plausible wetting states change, neither arm has a qualified clearance pass before the lab identifies the boundary state.
