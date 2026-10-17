import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import json_bytes, make_bundle
from soldershape.demo import demo_requests, read_demo
from soldershape.model import PYTHON_SOURCE_SHA256 as MODEL_SOURCE_SHA256
from soldershape.solver import PYTHON_SOURCE_SHA256 as SOLVER_SOURCE_SHA256, SolverError, solve


def main():
    parser = argparse.ArgumentParser(description="Record or verify the seven-case native misalignment demo.")
    parser.add_argument("--verify", action="store_true", help="Verify retained recording without changing it or running native code.")
    args = parser.parse_args()
    directory = ROOT / "demo"
    if args.verify:
        demo = read_demo(directory)
        assert [sample["screen"]["status"] for sample in demo["samples"]] == ["conditional_comparison", "conditional_comparison", "outside_model_scope", "numerical_failure"]
        assert demo["physical_qualification"] == "unqualified"
        print(json.dumps({"passed": True, "archive": demo["archive"], "samples": [
            {"id": point["id"], "screen": point["screen"], "input_sha256": [point[key]["input_sha256"] for key in ("reference", "candidate")]}
            for point in demo["samples"]]}, indent=2))
        return
    protocol_bytes = (directory / "protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    source = (ROOT / "examples" / protocol["footprint"]).read_text()
    identities = {"model.py": MODEL_SOURCE_SHA256, "solver.py": SOLVER_SOURCE_SHA256}
    if any(hashlib.sha256((ROOT/"soldershape"/name).read_bytes()).hexdigest() != digest for name, digest in identities.items()):
        raise ValueError("Numerical files differ from the loaded code. Restart before recording.")
    results = []
    for key, (spec, footprint) in demo_requests(protocol, source).items():
        try:
            result = solve(spec)
        except SolverError as error:
            result = {"input": spec.to_dict(), "input_sha256": spec.sha256,
                      "status": "failed", "error": str(error), "evidence": error.evidence}
        results.append({**result, "footprint": footprint, "design": key})
        print(key, results[-1]["status"], flush=True)
    for name, digest in identities.items():
        if hashlib.sha256((ROOT/"soldershape"/name).read_bytes()).hexdigest() != digest:
            raise ValueError("Numerical source changed during recording. Restart and record again.")
    with zipfile.ZipFile(io.BytesIO(make_bundle(results, source))) as archive:
        files = {name: archive.read(name) for name in archive.namelist() if name != "manifest.json"}
        manifest = json.loads(archive.read("manifest.json"))
    files["demo-protocol.json"] = protocol_bytes
    files["demo-recording.json"] = json_bytes(identities)
    files["THIRD_PARTY.md"] = (ROOT/"THIRD_PARTY.md").read_bytes()
    files["KICAD-LICENSE.md"] = (ROOT/"examples/KICAD-LICENSE.md").read_bytes()
    files["footprint-provenance.json"] = (ROOT/"examples/provenance.json").read_bytes()
    manifest["replay"] = "python3 tools/verify_demo.py FILE.zip --replay; includes a retained numerical failure, not seven numerical successes"
    for name in identities:
        files["calculation-source/"+name] = (ROOT/"soldershape"/name).read_bytes()
    manifest["files"] = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
    files["manifest.json"] = json_bytes(manifest)
    output = directory/"data/stress-cases.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    identity = {"archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
                "calculation_code_sha256": identities,
                "recording_method": "Fresh seven-case native computation",
                "physical_qualification": "unqualified"}
    (directory/"recording.json").write_bytes(json_bytes(identity))
    read_demo(directory)
    print(json.dumps(identity, indent=2))


if __name__ == "__main__":
    main()
