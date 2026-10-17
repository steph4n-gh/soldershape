# Rebuild the attributed board context

Run these commands from `/Volumes/Storage/oct16project`. Docker must have the pinned KiCad image available.

```sh
python3 board_demo/tools/extract.py
python3 board_demo/tools/verify_native.py
```

The extractor runs KiCad 10.0.6 with network access disabled. It reads the original board from a temporary copy. It writes normalized standalone footprints, the front copper and silkscreen SVG, `context.json`, and a file manifest. The verifier independently reloads the original source and checks all component and pad positions, sizes, net identities, import order, rotations, and support status.

A successful run prints `status` equal to `passed`, 235 components, 1177 pads, 5365 track objects, and 381 supported pads. The native receipt is `native-verification.json`. All 381 supported pads belong to U1. Front rectangular pads, through-hole pads, and all back-side pads remain inspect-only.

To check deterministic output, run the extractor twice and compare the complete manifest.

```sh
cp board_demo/manifest.json output/board-native-manifest-before.json
python3 board_demo/tools/extract.py
cmp output/board-native-manifest-before.json board_demo/manifest.json
```

The final command exits with code 0 and produces no output when every retained artifact matches. KiCad's generated standalone UUID records and the SVG title timestamp are removed. Original source UUIDs remain in the component context. The original source files remain byte-for-byte unchanged.

Use the cached image below if you need to identify the runtime.

```text
kicad/kicad@sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec
```

The board outline centerline is 93.98 by 50.8 mm at native board origin `[94.1, 61.42]` mm. KiCad's stroke-inclusive outline bounding box is larger. The SVG uses centerline dimensions, so its coordinates equal board coordinates minus that origin. The verifier checks every supported U1 circle against that mapping and reexports the complete native SVG independently for exact normalized byte comparison.

Standalone footprint coordinates have zero placement and zero rotation. KiCad converts back-side footprints to front-side library coordinates by reversing local Y. Their displayed board coordinates remain original native coordinates. The context records local +X in board coordinates. The verifier checks the side-aware transform on every pad, including rotated and back-side parts. Back-side computation remains disabled.

U1 pad J16 has importer index 173, net `SDRAM_D0`, local position `[4.4, -1.2]` mm, and board position `[142.88, 86.6]` mm. Its circular copper diameter is 0.4 mm. Its footprint declares a positive 0.05 mm mask margin. Actual board-level mask, upper package geometry, wetting, temperature, and assembly process remain unresolved.

`source/provenance.json` identifies the original ULX3S revision and source hashes. The modified MIT license requires the EMARD, RADIONA, and FER logos to remain unmodified and visible at their original locations on top silkscreen. The original board and its full native front silkscreen remain in this package. The source is used as attributed board context. The package supplies no ULX3S fabrication release or board-wide solder validation.
