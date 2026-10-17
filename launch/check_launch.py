"""Verify maintained docs, served evidence and the prepared media package."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website/dist"
sys.path.insert(0, str(ROOT))

from tools.prepare_launch_assets import CAPTURE, NOTICES, UI_COMMIT, example_files, read_walkthrough


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        for name in ("href", "src", "poster"):
            if name in attributes:
                self.references.append(attributes[name])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", type=Path, help="Actual browser-downloaded example wrapper")
    parser.add_argument("--base-url", help="Optional local preview origin for HTTP checks")
    parser.add_argument("--inventory", type=Path, default=ROOT / "launch/media-inventory.json")
    parser.add_argument("--receipt", type=Path, default=ROOT / "launch/checks.json")
    args = parser.parse_args()
    broken = []
    markdown = [ROOT / name for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "THIRD_PARTY.md",
                                         "board_demo/APP.md", "demo/README.md", "website/README.md", "launch/READINESS.md")]
    markdown += list((ROOT / "launch_sync").glob("*.md"))
    markdown += list((ROOT / "docs").rglob("*.md"))
    md_links = 0
    for path in markdown:
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            address = urlsplit(link.strip("<>"))
            if address.scheme or not address.path:
                continue
            md_links += 1
            if not (path.parent / unquote(address.path)).exists():
                broken.append([str(path.relative_to(ROOT)), link])
    pages = {}
    for path in SITE.rglob("*.html"):
        page = Page()
        page.feed(path.read_text())
        pages[path] = page
    site_targets = set()
    site_links = 0
    for path, page in pages.items():
        for link in page.references:
            address = urlsplit(link)
            if address.scheme or address.netloc:
                continue
            target = path.parent / unquote(address.path) if address.path else path
            target = target.resolve()
            if target.is_dir():
                target /= "index.html"
            site_links += 1
            site_targets.add(target)
            if not target.is_file():
                broken.append([str(path.relative_to(ROOT)), link])
            elif address.fragment and target in pages and address.fragment not in pages[target].ids:
                broken.append([str(path.relative_to(ROOT)), link])
    assert not broken, broken
    document, archives, verifications = read_walkthrough()
    inventory = json.loads(args.inventory.read_text())
    assert inventory["schema"] == "soldershape.launch-assets.v2"
    assert inventory["application_ui_commit"] == UI_COMMIT
    assert inventory["capture_manifest_sha256"] == sha(CAPTURE.read_bytes())
    assert inventory["source_capture"] == document["source_capture"]
    assert inventory["physical_qualification"] == "unqualified"
    assert inventory["scenarios"] == verifications
    assert json.loads((SITE / "media/walkthrough.json").read_bytes()) == document
    assert (SITE / "media/capture-manifest.json").read_bytes() == CAPTURE.read_bytes()
    actual = {str(path.relative_to(SITE / "media")) for path in (SITE / "media").rglob("*") if path.is_file()}
    assert actual == set(inventory["files"]), "The served media inventory has absent or additional files."
    for name, entry in inventory["files"].items():
        data = (SITE / "media" / name).read_bytes()
        assert len(data) == entry["bytes"] and sha(data) == entry["sha256"], name
    evidence_members = {}
    for identifier, archive in archives.items():
        folder = SITE / "media" / archive["folder"]
        extracted = {str(path.relative_to(folder)) for path in folder.rglob("*") if path.is_file()}
        assert extracted == set(archive["members"]), identifier
        for name, content in archive["members"].items():
            assert (folder / name).read_bytes() == content, name
        evidence_members[identifier] = len(extracted)
    for name, path in NOTICES.items():
        assert (SITE / "media" / name).read_bytes() == path.read_bytes(), name
    for name in document["source_capture"]["files"]:
        assert (SITE / "media" / name).read_bytes() == (ROOT / "docs/media" / name).read_bytes(), name
    captions = (SITE / "media/walkthrough.vtt").read_text()
    assert captions.startswith("WEBVTT")
    assert all(word in captions.lower() for word in ("300", "330", "still", "unqualified"))
    timing = re.findall(r"((?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s+-->\s+((?:\d{2}:)?\d{2}:\d{2}\.\d{3})", captions)
    intervals = []
    for start, end in timing:
        values = []
        for stamp in (start, end):
            seconds = 0.0
            for part in stamp.split(":"):
                seconds = seconds * 60 + float(part)
            values.append(seconds)
        intervals.append(values)
    duration = document["source_capture"]["duration_seconds"]
    assert intervals and intervals[0][0] == 0 and intervals[-1][1] == duration
    assert all(0 <= start < end <= duration for start, end in intervals)
    assert all(first[1] <= second[0] for first, second in zip(intervals, intervals[1:]))
    example = SITE / "media/soldershape-recorded-example.zip"
    expected_example = example_files(document, archives)
    with zipfile.ZipFile(example) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert len(archive.namelist()) == len(expected_example)
        assert set(archive.namelist()) == set(expected_example) == {"manifest.json", *manifest["sha256"]}
        for name, content in expected_example.items():
            assert archive.read(name) == content, name
        for name, digest in manifest["sha256"].items():
            assert sha(archive.read(name)) == digest, name
    if args.download:
        assert args.download.read_bytes() == example.read_bytes(), "Browser download differs"
    http = []
    if args.base_url:
        for path in sorted(site_targets | set(pages)):
            url = urljoin(args.base_url.rstrip("/") + "/", str(path.relative_to(SITE)))
            with urlopen(Request(url, method="HEAD"), timeout=10) as response:
                assert response.status == 200, url
                http.append(str(path.relative_to(SITE)))
    receipt = {"passed": True, "maintained_markdown_files": len(markdown), "markdown_local_links": md_links,
               "site_html_files": len(pages), "site_local_references": site_links, "broken_links": broken,
               "served_asset_hashes": len(inventory["files"]), "inner_evidence_members_match": evidence_members,
               "application_ui_commit": UI_COMMIT, "scenarios": verifications,
               "scenario_change": "held_wetted_plane_gap_only", "caption_intervals": intervals,
               "capture_manifest_sha256": sha(CAPTURE.read_bytes()), "inventory_sha256": sha(args.inventory.read_bytes()),
               "example_sha256": sha(example.read_bytes()), "actual_browser_download_matches": bool(args.download),
               "http_targets_passed": http, "physical_qualification": "unqualified"}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
