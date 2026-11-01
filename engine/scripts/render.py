#!/usr/bin/env python3
"""Render a job to MP4.

    python3 engine/scripts/render.py jobs/demo.json
    python3 engine/scripts/render.py jobs/demo.json --out /tmp/out
"""
import argparse, os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "core"))

import build

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--out", default="out")
a = ap.parse_args()
r = build.run(a.job, workroot=a.out)
print(json.dumps(r, indent=1))
sys.exit(0 if r["ok"] else 1)
