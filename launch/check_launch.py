"""Verify maintained docs, served evidence and the prepared media package."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website/dist"


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
    args = parser.parse_args()
    broken = []
    markdown = [ROOT / name for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "THIRD_PARTY.md",
                                         "board_demo/APP.md", "demo/README.md", "website/README.md", "launch/READINESS.md")]
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
    inventory = json.loads((ROOT / "launch/media-inventory.json").read_text())
    for name, entry in inventory["files"].items():
        data = (SITE / "media" / name).read_bytes()
        assert len(data) == entry["bytes"] and sha(data) == entry["sha256"], name
    with zipfile.ZipFile(ROOT / "refinement2/evidence/board-comparison.zip") as inner:
        for name in inner.namelist():
            assert (SITE / "media/evidence" / name).read_bytes() == inner.read(name), name
    example = SITE / "media/soldershape-recorded-example.zip"
    with zipfile.ZipFile(example) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert set(archive.namelist()) == {"manifest.json", *manifest["sha256"]}
        for name, digest in manifest["sha256"].items():
            assert sha(archive.read(name)) == digest
        assert sha(archive.read("board-comparison.zip")) == inventory["inner_archive_sha256"]
        assert archive.read("PROJECT-LICENSE.txt") == (ROOT / "LICENSE").read_bytes()
        assert archive.read("BOARD-LICENSE.md") == (ROOT / "board_demo/source/LICENSE.md").read_bytes()
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
               "served_asset_hashes": len(inventory["files"]), "inner_evidence_members_match": len(inner.namelist()),
               "example_sha256": sha(example.read_bytes()), "actual_browser_download_matches": bool(args.download),
               "http_targets_passed": http, "physical_qualification": "unqualified"}
    (ROOT / "launch/checks.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
