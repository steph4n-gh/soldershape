import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

from .artifacts import read_bundle, screen_pair
from .model import InputError, import_footprint, parse_case, request_from_footprint

ROOT = Path(__file__).resolve().parents[1]


def demo_requests(protocol, source):
    if protocol["schema"] != "soldershape.extreme-demo.v1" or len(protocol["records"]) != 7:
        raise InputError("Unsupported demo protocol.")
    records = {}
    for record in protocol["records"]:
        key = record["id"]
        if key in records:
            raise InputError("Duplicate demo record.")
        parameters = {**protocol["parameters"], **{name: record[name] for name in ("volume_mm3", "offset_mm", "standoff_mm")}}
        records[key] = request_from_footprint(source, protocol["pad_index"], parameters)
    return records


def demo_archive(directory=ROOT / "demo"):
    directory = Path(directory)
    identity = json.loads((directory / "recording.json").read_bytes())
    archive_bytes = (directory / "data/stress-cases.zip").read_bytes()
    if hashlib.sha256(archive_bytes).hexdigest() != identity["archive_sha256"]:
        raise InputError("Demo archive differs from its recording identity.")
    return archive_bytes, identity


def read_demo(directory=ROOT / "demo"):
    directory = Path(directory)
    archive_bytes, identity = demo_archive(directory)
    protocol_bytes = (directory / "protocol.json").read_bytes()
    if hashlib.sha256(protocol_bytes).hexdigest() != identity["protocol_sha256"]:
        raise InputError("Demo protocol differs from its recording identity.")
    protocol = json.loads(protocol_bytes)
    with tempfile.TemporaryDirectory(prefix="soldershape-recording-") as temporary:
        snapshot = Path(temporary) / "recording.zip"
        snapshot.write_bytes(archive_bytes)
        cases = read_bundle(snapshot)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        source = archive.read("source.kicad_mod").decode()
        if json.loads(archive.read("demo-recording.json")) != identity["calculation_code_sha256"]:
            raise InputError("Demo calculation source identity differs from its archive.")
        if archive.read("demo-protocol.json") != protocol_bytes:
            raise InputError("Archived demo protocol differs from the inspected protocol.")
        for name, digest in identity["calculation_code_sha256"].items():
            if hashlib.sha256(archive.read("calculation-source/"+name)).hexdigest() != digest:
                raise InputError("Archived demo source differs from its recorded identity.")
    expected = demo_requests(protocol, source)
    if len(cases) != len(expected):
        raise InputError("Demo cases do not match the recording protocol.")
    results = {}
    for (key, (spec, footprint)), (saved_spec, row) in zip(expected.items(), cases, strict=True):
        if spec != saved_spec or row.get("footprint") != footprint:
            raise InputError("Demo result differs from its protocol or source footprint.")
        results[key] = row
    samples = []
    for point in protocol["samples"]:
        reference, candidate = results[point["reference"]], results[point["candidate"]]
        parameters = dict(candidate["input"])
        del parameters["lower_diameter_mm"]
        baseline = {name: reference["input"][name] for name in ("upper_diameter_mm", "volume_mm3")} if point["kind"] == "volume_comparison" else None
        editable = parse_case({"schema": "soldershape.case.v1", "footprint_text": source,
                               "pad_index": protocol["pad_index"], "parameters": parameters, "baseline": baseline})
        samples.append({**{key: point[key] for key in ("id", "label", "kind")},
                        "reference": reference, "candidate": candidate,
                        "screen": screen_pair(reference, candidate), "editable_case": editable})
    return {"title": protocol["title"], "question": protocol["question"], "recorded": True,
            "physical_qualification": "unqualified", "archive": {"url": "/demo/evidence.zip", "sha256": identity["archive_sha256"], "case_count": len(cases)},
            "footprint": import_footprint(source), "selected_pad_index": protocol["pad_index"], "pitch_mm": protocol["pitch_mm"],
            "assumptions": protocol["assumptions"], "baseline": protocol["baseline"], "samples": samples}
