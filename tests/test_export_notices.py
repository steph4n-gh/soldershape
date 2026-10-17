import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from soldershape.artifacts import make_bundle, read_bundle
from soldershape.model import InputError
from soldershape.study import bundle_study

ROOT = Path(__file__).resolve().parents[1]
KICAD_SOURCE = ROOT/'examples/BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD.kicad_mod'


class ExportNotices(unittest.TestCase):
    def setUp(self):
        with zipfile.ZipFile(ROOT/'board_demo/data/default-comparison.zip') as archive:
            self.row = json.loads(archive.read('case-00/result.json'))
            self.row['evidence'] = json.loads(archive.read('case-00/evidence.json'))

    def files(self, source=''):
        with zipfile.ZipFile(io.BytesIO(make_bundle([self.row], source))) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        manifest = json.loads(files['manifest.json'])
        self.assertEqual(set(files), {'manifest.json', *manifest['files']})
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256(files[name]).hexdigest(), digest, name)
        return files

    def test_exact_kicad_example_carries_original_manifest_hashed_notice(self):
        source = KICAD_SOURCE.read_bytes()
        files = self.files(source.decode())
        self.assertEqual(files['source.kicad_mod'], source)
        self.assertEqual(files['KICAD-LICENSE.md'], (ROOT/'examples/KICAD-LICENSE.md').read_bytes())
        self.assertNotIn('BOARD-LICENSE.md', files)

    def test_generic_exports_of_extracted_board_footprints_carry_original_notice(self):
        for prefix in ('U1--', 'C1--'):
            source = next((ROOT/'board_demo/assets/footprints.pretty').glob(prefix+'*.kicad_mod')).read_bytes()
            with self.subTest(component=prefix):
                files = self.files(source.decode())
                self.assertEqual(files['source.kicad_mod'], source)
                self.assertEqual(files['BOARD-LICENSE.md'], (ROOT/'board_demo/source/LICENSE.md').read_bytes())
                self.assertNotIn('KICAD-LICENSE.md', files)

    def test_unknown_user_source_is_not_assigned_a_third_party_license(self):
        for source in ('(footprint "User footprint")', KICAD_SOURCE.read_text()+'\n'):
            with self.subTest(source=source[:40]):
                files = self.files(source)
                self.assertEqual(files['source.kicad_mod'], source.encode())
                self.assertNotIn('KICAD-LICENSE.md', files)
                self.assertNotIn('BOARD-LICENSE.md', files)

    def test_source_free_study_call_has_no_origin_notice_or_generic_review(self):
        files = self.files()
        for name in ('source.kicad_mod', 'KICAD-LICENSE.md', 'BOARD-LICENSE.md', 'review.html', 'review.json'):
            self.assertNotIn(name, files)
        with zipfile.ZipFile(ROOT/'cohesion/evidence/custom-study.zip') as archive:
            report = json.loads(archive.read('study-report.json'))
        with zipfile.ZipFile(io.BytesIO(bundle_study(report))) as archive:
            names = archive.namelist()
            self.assertIn('decision.html', names)
            self.assertEqual(archive.read('reference.kicad_mod'), report['study']['reference']['footprint_text'].encode())
            self.assertEqual(archive.read('candidate.kicad_mod'), report['study']['candidate']['footprint_text'].encode())
            for name in ('source.kicad_mod', 'KICAD-LICENSE.md', 'BOARD-LICENSE.md', 'review.html', 'review.json'):
                self.assertNotIn(name, names)

    def test_notice_bytes_are_covered_by_the_existing_integrity_check(self):
        content = make_bundle([self.row], KICAD_SOURCE.read_text())
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'evidence.zip'
            path.write_bytes(content)
            self.assertEqual(len(read_bundle(path)), 1)
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}
            files['KICAD-LICENSE.md'] += b'Changed notice'
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, value in files.items():
                    archive.writestr(name, value)
            with self.assertRaisesRegex(InputError, 'integrity check failed for KICAD-LICENSE.md'):
                read_bundle(path)


if __name__ == '__main__':
    unittest.main()
