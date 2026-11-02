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

def build_room(total: float, out: str = "room.wav", amp: float = 0.035,
               seed: int = 1):
    """Room tone. Seeded on purpose.

    anoisesrc without a seed returns different noise every run, which made the
    same commit render at -9.6 LUFS on one CI run and -15.3 on the next. A
    render has to be reproducible: same job in, same file out.
    """
    run([FF, "-y", "-f", "lavfi", "-i",
         f"anoisesrc=color=brown:amplitude={amp}:duration={total:.2f}:seed={seed}",
         "-af", "lowpass=f=320,volume=0.5", "-ar", "48000", "-ac", "1", out])

def master(voice: str, impacts: str, room: str, total: float, out: str,
           lufs: float = -14.0, bed: str = None, bed_gain: float = 0.17,
           impact_gain: float = 0.42, room_gain: float = 0.30,
           voice_gain: float = 1.0):
    """Final mix. bed (music) is optional — pass a file to include it.

    The levels are arguments, not constants, because earshot proved the cut
    impacts were 13 dB under the voice and every cut read as "NO HIT". A
    default that can be measured against a alternative has to be a knob.
    """
    ins = ["-i", voice, "-i", impacts, "-i", room]
    chain = [f"[0:a]volume={voice_gain},highpass=f=85[vo]",
             f"[1:a]volume={impact_gain}[im]",
             f"[2:a]volume={room_gain}[rm]"]
    mix = "[vo][im][rm]"
    if bed:
        ins += ["-i", bed]
        chain.append(f"[3:a]volume={bed_gain},atrim=0:{total:.3f}[bd]")
        mix += "[bd]"
    n = mix.count("[") - mix.count("]") + 4 if False else mix.count("]") 
    n = len([x for x in mix.split("][")])
    chain.append(f"{mix}amix=inputs={n}:normalize=0:duration=longest,"
                 f"atrim=0:{total:.3f}[mx]")
    # Two-pass loudnorm. Single-pass measured -19.1 LUFS on a job that asked
    # for -14 because it normalises from a short analysis window and the bed
    # was quiet. Measure first, then apply with the measured values.
    chain.append(f"[mx]loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json[out]")
    run([FF, "-y", *ins, "-filter_complex", ";".join(chain),
         "-map", "[out]", "-ar", "48000", "-ac", "2", out])

def loudnorm_second_pass(path: str, lufs: float = -14.0,
                         tp: float = -1.5, lra: float = 11.0):
    """Filter string for a measured loudnorm 2nd pass, or None if unmeasurable.

    One place decides how a mix is corrected. build.py (wav in), rankshort.py
    (mp4 in, video copied) and anything added later all call this, so the bug
    that lived in two separate blind loops cannot come back in a third.
    """
    m = _loudnorm_measure(path, lufs)
    need = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    if not m or any(k not in m for k in need):
        return None
    return (f"loudnorm=I={lufs}:TP={tp}:LRA={lra}"
            f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}"
            f":offset={m['target_offset']}:linear=true:print_format=summary")


def master_two_pass(voice, impacts, room, total, out, lufs=-14.0,
                    bed=None, bed_gain=0.17, attempts=3, tol=0.5,
                    impact_gain=0.42, room_gain=0.30, voice_gain=1.0):
    """Mix, then land the integrated loudness on target with a measured 2nd pass.

    What used to run here was `volume=<error>dB` in a loop: it guessed by the
    size of the error and hoped. On a sparse mix the error was read wrong (see
    loudness()), so it boosted by the maximum twice and shipped -9.6 LUFS.
    Now: measure with loudnorm's own JSON, re-apply with linear=true and the
    measured values so dynamics survive, and stop inside `tol`.
    """
    import os as _os

    master(voice, impacts, room, total, out, lufs=lufs, bed=bed,
           bed_gain=bed_gain, impact_gain=impact_gain, room_gain=room_gain,
           voice_gain=voice_gain)

    for _ in range(attempts):
        got = loudness(out)
        if got != got or got <= -60.0:      # unreadable or silent: never boost
            break
        if abs(got - lufs) <= tol:
            break
        af = loudnorm_second_pass(out, lufs)
        if not af:
            break
        tmp = out + ".tune.wav"
        run([FF, "-y", "-i", out, "-af", af, "-ar", "48000", "-ac", "2", tmp])
        _os.replace(tmp, out)
    return out


def loudness(path: str) -> float:
    """Integrated LUFS — from the Summary block ONLY.

    ebur128 prints a progress line every ~100 ms and every one of them contains
    "I:". The first one is the first 100 ms of the file (silence -> -70.0), not
    the measurement. Reading the first match made every mix look 56 dB too quiet
    and master_two_pass boosted it by the maximum. The Summary block is the only
    honest number; qc.py's "keep the last" loop was already right.
    """
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path,
                        "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    got, in_summary = float("nan"), False
    for line in r.stderr.splitlines():
        if "Summary:" in line:
            in_summary = True
            continue
        if in_summary and "I:" in line and "LUFS" in line:
            try:
                got = float(line.split("I:")[1].split("LUFS")[0].strip())
            except ValueError:
                pass
            break
    return got


def _loudnorm_measure(path: str, lufs: float = -14.0) -> dict:
    """First loudnorm pass: measure, do not change anything."""
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path, "-af",
                        f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    i, j = r.stderr.find("{"), r.stderr.rfind("}")
    if i < 0 or j <= i:
        return {}
    try:
        return json.loads(r.stderr[i:j + 1])
    except Exception:
        return {}
