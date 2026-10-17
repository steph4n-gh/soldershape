# Comment review

Scope: the new Python files under `coupons/tools` and `coupons/tests`. Same-family fresh reviewer, with no application-code edits. This review concerns comments and structural surprises, not scientific qualification or manufacturing release.

## Recommended deletions

1. `coupons/tools/verify_boards.py:1`: delete the module docstring. It repeats the file's purpose, has no `__doc__` consumer, and contains no constraint or external fact.
2. `coupons/tests/test_analysis.py:1`: delete the module docstring. Synthetic fixtures already identify themselves in their values and native test doubles. The top-level prose adds no executable check or external requirement.

These are ordinary redundant prose deletions, not `MUST KILL` workaround findings. No source files were edited by this reviewer.

## Functional strings

`coupons/tools/analyze.py:2` and `coupons/tools/build_boards.py:1` feed `ArgumentParser(description=__doc__)` at lines 491 and 161 in the reviewed snapshot. They supply user-visible CLI help. Removing them would remove help text. They are runtime interface text, not an explanation masking an application-code surprise.

The `analyze.py:1` shebang selects an interpreter for direct execution. There are no scoped lint, typing, correctness, or safety suppressions. The `argparse.SUPPRESS` at `build_boards.py:162` hides the Docker-only internal CLI flag; it is not a warning or correctness suppression.

## Result

Recommended comment/docstring deletions: 2. Actual deletions by this reviewer: 0. Restorations: 0. Reruns: 0. Architect sketches: none. Application-code fixes: none. Encoding offers or encodings: none. Unenforced comment constraints: none. No additional comment-backed structural surprises found.

## Reviewed snapshot

- `coupons/tools/analyze.py`: `92d80bd829bfa725d886d3cf6ed82f1cdf03c53b2c535c3776d4dda5a8fab7de`
- `coupons/tools/build_boards.py`: `4540b9f0b459afa2c4a4ee55c1c38a117c076ce3a44417442595453b460ddf41`
- `coupons/tools/verify_boards.py`: `f782f4130bb4388b363b8c81f870122b9e194e1e1e2939f323316f92147bd8c9`
- `coupons/tests/test_analysis.py`: `623a3b2b8c3900c59ca710e3ee30bb56a29a21114c206b0fd132e50e24068b38`

## Root disposition

Removed the two recommended unused module docstrings. Removed two equivalent unused strings from the later fabrication tests and PDF generator. Four deletions, zero restored comments, zero reruns required, zero suppressions, zero application behavior changes, and no unresolved encoding offer or constraint. CLI help strings remain consumed by their parsers. No structural fix was needed.
