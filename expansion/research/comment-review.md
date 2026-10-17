# Comment review

Scope is the new force analysis, lab packager, handbook renderer, force-analysis tests, board binding module, new board tests, and the changes to `soldershape/__main__.py` against `65b9839`. No application, test, CAD, or UI file was changed by this review.

## Findings

Three narrative module docstrings should be removed. They do not define a public API contract, describe an external constraint, or carry a legal requirement.

| File and line | Exact text | Disposition and proof |
| --- | --- | --- |
| `force_lab/tools/build_handbook.py:1` | `Render the quote-stage fixture drawings and laboratory handbook.` | Remove. The module name and `main()` express the operation. There is no `__doc__` consumer in this module. Removing the docstring does not change generated handbook text or any qualification gate. |
| `soldershape/board.py:1` | `Bind one numerical comparison to a verified native KiCad board selection.` | Remove. The module's public operations are named `board_case`, `run_board`, `bundle_board`, and `verify_board`. This sentence narrates their purpose and specifies no callable contract. There is no `__doc__` consumer in this module. |
| `force_lab/tests/test_analysis.py:1` | `Synthetic controls. These files contain no physical observations.` | Remove. `synthetic_solver` and the fixture evidence values already identify synthetic data explicitly. The solver receipt sets `evidence.synthetic` to `True`; input and outcome evidence values use `SYNTHETIC`. Removing the docstring does not remove those data labels or the tests that reject blank physical inputs. |

No workaround comments or surprise-hiding comments were found. There are no `MUST KILL` application-code flags and no architectural repair is needed for these three removals. This review makes no general engineering-correctness claim.

## Keeps and exclusions

- Keep `force_lab/tools/analyze.py:2`. Its module docstring is consumed by `argparse.ArgumentParser(description=__doc__)` at line 533 and appears verbatim in the public `python3 force_lab/tools/analyze.py --help` output, verified live. It is the CLI's command description.
- Keep `force_lab/tools/package_lab.py:1` for the same public CLI purpose. Its consumer is at line 82; `python3 force_lab/tools/package_lab.py --help` displays it, verified live.
- Keep the shebang at `force_lab/tools/analyze.py:1`. It is an operating-system interpreter directive rather than narrative commentary.
- `soldershape/__main__.py:1` is unchanged from `65b9839`, so it is outside the requested diff scope.
- The pre-existing `tests/` files were scanned for added comments and suppressions; none are changed against the base. New `tests/test_board.py` has no comments or docstrings.

Python tokenization and AST inspection found no inline or block comments beyond the one shebang in the new scoped files. A separate search for `noqa`, type-check suppressions, lint disables, TODOs, FIXMEs, HACKs, and pragmas found no suppressions. The string `ignore` in the numerical planning warning and `shutil.ignore_patterns` in a test are ordinary executable text/API use, not suppressions.

## Counts

Proposed deletions: 3 module docstrings. Actual deletions: 0, report-only. Restored comments: 0. Reruns: 0. `MUST KILL` flags: 0. New constraint encodings or encoding offers: 0. Open application repairs from this comment audit: 0. Parent acceptance and the three removals remain outstanding.
