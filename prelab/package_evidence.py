"""Preserve a generated evidence directory in a deterministic, hashed archive."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def package(source, archive):
    manifest = archive.with_name(archive.name + ".manifest.json")
    if archive.exists() or manifest.exists():
        raise ValueError("Use a new archive path. Existing evidence is preserved.")
    inventory = {}
    license_bytes = (Path(__file__).resolve().parents[1] / "LICENSE").read_bytes()
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|") as destination:
                for path in sorted(source.rglob("*")):
                    if path.is_symlink():
                        raise ValueError("Evidence archives require regular files, not symbolic links.")
                    if not path.is_file():
                        continue
                    name = str(path.relative_to(source))
                    with path.open("rb") as stream:
                        inventory[name] = hashlib.file_digest(stream, "sha256").hexdigest()
                    info = destination.gettarinfo(str(path), arcname=name)
                    info.mtime = info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with path.open("rb") as stream:
                        destination.addfile(info, stream)
                if "PROJECT-LICENSE.txt" in inventory:
                    raise ValueError("Evidence already uses the reserved project notice name.")
                info = tarfile.TarInfo("PROJECT-LICENSE.txt")
                info.size = len(license_bytes)
                destination.addfile(info, io.BytesIO(license_bytes))
                inventory[info.name] = hashlib.sha256(license_bytes).hexdigest()
    result = {"archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
              "archive_bytes": archive.stat().st_size, "files": inventory,
              "project_license_scope": "Original SolderShape code only. User inputs and third-party materials retain their own terms.",
              "scope": "Byte-preserving evidence archive. No digital signature or physical qualification."}
    manifest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"members": len(inventory), "bytes": result["archive_bytes"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    package(args.source.resolve(), args.archive.resolve())
