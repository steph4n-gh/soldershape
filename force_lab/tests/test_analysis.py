from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from force_lab.tools import analyze as a

SYNTHETIC_ENGINE = {"ready": True, "identity": "SYNTHETIC TEST ENGINE, NOT NATIVE EVIDENCE"}


def synthetic_solver(spec):
    forces = {"x_uN": -1000 * spec.offset_mm + 5000 * (spec.volume_mm3 - .005), "z_uN": 50000 * (spec.volume_mm3 - .006) - 100 * (spec.standoff_mm - .15) + 3 * (spec.lower_diameter_mm - .2)}
    return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked", "forces": forces, "model_warnings": [], "diagnostics": {"force_component_changes": {"x": {"absolute_uN": .0001}, "z": {"absolute_uN": .0001}}}, "engine": dict(SYNTHETIC_ENGINE), "evidence": {"synthetic": True}}


class ProspectiveForceBehavior(unittest.TestCase):
    def setUp(self):
        self.engine_patch = patch.object(a, "engine_info", return_value=dict(SYNTHETIC_ENGINE))
        self.engine_patch.start()
        self.addCleanup(self.engine_patch.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "inputs"
        a.templates(self.source)
        self.assignments = a.assignments()
        rows = []
        before = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        for row in self.assignments:
            rows.append({"specimen_id": row["specimen_id"], "lower_diameter_mm": .2, "upper_diameter_mm": .2, "standoff_mm": .15, "offset_mm": row["offset_mm"], "volume_mm3": row["volume_mm3"], "transverse_offset_mm": 0, "transverse_U_mm": .0001, "measured_at_utc": before, "measurement_evidence": "SYNTHETIC independent input"})
        a.save_csv(self.source / "inputs.csv", a.INPUT_COLUMNS, rows)
        metadata = a.read_json((self.source / "metadata.json").read_bytes())
        metadata.update({key: "SYNTHETIC evidence" for key, value in metadata.items() if value is None})
        metadata.update(temperature_C=300, temperature_U_C=1, liquidus_C=220, coverage_factor=2, commissioning_passed=True, inputs_independent_of_forces=True, unlinked_sources_independent=True, input_observed_at_utc=before, surface_tension_n_m={"value": .48, "evidence": "SYNTHETIC independent gamma"}, density_g_cm3={"value": 9, "evidence": "SYNTHETIC independent density"})
        a.write_json(self.source / "metadata.json", metadata)
        for filename in ("input_covariance.json", "calibration.json"):
            data = a.read_json((self.source / filename).read_bytes())
            data.update(budget_complete=True, completeness_evidence="SYNTHETIC complete budget")
            if filename == "calibration.json":
                data.update(coverage_factor=2, coverage_justification="SYNTHETIC normal known variances")
            for item in data["components"]:
                item.update(standard_u=.1 if filename == "calibration.json" else .0000001, evidence="SYNTHETIC known uncertainty")
            a.write_json(self.source / filename, data)
        self.freeze_path = self.root / "freeze"

    def tearDown(self):
        self.temp.cleanup()

    def freeze(self):
        with patch.object(a, "solve", side_effect=synthetic_solver):
            result = a.freeze(self.source, self.freeze_path)
        self.sha = result["manifest_sha256"]
        return result

    def outcomes(self, change=None):
        rows = []
        inputs = {row["specimen_id"]: row for row in a.csv_rows((self.source / "inputs.csv").read_bytes(), a.INPUT_COLUMNS)}
        for assignment in self.assignments:
            row = inputs[assignment["specimen_id"]]
            spec = a.JointSpec(**{field: float(row[field]) for field in a.FIELDS})
            result = synthetic_solver(spec)
            item = {"specimen_id": row["specimen_id"], "status": "measured", "corrected_force_uN": result["forces"][assignment["axis"] + "_uN"], "measured_at_utc": datetime.now(timezone.utc).isoformat(), "measurement_evidence": "SYNTHETIC force", "wetting_boundary": "pinned_both", "wetting_evidence": "SYNTHETIC image", "stable": "true", "stability_evidence": "SYNTHETIC dwell", "actual_gap_mm": .15, "actual_offset_mm": row["offset_mm"], "actual_transverse_offset_mm": 0, "actual_transverse_U_mm": .0001, "actual_temperature_C": 300, "tilt_deg": 0, "dwell_drift_um": .01}
            if change:
                change(item, assignment)
            rows.append(item)
        path = self.root / "outcomes.csv"
        a.save_csv(path, a.OUTCOME_COLUMNS, rows)
        return path

    def test_blank_templates_are_not_physical_inputs(self):
        blank = self.root / "blank"
        a.templates(blank)
        with self.assertRaisesRegex(a.DataError, "required|recorded|required exactly"):
            a.freeze(blank, self.freeze_path)
        self.assertFalse(self.freeze_path.exists())

    def test_rejects_any_preexisting_confirmation_outcome_file(self):
        (self.source / "outcomes.csv").write_text("even an empty file is forbidden")
        with self.assertRaisesRegex(a.DataError, "must not exist"):
            a.freeze(self.source, self.freeze_path)

    def test_freeze_snapshots_exact_supplied_bytes_and_reuses_identical_requests(self):
        metadata = self.source / "metadata.json"
        metadata.write_bytes(metadata.read_bytes() + b"\n \n")
        result = self.freeze()
        self.assertEqual((self.freeze_path / "metadata.json").read_bytes(), metadata.read_bytes())
        self.assertEqual(result["specimens"], 48)
        self.assertLess(result["distinct_native_requests"], 48 * 15)
        self.assertEqual(a.frozen(self.freeze_path, self.sha)[0]["eligible_native_predictions"], 48)

    def test_shared_bias_does_not_shrink_with_specimen_count(self):
        weights = {str(i): 1 / 6 for i in range(6)}
        common = [{"standard_u": 5, "coefficients": dict.fromkeys(weights, 1)}]
        separate = [{"standard_u": 5, "coefficients": {key: 1}} for key in weights]
        self.assertAlmostEqual(a.variance(weights, common), 25)
        self.assertAlmostEqual(a.variance(weights, separate), 25 / 6)
        contrast = {"five": -1, "seven": 1}
        self.assertEqual(a.variance(contrast, [{"standard_u": 5, "coefficients": {"five": 1, "seven": 1}}]), 0)
        self.assertEqual(a.variance(contrast, [{"standard_u": 5, "coefficients": {"five": 1, "seven": -1}}]), 100)

    def test_edited_freeze_or_manifest_cannot_pass_registered_digest(self):
        self.freeze()
        path = self.freeze_path / "predictions.json"
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        with self.assertRaisesRegex(a.DataError, "Frozen bytes changed"):
            a.frozen(self.freeze_path, self.sha)
        manifest_path = self.freeze_path / "manifest.json"
        manifest = a.read_json(manifest_path.read_bytes())
        manifest["files"]["predictions.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        a.write_json(manifest_path, manifest)
        with self.assertRaisesRegex(a.DataError, "independently registered"):
            a.frozen(self.freeze_path, self.sha)

    def test_synthetic_exact_forces_support_only_declared_endpoints(self):
        self.freeze()
        report = a.score(self.freeze_path, self.outcomes(), self.root / "score", self.sha)
        self.assertEqual(report["allocated_independent_specimens"], 48)
        self.assertEqual(len(report["endpoints"]), 6)
        self.assertTrue(all(item["status"] == "agreement_within_declared_guard" for item in report["endpoints"]))
        self.assertAlmostEqual(report["endpoints"][3]["observed_uN"], 10)
        self.assertTrue(report["endpoints"][5]["observed_sign_resolved"])

    def test_sign_inversion_is_a_disagreement(self):
        self.freeze()
        outcomes = self.outcomes(lambda row, assignment: row.update(corrected_force_uN=-row["corrected_force_uN"]))
        report = a.score(self.freeze_path, outcomes, self.root / "score", self.sha)
        self.assertTrue(all(item["status"] == "disagreement_exceeds_declared_guard" for item in report["endpoints"]))

    def test_common_x_bias_cannot_qualify_absolute_force_predictions(self):
        self.freeze()
        def bias(row, assignment):
            if assignment["axis"] == "x":
                row["corrected_force_uN"] += 50
        report = a.score(self.freeze_path, self.outcomes(bias), self.root / "score", self.sha)
        contrasts = [item for item in report["endpoints"] if item["kind"] == "5_minus_7nL_restoring_magnitude"]
        self.assertTrue(all(item["status"] == "agreement_within_declared_guard" for item in contrasts))
        self.assertEqual(report["overall_status"], "disagreement_exceeds_declared_guard")
        self.assertTrue(all(item["status"] == "disagreement_exceeds_declared_guard" for item in report["absolute_lateral_force_assessments"]))

    def test_unknown_wetting_and_unstable_forces_are_inconclusive(self):
        self.freeze()
        outcomes = self.outcomes(lambda row, assignment: row.update(wetting_boundary="unobserved", stable="unknown"))
        report = a.score(self.freeze_path, outcomes, self.root / "score", self.sha)
        self.assertTrue(all(item["status"] == "inconclusive" for item in report["endpoints"]))

    def test_duplicate_frame_is_not_an_independent_specimen(self):
        self.freeze()
        path = self.outcomes()
        rows = a.csv_rows(path.read_bytes(), a.OUTCOME_COLUMNS)
        a.save_csv(path, a.OUTCOME_COLUMNS, rows + rows[:1])
        with self.assertRaisesRegex(a.DataError, "duplicate outcome"):
            a.score(self.freeze_path, path, self.root / "score", self.sha)

    def test_opposing_block_biases_cannot_cancel_into_agreement(self):
        self.freeze()
        def bias(row, assignment):
            if assignment["axis"] == "z":
                row["corrected_force_uN"] += {"1": 10, "2": -10, "3": 0}[assignment["block"]]
        report = a.score(self.freeze_path, self.outcomes(bias), self.root / "score", self.sha)
        normals = [item for item in report["endpoints"] if item["kind"] == "mean_normal_force"]
        self.assertTrue(all(item["status"] == "disagreement_exceeds_declared_guard" for item in normals))
        self.assertTrue(all(item["individual_disagreements"] for item in normals))

    def test_actual_geometry_drift_is_inconclusive(self):
        self.freeze()
        report = a.score(self.freeze_path, self.outcomes(lambda row, assignment: row.update(actual_gap_mm=.151)), self.root / "score", self.sha)
        self.assertTrue(all(item["status"] == "inconclusive" for item in report["endpoints"]))

    def test_nonfinite_or_outcome_bearing_input_is_rejected(self):
        path = self.source / "input_covariance.json"
        data = a.read_json(path.read_bytes())
        data["outcomes"] = [100]
        a.write_json(path, data)
        with self.assertRaisesRegex(a.DataError, "cannot contain outcomes"):
            a.freeze(self.source, self.freeze_path)

    def test_unknown_uncertainty_rejects_freeze(self):
        path = self.source / "calibration.json"
        data = a.read_json(path.read_bytes())
        data["budget_complete"] = None
        a.write_json(path, data)
        with self.assertRaisesRegex(a.DataError, "unknown or incomplete"):
            a.freeze(self.source, self.freeze_path)

    def add_shared_temperature(self, volume_coefficient):
        path = self.source / "input_covariance.json"
        data = a.read_json(path.read_bytes())
        data["components"].append({"id": "shared-temperature", "source_unit": "K", "standard_u": 1, "evidence": "SYNTHETIC common temperature", "coefficients": {row["specimen_id"] + ".volume_mm3": volume_coefficient for row in self.assignments}})
        a.write_json(path, data)
        path = self.source / "calibration.json"
        data = a.read_json(path.read_bytes())
        data["components"] = [{"id": "shared-temperature", "source_unit": "K", "standard_u": 1, "evidence": "SYNTHETIC same temperature", "coefficients": {row["specimen_id"]: 1 for row in self.assignments}}]
        a.write_json(path, data)

    def test_shared_opposite_input_and_force_sensitivities_fail_precision_gate(self):
        self.add_shared_temperature(-.00002)
        self.freeze()
        report = a.score(self.freeze_path, self.outcomes(), self.root / "score", self.sha)
        normal = report["endpoints"][-1]
        self.assertEqual(normal["status"], "inconclusive")
        self.assertAlmostEqual(normal["measurement_U_uN"], 2)
        self.assertAlmostEqual(normal["residual_first_order_U_uN"], 4.000002083349458)
        self.assertEqual(report["overall_status"], "inconclusive")

    def test_matching_shared_input_and_force_sensitivities_cancel_in_residual_only(self):
        self.add_shared_temperature(.00002)
        self.freeze()
        report = a.score(self.freeze_path, self.outcomes(), self.root / "score", self.sha)
        normal = report["endpoints"][-1]
        self.assertEqual(normal["status"], "agreement_within_declared_guard")
        self.assertAlmostEqual(normal["measurement_U_uN"], 2)
        self.assertAlmostEqual(normal["input_first_order_U_uN"], 2.000004166696746)
        self.assertAlmostEqual(normal["residual_first_order_U_uN"], .004082491611299)

    def test_shared_source_cannot_use_inconsistent_units_or_standard_uncertainties(self):
        self.add_shared_temperature(.00002)
        path = self.source / "calibration.json"
        original = a.read_json(path.read_bytes())
        for field, value in (("source_unit", "uN"), ("standard_u", .5)):
            with self.subTest(field=field):
                data = json.loads(json.dumps(original))
                data["components"][0][field] = value
                a.write_json(path, data)
                with self.assertRaisesRegex(a.DataError, "inconsistent standard uncertainty or source unit"):
                    a.freeze(self.source, self.freeze_path)

    def test_unknown_cross_domain_independence_rejects_freeze(self):
        path = self.source / "metadata.json"
        data = a.read_json(path.read_bytes())
        data["unlinked_sources_independent"] = None
        a.write_json(path, data)
        with self.assertRaisesRegex(a.DataError, "Unknown cross-domain covariance"):
            a.freeze(self.source, self.freeze_path)

    def test_unbounded_transverse_alignment_rejects_freeze(self):
        path = self.source / "inputs.csv"
        rows = a.csv_rows(path.read_bytes(), a.INPUT_COLUMNS)
        rows[0]["transverse_offset_mm"] = .040
        a.save_csv(path, a.INPUT_COLUMNS, rows)
        with self.assertRaisesRegex(a.DataError, "Transverse displacement"):
            a.freeze(self.source, self.freeze_path)

    def test_unknown_frozen_transverse_uncertainty_rejects_freeze(self):
        path = self.source / "inputs.csv"
        rows = a.csv_rows(path.read_bytes(), a.INPUT_COLUMNS)
        rows[0]["transverse_U_mm"] = ""
        a.save_csv(path, a.INPUT_COLUMNS, rows)
        with self.assertRaisesRegex(a.DataError, "transverse expanded uncertainty is required"):
            a.freeze(self.source, self.freeze_path)

    def test_unbounded_or_unobserved_confirmation_transverse_alignment_is_inconclusive(self):
        self.freeze()
        for name, values in (("displaced", {"actual_transverse_offset_mm": .040}), ("unknown", {"actual_transverse_U_mm": ""}), ("uncertain", {"actual_transverse_U_mm": .0006})):
            with self.subTest(name=name):
                report = a.score(self.freeze_path, self.outcomes(lambda row, assignment: row.update(values)), self.root / name, self.sha)
                self.assertEqual(report["overall_status"], "inconclusive")
                self.assertTrue(all(item["status"] == "inconclusive" for item in report["endpoints"]))

    def test_plan_verifier_rederives_targets_flags_requests_and_complete_members(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            a.plan(directory)
        self.assertEqual(a.verify_plan(directory)["native_requests"], 20)
        path = directory / "plan.json"
        original = a.read_json(path.read_bytes())
        mutations = (
            lambda report: report["planning_targets"].update(lateral_contrast_uN=99999999),
            lambda report: report["planning_budget_scenarios"]["initial_budget_negative_control"].update(normal_gate_passes_local_screen=True),
            lambda report: report["cases"][0]["sensitivity_checks"][0].update(qualified=False),
            lambda report: report["cases"][0]["sensitivity_checks"][0].update(step=.005),
            lambda report: report["cases"][0].update(eligible=False),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                report = json.loads(json.dumps(original))
                mutate(report)
                a.write_json(path, report)
                with self.assertRaisesRegex(a.DataError, "differ from raw receipts"):
                    a.verify_plan(directory)
        a.write_json(path, original)
        (directory / "extra-receipt.txt").write_text("unlisted")
        with self.assertRaisesRegex(a.DataError, "member set changed"):
            a.verify_plan(directory)

    def test_static_plan_verification_needs_no_local_engine(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            a.plan(directory)
        with patch.object(a, "engine_info", return_value={"ready": False}) as local_engine, patch.object(a, "solve", side_effect=AssertionError("Static verification must not replay")):
            report = a.verify_plan(directory)
            local_engine.assert_not_called()
        self.assertEqual(report["native_requests"], 20)
        self.assertFalse(report["native_replay_performed"])

    def test_registered_frozen_verification_and_scoring_need_no_local_engine(self):
        self.freeze()
        with patch.object(a, "engine_info", return_value={"ready": False}) as local_engine, patch.object(a, "solve", side_effect=AssertionError("Frozen scoring must not replay")):
            manifest, _ = a.frozen(self.freeze_path, self.sha)
            report = a.score(self.freeze_path, self.outcomes(), self.root / "score", self.sha)
            local_engine.assert_not_called()
        self.assertEqual(manifest["engine"], SYNTHETIC_ENGINE)
        self.assertEqual(report["overall_status"], "supports_declared_force_endpoints_only")

    def test_wrong_archived_engine_contradicting_receipts_rejects_plan_and_freeze(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            a.plan(directory)
        for directory, filename, verify in ((directory, "plan.json", lambda path, sha: a.verify_plan(path)), (self.freeze_path, "manifest.json", a.frozen)):
            with self.subTest(filename=filename):
                if filename == "manifest.json":
                    self.freeze()
                path = directory / filename
                data = a.read_json(path.read_bytes())
                data["engine"]["identity"] = "WRONG ARCHIVED PRODUCER"
                a.write_json(path, data)
                with self.assertRaisesRegex(a.DataError, "receipt engine contradicts"):
                    verify(directory, a.digest(path.read_bytes()))

    def test_failed_attempts_without_engine_identity_remain_verifiable_failure_evidence(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=a.SolverError("SYNTHETIC failed native attempt")), patch.object(a, "engine_info", return_value={"ready": False}):
            report = a.plan(directory)
        self.assertTrue(all(not case["eligible"] and case["status"] == "failed" for case in report["cases"]))
        self.assertEqual(a.verify_plan(directory)["native_requests"], 20)

    def test_completed_receipt_cannot_lose_its_engine_identity(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            a.plan(directory)
        path = directory / "plan.json"
        report = a.read_json(path.read_bytes())
        name = next(name for name in report["files"] if name.startswith("receipts/"))
        receipt = a.read_json(gzip.decompress((directory / name).read_bytes()))
        receipt.pop("engine")
        (directory / name).write_bytes(gzip.compress(json.dumps(receipt).encode()))
        report["files"][name] = a.digest((directory / name).read_bytes())
        a.write_json(path, report)
        with self.assertRaisesRegex(a.DataError, "completed native receipt requires"):
            a.verify_plan(directory)

    def test_static_verification_still_rejects_stale_source_and_protocol_identity(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            a.plan(directory)
        self.freeze()
        with patch.dict(a.CODE, {"force_lab/tools/analyze.py": "stale source"}):
            with self.assertRaisesRegex(a.DataError, "Loaded calculation code differs"):
                a.verify_plan(directory)
            with self.assertRaisesRegex(a.DataError, "Loaded calculation code differs"):
                a.frozen(self.freeze_path, self.sha)
        path = directory / "plan.json"
        report = a.read_json(path.read_bytes())
        report["protocol_sha256"] = "stale protocol"
        a.write_json(path, report)
        with self.assertRaisesRegex(a.DataError, "Planning source or protocol differs"):
            a.verify_plan(directory)

    def test_unresolved_density_finite_difference_never_becomes_allowable_tolerance(self):
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=synthetic_solver):
            report = a.plan(directory)
        limits = report["planning_targets"]["one_source_at_a_time_limits"]["density_g_cm3"]
        self.assertIsNone(limits["normal_7nL_max_expanded_U_if_only_source"])
        self.assertIsNone(limits["contrast_max_expanded_U_if_fully_shared"])
        self.assertEqual(limits["resolution"], {"shared_contrast": False, "independent_contrast": False, "normal_7nL": False})

    def test_resolved_derivative_does_not_allow_extrapolation_outside_frozen_domain(self):
        def tiny_resolved_density(spec):
            result = synthetic_solver(spec)
            result["forces"]["z_uN"] += .03 * (spec.density_g_cm3 - 9)
            return result
        directory = self.root / "plan"
        with patch.object(a, "solve", side_effect=tiny_resolved_density):
            report = a.plan(directory)
        limits = report["planning_targets"]["one_source_at_a_time_limits"]["density_g_cm3"]
        self.assertEqual(limits["resolution"]["normal_7nL"], True)
        self.assertAlmostEqual(limits["max_expanded_U_within_registered_local_domain"]["normal_7nL"], .18)
        self.assertIsNone(limits["normal_7nL_max_expanded_U_if_only_source"])


if __name__ == "__main__":
    unittest.main()
