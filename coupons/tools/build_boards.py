"""Build the two passive coupon boards and lab allocation using pinned KiCad."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'coupons'
IMAGE = 'kicad/kicad@sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec'


def allocation(spec):
    rng = random.Random(spec['random_seed'])
    caps = [f'C{n:03d}' for n in range(1, 49)]
    rng.shuffle(caps)
    rows = []
    groups = [('pilot', f'P{run}', f'P{run:02d}') for run in range(1, 4)]
    groups += [('confirmatory', f'R{(n-1)//2+1}', f'B{n:02d}') for n in range(1, 7)]
    groups += [('profile', 'Q0', 'Q01'), ('spare', '', 'X01'), ('spare', '', 'X02')]
    for index, (role, run, board) in enumerate(groups):
        order = list(range(1, 5))
        rng.shuffle(order)
        for site in spec['carrier']['sites']:
            rows.append({'specimen_id': board+'-'+site['site'], 'role': role, 'run_id': run,
                         'carrier_id': board, 'site_id': site['site'], 'pair_id': f'{board}-P{site["pair"]}',
                         'arm': site['arm'], 'cap_id': caps.pop(), 'sphere_kit_id': 'K'+f'{len(rows)+1:03d}',
                         'carrier_rotation_deg': 90*(index % 2), 'placement_order': order[int(site['site'][1:])-1]})
    with (HERE / 'allocation.csv').open('w', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def generate(spec):
    import pcbnew as pcb

    out = HERE / 'hardware'
    out.mkdir(exist_ok=True)
    vector = lambda x, y: pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y))

    def layers(*ids):
        result = pcb.LSET()
        for layer in ids:
            result.AddLayer(layer)
        return result

    def line(board, start, end, layer=pcb.Edge_Cuts, width=.05):
        item = pcb.PCB_SHAPE(board)
        item.SetShape(pcb.SHAPE_T_SEGMENT)
        item.SetStart(vector(*start))
        item.SetEnd(vector(*end))
        item.SetLayer(layer)
        item.SetWidth(pcb.FromMM(width))
        board.Add(item)

    def rectangle(board, center, size, layer, filled=False):
        x, y = center
        w, h = size
        item = pcb.PCB_SHAPE(board)
        item.SetShape(pcb.SHAPE_T_RECT)
        item.SetStart(vector(x-w/2, y-h/2))
        item.SetEnd(vector(x+w/2, y+h/2))
        item.SetLayer(layer)
        item.SetWidth(pcb.FromMM(0 if filled else .02))
        item.SetFilled(filled)
        board.Add(item)

    def text(board, value, x, y, size=1, layer=pcb.F_SilkS):
        item = pcb.PCB_TEXT(board)
        item.SetText(value)
        item.SetPosition(vector(x, y))
        item.SetTextSize(vector(size, size))
        item.SetTextThickness(pcb.FromMM(size/6))
        item.SetLayer(layer)
        board.Add(item)

    def array(board, x, y, diameter, layer, reference):
        footprint = pcb.FOOTPRINT(board)
        footprint.SetPosition(vector(x, y))
        footprint.SetReference(reference)
        footprint.SetValue(f'{diameter:.3f}mm 5x4 0.5mm pitch')
        footprint.Reference().SetVisible(False)
        footprint.Value().SetVisible(False)
        footprint.SetLayer(layer)
        footprint.SetAttributes(pcb.FP_SMD)
        for row in range(spec['array']['rows']):
            for col in range(spec['array']['columns']):
                pad = pcb.PAD(footprint)
                pad.SetNumber(f'{chr(65+row)}{col+1}')
                pad.SetShape(pcb.PAD_SHAPE_CIRCLE)
                pad.SetAttribute(pcb.PAD_ATTRIB_SMD)
                pad.SetSize(vector(diameter, diameter))
                pad.SetLayerSet(layers(layer))
                pad.SetPosition(vector(x+(col-2)*.5, y+(row-1.5)*.5))
                footprint.Add(pad)
        board.Add(footprint)
        mask = pcb.F_Mask if layer == pcb.F_Cu else pcb.B_Mask
        rectangle(board, (x, y), spec['fabrication']['mask_window_mm'], mask, True)
        rectangle(board, (x, y), [3, 3], pcb.F_Fab)
        return footprint

    def board_base(width, height, thickness):
        board = pcb.BOARD()
        board.GetDesignSettings().SetBoardThickness(pcb.FromMM(thickness))
        board.GetDesignSettings().m_CopperEdgeClearance = pcb.FromMM(.2)
        corners = [(0, 0), (width, 0), (width, height), (0, height)]
        for a, b in zip(corners, corners[1:]+corners[:1]):
            line(board, a, b)
        return board

    carrier = board_base(spec['carrier']['width_mm'], spec['carrier']['height_mm'], spec['carrier']['thickness_mm'])
    for site in spec['carrier']['sites']:
        x, y = site['x_mm'], site['y_mm']
        array(carrier, x, y, spec['arms'][site['arm']]['pad_diameter_mm'], pcb.F_Cu, site['site'])
        text(carrier, site['site'], x, y-3)
        text(carrier, 'A1', x-2.6, y-.75, 1)
    for fid_index, (x, y) in enumerate([(4, 4), (36, 4), (4, 36)], 1):
        fid = pcb.FOOTPRINT(carrier)
        fid.SetPosition(vector(x, y))
        fid.SetReference(f'FID{fid_index}')
        fid.Reference().SetVisible(False)
        fid.Value().SetVisible(False)
        pad = pcb.PAD(fid)
        pad.SetSize(vector(1, 1))
        pad.SetShape(pcb.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcb.PAD_ATTRIB_SMD)
        pad.SetLayerSet(layers(pcb.F_Cu))
        pad.SetPosition(vector(x, y))
        fid.Add(pad)
        carrier.Add(fid)
        rectangle(carrier, (x, y), [2, 2], pcb.F_Mask, True)
    for x, y in [(4, 20), (36, 20)]:
        hole = pcb.FOOTPRINT(carrier)
        hole.SetPosition(vector(x, y))
        hole.SetReference(f'H{int(x)}')
        hole.Reference().SetVisible(False)
        hole.Value().SetVisible(False)
        pad = pcb.PAD(hole)
        pad.SetAttribute(pcb.PAD_ATTRIB_NPTH)
        pad.SetShape(pcb.PAD_SHAPE_CIRCLE)
        pad.SetSize(vector(3.2, 3.2))
        pad.SetDrillSize(vector(3.2, 3.2))
        pad.SetPosition(vector(x, y))
        pad.SetLayerSet(layers(pcb.F_Cu, pcb.B_Cu, pcb.F_Mask, pcb.B_Mask))
        hole.Add(pad)
        carrier.Add(hole)
    text(carrier, spec['experiment_id'], 20, 3, 1)
    text(carrier, 'BOARD ID: ______', 20, 37, 1)
    text(carrier, '40 x 40 mm / geometry coupon / no circuit', 20, 40, .8, pcb.Dwgs_User)
    pcb.SaveBoard(str(out / 'carrier.kicad_pcb'), carrier)

    cap = board_base(3, 3, spec['cap']['thickness_mm'])
    array(cap, 1.5, 1.5, spec['cap']['pad_diameter_mm'], pcb.B_Cu, 'CAP')
    text(cap, 'CAP', 1.5, 1.5, 1)
    line(cap, (.25, .25), (.7, .25), pcb.F_SilkS, .15)
    line(cap, (.25, .25), (.25, .7), pcb.F_SilkS, .15)
    pcb.SaveBoard(str(out / 'cap.kicad_pcb'), cap)
    geometry = {'kicad_version': pcb.GetBuildVersion(), 'image': IMAGE,
                'spec_sha256': hashlib.sha256((HERE / 'experiment.json').read_bytes()).hexdigest(), 'boards': {}}
    for name, board in [('carrier', carrier), ('cap', cap)]:
        board = pcb.LoadBoard(str(out / f'{name}.kicad_pcb'))
        pads = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                pads.append({'reference': fp.GetReference(), 'pad': pad.GetNumber(), 'attribute': int(pad.GetAttribute()),
                             'x_mm': pcb.ToMM(pad.GetPosition().x), 'y_mm': pcb.ToMM(pad.GetPosition().y),
                             'diameter_mm': pcb.ToMM(pad.GetSize().x), 'layer': int(pad.GetLayer())})
        geometry['boards'][name] = {'pads': pads, 'thickness_mm': pcb.ToMM(board.GetDesignSettings().GetBoardThickness()),
                                    'track_count': len(board.GetTracks()), 'footprint_count':len(board.GetFootprints())}
        exports = HERE / 'fabrication' / name
        exports.mkdir(parents=True, exist_ok=True)
        source = str(out / f'{name}.kicad_pcb')
        commands = [
            ['pcb','drc','--format','json','--output',str(HERE/'evidence'/f'{name}-drc.json'),source],
            ['pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts','--output',str(exports)+'/',source],
            ['pcb','export','drill','--output',str(exports)+'/',source],
            ['pcb','export','svg','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,Edge.Cuts,F.Fab','--mode-single','--page-size-mode','2','--output',str(out/f'{name}.svg'),source]
        ]
        for command in commands:
            result = subprocess.run(['kicad-cli',*command], capture_output=True, text=True)
            (HERE/'evidence'/f'{name}-{command[1]}-{command[2] if len(command)>2 else ""}.log').write_text(result.stdout+result.stderr)
            if result.returncode:
                raise RuntimeError(f'KiCad failed: {command}: {result.stdout} {result.stderr}')
        svg = out / f'{name}.svg'
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    (HERE/'evidence'/'native-geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    spec = json.loads((HERE/'experiment.json').read_text())
    if args.inside:
        generate(spec)
    else:
        allocation(spec)
        command = ['docker','run','--rm','--platform','linux/amd64','--network','none','-v',f'{ROOT}:/work', '-w','/work',IMAGE,
                   '/usr/bin/python3','coupons/tools/build_boards.py','--inside']
        subprocess.run(command,check=True)
        subprocess.run([sys.executable,str(HERE/'tools/verify_boards.py')],check=True)


if __name__ == '__main__':
    main()
