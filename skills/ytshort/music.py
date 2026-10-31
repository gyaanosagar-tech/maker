"""
music.py — video pe background music lagana (upload se PEHLE, ffmpeg se).

Kyun aise: kisi bhi platform ki "trending song library" API se lagana
lagbhag possible nahi hai (IG ka licensed catalog third-party tools ko nahi milta,
YouTube ka audio library API me nahi hai). To track ka file hum khud video me
mix kar dete hain — phir wo teeno jagah same chalti hai.

Aapke paas 2 raaste hain:
  A) royalty-free track ka file (best — copyright strike nahi)
  B) koi bhi track jo aapke paas mp3 me hai (copyright aapki zimmedari)

Use:
  from music import attach
  path = attach("video.mp4", "song.mp3", volume=0.25, fade_out=2)
"""
from __future__ import annotations

import os
import shutil
import subprocess

# ffmpeg system me na ho to imageio-ffmpeg ka static build use karo
_BUNDLED = None


def ffmpeg_bin() -> str:
    global _BUNDLED
    system = shutil.which("ffmpeg")
    if system:
        return system
    if _BUNDLED:
        return _BUNDLED
    try:
        import imageio_ffmpeg

        _BUNDLED = imageio_ffmpeg.get_ffmpeg_exe()
        return _BUNDLED
    except ImportError:
        raise RuntimeError(
            "ffmpeg nahi mila. `sudo apt install ffmpeg` (ya Mac: brew install ffmpeg) "
            "ya `pip install imageio-ffmpeg`"
        )


def probe_duration(path: str) -> float:
    """File ki length (seconds). ffprobe na ho to ffmpeg ke output se."""
    ffprobe = shutil.which("ffprobe")
    try:
        if ffprobe:
            out = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", path],
                capture_output=True, text=True, check=True).stdout.strip()
            return float(out)
    except Exception:
        pass
    # fallback: ffmpeg -i ka stderr parse
    result = subprocess.run([ffmpeg_bin(), "-i", path], capture_output=True, text=True)
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            stamp = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = stamp.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def attach(
    video_path: str,
    music_path: str,
    volume: float = 0.25,
    fade_out: float = 2.0,
    keep_original: bool = True,
    out_path: str | None = None,
) -> str:
    """
    Video pe music chadhao.

    volume       : music ka level (0.25 = halka background). Original audio 1.0 rehta hai.
    keep_original: True -> dono mix (ducking ke bina). False -> sirf music.
    fade_out     : aakhir me music fade out (seconds).

    Return: naya file path (original chhua nahi jaata).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(video_path)
    if not os.path.exists(music_path):
        raise FileNotFoundError(f"Music file nahi mili: {music_path}")

    out_path = out_path or os.path.splitext(video_path)[0] + "_music.mp4"
    v_dur = probe_duration(video_path) or 60.0
    fade_start = max(0.0, v_dur - fade_out)

    if keep_original:
        filter_complex = (
            f"[0:a]volume=1.0[a0];"
            f"[1:a]volume={volume},afade=t=in:st=0:d=1,"
            f"afade=t=out:st={fade_start:.2f}:d={fade_out},"
            f"aloop=loop=-1:size=2e9[am];"
            f"[a0][am]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        maps = ["-map", "0:v", "-map", "[aout]"]
    else:
        filter_complex = (
            f"[1:a]volume={volume},afade=t=in:st=0:d=1,"
            f"afade=t=out:st={fade_start:.2f}:d={fade_out},"
            f"aloop=loop=-1:size=2e9[aout]"
        )
        maps = ["-map", "0:v", "-map", "[aout]"]

    cmd = [
        ffmpeg_bin(), "-y", "-loglevel", "error",
        "-i", video_path,
        "-i", music_path,
        "-filter_complex", filter_complex,
        *maps,
        "-c:v", "copy",          # video ko chhedo mat — fast + quality same
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"music mix fail: {result.stderr[-500:]}")

    print(f"[music] {os.path.basename(music_path)} @ {volume} -> {os.path.basename(out_path)}")
    return out_path


def track_name(path: str) -> str:
    """Credits ke liye naam (filename se)."""
    return os.path.splitext(os.path.basename(path))[0].replace("_", " ")


def credit_line(path: str, artist: str | None = None) -> str:
    """Description me daalne ke liye credit."""
    name = track_name(path)
    return f"Music: {artist + ' — ' if artist else ''}{name}"


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="video + music")
    ap.add_argument("video")
    ap.add_argument("music")
    ap.add_argument("--volume", type=float, default=0.25)
    ap.add_argument("--no-original", action="store_true", help="original audio hatao")
    ap.add_argument("--out")
    args = ap.parse_args()
    print(attach(args.video, args.music, volume=args.volume,
                 keep_original=not args.no_original, out_path=args.out))
