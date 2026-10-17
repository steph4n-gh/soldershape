import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

from soldershape.__main__ import Server, replay
from soldershape.artifacts import make_bundle, read_bundle
from soldershape.model import InputError, JointSpec, LoadSpec, import_footprint, request_from_footprint


ROOT = Path(__file__).resolve().parents[1]
SOURCE = next((ROOT / "examples").glob("*.kicad_mod")).read_text()
PARAMETERS = json.loads((ROOT / "examples" / "parameters.json").read_text())


class Boundaries(unittest.TestCase):
    def test_actual_kicad_geometry(self):
        footprint = import_footprint(SOURCE)
        self.assertEqual(len(footprint["pads"]), 36)
        self.assertEqual(footprint["pads"][0]["identifier"], "A1")
        self.assertEqual(footprint["pads"][0]["size_mm"], [.2, .2])
        self.assertEqual(footprint["pads"][0]["x_mm"], -1)

    def test_quoted_labels_and_duplicate_identifiers_keep_distinct_indices(self):
        source = '(footprint "A \\"quoted\\" name" (pad "=1+1" smd circle (at 0 0) (size .2 .2) (layers "F.Cu")) (pad "=1+1" smd circle (at .4 0) (size .3 .3) (layers "F.Cu")))'
        footprint = import_footprint(source)
        self.assertEqual([p["index"] for p in footprint["pads"]], [0, 1])
        self.assertEqual(footprint["pads"][1]["size_mm"], [.3, .3])

    def test_selected_diameter_comes_from_footprint(self):
        spec, provenance = request_from_footprint(SOURCE, 0, PARAMETERS)
        self.assertEqual(spec.lower_diameter_mm, .2)
        self.assertEqual(provenance["pad"]["identifier"], "A1")
        with self.assertRaises(InputError):
            request_from_footprint(SOURCE, 0, {**PARAMETERS, "lower_diameter_mm": 5})

    def test_malformed_footprints_are_rejected(self):
        for source in (SOURCE + ")", '(footprint "bad" (pad "1" smd circle (at nan 0) (size .2 .2) (layers "F.Cu")))', '(footprint "bad" (pad "1" smd circle (at 0 0) (size .2 .2) (layers (unexpected))))'):
            with self.subTest(source=source[-80:]), self.assertRaises(InputError):
                import_footprint(source)

    def test_unsupported_pad_is_visible_but_cannot_be_solved(self):
        source = '(footprint "rect" (pad "1" smd rect (at 0 0) (size .2 .3) (layers "F.Cu")))'
        self.assertFalse(import_footprint(source)["pads"][0]["supported"])
        with self.assertRaises(InputError):
            request_from_footprint(source, 0, PARAMETERS)

    def test_numeric_and_boolean_domains(self):
        spec, _ = request_from_footprint(SOURCE, 0, PARAMETERS)
        for changes in ({"offset_mm": float("nan")}, {"offset_mm": True}, {"volume_mm3": 0}, {"gravity": "false"}, {"unknown": 1}):
            with self.subTest(changes=changes), self.assertRaises(InputError):
                JointSpec.from_dict({**spec.to_dict(), **changes})

    def test_failed_row_evidence_and_csv_survive_export(self):
        spec, _ = request_from_footprint(SOURCE, 0, PARAMETERS)
        row = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": "deliberate numerical failure", "evidence": {"stdout": "negative result retained"}}
        data = make_bundle([row], SOURCE)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertIn("deliberate numerical failure", archive.read("results.csv").decode())
            self.assertEqual(archive.read("case-00/stdout.txt"), b"negative result retained")
            self.assertIn("case-00/evidence.json", archive.namelist())
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "case.zip"
            path.write_bytes(data)
            self.assertEqual(read_bundle(path)[0][1]["status"], "failed")
            tampered = io.BytesIO()
            with zipfile.ZipFile(io.BytesIO(data)) as original, zipfile.ZipFile(tampered, "w") as changed:
                for name in original.namelist():
                    changed.writestr(name, b"tampered" if name == "case-00/stdout.txt" else original.read(name))
            path.write_bytes(tampered.getvalue())
            with self.assertRaisesRegex(InputError, "integrity"):
                read_bundle(path)

    def test_replay_reports_each_failed_case_and_continues(self):
        from soldershape.solver import SolverError
        spec, _ = request_from_footprint(SOURCE, 0, PARAMETERS)
        row = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": "original failure"}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "failed.zip"
            path.write_bytes(make_bundle([row, row], SOURCE))
            output = io.StringIO()
            with patch("soldershape.solver.solve", side_effect=SolverError("same upstream failure")) as mocked, redirect_stdout(output):
                code = replay(path)
            report = json.loads(output.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(mocked.call_count, 2)
            self.assertEqual(len(report["replay"]), 2)
            self.assertFalse(report["passed"])
            self.assertTrue(all(r["current_status"] == "failed" and not r["passed"] for r in report["replay"]))

    def test_loaded_replay_rebalances_and_retains_current_failure(self):
        spec = LoadSpec(.27, .28, .01745, 0, 4, gravity=False)
        saved = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked",
                 "equilibrium": spec.at_gap(.22).to_dict(), "forces": {"x_uN": 0, "z_uN": 4}, "engine": {},
                 "load_balance": {"target_uN": 4, "residual_uN": 0, "tolerance_uN": .01, "status": "balanced"}}
        saved["evidence"] = {"fixed_gap_verification": {"evidence": {"model_fe": "static model", "commands": "static commands"}},
                             "native_height_solve": {"evidence": {"model_fe": "loaded model", "commands": "loaded commands"}}}
        failed = {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": "Load has no checked equilibrium."}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "loaded.zip"
            path.write_bytes(make_bundle([saved]))
            with zipfile.ZipFile(path) as archive:
                self.assertEqual(archive.read("case-00/model.fe"), b"static model")
                self.assertEqual(archive.read("case-00/run.cmd"), b"static commands")
                self.assertEqual(archive.read("case-00/load-height/model.fe"), b"loaded model")
                self.assertEqual(archive.read("case-00/load-height/run.cmd"), b"loaded commands")
            output = io.StringIO()
            with patch("soldershape.solver.solve", return_value=failed) as solver, redirect_stdout(output):
                code = replay(path)
            self.assertEqual(code, 1)
            self.assertIsInstance(solver.call_args.args[0], LoadSpec)
            self.assertNotIn("standoff_mm", solver.call_args.args[0].to_dict())
            self.assertEqual(json.loads(output.getvalue())["replay"][0]["error"], failed["error"])
            path.write_bytes(make_bundle([failed]))
            self.assertIsInstance(read_bundle(path)[0][0], LoadSpec)
            with zipfile.ZipFile(path) as archive:
                self.assertNotIn("standoff_mm", json.loads(archive.read("case-00/input.json")))
                self.assertNotIn("case-00/mesh-mm.stl", archive.namelist())


class LocalHTTP(unittest.TestCase):
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

    def post(self, value, token=True, **headers):
        base = {"Content-Type": "application/json"}
        if token:
            base["X-SolderShape-Token"] = self.server.token
        return urlopen(Request(self.url + "/api/import", data=json.dumps(value).encode(), headers={**base, **headers}), timeout=5)

    def test_live_import_returns_actual_geometry(self):
        with self.post({"footprint_text": SOURCE}) as response:
            self.assertEqual(len(json.load(response)["footprint"]["pads"]), 36)

    def test_missing_local_session_is_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            self.post({"footprint_text": SOURCE}, token=False)
        self.assertEqual(caught.exception.code, 403)
        caught.exception.close()

    def test_foreign_origin_is_rejected_even_with_token(self):
        with self.assertRaises(HTTPError) as caught:
            self.post({"footprint_text": SOURCE}, Origin="https://example.com")
        self.assertEqual(caught.exception.code, 403)
        caught.exception.close()

    def test_unknown_fields_are_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            self.post({"footprint_text": SOURCE, "command": "not an operation"})
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()


if __name__ == "__main__":
    unittest.main()
