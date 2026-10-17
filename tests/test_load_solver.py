from dataclasses import replace
import math
import re
import unittest
from unittest.mock import patch

from soldershape.model import InputError, JointSpec, LoadSpec, joint_spec_from_dict, spherical_gap_mm
import soldershape.solver as native_solver
from soldershape.solver import engine_info, solve


def reference_request():
    return LoadSpec(.27, .28, .01745+math.pi*(.27/2)**2*.034, 0, 4, .48, 9, False)


class LoadInputs(unittest.TestCase):
    def test_distinct_physical_requests_and_case_dispatch(self):
        request = reference_request()
        self.assertEqual(joint_spec_from_dict(request.to_dict()), request)
        self.assertNotIn("standoff_mm", request.to_dict())
        fixed = request.at_gap(.224)
        self.assertEqual(joint_spec_from_dict(fixed.to_dict()), fixed)
        self.assertNotEqual(request.sha256, fixed.sha256)
        self.assertIsInstance(fixed, JointSpec)
        for value in (True, float("nan"), float("inf"), -1, 100001):
            with self.subTest(load=value), self.assertRaises(InputError):
                replace(request, normal_load_uN=value)
        with self.assertRaises(InputError):
            joint_spec_from_dict({**request.to_dict(), "standoff_mm": .224})
        with self.assertRaises(InputError):
            replace(request, lower_diameter_mm=-.27)

    def test_geometry_only_seed_reconstructs_spherical_volume(self):
        request = reference_request()
        height = spherical_gap_mm(request.lower_diameter_mm, request.upper_diameter_mm, request.volume_mm3)
        a, b = request.lower_diameter_mm/2, request.upper_diameter_mm/2
        volume = math.pi*height*(a*a+b*b)/2 + math.pi*height**3/6
        self.assertAlmostEqual(volume, request.volume_mm3, places=14)
        for value in (0, -1, float("nan"), True):
            with self.subTest(diameter=value), self.assertRaises(InputError):
                spherical_gap_mm(value, .28, .02)


@unittest.skipUnless(engine_info()["ready"], "Build the pinned native engine first.")
class NativeLoadEquilibrium(unittest.TestCase):
    def assert_balanced(self, request, result):
        self.assertEqual(result["status"], "refinement_checked", result.get("error"))
        self.assertEqual(result["input"], request.to_dict())
        self.assertEqual(result["input_sha256"], request.sha256)
        balance = result["load_balance"]
        self.assertEqual(balance["status"], "balanced")
        self.assertLessEqual(abs(result["forces"]["z_uN"]-request.normal_load_uN), balance["tolerance_uN"])
        self.assertLessEqual(balance["height_change_mm"], balance["height_change_tolerance_mm"])
        self.assertEqual(result["evidence"]["fixed_gap_verification"]["input"], result["equilibrium"])
        self.assertEqual(result["evidence"]["fixed_gap_verification"]["status"], "refinement_checked")
        self.assertEqual(result["model_warnings"], [])
        self.assertTrue(result["mesh_checks"]["closed"])
        self.assertEqual(result["mesh_checks"]["euler_characteristic"], 2)
        self.assertEqual(result["diagnostics"]["negative_eigenvalues"], 0)

    def test_loaded_height_and_offset_have_independent_force_balance(self):
        request = reference_request()
        result = solve(request)
        self.assert_balanced(request, result)
        self.assertAlmostEqual(result["equilibrium"]["standoff_mm"], .2246805, delta=.00001)
        offset = replace(request, lower_diameter_mm=.17,
                         volume_mm3=.01745+math.pi*(.17/2)**2*.034, offset_mm=.06)
        shifted = solve(offset)
        self.assert_balanced(offset, shifted)
        self.assertAlmostEqual(shifted["equilibrium"]["standoff_mm"], .242177, delta=.00002)

    def test_zero_load_agrees_with_unloaded_sphere(self):
        request = replace(reference_request(), normal_load_uN=0)
        result = solve(request)
        self.assert_balanced(request, result)
        expected = spherical_gap_mm(request.lower_diameter_mm, request.upper_diameter_mm, request.volume_mm3)
        self.assertAlmostEqual(result["equilibrium"]["standoff_mm"], expected, delta=.000002)

    def test_geometric_scaling_preserves_dimensionless_equilibrium(self):
        request = reference_request()
        heights = []
        for scale in (.5, 2):
            scaled = replace(request, lower_diameter_mm=request.lower_diameter_mm*scale,
                             upper_diameter_mm=request.upper_diameter_mm*scale,
                             volume_mm3=request.volume_mm3*scale**3,
                             normal_load_uN=request.normal_load_uN*scale)
            result = solve(scaled)
            self.assert_balanced(scaled, result)
            heights.append(result["equilibrium"]["standoff_mm"]/scale)
        self.assertAlmostEqual(heights[0], heights[1], delta=.000003)

    def test_unattainable_load_keeps_request_without_a_successful_shape(self):
        request = replace(reference_request(), normal_load_uN=100000)
        result = solve(request)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["input"], request.to_dict())
        self.assertEqual(result["input_sha256"], request.sha256)
        self.assertEqual(result["load_balance"]["status"], "not_balanced")
        self.assertNotIn("equilibrium", result)
        self.assertNotIn("mesh", result)
        self.assertNotIn("forces", result)
        self.assertTrue(result["evidence"])

    def test_native_delta_sensitivity_and_separated_geometry_starts(self):
        request = reference_request()
        original_model = native_solver._model
        for scale in (.5, 2):
            scaled = replace(request, lower_diameter_mm=request.lower_diameter_mm*scale,
                             upper_diameter_mm=request.upper_diameter_mm*scale,
                             volume_mm3=request.volume_mm3*scale**3,
                             normal_load_uN=request.normal_load_uN*scale)
            heights = []
            for factor in (.5, 2):
                def model_with_delta(joint, normal_load_uN=None):
                    model = original_model(joint, normal_load_uN)
                    if normal_load_uN is not None:
                        model = re.sub(r"pdelta = ([-+\d.eE]+)", lambda match: "pdelta = " + format(float(match[1])*factor, ".17g"), model, count=1)
                    return model
                with self.subTest(scale=scale, delta_factor=factor), patch.object(native_solver, "_model", model_with_delta):
                    result = solve(scaled)
                    self.assert_balanced(scaled, result)
                    heights.append(result["equilibrium"]["standoff_mm"]/scale)
            self.assertAlmostEqual(heights[0], heights[1], delta=.000003)

        offset = replace(request, lower_diameter_mm=.17,
                         volume_mm3=.01745+math.pi*(.17/2)**2*.034, offset_mm=.06)
        seed = spherical_gap_mm(offset.lower_diameter_mm, offset.upper_diameter_mm, offset.volume_mm3)
        heights = []
        for factor in (.9, 1.1):
            with self.subTest(seed_factor=factor), patch.object(native_solver, "spherical_gap_mm", return_value=seed*factor):
                result = solve(offset)
                self.assert_balanced(offset, result)
                heights.append(result["equilibrium"]["standoff_mm"])
        self.assertAlmostEqual(heights[0], heights[1], delta=.000003)


if __name__ == "__main__":
    unittest.main()
