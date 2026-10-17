"""Coupon conversion and completed campaign integrity checks."""

import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import gzip

from prelab.campaign import ROOT, plan, read, request, verify, sha, encode


class CouponRequests(unittest.TestCase):
    def setUp(self):
        self.protocol = read(ROOT / "prelab/protocol.json")
        self.nominal = self.protocol["scenarios"][0]

    def test_nominal_units_and_liquid_volume(self):
        item = request(self.protocol, self.nominal, "C220", "literal_rims")
        self.assertAlmostEqual(item.spec.normal_load_uN, 6.864655, places=10)
        self.assertAlmostEqual(item.spec.volume_mm3, .01715728467880506, places=14)
        self.assertEqual(item.correction_um, 0)
        self.assertEqual(item.spec.lower_diameter_mm, .22)
        self.assertEqual(item.spec.upper_diameter_mm, .28)

    def test_both_metal_cylinders_are_counted_once(self):
        item = request(self.protocol, self.nominal, "C220", "two_pad_cylinders")
        self.assertAlmostEqual(item.spec.volume_mm3, .020642881727962935, places=14)
        self.assertAlmostEqual(item.correction_um, 70, places=12)
        self.assertFalse(item.spec.gravity)

    def test_opposed_screened_spheres_are_not_a_second_volume_factor(self):
        scenario = next(s for s in self.protocol["scenarios"] if s["id"] == "opposed-requested-endpoints")
        a = request(self.protocol, scenario, "C220", "literal_rims")
        b = request(self.protocol, scenario, "C270", "literal_rims")
        self.assertAlmostEqual(a.spec.volume_mm3, .016758294230568287, places=14)
        self.assertAlmostEqual(b.spec.volume_mm3, .01756255831234901, places=14)
        self.assertAlmostEqual(a.spec.lower_diameter_mm, .225, places=12)
        self.assertAlmostEqual(b.spec.upper_diameter_mm, .275, places=12)

    def test_mass_changes_load_and_does_not_add_solder_weight(self):
        changed = copy.deepcopy(self.nominal)
        changed["common"]["cap_mass_mg"] = 28
        a = request(self.protocol, self.nominal, "C220", "literal_rims")
        b = request(self.protocol, changed, "C220", "literal_rims")
        self.assertEqual(b.spec.normal_load_uN, 2 * a.spec.normal_load_uN)
        self.assertEqual(b.spec.volume_mm3, a.spec.volume_mm3)

    def test_all_rows_remain_accounted_for_when_native_inputs_recur(self):
        table = plan(self.protocol)
        self.assertEqual(len(table["rows"]), 64)
        self.assertEqual(len(table["jobs"]), 61)
        self.assertIn(table["negative_control"], table["jobs"])
        for row in table["rows"]:
            self.assertIn(row["request_sha256"], table["jobs"])

    def test_published_paper_cannot_be_relabelled_as_actual_coupon(self):
        self.protocol["domain"] = "published_Table3"
        with self.assertRaisesRegex(ValueError, "actual coupon"):
            plan(self.protocol)

    def test_identical_and_reversed_geometries_have_matching_native_requests(self):
        original_a = request(self.protocol, self.nominal, "C220", "literal_rims")
        original_b = request(self.protocol, self.nominal, "C270", "literal_rims")
        self.protocol["parameters"]["lower_nominal_mm"] = {"C220": .27, "C270": .22}
        reverse_a = request(self.protocol, self.nominal, "C220", "literal_rims")
        reverse_b = request(self.protocol, self.nominal, "C270", "literal_rims")
        self.assertEqual(reverse_a.spec.sha256, original_b.spec.sha256)
        self.assertEqual(reverse_b.spec.sha256, original_a.spec.sha256)
        self.protocol["parameters"]["lower_nominal_mm"]["C270"] = .27
        identical = request(self.protocol, self.nominal, "C270", "literal_rims")
        self.assertEqual(identical.spec.sha256, reverse_a.spec.sha256)


class CompletedCampaign(unittest.TestCase):
    directory = ROOT / "prelab/evidence/campaign"

    def setUp(self):
        if not (self.directory / "manifest.json").exists():
            self.skipTest("Run the declared native campaign before integrity tests.")

    def test_real_campaign_verifies_and_negative_control_is_retained(self):
        result = verify(self.directory)
        self.assertEqual(result["expanded_rows"], 64)
        self.assertEqual(result["distinct_requests"], 61)
        self.assertTrue(result["negative_control_rejected"])

    def test_rehashed_forged_conclusion_still_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "campaign"
            shutil.copytree(self.directory, target)
            report = read(target / "report.json")
            report["pairs"][0]["C220_minus_C270_um"] = 999
            (target / "report.json").write_bytes(encode(report))
            manifest = read(target / "manifest.json")
            manifest["files"]["report.json"] = sha((target / "report.json").read_bytes())
            (target / "manifest.json").write_bytes(encode(manifest))
            with self.assertRaisesRegex(ValueError, "conclusion"):
                verify(target)

    def test_removing_failed_control_cannot_improve_the_verdict(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "campaign"
            shutil.copytree(self.directory, target)
            table = read(target / "plan.json")
            (target / "receipts" / (table["negative_control"] + ".json.gz")).unlink()
            with self.assertRaisesRegex(ValueError, "member set"):
                verify(target)

    def test_rehashed_success_without_native_engine_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "campaign"
            shutil.copytree(self.directory, target)
            table = read(target / "plan.json")
            name = "receipts/" + table["rows"][0]["request_sha256"] + ".json.gz"
            with gzip.open(target / name, "rt") as stream:
                result = json.load(stream)
            result.pop("engine")
            with gzip.open(target / name, "wt") as stream:
                json.dump(result, stream)
            manifest = read(target / "manifest.json")
            manifest["files"][name] = sha((target / name).read_bytes())
            (target / "manifest.json").write_bytes(encode(manifest))
            with self.assertRaisesRegex(ValueError, "engine identity"):
                verify(target)


if __name__ == "__main__":
    unittest.main()
