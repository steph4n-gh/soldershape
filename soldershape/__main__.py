"""Local browser workbench and repeatable command-line runs."""

import argparse
import base64
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import secrets
import sys
import threading
import traceback
import zipfile
from urllib.parse import urlsplit
from urllib.request import urlopen

from .artifacts import make_bundle, read_bundle
from .model import InputError, import_footprint, parse_case, request_from_footprint


ROOT = Path(__file__).resolve().parents[1]
WEB = Path(__file__).resolve().parent / "web"


def normalize_case(data):
    case = parse_case(data)
    if len((json.dumps(case, indent=2) + "\n").encode()) > 2_100_000:
        raise InputError("The formatted editable case exceeds 2.1 MB. Use a smaller footprint.")
    return case


def calculate(source, index, parameters, offsets=None):
    from .solver import SolverError, solve
    spec, footprint = request_from_footprint(source, index, parameters)
    points = [spec]
    if offsets is not None:
        if not isinstance(offsets, list) or not 1 <= len(offsets) <= 7:
            raise InputError("Choose one to seven sweep offsets.")
        points = [replace(spec, offset_mm=offset) for offset in offsets]
    results = []
    for point in points:
        try:
            result = solve(point)
        except SolverError as error:
            result = {"input": point.to_dict(), "input_sha256": point.sha256, "status": "failed",
                      "error": str(error), "evidence": getattr(error, "evidence", {})}
        result["footprint"] = footprint
        results.append(result)
    return results


def calculate_comparison(case):
    if case["baseline"] is None:
        raise InputError("Set a reference design before comparing.")
    results = []
    for role, parameters in (("Reference", {**case["parameters"], **case["baseline"]}), ("Candidate", case["parameters"])):
        result = calculate(case["footprint_text"], case["pad_index"], parameters)[0]
        result["design"] = role
        results.append(result)
    offset = case["parameters"]["offset_mm"]
    checked = all(result["status"] == "refinement_checked" for result in results)
    scope_clear = not any(result.get("model_warnings") for result in results)
    loaded = "normal_load_uN" in case["parameters"]
    comparable = checked and (offset != 0 or loaded) and scope_clear
    designs = []
    for result in results:
        forces = result.get("forces", {})
        lateral = forces.get("x_uN")
        designs.append({"role": result["design"], "input_sha256": result["input_sha256"],
                        "upper_diameter_mm": result["input"]["upper_diameter_mm"], "volume_mm3": result["input"]["volume_mm3"],
                        "gap_mm": result.get("equilibrium", result["input"]).get("standoff_mm"),
                        "status": result["status"], "force_x_uN": lateral, "force_z_uN": forces.get("z_uN"),
                        "restoring_force_uN": -math.copysign(1, offset)*lateral if lateral is not None and offset != 0 else None})
    reference, candidate = designs
    condition = "supported normal load" if loaded else "prescribed wetted-plane gap"
    comparison = {"status": "compared" if comparable else "inconclusive", "designs": designs,
                  "scope": f"Both designs use the current board pad, {condition}, offset and material. Predictions assume pinned circular rims and an isolated joint. Process-specific accuracy, alignment time and manufacturing yield are not qualified."}
    if comparable:
        comparison["delta"] = {"volume_mm3": candidate["volume_mm3"]-reference["volume_mm3"],
                               "volume_percent": (candidate["volume_mm3"]/reference["volume_mm3"]-1)*100,
                               "restoring_force_uN": candidate["restoring_force_uN"]-reference["restoring_force_uN"] if offset != 0 else None,
                               "gap_mm": candidate["gap_mm"]-reference["gap_mm"],
                               "vertical_force_uN": candidate["force_z_uN"]-reference["force_z_uN"]}
    else:
        if not checked:
            comparison["reason"] = "Both designs must pass numerical checks."
        elif not scope_clear:
            comparison["reason"] = "A surface extends beyond the pad planes. Substrate clearance is unknown in this model."
        else:
            comparison["reason"] = "Use a nonzero offset to compare centering force."
    return results, comparison


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address):
        super().__init__(address, Handler)
        self.token = secrets.token_urlsafe(32)
        self.computation = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *_args):
        pass

    def respond(self, status, data, content_type="application/json; charset=utf-8"):
        if not isinstance(data, bytes):
            data = json.dumps(data, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)

    def same_origin(self):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        return host in hosts and (origin is None or origin == "http://" + host)

    def do_GET(self):
        if not self.same_origin():
            self.respond(403, {"error": "Use this workbench's loopback address."})
            return
        path = urlsplit(self.path).path
        if path == "/api/bootstrap":
            from .solver import engine_info
            example = (ROOT / "examples" / json.loads((ROOT / "examples/provenance.json").read_text())["filename"])
            self.respond(200, {"application": "SolderShape", "token": self.server.token, "engine": engine_info(),
                               "example": {"filename": example.name, "text": example.read_text()}})
            return
        if path == "/api/study/example":
            self.respond(200, json.loads((ROOT / "examples/coupon-planning.study.json").read_text()))
            return
        assets = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
                  "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css"),
                  "/study": ("study.html", "text/html"), "/study.js": ("study.js", "text/javascript"),
                  "/study.css": ("study.css", "text/css")}
        if path not in assets:
            self.respond(404, {"error": "Not found."})
            return
        filename, content_type = assets[path]
        self.respond(200, (WEB / filename).read_bytes(), content_type + "; charset=utf-8")

    def do_POST(self):
        if not self.same_origin() or not secrets.compare_digest(self.headers.get("X-SolderShape-Token", ""), self.server.token):
            self.respond(403, {"error": "Reload the workbench to establish a local session."})
            return
        path = urlsplit(self.path).path
        if path not in {"/api/import", "/api/case", "/api/solve", "/api/sweep", "/api/compare", "/api/study", "/api/study/case"}:
            self.respond(404, {"error": "Unknown operation."})
            return
        if self.headers.get_content_type() != "application/json":
            self.respond(415, {"error": "Send application/json."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            limit = 4_300_000 if path in {"/api/study", "/api/study/case"} else 2_100_000
            if not 0 < length <= limit:
                raise InputError(f"Request body must be between 1 byte and {limit/1_000_000:g} MB.")
            body = json.loads(self.rfile.read(length), parse_constant=lambda value: (_ for _ in ()).throw(InputError("Non-finite JSON numbers are not accepted.")))
            if not isinstance(body, dict):
                raise InputError("Expected a JSON object.")
            if path == "/api/import":
                if set(body) != {"footprint_text"}:
                    raise InputError("Request fields do not match this operation.")
                self.respond(200, {"footprint": import_footprint(body["footprint_text"])})
                return
            if path in {"/api/study", "/api/study/case"}:
                from .study import bundle_study, read_study, run_study
                study = read_study(body)
                if path == "/api/study/case":
                    self.respond(200, {"study": study})
                    return
                if not self.server.computation.acquire(blocking=False):
                    self.respond(409, {"error": "Another computation is running. Wait for it to finish."})
                    return
                try:
                    report = run_study(study)
                    bundle = bundle_study(report)
                    self.respond(200, {"report": report, "bundle_base64": base64.b64encode(bundle).decode(),
                                       "bundle_filename": "soldershape-design-study.zip"})
                finally:
                    self.server.computation.release()
                return
            if path in {"/api/case", "/api/compare"}:
                case = normalize_case(body)
                if path == "/api/case":
                    self.respond(200, {"case": case, "footprint": import_footprint(case["footprint_text"])})
                    return
                if case["baseline"] is None:
                    raise InputError("Set a reference design before comparing.")
            else:
                required = {"footprint_text", "pad_index", "parameters"}
                if path == "/api/sweep":
                    required.add("offsets_mm")
                if not required <= set(body) or set(body) - required - {"baseline"}:
                    raise InputError("Request fields do not match this operation.")
                case = normalize_case({"schema": "soldershape.case.v1", "footprint_text": body["footprint_text"],
                                   "pad_index": body["pad_index"], "parameters": body["parameters"], "baseline": body.get("baseline")})
            if not self.server.computation.acquire(blocking=False):
                self.respond(409, {"error": "Another computation is running. Wait for it to finish."})
                return
            try:
                comparison = None
                if path == "/api/compare":
                    results, comparison = calculate_comparison(case)
                else:
                    results = calculate(case["footprint_text"], case["pad_index"], case["parameters"], body.get("offsets_mm"))
                bundle = make_bundle(results, case["footprint_text"], case, comparison)
                self.respond(200, {"results": results, "bundle_base64": base64.b64encode(bundle).decode(),
                                   "comparison": comparison,
                                   "bundle_filename": {"/api/sweep": "soldershape-sweep.zip", "/api/compare": "soldershape-comparison.zip"}.get(path, "soldershape-case.zip")})
            finally:
                self.server.computation.release()
        except (InputError, ValueError, UnicodeError) as error:
            self.respond(400, {"error": str(error)})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            traceback.print_exc()
            self.respond(500, {"error": "The computation failed unexpectedly. Details are in the local terminal."})


def replay(path):
    from .solver import SolverError, solve
    cases = read_bundle(path)
    with zipfile.ZipFile(path) as archive:
        if "study.json" in archive.namelist():
            from .study import replay_study
            report = replay_study(path)
            print(json.dumps(report, indent=2))
            return 0 if report["passed"] else 1
    checks = []
    for spec, saved in cases:
        try:
            current = solve(spec)
        except SolverError as error:
            checks.append({"input_sha256": spec.sha256, "previous_status": saved["status"],
                           "current_status": "failed", "error": str(error), "passed": False})
            continue
        if current["status"] == "failed":
            checks.append({"input_sha256": spec.sha256, "previous_status": saved["status"],
                           "current_status": "failed", "error": current.get("error", "Solver failed."), "passed": False})
            continue
        if saved["status"] == "failed":
            checks.append({"input_sha256": spec.sha256, "previous_status": "failed", "current_status": current["status"], "passed": False})
            continue
        force_scale = spec.surface_tension_n_m * spec.lower_diameter_mm * 500
        differences = {axis: abs(current["forces"][axis] - saved["forces"][axis]) for axis in ("x_uN", "z_uN")}
        passed = current["status"] == saved["status"] and all(
            differences[axis] <= max(abs(saved["forces"][axis]) * .01, force_scale * .0001)
            for axis in differences)
        gap_difference = None
        if "normal_load_uN" in spec.to_dict():
            gap_difference = abs(current["equilibrium"]["standoff_mm"] - saved["equilibrium"]["standoff_mm"])
            passed = passed and gap_difference <= max(1e-5, saved["equilibrium"]["standoff_mm"]*.001)
            passed = passed and current["load_balance"]["status"] == saved["load_balance"]["status"]
        checks.append({"input_sha256": spec.sha256, "status": current["status"], "force_difference_uN": differences,
                       "gap_difference_mm": gap_difference,
                       "source_matches": bool(current["engine"].get("source_sha256")) and current["engine"].get("source_sha256") == saved["engine"].get("source_sha256"),
                       "binary_matches": bool(current["engine"].get("binary_sha256")) and current["engine"].get("binary_sha256") == saved["engine"].get("binary_sha256"), "passed": passed})
    print(json.dumps({"replay": checks, "passed": all(row["passed"] for row in checks),
                      "verification_kind": "numerical_equivalence",
                      "exact_engine_provenance": all(row.get("source_matches") and row.get("binary_matches") for row in checks),
                      "scope": "Passing numerical replay does not establish matching engine identity or physical accuracy."}, indent=2))
    return 0 if all(row["passed"] for row in checks) else 1


def main():
    parser = argparse.ArgumentParser(prog="python3 -m soldershape", description="Local KiCad solder-joint equilibrium workbench.")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Open the loopback browser workbench.")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--open", action="store_true", help="Open the workbench in your default browser.")
    pads = sub.add_parser("pads", help="Inspect supported pads in a footprint.")
    pads.add_argument("footprint", type=Path)
    command = sub.add_parser("solve", help="Compute a footprint pad and export a reproducible ZIP.")
    command.add_argument("footprint", type=Path)
    command.add_argument("--pad", default="A1")
    command.add_argument("--parameters", type=Path, default=ROOT / "examples" / "parameters.json")
    command.add_argument("--offsets", help="Comma-separated offsets in millimeters. Use --offsets=-0.02,0,0.02.")
    command.add_argument("--output", type=Path, default=ROOT / "output" / "soldershape-case.zip")
    command = sub.add_parser("replay", help="Verify a bundle and recompute trusted inputs.")
    command.add_argument("bundle", type=Path)
    command = sub.add_parser("solve-case", help="Recompute an editable case or its reference comparison.")
    command.add_argument("case", type=Path)
    command.add_argument("--output", type=Path, default=ROOT / "output" / "soldershape-case.zip")
    command = sub.add_parser("study", help="Compare two board revisions and export a decision study.")
    command.add_argument("study", type=Path)
    command.add_argument("--output", type=Path, default=ROOT / "output" / "soldershape-design-study.zip")
    args = parser.parse_args()
    try:
        if args.command == "serve":
            try:
                server = Server(("127.0.0.1", args.port))
            except OSError:
                if not args.open:
                    raise
                url = f"http://127.0.0.1:{args.port}"
                try:
                    with urlopen(url + "/api/bootstrap", timeout=2) as response:
                        existing = json.loads(response.read(2_100_000))
                    if not isinstance(existing, dict) or existing.get("application") != "SolderShape":
                        raise ValueError("The port belongs to another application.")
                except (OSError, ValueError) as error:
                    raise InputError(f"Port {args.port} is occupied. Choose another port with --port.") from error
                import webbrowser
                webbrowser.open(url)
                print(f"Opened the existing SolderShape workbench at {url}")
                return 0
            print(f"SolderShape at http://127.0.0.1:{server.server_port}", flush=True)
            print("Pinned circular pads. Numerical checks do not qualify physical accuracy.", flush=True)
            if args.open:
                import webbrowser
                webbrowser.open(f"http://127.0.0.1:{server.server_port}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return 0
        if args.command == "pads":
            print(json.dumps(import_footprint(args.footprint.read_text()), indent=2))
            return 0
        if args.command == "replay":
            return replay(args.bundle)
        if args.command == "study":
            from .study import bundle_study, run_study
            if args.study.stat().st_size > 4_300_000:
                raise InputError("Design studies are limited to 4.3 MB.")
            report = run_study(json.loads(args.study.read_text()))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(bundle_study(report))
            print(json.dumps({"decision": report["decision"], "nominal": report["nominal"],
                              "physical_qualification": report["physical_qualification"],
                              "output": str(args.output.resolve())}, indent=2))
            return 1 if report["decision"]["status"] in {"numerical_failure", "model_scope_inconclusive"} else 0
        if args.command == "solve-case":
            if args.case.stat().st_size > 2_100_000:
                raise InputError("Editable cases are limited to 2.1 MB.")
            case = normalize_case(json.loads(args.case.read_text()))
            comparison = None
            if case["baseline"] is not None:
                results, comparison = calculate_comparison(case)
            else:
                results = calculate(case["footprint_text"], case["pad_index"], case["parameters"])
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(make_bundle(results, case["footprint_text"], case, comparison))
            print(json.dumps({"results": [{key: row[key] for key in ("design", "input", "equilibrium", "load_balance", "status", "forces", "error") if key in row} for row in results],
                              "comparison": comparison, "output": str(args.output.resolve())}, indent=2))
            return 0 if all(row["status"] == "refinement_checked" for row in results) else 1
        source = args.footprint.read_text()
        footprint = import_footprint(source)
        candidates = [p["index"] for p in footprint["pads"] if p["identifier"] == args.pad]
        if len(candidates) != 1:
            raise InputError("The pad label must match exactly one pad. Use the browser for duplicate labels.")
        parameters = json.loads(args.parameters.read_text())
        offsets = [_number_offset(x) for x in args.offsets.split(",")] if args.offsets else None
        results = calculate(source, candidates[0], parameters, offsets)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(make_bundle(results, source))
        for result in results:
            print(json.dumps({k: result[k] for k in ("input", "equilibrium", "load_balance", "status", "forces", "diagnostics", "error") if k in result}, indent=2))
        print(str(args.output.resolve()))
        return 0 if all(row["status"] == "refinement_checked" for row in results) else 1
    except (OSError, InputError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


def _number_offset(value):
    offset = float(value)
    if not math.isfinite(offset):
        raise InputError("Offsets must be finite.")
    return offset


if __name__ == "__main__":
    sys.exit(main())
