"""Quote-stage fixture geometry. All lengths are millimeters."""

import json
from pathlib import Path

import cadquery as cq


SPEC_PATH = Path(__file__).with_name("spec.json")


def read_spec():
    return json.loads(SPEC_PATH.read_text())


def box(lx, ly, lz, center):
    return cq.Workplane("XY").box(lx, ly, lz).translate(center).val()


def cylinder(radius, length, origin, direction):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*origin), cq.Vector(*direction))


def build(spec, offset=0.040, axis="x"):
    if axis not in ("x", "z") or offset not in spec["joint"]["offsets"]:
        raise ValueError("Use a declared offset and indexed x or z configuration")
    j, cap, rod = (spec[k] for k in ("joint", "upper_cap", "stalk"))
    chip, tc, ped, base, bracket, adapter, shields = (spec[k] for k in ("lower_chip", "thermal_carrier", "pedestal", "base", "bracket", "adapter_blank", "shields"))
    film = j["thin_film_thickness"]
    cap_bottom = j["upper_wet_face_z"] + film
    cap_top = cap_bottom + cap["thickness"]
    rod_z = cap_top + rod["bottom_clearance_above_cap"] + rod["diameter"] / 2
    rod_end = offset + rod["end_relative_to_pad_x"]
    rod_start = rod_end - rod["length"]
    chip_top = j["lower_wet_face_z"] - film
    chip_bottom = chip_top - chip["thickness"]
    thermal_top = chip_bottom + tc["pocket_depth"]
    thermal_bottom = thermal_top - tc["thickness"]
    base_top = thermal_bottom - ped["height"]
    parts = {}

    def add(name, shape, material, moving=False, role="custom part"):
        parts[name] = {"shape": shape, "material": material, "moving": moving, "role": role}

    cap_center_x = offset + cap["pad_free_edge_setback"] - cap["length"] / 2
    add("upper_cap", box(cap["length"], cap["width"], cap["thickness"], (cap_center_x, 0, cap_bottom + cap["thickness"] / 2)), "silica", True)
    add("upper_island", cylinder(j["diameter"] / 2, film, (offset, 0, j["upper_wet_face_z"]), (0, 0, 1)), "metal_placeholder", True, "illustrative thin-film envelope")
    stalk = cylinder(rod["diameter"] / 2, rod["length"], (rod_start, 0, rod_z), (1, 0, 0))
    add("stalk", stalk, "silica", True)
    hb = spec["hot_bond"]
    bond = box(hb["length"], hb["width"], hb["height"], (rod_end - hb["length"] / 2, 0, cap_top + hb["height"] / 2)).cut(stalk)
    add("hot_bond", bond, "bond_placeholder", True, "unqualified conformal bond envelope")
    tab = spec["cool_tab"]
    tab_center = rod_start - tab["length"] / 2
    add("cool_tab", box(tab["length"], tab["width"], tab["thickness"], (tab_center, 0, cap_bottom + tab["thickness"] / 2)), "silica", True, "sensor-tip attachment target; vendor interface unresolved")
    cool_bond = box(tab["length"], hb["width"], hb["height"], (tab_center, 0, cap_top + hb["height"] / 2))
    add("cool_bond", cool_bond, "bond_placeholder", True, "unqualified tab-to-stalk end bond envelope")
    add("lower_chip", box(chip["length"], chip["width"], chip["thickness"], (0, 0, chip_bottom + chip["thickness"] / 2)), "silica")
    add("lower_island", cylinder(j["diameter"] / 2, film, (0, 0, chip_top), (0, 0, 1)), "metal_placeholder", role="illustrative thin-film envelope")
    thermal = box(tc["length"], tc["width"], tc["thickness"], (0, 0, thermal_bottom + tc["thickness"] / 2))
    pocket = box(tc["pocket_length"], tc["pocket_width"], tc["pocket_depth"] + 1, (0, 0, thermal_top - tc["pocket_depth"] + (tc["pocket_depth"] + 1) / 2))
    add("thermal_carrier", thermal.cut(pocket), "alumina", role="heater mating face unresolved")
    add("pedestal", box(ped["length"], ped["width"], ped["height"], (0, 0, thermal_bottom - ped["height"] / 2)), "alumina", role="insulating support; heater integration unresolved")
    plate = box(base["length"], base["width"], base["thickness"], (base["center_x"], 0, base_top - base["thickness"] / 2))
    for dx in (-base["mount_pitch"] / 2, base["mount_pitch"] / 2):
        for y in (-base["mount_pitch"] / 2, base["mount_pitch"] / 2):
            plate = plate.cut(cylinder(base["mount_hole_diameter"] / 2, base["thickness"], (base["center_x"] + dx, y, base_top - base["thickness"]), (0, 0, 1)))
    for y in (-bracket["hole_pitch"] / 2, bracket["hole_pitch"] / 2):
        plate = plate.cut(cylinder(1.65, base["thickness"], (bracket["base_hole_x"], y, base_top - base["thickness"]), (0, 0, 1)))
    wall_x = bracket["back_x"] + bracket["wall_thickness"] / 2
    wall = box(bracket["wall_thickness"], bracket["width"], bracket["height"], (wall_x, 0, base_top + bracket["height"] / 2))
    foot = box(bracket["foot_length"], bracket["width"], bracket["foot_thickness"], (bracket["back_x"] + bracket["foot_length"] / 2, 0, base_top + bracket["foot_thickness"] / 2))
    face_x = bracket["back_x"] + bracket["wall_thickness"]
    shelf_center_x = face_x + bracket["shelf_length"] / 2
    shelf = box(bracket["shelf_length"], bracket["width"], bracket["shelf_thickness"], (shelf_center_x, 0, bracket["shelf_top_z"] - bracket["shelf_thickness"] / 2))
    support = wall.fuse(foot).fuse(shelf).clean()
    for y in (-bracket["hole_pitch"] / 2, bracket["hole_pitch"] / 2):
        support = support.cut(cylinder(bracket["clearance_diameter"] / 2, bracket["foot_thickness"], (bracket["base_hole_x"], y, base_top), (0, 0, 1)))
        support = support.cut(cylinder(bracket["clearance_diameter"] / 2, bracket["wall_thickness"], (bracket["back_x"], y, bracket["face_hole_z"]), (1, 0, 0)))
        support = support.cut(cylinder(bracket["clearance_diameter"] / 2, bracket["shelf_thickness"], (shelf_center_x, y, bracket["shelf_top_z"] - bracket["shelf_thickness"]), (0, 0, 1)))
    add("indexed_bracket", support, "aluminum")
    if axis == "x":
        blank = box(adapter["thickness"], adapter["width"], adapter["length"], (face_x + adapter["thickness"] / 2, 0, bracket["face_hole_z"]))
        for y in (-adapter["fixture_hole_pitch"] / 2, adapter["fixture_hole_pitch"] / 2):
            blank = blank.cut(cylinder(adapter["fixture_hole_diameter"] / 2, adapter["thickness"], (face_x, y, bracket["face_hole_z"]), (1, 0, 0)))
    else:
        blank = box(adapter["length"], adapter["width"], adapter["thickness"], (shelf_center_x, 0, bracket["shelf_top_z"] + adapter["thickness"] / 2))
        for y in (-adapter["fixture_hole_pitch"] / 2, adapter["fixture_hole_pitch"] / 2):
            blank = blank.cut(cylinder(adapter["fixture_hole_diameter"] / 2, adapter["thickness"], (shelf_center_x, y, bracket["shelf_top_z"]), (0, 0, 1)))
    add("sensor_adapter_blank", blank, "aluminum", role="internal mounting only; vendor pattern unmachined")
    for i, x in enumerate(shields["x_positions"]):
        sign = -1 if i == 0 else 1
        shield = box(shields["thickness"], shields["width"], shields["top_z"] - base_top, (x, 0, (shields["top_z"] + base_top) / 2))
        shield_foot = box(shields["foot_length"], shields["width"], shields["thickness"], (x + sign * (shields["foot_length"] - shields["thickness"]) / 2, 0, base_top + shields["thickness"] / 2))
        shield = shield.fuse(shield_foot).cut(cylinder(shields["aperture_diameter"] / 2, shields["thickness"], (x - shields["thickness"] / 2, 0, rod_z), (1, 0, 0)))
        hole_x = x + sign * 2
        for y in (-shields["hole_y"], shields["hole_y"]):
            shield = shield.cut(cylinder(shields["foot_hole_diameter"] / 2, shields["thickness"], (hole_x, y, base_top), (0, 0, 1)))
            plate = plate.cut(cylinder(1.25, base["thickness"], (hole_x, y, base_top - base["thickness"]), (0, 0, 1)))
        add(f"shield_{i + 1}", shield.clean(), "steel")
    add("base", plate, "aluminum", role="internal fixture pattern; lab stage adapter unresolved")
    datums = {"upper_pad_xyz": [offset, 0, j["upper_wet_face_z"]], "lower_pad_xyz": [0, 0, j["lower_wet_face_z"]], "cap_top_z": cap_top, "rod_center_z": rod_z, "rod_start_x": rod_start, "rod_end_x": rod_end, "base_top_z": base_top, "thermal_top_z": thermal_top, "axis": axis, "offset_mm": offset}
    return parts, datums
