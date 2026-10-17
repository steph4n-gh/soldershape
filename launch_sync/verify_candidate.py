"""Check every member of an extracted, engine-free source candidate."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    root = args.directory.resolve()
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_bytes())
    assert not (root / '.git').exists() and not (root / '.engine').exists()
    files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    assert files == set(manifest['sha256']) | {'RELEASE-MANIFEST.json'}
    for name, digest in manifest['sha256'].items():
        with (root / name).open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == digest, name
    for name in ('output/soldershape-force-lab-r1-noticed.zip', 'output/soldershape-coupon-r1-noticed.zip'):
        with zipfile.ZipFile(root / name) as archive:
            assert archive.read('LICENSE') == (root / 'LICENSE').read_bytes()
            assert archive.read('THIRD_PARTY.md') == (root / 'THIRD_PARTY.md').read_bytes()
    receipt = {'passed': True, 'source_commit': manifest['source_commit'], 'files': len(manifest['sha256']),
               'git_metadata_present': False, 'engine_present': False,
               'standalone_lab_notices_match': True, 'physical_qualification': 'unqualified'}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
