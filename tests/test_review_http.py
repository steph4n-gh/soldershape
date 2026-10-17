import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen
import zipfile

from soldershape.__main__ import Server
from soldershape.artifacts import json_bytes, review_html
from soldershape.board import verify_board
from soldershape.solver import SolverError
from soldershape.model import InputError

ROOT = Path(__file__).resolve().parents[1]


class ReviewHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(('127.0.0.1', 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        with zipfile.ZipFile(ROOT/'board_demo/data/default-comparison.zip') as archive:
            cls.report = json.loads(archive.read('board-report.json'))
            cls.rows = [json.loads(archive.read(f'case-{index:02d}/result.json')) for index in range(2)]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, path, body):
        with urlopen(Request(self.url+path, data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json', 'X-SolderShape-Token': self.server.token}), timeout=10) as response:
            return json.load(response)

    def computed(self, spec):
        row = copy.deepcopy(next(row for row in self.rows if row['input']['volume_mm3'] == spec.volume_mm3))
        self.assertEqual(row['input'], spec.to_dict())
        return row

    def assert_bound_review(self, payload):
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload['bundle_base64']))) as archive:
            self.assertEqual(payload['review_html'].encode(), archive.read('review.html'))
            self.assertEqual(payload['review_html'].encode(), review_html(payload['review']))
            self.assertEqual(json_bytes(payload['review']), archive.read('review.json'))
            return archive.namelist()

    def test_generic_comparison_response_and_download_use_identical_saved_rows_and_brief(self):
        with patch('soldershape.solver.solve', side_effect=self.computed):
            payload = self.post('/api/compare', self.report['editable_case'])
        self.assert_bound_review(payload)
        self.assertEqual(payload['review']['kind'], 'comparison')
        self.assertEqual(payload['review']['rows'][0]['input_sha256'], self.rows[0]['input_sha256'])
        self.assertNotIn('board_selection', payload['review']['context'])

    def test_fresh_board_response_has_brief_without_changing_archived_report_protocol(self):
        with patch('soldershape.solver.solve', side_effect=self.computed):
            payload = self.post('/api/board/compare', self.report['request'])
        self.assert_bound_review(payload)
        self.assertNotIn('review', payload['report'])
        self.assertEqual(payload['review']['context']['board_selection']['pad_identifier'], 'J16')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'board.zip'
            path.write_bytes(base64.b64decode(payload['bundle_base64']))
            self.assertTrue(verify_board(path)['passed'])
            with zipfile.ZipFile(path) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}
            altered = json.loads(files['review.json'])
            altered['rows'][0]['forces']['x_uN'] = 123
            files['review.json'] = json_bytes(altered)
            manifest = json.loads(files['manifest.json'])
            manifest['files'] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items() if name != 'manifest.json'}
            files['manifest.json'] = json_bytes(manifest)
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(InputError, 'canonical numerical result'):
                verify_board(path)

    def test_failed_row_review_and_export_preserve_failure_without_substituted_forces(self):
        case = self.report['editable_case']
        body = {key: case[key] for key in ('footprint_text', 'pad_index', 'parameters')}
        with patch('soldershape.solver.solve', side_effect=SolverError('SYNTHETIC <script>engine failure</script>')):
            payload = self.post('/api/solve', body)
        self.assert_bound_review(payload)
        row = payload['review']['rows'][0]
        self.assertEqual(payload['review']['kind'], 'single')
        self.assertEqual(row['numerical_status'], 'failed')
        self.assertNotIn('forces', row)
        self.assertNotIn('equilibrium', row)
        self.assertEqual(row['error'], 'SYNTHETIC <script>engine failure</script>')
        self.assertIn('&lt;script&gt;engine failure&lt;/script&gt;', payload['review_html'])
        self.assertNotIn('<script>', payload['review_html'])

    def test_fresh_study_retains_its_decision_brief_and_equivalent_domain_scope(self):
        study = json.loads((ROOT/'examples/coupon-planning.study.json').read_text())
        with patch('soldershape.study.solve', side_effect=SolverError('SYNTHETIC unavailable engine')):
            payload = self.post('/api/study', study)
        self.assertNotIn('review', payload)
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload['bundle_base64']))) as archive:
            self.assertNotIn('review.json', archive.namelist())
            self.assertNotIn('review.html', archive.namelist())
            self.assertIn('decision.html', archive.namelist())
            self.assertIn('equivalent', archive.read('decision.html').decode().lower())


if __name__ == '__main__':
    unittest.main()
