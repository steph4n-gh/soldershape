"""Boundary bookkeeping and physical-eligibility controls for the research adapter."""

import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from soldershape.model import InputError, LoadSpec
from prelab.finite import FinitePadRequest, _adapt_model, _commands, _interface_diagnostics, envelope_spec, fixed_energy_check, native_model


class FinitePadTests(unittest.TestCase):
    def request(self, depth=.035):
        return FinitePadRequest(LoadSpec(.22, .28, .01715728467880506, 0, 6.864655, gravity=False), .035, .035, depth, depth)

    def test_exact_liquid_volume_bookkeeping(self):
        request = self.request()
        copper = math.pi * ((.22/2)**2 + (.28/2)**2) * .035
        self.assertAlmostEqual(envelope_spec(request).volume_mm3-copper, .01715728467880506, places=16)
        self.assertEqual(envelope_spec(self.request(0)), self.request(0).liquid)

    def test_reject_unmodelled_gravity_and_invalid_depth(self):
        with self.assertRaises(InputError):
            FinitePadRequest(LoadSpec(.22, .28, .017, 0, 7), .035, .035, 0, 0)
        for depth in (-.001, .036, float("nan"), True):
            with self.subTest(depth=depth), self.assertRaises(InputError):
                self.request(depth)

    def test_model_assigns_inherited_obstacles_only_to_free_interface(self):
        model = native_model(self.request(), .25, 6.864655)
        self.assertIn("constraint 7 nonnegative", model)
        self.assertIn("formula: maximum(z-lower_depth", model)
        self.assertIn("tension S_TENSION constraints 5,6,7,8", model)
        self.assertIn("13 0 0 height constraint 2 fixed bare pad_energy", model)
        self.assertNotIn("tension 0 constraints 5", model)
        with self.assertRaises(RuntimeError):
            _adapt_model(self.request(), "not the native model")

    def test_curved_patch_penetration_is_detected(self):
        text = "\n".join(("QV 1 .011 0 0", "QV 2 .011 0 .0035", "QV 3 .012 .001 .0035", "QV 4 .010 0 .00175", "QV 5 .0115 .0005 .0035", "QV 6 .0115 .0005 .00175", "QE 1 1 2 4", "QE 2 2 3 5", "QE 3 3 1 6", "QF 1 1 2 3"))
        result = _interface_diagnostics(text, self.request(), .25)
        self.assertTrue(result["intrusion_detected"])
        self.assertEqual(result["free_facets"], 1)
        self.assertEqual(result["samples"], 15)
        self.assertFalse(result["continuous_clearance_certified"])

    def test_prescribed_rim_samples_are_not_new_wall_contact(self):
        text = "\n".join(("QV 1 .011 0 0", "QV 2 0 .011 0", "QV 3 .012 0 .01", "QV 4 .007778174593 .007778174593 0", "QV 5 .006 .0055 .005", "QV 6 .0115 0 .005", "QE 1 1 2 4", "QE 2 2 3 5", "QE 3 3 1 6", "QF 1 1 2 3"))
        result = _interface_diagnostics(text, self.request(0), .25)
        self.assertEqual(result["new_contact_samples"]["lower_copper"], 0)

    def test_sampling_precedes_flattening_without_extra_mesh_refinement(self):
        from soldershape.solver import _commands as original
        bare = original(2, False)
        finite = _commands(original, 2, False)
        self.assertEqual(finite.splitlines().count("r"), bare.splitlines().count("r"))
        self.assertLess(finite.index('} >>> "interface.txt"'), finite.index("\nlinear\n"))
        self.assertIn("foreach facet ff where ff.density > 0", finite)
        self.assertEqual(finite.count("eigenprobe 0"), bare.count("eigenprobe 0"))

    def test_relaxed_energy_units_and_sign_against_linear_energy(self):
        request = self.request()
        def exact_linear_energy(request, directory, kind, height, levels):
            energy = 1-request.liquid.normal_load_uN*height/100
            return {"physical_eligibility": True, "energy_erg": energy, "status": "refinement_checked", "request_sha256": request.sha256,
                    "levels": [{"level": index, "facets": 100*4**index, "energy_erg": energy+.001/4**index} for index in range(levels)]}
        with tempfile.TemporaryDirectory() as temporary, patch("prelab.finite._isolated", exact_linear_energy):
            result = fixed_energy_check(request, Path(temporary)/"check", .1782, level_count=3)
        self.assertEqual(result["status"], "reaction_checked")
        for row in result["checks"]:
            self.assertAlmostEqual(row["reaction_uN"], 6.864655, places=8)
            self.assertEqual(len(row["reactions_by_refinement"]), 3)


if __name__ == "__main__":
    unittest.main()
