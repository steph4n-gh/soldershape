"""Replay numerical references and the complete import-to-export operation."""

from collections import Counter
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import make_bundle, read_bundle
from soldershape.model import InputError, JointSpec, import_footprint, request_from_footprint
from soldershape.solver import engine_info, solve


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def segment_hits(a, b, triangle, epsilon=1e-10):
    p, q, r = triangle
    edge1, edge2, direction = sub(q, p), sub(r, p), sub(b, a)
    h = cross(direction, edge2)
    determinant = dot(edge1, h)
    scale = math.sqrt(dot(edge1, edge1) * dot(h, h))
    if abs(determinant) <= epsilon * max(scale, 1e-30):
        return False
    s = sub(a, p)
    u = dot(s, h) / determinant
    v = dot(direction, cross(s, edge1)) / determinant
    t = dot(edge2, cross(s, edge1)) / determinant
    return epsilon < t < 1-epsilon and epsilon < u and epsilon < v and u+v < 1-epsilon


def triangles_cross(first, second):
    return any(segment_hits(triangle[i], triangle[(i+1) % 3], other)
               for triangle, other in ((first, second), (second, first)) for i in range(3))


def mesh_intersections(mesh):
    vertices, triangles = mesh["vertices_mm"], mesh["triangles"]
    boxes = []
    for index, tri in enumerate(triangles):
        points = [vertices[i] for i in tri]
        boxes.append((min(v[0] for v in points), max(v[0] for v in points),
                      min(v[1] for v in points), max(v[1] for v in points),
                      min(v[2] for v in points), max(v[2] for v in points), index))
    active = []
    pairs_checked = 0
    for box in sorted(boxes):
        active = [candidate for candidate in active if candidate[1] > box[0]]
        tri = triangles[box[6]]
        for other in active:
            if other[3] < box[2] or box[3] < other[2] or other[5] < box[4] or box[5] < other[4]:
                continue
            second = triangles[other[6]]
            if set(tri) & set(second):
                continue
            pairs_checked += 1
            if triangles_cross([vertices[i] for i in tri], [vertices[i] for i in second]):
                return {"proper_intersections": 1, "first_pair": [box[6], other[6]], "pairs_checked": pairs_checked}
        active.append(box)
    return {"proper_intersections": 0, "pairs_checked": pairs_checked,
            "scope": "Nonadjacent triangle pairs; proper transverse crossings. Coplanar overlaps and tangential contacts are not certified."}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def reference_gate():
    reference = ROOT / ".engine" / "bga" / "bga-4.fe"
    if not reference.exists():
        reference = next((ROOT / ".engine").rglob("bga-4.fe"))
    commands = 'gogo\nprintf "REFERENCE %.17g\\n",zforce7.value\nr\ng 5\nhessian\nhessian\nprintf "REFERENCE %.17g\\n",zforce7.value\nr\ng 5\nhessian\nhessian\nprintf "REFERENCE %.17g\\n",zforce7.value\nquit 0\n'
    (ROOT / "evidence" / "upstream-reference.cmd").write_text(commands)
    run = subprocess.run([str(ROOT / ".engine" / "src" / "evolver"), reference.name], cwd=reference.parent,
                         input=commands, capture_output=True, text=True, timeout=60)
    (ROOT / "evidence" / "upstream-reference.txt").write_text(run.stdout + run.stderr)
    check(run.returncode == 0 and not re.search(r"\b(?:ERROR|WARNING)\b", run.stdout + run.stderr), "Upstream reference engine error")
    values = [float(x) for x in re.findall(r"REFERENCE ([-+\d.eE]+)\n", run.stdout)]
    expected = [24.583607839182264, 18.668111551491222, 17.195067593386000]
    check(len(values) == 3, "Missing reference force values")
    relative = [abs(a/b-1) for a, b in zip(values, expected)]
    check(max(relative) < .001, "Published BGA force reference differs by over 0.1 percent")
    return {"computed_dyn": values, "published_dyn": expected, "relative_error": relative,
            "source": "https://kenbrakke.com/evolver/bga/bga-4.htm"}


def rejection_checks(source):
    count = 0
    for bad in (source + ")", '(footprint "bad" (pad "A1" smd circle (at nan 0) (size .2 .2) (layers "F.Cu")))'):
        try:
            import_footprint(bad)
        except InputError:
            count += 1
        else:
            raise AssertionError("Malformed footprint was accepted")
    for values in ({"offset_mm": float("nan")}, {"gravity": "false"}, {"volume_mm3": -1}, {"offset_mm": True}):
        try:
            JointSpec.from_dict({"lower_diameter_mm": .2, "upper_diameter_mm": .2, "standoff_mm": .15,
                                 "volume_mm3": .006, "offset_mm": .02, **values})
        except InputError:
            count += 1
        else:
            raise AssertionError("Invalid numerical request was accepted")
    unsupported = '(footprint "square" (pad "1" smd rect (at 0 0) (size .2 .2) (layers "F.Cu")))'
    try:
        request_from_footprint(unsupported, 0, {"upper_diameter_mm": .2, "standoff_mm": .15, "volume_mm3": .006, "offset_mm": 0})
    except InputError:
        count += 1
    else:
        raise AssertionError("Unsupported square was silently modeled as a circle")
    return count


def main():
    (ROOT / "evidence").mkdir(exist_ok=True)
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    source = (ROOT / "examples" / json.loads((ROOT / "examples/provenance.json").read_text())["filename"]).read_text()
    footprint = import_footprint(source)
    check(len(footprint["pads"]) == 36 and footprint["pads"][0]["identifier"] == "A1", "Real KiCad example import differs")
    check(footprint["pads"][0]["size_mm"] == [.2, .2] and footprint["pads"][0]["x_mm"] == -1, "Pad units or position lost")
    report = {"engine": engine_info(), "footprint": {"name": footprint["name"], "sha256": footprint["sha256"], "pad_count": len(footprint["pads"])},
              "rejection_checks": rejection_checks(source), "published_reference": reference_gate()}
    radius, height, tension = .25, .3, .48
    cylinder = JointSpec(2*radius, 2*radius, height, math.pi*radius*radius*height, 0, tension, 9, False)
    analytic = solve(cylinder)
    expected_z = -math.pi*radius*tension*1000
    check(analytic["status"] == "refinement_checked", "Cylinder failed numerical checks")
    check(abs(analytic["forces"]["z_uN"]/expected_z-1) < .02, "Cylinder force differs by over 2 percent")
    check(abs(analytic["forces"]["x_uN"]) < abs(expected_z)*.0001, "Cylinder has spurious lateral force")
    report["cylinder"] = {"computed_uN": analytic["forces"], "analytic_z_uN": expected_z,
                          "relative_z_error": abs(analytic["forces"]["z_uN"]/expected_z-1), "diagnostics": analytic["diagnostics"]}
    spec, provenance = request_from_footprint(source, 0, json.loads((ROOT / "examples" / "parameters.json").read_text()))
    results = []
    for offset in (-.04, -.02, 0, .02, .04):
        result = solve(replace(spec, offset_mm=offset))
        result["footprint"] = provenance
        check(result["status"] == "refinement_checked", f"Offset {offset} failed refinement checks")
        check(result["mesh_checks"]["euler_characteristic"] == 2, "Joint mesh is not topologically spherical")
        results.append(result)
    for negative, positive in ((results[0], results[-1]), (results[1], results[-2])):
        fx1, fx2 = negative["forces"]["x_uN"], positive["forces"]["x_uN"]
        check(fx1 > 0 > fx2 and abs((fx1+fx2)/fx1) < .03, "Mirrored offsets do not give mirrored restoring forces")
    report["offset_sweep"] = [{"offset_mm": r["input"]["offset_mm"], "forces": r["forces"], "status": r["status"], "diagnostics": r["diagnostics"]} for r in results]
    no_gravity = solve(replace(spec, gravity=False))
    doubled = solve(replace(spec, gravity=False, surface_tension_n_m=spec.surface_tension_n_m*2))
    ratios = {axis: doubled["forces"][axis]/no_gravity["forces"][axis] for axis in ("x_uN", "z_uN")}
    check(all(abs(ratio/2-1) < .02 for ratio in ratios.values()), "No-gravity force does not scale with tension")
    report["surface_tension_scaling"] = ratios
    lower_volume = solve(replace(spec, volume_mm3=.005))
    higher_volume = solve(replace(spec, volume_mm3=.007))
    report["volume_comparison"] = [{"volume_mm3": r["input"]["volume_mm3"], "forces": r["forces"], "status": r["status"]} for r in (lower_volume, results[3], higher_volume)]
    check(all(r["status"] == "refinement_checked" for r in (lower_volume, higher_volume)), "Volume comparison missed numerical checks")
    unequal = solve(replace(spec, upper_diameter_mm=.24))
    check(unequal["status"] == "refinement_checked", "Unequal circular pad example missed checks")
    report["unequal_pad"] = {"upper_diameter_mm": .24, "forces": unequal["forces"], "diagnostics": unequal["diagnostics"]}
    check(triangles_cross([(0,0,0),(1,0,0),(0,1,0)], [(.2,.2,-1),(.2,.2,1),(.8,.8,0)]), "Intersection detector missed its positive control")
    check(not triangles_cross([(0,0,0),(1,0,0),(0,1,0)], [(0,0,2),(1,0,2),(0,1,2)]), "Intersection detector failed its negative control")
    report["mesh_intersection_checks"] = []
    for name, result in (("selected", results[3]), ("unequal", unequal)):
        mesh_check = mesh_intersections(result["mesh"])
        check(mesh_check["proper_intersections"] == 0, "Representative export contains a proper triangle crossing")
        report["mesh_intersection_checks"].append({"case": name, **mesh_check, "topology": result["mesh_checks"]})
    bundle = make_bundle(results, source)
    path = out / "acceptance-sweep.zip"
    path.write_bytes(bundle)
    cases = read_bundle(path)
    check(len(cases) == 5, "Export dropped a sweep row")
    with zipfile.ZipFile(path) as archive:
        csv = archive.read("results.csv").decode()
        check(len(csv.splitlines()) == 6 and "force_x_uN" in csv, "CSV does not contain the actual sweep")
        stl = archive.read("case-03/mesh-mm.stl").decode()
        check(stl.count("endfacet") == len(results[3]["mesh"]["triangles"]), "STL facet count differs from displayed mesh")
        saved = json.loads(archive.read("case-03/result.json"))
        check(saved["mesh"] == results[3]["mesh"] and saved["forces"] == results[3]["forces"], "Export changed the solved mesh or force")
    single = out / "acceptance-case.zip"
    single.write_bytes(make_bundle([results[3]], source))
    replay = subprocess.run([sys.executable, "-m", "soldershape", "replay", str(single)], cwd=ROOT, text=True, capture_output=True, timeout=120)
    check(replay.returncode == 0, "Replay failed: " + replay.stdout + replay.stderr)
    report["replay"] = json.loads(replay.stdout)
    report["artifacts"] = {"sweep": str(path.relative_to(ROOT)), "sweep_sha256": hashlib.sha256(bundle).hexdigest(), "case": str(single.relative_to(ROOT))}
    report["passed"] = True
    (ROOT / "evidence" / "acceptance.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"passed": True, "numerical_cases": 11, "report": "evidence/acceptance.json", "bundle": str(path)}, indent=2))


if __name__ == "__main__":
    main()
