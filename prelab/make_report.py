"""Build the readable pre-lab report from independently verified evidence."""

from html import escape
import json
from pathlib import Path

from prelab.verify import EVIDENCE, ROOT, verify_all


def build():
    verification = verify_all()
    report = json.loads((EVIDENCE / "campaign/report.json").read_bytes())
    rigid = json.loads((EVIDENCE / "rigid-cap.json").read_bytes())
    names = {"nominal": "Nominal planning inputs", "opposed-requested-endpoints": "Opposite requested geometry endpoints",
             "opposed-wider-volume": "Opposite ±5% liquid volume and pad endpoints"}
    rows = [row for row in report["pairs"] if row["scenario"] in names]
    mapping = {"literal_rims": "Top-rim pinning", "two_pad_cylinders": "Full-sidewall envelope hypothesis"}
    markdown_table = ["| Scenario | Assumed boundary | C220 gap, µm | C270 gap, µm | C220 minus C270, µm |",
                      "| --- | --- | ---: | ---: | ---: |"]
    html_rows = []
    for row in rows:
        values = [names[row["scenario"]], mapping[row["mapping"]],
                  f'{row["arms"]["C220"]["gap_um"]:.3f}', f'{row["arms"]["C270"]["gap_um"]:.3f}',
                  f'{row["C220_minus_C270_um"]:+.3f}']
        markdown_table.append("| " + " | ".join(values) + " |")
        html_rows.append("<tr>" + "".join("<td>"+escape(value)+"</td>" for value in values) + "</tr>")
    gradients = [arm for row in rigid["cases"] if row["scenario"] == "left_to_right_gradient" for arm in row["arms"].values()]
    gradient_range = f'{min(x["joint_gap_range_um"] for x in gradients):.2f} to {max(x["joint_gap_range_um"] for x in gradients):.2f}'
    comparator = max(abs(arm["native_minus_analytical_um"]) for row in report["pairs"] for arm in row["arms"].values())
    intro = "C220 is higher under the tested shared boundary and common process shifts. Its advantage is not unconditional. Neither coupon has a qualified 185 µm clearance pass."
    scope = "These are calculations at artificial planning inputs. No new specimen was fabricated or measured. Sampled scenarios are not probability distributions or continuous uncertainty bounds. The actual coupon has twenty joints and copper at both ends. The older paper's one-cylinder correction is a separate experiment."
    conclusion = "At opposite requested pad and sphere endpoints, the predicted advantage is below the requested 3 µm paired measurement uncertainty. Opposite ±5% liquid-volume stress reverses the ranking. That wider volume stress exceeds the screened sphere band and is not a measured process tolerance. Unknown arm-specific wetting can also reverse the ranking."
    residual = verification["finite_pad"]["full_wetting_maximum_load_residual_uN"]
    physics = f"The finite-pad prototype explicitly represents solid exclusion around prescribed copper wetting depths. Liquid volume and metal-envelope volume remain separate. Gravity is disabled in that envelope. At the declared nominal fixed gaps, both full-wetting cases pass sampled curved-interface checks and fresh relaxed-energy reaction checks. Maximum load residual across both difference steps and the final two mesh levels is {residual:.6f} µN against a 0.01 µN numerical tolerance. This is numerical consistency, not physical force accuracy."
    limits = "The C270 moving-height calculation retains a native active-set failure. The deliberately penetrating obstacle control remains intrusive and not converged. Active new contact lacks the required wetting-area energy. The prototype is research only. It supplies no continuous solid-clearance certificate, unique-equilibrium proof, or general loaded finite-pad solver. The public solver is unchanged."
    coupled = f"A prescribed 317.5 to 322.5 µm sphere gradient produces {gradient_range} µm gap variation in the analytical rigid-cap model. This exceeds the protocol's raw 3 µm range comparison even though the sphere endpoints match the requested geometry band before measurement uncertainty. The construction is not a predicted manufacturing frequency. A symmetric volume pattern stays flat but needs tensile joint reactions and exceeds the model's declared applicability screen. All cases remain in the evidence."
    trust = f"Trust the request conversions, retained failure accounting, reproduced native scenario calculations and mechanically balanced analytical examples within their stated assumptions. All six original coupon planning requests reproduce, including actual-liquid gravity controls. Twelve accepted critical requests and one rejected control have fresh identity-checked replay. The analytical spring comparator differs from native gap predictions by at most {comparator:.3f} µm across this sampled campaign. That agreement is not a physical error bound."
    lab = "Measure both hot contact-line locations and finished pad heights first. Independently identify solder mass and liquid density, cap mass, the sphere-to-joint placement map, hot local gaps and cap tilt. Qualify the hot-to-cold transformation before treating liquid predictions as cooled clearance. Observe load-displacement behavior separately before qualifying forces. These measurements distinguish causes that fitting one height cannot separate."
    commands = """python3 prelab/verify.py
python3 -m unittest prelab.test_campaign prelab.test_replay prelab.test_rigid_cap prelab.test_finite -v
python3 prelab/campaign.py run output/prelab-campaign-new --workers 2
python3 prelab/replay.py output/prelab-campaign-new output/prelab-replay-new
python3 prelab/rigid_cap.py --verify
python3 -m prelab.run_finite output/prelab-finite-new
python3 -m prelab.make_report"""
    text = "# What the 220 versus 270 µm coupon can establish\n\n" + intro + "\n\n" + scope + "\n\n"
    text += "## Native decision checks\n\n" + "\n".join(markdown_table) + "\n\n" + conclusion + "\n\n"
    text += "## Physical model experiment\n\n" + physics + "\n\n" + limits + "\n\n"
    text += "## Twenty-joint coupling\n\n" + coupled + "\n\n"
    text += "## What is supported\n\n" + trust + "\n\n"
    text += "## Measurements still required\n\n" + lab + "\n\nSee [the lab addendum](LAB_ADDENDUM.md) and [the fixed protocol](protocol.json).\n\n"
    text += "## Reproduce\n\nUse Python 3.12 or newer, the pinned engine, and this Git checkout containing baseline `33666d3`. Offline verification does not run the engine. Finite-pad recomputation uses Git to verify unchanged production sources. New campaign and replay directories must not exist.\n\n```sh\n" + commands + "\n```\n\n"
    text += "The original `evidence/replay` and intermediate `evidence/replay-identity-checked` checks are superseded by `evidence/replay-final`. Independent review found missing per-receipt identity checks, including a missing native-engine field on accepted results. The final command requires those fields and the complete campaign was recomputed. Earlier records remain preserved. A matching hash is local integrity, not a digital signature or trusted timestamp.\n"
    (ROOT / "prelab/REPORT.md").write_text(text)
    html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SolderShape | Pre-lab findings</title><link rel="icon" href="data:,"><link rel="stylesheet" href="/board.css"><link rel="stylesheet" href="/ui.css"><script src="/ui.js" defer></script></head><body><span id="engine-state">Recorded pre-lab evidence</span><main class="prelab-report"><section class="intro"><div><p class="eyebrow">PRE-LAB VERIFICATION</p><h1>Which choice survives?</h1><p class="subtitle">' + escape(intro) + '</p><p>' + escape(scope) + '</p><p><a href="/lab">Back to physical tests</a> · <a href="/lab/prelab-protocol.json" download>Download the scenario protocol</a> · <a href="/lab/prelab-results.json" download>Download native results</a></p></div></section>'
    html += '<section class="panel lab-panel"><h2>Separate the ranking from clearance.</h2><div class="table-scroll"><table class="prelab-table"><thead><tr>' + ''.join('<th scope="col">'+escape(x)+'</th>' for x in ('Scenario','Assumed boundary','C220 gap, µm','C270 gap, µm','C220 minus C270, µm')) + '</tr></thead><tbody>'+''.join(html_rows)+'</tbody></table></div><p>'+escape(conclusion)+'</p><p>The 185 µm target is a finished-pad-face gap. These single-joint calculations do not establish a whole-cap minimum.</p></section>'
    for title, paragraphs in (("Finite copper changes the question.",(physics,limits)),("Twenty joints share one cap.",(coupled,)),("What the evidence supports.",(trust,)),("Measure the assumptions first.",(lab,))):
        html += '<section class="panel lab-panel"><h2>'+escape(title)+'</h2>'+''.join('<p>'+escape(p)+'</p>' for p in paragraphs)+'</section>'
    html += '<section class="panel lab-panel"><h2>Prepare the lab pilot.</h2><p><a href="/lab/prelab-measurements.txt" download="SolderShape-prelab-measurements.md">Download the measurement addendum</a>. Keep the existing quote-stage fabrication and confirmation gates.</p><details><summary>Reproduce and verify locally</summary><pre>'+escape(commands)+'</pre><p>Run at the source checkout root. The pinned native engine is needed for fresh calculations. The finite adapter requires the baseline Git history. No archived Python or Evolver script is executed by offline verification.</p></details></section></main></body></html>'
    (ROOT / "prelab/REPORT.html").write_text(html + "\n")
    return verification


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
