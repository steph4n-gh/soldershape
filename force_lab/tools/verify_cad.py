#!/usr/bin/env python3
"""Read back neutral geometry and verify the quote-stage fixture contract."""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import ezdxf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "force_lab/cad"))
from model import SPEC_PATH, build, cylinder, read_spec


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    bb = shape.BoundingBox()
    return [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax]


def close(actual, expected, tolerance, label):
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{label}: {actual} != {expected} within {tolerance}")


def overlap_volume(a, b):
    aa, bb = bounds(a), bounds(b)
    if any(min(aa[i+3], bb[i+3]) - max(aa[i], bb[i]) < 1e-8 for i in range(3)):
        return 0.0
    return a.intersect(b).Volume()


def main():
    spec = read_spec()
    out = ROOT / "force_lab/hardware"
    proof = ROOT / "force_lab/cad/evidence"
    proof.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((out / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if digest(ROOT / name) != expected:
            raise AssertionError(f"Changed generated/source file: {name}")
    records = []
    for axis in ("x", "z"):
        for offset in spec["joint"]["offsets"]:
            parts, datums = build(spec, offset, axis)
            tag = f"{axis}-{round(offset*1000):03d}um"
            source = cq.Compound.makeCompound([p["shape"] for p in parts.values()])
            neutral = cq.importers.importStep(str(out / f"fixture-{tag}.step")).val()
            if not neutral.isValid() or len(neutral.Solids()) != len(parts):
                raise AssertionError(f"Invalid or missing neutral assembly solids: {tag}")
            close(neutral.Volume(), source.Volume(), 1e-5, tag + " volume")
            for i, (actual, expected) in enumerate(zip(bounds(neutral), bounds(source))):
                close(actual, expected, 1e-6, f"{tag} bbox {i}")
            collisions = []
            for (name_a, a), (name_b, b) in itertools.combinations(parts.items(), 2):
                volume = overlap_volume(a["shape"], b["shape"])
                if volume > 1e-8:
                    collisions.append([name_a, name_b, volume])
            if collisions:
                raise AssertionError(f"Solid interference {tag}: {collisions}")
            close(bounds(parts["lower_island"]["shape"])[5], 0, 1e-9, "lower wet face")
            close(bounds(parts["upper_island"]["shape"])[2], .150, 1e-9, "upper wet face")
            close(parts["upper_island"]["shape"].Center().x, offset, 1e-9, "upper pad offset")
            fixed = [p["shape"] for p in parts.values() if not p["moving"]]
            moving = cq.Compound.makeCompound([p["shape"] for p in parts.values() if p["moving"]])
            min_fixed_clearance = min(moving.distance(s) for s in fixed)
            if min_fixed_clearance < .059:
                raise AssertionError("Unexpected upper-path approach to fixed structure")
            o = spec["optics"]
            for direction in ((1, 0, 0), (0, 1, 0)):
                origin = tuple(o["external_aperture_start"] * v for v in direction)
                origin = (origin[0], origin[1], .075)
                aperture = cylinder(o["external_aperture_diameter"] / 2, o["external_aperture_length"], origin, direction)
                ray = cylinder(o["gap_ray_radius"], o["external_aperture_start"] + o["external_aperture_length"], (offset, 0, .075), direction)
                for name, part in parts.items():
                    if overlap_volume(part["shape"], aperture) > 1e-8 or overlap_volume(part["shape"], ray) > 1e-8:
                        raise AssertionError(f"Blocked optical reserve/ray: {tag} {name}")
            records.append({"configuration": tag, "neutral_solids": len(neutral.Solids()), "neutral_volume_mm3": neutral.Volume(), "neutral_bbox_mm": bounds(neutral), "unintended_intersections": collisions, "minimum_upper_to_fixed_clearance_mm": min_fixed_clearance, "wet_face_gap_mm": .150, "pad_offset_mm": offset, "external_optical_aperture_mm": o["external_aperture_diameter"], "datums": datums})
    parts, datums = build(spec)
    for path in sorted((out / "parts").glob("*.step")):
        name = path.stem
        if name.endswith("-x") or name.endswith("-z"):
            shape = build(spec, axis=name[-1])[0]["sensor_adapter_blank"]["shape"]
        else:
            shape = parts[name]["shape"]
        imported = cq.importers.importStep(str(path)).val()
        if not imported.isValid() or len(imported.Solids()) != 1:
            raise AssertionError(f"Invalid neutral part: {path.name}")
        close(imported.Volume(), shape.Volume(), 1e-6, path.name + " volume")
        for i, (a, b) in enumerate(zip(bounds(imported), bounds(shape))):
            close(a, b, 1e-6, f"{path.name} bbox {i}")
    base_readback = cq.importers.importStep(str(out / "parts/base.step")).val()
    cylinders = []
    for face in base_readback.Faces():
        if face.geomType() == "CYLINDER":
            geometry = face._geomAdaptor().Cylinder()
            center = face.Center()
            cylinders.append((center.x, center.y, geometry.Radius()))
    expected_holes = [(x, y, 2.25) for x in (-50., 10.) for y in (-30., 30.)]
    expected_holes += [(-40., y, 1.65) for y in (-10., 10.)]
    expected_holes += [(x, y, 1.25) for x in (-20., -13.) for y in (-4., 4.)]
    if len(cylinders) != len(expected_holes):
        raise AssertionError("Independent base hole readback count")
    for expected in expected_holes:
        if not any(max(abs(a-b) for a, b in zip(hole, expected)) < 1e-6 for hole in cylinders):
            raise AssertionError(f"Independent base hole position/radius missing: {expected}")
    thermal_readback = cq.importers.importStep(str(out / "parts/thermal_carrier.step")).val()
    pocket_bottom_z = datums["thermal_top_z"] - spec["thermal_carrier"]["pocket_depth"]
    floors = [face for face in thermal_readback.Faces() if face.geomType() == "PLANE" and abs(face.Center().z - pocket_bottom_z) < 1e-7]
    if len(floors) != 1:
        raise AssertionError("Independent pocket floor readback")
    close(floors[0].Area(), 10.2**2, 1e-6, "neutral pocket area")
    floor_bounds = bounds(floors[0])
    close(floor_bounds[3] - floor_bounds[0], 10.2, 1e-6, "neutral pocket X size")
    close(floor_bounds[4] - floor_bounds[1], 10.2, 1e-6, "neutral pocket Y size")
    for upper in (True, False):
        path = out / ("upper-cap-boundaries.dxf" if upper else "lower-chip-boundaries.dxf")
        doc = ezdxf.readfile(path)
        if doc.units != 4 or doc.audit().has_errors:
            raise AssertionError("Invalid DXF or non-mm units")
        circles = list(doc.modelspace().query('CIRCLE[layer=="METAL_ISLAND"]'))
        if len(circles) != 1:
            raise AssertionError("One and only one wettable island required")
        close(circles[0].dxf.radius * 2, .200, 1e-10, "DXF island diameter")
        close(circles[0].dxf.center.x, 0, 1e-10, "DXF pad center X")
    moving_names = [name for name, p in parts.items() if p["moving"]]
    path_names = ["upper_island", "upper_cap", "hot_bond", "stalk", "cool_bond", "cool_tab"]
    for a, b in zip(path_names, path_names[1:]):
        close(parts[a]["shape"].distance(parts[b]["shape"]), 0, 1e-7, "load-path adjacency " + a + "/" + b)
    force = spec["loads"]["reference_transverse_force_uN"]
    g = spec["loads"]["gravity_m_s2"]
    support = parts["cool_tab"]["shape"].Center()
    mass_mg = 0
    gravity_moment_uNm = 0
    masses = {}
    for name in moving_names:
        part = parts[name]
        mass = part["shape"].Volume() * spec["materials"][part["material"]]["density_g_cm3"]
        masses[name] = mass
        mass_mg += mass
        gravity_moment_uNm += mass * g * (part["shape"].Center().x - support.x) / 1000
    if mass_mg > spec["loads"]["moving_mass_target_mg"]:
        raise AssertionError("Modeled moving mass exceeds target")
    j, rod = spec["joint"], spec["stalk"]
    e_pa = spec["materials"]["silica"]["youngs_modulus_gpa"] * 1e9
    moment_m4 = math.pi * (rod["diameter"] * .001) ** 4 / 64
    stiffness = 3 * e_pa * moment_m4 / (rod["length"] * .001) ** 3
    tilt = math.radians(j["initial_tilt_limit_deg"])
    optical_margin = spec["shields"]["aperture_diameter"] / 2 - rod["diameter"] / 2 - (rod["length"] + spec["cool_tab"]["length"]) * math.sin(tilt)
    cap_extent = spec["upper_cap"]["length"] - spec["upper_cap"]["pad_free_edge_setback"]
    minimum_tilt_gap = j["upper_wet_face_z"] - cap_extent * math.sin(tilt)
    if optical_margin <= 0 or minimum_tilt_gap <= 0:
        raise AssertionError("Tilt/motion envelope collides")
    rejected_spec = json.loads(json.dumps(spec))
    rejected_spec["bracket"]["shelf_top_z"] = 16.7
    rejected_parts, _ = build(rejected_spec)
    rejected_overlap = overlap_volume(rejected_parts["indexed_bracket"]["shape"], rejected_parts["sensor_adapter_blank"]["shape"])
    if rejected_overlap < 1:
        raise AssertionError("Known shelf/adapter collision negative control was not detected")
    negative = {"kind": "development-negative-control", "physical_data": False, "change": "Shelf top initially 16.7 mm, moved to 26.7 mm to clear the vertical 30 mm adapter blank.", "initial_overlap_mm3": rejected_overlap, "initial_shelf_top_z_mm": 16.7, "current_shelf_top_z_mm": spec["bracket"]["shelf_top_z"]}
    (proof / "development-collision.json").write_text(json.dumps(negative, indent=2) + "\n")
    checks = {"schema": "soldershape.fixture-verification.v1", "status": "digital geometry verified; quote stage; physical integration not accepted", "spec_sha256": digest(SPEC_PATH), "manifest_sha256": digest(out / "manifest.json"), "verifier_sha256": digest(Path(__file__)), "configurations": records, "neutral_part_count": len(list((out / "parts").glob("*.step"))), "independently_read_base_holes_xyz_radius_mm": sorted(cylinders), "independently_read_pocket_bounds_mm": floor_bounds, "load_path": path_names + ["UNRESOLVED supplier-approved sensor attachment"], "modeled_moving_mass_mg": mass_mg, "moving_part_masses_mg": masses, "unallocated_tip_attachment_mass_to_100mg_target_mg": spec["loads"]["moving_mass_target_mg"] - mass_mg, "modeled_deadweight_uN": mass_mg * g, "modeled_gravity_moment_at_tab_uNm": gravity_moment_uNm, "reference_joint_force_uN": force, "reference_normal_joint_moment_at_tab_uNm": force * abs(.040 - support.x) / 1000, "worst_sum_gravity_and_reference_normal_moment_uNm": abs(gravity_moment_uNm) + force * abs(.040 - support.x) / 1000, "rod_only_transverse_stiffness_N_m": stiffness, "rod_only_reference_deflection_um": force / stiffness, "rod_uniform_200K_expansion_um": rod["length"] * spec["materials"]["silica"]["cte_per_k"] * spec["loads"]["uniform_temperature_change_k"] * 1000, "tilt_envelope_deg": j["initial_tilt_limit_deg"], "lower_bound_cap_to_lower_plane_under_tilt_mm": minimum_tilt_gap, "lower_bound_rod_to_shield_under_tilt_mm": optical_margin, "continuous_offset_sweep_mm": [.040, .120], "sweep_argument": "All moving parts translate only in X. Rod aperture cross-section is constant along X; cap remains above lower plane, and no other fixed body overlaps its swept bounds. Tilt bounds subtract the maximum entire-carrier displacement from radial aperture clearance.", "limitations": spec["unreleased_interfaces"]}
    (proof / "verification.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({k: checks[k] for k in ("status", "neutral_part_count", "modeled_moving_mass_mg", "modeled_deadweight_uN", "modeled_gravity_moment_at_tab_uNm", "worst_sum_gravity_and_reference_normal_moment_uNm", "rod_only_transverse_stiffness_N_m", "rod_only_reference_deflection_um", "lower_bound_cap_to_lower_plane_under_tilt_mm", "lower_bound_rod_to_shield_under_tilt_mm")}, indent=2))


if __name__ == "__main__":
    main()
