"""Replay the destructive Newton-step defect and the repaired force checks."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from soldershape.model import JointSpec
from soldershape import solver


def baseline_commands(level_count):
    lines = ["M 2", "u", "g 3", "r", "g 5", "r", "g 5", "hessian", "hessian"]
    for level in range(level_count):
        if level:
            lines.extend(["r", "g 10", "hessian", "hessian", "hessian"])
        lines.extend([
            "energy_before := total_energy", "g 5", "hessian", "hessian",
            "stationarity_delta := abs(total_energy-energy_before)",
            "do_xforce", "do_zforce", "eigenprobe 0",
            f'printf "SS_LEVEL {level} %d %.17g %.17g %.17g %.17g %.17g %d %.17g\\n",facet_count,xforce,zforce,total_energy,body[1].volume,(body[1].volume-body[1].target)/body[1].target,eigen_neg,stationarity_delta',
        ])
    lines.extend([
        "r", "linear", "recalc",
        '{ foreach vertex vv do printf "VERTEX %d %.17g %.17g %.17g\\n",vv.id,vv.x,vv.y,vv.z; foreach facet ff do printf "TRIANGLE %d %d %d %d\\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id; } >>> "mesh.txt"',
        'printf "SS_DONE %d %.17g\\n",facet_count,body[1].volume', "quit 0",
    ])
    return "\n".join(lines) + "\n"


def compact(result):
    return {key: result[key] for key in ("input", "status", "forces", "diagnostics", "levels", "mesh_checks") if key in result}


def main():
    high = JointSpec(.64, .64, .0351, .01181699087727595, .031, 1, 9, False)
    middle = replace(high, standoff_mm=.0347, offset_mm=.0102)
    current_commands = solver._commands
    report = {"solver_sha256": hashlib.sha256((ROOT / "soldershape/solver.py").read_bytes()).hexdigest(), "engine": solver.engine_info(), "baseline": {}, "repaired": {}, "energy_derivatives": []}
    try:
        solver._commands = baseline_commands
        for name, spec in (("thin_high", high), ("thin_middle", middle)):
            try:
                report["baseline"][name] = compact(solver.solve(spec))
            except solver.SolverError as error:
                report["baseline"][name] = {"input": spec.to_dict(), "status": "engine_error", "error": str(error), "evidence": error.evidence}
    finally:
        solver._commands = current_commands
    assert report["baseline"]["thin_high"]["status"] == "engine_error"
    assert report["baseline"]["thin_middle"]["status"] == "not_converged"
    for name, spec in (("thin_high", high), ("thin_middle", middle)):
        result = solver.solve(spec)
        assert result["status"] == "refinement_checked"
        report["repaired"][name] = compact(result)
    for field, step_mm, component in (("offset_mm", .00005, "x_uN"), ("standoff_mm", .000005, "z_uN")):
        minus, plus = [solver.solve(replace(high, **{field: getattr(high, field) + sign*step_mm})) for sign in (-1, 1)]
        assert minus["status"] == plus["status"] == "refinement_checked"
        energy_delta = plus["levels"][-1]["energy_erg"] - minus["levels"][-1]["energy_erg"]
        force = -energy_delta/(2*step_mm/10)*10
        virtual = report["repaired"]["thin_high"]["forces"][component]
        relative = abs(force/virtual - 1)
        assert relative < .001
        report["energy_derivatives"].append({"field": field, "step_mm": step_mm, "force_uN": force, "virtual_force_uN": virtual, "relative_difference": relative, "minus": compact(minus), "plus": compact(plus)})
    report["passed"] = True
    output = ROOT / "output" / "solver-repair-replay.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"passed": True, "report": str(output), "solver_sha256": report["solver_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
