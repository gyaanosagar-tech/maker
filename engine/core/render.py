"""Render — frames to MP4, audio muxed at exact length.

Never stream frames through a pipe for a long render: write frames to disk,
then encode. A broken pipe silently truncates the file.
"""
import os, subprocess, shutil

FF = os.environ.get("FFMPEG", "ffmpeg")

def encode(frames_dir: str, fps: int, out: str, audio: str = None,
           crf: int = 19, preset: str = "medium"):
    pat = os.path.join(frames_dir, "f%05d.png")
    cmd = [FF, "-y", "-framerate", str(fps), "-i", pat]
    if audio and os.path.exists(audio):
        cmd += ["-i", audio, "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-r", str(fps), out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-2000:])
    return out

def cleanup(frames_dir: str):
    if os.path.isdir(frames_dir):
        shutil.rmtree(frames_dir, ignore_errors=True)
