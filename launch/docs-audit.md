# Launch documentation audit

Audited the local checkout at `79170fc` on 2026-10-16. This is a read-only documentation review, apart from this report. No fresh installation, native recomputation, public deployment, or physical test was performed.

The engineering record is unusually thorough. The newcomer path is not ready to be the public front door. Publish an exploratory research workbench with explicit limits, after resolving the first-party license and separating the short user path from the research history. Do not launch a physically validated PCB design service.

## Fix before a public source release

| Priority | Finding | Smallest useful repair |
| --- | --- | --- |
| P0 | There is no root license for the first-party application. The only tracked `LICENSE` filename is the upstream ULX3S notice. `THIRD_PARTY.md` correctly limits its upstream redistribution claims. | The owner selects the first-party license and copyright holder. Add the exact text, identify its scope, and preserve all separate upstream notices. Do not describe the current checkout as open source before this is settled. |
| P0 | There is no configured Git remote. A public source URL, issue URL, download URL, release tag, and public source install command do not yet exist. | Create verified repository and release links only after those resources exist. Keep placeholders out of the public landing page. |
| P1 | `README.md` has 3,117 words and combines setup, product explanation, old experiments, numerical detail, lab planning, and project history. It has no visible screenshot. | Make the README the short front door. Include the user, outcome, one current image, supported scope, canonical local setup, one worked comparison, evidence export, physical status, and links to detailed guides. Keep the existing scientific record reachable. |
| P1 | Runtime links use four ports. README's opening Board section uses 8769, its default run path uses 8765, Board instructions use 8768, and Demo instructions use 8767. | Pick one documented default, preferably the CLI's existing 8765. Use route names in prose and show `--port` only as an explicit occupied-port alternative. Historical browser receipts should retain their original ports. |
| P1 | The README tells users to run from the project directory but has no source acquisition step. Some guides name the author's `/Volumes/Storage/oct16project` path. | After the repository exists, give an exact clone or source-download path. Replace author-specific paths in maintained guides with “repository root.” Do not rewrite original source bytes or historical receipts. |
| P1 | Scientific status is accurate but spread across many large reports. `PRODUCT_RELEASE.md` says “All 24 tests pass” for its historical release, while the current refinement records 94 tests. | Add one current status page that distinguishes numerical verification, limited published-height comparison, failed published-force qualification, and uncommissioned physical tests. Label `PRODUCT_RELEASE.md` as historical and link the latest verification. |
| P1 | There is no contributor guide or issue reporting route. | Add a concise contributor guide with current source map, exact checks, engine requirement, a restart-after-source-edit note, and a bug report checklist. Require exact inputs, input hash, engine identity, status, and a redacted evidence bundle. Explain that uploaded footprints and board files may be proprietary. |

## What the current code and commands establish

The ordinary application uses Python's standard library and browser assets. It does not need a runtime `pip install`. Native computation requires Python 3.12 or newer, a C compiler, `make`, and an initial network connection. `tools/setup_engine.py` downloads two hash-pinned upstream archives, compiles the headless engine, and records provenance. It rebuilds `.engine/src`, so describe it as setup rather than an inert diagnostic command.

The existing runtime is qualified on Apple Silicon macOS only. During this audit, Python reported 3.14.4, Apple clang reported 21.0.0, and `engine_info()` reported the pinned engine ready. Linux and Windows remain unqualified. Keep optional KiCad Docker, CadQuery, and PDF-generation environments in their own guides.

The following CLI paths were executed successfully for interface inspection.

```sh
python3 -m soldershape --help
python3 -m soldershape serve --help
python3 -m soldershape solve-case --help
python3 -m soldershape replay --help
python3 -m soldershape pads examples/BGA-36_3.396x3.466mm_Layout6x6_P0.4mm_Ball0.25mm_Pad0.2mm_NSMD.kicad_mod
```

The footprint command returned 36 pads and a supported circular A1 pad with a 0.2 mm diameter. This audit did not rerun setup or independently establish a clean machine installation. The current 94-test and native replay results come from the committed [second refinement evidence](../refinement2/RESULTS.md).

The source confirms that `serve` defaults to port 8765 and binds only to `127.0.0.1`. `Start SolderShape.command` checks Python, builds a missing engine, and requests `serve --open`. It opens `/board`. The service is a local workbench, not a public multi-user computation API.

## Give each reader a clear path

Keep these documents small and focused.

- The README introduces the product, actual value, current status, local setup, screenshot, and first comparison.
- A getting-started tutorial walks through the recorded Board comparison, a fresh calculation, the exact Board-to-Joint transfer, and readable review plus evidence export. State what users should see at each step. Recorded preview must remain distinct from fresh native computation.
- A model and validation reference states supported geometry, units, force conventions, numerical statuses, physical evidence, failures, and omitted effects. Link the full frozen research reports rather than duplicating their numbers everywhere.
- A contributor guide explains source ownership, focused tests, full suite, archive verification, and preservation of negative results. `python3 -m unittest discover -s tests -v` is the current application test command. `node cohesion/verify-ui-state.cjs` is a separate mocked storage and UI boundary check, not browser proof.
- A release checklist names the exact source revision, clean setup evidence, tested platform, current screenshots, downloadable archive hashes, third-party notices, current test and replay receipts, and unresolved blockers. One current release note links the preserved historical records.

Do not add a documentation framework, account system, new build pipeline, or cross-platform installation promise to solve these gaps.

## Screenshots and video

There are 20 tracked raster images and no tracked MP4, WebM, MOV, or GIF recordings. The current [Board review](../refinement2/board-review.png), [product view](../refinement2/product-refined.png), [supported-load view](../refinement2/loaded-review.png), and [narrow view](../refinement2/board-narrow.png) supply real material. They are evidence assets, but the README does not present them. Old workbench screenshots no longer represent the current product.

The minimum launch set is one current desktop image, one close view of the readable force comparison, and one supported-load or retained-failure image. Show the visible physical-status copy in at least one primary image. Keep the board authors' required logos and attribution intact. Use actual application captures rather than generated solder or hardware photography.

A short screen recording would help explain the value more than another feature page. A useful 60 to 90 second recording follows one task.

1. Locate U1 J16 on the attributed board and show which inputs are hypothetical.
2. Compare 40 and 56 nL at the declared held gap. Identify the weaker restoration and upward normal force in the larger-volume candidate.
3. Inspect the same joint without retyping its geometry. Show the matching unit cues.
4. Download the readable review and native evidence. Show the files and replay command.
5. End on the physical qualification status and the next measurement needed.

Do not imply whole-board simulation, measured forces, free package motion, or production approval. A video is useful launch material, not a prerequisite for a first source release if current images and the tutorial are clear.

## Public site and subdomain

A static product page on a dedicated `steph4n.dev` subdomain is a good fit for the current delivery. It can explain the workflow, show real screens, expose the numerical and physical status, and link source, setup, a recorded walkthrough, and an example evidence bundle. Choose the exact subdomain with the owner or use a clearly reported default.

Do not place localhost URLs in public calls to action. Do not present a static screenshot or animation as a live native solve. The Python service shells out to a native C engine, so a Cloudflare static deployment cannot host the existing computation path unchanged. A hosted interactive solver would need a separately justified runtime and resource policy. It does not belong in the minimum documentation launch.

## Link and asset checks

A local Markdown-target scan found no missing relative targets in `README.md`, `PRODUCT_RELEASE.md`, `refinement2/RESULTS.md`, `board_demo/APP.md`, `demo/README.md`, `force_lab/README.md`, `coupons/README.md`, and `THIRD_PARTY.md`. External URLs and fragment targets were not checked. The copied upstream `board_demo/source/README.md` has repository-root links that belong to its original project. Preserve its bytes and direct users through the maintained first-party Board guide.

The checkout has 998 tracked files and 177,470,123 tracked bytes. Much of that is retained numerical evidence. Preserve those records. A landing page should upload only its chosen static assets, not the full application tree, engine cache, lab handoff, or historical archives. A later release can provide a deliberately scoped source snapshot without erasing the scientific record.

## Release decision

The current product can support a candid exploratory research release after the first-party license, public repository identity, short newcomer path, and verified launch assets are resolved. Physical force qualification is not a gate for publishing bounded research software. It is a gate for selling its force output as trusted PCB manufacturing guidance. Keep that distinction on the README, site, tutorial, and exported example.
