#!/usr/bin/env python3
"""Build the pinned upstream numerical engine for local evaluation."""

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / ".engine"
SOURCE_URL = "https://kenbrakke.com/evolver/downloads/evolver-2.70.tar.gz"
SOURCE_SHA256 = "be7d60d9eb690f1fb124e2ecc12237a7a35be1935bfa5e92be3fe912207a3b6b"
BGA_URL = "https://kenbrakke.com/evolver/downloads/bga-files.zip"
BGA_SHA256 = "96389e8200320cc8acfbf60b8ed23e2d05941613af5b55824c36890113c6e659"
SHIM = "void set_graphics_title(int which, char *title) { (void)which; (void)title; }\n"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url, expected, target):
    if target.exists() and digest(target) == expected:
        return
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "SolderShape/0.1 (local numerical evaluation)", "Accept": "*/*"}), timeout=60) as response, temporary.open("wb") as output:
            total = 0
            while block := response.read(1024 * 1024):
                total += len(block)
                if total > 40_000_000:
                    raise RuntimeError("Upstream archive exceeds the download limit.")
                output.write(block)
        if digest(temporary) != expected:
            raise RuntimeError("Upstream archive SHA-256 does not match the pinned source.")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def safe_path(root, name):
    destination = (root / name).resolve()
    if destination != root.resolve() and root.resolve() not in destination.parents:
        raise RuntimeError("Archive contains an unsafe path.")
    return destination


def extract_source(archive, root):
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        if sum(member.size for member in members) > 80_000_000:
            raise RuntimeError("Source archive exceeds extraction limit.")
        for member in members:
            safe_path(root, member.name)
            if not member.isfile() and not member.isdir():
                raise RuntimeError("Source archive contains a link or special file.")
        source.extractall(root, members=members, filter="data")


def extract_bga(archive, root):
    root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as source:
        if sum(item.file_size for item in source.infolist()) > 10_000_000:
            raise RuntimeError("BGA archive exceeds extraction limit.")
        for item in source.infolist():
            safe_path(root, item.filename)
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError("BGA archive contains a symbolic link.")
        source.extractall(root)


def main():
    ENGINE.mkdir(exist_ok=True)
    archive = ENGINE / "evolver-2.70.tar.gz"
    bga_archive = ENGINE / "bga-files.zip"
    download(SOURCE_URL, SOURCE_SHA256, archive)
    download(BGA_URL, BGA_SHA256, bga_archive)
    if (ENGINE / "src").exists():
        shutil.rmtree(ENGINE / "src")
    extract_source(archive, ENGINE)
    extract_bga(bga_archive, ENGINE / "bga")
    shim = ENGINE / "headless-title.c"
    shim.write_text(SHIM)
    compiler = shutil.which("cc")
    make = shutil.which("make")
    if not compiler or not make:
        raise RuntimeError("A C compiler and make are required. Install the platform command line developer tools.")
    commands = [
        [compiler, "-c", str(shim), "-o", str(ENGINE / "headless-title.o")],
        [make, "-C", str(ENGINE / "src"), "-j4", f"CC={compiler} -O2 -std=gnu89 -w", "CFLAGS=-DGENERIC", "GRAPH=nulgraph.o", "GRAPHLIB=../headless-title.o"],
    ]
    log = []
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True, timeout=180, env={**os.environ, "LC_ALL": "C"})
        log.append(result.stdout + result.stderr)
        (ENGINE / "build.log").write_text("\n".join(log))
        if result.returncode:
            raise RuntimeError("Engine build failed. See .engine/build.log.")
    binary = ENGINE / "src" / "evolver"
    metadata = {
        "version": "2.70a",
        "source_url": SOURCE_URL,
        "source_sha256": SOURCE_SHA256,
        "reference_url": BGA_URL,
        "reference_sha256": BGA_SHA256,
        "binary_sha256": digest(binary),
        "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
        "build_commands": commands,
        "numerical_source_modified": False,
        "patch": {"purpose": "Supply missing no-op title callback for the headless graphics target.", "source": SHIM, "sha256": digest(shim)},
        "license_note": "Local upstream evaluation. Component notices require review before redistribution; upstream source is not vendored in this project.",
    }
    (ENGINE / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"ready": True, **metadata}, indent=2))


if __name__ == "__main__":
    main()
