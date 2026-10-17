"""Replay matched NIST fixed-displacement and conditional force-balance cases."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from soldershape.solver import ENGINE, engine_info

SOURCE_URL = "https://www.ctcms.nist.gov/solder/underfill/underfill.zip"
SOURCE_HASH = "fa1ceb86bd9f37214194370b809ee92e73614ed3c1c7b1e43a80460d759bfcc5"
NUMBER = r"[-+0-9.eE]+"
FIXED_CASES = {"h2-x2": (.0351, .0071), "h4-x4": (.0372, .0151), "h6-x6": (.0351, .031)}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def source_files(archive):
    if not archive.exists():
        archive.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
        archive.write_bytes(urllib.request.urlopen(request, timeout=30).read())
    if sha256(archive.read_bytes()) != SOURCE_HASH:
        raise ValueError("NIST archive hash differs from the frozen archive.")
    with zipfile.ZipFile(archive) as saved:
        return {name: saved.read(name) for name in saved.namelist()
                if "/" not in name and name.endswith((".fe", ".cmd"))}


def geometry_checks(path, height):
    vertices, faces = {}, []
    for line in path.read_text().splitlines():
        parts = line.split()
        if parts[0] == "V":
            vertices[int(parts[1])] = list(map(float, parts[2:]))
        elif parts[0] == "F":
            faces.append(list(map(int, parts[2:])))
    angles = []
    for face in faces:
        xyz = [vertices[index] for index in face]
        if max(point[2] for point in xyz) - min(point[2] for point in xyz) < 1e-10:
            continue
        a = [xyz[1][i] - xyz[0][i] for i in range(3)]
        b = [xyz[2][i] - xyz[0][i] for i in range(3)]
        normal = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
        normal_z = normal[2] / math.sqrt(sum(value*value for value in normal))
        for side, z in ((1, 0), (2, height)):
            if sum(abs(point[2]-z) < 1e-10 for point in xyz) >= 2:
                cosine = normal_z if side == 1 else -normal_z
                angles.append(math.degrees(math.acos(max(-1, min(1, cosine)))))
    z_min, z_max = min(v[2] for v in vertices.values()), max(v[2] for v in vertices.values())
    return {"minimum_z_mm": z_min, "maximum_z_mm": z_max,
            "sampled_plane_intrusion_mm": max(0, -z_min, z_max-height),
            "sampled_contact_angles_degrees": [min(angles), max(angles)],
            "contact_angle_samples": len(angles),
            "scope": "Flat export vertices and adjacent facet normals. These are sampled checks, not curved-element bounds."}


def run_native(files, directory, height, offset, pad_um=5, gamma=1):
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (directory / name).write_bytes(data)
    model = files["force.fe"].decode()
    replacements = {
        "PARAMETER gamma=45/100": f"PARAMETER gamma={gamma:.17g}",
        "PARAMETER theta_out1=140": "PARAMETER theta_out1=150",
        "PARAMETER theta_out2=140": "PARAMETER theta_out2=150",
        "PARAMETER volsolder = .029": "PARAMETER volsolder = .0086",
        "PARAMETER padthick= 4.0e-3": f"PARAMETER padthick= {pad_um/1000:.17g}",
        "parameter hgt = 0.1": f"parameter hgt = {height:.17g}",
        "parameter xoff = -0.0": f"parameter xoff = {offset:.17g}",
        "parameter fz=mass*grav*cos(pi*tilt/180)/no_pads": "parameter fz=0",
        "parameter fx=mass*grav*sin(pi*tilt/180)/no_pads": "parameter fx=0",
    }
    for before, after in replacements.items():
        if before not in model:
            raise ValueError(f"Frozen NIST model no longer contains {before!r}.")
        model = model.replace(before, after)
    (directory / "joint.fe").write_text(model)
    commands = [
        "set vertex constraint 5 where on_constraint 1",
        "set edge constraint 5 where on_constraint 1",
        "set vertex constraint 6 where on_constraint 2 and id != 13",
        "set edge constraint 6 where on_constraint 2", "fixonconstraint",
        "set edge fixed where on_constraint 1 or on_constraint 2",
        "M 2", "u", "g 3", "r", "g 30", "r", "g 30", "hessian_seek", "hessian_seek",
    ]
    for level in range(3):
        if level:
            commands += ["r", "g 30", "hessian_seek", "hessian_seek", "hessian_seek"]
        commands += ["g 30", "hessian_seek", "hessian_seek", "forcex", "forcez", "eigenprobe 0",
                     f'printf "UP_RESULT {level} %.17g %.17g %.17g %.17g\\n",forx,forz,total_energy,body[1].volume']
    commands += ["r", "linear", "recalc",
                 '{ foreach vertex vv do printf "V %d %.17g %.17g %.17g\\n",vv.id,vv.x,vv.y,vv.z; foreach facet ff do printf "F %d %d %d %d\\n",ff.id,ff.vertex[1].id,ff.vertex[2].id,ff.vertex[3].id; } >>> "mesh.txt"', "quit 0"]
    command_text = "\n".join(commands) + "\n"
    (directory / "commands.cmd").write_text(command_text)
    result = subprocess.run([str(ENGINE / "src/evolver"), "joint.fe"], cwd=directory,
                            input=command_text, capture_output=True, text=True, timeout=90)
    (directory / "stdout.txt").write_text(result.stdout)
    (directory / "stderr.txt").write_text(result.stderr)
    pattern = rf"UP_RESULT (\d+) ({NUMBER}) ({NUMBER}) ({NUMBER}) ({NUMBER})\n"
    rows = [{"level": int(row[0]), "force_x_uN": float(row[1])*1000,
             "force_z_uN": float(row[2])*1000, "energy_native": float(row[3]),
             "volume_mm3": float(row[4])} for row in re.findall(pattern, result.stdout)]
    eigen = [list(map(int, row)) for row in re.findall(r"Eigencounts:\s+(\d+) <,\s+(\d+) ==,\s+(\d+) >", result.stdout)]
    warnings = re.findall(r".*(?:WARNING|ERROR).*", result.stdout+result.stderr)
    if result.returncode or warnings or len(rows) != 3 or len(eigen) != 3 or any(row[0] for row in eigen):
        raise RuntimeError(f"Unqualified native result in {directory}.")
    volume = .0086 + 2*math.pi*.32*.32*pad_um/1000
    changes = {axis: abs(rows[-1][f"force_{axis}_uN"]-rows[-2][f"force_{axis}_uN"])/max(abs(rows[-1][f"force_{axis}_uN"]), 1) for axis in ("x", "z")}
    if max(changes.values()) > .01 or max(abs(row["volume_mm3"]/volume-1) for row in rows) > 1e-9:
        raise RuntimeError(f"Native refinement or volume check failed in {directory}.")
    return {"height_mm": height, "offset_mm": offset, "pad_thickness_um": pad_um,
            "force_refinement_relative_changes": changes,
            "gamma_N_per_m": gamma, "levels": rows, "eigen_counts": eigen,
            "warnings": warnings, "geometry": geometry_checks(directory / "mesh.txt", height),
            "files_sha256": {name: sha256((directory/name).read_bytes()) for name in
                             ("joint.fe", "commands.cmd", "stdout.txt", "stderr.txt", "mesh.txt")}}


def balance(files, directory, pad_um):
    normal = .0015*9800*math.cos(math.radians(4.5))/8*1000
    shear = .0015*9800*math.sin(math.radians(4.5))/8*1000
    height, offset = (.0344 if pad_um == 4 else .0364), .014
    trials = []

    def evaluate(h, x):
        trial = run_native(files, directory / f"trial-{len(trials):02d}", h, x, pad_um, .4)
        final = trial["levels"][-1]
        residual = [final["force_z_uN"]-normal, -final["force_x_uN"]-shear]
        trials.append({"result": trial, "residual_uN": residual})
        return residual

    for _ in range(6):
        residual = evaluate(height, offset)
        if max(abs(residual[0]/normal), abs(residual[1]/shear)) < .001:
            break
        dh, dx = .00005, .0001
        changed_h, changed_x = evaluate(height+dh, offset), evaluate(height, offset+dx)
        a, b = (changed_h[0]-residual[0])/dh, (changed_x[0]-residual[0])/dx
        c, d = (changed_h[1]-residual[1])/dh, (changed_x[1]-residual[1])/dx
        determinant = a*d-b*c
        step_h = (-residual[0]*d+b*residual[1])/determinant
        step_x = (-a*residual[1]+c*residual[0])/determinant
        scale = min(1, .001/max(abs(step_h), 1e-30), .005/max(abs(step_x), 1e-30))
        height, offset = height+scale*step_h, offset+scale*step_x
    else:
        raise RuntimeError("Force balance did not meet its declared residual threshold.")
    return {"normal_load_uN": normal, "shear_load_uN": shear,
            "load_assumption": "Source-commented mass 0.0015 kg at tilt 4.5 degrees, eight joints. This does not establish the measured specimen's actual normal load.",
            "height_mm": height, "offset_mm": offset, "trials": trials}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=ROOT/".research/physical/nist-extraction/underfill.zip")
    parser.add_argument("--output", type=Path, default=ROOT/".research/model-repair/upstream-replay")
    parser.add_argument("--fixed-only", action="store_true")
    args = parser.parse_args()
    engine = engine_info()
    if not engine["ready"]:
        raise RuntimeError(engine["error"])
    files = source_files(args.archive)
    args.output.mkdir(parents=True, exist_ok=True)
    results = {"source_url": SOURCE_URL, "source_sha256": SOURCE_HASH, "engine": engine,
               "script_sha256": sha256(Path(__file__).read_bytes()), "fixed": {}, "balanced": {}}
    for name, (height, offset) in FIXED_CASES.items():
        results["fixed"][name] = run_native(files, args.output/name, height, offset)
    if not args.fixed_only:
        for pad in (4, 5):
            results["balanced"][str(pad)] = balance(files, args.output/f"balance-{pad}um", pad)
    (args.output/"results.json").write_text(json.dumps(results, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"fixed_forces_uN": {name: data["levels"][-1] for name, data in results["fixed"].items()},
                      "balanced": {name: {key: data[key] for key in ("height_mm", "offset_mm")} for name, data in results["balanced"].items()},
                      "result_file": str(args.output/"results.json")}, indent=2))


if __name__ == "__main__":
    main()
