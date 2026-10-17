import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

from soldershape.__main__ import Server
from soldershape.artifacts import json_bytes, read_bundle
from soldershape.board import DIRECTORY, board_case, default_request, read_board, recorded_board, run_board, verify_board
from soldershape.demo import screen_pair
from soldershape.model import InputError
from soldershape.solver import SolverError

ROOT = Path(__file__).resolve().parents[1]


def reseal(content, change):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    change(files)
    manifest = json.loads(files.pop("manifest.json"))
    manifest["files"] = {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}
    files["manifest.json"] = json_bytes(manifest)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return output.getvalue()


class BoardBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = read_board()
        cls.request = default_request(cls.context)

    def test_actual_dense_board_selection_derives_copper_from_original_pad(self):
        self.assertEqual(self.context["counts"]["components"], 235)
        self.assertEqual(self.context["counts"]["pads"], 1177)
        self.assertEqual(self.context["counts"]["track_objects"], 5365)
        request, selection, case = board_case(self.request, self.context)
        self.assertEqual(selection["reference"], "U1")
        self.assertEqual(selection["pad_identifier"], "J16")
        self.assertEqual(selection["pad_net"], "SDRAM_D0")
        self.assertEqual(selection["lower_diameter_mm"], .4)
        self.assertEqual(selection["board_xy_mm"], [142.88, 86.6])
        self.assertEqual(selection["local_xy_mm"], [4.4, -1.2])
        self.assertEqual(case["parameters"]["volume_mm3"], .056)
        self.assertEqual(case["baseline"]["volume_mm3"], .04)
        self.assertNotIn("lower_diameter_mm", request["parameters"])
        self.assertEqual(selection["board_sha256"], hashlib.sha256((DIRECTORY/"source/ulx3s.kicad_pcb").read_bytes()).hexdigest())

    def test_forged_identity_geometry_and_unsupported_selection_are_rejected(self):
        unsupported = next((component, pad) for component in self.context["components"] for pad in component["pads"] if not pad["supported"])
        component, pad = unsupported
        for change in ({"board_sha256": "0"*64}, {"reference": "forged"}, {"pad_index": True}, {"pad_index": 99999},
                       {"parameters": {**self.request["parameters"], "lower_diameter_mm": .2}},
                       {"parameters": {**self.request["parameters"], "normal_load_uN": 10}},
                       {"reference": component["reference"], "pad_index": pad["index"]}, {"baseline": None}, {"unexpected": 1}):
            with self.subTest(change=change), self.assertRaises(InputError):
                board_case({**self.request, **change}, self.context)

    def test_source_mutation_fails_trusted_context_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)/"board"
            shutil.copytree(DIRECTORY, directory, ignore=shutil.ignore_patterns("data"))
            path = directory/"source/ulx3s.kicad_pcb"
            path.write_bytes(path.read_bytes()+b"\n")
            with self.assertRaisesRegex(InputError, "integrity"):
                read_board(directory)

    def test_changed_loaded_calculation_source_blocks_new_computation(self):
        with patch.dict("soldershape.board.LOADED_CODE_SHA256", {"model.py": "0"*64}):
            with self.assertRaisesRegex(InputError, "Restart"):
                run_board(self.request)

    def test_recorded_default_is_two_fresh_400_micrometer_cases_and_exact_meshes(self):
        payload, verification = recorded_board()
        report = payload["report"]
        self.assertTrue(verification["passed"])
        self.assertTrue(report["recorded"])
        self.assertEqual(report["physical_qualification"], "unqualified")
        self.assertEqual([row["status"] for row in report["results"]], ["refinement_checked"]*2)
        self.assertEqual(report["screen"]["status"], "conditional_comparison")
        self.assertTrue(report["screen"]["reference_rule_met"])
        self.assertFalse(report["screen"]["candidate_rule_met"])
        self.assertAlmostEqual(report["results"][0]["forces"]["x_uN"], -184.52638094190732, places=7)
        self.assertAlmostEqual(report["results"][0]["forces"]["z_uN"], -181.28387853829275, places=7)
        self.assertAlmostEqual(report["results"][1]["forces"]["x_uN"], -164.3854725452698, places=7)
        self.assertAlmostEqual(report["results"][1]["forces"]["z_uN"], 13.385897738397528, places=7)
        for row in report["results"]:
            self.assertEqual(row["input"]["lower_diameter_mm"], .4)
            self.assertGreater(len(row["mesh"]["triangles"]), 100)
            self.assertNotIn("evidence", row)
        cases = read_bundle(DIRECTORY/"data/default-comparison.zip")
        self.assertEqual([spec.volume_mm3 for spec, _ in cases], [.04, .056])

    def test_resealed_selection_source_context_mesh_and_conclusion_tampering_fail(self):
        content = (DIRECTORY/"data/default-comparison.zip").read_bytes()
        def selection(files):
            value = json.loads(files["board-selection.json"])
            value["pad_identifier"] = "A1"
            files["board-selection.json"] = json_bytes(value)
        def source(files):
            files["board-source.kicad_pcb"] += b"\n"
        def context(files):
            value = json.loads(files["board-context.json"])
            value["components"][0]["rotation_deg"] += 1
            files["board-context.json"] = json_bytes(value)
        def conclusion(files):
            value = json.loads(files["board-report.json"])
            value["screen"]["headline"] = "Production qualified"
            files["board-report.json"] = json_bytes(value)
        def mesh(files):
            files["case-00/mesh-mm.obj"] += b"v 0 0 0\n"
        def mapping(files):
            value = json.loads(files["board-report.json"])
            value["request"]["pad_index"] = 0 if value["request"]["pad_index"] != 0 else 1
            files["board-report.json"] = json_bytes(value)
        def calculation_source(files):
            files["calculation-source/solver.py"] += b"\n"
        for change in (selection, source, context, conclusion, mesh, mapping, calculation_source):
            with self.subTest(change=change.__name__), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary)/"tampered.zip"
                path.write_bytes(reseal(content, change))
                with self.assertRaises(InputError):
                    verify_board(path)

    def test_volume_headline_follows_actual_order_and_other_geometry_stays_neutral(self):
        with zipfile.ZipFile(DIRECTORY/"data/default-comparison.zip") as archive:
            reference, candidate = [json.loads(archive.read(f"case-{index:02d}/result.json")) for index in range(2)]
        expected = "Less solder meets this declared fixture objective. More solder pushes upward."
        self.assertEqual(screen_pair(reference, candidate)["headline"], expected)
        self.assertEqual(screen_pair(candidate, reference)["headline"], expected)
        synthetic_reference = {**reference, "input": {**reference["input"], "volume_mm3": candidate["input"]["volume_mm3"], "upper_diameter_mm": .5}}
        self.assertEqual(screen_pair(synthetic_reference, candidate)["headline"], "Reference meets this declared fixture objective. Candidate pushes upward.")
        synthetic_candidate = {**candidate, "forces": {"x_uN": 0, "z_uN": -1}}
        self.assertEqual(screen_pair(reference, synthetic_candidate)["headline"], "Less solder meets this declared fixture objective. More solder does not.")


class BoardHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(("127.0.0.1", 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.request = default_request(read_board())

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, body, token=None):
        return urlopen(Request(self.url+"/api/board/compare", data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "X-SolderShape-Token": self.server.token if token is None else token}), timeout=10)

    def test_context_source_and_native_svg_are_served(self):
        with urlopen(self.url+"/api/board") as response:
            payload = json.load(response)
        self.assertEqual(payload["default_request"], self.request)
        with urlopen(self.url+"/board.svg") as response:
            self.assertEqual(hashlib.sha256(response.read()).hexdigest(), payload["context"]["svg"]["sha256"])
        with urlopen(self.url+"/board/license.txt") as response:
            self.assertEqual(response.read(), (DIRECTORY/"source/LICENSE.md").read_bytes())

    def test_auth_and_lock_and_selected_geometry_are_enforced(self):
        with self.assertRaises(HTTPError) as error:
            self.post(self.request, token="")
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        self.server.computation.acquire()
        try:
            with self.assertRaises(HTTPError) as busy:
                self.post(self.request)
            self.assertEqual(busy.exception.code, 409)
            busy.exception.close()
        finally:
            self.server.computation.release()
        with self.assertRaises(HTTPError) as forged:
            self.post({**self.request, "parameters": {**self.request["parameters"], "lower_diameter_mm": .2}})
        self.assertEqual(forged.exception.code, 400)
        forged.exception.close()

    def test_failed_native_cases_export_the_negative_result_without_qualification(self):
        with patch("soldershape.solver.solve", side_effect=SolverError("SYNTHETIC engine unavailable")):
            with self.post(self.request) as response:
                payload = json.load(response)
        self.assertEqual(payload["report"]["physical_qualification"], "unqualified")
        self.assertEqual(payload["report"]["screen"]["status"], "numerical_failure")
        self.assertEqual([row["status"] for row in payload["report"]["results"]], ["failed", "failed"])
        import base64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/"negative.zip"
            path.write_bytes(base64.b64decode(payload["bundle_base64"]))
            result = verify_board(path)
        self.assertTrue(result["passed"])
        self.assertEqual(result["screen"]["status"], "numerical_failure")
        self.assertFalse(self.server.computation.locked())


if __name__ == "__main__":
    unittest.main()
