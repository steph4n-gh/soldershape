"""Reject matching replay values when their request or engine identity differs."""

import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prelab.campaign import ROOT, read
from prelab.replay import replay


class ReplayIdentity(unittest.TestCase):
    def test_forged_worker_identity_cannot_pass_by_preserving_forces(self):
        campaign = ROOT / "prelab/evidence/campaign"
        if not (campaign / "manifest.json").exists():
            self.skipTest("Run the native campaign before replay identity checks.")
        recorded_engine = read(campaign / "manifest.json")["engine"]
        for damage in ("load", "input_hash", "producer_engine", "result_engine", "missing_result_engine"):
            with self.subTest(damage=damage), tempfile.TemporaryDirectory() as temporary:
                def substitute(command, **kwargs):
                    source = campaign / "receipts" / (Path(command[-2]).stem + ".json.gz")
                    with gzip.open(source, "rt") as stream:
                        result = json.load(stream)
                    if damage == "load":
                        result["input"]["normal_load_uN"] += 1
                    elif damage == "input_hash":
                        result["input_sha256"] = "0" * 64
                    elif damage == "producer_engine":
                        result["producer_engine"]["binary_sha256"] = "0" * 64
                    elif damage == "result_engine":
                        result.setdefault("engine", {})["binary_sha256"] = "0" * 64
                    else:
                        result.pop("engine", None)
                    with gzip.open(command[-1], "wt") as stream:
                        json.dump(result, stream)
                with patch("prelab.replay.engine_info", return_value=recorded_engine), patch("prelab.replay.subprocess.run", side_effect=substitute):
                    with self.assertRaisesRegex(ValueError, "Fresh replay"):
                        replay(campaign, Path(temporary) / "replay")


if __name__ == "__main__":
    unittest.main()
