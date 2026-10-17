import base64
import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

from . import model, solver
from .artifacts import json_bytes, make_bundle, mesh_obj, mesh_stl, read_bundle, results_csv
from .demo import screen_pair
from .model import InputError, import_footprint, parse_case, request_from_footprint

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "board_demo"
CODE_FILES = ("model.py", "solver.py", "board.py", "__main__.py", "artifacts.py", "demo.py")
LOADED_CODE_SHA256 = {name: hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in CODE_FILES}
LOADED_CODE_SHA256.update({"model.py": model.PYTHON_SOURCE_SHA256, "solver.py": solver.PYTHON_SOURCE_SHA256})
SCOPE = [
    "Only the selected isolated joint is computed. Board traces and other pads supply context.",
    "The board supplies lower copper geometry. Upper pad, gap, offset, solder volume and material are hypothetical process inputs until measured independently.",
    "Board mask rules, final CAM, wetting, contact-angle hysteresis, flux, oxide and neighboring joints are unresolved.",
    "Physical force accuracy remains unqualified. Numerical replay does not qualify self-alignment, bridging, package mechanics or assembly yield.",
    "The held-gap objective requires lateral restoration and no upward separating force. It is not a production volume recommendation.",
]


def _hash(content):
    return hashlib.sha256(content).hexdigest()


def _json(content):
    return json.loads(content, parse_constant=lambda value: (_ for _ in ()).throw(InputError("Non-finite JSON numbers are not accepted.")))


def _file(directory, name):
    if not isinstance(name, str) or not name or name.startswith("/") or ".." in name.split("/") or "\\" in name:
        raise InputError("Invalid board artifact path.")
    path = Path(directory)/name
    if not path.resolve().is_relative_to(Path(directory).resolve()):
        raise InputError("Board artifact leaves its context directory.")
    return path


def _code_sources():
    from . import __main__ as application
    sources = {name: (Path(__file__).parent/name).read_bytes() for name in CODE_FILES}
    loaded = {**LOADED_CODE_SHA256, "__main__.py": application.PYTHON_SOURCE_SHA256}
    if {name: _hash(data) for name, data in sources.items()} != loaded:
        raise InputError("Calculation source changed after loading. Restart before computing or exporting.")
    return sources


def read_board(directory=DIRECTORY):
    directory = Path(directory)
    try:
        manifest = _json((directory/"manifest.json").read_bytes())
        files = manifest.get("files")
        required = {"context.json", "source/ulx3s.kicad_pcb", "source/LICENSE.md", "source/provenance.json", "native-verification.json"}
        if not isinstance(files, dict) or not required <= set(files):
            raise InputError("Board extraction manifest is incomplete.")
        for name, identity in files.items():
            content = _file(directory, name).read_bytes()
            if not isinstance(identity, dict) or _hash(content) != identity.get("sha256") or len(content) != identity.get("bytes"):
                raise InputError("Board extraction integrity failed for "+name)
        context = _json((directory/"context.json").read_bytes())
        if context.get("schema") != "soldershape.board-context.v1":
            raise InputError("Unsupported board context.")
        source = context["source"]
        if _hash((directory/"source/ulx3s.kicad_pcb").read_bytes()) != source["board_sha256"]:
            raise InputError("Original board source differs from its context.")
        if _hash((directory/"source/LICENSE.md").read_bytes()) != source["license_sha256"]:
            raise InputError("Board license differs from its context.")
        svg = context["svg"]
        if files.get(svg["file"], {}).get("sha256") != svg["sha256"]:
            raise InputError("Board drawing identity differs from its manifest.")
        receipt = _json((directory/"native-verification.json").read_bytes())
        if (receipt.get("status") != "passed" or receipt.get("context_sha256") != _hash((directory/"context.json").read_bytes())
                or receipt.get("source_sha256") != source["board_sha256"] or receipt.get("svg_sha256") != svg["sha256"]
                or receipt.get("counts") != context["counts"]):
            raise InputError("Native board readback does not match the current extraction.")
        if (context["extraction"]["extractor_sha256"] != _hash((directory/"tools/extract.py").read_bytes())
                or receipt["verifier_sha256"] != _hash((directory/"tools/verify_native.py").read_bytes())):
            raise InputError("Native extraction tools changed. Rebuild and verify the board context.")
        references = set()
        for component in context["components"]:
            reference = component["reference"]
            if component["pads"] and reference in references:
                raise InputError("Duplicate board component reference.")
            if component["pads"]:
                references.add(reference)
            source_bytes = _file(directory, component["footprint_file"]).read_bytes()
            if _hash(source_bytes) != component["footprint_sha256"] or files.get(component["footprint_file"], {}).get("sha256") != component["footprint_sha256"]:
                raise InputError("Extracted footprint identity differs from its context.")
            if not component["pads"]:
                continue
            footprint = import_footprint(source_bytes.decode())
            if len(footprint["pads"]) != len(component["pads"]):
                raise InputError("Extracted pad count differs from the board context.")
            for expected, pad in zip(footprint["pads"], component["pads"], strict=True):
                if (expected["index"], expected["identifier"], [expected["x_mm"], expected["y_mm"]], expected["size_mm"], expected["shape"]) != (
                        pad["index"], pad["identifier"], pad["local_xy_mm"], pad["size_mm"], pad["shape"]):
                    raise InputError("Extracted pad geometry differs from the board context.")
                if pad["supported"] and (not expected["supported"] or component["side"] != "front"):
                    raise InputError("Board context promotes an unsupported pad.")
        return context
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as error:
        if isinstance(error, InputError):
            raise
        raise InputError("Invalid board extraction: "+str(error)) from error


def default_request(context):
    component = next((item for item in context["components"] if item["reference"] == "U1"), None)
    if component is None:
        raise InputError("The demonstration requires the identified U1 component.")
    supported = [pad for pad in component["pads"] if pad["supported"]]
    pad = next((item for item in supported if item["identifier"] == "J16"), supported[0] if supported else None)
    if pad is None:
        raise InputError("No supported U1 pad is available.")
    return {"schema": "soldershape.board-request.v1", "board_sha256": context["source"]["board_sha256"],
            "reference": "U1", "pad_index": pad["index"],
            "parameters": {"upper_diameter_mm": .4, "standoff_mm": .3, "volume_mm3": .056,
                           "offset_mm": .24, "surface_tension_n_m": .48, "density_g_cm3": 9, "gravity": True},
            "baseline": {"upper_diameter_mm": .4, "volume_mm3": .040}}


def board_case(request, context=None, directory=DIRECTORY):
    if not isinstance(request, dict) or set(request) != {"schema", "board_sha256", "reference", "pad_index", "parameters", "baseline"}:
        raise InputError("A board request must contain schema, board_sha256, reference, pad_index, parameters and baseline.")
    if request["schema"] != "soldershape.board-request.v1":
        raise InputError("Unsupported board request.")
    context = read_board(directory) if context is None else context
    if request["board_sha256"] != context["source"]["board_sha256"]:
        raise InputError("Selected board identity differs from the trusted extraction.")
    components = [item for item in context["components"] if item["reference"] == request["reference"]]
    if len(components) != 1:
        raise InputError("Select a component from the identified board.")
    component = components[0]
    index = request["pad_index"]
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(component["pads"]):
        raise InputError("Select a valid board pad index.")
    pad = component["pads"][index]
    if not pad["supported"]:
        raise InputError(pad["unsupported_reason"] or "This board pad is inspect-only.")
    parameters = request["parameters"]
    if not isinstance(parameters, dict) or "normal_load_uN" in parameters:
        raise InputError("This board comparison requires a prescribed wetted-plane gap.")
    source = _file(directory, component["footprint_file"]).read_text()
    case = parse_case({"schema": "soldershape.case.v1", "footprint_text": source, "pad_index": index,
                       "parameters": parameters, "baseline": request["baseline"]})
    if case["baseline"] is None:
        raise InputError("A board comparison requires a reference volume and upper diameter.")
    normalized = {**request, "parameters": case["parameters"], "baseline": case["baseline"]}
    selection = {**{name: context["source"][name] for name in ("repository", "commit", "board_sha256", "license_sha256")},
                 "reference": component["reference"], "value": component["value"], "component_uuid": component["uuid"],
                 "component_rotation_deg": component["rotation_deg"], "component_side": component["side"],
                 "footprint_file": component["footprint_file"], "footprint_sha256": component["footprint_sha256"],
                 "pad_index": index, "pad_identifier": pad["identifier"], "pad_net": pad["net"],
                 "lower_diameter_mm": pad["size_mm"][0], "local_xy_mm": pad["local_xy_mm"],
                 "board_xy_mm": pad["board_xy_mm"], "local_x_board": component["local_x_board"]}
    return normalized, selection, case


def _report(request, selection, case, results, code_hashes):
    from .__main__ import calculate_comparison
    if len(results) != 2:
        raise InputError("A board comparison contains exactly two cases.")
    for row, role, parameters in zip(results, ("Reference", "Candidate"), ({**case["parameters"], **case["baseline"]}, case["parameters"]), strict=True):
        spec, footprint = request_from_footprint(case["footprint_text"], case["pad_index"], parameters)
        if row.get("input") != spec.to_dict() or row.get("input_sha256") != spec.sha256 or row.get("footprint") != footprint or row.get("design") != role:
            raise InputError("Numerical results differ from their selected board pad or comparison request.")
    _, comparison = calculate_comparison(case, existing_results=results)
    return {"schema": "soldershape.board-report.v1", "request": request, "selection": selection,
            "editable_case": case, "results": results, "comparison": comparison,
            "screen": screen_pair(*results), "physical_qualification": "unqualified",
            "scope": SCOPE, "calculation_code_sha256": code_hashes}


def public_report(report):
    return {**report, "results": [{name: value for name, value in row.items() if name != "evidence"} for row in report["results"]]}


def run_board(request, directory=DIRECTORY):
    from .__main__ import calculate_comparison
    sources = _code_sources()
    normalized, selection, case = board_case(request, directory=directory)
    results, _ = calculate_comparison(case)
    if _code_sources() != sources:
        raise InputError("Calculation source changed during the comparison. Restart and recompute.")
    return _report(normalized, selection, case, results, {name: _hash(data) for name, data in sources.items()})


def bundle_board(report, directory=DIRECTORY):
    context = read_board(directory)
    normalized, selection, case = board_case(report["request"], context, directory)
    if report != _report(normalized, selection, case, report["results"], report["calculation_code_sha256"]):
        raise InputError("Board report differs from its regenerated selection and conclusions.")
    sources = _code_sources()
    if {name: _hash(data) for name, data in sources.items()} != report["calculation_code_sha256"]:
        raise InputError("Calculation source changed after computation. Recompute before export.")
    with zipfile.ZipFile(io.BytesIO(make_bundle(report["results"], case["footprint_text"], case, report["comparison"]))) as archive:
        files = {name: archive.read(name) for name in archive.namelist() if name != "manifest.json"}
        manifest = _json(archive.read("manifest.json"))
    files.update({"board-report.json": json_bytes(public_report(report)), "board-selection.json": json_bytes(selection),
                  "board-context.json": (Path(directory)/"context.json").read_bytes(),
                  "board-extraction-manifest.json": (Path(directory)/"manifest.json").read_bytes(),
                  "board-source.kicad_pcb": (Path(directory)/"source/ulx3s.kicad_pcb").read_bytes(),
                  "BOARD-LICENSE.md": (Path(directory)/"source/LICENSE.md").read_bytes(),
                  "board-source-provenance.json": (Path(directory)/"source/provenance.json").read_bytes()})
    receipt = Path(directory)/"native-verification.json"
    files["board-native-verification.json"] = receipt.read_bytes()
    files["board-extractor.py"] = (Path(directory)/"tools/extract.py").read_bytes()
    files["board-native-verifier.py"] = (Path(directory)/"tools/verify_native.py").read_bytes()
    files.update({"calculation-source/"+name: data for name, data in sources.items()})
    manifest.update(board_schema="soldershape.board-report.v1", replay="python3 tools/verify_board.py FILE.zip --replay; native board readback is separate from numerical replay",
                    files={name: _hash(data) for name, data in sorted(files.items())})
    files["manifest.json"] = json_bytes(manifest)
    if len(files) > 100 or sum(map(len, files.values())) > 160_000_000:
        raise InputError("Board evidence exceeds the existing numerical archive limits.")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 10, 16, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    if len(output.getvalue()) > 40_000_000:
        raise InputError("Board evidence exceeds the existing compressed archive limit.")
    return output.getvalue()


def response_payload(report, bundle, recorded=False):
    visible = public_report(report)
    visible["recorded"] = recorded
    return {"report": visible, "bundle_base64": base64.b64encode(bundle).decode(), "bundle_filename": "soldershape-board-comparison.zip"}


def verify_board(path, replay=False, directory=DIRECTORY):
    if Path(path).stat().st_size > 40_000_000:
        raise InputError("Bundle exceeds 40 MB.")
    content = Path(path).read_bytes()
    with tempfile.TemporaryDirectory(prefix="soldershape-board-") as temporary:
        snapshot = Path(temporary)/"evidence.zip"
        snapshot.write_bytes(content)
        cases = read_bundle(snapshot)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        saved = _json(archive.read("board-report.json"))
        source_hashes = saved["calculation_code_sha256"]
        if set(source_hashes) != set(CODE_FILES) or any(_hash(archive.read("calculation-source/"+name)) != digest for name, digest in source_hashes.items()):
            raise InputError("Archived calculation source differs from its recorded identity.")
        context = read_board(directory)
        if archive.read("board-context.json") != (Path(directory)/"context.json").read_bytes():
            raise InputError("Archived board context differs from trusted native extraction.")
        for archived, local in (("board-source.kicad_pcb", "source/ulx3s.kicad_pcb"), ("BOARD-LICENSE.md", "source/LICENSE.md"),
                                ("board-source-provenance.json", "source/provenance.json"), ("board-extraction-manifest.json", "manifest.json"),
                                ("board-native-verification.json", "native-verification.json"), ("board-extractor.py", "tools/extract.py"),
                                ("board-native-verifier.py", "tools/verify_native.py")):
            if archive.read(archived) != (Path(directory)/local).read_bytes():
                raise InputError("Archived board artifact differs from trusted extraction for "+archived)
        normalized, selection, case = board_case(saved["request"], context, directory)
        results = [row for _, row in cases]
        expected = _report(normalized, selection, case, results, source_hashes)
        if saved != expected:
            raise InputError("Archived report differs from its regenerated request, selected pad or conclusions.")
        for name, value in (("board-selection.json", selection), ("editable-case.json", case), ("comparison.json", saved["comparison"])):
            if archive.read(name) != json_bytes(value):
                raise InputError("Archived export differs from regenerated "+name)
        if archive.read("source.kicad_mod") != case["footprint_text"].encode() or archive.read("results.csv") != results_csv(results):
            raise InputError("Archived source or CSV differs from selected numerical results.")
        for index, row in enumerate(results):
            if "mesh" in row:
                for suffix, encoder in (("obj", mesh_obj), ("stl", mesh_stl)):
                    if archive.read(f"case-{index:02d}/mesh-mm.{suffix}") != encoder(row["mesh"]):
                        raise InputError("Archived mesh differs from exact solved vertices and triangles.")
    checks = []
    if replay:
        current = run_board(normalized, directory)
        for (spec, previous), fresh in zip(cases, current["results"], strict=True):
            passed = previous["status"] == fresh["status"] == "refinement_checked"
            differences = None
            source_matches = all(previous.get("engine", {}).get(key) and previous["engine"][key] == fresh.get("engine", {}).get(key)
                                 for key in ("source_sha256", "binary_sha256"))
            if passed:
                differences = {axis: abs(fresh["forces"][axis]-previous["forces"][axis]) for axis in ("x_uN", "z_uN")}
                scale = spec.surface_tension_n_m*spec.lower_diameter_mm*500
                passed = source_matches and previous.get("model_warnings") == fresh.get("model_warnings") and all(
                    difference <= max(abs(previous["forces"][axis])*.01, scale*.0001) for axis, difference in differences.items())
            checks.append({"input_sha256": spec.sha256, "previous_status": previous["status"], "current_status": fresh["status"],
                           "force_difference_uN": differences, "exact_engine_provenance": source_matches, "passed": passed})
        if current["screen"] != saved["screen"]:
            raise InputError("Native replay changes the conditional screen.")
    return {"passed": all(row["passed"] for row in checks), "integrity_verified": True, "selection_verified": True,
            "archive_sha256": _hash(content), "case_count": len(cases), "selection": selection,
            "screen": saved["screen"], "replayed": replay, "checks": checks, "physical_qualification": "unqualified",
            "verification_kind": "numerical_equivalence" if replay else "archive_binding_to_trusted_native_extraction",
            "native_board_readback": "Retained receipt verified by identity. Rerun board_demo/tools/verify_native.py for an independent native inspection."}


def recorded_board(directory=DIRECTORY):
    directory = Path(directory)
    identity = _json((directory/"recording.json").read_bytes())
    path = directory/"data/default-comparison.zip"
    content = path.read_bytes()
    if _hash(content) != identity["archive_sha256"]:
        raise InputError("Recorded board archive differs from its identity.")
    verified = verify_board(path, directory=directory)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        report = _json(archive.read("board-report.json"))
    if report["request"] != board_case(default_request(read_board(directory)), directory=directory)[0]:
        raise InputError("Recorded comparison differs from the displayed default request.")
    if identity["calculation_code_sha256"] != report["calculation_code_sha256"]:
        raise InputError("Board recording source identity differs from its archive.")
    return response_payload(report, content, recorded=True), verified
