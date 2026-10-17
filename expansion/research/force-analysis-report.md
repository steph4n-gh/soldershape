# Force experiment scientific core

Implemented the new isolated-force experiment under `force_lab/`. The old loaded-height coupon and all numerical model/solver code remain untouched. The 48 specimen allocation comprises three independent preparation blocks, two independently prepared pairs per axis and offset, two force axes, two offsets and two volumes. Dwell frames, reversal observations and repeated force samples do not add specimens.

`force_lab/tools/analyze.py` owns blank templates, unqualified numerical planning, exact-byte prospective freezing, freeze verification and later outcome scoring. Uncertainty is represented by independent source components with signed coefficients. A shared bias therefore stays shared across the six specimens. This is full covariance represented as a sum of positive semidefinite source outer products. Each physical input and force observation must have positive quantified uncertainty and independently supported budget completeness. No generic matrix framework or extra dependency is required.

Freeze consumes geometry/liquid-volume records, material/process evidence, input covariance and commissioned force calibration. It rejects any existing `outcomes.csv`, incomplete uncertainty, unsupported interface/gravity, unknown commissioning and unverified temperature or material inputs. It snapshots the bytes it parses. It records source identity and all native evidence. Scoring requires the independently registered manifest digest. A changed manifest or receipt fails. Input timestamps must precede the freeze. Force outcomes must follow it. Unknown wetting, instability, hot-coordinate departure, excessive tilt/drift and missing outcomes are inconclusive. Model disagreements remain visible in individual and preparation-block assessments.

The prospective protocol requires actual hot rim geometry observed with the force channel blinded. A cold stage setpoint does not establish these inputs. Freeze registration precedes confirmatory force acquisition. A repeated thermal cycle must independently reestablish the frozen coordinates within their declared interval. This is a lab acceptance requirement. If operationally impractical, revise the protocol prospectively rather than quietly acquiring force outcomes before freezing.

The force model remains physically unqualified. Local covariance propagation is a first-order screen. The numerical guard adds refinement changes and one-at-a-time central-step midpoint nonlinearities. It does not bound mixed interactions, unmodeled wetting chemistry, hysteresis, surface oxide, thermal gradients, tilt or physical discrepancy. No statistical sample-size guarantee or production release follows from agreement.

Model the Domain shaped the separate protocol, immutable freeze and later observations. Prove It Works shaped the recorded native receipts and executable synthetic negative controls. Explain the Number separated covariance, force measurement uncertainty, numerical checks and unmeasured planning allocations.

## Measured numerical results

Twenty distinct native requests comprise two central cases, fourteen forward perturbations, and four additional negative-side gap/volume perturbations. Every request passed numerical refinement and sampled plane checks. This is numerical agreement only. At 120 um offset the unchanged solver gives Fx=-92.26328365 and -82.19306382 uN for 5 and 7 nL. The restoring-magnitude contrast is 10.07021982 uN. The 7 nL normal force is +7.61948089 uN.

With independent expanded force-measurement U=2 uN per specimen, the one-pair measurement contrast U is 2.82842712 uN. A three-to-one contrast discrimination margin permits total guard at most 3.35673994 uN, leaving input-prediction U at most 1.80767891 uN before numerical guards. For the normal 3 uN combined gate, measurement U=2 leaves input U at most 2.23606798 uN.

The initial unmeasured expanded-input allocation has each rim D, gap and offset U=0.5 um, volume U=0.1 nL, gamma U=0.0048 N/m and density U=0.09 g/cm3. It yields 7 nL normal input U=5.26561853 uN and combined guard=5.64430438 uN. It fails the 3 uN normal gate. Its lateral contrast guard=3.12566225 uN passes the proposed contrast screen.

A tighter unmeasured candidate uses D and gap U=0.25 um, offset U=0.5 um and volume U=0.02 nL, with the same material uncertainties. It yields normal input U=1.39898500 uN and combined guard=2.45238424 uN. Its lateral contrast guard=2.88831945 uN. Both pass the local planning screen. Neither allocation is measured sensor or lab capability. Geometry/volume are independent between specimens. Gamma and density are fully shared between volumes. Other source groups are independent. No ensemble averaging is assumed.

One-source full-budget normal limits at 7 nL are gap U=0.621 um or liquid-volume U=0.04578 nL. Each consumes the whole input budget alone. These are not simultaneous tolerances. The near-zero lateral density sensitivity is below useful numerical resolution and its very large algebraic single-source limit is not a practical tolerance.

## Verification commands

```sh
cd /Volumes/Storage/oct16project
python3 -m unittest discover -s force_lab/tests -v
python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120
python3 force_lab/tools/analyze.py plan output/force-plan-fresh
python3 force_lab/tools/analyze.py templates output/force-lab-blank
```

The behavior suite passes 14 synthetic controls. Exact-force synthetic observations can pass the declared screen. Inverted force signs fail. A common +50 uN x bias can leave the volume contrast unchanged but the overall absolute-force assessment fails. Opposing preparation-block biases cannot disappear in an overall mean. Shared systematic uncertainty does not shrink by sqrt(n). Unknown wetting, unstable force, coordinate drift, incomplete uncertainty, duplicate dwell frames, pre-existing outcomes and tampered frozen bytes all reject qualification. The shipped physical templates are blank.

A prospective freeze can only be made after independent commissioning and physical input measurement. Its later commands are:

```sh
python3 force_lab/tools/analyze.py freeze INPUT_DIRECTORY NEW_FREEZE_DIRECTORY
python3 force_lab/tools/analyze.py verify NEW_FREEZE_DIRECTORY --manifest-sha256 REGISTERED_SHA256
python3 force_lab/tools/analyze.py score NEW_FREEZE_DIRECTORY OUTCOMES.csv NEW_SCORE_DIRECTORY --manifest-sha256 REGISTERED_SHA256
```

The output freeze directory must not already exist. Confirmation `outcomes.csv` must not exist at freeze. The blank `outcomes-template.csv` is intentionally separate. Register the exact returned manifest digest independently with the lab before confirmation. A coverage factor other than justified k=2 requires a prospective protocol revision.
