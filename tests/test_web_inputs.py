from html.parser import HTMLParser
from pathlib import Path
import unittest

from soldershape.model import InputError, JointSpec

ROOT = Path(__file__).resolve().parents[1]


class Inputs(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.fields = {}
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        fields = dict(attributes)
        if tag == 'input' and fields.get('type') == 'number':
            self.fields[fields['id']] = fields


class BrowserInputRanges(unittest.TestCase):
    def test_board_browser_range_matches_canonical_boundary(self):
        fields = Inputs((ROOT/'soldershape/web/board.html').read_text()).fields
        defaults = dict(lower_diameter_mm=.4, upper_diameter_mm=.4, standoff_mm=.3,
                        volume_mm3=.056, offset_mm=.24, surface_tension_n_m=.48, density_g_cm3=9)
        names = [('upper-diameter', 'upper_diameter_mm', 1000), ('held-gap', 'standoff_mm', 1000),
                 ('offset', 'offset_mm', 1000), ('candidate-volume', 'volume_mm3', 1000),
                 ('reference-volume', 'volume_mm3', 1000), ('surface-tension', 'surface_tension_n_m', 1),
                 ('density', 'density_g_cm3', 1)]
        for element, parameter, scale in names:
            with self.subTest(field=element):
                bounds = fields[element]
                self.assertIn('min', bounds)
                self.assertIn('max', bounds)
                low, high = float(bounds['min'])/scale, float(bounds['max'])/scale
                for value in (low, high):
                    JointSpec(**{**defaults, parameter:value})
                for value in (low-max(abs(low)*1e-6, 1e-9), high+max(abs(high)*1e-6, 1e-9)):
                    with self.assertRaises(InputError):
                        JointSpec(**{**defaults, parameter:value})


if __name__ == '__main__':
    unittest.main()
