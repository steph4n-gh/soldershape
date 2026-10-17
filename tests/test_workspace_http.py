import hashlib
import json
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from soldershape.__main__ import Server
from soldershape.board import board_case, default_request, read_board

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server(('127.0.0.1', 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.context = read_board()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, body, token=None):
        return urlopen(Request(self.url+'/api/board/case', data=json.dumps(body).encode(), headers={
            'Content-Type': 'application/json',
            'X-SolderShape-Token': self.server.token if token is None else token}), timeout=10)

    def test_board_draft_opens_exact_case_without_computation(self):
        request = default_request(self.context)
        request['parameters']['offset_mm'] = .231
        request['parameters']['volume_mm3'] = .053
        expected = board_case(request, self.context)[2]
        self.server.computation.acquire()
        try:
            with self.post(request) as response:
                actual = json.load(response)
        finally:
            self.server.computation.release()
        self.assertEqual(actual['case'], expected)
        self.assertEqual(actual['selection']['pad_identifier'], 'J16')
        self.assertEqual(actual['footprint']['pads'][request['pad_index']]['size_mm'], [.4, .4])

    def test_board_handoff_rejects_forged_source_and_missing_token(self):
        request = default_request(self.context)
        for token, board_hash, status in [('', request['board_sha256'], 403),
                                           (self.server.token, '0'*64, 400)]:
            request['board_sha256'] = board_hash
            with self.assertRaises(HTTPError) as error:
                self.post(request, token)
            self.assertEqual(error.exception.code, status)
            error.exception.close()

    def test_fixed_resources_preserve_release_identity(self):
        resources = {
            '/lab/kit.zip': ('output/soldershape-force-lab-r1-noticed.zip', 'application/zip'),
            '/lab/handbook.pdf': ('output/pdf/soldershape-force-lab-handoff.pdf', 'application/pdf'),
            '/lab/rfq.txt': ('force_lab/RFQ.md', 'text/plain'),
            '/lab/procedure.txt': ('force_lab/PROCEDURE.md', 'text/plain'),
            '/lab/bom.csv': ('force_lab/BOM.csv', 'text/csv'),
            '/lab/uncertainties.txt': ('force_lab/uncertainties.md', 'text/plain'),
            '/lab/height-coupon.zip': ('output/soldershape-coupon-r1-noticed.zip', 'application/zip'),
            '/lab/prelab.html': ('prelab/REPORT.html', 'text/html'),
            '/lab/prelab-protocol.json': ('prelab/protocol.json', 'application/json'),
            '/lab/prelab-results.json': ('prelab/evidence/campaign/report.json', 'application/json'),
            '/lab/prelab-measurements.txt': ('prelab/LAB_ADDENDUM.md', 'text/plain'),
        }
        for route, (filename, mime) in resources.items():
            with self.subTest(route=route), urlopen(self.url+route) as response:
                self.assertEqual(response.headers.get_content_type(), mime)
                self.assertEqual(hashlib.sha256(response.read()).digest(), hashlib.sha256((ROOT/filename).read_bytes()).digest())
        with self.assertRaises(HTTPError) as unknown:
            urlopen(self.url+'/lab/../../README.md')
        self.assertEqual(unknown.exception.code, 404)
        unknown.exception.close()

    def test_all_tasks_load_common_shell(self):
        for route in ('/', '/board', '/study', '/demo', '/lab', '/lab/prelab.html'):
            with self.subTest(route=route), urlopen(self.url+route) as response:
                html = response.read()
                self.assertIn(b'href="/ui.css"', html)
                self.assertIn(b'src="/ui.js"', html)


if __name__ == '__main__':
    unittest.main()
