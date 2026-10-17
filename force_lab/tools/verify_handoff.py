"""Inspect and smoke-test a force package from a new extracted directory."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from package_lab import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cad-python", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Use a new extraction directory.")
    content = args.archive.read_bytes()
    identity = verify(args.archive)
    if hashlib.sha256(content).hexdigest() != identity["archive_sha256"]:
        raise ValueError("Archive changed during verification.")
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        archive.extractall(args.output)
    commands = [[sys.executable, "force_lab/tools/analyze.py", "verify-plan", "force_lab/planning/native-120"],
                [sys.executable, "-m", "unittest", "discover", "-s", "force_lab/tests", "-v"]]
    if args.cad_python:
        commands.append([str(args.cad_python.absolute()), "force_lab/tools/verify_cad.py"])
    checks = []
    for index, command in enumerate(commands, 1):
        result = subprocess.run(command, cwd=args.output, capture_output=True, text=True)
        (args.output / f"handoff-check-{index}.log").write_text(result.stdout + result.stderr)
        checks.append({"command": command, "returncode": result.returncode, "passed": result.returncode == 0})
        if result.returncode:
            raise RuntimeError(f"Extracted check {index} failed. See {args.output}/handoff-check-{index}.log")
    report = {"package": identity, "checks": checks, "cad_readback_exercised": args.cad_python is not None,
              "engine_cache_present": (args.output / ".engine").exists(),
              "scope": "Static recorded-evidence verification, synthetic behavior controls and optional neutral CAD readback. No physical observations or fresh solver replay."}
    (args.output / "handoff-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
