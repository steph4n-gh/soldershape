"""Verify the actual browser downloads retained for the cohesion acceptance run."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.artifacts import read_bundle
from soldershape.board import verify_board
from soldershape.study import read_study


def check():
    evidence = ROOT / 'cohesion/evidence'
    comparison = read_bundle(evidence / 'board-to-joint-comparison.zip')
    assert len(comparison) == 2
    assert [spec.volume_mm3 for spec, _ in comparison] == [.04, .052]
    assert all(spec.offset_mm == .231 and spec.lower_diameter_mm == .4 for spec, _ in comparison)
    assert all(row['status'] == 'refinement_checked' for _, row in comparison)
    sweep = read_bundle(evidence / 'offset-sweep.zip')
    assert [spec.offset_mm for spec, _ in sweep] == [-.02, -.01, 0, .01, .02]
    assert all(row['status'] == 'refinement_checked' for _, row in sweep)
    cases = read_bundle(evidence / 'custom-study.zip')
    with zipfile.ZipFile(evidence / 'custom-study.zip') as archive:
        study = json.loads(archive.read('study.json'))
        report = json.loads(archive.read('study-report.json'))
        assert read_study(study) == study
        assert json.loads((evidence / 'custom-study.json').read_text()) == study
        assert study['requirement']['pad_face_gap_um'] == 186
        assert study['volume_fraction'] == .04 and study['two_pad']['lower_metal_um'] == 32
        assert len(cases) == 4 and all(row['status'] == 'refinement_checked' for _, row in cases)
        assert report['physical_qualification'] == 'unqualified'
        for arm in ('reference', 'candidate'):
            assert archive.read(arm + '.kicad_mod').decode() == study[arm]['footprint_text']
        for name, digest in report['calculation_code_sha256'].items():
            assert hashlib.sha256(archive.read('calculation-source/' + name)).hexdigest() == digest
    board = verify_board(evidence / 'current-board.zip')
    assert board['passed']
    for row in json.loads((ROOT / 'cohesion/integrity.json').read_text()):
        content = (ROOT / row['path']).read_bytes()
        assert len(content) == row['bytes'] and hashlib.sha256(content).hexdigest() == row['sha256']
    return {'passed': True, 'generic_native_cases': len(comparison) + len(sweep) + len(cases),
            'board_binding': True, 'prior_evidence_and_numerical_sources_unchanged': True,
            'physical_qualification': 'unqualified'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
