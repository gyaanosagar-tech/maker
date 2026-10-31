"""Audio — voice timeline, impacts, bed, loudness.

Mix order matters: voice is the reference, everything else ducks under it.
Target -14 LUFS integrated (YouTube normalises to about that).
"""
import json, os, subprocess

FF = os.environ.get("FFMPEG", "ffmpeg")
FP = os.environ.get("FFPROBE", "ffprobe")

def dur(path: str) -> float:
    out = subprocess.run([FP, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)[:200]}\n{r.stderr[-1500:]}")
    return r

def build_voice(narration: list, total: float, out: str):
    """narration: [(path, start_seconds), ...] -> single track at exact offsets."""
    if not narration:
        run([FF, "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={total:.3f}",
             "-ar", "48000", "-ac", "1", out])
        return
    inputs, filt = [], []
    for i, (path, st) in enumerate(narration):
        inputs += ["-i", path]
        ms = int(round(st * 1000))
        filt.append(f"[{i}:a]adelay={ms}|{ms}[v{i}]")
    mix = "".join(f"[v{i}]" for i in range(len(narration)))
    filt.append(f"{mix}amix=inputs={len(narration)}:normalize=0:duration=longest,"
                f"apad,atrim=0:{total:.3f}[vo]")
    run([FF, "-y", *inputs, "-filter_complex", ";".join(filt),
         "-map", "[vo]", "-ar", "48000", "-ac", "1", out])

def build_impacts(at: list, total: float, freq: float = 58.0, out: str = "impacts.wav"):
    """Sub-bass thump on every cut. Cheap, and it is what makes a cut land."""
    if not at:
        run([FF, "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono:d={total:.3f}",
             "-ar", "48000", "-ac", "1", out])
        return
    parts = []
    for i, st in enumerate(at):
        ms = int(round(st * 1000))
        parts.append(f"aevalsrc=0.55*sin(2*PI*{freq}*t)*exp(-9*t):s=48000:d=0.85,"
                     f"adelay={ms}|{ms}[k{i}]")
    parts.append("".join(f"[k{i}]" for i in range(len(at))) +
                 f"amix=inputs={len(at)}:normalize=0:duration=longest,atrim=0:{total:.3f}[imp]")
    run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=0.1",
         "-filter_complex", ";".join(parts), "-map", "[imp]",
         "-ar", "48000", "-ac", "1", out])

def build_room(total: float, out: str = "room.wav", amp: float = 0.035):
    run([FF, "-y", "-f", "lavfi", "-i",
         f"anoisesrc=color=brown:amplitude={amp}:duration={total:.2f}",
         "-af", "lowpass=f=320,volume=0.5", "-ar", "48000", "-ac", "1", out])

def master(voice: str, impacts: str, room: str, total: float, out: str,
           lufs: float = -14.0, bed: str = None, bed_gain: float = 0.17):
    """Final mix. bed (music) is optional — pass a file to include it."""
    ins = ["-i", voice, "-i", impacts, "-i", room]
    chain = ["[0:a]volume=1.0,highpass=f=85[vo]",
             "[1:a]volume=0.42[im]",
             "[2:a]volume=0.30[rm]"]
    mix = "[vo][im][rm]"
    if bed:
        ins += ["-i", bed]
        chain.append(f"[3:a]volume={bed_gain},atrim=0:{total:.3f}[bd]")
        mix += "[bd]"
    n = mix.count("[") - mix.count("]") + 4 if False else mix.count("]") 
    n = len([x for x in mix.split("][")])
    chain.append(f"{mix}amix=inputs={n}:normalize=0:duration=longest,"
                 f"atrim=0:{total:.3f}[mx]")
    chain.append(f"[mx]loudnorm=I={lufs}:TP=-1.5:LRA=11[out]")
    run([FF, "-y", *ins, "-filter_complex", ";".join(chain),
         "-map", "[out]", "-ar", "48000", "-ac", "2", out])

def loudness(path: str) -> float:
    r = subprocess.run([FF, "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "I:" in line and "LUFS" in line:
            return float(line.split("I:")[1].split("LUFS")[0].strip())
    return float("nan")
