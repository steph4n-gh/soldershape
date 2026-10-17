SolderShape is a local research workbench for comparing equilibrium solder-joint assumptions on an actual KiCad pad. Start with the [guided research preview](https://soldershape.steph4n.dev) and [getting-started guide](https://github.com/steph4n-gh/soldershape/blob/v0.4.0-preview.1/docs/getting-started.md).

The Board walkthrough compares 40 and 56 nL on ULX3S U1/J16 at 300 and 330 µm held gaps. It keeps source copper, hypothetical process inputs, numerical outcomes and required lab measurements together. Only the selected isolated joint is calculated.

Physical force accuracy remains unqualified. Published force discrepancies, wetting uncertainty, ranking reversals and numerical failures remain in the research record. This release does not establish production approval, self-alignment, bridging, yield or reliability.

Download the complete source package for the workbench, retained evidence and optional prebuilt lab files. The large package includes the force and height-coupon kits. Each kit is also attached separately for an outside-lab quotation. Both remain unqualified planning material. The 200 µm force fixture needs adaptation for the 400 µm Board question. The native engine binary and upstream C source are not redistributed.

From the extracted source root, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8765
```

Then open `http://127.0.0.1:8765/board`. Python 3.12 or newer, a C compiler and make are required. Native computation was exercised on Apple Silicon macOS. Hosted Ubuntu CI checks portable source boundaries, not native Linux operation or physical accuracy.

The exact release source passed hosted CI and all 41 portable checks in a fresh extraction. All 1,502 package members matched the release manifest. A fresh pinned engine replayed both 330 µm Board cases with zero force difference. These are numerical checks.

`SHA256SUMS` identifies the three attached ZIP or TAR packages. On macOS, verify downloaded packages with `shasum -a 256 -c SHA256SUMS` after placing all three in one directory. The complete archive also contains `RELEASE-MANIFEST.json` for every source member. Checksums establish integrity, not an independent signature.

Original SolderShape material uses MIT. Third-party boards, footprints and engine notices retain their own terms. See LICENSE and THIRD_PARTY.md in the source. Report vulnerabilities through [private GitHub reporting](https://github.com/steph4n-gh/soldershape/security/advisories/new).
