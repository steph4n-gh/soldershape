import base64
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

from soldershape.__main__ import Server, calculate_comparison, main, normalize_case
from soldershape.model import InputError, parse_case


ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "examples/volume-comparison.soldershape.json").read_text())


class EditableCases(unittest.TestCase):
    def test_saved_inputs_round_trip_without_result_claims(self):
        case = parse_case(CASE)
        self.assertEqual(parse_case(json.loads(json.dumps(case))), case)
        self.assertEqual(case["baseline"], {"upper_diameter_mm": .2, "volume_mm3": .005})
        self.assertNotIn("lower_diameter_mm", case["parameters"])
        self.assertNotIn("forces", case)

    def test_case_cannot_override_shared_conditions_or_execute_code(self):
        for changes in ({"schema": "future"}, {"command": "execute"}, {"baseline": {"upper_diameter_mm": .2, "volume_mm3": .005, "offset_mm": .01}},
                        {"baseline": {"upper_diameter_mm": .2, "volume_mm3": float("nan")}}, {"pad_index": True},
                        {"parameters": {**CASE["parameters"], "lower_diameter_mm": 9}}):
            with self.subTest(changes=changes), self.assertRaises(InputError):
                parse_case({**CASE, **changes})

    def test_comparison_is_fresh_and_preserves_fixed_conditions(self):
        def computed(spec):
            return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked",
                    "forces": {"x_uN": -10 if spec.volume_mm3 == .005 else -8, "z_uN": -20 if spec.volume_mm3 == .005 else 3},
                    "engine": {}}
        with patch("soldershape.solver.solve", side_effect=computed) as solver:
            rows, comparison = calculate_comparison(parse_case(CASE))
        self.assertEqual(solver.call_count, 2)
        self.assertEqual([row["design"] for row in rows], ["Reference", "Candidate"])
        for key in ("lower_diameter_mm", "offset_mm", "standoff_mm", "surface_tension_n_m", "density_g_cm3", "gravity"):
            self.assertEqual(rows[0]["input"][key], rows[1]["input"][key])
        self.assertEqual(comparison["status"], "compared")
        self.assertEqual(comparison["delta"]["restoring_force_uN"], -2)
        self.assertEqual(comparison["delta"]["vertical_force_uN"], 23)
        self.assertAlmostEqual(comparison["delta"]["volume_percent"], 20)

    def test_failed_or_zero_offset_comparison_has_no_improvement_verdict(self):
        from soldershape.solver import SolverError
        with patch("soldershape.solver.solve", side_effect=SolverError("unstable equilibrium")):
            rows, comparison = calculate_comparison(parse_case(CASE))
        self.assertEqual([row["status"] for row in rows], ["failed", "failed"])
        self.assertEqual(comparison["status"], "inconclusive")
        self.assertNotIn("delta", comparison)
        zero = parse_case({**CASE, "parameters": {**CASE["parameters"], "offset_mm": 0}})
        def computed(spec):
            return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked", "forces": {"x_uN": 0, "z_uN": 2}}
        with patch("soldershape.solver.solve", side_effect=computed):
            _, comparison = calculate_comparison(zero)
        self.assertNotIn("delta", comparison)
        self.assertIsNone(comparison["designs"][0]["restoring_force_uN"])
        self.assertEqual(comparison["designs"][0]["force_z_uN"], 2)

    def test_surface_beyond_pad_planes_keeps_forces_but_blocks_design_verdict(self):
        def computed(spec):
            return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked",
                    "forces": {"x_uN": -10, "z_uN": -20},
                    "mesh": {"vertices_mm": [[0, 0, -.001], [0, 0, .151]]},
                    "model_warnings": ["Substrate clearance is unknown."],
                    "diagnostics": {"pad_plane_excursion_mm": {"below_lower": .001}}}
        with patch("soldershape.solver.solve", side_effect=computed):
            rows, comparison = calculate_comparison(parse_case(CASE))
        self.assertEqual(rows[0]["status"], "refinement_checked")
        self.assertEqual(rows[0]["forces"]["x_uN"], -10)
        self.assertAlmostEqual(rows[0]["diagnostics"]["pad_plane_excursion_mm"]["below_lower"], .001)
        self.assertIn("Substrate", rows[0]["model_warnings"][0])
        self.assertEqual(comparison["status"], "inconclusive")
        self.assertNotIn("delta", comparison)

    def test_loaded_zero_offset_comparison_reports_height_without_centering_verdict(self):
        parameters = {key: value for key, value in CASE["parameters"].items() if key != "standoff_mm"}
        case = parse_case({**CASE, "parameters": {**parameters, "normal_load_uN": 4, "offset_mm": 0}})
        def computed(spec):
            gap = .2 if spec.volume_mm3 == .005 else .22
            return {"input": spec.to_dict(), "input_sha256": spec.sha256, "equilibrium": spec.at_gap(gap).to_dict(),
                    "status": "refinement_checked", "forces": {"x_uN": 0, "z_uN": 4}}
        with patch("soldershape.solver.solve", side_effect=computed):
            rows, comparison = calculate_comparison(case)
        self.assertNotIn("standoff_mm", rows[0]["input"])
        self.assertEqual(comparison["status"], "compared")
        self.assertAlmostEqual(comparison["delta"]["gap_mm"], .02)
        self.assertIsNone(comparison["delta"]["restoring_force_uN"])
        self.assertIn("normal load", comparison["scope"])

    def test_pretty_saved_case_fits_the_reopen_limit(self):
        prefix, suffix = '(footprint "', '" (pad "1" smd circle (at 0 0) (size .2 .2) (layers "F.Cu")))'
        source = prefix + "x"*(1_999_900-len(prefix)-len(suffix)) + suffix
        case = normalize_case({**CASE, "footprint_text": source})
        saved = (json.dumps(case, indent=2) + "\n").encode()
        self.assertGreater(len(saved), 2_000_000)
        self.assertLessEqual(len(saved), 2_100_000)
        self.assertEqual(normalize_case(json.loads(saved)), case)


class CaseHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(("127.0.0.1", 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, path, body):
        return urlopen(Request(self.url + path, data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "X-SolderShape-Token": self.server.token}), timeout=5)

    def test_live_case_open_normalizes_and_returns_original_pad_geometry(self):
        with self.post("/api/case", CASE) as response:
            data = json.load(response)
        self.assertEqual(data["case"], parse_case(CASE))
        self.assertEqual(len(data["footprint"]["pads"]), 36)
        self.assertEqual(data["footprint"]["pads"][0]["size_mm"], [.2, .2])

    def test_case_rejects_nonfinite_and_unexpected_fields(self):
        for body in ({**CASE, "baseline": {"upper_diameter_mm": .2, "volume_mm3": float("inf")}}, {**CASE, "forces": {"x_uN": 999}}):
            with self.subTest(body=list(body)), self.assertRaises(HTTPError) as caught:
                self.post("/api/case", body)
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()

    def test_compare_exports_both_failed_rows_and_input_only_case(self):
        from soldershape.solver import SolverError
        with patch("soldershape.solver.solve", side_effect=SolverError("unstable equilibrium")):
            with self.post("/api/compare", CASE) as response:
                data = json.load(response)
        self.assertEqual(data["comparison"]["status"], "inconclusive")
        self.assertEqual(len(data["results"]), 2)
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(data["bundle_base64"]))) as archive:
            self.assertEqual(json.loads(archive.read("editable-case.json")), parse_case(CASE))
            self.assertEqual(json.loads(archive.read("comparison.json"))["status"], "inconclusive")
            self.assertIn("Reference", archive.read("results.csv").decode())
            self.assertIn("Candidate", archive.read("results.csv").decode())
            self.assertEqual(json.loads(archive.read("manifest.json"))["case_count"], 2)

    def test_open_reuses_verified_existing_workbench(self):
        with patch("sys.argv", ["soldershape", "serve", "--port", str(self.server.server_port), "--open"]), patch("webbrowser.open") as opened, redirect_stdout(io.StringIO()):
            code = main()
        self.assertEqual(code, 0)
        opened.assert_called_once_with(self.url)

    def test_open_leaves_foreign_listener_alone(self):
        response = io.BytesIO(b'{"application":"Another service"}')
        with patch("sys.argv", ["soldershape", "serve", "--port", str(self.server.server_port), "--open"]), patch("soldershape.__main__.urlopen", return_value=response), patch("webbrowser.open") as opened, patch("sys.stderr", new_callable=io.StringIO):
            code = main()
        self.assertEqual(code, 2)
        opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
