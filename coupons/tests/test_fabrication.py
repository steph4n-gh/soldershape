from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

COUPONS = Path(__file__).resolve().parents[1]
MODULE = importlib.util.spec_from_file_location("coupon_boards", COUPONS / "tools/verify_boards.py")
boards = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(boards)


class ManufacturingChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        for directory in ("fabrication", "hardware", "evidence"):
            shutil.copytree(COUPONS / directory, self.base / directory)
        for filename in ("experiment.json", "allocation.csv"):
            shutil.copyfile(COUPONS / filename, self.base / filename)

    def verify(self):
        with patch.object(boards, "HERE", self.base), redirect_stdout(io.StringIO()):
            boards.main()

    def test_delivered_exports_match_controlled_comparison(self):
        self.verify()

    def test_wrong_lower_pad_size_is_rejected(self):
        path = self.base / "fabrication/carrier/carrier-F_Cu.gtl"
        source = path.read_text()
        self.assertIn("C,0.220000", source)
        path.write_text(source.replace("C,0.220000", "C,0.230000"))
        with self.assertRaises(AssertionError):
            self.verify()

    def test_smaller_cap_mask_window_is_rejected(self):
        path = self.base / "fabrication/cap/cap-B_Mask.gbs"
        source = path.read_text()
        self.assertIn("X100000", source)
        path.write_text(source.replace("X100000", "X150000"))
        with self.assertRaises(AssertionError):
            self.verify()

    def test_unexpected_opposite_side_copper_is_rejected(self):
        source = self.base / "fabrication/cap/cap-B_Cu.gbl"
        shutil.copyfile(source, self.base / "fabrication/cap/cap-F_Cu.gtl")
        with self.assertRaises(AssertionError):
            self.verify()


if __name__ == "__main__":
    unittest.main()
