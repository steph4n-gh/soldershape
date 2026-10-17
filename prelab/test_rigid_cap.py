import math
import unittest

from prelab.rigid_cap import SpringJoint, build_report, solve_rigid_cap


class RigidCapTests(unittest.TestCase):
    def rectangle(self, height=200.0, stiffness=2.0):
        return [SpringJoint(str(i), x, y, height, stiffness, height)
                for i, (x, y) in enumerate(((-1, -.5), (1, -.5), (-1, .5), (1, .5)))]

    def assert_balanced(self, result):
        for name in ("force_residual_uN", "torque_x_residual_uN_mm", "torque_y_residual_uN_mm"):
            self.assertAlmostEqual(result[name], 0.0, places=9)

    def test_uniform_load_has_literal_equal_force_and_height(self):
        result = solve_rigid_cap(self.rectangle(), 8.0)
        self.assertEqual(result["joint_gap_min_um"], 199.0)
        self.assertEqual(result["joint_gap_max_um"], 199.0)
        self.assertEqual(result["tilt_angle_deg"], 0.0)
        self.assertEqual([row["reaction_uN"] for row in result["local_joints"]], [2.0]*4)
        self.assert_balanced(result)

    def test_unloaded_height_plane_is_inherited_as_cap_tilt(self):
        joints = [SpringJoint(joint.joint_id, joint.x_mm, joint.y_mm,
                              200.0+3.0*joint.x_mm-2.0*joint.y_mm, 2.0, 200.0)
                  for joint in self.rectangle()]
        result = solve_rigid_cap(joints, 8.0)
        self.assertEqual(result["plane_height_at_joint_centroid_um"], 199.0)
        self.assertEqual(result["slope_x_um_per_mm"], 3.0)
        self.assertEqual(result["slope_y_um_per_mm"], -2.0)
        self.assertEqual([row["reaction_uN"] for row in result["local_joints"]], [2.0]*4)
        self.assertAlmostEqual(result["tilt_angle_deg"], math.degrees(math.atan(math.sqrt(13)/1000)))
        self.assert_balanced(result)

    def test_axis_permutation_preserves_gaps_and_reactions(self):
        joints = [SpringJoint(str(i), x, y, 200+3*x-2*y+i, 2+i, 200)
                  for i, (x, y) in enumerate(((-1, -.5), (1, -.5), (-1, .5), (1, .5)))]
        original = solve_rigid_cap(joints, 12.0, (.15, -.1))
        permuted = solve_rigid_cap([SpringJoint(j.joint_id, j.y_mm, j.x_mm, j.unloaded_gap_um,
                                                j.stiffness_n_m, j.unloaded_domain_height_um) for j in joints],
                                   12.0, (-.1, .15))
        for left, right in zip(original["local_joints"], permuted["local_joints"]):
            self.assertAlmostEqual(left["gap_um"], right["gap_um"], places=10)
            self.assertAlmostEqual(left["reaction_uN"], right["reaction_uN"], places=9)
        self.assertAlmostEqual(original["slope_x_um_per_mm"], permuted["slope_y_um_per_mm"], places=10)
        self.assert_balanced(original)
        self.assert_balanced(permuted)

    def test_singular_positions_are_rejected(self):
        joints = [SpringJoint(str(i), i, 2*i, 200, 2, 200) for i in range(4)]
        with self.assertRaisesRegex(ValueError, "span a plane"):
            solve_rigid_cap(joints, 8.0)

    def test_tensile_reactions_are_retained(self):
        joints = [SpringJoint(str(i), x, y, height, 2, 200)
                  for i, (x, y, height) in enumerate(((-1, -1, 204), (1, -1, 196),
                                                     (-1, 1, 196), (1, 1, 204)))]
        result = solve_rigid_cap(joints, 8.0)
        self.assertEqual([row["reaction_uN"] for row in result["local_joints"]], [10, -6, -6, 10])
        self.assertEqual(result["tensile_joint_count"], 2)
        self.assertFalse(result["within_declared_one_percent_deformation_screen"])
        self.assert_balanced(result)

    def test_invalid_stiffness_is_rejected(self):
        joints = self.rectangle(stiffness=0)
        with self.assertRaisesRegex(ValueError, "positive"):
            solve_rigid_cap(joints, 8.0)

    def test_coupon_uniform_matches_literal_eq9_values(self):
        report = build_report()
        expected = {"literal_rims": {"C220": 223.349072009816, "C270": 207.51966907047608},
                    "two_pad_cylinders": {"C220": 178.24975366079875, "C270": 167.31802279103348}}
        self.assertEqual(report["analytical_cap_cases"], 12)
        self.assertEqual(report["native_solves"], 0)
        for case in report["cases"]:
            if case["scenario"] == "uniform":
                for arm, result in case["arms"].items():
                    self.assertAlmostEqual(result["joint_gap_min_um"], expected[case["mapping"]][arm], places=7)
                    self.assertAlmostEqual(result["independent_equal_load_min_um"], result["joint_gap_min_um"], places=10)
                    for joint in result["local_joints"]:
                        self.assertAlmostEqual(joint["reaction_uN"], 6.864655, places=9)
                    self.assert_balanced(result)

    def test_prescribed_gradient_exposes_three_micrometer_gate(self):
        for case in build_report()["cases"]:
            if case["scenario"] == "left_to_right_gradient":
                for result in case["arms"].values():
                    self.assertGreater(result["joint_gap_range_um"], 5.3)
                    self.assertLess(result["joint_gap_range_um"], 6.3)
                    self.assertTrue(result["predicted_gap_range_exceeds_3_um"])
                    self.assertTrue(result["within_declared_one_percent_deformation_screen"])
                    self.assertEqual(result["tensile_joint_count"], 0)
                    self.assert_balanced(result)

    def test_symmetric_volume_pattern_is_flat_with_retained_tension(self):
        for case in build_report()["cases"]:
            if case["scenario"] == "symmetric_outer_rows_high":
                for result in case["arms"].values():
                    self.assertAlmostEqual(result["joint_gap_range_um"], 0.0, places=10)
                    self.assertEqual(result["tensile_joint_count"], 10)
                    self.assertFalse(result["within_declared_one_percent_deformation_screen"])
                    diameters = [row["sphere_diameter_um"] for row in result["sphere_map"]]
                    self.assertEqual(diameters.count(317.5), 10)
                    self.assertEqual(diameters.count(322.5), 10)
                    self.assert_balanced(result)


if __name__ == "__main__":
    unittest.main()
