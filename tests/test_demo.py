import hashlib
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
from soldershape.demo import read_demo
from soldershape.model import InputError, parse_case

ROOT = Path(__file__).resolve().parents[1]


class RecordedDemo(unittest.TestCase):
    def test_unrelated_native_failure_cannot_match_hessian_warning(self):
        from tools.verify_demo import failure_signature
        common = {"termination": "completed", "returncode": 0}
        hessian = {**common, "stderr": "WARNING 1825: Hessian not positive definite. Index: 7"}
        another = {**common, "stderr": "WARNING 9999: Unsupported command"}
        self.assertNotEqual(failure_signature(hessian), failure_signature(another))
        self.assertNotEqual(failure_signature(hessian), failure_signature({**common, "stderr": ""}))

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        shutil.copytree(ROOT/"demo/data", self.directory/"data")
        for name in ("protocol.json", "recording.json"):
            shutil.copy2(ROOT/"demo"/name, self.directory/name)

    def reseal(self, change):
        path = self.directory/"data/stress-cases.zip"
        with zipfile.ZipFile(path) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        change(files)
        manifest = json.loads(files.pop("manifest.json"))
        manifest["files"] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
        files["manifest.json"] = json_bytes(manifest)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        identity = json.loads((self.directory/"recording.json").read_text())
        identity["archive_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.directory/"recording.json").write_bytes(json_bytes(identity))

    def test_actual_recording_shows_contrast_scope_limit_and_failed_control(self):
        demo = read_demo(self.directory)
        self.assertEqual(demo["physical_qualification"], "unqualified")
        normal = demo["samples"][1]
        self.assertEqual(normal["id"], "offset-120")
        self.assertAlmostEqual(normal["reference"]["forces"]["x_uN"], -92.263283646421, places=7)
        self.assertGreater(normal["candidate"]["forces"]["z_uN"], 0)
        self.assertTrue(normal["screen"]["reference_rule_met"])
        self.assertFalse(normal["screen"]["candidate_rule_met"])
        self.assertEqual(demo["samples"][2]["screen"]["status"], "outside_model_scope")
        self.assertIsNone(demo["samples"][2]["screen"]["candidate_rule_met"])
        self.assertEqual(demo["samples"][3]["candidate"]["status"], "failed")
        self.assertNotIn("mesh", demo["samples"][3]["candidate"])
        self.assertEqual(demo["samples"][3]["screen"]["status"], "numerical_failure")

    def test_editable_cases_preserve_volume_comparison_and_distinct_gap_control(self):
        for point in read_demo(self.directory)["samples"]:
            case = parse_case(point["editable_case"])
            self.assertEqual(case["parameters"], {key: value for key, value in point["candidate"]["input"].items() if key != "lower_diameter_mm"})
            if point["kind"] == "volume_comparison":
                self.assertEqual(case["baseline"]["volume_mm3"], .005)
                self.assertEqual(case["parameters"]["volume_mm3"], .007)
            else:
                self.assertIsNone(case["baseline"])
                self.assertEqual(case["parameters"]["standoff_mm"], .06)

    def test_unsealed_archive_edit_is_rejected(self):
        path = self.directory/"data/stress-cases.zip"
        path.write_bytes(path.read_bytes()+b"changed")
        with self.assertRaisesRegex(InputError, "archive differs"):
            read_demo(self.directory)

    def test_resealed_wrong_request_cannot_reuse_native_receipt(self):
        def change(files):
            from soldershape.model import JointSpec
            row = json.loads(files["case-00/result.json"])
            row["input"]["offset_mm"] = .041
            row["input_sha256"] = JointSpec.from_dict(row["input"]).sha256
            files["case-00/result.json"] = json_bytes(row)
            files["case-00/input.json"] = json_bytes(row["input"])
        self.reseal(change)
        with self.assertRaisesRegex(InputError, "differs from its protocol"):
            read_demo(self.directory)

    def test_resealed_source_copy_must_match_recorded_identity(self):
        self.reseal(lambda files: files.update({"calculation-source/model.py": files["calculation-source/model.py"]+b"\n"}))
        with self.assertRaisesRegex(InputError, "source differs"):
            read_demo(self.directory)

    def test_verified_byte_snapshot_is_used_if_original_archive_changes(self):
        def change_original(snapshot):
            (self.directory/"data/stress-cases.zip").write_bytes(b"changed after capture")
            return read_bundle(snapshot)
        with patch("soldershape.demo.read_bundle", side_effect=change_original):
            self.assertEqual(read_demo(self.directory)["archive"]["case_count"], 7)


class DemoHTTP(unittest.TestCase):
    def test_recorded_route_never_runs_solver_and_download_matches_display(self):
        server = Server(("127.0.0.1", 0))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_port}"
        with patch("soldershape.solver.solve", side_effect=AssertionError("Recorded page must not solve.")):
            with urlopen(base+"/api/demo") as response:
                demo = json.load(response)
            with urlopen(base+demo["archive"]["url"]) as response:
                payload = response.read()
                self.assertEqual(response.headers.get_content_type(), "application/zip")
            self.assertEqual(hashlib.sha256(payload).hexdigest(), demo["archive"]["sha256"])
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(base+"/api/demo", headers={"Origin": "https://outside.invalid"}))
        self.addCleanup(error.exception.close)
        self.assertEqual(error.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
