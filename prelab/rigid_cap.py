"""Check force and moment coupling in the twenty-joint coupon analytically."""

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coupons.tools.analyze import analytical, loaded_code_hashes
from soldershape.model import LoadSpec

SOURCES = ("prelab/rigid_cap.py", "prelab/test_rigid_cap.py", "prelab/protocol.json",
           "prelab/design/uncertainty.md", "prelab/design/rigid-cap-notes.md",
           "coupons/experiment.json", "coupons/tools/analyze.py",
           "soldershape/model.py", "soldershape/solver.py")
OUTPUT = ROOT / "prelab/evidence/rigid-cap.json"
LOADED_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True)
class SpringJoint:
    joint_id: str
    x_mm: float
    y_mm: float
    unloaded_gap_um: float
    stiffness_n_m: float
    unloaded_domain_height_um: float


def solve_three(matrix, rhs):
    augmented = [list(row) + [value] for row, value in zip(matrix, rhs)]
    scale = max(abs(value) for row in matrix for value in row)
    for column in range(3):
        pivot = max(range(column, 3), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= scale * 1e-12:
            raise ValueError("Joint positions must span a plane, not a line or a point.")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(3):
            if row != column:
                multiplier = augmented[row][column]
                augmented[row] = [a - multiplier * b for a, b in zip(augmented[row], augmented[column])]
    return [row[3] for row in augmented]


def solve_rigid_cap(joints, load_uN, com_mm=(0.0, 0.0)):
    joints = tuple(joints)
    if len(joints) < 3 or len({joint.joint_id for joint in joints}) != len(joints):
        raise ValueError("At least three uniquely named joints are required.")
    values = (load_uN, *com_mm, *(value for joint in joints for value in
              (joint.x_mm, joint.y_mm, joint.unloaded_gap_um, joint.stiffness_n_m,
               joint.unloaded_domain_height_um)))
    if any(not math.isfinite(value) for value in values) or load_uN < 0:
        raise ValueError("The load, center of mass, and joint values must be finite, with nonnegative load.")
    if any(min(joint.unloaded_gap_um, joint.stiffness_n_m,
               joint.unloaded_domain_height_um) <= 0 for joint in joints):
        raise ValueError("Unloaded gaps, domain heights, and stiffnesses must be positive.")
    center_x = math.fsum(joint.x_mm for joint in joints) / len(joints)
    center_y = math.fsum(joint.y_mm for joint in joints) / len(joints)
    scale = max(max(abs(joint.x_mm - center_x), abs(joint.y_mm - center_y)) for joint in joints)
    if scale == 0:
        raise ValueError("Joint positions must span a plane, not a line or a point.")
    vectors = [(1.0, (joint.x_mm-center_x)/scale, (joint.y_mm-center_y)/scale) for joint in joints]
    com_vector = (1.0, (com_mm[0]-center_x)/scale, (com_mm[1]-center_y)/scale)
    matrix = [[math.fsum(joint.stiffness_n_m * vector[i] * vector[j]
                        for joint, vector in zip(joints, vectors)) for j in range(3)] for i in range(3)]
    rhs = [math.fsum(joint.stiffness_n_m * joint.unloaded_gap_um * vector[i]
                    for joint, vector in zip(joints, vectors)) - load_uN * com_vector[i] for i in range(3)]
    height, slope_x_scaled, slope_y_scaled = solve_three(matrix, rhs)
    slope_x, slope_y = slope_x_scaled / scale, slope_y_scaled / scale
    local = []
    for joint, vector in zip(joints, vectors):
        gap = height + slope_x_scaled * vector[1] + slope_y_scaled * vector[2]
        deformation = joint.unloaded_gap_um - gap
        reaction = joint.stiffness_n_m * deformation
        local.append({"joint_id": joint.joint_id, "x_mm": joint.x_mm, "y_mm": joint.y_mm,
                      "unloaded_gap_um": joint.unloaded_gap_um,
                      "unloaded_domain_height_um": joint.unloaded_domain_height_um,
                      "stiffness_N_m": joint.stiffness_n_m, "gap_um": gap,
                      "compression_um": deformation, "reaction_uN": reaction,
                      "tensile": reaction < -1e-9,
                      "absolute_deformation_fraction": abs(deformation)/joint.unloaded_domain_height_um,
                      "independent_equal_load_gap_um": joint.unloaded_gap_um - load_uN/len(joints)/joint.stiffness_n_m})
    gaps = [row["gap_um"] for row in local]
    independent = [row["independent_equal_load_gap_um"] for row in local]
    force_residual = math.fsum(row["reaction_uN"] for row in local) - load_uN
    torque_x = math.fsum(row["y_mm"] * row["reaction_uN"] for row in local) - com_mm[1] * load_uN
    torque_y = -math.fsum(row["x_mm"] * row["reaction_uN"] for row in local) + com_mm[0] * load_uN
    maximum_fraction = max(row["absolute_deformation_fraction"] for row in local)
    return {"plane_height_at_joint_centroid_um": height,
            "joint_centroid_mm": [center_x, center_y], "slope_x_um_per_mm": slope_x,
            "slope_y_um_per_mm": slope_y,
            "tilt_angle_deg": math.degrees(math.atan(math.hypot(slope_x, slope_y)/1000)),
            "joint_gap_min_um": min(gaps), "joint_gap_max_um": max(gaps),
            "joint_gap_range_um": max(gaps)-min(gaps),
            "independent_equal_load_min_um": min(independent),
            "independent_equal_load_max_um": max(independent),
            "independent_equal_load_range_um": max(independent)-min(independent),
            "force_residual_uN": force_residual, "torque_x_residual_uN_mm": torque_x,
            "torque_y_residual_uN_mm": torque_y,
            "tensile_joint_count": sum(row["tensile"] for row in local),
            "maximum_absolute_deformation_fraction": maximum_fraction,
            "within_declared_one_percent_deformation_screen": maximum_fraction <= 0.01,
            "local_joints": local}


def build_report():
    loaded_code_hashes()
    source = {name: (ROOT / name).read_bytes() for name in SOURCES}
    if hashlib.sha256(source["prelab/rigid_cap.py"]).hexdigest() != LOADED_SOURCE_SHA256:
        raise ValueError("Rigid-cap source differs from loaded code. Restart Python before recording results.")
    experiment = json.loads(source["coupons/experiment.json"])
    protocol = json.loads(source["prelab/protocol.json"])
    if experiment["experiment_id"] != "SS-C220-C270-R1" or protocol["domain"] != "actual_SS-C220-C270-R1_coupon":
        raise ValueError("This check requires the actual coupon domain.")
    array = experiment["array"]
    if (array["columns"], array["rows"], array["joint_count"], array["pitch_mm"]) != (5, 4, 20, 0.5):
        raise ValueError("This bounded check requires the declared five by four coupon array.")
    nominal = next(row["common"] for row in protocol["scenarios"] if row["id"] == "nominal")
    parameters = protocol["parameters"]
    total_load = nominal["cap_mass_mg"] * parameters["g_m_s2"]
    rows = []
    for scenario in ("uniform", "left_to_right_gradient", "symmetric_outer_rows_high"):
        for mapping, boundary in protocol["boundaries"].items():
            arms = {}
            for arm, lower in parameters["lower_nominal_mm"].items():
                upper = parameters["upper_nominal_mm"]
                lower_depth = boundary["depth_fraction"] * nominal["lower_metal_um"] / 1000
                upper_depth = boundary["depth_fraction"] * nominal["upper_metal_um"] / 1000
                correction_um = 1000 * (lower_depth + upper_depth)
                metal_volume = math.pi / 4 * (lower**2 * lower_depth + upper**2 * upper_depth)
                joints, sphere_map = [], []
                for row in range(array["rows"]):
                    for column in range(array["columns"]):
                        diameter = (nominal["sphere_diameter_um"] if scenario == "uniform" else
                                    317.5 + 5.0 * column / (array["columns"]-1)
                                    if scenario == "left_to_right_gradient" else
                                    322.5 if row in (0, array["rows"]-1) else 317.5)
                        volume = math.pi / 6 * (diameter/1000)**3
                        spec = LoadSpec(lower_diameter_mm=lower, upper_diameter_mm=upper,
                                        volume_mm3=volume + metal_volume, offset_mm=0, normal_load_uN=0,
                                        surface_tension_n_m=parameters["gamma_n_m"],
                                        density_g_cm3=parameters["density_g_cm3"], gravity=False)
                        baseline = analytical(spec, correction_um)
                        x = (column-(array["columns"]-1)/2) * array["pitch_mm"]
                        y = (row-(array["rows"]-1)/2) * array["pitch_mm"]
                        joint_id = f"R{row+1}C{column+1}"
                        joints.append(SpringJoint(joint_id, x, y, baseline["gap_um"],
                                                  baseline["stiffness_N_m"], baseline["gap_um"]+correction_um))
                        sphere_map.append({"joint_id": joint_id, "sphere_diameter_um": diameter,
                                           "geometric_liquid_volume_mm3": volume})
                result = solve_rigid_cap(joints, total_load)
                result.update(lower_diameter_mm=lower, upper_diameter_mm=upper,
                              lower_depth_mm=lower_depth, upper_depth_mm=upper_depth,
                              pad_face_correction_um=correction_um, sphere_map=sphere_map,
                              predicted_gap_range_exceeds_3_um=result["joint_gap_range_um"] > experiment["model"]["max_gap_range_um"])
                arms[arm] = result
            rows.append({"scenario": scenario, "mapping": mapping, "arms": arms,
                         "C220_minus_C270_joint_minimum_um": arms["C220"]["joint_gap_min_um"] - arms["C270"]["joint_gap_min_um"]})
    if any((ROOT / name).read_bytes() != content for name, content in source.items()):
        raise ValueError("Source changed during the analytical check.")
    return {"schema": "soldershape.prelab.rigid-cap.v1", "domain": protocol["domain"],
            "source_sha256": {name: hashlib.sha256(content).hexdigest() for name, content in source.items()},
            "native_solves": 0, "analytical_cap_cases": len(rows)*2,
            "analytical_joint_evaluations": len(rows)*2*array["joint_count"],
            "stiffness_source": "https://imapsjmep.org/article/39820.pdf, Eq. 9, as implemented in coupons/tools/analyze.py",
            "array": array, "cap_mass_mg": nominal["cap_mass_mg"],
            "external_load_uN": total_load, "center_of_mass_mm": [0.0, 0.0],
            "gamma_N_m": parameters["gamma_n_m"],
            "scope": "Deterministic first-order analytical spring check, not native validation, a probability distribution, an interval bound or physical acceptance.",
            "assumptions": [
                "The actual five by four, 0.5 mm pitch pad centers lie in a perfectly flat lower plane.",
                "The cap is perfectly rigid. Its center of mass is at the array center. Only its mass supplies external force.",
                "Each joint exerts a vertical point force with Eq. 9 unloaded spherical height and stiffness.",
                "F_i = k_i * (h0_i - H - slope_x*x_i - slope_y*y_i), with force in micronewtons and height in micrometers.",
                "No cap bending, contact-line motion, local tilt-induced shape change, lateral force, intrinsic joint moment or solder gravity is represented.",
                "Geometric sphere volume is equated to liquid volume for this stress construction only. No measured molten-density conversion is claimed.",
                "Literal rims add no cylinder volume or height correction. Two cylinders add both metal volumes and subtract both 35 micrometer heights.",
                "The 317.5 to 322.5 micrometer endpoints are requested geometric limits without measurement uncertainty, not manufactured acceptance.",
                "The gradient and symmetric pattern are prescribed placements, not observations or stochastic process models.",
                "The one-percent absolute deformation limit is an unqualified engineering screen for this reduced model, not an error bound.",
                "Tensile reactions remain in force balance. Their physical wetting stability is unqualified. No unilateral contact clipping is used.",
                "The three micrometer comparison is a raw analytical warning. The lab eligibility gate additionally requires uncertainty and actual measured geometry.",
                "Minima cover the twenty idealized joint sites only. They establish neither actual whole-cap minimum nor cold clearance."
            ], "cases": rows, "physical_qualification": "unqualified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Recompute and compare the recorded analytical check.")
    args = parser.parse_args()
    report = build_report()
    if args.verify:
        if json.loads(OUTPUT.read_bytes()) != report:
            raise ValueError("Recorded rigid-cap result differs from the recomputed source and mechanics.")
        print("Rigid-cap result matches source hashes and recomputed mechanics.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n")
        print(OUTPUT)


if __name__ == "__main__":
    main()
