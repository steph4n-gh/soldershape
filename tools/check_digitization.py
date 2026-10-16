"""Recalculate the frozen manual Figure 5 pixel readings without PDF dependencies."""

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, help="Also verify the downloaded primary PDF's SHA-256.")
    args = parser.parse_args()
    record = json.loads((ROOT / "evidence/physical/nist-extraction.json").read_text())
    if args.pdf is not None:
        digest = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
        if digest != record["source_sha256"]:
            raise SystemExit("The PDF does not match the frozen primary source.")
    calibration = record["calibration"]
    origin = calibration["origin_px"]
    force = [(v-o)/150 for v, o in zip(calibration["force_150_uN_px"], origin)]
    dimension = [(v-o)/60 for v, o in zip(calibration["height_60_um_px"], origin)]
    determinant = force[0]*dimension[1] - dimension[0]*force[1]

    def coordinates(x, y):
        dx, dy = x-origin[0], y-origin[1]
        return ((dx*dimension[1]-dimension[0]*dy)/determinant,
                (force[0]*dy-dx*force[1])/determinant)

    for row in record["observations"]:
        applied, value = coordinates(row["pixel_x"], row["pixel_y"])
        upper = coordinates(row["pixel_x"], row["errorbar_top_pixel_y"])[1]
        bottom = row["errorbar_bottom_pixel_y"]
        lower = None if bottom is None else round(coordinates(row["pixel_x"], bottom)[1], 1)
        measured = (round(applied, 1), round(value, 1), round(upper, 1), lower)
        saved = (row["shear_uN"], row["value_um"], row["plotted_upper_um"], row["plotted_lower_um"])
        if measured != saved:
            raise SystemExit(f"Pixel calibration differs for {row['id']}: {measured} versus {saved}.")
    effective_volume = round(record["solder_volume_mm3"] + 2*math.pi*(record["pad_diameter_mm"]/2)**2*record["pad_thickness_mm"], 9)
    if effective_volume != record["flat_plane_effective_volume_mm3"]:
        raise SystemExit("The published pad-slab volume transformation differs.")
    print(json.dumps({"passed": True, "experimental_symbols": len(record["observations"]),
                      "pdf_sha256_checked": args.pdf is not None, "effective_volume_mm3": effective_volume,
                      "scope": "Recalculation of recorded manual pixel readings, not an independent redigitization or physical validation."}, indent=2))


if __name__ == "__main__":
    main()
