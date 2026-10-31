"""QC — verify, never assume.

Every check here exists because it has silently failed before.
"""
import json, os, subprocess

FP = os.environ.get("FFPROBE", "ffprobe")

def probe(path: str) -> dict:
    r = subprocess.run([FP, "-v", "error", "-print_format", "json",
                        "-show_format", "-show_streams", path],
                       capture_output=True, text=True)
    return json.loads(r.stdout or "{}")

def check(path: str, expect_frames: int = None, fps: int = 30,
          w: int = 1080, h: int = 1920, min_lufs: float = -18, max_lufs: float = -10) -> dict:
    p = probe(path)
    v = next((s for s in p.get("streams", []) if s["codec_type"] == "video"), {})
    a = next((s for s in p.get("streams", []) if s["codec_type"] == "audio"), {})
    out = {"path": path, "ok": True, "problems": []}

    if v.get("width") != w or v.get("height") != h:
        out["problems"].append(f"size {v.get('width')}x{v.get('height')} != {w}x{h}")
    if not a:
        out["problems"].append("no audio stream")
    if expect_frames:
        n = subprocess.run([FP, "-v", "error", "-select_streams", "v:0",
                            "-count_frames", "-show_entries", "stream=nb_read_frames",
                            "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
        got = int(n) if n.isdigit() else -1
        out["frames"] = got
        if got != expect_frames:
            out["problems"].append(f"frames {got} != {expect_frames}")

    if a:
        r = subprocess.run(["ffmpeg", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True)
        got = float("nan")
        for line in r.stderr.splitlines():
            if "I:" in line and "LUFS" in line:
                got = float(line.split("I:")[1].split("LUFS")[0].strip())
        out["lufs"] = got
        if got == got and not (min_lufs <= got <= max_lufs):
            out["problems"].append(f"loudness {got} LUFS outside {min_lufs}..{max_lufs}")

    out["duration"] = float(p.get("format", {}).get("duration", 0) or 0)
    out["size_mb"] = round(int(p.get("format", {}).get("size", 0) or 0) / 1e6, 2)
    out["ok"] = not out["problems"]
    return out
