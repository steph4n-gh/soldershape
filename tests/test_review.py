import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from soldershape.__main__ import calculate_comparison
from soldershape.artifacts import json_bytes, make_bundle, read_bundle, review_html, review_record
from soldershape.board import recorded_board, verify_board
from soldershape.model import InputError, joint_spec_from_dict

ROOT = Path(__file__).resolve().parents[1]


def board_rows():
    with zipfile.ZipFile(ROOT/'board_demo/data/default-comparison.zip') as archive:
        report = json.loads(archive.read('board-report.json'))
        return report, [json.loads(archive.read(f'case-{index:02d}/result.json')) for index in range(2)]


def synthetic(row, *, offset=None, loaded=False, gap=.3, **changes):
    result = copy.deepcopy(row)
    inputs = result['input']
    if offset is not None:
        inputs['offset_mm'] = offset
    if loaded:
        inputs.pop('standoff_mm', None)
        inputs['normal_load_uN'] = 10
    spec = joint_spec_from_dict(inputs)
    result['input_sha256'] = spec.sha256
    result['equilibrium'] = spec.at_gap(gap).to_dict() if loaded else spec.to_dict()
    if loaded:
        result['load_balance'] = {'target_uN': 10, 'residual_uN': 0, 'tolerance_uN': .1, 'status': 'balanced'}
        result['forces'] = {'x_uN': 0, 'z_uN': 10}
    return {**result, **changes}


def comparison_for(report, rows):
    case = copy.deepcopy(report['editable_case'])
    case['parameters'] = {key: value for key, value in rows[-1]['input'].items() if key != 'lower_diameter_mm'}
    return calculate_comparison(case, existing_results=rows)[1]


def rewrite_archive(content, change, *, reseal=True):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    change(files)
    if reseal:
        manifest = json.loads(files['manifest.json'])
        manifest['files'] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items() if name != 'manifest.json'}
        files['manifest.json'] = json_bytes(manifest)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return stream.getvalue()


class ReviewMeaning(unittest.TestCase):
    def setUp(self):
        self.report, self.rows = board_rows()
        self.source = self.report['editable_case']['footprint_text']

    def test_real_held_gap_board_facts_preserve_force_sign_and_declared_objective(self):
        review = review_record(self.rows, self.report['comparison'], source=self.source, board_selection=self.report['selection'])
        self.assertEqual(review['headline'], 'Less solder meets this declared fixture objective. More solder pushes upward.')
        self.assertIn('The objective requires lateral restoration and no upward separating force at the held gap.', review['facts'])
        self.assertIn('Restoring force 184.526 µN (toward alignment).', review['rows'][0]['facts'])
        self.assertIn('The solder pushes the upper pad upward at this held gap.', review['rows'][1]['facts'])
        self.assertEqual(review['rows'][0]['input']['upper_diameter_mm'], .4)
        self.assertEqual(review['rows'][0]['forces']['x_uN'], -184.52638094190732)
        self.assertIn({'label': 'Held wetted-plane gap', 'value': '300 µm (0.3 mm)'}, review['rows'][0]['inputs'])
        self.assertIn({'label': 'Solder volume', 'value': '40 nL (0.04 mm³)'}, review['rows'][0]['inputs'])
        self.assertEqual(review['physical_qualification'], 'unqualified')

    def test_generic_pair_keeps_facts_without_imposing_board_fixture_objective(self):
        review = review_record(self.rows, self.report['comparison'], source=self.source)
        self.assertEqual(review['comparison_status'], 'compared')
        self.assertIn('Candidate minus reference restoring force -20.1409 µN.', review['facts'])
        self.assertIn('These forces and gaps do not select a production solder volume.', review['facts'])
        self.assertNotIn('declared fixture objective', review['headline'])
        self.assertNotIn('board_selection', review['context'])

    def test_synthetic_negative_offset_and_lateral_sign_crossing(self):
        rows = [synthetic(row, offset=-.24, forces={'x_uN': force, 'z_uN': -2}) for row, force in zip(self.rows, (8, -3))]
        review = review_record(rows, comparison_for(self.report, rows), source=self.source)
        self.assertIn('Restoring force 8 µN (toward alignment).', review['rows'][0]['facts'])
        self.assertIn('Restoring force -3 µN (away from alignment).', review['rows'][1]['facts'])
        self.assertIn('Candidate minus reference restoring force -11 µN.', review['facts'])

    def test_synthetic_zero_offset_held_gap_has_no_centering_preference(self):
        rows = [synthetic(row, offset=0, forces={'x_uN': 0, 'z_uN': 2}) for row in self.rows]
        review = review_record(rows, comparison_for(self.report, rows), source=self.source, board_selection=self.report['selection'])
        self.assertEqual(review['comparison_status'], 'inconclusive')
        self.assertEqual(review['headline'], 'The comparison is inconclusive.')
        self.assertIn('Use a nonzero offset to compare centering force.', review['facts'])
        self.assertIn('Zero offset has no lateral restoration comparison.', review['rows'][0]['facts'])
        self.assertNotIn('meets this declared fixture objective', review['headline'])

    def test_synthetic_aligned_supported_load_compares_solved_gaps_and_expected_support(self):
        rows = [synthetic(row, offset=0, loaded=True, gap=gap) for row, gap in zip(self.rows, (.3, .32))]
        review = review_record(rows, comparison_for(self.report, rows), source=self.source, board_selection=self.report['selection'])
        self.assertEqual(review['comparison_status'], 'compared')
        self.assertIn('Candidate minus reference solved gap 20 µm (0.02 mm) under the same downward load.', review['facts'])
        self.assertIn('Upward load support is expected in this supported-load comparison.', review['facts'])
        self.assertIn('Zero offset has no lateral restoration comparison.', review['facts'])
        self.assertIn('Upward solder force balances the declared downward load within the numerical tolerance.', review['rows'][0]['facts'])
        self.assertNotIn('declared fixture objective', review['headline'])
        self.assertNotIn('Held wetted-plane gap', json.dumps(review['rows'][0]['inputs']))

    def test_failure_unchecked_and_scope_warning_block_comparative_conclusions(self):
        for status, warnings in [('failed', []), ('not_converged', []), ('refinement_checked', ['Substrate clearance is unknown.'])]:
            with self.subTest(status=status, warnings=warnings):
                rows = [synthetic(self.rows[0], status=status, model_warnings=warnings, error='Retained synthetic failure'), self.rows[1]]
                review = review_record(rows, comparison_for(self.report, rows), source=self.source, board_selection=self.report['selection'])
                self.assertEqual(review['comparison_status'], 'inconclusive')
                self.assertEqual(review['headline'], 'The comparison is inconclusive.')
                self.assertEqual(review['rows'][0]['warnings'], warnings)
                if status == 'failed':
                    self.assertNotIn('forces', review['rows'][0])
                    self.assertNotIn('equilibrium', review['rows'][0])
                    self.assertEqual(review['rows'][0]['error'], 'Retained synthetic failure')
                    self.assertIn('No force or solved gap is available for this failed row.', review['rows'][0]['facts'])
                elif status == 'not_converged':
                    self.assertIn('Returned numbers are unchecked numerical output. No comparative conclusion follows.', review['rows'][0]['facts'])
                else:
                    self.assertEqual(review['rows'][0]['headline'], 'A model limit blocks a design preference.')

    def test_unchecked_load_does_not_claim_balance(self):
        row = synthetic(self.rows[0], loaded=True, status='not_converged', forces={'x_uN': 1, 'z_uN': -2}, load_balance={'status': 'not_balanced'})
        review = review_record([row], source=self.source)
        self.assertIn('Positive Z is the load-support direction. This row has not established a checked load balance.', review['facts'])
        self.assertNotIn('Upward solder force balances', ' '.join(review['facts']))

    def test_single_and_sweep_keep_each_saved_row_identity_without_inventing_reference(self):
        single = review_record([self.rows[1]], source=self.source)
        self.assertEqual(single['kind'], 'single')
        self.assertNotIn('comparison_status', single)
        self.assertNotIn('Candidate minus', ' '.join(single['facts']))
        rows = [synthetic(self.rows[0], offset=-.1), synthetic(self.rows[0], offset=0),
                synthetic(self.rows[0], offset=.1, status='failed', error='Synthetic missing equilibrium')]
        for row in rows:
            row.pop('design', None)
        sweep = review_record(rows, source=self.source)
        self.assertEqual(sweep['kind'], 'sweep')
        self.assertEqual([row['input_sha256'] for row in sweep['rows']], [row['input_sha256'] for row in rows])
        self.assertEqual([row['input']['offset_mm'] for row in sweep['rows']], [-.1, 0, .1])
        self.assertNotIn('forces', sweep['rows'][2])
        self.assertEqual(sweep['headline'], 'Inspect each saved offset. No sweep optimum is claimed.')

    def test_offline_html_escapes_names_warnings_errors_and_keeps_exact_canonical_values(self):
        row = synthetic(self.rows[0], status='failed', error='<script>alert("error")</script>', model_warnings=['<img src="https://example.invalid/a">'])
        row['footprint']['name'] = '<img src=x onerror=alert(1)>'
        row['footprint']['pad']['identifier'] = '</td><script>alert(2)</script>'
        html = review_html(review_record([row], source=self.source)).decode()
        self.assertIn('&lt;script&gt;alert(&quot;error&quot;)&lt;/script&gt;', html)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', html)
        self.assertNotIn('<script', html)
        self.assertNotIn('<img', html)
        self.assertNotIn('src="https:', html)
        checked = review_html(review_record(self.rows, self.report['comparison'], source=self.source)).decode()
        self.assertIn('-184.52638094190732', checked)
        self.assertIn('40 nL (0.04 mm³)', checked)
        self.assertIn('python3 -m soldershape replay FILE.zip', checked)
        self.assertIn('isolated equilibrium joint with fully wetted pinned circular rims', checked)
        self.assertIn('Wetting chemistry, thermal reflow and neighboring joints are unresolved.', checked)
        self.assertIn('This report works as a standalone HTML file.', checked)
        self.assertIn('Its evidence links work only when it sits in the extracted accompanying evidence ZIP.', checked)
        self.assertIn('separate files, not embedded in this HTML', checked)
        self.assertIn('<h3>Links within the extracted accompanying evidence ZIP</h3>', checked)


class ReviewArchives(unittest.TestCase):
    def setUp(self):
        self.report, self.rows = board_rows()
        self.source = self.report['editable_case']['footprint_text']
        self.bundle = make_bundle(self.rows, self.source, self.report['editable_case'], self.report['comparison'])

    def read(self, content):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'evidence.zip'
            path.write_bytes(content)
            return read_bundle(path)

    def test_source_bound_bundle_contains_exact_manifest_hashed_brief(self):
        review = review_record(self.rows, self.report['comparison'], source=self.source)
        with zipfile.ZipFile(io.BytesIO(self.bundle)) as archive:
            self.assertEqual(archive.read('review.json'), json_bytes(review))
            self.assertEqual(archive.read('review.html'), review_html(review))
            manifest = json.loads(archive.read('manifest.json'))
            self.assertEqual(manifest['files']['review.html'], hashlib.sha256(review_html(review)).hexdigest())
        self.assertEqual(len(self.read(self.bundle)), 2)

    def test_unsealed_html_tamper_and_resealed_canonical_row_tamper_fail(self):
        def html(files):
            files['review.html'] += b'<p>Changed</p>'
        def canonical(files):
            review = json.loads(files['review.json'])
            review['rows'][0]['forces']['x_uN'] = 123
            files['review.json'] = json_bytes(review)
        with self.assertRaisesRegex(InputError, 'integrity'):
            self.read(rewrite_archive(self.bundle, html, reseal=False))
        with self.assertRaisesRegex(InputError, 'canonical numerical result'):
            self.read(rewrite_archive(self.bundle, canonical))

    def test_unpaired_review_is_rejected_after_resealing(self):
        with self.assertRaisesRegex(InputError, 'both review files'):
            self.read(rewrite_archive(self.bundle, lambda files: files.pop('review.html')))

    def test_renderer_wording_and_css_changes_do_not_invalidate_existing_evidence(self):
        with patch('soldershape.artifacts.review_html', return_value=b'Future CSS and wording'), patch('soldershape.artifacts._quantity', return_value='Future format'):
            self.assertEqual(len(self.read(self.bundle)), 2)

    def test_old_archives_and_source_free_study_exports_remain_unchanged(self):
        for path, digest in [('board_demo/data/default-comparison.zip', '1b87dca00de964b62cce902e071dad063b2f935f79d340817ff9e810bfff9604'),
                             ('demo/data/stress-cases.zip', '914ef334f8850be64a1c5b325647c1d9bc6adf6acfdcac6a3d04920bd4f27f24')]:
            content = (ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
            self.assertGreater(len(self.read(content)), 0)
        with zipfile.ZipFile(ROOT/'cohesion/evidence/custom-study.zip') as archive:
            self.assertNotIn('review.json', archive.namelist())
            self.assertIn('decision.html', archive.namelist())
        self.assertTrue(verify_board(ROOT/'board_demo/data/default-comparison.zip')['passed'])
        recorded, _ = recorded_board()
        self.assertIn('review', recorded)
        self.assertNotIn('review_html', recorded)
        self.assertNotIn('review', recorded['report'])
        with zipfile.ZipFile(io.BytesIO(make_bundle(self.rows))) as archive:
            self.assertNotIn('review.json', archive.namelist())
            self.assertNotIn('review.html', archive.namelist())

    def test_seven_fully_evidenced_loaded_rows_fit_existing_member_limit(self):
        with zipfile.ZipFile(ROOT/'cohesion/evidence/custom-study.zip') as archive:
            row = json.loads(archive.read('case-00/result.json'))
            row['evidence'] = json.loads(archive.read('case-00/evidence.json'))
        content = make_bundle([row]*7, self.source, self.report['editable_case'], self.report['comparison'])
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertEqual(len(archive.namelist()), 100)
            self.assertIn('review.html', archive.namelist())
        self.assertEqual(len(self.read(content)), 7)


if __name__ == '__main__':
    unittest.main()
