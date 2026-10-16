#!/bin/zsh
set -eu
cd -- "${0:A:h}"
python3 -c 'import sys; sys.exit("SolderShape needs Python 3.12 or newer. See README.md.") if sys.version_info < (3, 12) else None'
if ! python3 -c 'from soldershape.solver import engine_info; import sys; sys.exit(0 if engine_info().get("ready") else 1)'; then
  python3 tools/setup_engine.py
fi
python3 -m soldershape serve --open
