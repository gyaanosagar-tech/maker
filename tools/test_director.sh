#!/usr/bin/env bash
set -e
python3 -c "import ast,sys; ast.parse(open('tools/director.py').read())"
python3 tools/director.py --requirements hook,voice,pacing,transitions,energy,render,qc >/dev/null
echo "director ok"
