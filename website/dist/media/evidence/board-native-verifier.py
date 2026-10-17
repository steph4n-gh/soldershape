"""Independently compare extracted geometry with original native board objects."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "board_demo"
IMAGE = "kicad/kicad@sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected, label, tolerance=1e-6):
    if len(actual) != len(expected) or any(abs(a-b) > tolerance for a, b in zip(actual, expected)):
        raise ValueError(f"{label}: {actual} != {expected}")


def module_text(source, uuid):
    legacy = uuid.split("-")[-1][-8:].upper()
    location = re.search(r"\(tstamp (?:" + re.escape(uuid) + "|" + legacy + r")\)", source, re.IGNORECASE)
    if location is None:
        raise ValueError("Original footprint timestamp not found")
    start = max(source.rfind("\n  (module ", 0, location.start()), source.rfind("\n  (footprint ", 0, location.start()))
    if start < 0:
        raise ValueError("Original footprint module not found")
    start += 3
    depth, quoted, escape = 0, False, False
    for index in range(start, len(source)):
        char = source[index]
        if escape:
            escape = False
        elif char == "\\" and quoted:
            escape = True
        elif char == '"':
            quoted = not quoted
        elif not quoted:
            depth += (char == "(") - (char == ")")
            if depth == 0:
                return source[start:index+1]
    raise ValueError("Unterminated original module")


def verify():
    import pcbnew as pcb
    sys.path.insert(0, str(ROOT))
    from soldershape.model import import_footprint

    context = json.loads((HERE / "context.json").read_text())
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, identity in manifest["files"].items():
        if name == "native-verification.json":
            continue
        path = HERE / name
        if path.stat().st_size != identity["bytes"] or sha(path) != identity["sha256"]:
            raise ValueError(f"Manifest changed: {name}")
    if context["source"]["board_sha256"] != sha(HERE / "source/ulx3s.kicad_pcb"):
        raise ValueError("Context source identity differs")
    if context["source"]["license_sha256"] != sha(HERE / "source/LICENSE.md"):
        raise ValueError("Context license identity differs")
    if context["extraction"]["extractor_sha256"] != sha(HERE / "tools/extract.py"):
        raise ValueError("Extractor changed since generated context")
    source_bytes = (HERE / "source/ulx3s.kicad_pcb").read_bytes()
    with tempfile.TemporaryDirectory(prefix="soldershape-original-") as temporary:
        source = Path(temporary) / "ulx3s.kicad_pcb"
        source.write_bytes(source_bytes)
        board = pcb.LoadBoard(str(source))
        fresh_svg = Path(temporary) / "board.svg"
        subprocess.run(["kicad-cli", "pcb", "export", "svg", "--layers", "F.Cu,F.Silkscreen,Edge.Cuts", "--mode-single", "--page-size-mode", "2", "--output", str(fresh_svg), str(source)], capture_output=True, text=True, check=True)
        rendered = re.sub(r"<title>.*?</title>", "<title>ULX3S original front copper, silkscreen, and outline</title>", fresh_svg.read_text(), count=1)
        rendered = "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
        if rendered.encode() != (HERE / context["svg"]["file"]).read_bytes():
            (ROOT / "output/board-native-svg-difference.svg").write_text(rendered)
            raise ValueError("Full original native SVG reexport differs; retained output/board-native-svg-difference.svg")
        originals = {item.m_Uuid.AsString(): item for item in board.GetFootprints()}
        edge_points = [point for item in board.GetDrawings() if item.GetLayer() == pcb.Edge_Cuts for point in (item.GetStart(), item.GetEnd())]
        left, top = min(point.x for point in edge_points), min(point.y for point in edge_points)
        right, bottom = max(point.x for point in edge_points), max(point.y for point in edge_points)
        close(context["bounds_mm"], [pcb.ToMM(value) for value in (left, top, right-left, bottom-top)], "Original board bounds")
        close(context["svg"]["bounds_mm"], context["bounds_mm"], "SVG coordinate origin")
        shapes = {pcb.PAD_SHAPE_CIRCLE: "circle", pcb.PAD_SHAPE_RECT: "rect", pcb.PAD_SHAPE_OVAL: "oval", pcb.PAD_SHAPE_TRAPEZOID: "trapezoid", pcb.PAD_SHAPE_ROUNDRECT: "roundrect", pcb.PAD_SHAPE_CHAMFERED_RECT: "chamfered_rect", pcb.PAD_SHAPE_CUSTOM: "custom"}
        if len(originals) != len(context["components"]):
            raise ValueError("Component count differs")
        total, supported, rotated, backside = 0, 0, 0, 0
        maxima = {"board_position_mm": 0.0, "local_position_mm": 0.0, "transformed_position_mm": 0.0}
        examples = []
        for component in context["components"]:
            native = originals.pop(component["uuid"])
            if component["reference"] != native.GetReference() or component["value"] != native.GetValue():
                raise ValueError("Component metadata differs")
            origin = [pcb.ToMM(native.GetPosition().x), pcb.ToMM(native.GetPosition().y)]
            close(component["board_position_mm"], origin, "Component position")
            close([component["rotation_deg"]], [native.GetOrientationDegrees()], "Component angle")
            if component["side"] != ("back" if native.IsFlipped() else "front"):
                raise ValueError("Component side differs")
            box = native.GetBoundingBox(False, False)
            close(component["bounds_mm"], [pcb.ToMM(value) for value in (box.GetX(), box.GetY(), box.GetWidth(), box.GetHeight())], "Original component bounds")
            theta = math.radians(native.GetOrientationDegrees())
            cos, sin = math.cos(theta), math.sin(theta)
            close(component["local_x_board"], [cos, -sin], "Local +X vector", 1e-10)
            footprint = HERE / component["footprint_file"]
            if sha(footprint) != component["footprint_sha256"]:
                raise ValueError("Footprint identity differs")
            native_pads = list(native.Pads())
            parsed = import_footprint(footprint.read_text()) if native_pads else {"pads": []}
            if len(native_pads) != len(component["pads"]) or len(parsed["pads"]) != len(native_pads):
                raise ValueError("Pad count differs")
            remaining = list(native_pads)
            for pad, imported in zip(component["pads"], parsed["pads"]):
                if pad["index"] != imported["index"] or pad["identifier"] != imported["identifier"]:
                    raise ValueError("Importer pad order differs")
                candidates = [item for item in remaining if item.GetNumber() == pad["identifier"] and
                              abs(pcb.ToMM(item.GetFPRelativePosition().x)-imported["x_mm"]) < 1e-8 and
                              abs(pcb.ToMM(item.GetFPRelativePosition().y)*(-1 if native.IsFlipped() else 1)-imported["y_mm"]) < 1e-8 and
                              abs(pcb.ToMM(item.GetSize().x)-imported["size_mm"][0]) < 1e-8 and
                              abs(pcb.ToMM(item.GetSize().y)-imported["size_mm"][1]) < 1e-8]
                if len(candidates) != 1:
                    raise ValueError(f"Native pad correspondence is ambiguous: {component['reference']} {imported} {len(candidates)}")
                actual = candidates[0]
                remaining.remove(actual)
                board_xy = [pcb.ToMM(actual.GetPosition().x), pcb.ToMM(actual.GetPosition().y)]
                local_xy = [pcb.ToMM(actual.GetFPRelativePosition().x), pcb.ToMM(actual.GetFPRelativePosition().y)*(-1 if native.IsFlipped() else 1)]
                close(pad["board_xy_mm"], board_xy, "Native pad board position")
                close(pad["local_xy_mm"], local_xy, "Native pad local position")
                close([imported["x_mm"], imported["y_mm"]], local_xy, "Standalone pad position")
                close(pad["size_mm"], [pcb.ToMM(actual.GetSize().x), pcb.ToMM(actual.GetSize().y)], "Native copper size")
                close(imported["size_mm"], pad["size_mm"], "Imported copper size")
                native_y = local_xy[1]*(-1 if native.IsFlipped() else 1)
                transformed = [origin[0] + cos*local_xy[0] + sin*native_y, origin[1] - sin*local_xy[0] + cos*native_y]
                close(transformed, board_xy, "Rotated pad transform", 2e-6)
                for key, a, b in [("board_position_mm", pad["board_xy_mm"], board_xy), ("local_position_mm", pad["local_xy_mm"], local_xy), ("transformed_position_mm", transformed, board_xy)]:
                    maxima[key] = max(maxima[key], *(abs(x-y) for x,y in zip(a,b)))
                if pad["net"] != actual.GetNetname() or pad["shape"] != imported["shape"] or pad["shape"] != shapes[actual.GetShape()] or pad["native_attribute"] != int(actual.GetAttribute()):
                    raise ValueError("Native pad metadata differs")
                expected_supported = imported["supported"] and not native.IsFlipped()
                if pad["supported"] != expected_supported or (pad["unsupported_reason"] is None) != expected_supported:
                    raise ValueError("Pad support status differs")
                total += 1
                supported += pad["supported"]
                rotated += bool(abs(native.GetOrientationDegrees()) > 1e-8)
                backside += native.IsFlipped()
            if component["reference"] in ("U1", "U2", "J1"):
                identifier = "J16" if component["reference"] == "U1" else "1"
                pad = next(item for item in component["pads"] if item["identifier"] == identifier)
                raw_module = module_text(source_bytes.decode(), component["uuid"])
                raw = import_footprint(raw_module)
                raw_pad = next(item for item in raw["pads"] if item["identifier"] == identifier)
                close(pad["local_xy_mm"], [raw_pad["x_mm"], raw_pad["y_mm"]], "Original pad text position")
                close(pad["size_mm"], raw_pad["size_mm"], "Original pad text copper size")
                declaration = re.search(r'\(pad (?:"?' + re.escape(identifier) + r'"?)\s+[^\n]+', raw_module)
                examples.append({"reference": component["reference"], "uuid": component["uuid"], "rotation_deg": component["rotation_deg"],
                                 "pad": pad, "original_declaration": declaration.group(0) if declaration else "not found"})
        xml = ET.fromstring((HERE / context["svg"]["file"]).read_bytes())
        viewbox = [float(value) for value in xml.attrib["viewBox"].split()]
        close(viewbox, [0,0,*context["bounds_mm"][2:]], "SVG dimensions")
        circles = {(round(float(item.attrib["cx"]), 4), round(float(item.attrib["cy"]), 4), round(float(item.attrib["r"]), 4))
                   for item in xml.iter() if item.tag.endswith("}circle")}
        u1 = next(item for item in context["components"] if item["reference"] == "U1")
        matched = 0
        for pad in u1["pads"]:
            if not pad["supported"]:
                continue
            key = (round(pad["board_xy_mm"][0]-context["svg"]["bounds_mm"][0],4),
                   round(pad["board_xy_mm"][1]-context["svg"]["bounds_mm"][1],4), round(pad["size_mm"][0]/2,4))
            if key not in circles:
                raise ValueError(f"Source pad missing from native SVG at expected coordinate: {pad['identifier']}")
            matched += 1
        logos = [{"reference": item["reference"], "uuid": item["uuid"], "side": item["side"], "board_position_mm": item["board_position_mm"], "bounds_mm": item["bounds_mm"]}
                 for item in context["components"] if item["reference"].upper() in ("EMARD", "RADIONA", "FER")]
        expected_counts = {"components": len(context["components"]), "pads": total, "track_objects": len(board.GetTracks()), "supported_pads": supported}
        if context["counts"] != expected_counts:
            raise ValueError("Context counts differ")
        receipt = {"schema": "soldershape.board-native-verification.v1", "status": "passed", "kicad_version": pcb.GetBuildVersion(),
                   "verifier_sha256": sha(Path(__file__)), "context_sha256": sha(HERE / "context.json"), "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                   "svg_sha256": sha(HERE / context["svg"]["file"]), "counts": expected_counts,
                   "verified_rotated_pads": rotated, "verified_back_side_pads": backside, "maximum_error": maxima,
                   "svg_u1_circle_matches": matched, "svg_full_native_reexport_match": True, "svg_mapping": "SVG x=board_x-94.1 and SVG y=board_y-61.42, in millimeters. Matches every supported U1 circle at 0.0001 mm SVG precision.",
                   "examples": examples, "required_logo_context": logos,
                   "scope": "Native coordinate, copper geometry, importer-order and selected source-text agreement. No physical solder validation or board fabrication qualification."}
        (HERE / "native-verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    manifest["files"]["native-verification.json"] = {"sha256": sha(HERE / "native-verification.json"), "bytes": (HERE / "native-verification.json").stat().st_size}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "passed", **expected_counts, "svg_u1_circle_matches": matched, "maximum_error": maxima}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside:
        verify()
    else:
        subprocess.run(["docker", "run", "--rm", "--platform", "linux/amd64", "--network", "none", "-v", f"{ROOT}:/work", "-w", "/work", IMAGE,
                        "/usr/bin/python3", "board_demo/tools/verify_native.py", "--inside"], check=True)


if __name__ == "__main__":
    main()
