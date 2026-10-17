"""Compare anonymous deployed responses with this release's static source."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'website/dist'
ORIGIN = 'https://soldershape.steph4n.dev/'
EDGE_SCRIPT_SHA256 = '6a75d68b52efbad75a56e87a7ed4a35db2a3a1eb32339a68733bba7110a10715'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(path):
    relative = path.relative_to(SITE).as_posix()
    request = Request(ORIGIN + quote(relative), headers={
        'User-Agent': 'SolderShape-publication-check/1.0', 'Accept-Encoding': 'identity'})
    with urlopen(request, timeout=30) as response:
        actual = response.read()
        assert response.status == 200, relative
    canonical = path.read_bytes()
    normalized = actual
    edge_scripts = 0
    if path.suffix == '.html' and actual != canonical:
        for match in re.finditer(rb'<script>.*?</script>', actual, flags=re.DOTALL):
            script = match.group()
            if b'/cdn-cgi/challenge-platform/scripts/jsd/main.js' not in script:
                continue
            shape = re.sub(rb"r:'[0-9a-f]+'", b"r:'RAY_ID'", script)
            shape = re.sub(rb"t:'[A-Za-z0-9+/=]+'", b"t:'TIMESTAMP'", shape)
            assert sha(shape) == EDGE_SCRIPT_SHA256, relative
            normalized = normalized.replace(script, b'', 1)
            edge_scripts += 1
        assert edge_scripts <= 1, relative
    assert normalized == canonical, relative
    return {'file': relative, 'status': 200, 'bytes': len(actual), 'response_sha256': sha(actual),
            'canonical_sha256': sha(canonical), 'cloudflare_managed_scripts': edge_scripts,
            'canonical_bytes_match': True}


def main():
    paths = sorted(path for path in SITE.rglob('*') if path.is_file())
    with ThreadPoolExecutor(max_workers=6) as pool:
        checks = list(pool.map(verify, paths))
    record = {'passed': True, 'origin': ORIGIN, 'authentication_sent': False,
              'files': len(checks), 'checks': checks,
              'html_normalization': 'Only the pinned Cloudflare managed JS-detection script. Ray ID and timestamp vary.'}
    (ROOT / 'publication/evidence/public-files.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'passed': True, 'files': len(checks), 'authentication_sent': False}))


if __name__ == '__main__':
    main()
