import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from soldershape.artifacts import json_bytes
from soldershape.board import bundle_board, default_request, read_board, run_board, verify_board
from soldershape.model import InputError


def main():
    parser = argparse.ArgumentParser(description="Verify selected board-pad binding and optionally replay two native cases.")
    parser.add_argument("archive", nargs="?", type=Path, default=ROOT/"board_demo/data/default-comparison.zip")
    parser.add_argument("--replay", action="store_true", help="Regenerate both requests and run the local pinned native engine.")
    parser.add_argument("--record", action="store_true", help="Compute and retain a fresh hypothetical default comparison.")
    args = parser.parse_args()
    try:
        if args.record:
            report = run_board(default_request(read_board()))
            content = bundle_board(report)
            args.archive.parent.mkdir(parents=True, exist_ok=True)
            args.archive.write_bytes(content)
            if args.archive.resolve() == (ROOT/"board_demo/data/default-comparison.zip").resolve():
                identity = {"schema": "soldershape.board-recording.v1", "archive_sha256": hashlib.sha256(content).hexdigest(),
                            "calculation_code_sha256": report["calculation_code_sha256"],
                            "recording_method": "Two fresh native calculations at the actual selected 400 micrometer copper pad with hypothetical process inputs.",
                            "physical_qualification": "unqualified"}
                (ROOT/"board_demo/recording.json").write_bytes(json_bytes(identity))
        result = verify_board(args.archive, replay=args.replay)
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    except (InputError, OSError, KeyError, TypeError, ValueError, zipfile.BadZipFile) as error:
        print(json.dumps({"passed": False, "error": str(error), "physical_qualification": "unqualified"}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
