# Independent product review

The reviewed product changes have no remaining material correctness, security, or usability finding in the inspected scope. Two reproduced P2 defects and one minor display defect were repaired by the coordinator and independently checked again. This is a source and local HTTP/CLI review from a separate agent using the same model family. It is not a separate physical-validation verdict or a browser usability sign-off.

## Scope and behavior

The base is `fc384a0`. The scope is `soldershape/model.py`, `soldershape/__main__.py`, `soldershape/artifacts.py`, `soldershape/web/*`, `Start SolderShape.command`, and `tests/test_cases.py`.

An editable case contains its format version, footprint text, stable selected-pad index, current parameters, and an optional reference containing only upper-pad diameter and solder volume. The server validates and normalizes the whole case before accepting it. Saved inputs cannot supply forces, solver commands, executable code, the board-pad diameter, or independent reference conditions. Comparison recomputes both designs through the public solver under the same selected board pad, gap, offset, material, and gravity setting.

The browser validates an opened case before replacing its current draft. It does not load saved forces as fresh results. Parameter, pad, footprint, and reference changes invalidate displayed results and downloadable output. In-flight computation replies carry the initiating input revision and are discarded after an edit. This revision behavior was inspected in source; the coordinator owns the live browser checks.

## Findings and repairs

1. **P2, repaired. A saved case could exceed the browser's reopen limit.** The original case-open path rejected files above 2,000,000 bytes while the HTTP and CLI paths accepted 2,100,000 bytes. A valid 1,999,900-byte footprint produced a 2,000,209-byte formatted case. The server accepted it, but the browser's own open path rejected it. The repaired browser uses 2,100,000 bytes, and `normalize_case` rejects inputs whose formatted saved representation would exceed that limit. The same 2,000,209-byte case now saves and reopens exactly through live HTTP. The new large-case test passes.

2. **P2, repaired. Launching again did not reopen the workbench.** With an existing listener, the original `serve --open` returned exit code 2 with `[Errno 48] Address already in use` and never invoked the browser opener. The repaired path recognizes an existing SolderShape service through its bootstrap response and opens its URL. A live existing workbench returned exit code 0 with one browser-open call. A live foreign service returned exit code 2 with no browser-open call and kept its listening socket. The corresponding two tests pass.

3. **P3, repaired. A model warning repeated its category prefix.** Both the calculation result and browser renderer prepended `Model scope:`, producing a duplicate label. The renderer now displays each warning once.

No other material finding was established. In particular, the new pad-plane excursion check preserves computed force evidence, reports substrate-clearance uncertainty, and prevents a successful design-comparison verdict when either surface extends beyond the modeled pad planes. Numerical status remains separate from that model limitation. A focused regression demonstrates this behavior without claiming physical accuracy.

## Runtime checks

These commands passed during the review.

```sh
python3 -m unittest discover -s tests -p 'test_cases.py' -v
python3 -m unittest discover -s tests -p 'test_boundaries.py' -v
node --check soldershape/web/app.js
zsh -n 'Start SolderShape.command'
```

There were 11 case/launch/comparison tests and 12 boundary tests. The boundary tests include the live import path, token and foreign-origin rejection, unsupported geometry, numeric domains, archive integrity, and preservation of failed-row evidence. Numerical solver regressions are a separate coordinator-owned check.

A real native-engine HTTP comparison of `examples/volume-comparison.soldershape.json` ran twice. The second run used the final source hashes below, including the new pad-plane guard. Both rows returned `refinement_checked`, both had no model warning, and the comparison returned `compared`.

| Design | Volume, mm³ | X force, µN | Z force, µN |
| --- | ---: | ---: | ---: |
| Reference | 0.005 | -20.36428851937 | -128.77095172947327 |
| Candidate | 0.006 | -19.63342805000323 | -43.77622501901732 |

The candidate changed volume by +20%, restoring force by -0.7308604693667711 µN, and vertical force by +84.99472671045595 µN. These are conditional equilibrium calculations, not a manufacturing recommendation. For each row, the largest upper-plane excursion was floating-point noise of 2.7755575615628914e-17 mm against a 1.5e-7 mm tolerance. The lower-plane excursion was zero.

The first native response's 1,568,589-byte ZIP was inspected in memory. All manifest hashes matched. The editable parameters matched the request. Reference and candidate each had separate OBJ and STL files, their own exact normalized inputs, and different input hashes. That first run preceded the pad-plane guard; the export implementation did not change between the two runs.

Reference input SHA-256 is `53f398e8cd9b5212fad425cdb49567af253df26fe7970e9712a56353192fcc13`. Candidate input SHA-256 is `ea92580bd3559839abb3cf543c8b3db1e1822ee60580542ec46fbb4a594de73b`.

## Comment Sicko and deslop review

No new application comments or docstrings require deletion. The launcher shebang is executable metadata. No scoped lint suppressions, type suppressions, constraint comments, `IMPORTANT` comments, or `do not remove` instructions were introduced.

The deletion count is zero. No comment was restored. There was no rejected report or rerun. No architecture sketch, constraint encoding, or encoding offer was necessary. No constraint remains unenforced. This read-only reviewer made no application-code edit. No material deslop finding remains; the added input checks are at HTTP/file boundaries, and the result checks keep unqualified comparisons from receiving an improvement verdict.

## Reviewed hashes

These SHA-256 values were captured before the second native run and checked again after it. All were unchanged. The solver hash records runtime provenance; this review does not replace the numerical review.

| File | SHA-256 |
| --- | --- |
| `soldershape/model.py` | `3eef0883253f051c75cc5e67641924ec48f31eef17efd9b5ba265115269b3e91` |
| `soldershape/__main__.py` | `3870de483dc43e660b49dd1a6e20f8fd08cac96d73095834f0cd326639327739` |
| `soldershape/artifacts.py` | `a819b4cc21cf5fc6864d87f6506d1a41c973f14107264dc2d5300e9ad26b3666` |
| `soldershape/web/app.js` | `aff5f697b7a0d03253ede7495507411b289da9a39b759883bd55d8a6af9c0f65` |
| `soldershape/web/index.html` | `eb3c25ffe1e2a8a3661a233ceb67f877ddd2af3e217e979a8df0fbbaf888c99b` |
| `soldershape/web/style.css` | `e4d2597aeb6e4d2f43c86a02595bb05f7057d9a2518bf80d3758cd80182b4f1e` |
| `Start SolderShape.command` | `3cc161f8430f2dc5565009d57676657855ef2415f9302ecc7772dd81b611f65a` |
| `tests/test_cases.py` | `8763064648ecdbc45811a8af36c3aa28b2875fc143fa87b61a66e54a38c8719f` |
| `soldershape/solver.py` | `07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98` |

The displayed physical-benchmark note still says that review is underway. Updating that note to the completed campaign's supported verdict belongs to the coordinator's final evidence reconciliation. Physical accuracy remains explicitly unqualified for an arbitrary user design.
