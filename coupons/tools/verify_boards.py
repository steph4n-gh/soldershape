from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1]


def gerber(path):
    source = path.read_text()
    assert '%MOMM*%' in source and '%FSLAX46Y46*%' in source, 'Expected explicit mm, 4.6 Gerber coordinates.'
    apertures = {int(n): (shape, float(size)) for n, shape, size in re.findall(r'%ADD(\d+)([A-Z]),([\d.]+)\*%', source)}
    active = None
    flashes, lines, regions = [], [], []
    x = y = 0
    region = None
    for line in source.splitlines():
        selected = re.fullmatch(r'D(\d+)\*', line)
        if selected:
            active = int(selected[1])
        if line == 'G36*':
            region = []
        if line == 'G37*':
            regions.append(region)
            region = None
        point = re.fullmatch(r'(?:X(-?\d+))?(?:Y(-?\d+))?D0([123])\*', line)
        if point and (point[1] is not None or point[2] is not None):
            nx = int(point[1]) if point[1] is not None else x
            ny = int(point[2]) if point[2] is not None else y
            position = (round(nx/1e6, 6), round(-ny/1e6, 6))
            if region is not None:
                region.append(position)
            elif point[3] == '3':
                flashes.append((*position, *apertures[active]))
            elif point[3] == '1':
                lines.append(((x/1e6, -y/1e6), position))
            x, y = nx, ny
    return flashes, lines, regions


def expected_grid(x, y, diameter):
    return {(round(x+dx, 6), round(y+dy, 6), 'C', diameter)
            for dx in (-1, -.5, 0, .5, 1) for dy in (-.75, -.25, .25, .75)}


def main():
    spec = json.loads((HERE/'experiment.json').read_text())
    assert spec['array'] == {'columns':5,'rows':4,'pitch_mm':.5,'joint_count':20}
    actual = json.loads((HERE/'evidence/native-geometry.json').read_text())
    assert actual['spec_sha256'] == hashlib.sha256((HERE/'experiment.json').read_bytes()).hexdigest()
    report = {'status':'files_geometry_verified', 'fabrication_released':False, 'checks':[], 'files':{}}
    for name in ('carrier', 'cap'):
        drc = json.loads((HERE/'evidence'/f'{name}-drc.json').read_text())
        assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'], f'{name}: DRC issues remain.'
        board = actual['boards'][name]
        assert board['track_count'] == 0
        copper_layer = 'F_Cu.gtl' if name == 'carrier' else 'B_Cu.gbl'
        flashes, traces, _ = gerber(HERE/'fabrication'/name/f'{name}-{copper_layer}')
        expected = set()
        if name == 'carrier':
            for site in spec['carrier']['sites']:
                expected |= expected_grid(site['x_mm'], site['y_mm'], spec['arms'][site['arm']]['pad_diameter_mm'])
            expected |= {(4,4,'C',1),(36,4,'C',1),(4,36,'C',1)}
            assert Counter(f[3] for f in flashes) == { .22:40, .27:40, 1.0:3 }
        else:
            expected = expected_grid(1.5, 1.5, .28)
            assert Counter(f[3] for f in flashes) == { .28:20 }
        assert len(flashes) == len(expected) and set(flashes) == expected, f'{name}: copper geometry mismatch.'
        assert not traces, f'{name}: unexpected copper tracks.'
        other_layer = 'B_Cu.gbl' if name == 'carrier' else 'F_Cu.gtl'
        other = gerber(HERE/'fabrication'/name/f'{name}-{other_layer}')
        assert not any(other), f'{name}: unexpected opposite-side copper.'
        mask_layer = 'F_Mask.gts' if name == 'carrier' else 'B_Mask.gbs'
        _, _, regions = gerber(HERE/'fabrication'/name/f'{name}-{mask_layer}')
        windows = []
        for region in regions:
            xs, ys = zip(*region)
            width, height = round(max(xs)-min(xs),6), round(max(ys)-min(ys),6)
            if (width,height) == tuple(spec['fabrication']['mask_window_mm']):
                windows.append(((min(xs)+max(xs))/2, (min(ys)+max(ys))/2))
        expected_centers = {(s['x_mm'],s['y_mm']) for s in spec['carrier']['sites']} if name=='carrier' else {(1.5,1.5)}
        assert len(windows)==len(expected_centers) and set(windows)==expected_centers, f'{name}: mask windows differ.'
        edges = gerber(HERE/'fabrication'/name/f'{name}-Edge_Cuts.gm1')[1]
        width = spec[name]['width_mm']
        height = spec[name]['height_mm']
        expected_edges = {frozenset((a,b)) for a,b in [((0,0),(width,0)),((width,0),(width,height)),((width,height),(0,height)),((0,height),(0,0))]}
        assert len(edges)==4 and {frozenset(edge) for edge in edges}==expected_edges, f'{name}: board outline mismatch.'
        assert board['thickness_mm'] == spec[name]['thickness_mm']
        report['checks'].append({'board':name,'copper_flashes':len(flashes),'mask_array_windows':len(windows),'dimensions_mm':[width,height],'drc_violations':0})
    drill = (HERE/'fabrication/carrier/carrier.drl').read_text()
    assert 'NonPlated,NPTH' in drill and 'T1C3.200' in drill
    assert set(re.findall(r'X([\d.]+)Y(-?[\d.]+)',drill))=={('4.0','-20.0'),('36.0','-20.0')}
    cap_drill = (HERE/'fabrication/cap/cap.drl').read_text()
    assert not re.findall(r'X[\d.]+Y-?[\d.]+',cap_drill), 'Cap must have no holes.'
    with (HERE/'allocation.csv').open() as source:
        allocation = list(csv.DictReader(source))
    assert len(allocation)==48 and len({row['cap_id'] for row in allocation})==48
    scored = [row for row in allocation if row['role']=='confirmatory']
    assert len(scored)==24 and Counter(row['arm'] for row in scored)=={'C220':12,'C270':12}
    assert Counter(row['run_id'] for row in scored)=={'R1':8,'R2':8,'R3':8}
    for run in ('R1', 'R2', 'R3'):
        assert Counter(row['carrier_rotation_deg'] for row in scored if row['run_id']==run)=={'0':4,'90':4}
    assert len({row['pair_id'] for row in scored})==12
    for pair in {row['pair_id'] for row in scored}:
        assert {row['arm'] for row in scored if row['pair_id']==pair}=={'C220','C270'}
    for path in sorted((HERE/'hardware').glob('*'))+sorted((HERE/'fabrication').rglob('*')):
        if path.is_file() and path.suffix != '.kicad_prl':
            report['files'][str(path.relative_to(HERE))]=hashlib.sha256(path.read_bytes()).hexdigest()
    report['geometry_sha256']=hashlib.sha256(json.dumps(report['checks'],sort_keys=True).encode()).hexdigest()
    (HERE/'evidence/fabrication-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='files'},indent=2))


if __name__ == '__main__':
    main()
