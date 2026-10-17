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
for volume in (.005, .007):
    for offset in (.04, .08, .12):
        spec, provenance = request_from_footprint(source, 0, {'upper_diameter_mm':.2, 'standoff_mm':.15,
            'volume_mm3':volume, 'offset_mm':offset, 'surface_tension_n_m':.48, 'density_g_cm3':9., 'gravity':True})
        try:
            result = solve(spec)
        except SolverError as error:
            result = {'input':spec.to_dict(), 'input_sha256':spec.sha256, 'status':'failed', 'error':str(error), 'evidence':error.evidence}
        result.update(footprint=provenance, design=f'{volume*1000:g} nL at {offset*1000:g} um')
        results.append(result)
        summary = {key:result.get(key) for key in ('design','status','forces','model_warnings','mesh_checks','error')}
        print(json.dumps(summary), flush=True)
        (ROOT/'output/extreme-probe.zip').write_bytes(make_bundle(results, source))
