import csv
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MODULE = importlib.util.spec_from_file_location("coupon_analysis", ROOT / "coupons/tools/analyze.py")
analysis = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(analysis)


class AnalysisChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.input_path = self.base / "inputs.csv"
        self.meta_path = self.base / "metadata.json"
        self.outcome_path = self.base / "outcomes.csv"
        self.output = self.base / "freeze"
        self.spec = analysis.read_json(analysis.COUPONS / "experiment.json")
        self.assignments = analysis.allocation()
        self.before = (datetime.now(timezone.utc)-timedelta(hours=2)).isoformat()
        self.frozen_time = (datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
        self.after = (datetime.now(timezone.utc)-timedelta(minutes=30)).isoformat()
        self.inputs = []
        for assignment in self.assignments:
            row = dict(cap_id=assignment["cap_id"], cap_mass_mg=14, cap_mass_U_mg=.01,
                       solder_kit_mass_mg=2.9, solder_kit_mass_U_mg=.01,
                       lower_diameter_mm=.22 if assignment["arm"] == "C220" else .27, lower_diameter_U_mm=.001,
                       upper_diameter_mm=.28, upper_diameter_U_mm=.001, lower_metal_um=35, lower_metal_U_um=1,
                       upper_metal_um=35, upper_metal_U_um=1, pre_offset_mm=0, pre_offset_U_mm=.001,
                       measurement_evidence="SYNTHETIC INPUT FIXTURE", measured_at_utc=self.before)
            self.inputs.append(row)
        self.metadata = dict(alloy="Sn63Pb37", flux="SYNTHETIC FLUX", reflow_profile="SYNTHETIC PROFILE",
                             temperature_C=210, temperature_U_C=2, liquid_density_g_cm3=dict(value=8.5, U=.1, source="SYNTHETIC SOURCE"),
                             surface_tension_n_m=dict(value=.48, U=.02, source="SYNTHETIC SOURCE"), coverage_factor=2,
                             pilot=dict(qualified=True, evidence="SYNTHETIC PILOT"), measurement_method="SYNTHETIC METHOD",
                             hot_method_evidence="SYNTHETIC HOT METHOD", lab="TEST ONLY")
        self.write_csv(self.input_path, analysis.INPUT_COLUMNS, self.inputs)
        analysis.write_json(self.meta_path, self.metadata)

    def write_csv(self, path, columns, rows):
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, columns)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def synthetic_solve(spec):
        height = .2 if spec.lower_diameter_mm < .25 else .19
        return {"input": spec.to_dict(), "input_sha256": spec.sha256, "status": "refinement_checked",
                "load_balance": {"status": "balanced"}, "equilibrium": spec.at_gap(height).to_dict(),
                "evidence": {"kind": "SYNTHETIC TEST DOUBLE. NOT NATIVE OR PHYSICAL DATA."}}

    def freeze(self):
        with patch.object(analysis, "solve", self.synthetic_solve), patch.object(analysis, "utc_now", return_value=self.frozen_time):
            return analysis.freeze(self.input_path, self.meta_path, self.output)

    def outcomes(self, phases=("post_reflow", "molten"), shift=0):
        rows = []
        for assignment in self.assignments:
            height = (200 if assignment["arm"] == "C220" else 190) + shift
            for phase in phases:
                rows.append(dict(cap_id=assignment["cap_id"], phase=phase, status="measured",
                                 mean_gap_um=height, mean_gap_U_um=1, min_gap_um=height-.5, min_gap_U_um=1,
                                 max_gap_um=height+.5, max_gap_U_um=1, joints_measured=20, full_volume_3d="true",
                                 observed_offset_mm=0, observed_offset_U_mm=.001, defects="none",
                                 measurement_evidence="SYNTHETIC OUTCOME FIXTURE", measured_at_utc=self.after,
                                 temperature_C=210 if phase == "molten" else 20, temperature_U_C=.5,
                                 wetted_joints=20, wetting_boundary_status="matches_frozen", wetting_evidence="SYNTHETIC WETTING OBSERVATIONS",
                                 range_U_um="", range_uncertainty_evidence="",
                                 pair_difference_U_um="", pair_uncertainty_evidence=""))
        return rows

    def score(self, rows):
        self.write_csv(self.outcome_path, analysis.OUTCOME_COLUMNS, rows)
        return analysis.score(self.output, self.outcome_path, self.base / "score.json")

    def test_synthetic_positive_is_cap_level_and_run_blocked(self):
        manifest = self.freeze()
        self.assertEqual(manifest["distinct_native_requests"], 6)
        report = self.score(self.outcomes())
        self.assertEqual(report["attempted_caps"], 24)
        self.assertEqual(len(report["runs"]), 3)
        self.assertTrue(all(run["molten"]["complete_pairs"] == 4 for run in report["runs"]))
        self.assertEqual(report["decisions"]["post_reflow"]["direction"], "C220_higher_in_all_three_runs")
        self.assertEqual(report["liquid_model_verdict"], "consistent_at_frozen_inputs")

    def test_twenty_micrometer_error_is_preserved_as_disagreement(self):
        self.freeze()
        report = self.score(self.outcomes(shift=20))
        self.assertEqual(report["liquid_model_verdict"], "disagrees_at_frozen_inputs")
        self.assertEqual(report["caps"][0]["phases"]["molten"]["models"][0]["mean_minus_prediction_um"], 20)

    def test_cold_only_cannot_qualify_liquid_model(self):
        self.freeze()
        report = self.score(self.outcomes(phases=("post_reflow",)))
        self.assertEqual(report["liquid_model_verdict"], "inconclusive")
        self.assertEqual(report["decisions"]["post_reflow"]["direction"], "C220_higher_in_all_three_runs")

    def test_missing_and_failed_caps_remain_attempted(self):
        self.freeze()
        rows = self.outcomes(phases=("post_reflow",))[2:]
        rows[0] = {"cap_id": rows[0]["cap_id"], "phase": "post_reflow", "status": "assembly_failed",
                   "defects": "SYNTHETIC open joint", "measurement_evidence": "TEST", "measured_at_utc": self.after}
        report = self.score(rows)
        self.assertEqual(report["attempted_caps"], 24)
        counts = [cap["phases"]["post_reflow"]["status"] for cap in report["caps"]]
        self.assertEqual(counts.count("measurement_missing"), 2)
        self.assertEqual(counts.count("assembly_failed"), 1)
        self.assertEqual(report["decisions"]["post_reflow"]["direction"], "inconclusive")

    def test_blank_inputs_and_unqualified_pilot_rejected_before_native(self):
        self.inputs[0]["cap_mass_mg"] = ""
        self.write_csv(self.input_path, analysis.INPUT_COLUMNS, self.inputs)
        with patch.object(analysis, "solve") as native:
            with self.assertRaises(analysis.DataError):
                analysis.freeze(self.input_path, self.meta_path, self.output)
            native.assert_not_called()
        self.metadata["pilot"]["qualified"] = False
        with self.assertRaises(analysis.DataError):
            analysis.validate_metadata(self.metadata, self.spec)

    def test_outcome_leakage_in_inputs_and_duplicate_inputs_rejected(self):
        self.write_csv(self.input_path, analysis.INPUT_COLUMNS+("measured_gap_um",), self.inputs)
        with self.assertRaises(analysis.DataError):
            analysis.freeze(self.input_path, self.meta_path, self.output)
        self.inputs[0]["cap_id"] = self.inputs[1]["cap_id"]
        self.write_csv(self.input_path, analysis.INPUT_COLUMNS, self.inputs)
        with self.assertRaises(analysis.DataError):
            analysis.freeze(self.input_path, self.meta_path, self.output)

    def test_duplicate_unknown_or_early_outcomes_rejected(self):
        self.freeze()
        rows = self.outcomes()
        for changed in (rows+[rows[0]], [dict(row, cap_id="unknown") for row in rows],
                        [dict(row, measured_at_utc=self.before) for row in rows]):
            with self.subTest(changed=changed[0]["cap_id"]):
                with self.assertRaises(analysis.DataError):
                    self.score(changed)

    def test_missing_uncertainty_and_partial_minimum_cannot_pass(self):
        self.freeze()
        rows = self.outcomes()
        rows[0]["min_gap_U_um"] = ""
        with self.assertRaises(analysis.DataError):
            self.score(rows)
        rows = self.outcomes()
        rows[0].update(full_volume_3d="false", joints_measured=4)
        report = self.score(rows)
        value = report["caps"][0]["phases"]["post_reflow"]
        self.assertEqual(value["clearance"], "inconclusive")
        self.assertFalse(value["geometry_gate"])

    def test_frozen_input_tampering_rejected(self):
        self.freeze()
        with (self.output / "inputs.csv").open("a") as stream:
            stream.write("\n")
        with self.assertRaises(analysis.DataError):
            self.score(self.outcomes())

    def test_offset_drift_keeps_clearance_but_blocks_model_agreement(self):
        self.freeze()
        rows = self.outcomes()
        rows[1]["observed_offset_mm"] = .01
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertEqual(value["clearance"], "above_guardband")
        self.assertFalse(value["frozen_offset_consistency_gate"])
        self.assertEqual(value["central_model_agreement"], "inconclusive")

    def test_two_slab_conversion_and_solder_excluded_from_external_load(self):
        spec = analysis.read_json(analysis.COUPONS / "experiment.json")
        row = self.inputs[0]
        literal, correction = analysis.request(row, self.metadata, spec, "literal_rims")
        secondary, secondary_correction = analysis.request(row, self.metadata, spec, "two_pad_cylinders")
        self.assertAlmostEqual(literal.volume_mm3, 2.9/20/8.5)
        self.assertAlmostEqual(literal.normal_load_uN, 14*9.80665/20)
        self.assertEqual(correction, 0)
        self.assertEqual(secondary_correction, 70)
        self.assertGreater(secondary.volume_mm3, literal.volume_mm3)
        self.assertFalse(secondary.gravity)

    def test_native_failure_is_retained_not_replaced_by_formula(self):
        def failed(spec):
            return {"input": spec.to_dict(), "status": "failed", "error": "SYNTHETIC NATIVE FAILURE"}
        with patch.object(analysis, "solve", failed):
            analysis.freeze(self.input_path, self.meta_path, self.output)
        rows = analysis.read_json(self.output / "predictions.json")["caps"]
        self.assertIsNone(rows[0]["models"][0]["predicted_pad_face_gap_um"])
        self.assertEqual(rows[0]["models"][0]["native_error"], "SYNTHETIC NATIVE FAILURE")

    def test_unobserved_wetting_cannot_qualify_model_or_process_pair(self):
        self.freeze()
        rows = self.outcomes()
        rows[1].update(wetting_boundary_status="unobserved", wetted_joints="", wetting_evidence="")
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertEqual(value["clearance"], "above_guardband")
        self.assertEqual(value["central_model_agreement"], "inconclusive")
        self.assertEqual(report["liquid_model_verdict"], "inconclusive")
        self.assertEqual(report["decisions"]["molten"]["direction"], "inconclusive")

    def test_boundary_mismatch_keeps_observed_process_pair(self):
        self.freeze()
        rows = self.outcomes()
        rows[1].update(wetting_boundary_status="fails")
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertEqual(value["central_model_agreement"], "inconclusive")
        self.assertEqual(report["decisions"]["molten"]["direction"], "C220_higher_in_all_three_runs")

    def test_gap_range_includes_uncertainty(self):
        self.freeze()
        rows = self.outcomes()
        rows[1].update(min_gap_um=198.75, max_gap_um=201.25)
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertEqual(value["clearance"], "above_guardband")
        self.assertEqual(value["central_model_agreement"], "inconclusive")
        self.assertEqual(report["decisions"]["molten"]["direction"], "inconclusive")

    def test_lab_supplied_correlated_range_budget_requires_evidence(self):
        self.freeze()
        rows = self.outcomes()
        rows[1].update(min_gap_um=198.75, max_gap_um=201.25, range_U_um=.4,
                       range_uncertainty_evidence="SYNTHETIC CORRELATED RANGE BUDGET")
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertAlmostEqual(value["guarded_gap_range_um"], 2.9)
        self.assertEqual(value["central_model_agreement"], "consistent_at_frozen_inputs")
        rows[1]["range_uncertainty_evidence"] = ""
        with self.assertRaises(analysis.DataError):
            self.score(rows)

    def test_matching_boundary_and_wetting_counts_require_evidence(self):
        self.freeze()
        for changes in ({"wetting_evidence": ""}, {"wetted_joints": 19},
                        {"wetting_boundary_status": "unknown"}):
            with self.subTest(changes=changes):
                rows = self.outcomes()
                rows[1].update(changes)
                with self.assertRaises(analysis.DataError):
                    self.score(rows)

    def test_unknown_boundary_with_twenty_wetted_joints_keeps_process_comparison(self):
        self.freeze()
        rows = self.outcomes()
        rows[1].update(wetting_boundary_status="unobserved")
        report = self.score(rows)
        value = report["caps"][0]["phases"]["molten"]
        self.assertEqual(value["central_model_agreement"], "inconclusive")
        self.assertEqual(report["decisions"]["molten"]["direction"], "C220_higher_in_all_three_runs")

    def test_unqualified_hot_method_keeps_cold_decision(self):
        self.metadata["hot_method_evidence"] = None
        analysis.write_json(self.meta_path, self.metadata)
        self.freeze()
        report = self.score(self.outcomes())
        self.assertEqual(report["liquid_model_verdict"], "inconclusive")
        self.assertEqual(report["decisions"]["molten"]["direction"], "inconclusive")
        self.assertEqual(report["decisions"]["post_reflow"]["direction"], "C220_higher_in_all_three_runs")
        self.assertEqual(report["caps"][0]["phases"]["post_reflow"]["central_model_agreement"], "inconclusive")

    def test_frozen_solid_temperature_cannot_be_called_molten(self):
        for temperature, uncertainty in ((20, .5), (184, 1)):
            with self.subTest(temperature=temperature, uncertainty=uncertainty):
                self.metadata.update(temperature_C=temperature, temperature_U_C=uncertainty)
                analysis.write_json(self.meta_path, self.metadata)
                with patch.object(analysis, "solve") as native:
                    with self.assertRaises(analysis.DataError):
                        analysis.freeze(self.input_path, self.meta_path, self.output)
                    native.assert_not_called()
                self.assertFalse(self.output.exists())

    def test_molten_temperature_interval_must_fit_frozen_plateau(self):
        self.freeze()
        for temperature, uncertainty in ((210, 100), (209, 2)):
            with self.subTest(temperature=temperature, uncertainty=uncertainty):
                rows = self.outcomes()
                rows[1].update(temperature_C=temperature, temperature_U_C=uncertainty)
                report = self.score(rows)
                value = report["caps"][0]["phases"]["molten"]
                self.assertFalse(value["temperature_gate"])
                self.assertEqual(value["central_model_agreement"], "inconclusive")


if __name__ == "__main__":
    unittest.main()
