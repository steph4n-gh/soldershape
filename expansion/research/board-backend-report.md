# Board binding and numerical evidence

The backend now binds an actual ULX3S pad to the existing isolated-joint comparison. It reuses the footprint importer, normalized editable case, native calculation, comparison, conditional screen, mesh export and numerical archive limits. No numerical model or solver source changed.

The trusted native extraction contains 235 components, 1,177 pads and 5,365 track objects. Its 381 supported pads belong to U1. Default selection U1 J16 is net SDRAM_D0, source copper diameter 0.4 mm, local position [4.4, -1.2] mm, board position [142.88, 86.6] mm and package-local +X board vector [1, 0]. Duplicate zero-pad logo references remain inspectable. Unsupported and back-side pads cannot become solve requests.

## Native result

Two fresh calculations use hypothetical opposing diameter 0.4 mm, held gap 0.3 mm, offset +0.24 mm, surface tension 0.48 N/m, density 9 g/cm³ and gravity enabled.

| Role | Volume | Fx | Fz | Vertices | Triangles | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Reference | 40 nL | -184.52638094190732 µN | -181.28387853829275 µN | 3,170 | 6,336 | refinement_checked |
| Candidate | 56 nL | -164.3854725452698 µN | +13.385897738397528 µN | 12,482 | 24,960 | refinement_checked |

Both have no model warning. The declared held-gap objective accepts lateral restoration without upward separation. The lower volume meets that conditional objective. These are numerical predictions from hypothetical process inputs. Existing physical force qualification remains unresolved.

Final retained default archive is `board_demo/data/default-comparison.zip`. Its SHA-256 is `1b87dca00de964b62cce902e071dad063b2f935f79d340817ff9e810bfff9604`. It contains 39 members and 5,697,470 compressed bytes. The original source board, license, source provenance, native context/manifest/receipt/tools, selected standalone footprint, editable case, two raw native results, OBJ/STL meshes and calculation sources share one flat archive. The old seven-case, 100-member and compressed/uncompressed limits remain unchanged.

Native replay matched both saved force components exactly, with differences 0.0 µN and matching native source/binary identities. The receipt is `output/board-replay.json`. This is numerical agreement, not a physical observation.

## Interface

- `GET /api/board` returns verified context, default request and recorded-preview availability.
- `GET /api/board/recorded` returns a verified recorded report and archive. Its normalized request must equal the current default request and trusted selected footprint.
- `GET /board/evidence.zip`, `/board/source.kicad_pcb`, `/board/license.txt` and `/board.svg` serve fixed paths.
- `POST /api/board/compare` validates the source identity, component, pad and process inputs, then uses the existing session token, same-origin guard and computation lock.
- `tools/verify_board.py` verifies binding, exact exported meshes and conclusions. `--replay` regenerates requests and executes the local engine. Generic `python3 -m soldershape replay` recognizes board evidence and dispatches to this verifier.

Every local manifest member is length/hash checked. The successful native receipt must match the current context/source/SVG/counts and current extractor/verifier bytes. Archived context and source must match that trusted extraction. Lower copper diameter and coordinates come from the trusted selected pad; client overrides and unsupported selections are rejected. Archive verification reads an immutable byte snapshot, enforces existing limits and never executes archived scripts.

## Root-cause repair from independent review

`screen_pair` previously assumed that the reference volume was always smaller and attributed every failed objective to an upward force. It now compares actual liquid volumes only when every other normalized input is equal. Comparisons that also change geometry use Reference/Candidate labels. An upward-force statement requires actual Fz greater than zero. Reversed real 40/56 nL records, an equal-volume different-upper-diameter control, and a zero-lateral/downward-force control cover these cases. Historical 5/7 nL headline behavior remains unchanged.

## Verification

Commands run from `/Volumes/Storage/oct16project`:

```sh
python3 tools/verify_board.py --record
python3 tools/verify_board.py --replay > output/board-replay.json
python3 -m unittest discover -s tests -p 'test_board*.py'
PYTHONPATH=tests python3 -m unittest test_board.BoardBinding.test_changed_loaded_calculation_source_blocks_new_computation test_board.BoardBinding.test_resealed_selection_source_context_mesh_and_conclusion_tampering_fail
python3 -m unittest discover -s tests -p 'test_cases.py'
python3 -m unittest discover -s tests -p 'test_demo.py'
git diff --check
```

The board suite passed nine tests in 8.758 seconds. The last added loaded-source guard and extended resealed-source tamper control passed in a separate two-test run. The current board suite contains ten tests. The legacy editable-case suite passed 12 tests in 0.878 seconds. The historical demo suite passed eight tests in 3.556 seconds. Python compilation and diff whitespace checks passed.

The first board-test attempt overlapped an active native rebuild. It failed closed because the transient manifest did not yet include its successful native receipt. That run had one failure and one setup error; no computational result or export was accepted. After the native owner finished and froze the manifest, the board suite and replay passed. This negative result is retained here rather than recast as successful verification.

The actual browser workflow and downloaded archive still require the root's independent UI verification. This report makes no claim that a browser was exercised by this backend agent.

## Remaining limits

The archive verifier binds this pinned board to the trusted local extraction. Native board readback is a separate geometric proof, and its receipt does not physically validate a solder joint. Stage interfaces, measured process inputs and held-out force observations belong to the force-lab workflow. KiCad remains a stronger general board viewer. The useful addition here is an identified, replayable force hypothesis without manually transcribing the board pad, not a board-wide assembly solver.
