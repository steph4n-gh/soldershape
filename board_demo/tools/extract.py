"""Extract identified board context with the pinned native KiCad runtime."""

import argparse
from collections import defaultdict
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def generate():
    import pcbnew as pcb
    sys.path.insert(0, str(ROOT))
    from soldershape.model import import_footprint

    provenance = json.loads((HERE / "source/provenance.json").read_text())
    for name, identity in provenance["files"].items():
        if digest(HERE / "source" / name) != identity["sha256"]:
            raise ValueError(f"Original source changed: {name}")
    source = HERE / "source/ulx3s.kicad_pcb"
    assets = HERE / "assets"
    assets.mkdir(exist_ok=True)
    library = assets / "footprints.pretty"
    library.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="soldershape-board-") as temporary:
        native_source = Path(temporary) / "ulx3s.kicad_pcb"
        native_source.write_bytes(source.read_bytes())
        board = pcb.LoadBoard(str(native_source))
        outlines = [item for item in board.GetDrawings() if item.GetLayer() == pcb.Edge_Cuts]
        if len(outlines) != 4 or any(item.GetShape() != pcb.SHAPE_T_SEGMENT for item in outlines):
            raise ValueError("This extractor expects the pinned rectangular four-segment outline.")
        points = [point for line in outlines for point in (line.GetStart(), line.GetEnd())]
        left, top = min(p.x for p in points), min(p.y for p in points)
        right, bottom = max(p.x for p in points), max(p.y for p in points)
        bounds = [round(pcb.ToMM(v), 9) for v in (left, top, right-left, bottom-top)]
        command = ["kicad-cli", "pcb", "export", "svg", "--layers", "F.Cu,F.Silkscreen,Edge.Cuts",
                   "--mode-single", "--page-size-mode", "2", "--output", str(assets / "board.svg"), str(native_source)]
        subprocess.run(command, capture_output=True, text=True, check=True)
        svg_path = assets / "board.svg"
        svg = svg_path.read_text()
        svg = re.sub(r"<title>.*?</title>", "<title>ULX3S original front copper, silkscreen, and outline</title>", svg, count=1)
        svg_path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n")
        xml = ET.fromstring(svg_path.read_bytes())
        viewbox = [float(v) for v in xml.attrib["viewBox"].split()]
        if any(abs(a-b) > 1e-8 for a, b in zip(viewbox, [0, 0, bounds[2], bounds[3]])):
            raise ValueError("Native SVG dimensions differ from board outline.")
        plugin = pcb.PCB_IO_MGR.FindPlugin(pcb.PCB_IO_MGR.KICAD_SEXP)
        components = []
        shape_names = {pcb.PAD_SHAPE_CIRCLE: "circle", pcb.PAD_SHAPE_RECT: "rect", pcb.PAD_SHAPE_OVAL: "oval",
                       pcb.PAD_SHAPE_TRAPEZOID: "trapezoid", pcb.PAD_SHAPE_ROUNDRECT: "roundrect",
                       pcb.PAD_SHAPE_CHAMFERED_RECT: "chamfered_rect", pcb.PAD_SHAPE_CUSTOM: "custom"}
        xy = lambda vector: [round(pcb.ToMM(vector.x), 9), round(pcb.ToMM(vector.y), 9)]
        for original in sorted(board.GetFootprints(), key=lambda item: (item.GetReference(), item.m_Uuid.AsString())):
            reference, uuid = original.GetReference(), original.m_Uuid.AsString()
            position = xy(original.GetPosition())
            angle = original.GetOrientationDegrees()
            box = original.GetBoundingBox(False, False)
            by_geometry = defaultdict(list)
            for pad in original.Pads():
                local = xy(pad.GetFPRelativePosition())
                if original.IsFlipped():
                    local[1] = -local[1]
                size = xy(pad.GetSize())
                key = (pad.GetNumber(), *local, *size, shape_names.get(pad.GetShape(), str(pad.GetShape())))
                by_geometry[key].append({"identifier": pad.GetNumber(), "net": pad.GetNetname(),
                                         "local_xy_mm": local, "board_xy_mm": xy(pad.GetPosition()), "size_mm": size,
                                         "shape": key[-1], "native_attribute": int(pad.GetAttribute())})
            filename = re.sub(r"[^A-Za-z0-9_.-]", "_", reference) + "--" + uuid
            footprint = pcb.FOOTPRINT(original)
            footprint.SetPosition(pcb.VECTOR2I(0, 0))
            footprint.SetOrientationDegrees(0)
            footprint.SetFPID(pcb.LIB_ID("", filename))
            plugin.FootprintSave(str(library), footprint)
            footprint_path = library / (filename + ".kicad_mod")
            text = footprint_path.read_text()
            text = re.sub(r'^\s*\(uuid "[^"\n]+"\)\n', "", text, flags=re.MULTILINE)
            footprint_path.write_text(text)
            imported = import_footprint(text) if by_geometry else {"pads": []}
            pads = []
            for imported_pad in imported["pads"]:
                key = (imported_pad["identifier"], imported_pad["x_mm"], imported_pad["y_mm"],
                       *imported_pad["size_mm"], imported_pad["shape"])
                matches = by_geometry.get(key, [])
                if len(matches) != 1:
                    raise ValueError(f"Ambiguous native/importer pad mapping: {reference} {key} ({len(matches)})")
                record = matches.pop()
                reason = imported_pad["unsupported_reason"]
                if original.IsFlipped():
                    reason = "Back-side footprint is inspect-only; mirrored model selection is not qualified."
                record.update(index=imported_pad["index"], supported=reason is None, unsupported_reason=reason,
                              declared_mask_margin_mm=imported_pad["declared_mask_margin_mm"])
                pads.append(record)
            if any(by_geometry.values()):
                raise ValueError(f"Native pads absent from importer: {reference}")
            theta = math.radians(angle)
            components.append({"reference": reference, "value": original.GetValue(), "uuid": uuid,
                               "side": "back" if original.IsFlipped() else "front", "board_position_mm": position,
                               "rotation_deg": angle, "bounds_mm": [round(pcb.ToMM(v), 9) for v in (box.GetX(), box.GetY(), box.GetWidth(), box.GetHeight())],
                               "footprint_file": str(footprint_path.relative_to(HERE)), "footprint_sha256": digest(footprint_path),
                               "local_x_board": [round(math.cos(theta), 12), round(-math.sin(theta), 12)], "pads": pads})
        bbox = board.GetBoardEdgesBoundingBox()
        context = {"schema": "soldershape.board-context.v1", "source": {"repository": provenance["repository"], "commit": provenance["commit"],
                   "board_sha256": digest(source), "license_sha256": digest(HERE / "source/LICENSE.md")},
                   "extraction": {"kicad_version": pcb.GetBuildVersion(), "image": IMAGE, "extractor_sha256": digest(Path(__file__)),
                                  "normalization": "Native standalone footprints translated to origin and rotated to zero. KiCad library export converts back-side footprints to front-side library coordinates by reversing local Y. Back-side selection remains inspect-only. Generated UUID records and SVG export timestamp removed. Original board unchanged."},
                   "bounds_mm": bounds, "stroke_inclusive_bounds_mm": [round(pcb.ToMM(v), 9) for v in (bbox.GetX(), bbox.GetY(), bbox.GetWidth(), bbox.GetHeight())],
                   "svg": {"file": "assets/board.svg", "sha256": digest(svg_path), "bounds_mm": bounds, "layers": ["F.Cu", "F.Silkscreen", "Edge.Cuts"]},
                   "counts": {"components": len(components), "pads": sum(len(c["pads"]) for c in components), "track_objects": len(board.GetTracks()),
                              "supported_pads": sum(p["supported"] for c in components for p in c["pads"])},
                   "scope": "Original attributed board context. Circular front SMD copper pads can define isolated hypothetical joint requests. Board-level mask, actual package, wetting, and coupled assembly remain unresolved.",
                   "components": components}
        write_json(HERE / "context.json", context)
    identities = {str(path.relative_to(HERE)): {"sha256": digest(path), "bytes": path.stat().st_size}
                  for path in sorted([HERE / "context.json", *assets.rglob("*.svg"), *library.glob("*.kicad_mod"),
                                      *[HERE / "source" / name for name in provenance["files"]], HERE / "source/provenance.json", HERE / "tools/extract.py", HERE / "tools/verify_native.py"])}
    write_json(HERE / "manifest.json", {"schema": "soldershape.board-files.v1", "files": identities})
    print(json.dumps(context["counts"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside:
        generate()
    else:
        subprocess.run(["docker", "run", "--rm", "--platform", "linux/amd64", "--network", "none", "-v", f"{ROOT}:/work", "-w", "/work", IMAGE,
                        "/usr/bin/python3", "board_demo/tools/extract.py", "--inside"], check=True)
        subprocess.run([sys.executable, str(HERE / "tools/verify_native.py")], check=True)


if __name__ == "__main__":
    main()
