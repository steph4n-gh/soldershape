import copy
import hashlib
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from soldershape.artifacts import read_bundle
from soldershape.model import InputError
from soldershape.study import _analytical, _requests, bundle_study, read_study, replay_study, run_study

ROOT = Path(__file__).resolve().parents[1]


def planning():
    return json.loads((ROOT / "examples/coupon-planning.study.json").read_text())


def synthetic_native(spec):
    height = _analytical(spec, 0)["gap_um"]
    if height is None:
        height = 220.0
    equilibrium = spec.at_gap(height/1000).to_dict()
    return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked", "equilibrium": equilibrium,
            "forces": {"x_uN": 0, "z_uN": spec.normal_load_uN},
            "load_balance": {"target_uN": spec.normal_load_uN, "status": "balanced", "residual_uN": 0, "tolerance_uN": .01},
            "engine": {"source_sha256": "synthetic-test-double", "binary_sha256": "synthetic-test-double"},
            "model_warnings": [], "evidence": {"stdout": "SYNTHETIC TEST DOUBLE. Not native computation.", "commands": "archived evidence only"},
            "mesh": {"vertices_mm": [[0, 0, 0], [.1, 0, 0], [0, .1, 0], [0, 0, .1]],
                     "triangles": [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]}}


def reseal(content, mutation, reseal_manifest=True):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    mutation(files)
    if reseal_manifest:
        manifest = json.loads(files["manifest.json"])
        manifest["files"] = {name: hashlib.sha256(value).hexdigest() for name, value in files.items() if name != "manifest.json"}
        files["manifest.json"] = json.dumps(manifest).encode()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)
    return stream.getvalue()


class StudyInputs(unittest.TestCase):
    def test_changed_files_cannot_be_stamped_as_the_loaded_code(self):
        for name in ("model.py", "solver.py", "study.py"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                shutil.copytree(ROOT / "soldershape", base / "soldershape", ignore=shutil.ignore_patterns("__pycache__"))
                (base / "study.json").write_text(json.dumps(planning()))
                script = """import json
from pathlib import Path
from soldershape.study import run_study
from soldershape.model import InputError
path = Path('soldershape') / __import__('sys').argv[1]
path.write_bytes(path.read_bytes()+b'\\n')
try:
    run_study(json.loads(Path('study.json').read_text()))
except InputError as error:
    assert 'Restart SolderShape' in str(error), str(error)
else:
    raise AssertionError('Changed source was accepted as loaded code')
"""
                result = subprocess.run([sys.executable, "-c", script, name], cwd=base, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_opposite_native_and_analytical_ordering_is_inconclusive(self):
        data = planning()
        data.update(two_pad=None, volume_fraction=0)
        data["candidate"]["footprint_text"] = data["reference"]["footprint_text"].replace("0.22 0.22", "0.2201 0.2201")
        def perturbed_numerical_double(spec):
            result = synthetic_native(spec)
            height = result["equilibrium"]["standoff_mm"] + (-.0001 if spec.lower_diameter_mm == .22 else .0001)
            result["equilibrium"] = spec.at_gap(height).to_dict()
            return result
        with patch("soldershape.study.solve", side_effect=perturbed_numerical_double):
            report = run_study(data)
        self.assertGreater(report["nominal"][1]["native_gap_um"], report["nominal"][0]["native_gap_um"])
        self.assertLess(report["nominal"][1]["analytical_gap_um"], report["nominal"][0]["analytical_gap_um"])
        self.assertEqual(report["decision"]["status"], "assumption_sensitive")

    def test_nominal_methods_on_opposite_sides_cannot_screen_the_criterion(self):
        data = planning()
        data.update(two_pad=None, volume_fraction=0)
        data["requirement"]["pad_face_gap_um"] = 223.33
        def measured_numerical_case(spec):
            result = synthetic_native(spec)
            gap = 223.31880160132934 if spec.lower_diameter_mm == .22 else 207.52181485954353
            result["equilibrium"] = spec.at_gap(gap/1000).to_dict()
            return result
        with patch("soldershape.study.solve", side_effect=measured_numerical_case):
            report = run_study(data)
        self.assertLess(report["nominal"][0]["margin_um"], 0)
        self.assertGreater(report["nominal"][0]["analytical_gap_um"]-223.33, 0)
        self.assertEqual(report["decision"]["status"], "assumption_sensitive")

    def test_two_sources_control_actual_requests_and_round_trip(self):
        study = read_study(planning())
        self.assertEqual(read_study(study), study)
        rows = list(_requests(study))
        self.assertEqual(len(rows), 4)
        self.assertEqual([row[2].lower_diameter_mm for row in rows], [.22, .27, .22, .27])
        self.assertNotEqual(rows[0][4]["sha256"], rows[1][4]["sha256"])
        self.assertNotEqual(rows[0][2].sha256, rows[1][2].sha256)
        self.assertNotIn("standoff_mm", rows[0][2].to_dict())
        self.assertAlmostEqual(rows[2][2].volume_mm3, .020642881727962935, places=12)
        self.assertEqual(rows[2][3], 70)

    def test_independent_formula_retained_reference_values(self):
        rows = list(_requests(read_study(planning())))
        expected = [223.34907200981604, 207.51966907047608, 178.24975366079877, 167.31802279103346]
        for (_, _, spec, correction, _), value in zip(rows, expected):
            analytical = _analytical(spec, correction)
            self.assertTrue(analytical["eligible"])
            self.assertAlmostEqual(analytical["gap_um"], value, places=8)
            self.assertLess(analytical["compression_fraction"], .01)

    def test_missing_evidence_mask_conflict_and_parameter_override_rejected(self):
        mutations = [lambda data: data["candidate"].update(boundary_evidence=" "),
                     lambda data: data.update(input_evidence=""),
                     lambda data: data["requirement"].update(source=""),
                     lambda data: data["two_pad"].update(evidence=""),
                     lambda data: data["parameters"].update(lower_diameter_mm=.3),
                     lambda data: data["parameters"].update(standoff_mm=.2),
                     lambda data: data.update(volume_fraction=.21),
                     lambda data: data.update(volume_fraction=True),
                     lambda data: data["parameters"].update(gravity=True),
                     lambda data: data["candidate"].update(footprint_text=data["candidate"]["footprint_text"].replace('(size 0.27 0.27)', '(solder_mask_margin -0.01) (size 0.27 0.27)'))]
        for mutation in mutations:
            data = planning()
            mutation(data)
            with self.subTest(data=data), self.assertRaises(InputError):
                read_study(data)


class SyntheticStudyPolicy(unittest.TestCase):
    @patch("soldershape.study.solve", side_effect=synthetic_native)
    def test_declared_hypotheses_reverse_criterion_without_physical_pass(self, native):
        report = run_study(planning())
        self.assertEqual(native.call_count, 4)
        self.assertEqual(report["decision"]["status"], "assumption_sensitive")
        self.assertEqual(report["physical_qualification"], "unqualified")
        self.assertEqual(len(report["samples"]), 12)
        self.assertTrue(all(row["eligible"] for row in report["samples"]))
        self.assertTrue(all(row["margin_um"] > 0 for row in report["nominal"][:2]))
        self.assertTrue(all(row["margin_um"] < 0 for row in report["nominal"][2:]))
        self.assertIn("not measured physical solder shape", report["results"][2]["mesh_scope"])
        self.assertEqual(report["results"][0]["input"]["lower_diameter_mm"], .22)
        self.assertEqual(report["results"][1]["input"]["lower_diameter_mm"], .27)

    @patch("soldershape.study.solve", side_effect=synthetic_native)
    def test_literal_only_unchanged_samples_and_unsupported_screens(self, native):
        data = planning()
        data["two_pad"] = None
        self.assertEqual(run_study(data)["decision"]["status"], "screened_samples")
        for change in ({"offset_mm": .02}, {"gravity": True}, {"normal_load_uN": 1000}):
            altered = copy.deepcopy(data)
            altered["parameters"].update(change)
            report = run_study(altered)
            self.assertEqual(report["decision"]["status"], "sensitivity_unavailable")
            self.assertFalse(any(row["eligible"] for row in report["samples"]))
        self.assertEqual(len(run_study(data)["results"]), 2)

    def test_failed_native_case_keeps_raw_evidence_and_blocks_conclusion(self):
        def failed(spec):
            return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "failed", "error": "synthetic failure",
                    "evidence": {"failed_native_attempt": {"stdout": "SYNTHETIC negative control", "commands": "never run"}}}
        with patch("soldershape.study.solve", side_effect=failed):
            report = run_study(planning())
        self.assertEqual(report["decision"]["status"], "numerical_failure")
        self.assertEqual(len(report["results"]), 4)
        self.assertIsNone(report["results"][0]["pad_face_gap_um"])
        with zipfile.ZipFile(io.BytesIO(bundle_study(report))) as archive:
            self.assertIn(b"SYNTHETIC negative control", archive.read("case-00/load-height/stdout.txt"))

    def test_nominal_disagreement_blocks_screened_conclusion(self):
        def disagree(spec):
            result = synthetic_native(spec)
            result["equilibrium"]["standoff_mm"] += .002
            return result
        data = planning()
        data["two_pad"] = None
        with patch("soldershape.study.solve", side_effect=disagree):
            report = run_study(data)
        self.assertEqual(report["decision"]["status"], "sensitivity_unavailable")
        self.assertAlmostEqual(report["nominal"][0]["native_minus_analytical_um"], 2)


class SyntheticStudyArchive(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "study.zip"
        with patch("soldershape.study.solve", side_effect=synthetic_native):
            self.report = run_study(planning())
        self.content = bundle_study(self.report)
        self.path.write_bytes(self.content)

    def test_readable_sources_equivalent_mesh_labels_and_deterministic_archive(self):
        self.assertEqual(len(read_bundle(self.path)), 4)
        self.assertEqual(bundle_study(self.report), self.content)
        with zipfile.ZipFile(self.path) as archive:
            for name in ("study.json", "study-report.json", "reference.kicad_mod", "candidate.kicad_mod", "samples.csv", "decision.html"):
                self.assertIn(name, archive.namelist())
            self.assertIn("case-02/equivalent-domain-mm.obj", archive.namelist())
            self.assertNotIn("case-02/mesh-mm.obj", archive.namelist())
            self.assertIn(b"Physical qualification is unqualified", archive.read("decision.html"))
        with patch("soldershape.study.solve", side_effect=synthetic_native) as solver:
            replay = replay_study(self.path)
        self.assertTrue(replay["passed"], replay)
        self.assertEqual(solver.call_count, 4)
        self.assertTrue(replay["requests_regenerated"])

    def test_integrity_tampering_and_resealed_conclusions_are_rejected(self):
        def bad_conclusion(files):
            report = json.loads(files["study-report.json"])
            report["decision"]["headline"] = "Fabrication approved."
            files["study-report.json"] = json.dumps(report).encode()
        for reseal_manifest in (False, True):
            self.path.write_bytes(reseal(self.content, bad_conclusion, reseal_manifest))
            with patch("soldershape.study.solve") as native:
                replay = replay_study(self.path)
            self.assertFalse(replay["passed"])
            self.assertFalse(native.called)

    def test_resealed_study_change_cannot_reuse_stored_native_requests(self):
        def change_input(files):
            study = json.loads(files["study.json"])
            study["parameters"]["volume_mm3"] *= 1.01
            report = json.loads(files["study-report.json"])
            report["study"] = study
            from soldershape.study import _digest
            report["study_sha256"] = _digest(study)
            files["study.json"] = json.dumps(study).encode()
            files["study-report.json"] = json.dumps(report).encode()
        self.path.write_bytes(reseal(self.content, change_input))
        with patch("soldershape.study.solve") as native:
            replay = replay_study(self.path)
        self.assertFalse(replay["passed"])
        self.assertIn("regenerated study request", replay["error"])
        self.assertFalse(native.called)

    def test_resealed_calculation_source_edit_is_rejected(self):
        self.path.write_bytes(reseal(self.content, lambda files: files.update({"calculation-source/model.py": b"changed source"})))
        with patch("soldershape.study.solve") as native:
            result = replay_study(self.path)
        self.assertFalse(result["passed"])
        self.assertIn("calculation source", result["error"])
        self.assertFalse(native.called)

    def test_static_report_escapes_evidence_and_replay_never_executes_archived_commands(self):
        data = planning()
        data["input_evidence"] = '<script>alert("x")</script>'
        with patch("soldershape.study.solve", side_effect=synthetic_native):
            report = run_study(data)
        content = bundle_study(report)
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document = archive.read("decision.html")
            self.assertNotIn(b"<script>", document)
            self.assertIn(b"&lt;script&gt;", document)
            self.assertIn(b"External supported load per joint", document)
            self.assertIn(b"6.864655", document)
            self.assertIn(b"Surface tension, N/m", document)
            self.assertIn(b"Lower finished metal 35.0", document)
            for filename, digest in report["calculation_code_sha256"].items():
                self.assertEqual(hashlib.sha256(archive.read("calculation-source/"+filename)).hexdigest(), digest)
        marker = Path(self.directory.name) / "must-not-exist"
        def commands(files):
            files["case-00/run.cmd"] = f"touch {marker}".encode()
        self.path.write_bytes(reseal(content, commands))
        with patch("soldershape.study.solve", side_effect=synthetic_native):
            self.assertTrue(replay_study(self.path)["passed"])
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
