# What the 220 versus 270 µm coupon can establish

C220 is higher under the tested shared boundary and common process shifts. Its advantage is not unconditional. Neither coupon has a qualified 185 µm clearance pass.

These are calculations at artificial planning inputs. No new specimen was fabricated or measured. Sampled scenarios are not probability distributions or continuous uncertainty bounds. The actual coupon has twenty joints and copper at both ends. The older paper's one-cylinder correction is a separate experiment.

## Native decision checks

| Scenario | Assumed boundary | C220 gap, µm | C270 gap, µm | C220 minus C270, µm |
| --- | --- | ---: | ---: | ---: |
| Nominal planning inputs | Top-rim pinning | 223.319 | 207.522 | +15.797 |
| Nominal planning inputs | Full-sidewall envelope hypothesis | 178.203 | 167.314 | +10.890 |
| Opposite requested geometry endpoints | Top-rim pinning | 216.890 | 214.074 | +2.816 |
| Opposite requested geometry endpoints | Full-sidewall envelope hypothesis | 173.209 | 172.366 | +0.843 |
| Opposite ±5% liquid volume and pad endpoints | Top-rim pinning | 213.273 | 217.485 | -4.213 |
| Opposite ±5% liquid volume and pad endpoints | Full-sidewall envelope hypothesis | 170.076 | 175.314 | -5.238 |

At opposite requested pad and sphere endpoints, the predicted advantage is below the requested 3 µm paired measurement uncertainty. Opposite ±5% liquid-volume stress reverses the ranking. That wider volume stress exceeds the screened sphere band and is not a measured process tolerance. Unknown arm-specific wetting can also reverse the ranking.

## Physical model experiment

The finite-pad prototype explicitly represents solid exclusion around prescribed copper wetting depths. Liquid volume and metal-envelope volume remain separate. Gravity is disabled in that envelope. At the declared nominal fixed gaps, both full-wetting cases pass sampled curved-interface checks and fresh relaxed-energy reaction checks. Maximum load residual across both difference steps and the final two mesh levels is 0.003471 µN against a 0.01 µN numerical tolerance. This is numerical consistency, not physical force accuracy.

The C270 moving-height calculation retains a native active-set failure. The deliberately penetrating obstacle control remains intrusive and not converged. Active new contact lacks the required wetting-area energy. The prototype is research only. It supplies no continuous solid-clearance certificate, unique-equilibrium proof, or general loaded finite-pad solver. The public solver is unchanged.

## Twenty-joint coupling

A prescribed 317.5 to 322.5 µm sphere gradient produces 5.34 to 6.23 µm gap variation in the analytical rigid-cap model. This exceeds the protocol's raw 3 µm range comparison even though the sphere endpoints match the requested geometry band before measurement uncertainty. The construction is not a predicted manufacturing frequency. A symmetric volume pattern stays flat but needs tensile joint reactions and exceeds the model's declared applicability screen. All cases remain in the evidence.

## What is supported

Trust the request conversions, retained failure accounting, reproduced native scenario calculations and mechanically balanced analytical examples within their stated assumptions. All six original coupon planning requests reproduce, including actual-liquid gravity controls. Twelve accepted critical requests and one rejected control have fresh identity-checked replay. The analytical spring comparator differs from native gap predictions by at most 0.097 µm across this sampled campaign. That agreement is not a physical error bound.

## Measurements still required

Measure both hot contact-line locations and finished pad heights first. Independently identify solder mass and liquid density, cap mass, the sphere-to-joint placement map, hot local gaps and cap tilt. Qualify the hot-to-cold transformation before treating liquid predictions as cooled clearance. Observe load-displacement behavior separately before qualifying forces. These measurements distinguish causes that fitting one height cannot separate.

See [the lab addendum](LAB_ADDENDUM.md) and [the fixed protocol](protocol.json).

## Reproduce

Use Python 3.12 or newer, the pinned engine, and this Git checkout containing baseline `33666d3`. Offline verification does not run the engine. Finite-pad recomputation uses Git to verify unchanged production sources. New campaign and replay directories must not exist.

```sh
python3 prelab/verify.py
python3 -m unittest prelab.test_campaign prelab.test_replay prelab.test_rigid_cap prelab.test_finite -v
python3 prelab/campaign.py run output/prelab-campaign-new --workers 2
python3 prelab/replay.py output/prelab-campaign-new output/prelab-replay-new
python3 prelab/rigid_cap.py --verify
python3 -m prelab.run_finite output/prelab-finite-new
python3 -m prelab.make_report
```

The original `evidence/replay` and intermediate `evidence/replay-identity-checked` checks are superseded by `evidence/replay-final`. Independent review found missing per-receipt identity checks, including a missing native-engine field on accepted results. The final command requires those fields and the complete campaign was recomputed. Earlier records remain preserved. A matching hash is local integrity, not a digital signature or trusted timestamp.
