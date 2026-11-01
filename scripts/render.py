#!/usr/bin/env python3
"""Repo entry point. Delegates to engine/ — one implementation, not two.

    python3 scripts/render.py jobs/demo.json
"""
import os, runpy, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.execv(sys.executable, [sys.executable,
                          os.path.join(root, "engine", "scripts", "render.py")] + sys.argv[1:])
