#!/usr/bin/env python3
"""Build the quote-stage fixture and thin-film boundary artwork."""

import hashlib
import html
import json
from pathlib import Path
import platform
import sys

import cadquery as cq
import ezdxf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "force_lab/cad"))
from model import SPEC_PATH, build, read_spec


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(shape):
    bb = shape.BoundingBox()
    return [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]


def drawing(path, title, shape, notes, projection=(1, -1, 1)):
    image = cq.exporters.getSVG(shape, {"width": 760, "height": 440, "marginLeft": 30, "marginTop": 30, "showAxes": False, "showHidden": False, "projectionDir": projection})
    image = image[image.index("<svg"):]
    line_y = 510
    rows = []
    for note in notes:
        rows.append(f'<text x="36" y="{line_y}" font-size="15">{html.escape(str(note))}</text>')
        line_y += 23
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="840" height="{max(760, line_y + 65)}" viewBox="0 0 840 {max(760, line_y + 65)}"><rect width="100%" height="100%" fill="white"/><g font-family="Arial,sans-serif" fill="#12283c"><text x="36" y="35" font-size="23">{html.escape(title)}</text><text x="36" y="61" font-size="13">SolderShape Q1 | millimeters | QUOTE STAGE | vendor interfaces UNRELEASED</text><g transform="translate(36 70)">{image}</g>{"".join(rows)}<text x="36" y="{line_y + 20}" font-size="12">Source model.py + spec.json. Linear dimensions govern. Do not scale this drawing.</text></g></svg>')


def micro_drawing(path, spec, offset):
    j, c = spec["joint"], spec["upper_cap"]
    scale = 190
    x = lambda a: 440 + a * scale
    z = lambda a: 250 - a * scale
    left, right = offset + c["pad_free_edge_setback"] - c["length"], offset + c["pad_free_edge_setback"]
    top = j["upper_wet_face_z"] + j["thin_film_thickness"] + c["thickness"]
    h = html.escape
    path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="#215e7f"/></marker></defs>
<rect width="900" height="600" fill="white"/><g font-family="Arial,sans-serif" fill="#12283c"><text x="32" y="35" font-size="23">Q1 joint section | offset {offset:.3f} mm</text><text x="32" y="62" font-size="14">Geometry target only. Wetting, bonds and full-rim visibility are unqualified.</text>
<rect x="{x(left)}" y="{z(top)}" width="{c['length']*scale}" height="{c['thickness']*scale}" fill="#dceff5" stroke="#215e7f"/>
<rect x="{x(-2)}" y="{z(-j['thin_film_thickness'])}" width="{4*scale}" height="{.5*scale}" fill="#dceff5" stroke="#215e7f"/>
<path d="M{x(-.1)} {z(0)}H{x(.1)}M{x(offset-.1)} {z(.15)}H{x(offset+.1)}" stroke="#ad7418" stroke-width="4"/>
<circle cx="{x(offset-.1)}" cy="{z(.15)}" r="3" fill="white" stroke="#ad7418"/><circle cx="{x(offset+.1)}" cy="{z(.15)}" r="3" fill="white" stroke="#ad7418"/>
<text x="{x(offset-.1)-8}" y="{z(.15)-12}" font-size="12" text-anchor="end">upper -X rim</text><text x="{x(offset+.1)+8}" y="{z(.15)-12}" font-size="12">upper +X rim</text>
<line x1="{x(.55)}" y1="{z(0)}" x2="{x(.55)}" y2="{z(.15)}" stroke="#215e7f" marker-start="url(#a)" marker-end="url(#a)"/><text x="{x(.62)}" y="{z(.075)+5}" font-size="16">0.150 wet face gap</text>
<line x1="{x(0)}" y1="{z(-.65)}" x2="{x(offset)}" y2="{z(-.65)}" stroke="#215e7f" marker-start="url(#a)" marker-end="url(#a)"/><text x="{x(-.5)}" y="{z(-.8)}" font-size="16">offset {offset:.3f} in +X; gravity in -Z</text>
<text x="32" y="440" font-size="16">Both circular wettable islands diameter {j['diameter']:.3f}. Pad thickness envelope {j['thin_film_thickness']*1000:.1f} micrometers.</text>
<text x="32" y="467" font-size="16">Upper cap 2.000 x 2.000 x 0.300. Free +X edge setback {c['pad_free_edge_setback']:.3f}.</text>
<text x="32" y="494" font-size="16">Lower chip 10.000 x 10.000 x 0.500. Film thickness is separately measured.</text>
<text x="32" y="521" font-size="16">Nonwetting surround must cover exposed face outside island. No tall post or wet sidewall.</text>
<text x="32" y="550" font-size="14">Drawing is schematic in section. STEP and explicit dimensions govern. Do not scale.</text></g></svg>''')


def artwork(path, spec, upper):
    doc = ezdxf.new("R2010")
    doc.units = 4
    for name, color in (("METAL_ISLAND", 2), ("NONWET_BOUNDARY", 4), ("SUBSTRATE_OUTLINE", 7), ("DATUM_ONLY", 6)):
        doc.layers.new(name, dxfattribs={"color": color})
    model = doc.modelspace()
    r = spec["joint"]["diameter"] / 2
    model.add_circle((0, 0), r, dxfattribs={"layer": "METAL_ISLAND"})
    model.add_circle((0, 0), r, dxfattribs={"layer": "NONWET_BOUNDARY"})
    if upper:
        cap = spec["upper_cap"]
        xmin, xmax, ymin, ymax = cap["pad_free_edge_setback"] - cap["length"], cap["pad_free_edge_setback"], -cap["width"] / 2, cap["width"] / 2
    else:
        chip = spec["lower_chip"]
        xmin, xmax, ymin, ymax = -chip["length"] / 2, chip["length"] / 2, -chip["width"] / 2, chip["width"] / 2
    model.add_lwpolyline([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)], close=True, dxfattribs={"layer": "SUBSTRATE_OUTLINE"})
    model.add_line((-.04, 0), (.04, 0), dxfattribs={"layer": "DATUM_ONLY"})
    model.add_line((0, -.04), (0, .04), dxfattribs={"layer": "DATUM_ONLY"})
    doc.saveas(path)


def main():
    spec = read_spec()
    out = ROOT / "force_lab/hardware"
    (out / "parts").mkdir(parents=True, exist_ok=True)
    (out / "drawings").mkdir(exist_ok=True)
    records = {}
    for axis in ("x", "z"):
        for offset in spec["joint"]["offsets"]:
            parts, datums = build(spec, offset, axis)
            tag = f"{axis}-{round(offset*1000):03d}um"
            compound = cq.Compound.makeCompound([p["shape"] for p in parts.values()])
            cq.exporters.export(compound, str(out / f"fixture-{tag}.step"))
            records[tag] = {"datums": datums, "parts": {name: {"bbox_mm": bbox(p["shape"]), "volume_mm3": p["shape"].Volume(), "solid_count": len(p["shape"].Solids()), "material": p["material"], "moving": p["moving"], "role": p["role"]} for name, p in parts.items()}}
            if offset == spec["joint"]["offsets"][0]:
                for name, p in parts.items():
                    part_name = f"{name}-{axis}" if name == "sensor_adapter_blank" else name
                    if axis == "x" or name == "sensor_adapter_blank":
                        cq.exporters.export(p["shape"], str(out / "parts" / f"{part_name}.step"))
                drawing(out / "drawings" / f"assembly-{axis}.svg", f"Fixture Q1 | {axis.upper()} sensitive-axis configuration", compound, ["Joint stays horizontal in both index configurations. Vendor sensor head is intentionally absent.", "Upper load path: island, cap, conformal bond, silica stalk, cool bond/tab, approved sensor tip.", "Do not add a guide, temperature wire or shield contact to the moving carrier.", "Base 80 x 80 x 8. Internal mounting clearance holes diameter 4.5 on a 60 x 60 square.", "Sensor mating, stage, heater, chamber and all bond/process interfaces remain unreleased."])
    parts, _ = build(spec)
    dimension_notes = {
        "base": ["80.000 X x 80.000 Y x 8.000 Z. Datum center X=-20.000, Y=0.", "4 x diameter 4.500 THRU at X=-50,+10 and Y=-30,+30.", "2 x M4 THRU at X=-40, Y=-10,+10. STEP models diameter 3.300 tap drill.", "4 x M3 THRU at X=-20,-13 and Y=-4,+4. STEP models diameter 2.500 tap drill.", "Internal fixture pattern only. Lab stage interface requires separate accepted drawing."],
        "indexed_bracket": ["Wall 10.000 X x 40.000 Y x 60.000 Z. Back X=-56.000. Bottom at base top.", "Foot 20.000 X x 40.000 Y x 6.000 Z from X=-56 to -36.", "Shelf 30.000 X x 40.000 Y x 6.000 Z from X=-46 to -16; top Z=26.700.", "2 x diameter 4.500 THRU foot at X=-40, Y=-10,+10.", "2 x diameter 4.500 THRU wall along X at Y=-10,+10, Z=1.000.", "2 x diameter 4.500 THRU shelf along Z at X=-31, Y=-10,+10.", "Internal holes only. Break sharp edges 0.2 max. General machined tolerance +/-0.05 mm."],
        "thermal_carrier": ["24.000 X x 24.000 Y x 3.000 Z. Center X=Y=0.", "Centered square pocket 10.200 x 10.200, depth 0.200 from top.", "Lower 10.000 x 10.000 chip gives nominal 0.100 clearance on each side.", "Top Z=-0.3005 for illustrative 0.0005 film. Heater contact on bottom is unresolved.", "Alumina thermal carrier is a quote item. Retention and heater integration require lab approval."],
        "pedestal": ["12.000 X x 12.000 Y x 20.000 Z. Center X=Y=0.", "Top meets thermal-carrier underside. Bottom meets base top Z=-23.3005.", "Alumina. Lab approves bond/clamp, heater integration and temperature gradient."],
        "upper_cap": ["Transparent fused silica 2.000 X x 2.000 Y x 0.300 Z.", "Island diameter 0.200 on underside; center 0.350 from free +X edge, centered Y.", "No opaque support or bond over the island. Hot bond extends X=-1.600 to -0.800 relative to pad.", "Thin-film process and complete contact-line observation require lab qualification."],
        "stalk": ["Fused silica circular rod diameter 1.000, length 20.000.", "Rod axis parallel +X. Free end X=pad X-0.800. Center Z=1.0005.", "Bottom is 0.050 above cap top. Supplier-approved conformal bond bridges the gap.", "Room-temperature beam estimate only. Sensor moment and cross-load acceptance required."],
        "lower_chip": ["Transparent fused silica 10.000 X x 10.000 Y x 0.500 Z.", "Centered circular island diameter 0.200 on upper face. Nonwetting surround on remaining face.", "Substrate top Z=-0.0005; actual island wet face Z=0 after measured metal thickness.", "DXF describes boundaries only. It is not a released lithography or deposition process."],
        "cool_tab": ["Fused silica 2.500 X x 1.500 Y x 0.300 Z.", "At the cool rod end. Thin supplier-approved bond touches the rod end face.", "Unresolved sensor-tip attachment. Do not substitute a massive clamp without recalculating loads."],
        "shield_1": ["Polished stainless sheet thickness 0.500, width Y=12.000.", "Upright center X=-18.000; top Z=6.000; foot bottom at base top.", "Foot length 6.000, directed toward -X. Inside bend radius is a lab quote detail.", "Diameter 4.000 noncontact aperture along X, center Y=0, Z=1.0005.", "2 x diameter 3.400 THRU foot at X=-20.000, Y=-4,+4."],
        "shield_2": ["Polished stainless sheet thickness 0.500, width Y=12.000.", "Upright center X=-15.000; top Z=6.000; foot bottom at base top.", "Foot length 6.000, directed toward +X. Inside bend radius is a lab quote detail.", "Diameter 4.000 noncontact aperture along X, center Y=0, Z=1.0005.", "2 x diameter 3.400 THRU foot at X=-13.000, Y=-4,+4."],
    }
    for name, notes in dimension_notes.items():
        drawing(out / "drawings" / f"{name}.svg", f"Q1 | {name.replace('_',' ')}", parts[name]["shape"], notes)
    for axis in ("x", "z"):
        pp, _ = build(spec, axis=axis)
        notes = ["30.000 x 30.000 x 3.000 aluminum adapter blank.", "Two internal diameter 4.500 THRU holes on a 20.000 pitch, centered on the blank.", "X configuration mounts on upright face. Z configuration mounts on shelf top.", "Remaining vendor sensor pattern is UNMACHINED. No supplier compatibility claimed.", "These orthogonal mounting datums do not establish where an actual sensor tip will lie.", "Lab/supplier must accept sensor envelope and reproduce the unchanged hot-joint datum."]
        drawing(out / "drawings" / f"sensor_adapter_blank-{axis}.svg", f"Q1 | sensor adapter blank {axis}", pp["sensor_adapter_blank"]["shape"], notes)
    for offset in spec["joint"]["offsets"]:
        micro_drawing(out / "drawings" / f"joint-{round(offset*1000):03d}um.svg", spec, offset)
    artwork(out / "upper-cap-boundaries.dxf", spec, True)
    artwork(out / "lower-chip-boundaries.dxf", spec, False)
    (out / "geometry.json").write_text(json.dumps({"schema": "soldershape.fixture-geometry.v1", "spec_sha256": digest(SPEC_PATH), "cadquery_version": cq.__version__, "python_version": platform.python_version(), "configurations": records}, indent=2) + "\n")
    paths = [SPEC_PATH, ROOT / "force_lab/cad/model.py", ROOT / "force_lab/cad/requirements.txt", ROOT / "force_lab/cad/requirements-lock.txt", Path(__file__).resolve(), ROOT / "force_lab/tools/verify_cad.py"]
    paths += sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json")
    (out / "manifest.json").write_text(json.dumps({"schema": "soldershape.fixture-files.v1", "files": {str(p.relative_to(ROOT)): digest(p) for p in paths}}, indent=2) + "\n")
    print(json.dumps({"output": str(out), "configurations": list(records), "file_count": len(paths), "status": spec["status"]}, indent=2))


if __name__ == "__main__":
    main()
