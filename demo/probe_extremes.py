import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.model import request_from_footprint
from soldershape.solver import solve, SolverError
from soldershape.artifacts import make_bundle

source = (ROOT/'examples'/json.loads((ROOT/'examples/provenance.json').read_text())['filename']).read_text()
results = []
for label, volume, offset, gap in [('5 nL at 200 um', .005, .2, .15), ('7 nL at 200 um', .007, .2, .15), ('Compressed 7 nL at 40 um', .007, .04, .06)]:
    spec, provenance = request_from_footprint(source, 0, {'upper_diameter_mm':.2, 'standoff_mm':gap,
        'volume_mm3':volume, 'offset_mm':offset, 'surface_tension_n_m':.48, 'density_g_cm3':9., 'gravity':True})
    try:
        result = solve(spec)
    except SolverError as error:
        result = {'input':spec.to_dict(), 'input_sha256':spec.sha256, 'status':'failed', 'error':str(error), 'evidence':error.evidence}
    result.update(footprint=provenance, design=label)
    results.append(result)
    print(json.dumps({key:result.get(key) for key in ('design','status','forces','model_warnings','error')}), flush=True)
    (ROOT/'output/extreme-boundary-probe.zip').write_bytes(make_bundle(results, source))
