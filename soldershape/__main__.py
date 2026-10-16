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
from urllib.parse import urlsplit

from .artifacts import make_bundle, read_bundle
from .model import InputError, import_footprint, request_from_footprint


ROOT = Path(__file__).resolve().parents[1]
WEB = Path(__file__).resolve().parent / "web"


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
            example = next((ROOT / "examples").glob("*.kicad_mod"))
            self.respond(200, {"token": self.server.token, "engine": engine_info(),
                               "example": {"filename": example.name, "text": example.read_text()}})
            return
        assets = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
                  "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css")}
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
        if path not in {"/api/import", "/api/solve", "/api/sweep"}:
            self.respond(404, {"error": "Unknown operation."})
            return
        if self.headers.get_content_type() != "application/json":
            self.respond(415, {"error": "Send application/json."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 2_100_000:
                raise InputError("Request body must be between 1 byte and 2.1 MB.")
            body = json.loads(self.rfile.read(length), parse_constant=lambda value: (_ for _ in ()).throw(InputError("Non-finite JSON numbers are not accepted.")))
            if not isinstance(body, dict):
                raise InputError("Expected a JSON object.")
            allowed = {"footprint_text"} if path == "/api/import" else {"footprint_text", "pad_index", "parameters"}
            if path == "/api/sweep":
                allowed.add("offsets_mm")
            if set(body) != allowed:
                raise InputError("Request fields do not match this operation.")
            if path == "/api/import":
                self.respond(200, {"footprint": import_footprint(body["footprint_text"])})
                return
            if not self.server.computation.acquire(blocking=False):
                self.respond(409, {"error": "Another computation is running. Wait for it to finish."})
                return
            try:
                results = calculate(body["footprint_text"], body["pad_index"], body["parameters"], body.get("offsets_mm"))
                bundle = make_bundle(results, body["footprint_text"])
                self.respond(200, {"results": results, "bundle_base64": base64.b64encode(bundle).decode(),
                                   "bundle_filename": "soldershape-sweep.zip" if path == "/api/sweep" else "soldershape-case.zip"})
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
    checks = []
    for spec, saved in read_bundle(path):
        try:
            current = solve(spec)
        except SolverError as error:
            checks.append({"input_sha256": spec.sha256, "previous_status": saved["status"],
                           "current_status": "failed", "error": str(error), "passed": False})
            continue
        if saved["status"] == "failed":
            checks.append({"input_sha256": spec.sha256, "previous_status": "failed", "current_status": current["status"], "passed": False})
            continue
        force_scale = spec.surface_tension_n_m * spec.lower_diameter_mm * 500
        differences = {axis: abs(current["forces"][axis] - saved["forces"][axis]) for axis in ("x_uN", "z_uN")}
        passed = current["status"] == saved["status"] and all(
            differences[axis] <= max(abs(saved["forces"][axis]) * .01, force_scale * .0001)
            for axis in differences)
        checks.append({"input_sha256": spec.sha256, "status": current["status"], "force_difference_uN": differences,
                       "source_matches": current["engine"].get("source_sha256") == saved["engine"].get("source_sha256"),
                       "binary_matches": current["engine"].get("binary_sha256") == saved["engine"].get("binary_sha256"), "passed": passed})
    print(json.dumps({"replay": checks, "passed": all(row["passed"] for row in checks)}, indent=2))
    return 0 if all(row["passed"] for row in checks) else 1


def main():
    parser = argparse.ArgumentParser(prog="python3 -m soldershape", description="Local KiCad solder-joint equilibrium workbench.")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Open the loopback browser workbench.")
    serve.add_argument("--port", type=int, default=8765)
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
    args = parser.parse_args()
    try:
        if args.command == "serve":
            server = Server(("127.0.0.1", args.port))
            print(f"SolderShape at http://127.0.0.1:{server.server_port}", flush=True)
            print("Fully wetted circular pads. Equilibrium model. No physical validation.", flush=True)
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
            print(json.dumps({k: result[k] for k in ("input", "status", "forces", "diagnostics", "error") if k in result}, indent=2))
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
