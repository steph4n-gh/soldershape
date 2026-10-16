from dataclasses import replace
import unittest

from soldershape.model import JointSpec
from soldershape.solver import engine_info, solve


@unittest.skipUnless(engine_info()["ready"], "Build the pinned native engine first.")
class ThinBridgeRelaxation(unittest.TestCase):
    def test_thin_bridges_and_re_equilibrated_energy_derivatives(self):
        high = JointSpec(.64, .64, .0351, .01181699087727595, .031, 1, 9, False)
        middle = replace(high, standoff_mm=.0347, offset_mm=.0102)
        results = [solve(spec) for spec in (high, middle)]
        for result in results:
            with self.subTest(input=result["input"]):
                self.assertEqual(result["status"], "refinement_checked")
                self.assertEqual(result["diagnostics"]["negative_eigenvalues"], 0)
                self.assertLessEqual(result["diagnostics"]["stationarity_energy_change_relative"], 1e-7)
                self.assertLessEqual(result["diagnostics"]["volume_relative_error"], .001)
                self.assertLessEqual(result["diagnostics"]["force_change_relative"], .01)

        for field, step_mm, component in (("offset_mm", .00005, "x_uN"), ("standoff_mm", .000005, "z_uN")):
            with self.subTest(component=component):
                minus, plus = [solve(replace(high, **{field: getattr(high, field) + sign*step_mm})) for sign in (-1, 1)]
                self.assertEqual(minus["status"], "refinement_checked")
                self.assertEqual(plus["status"], "refinement_checked")
                energy_delta_erg = plus["levels"][-1]["energy_erg"] - minus["levels"][-1]["energy_erg"]
                force_uN = -energy_delta_erg / (2*step_mm/10) * 10
                self.assertLess(abs(force_uN/results[0]["forces"][component] - 1), .001)


if __name__ == "__main__":
    unittest.main()
