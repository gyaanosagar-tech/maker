#!/usr/bin/env python3
"""Placeholder renderer entrypoint.

Replace the body of `render()` with the real pipeline. The contract is:

    python scripts/render.py --job jobs/foo.json  ->  writes out/<name>.mp4

Keeping this file present means render.yml works on day one instead of
failing with "no such file".
"""
import argparse, json, os, subprocess, sys

def render(job):
    name = job.get("name", "output")
    os.makedirs("out", exist_ok=True)
    w, h = (job.get("resolution") or "1080x1920").split("x")
    fps = job.get("fps", 30)
    dur = max(2, len(job.get("beats", [])) * 2)
    dst = f"out/{name}.mp4"
    print(f"rendering {w}x{h} @{fps} for {dur}s -> {dst}")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "lavfi", "-i", f"color=c=0x0d0d12:s={w}x{h}:d={dur}:r={fps}",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={dur}",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", dst,
    ], check=True)
    print("done:", os.path.getsize(dst), "bytes")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    a = ap.parse_args()
    with open(a.job) as f:
        job = json.load(f)
    render(job)

if __name__ == "__main__":
    main()
