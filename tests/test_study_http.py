import base64
import io
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import zipfile

from soldershape.__main__ import Server
from soldershape.solver import SolverError

ROOT = Path(__file__).resolve().parents[1]


class StudyHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(('127.0.0.1', 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, path, body, token=None):
        return urlopen(Request(self.url+path, data=json.dumps(body).encode(), headers={
            'Content-Type':'application/json', 'X-SolderShape-Token':self.server.token if token is None else token}), timeout=5)

    def test_open_preserves_both_actual_footprint_revisions(self):
        study = json.loads((ROOT/'examples/coupon-planning.study.json').read_text())
        with self.post('/api/study/case', study) as response:
            accepted = json.load(response)['study']
        self.assertNotEqual(accepted['reference']['footprint_text'], accepted['candidate']['footprint_text'])
        self.assertEqual(accepted['requirement']['pad_face_gap_um'], 185)
        with urlopen(self.url+'/study') as response:
            self.assertIn(b'SolderShape | Pad comparison', response.read())

    def test_native_failure_is_retained_in_real_export(self):
        study = json.loads((ROOT/'examples/coupon-planning.study.json').read_text())
        with patch('soldershape.study.solve', side_effect=SolverError('SYNTHETIC unavailable engine')):
            with self.post('/api/study', study) as response:
                data = json.load(response)
        self.assertEqual(data['report']['decision']['status'], 'numerical_failure')
        self.assertEqual(data['report']['physical_qualification'], 'unqualified')
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(data['bundle_base64']))) as archive:
            self.assertIn('study.json', archive.namelist())
            self.assertIn('decision.html', archive.namelist())
            self.assertEqual(json.loads(archive.read('manifest.json'))['case_count'], 4)
            self.assertIn('SYNTHETIC unavailable engine', archive.read('results.csv').decode())

    def test_study_requires_token_and_declared_evidence(self):
        study = json.loads((ROOT/'examples/coupon-planning.study.json').read_text())
        with self.assertRaises(HTTPError) as missing:
            self.post('/api/study/case', study, token='')
        self.assertEqual(missing.exception.code, 403)
        missing.exception.close()
        study['reference']['boundary_evidence'] = ''
        with self.assertRaises(HTTPError) as invalid:
            self.post('/api/study/case', study)
        self.assertEqual(invalid.exception.code, 400)
        invalid.exception.close()


if __name__ == '__main__':
    unittest.main()
