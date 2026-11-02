"""Regression tests for the engine's loudness path.

These exist because of one bug that survived 25 published videos and turned
five CI runs red: `audio.loudness()` read ebur128's FIRST progress line (-70.0,
the first 100 ms of silence) instead of the Summary block (-9.6), so the
"two-pass" correction boosted the mix by the maximum twice and shipped a
-9.6 LUFS master. qc.py then failed the render — correctly — and the failure
was blamed on CI instead of on the code.

Run:  python3 -m pytest tests/ -v
Needs ffmpeg on PATH (same requirement as the engine).
"""
import hashlib
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = os.path.join(os.path.dirname(HERE), "engine", "core")
sys.path.insert(0, CORE)

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg not on PATH")

FF = "ffmpeg"


def _run(args):
    subprocess.run([FF, "-y", "-loglevel", "error", *args], check=True)


@pytest.fixture(scope="module")
def audio_mod():
    import audio
    return audio


def _tone(path, seconds=1.0, freq=1000, amp=0.5, channels=1):
    _run(["-f", "lavfi", "-i",
          f"sine=frequency={freq}:duration={seconds}",
          "-af", f"volume={amp}", "-ar", "48000", "-ac", str(channels), path])


def _silence(path, seconds=1.0, channels=1):
    _run(["-f", "lavfi", "-i",
          f"anullsrc=r=48000:cl={'mono' if channels == 1 else 'stereo'}:d={seconds}",
          "-ar", "48000", "-ac", str(channels), path])


def _concat(parts, out):
    with open(os.path.join(os.path.dirname(out), "list.txt"), "w") as fh:
        for p in parts:
            fh.write(f"file '{p}'\n")
    _run(["-f", "concat", "-safe", "0", "-i",
          os.path.join(os.path.dirname(out), "list.txt"), "-ar", "48000",
          "-ac", "1", out])


# --------------------------------------------------------------------------
# 1. THE regression. A file that opens with silence must not read as -70.
# --------------------------------------------------------------------------
def test_loudness_reads_summary_not_the_first_progress_line(tmp_path, audio_mod):
    """A 1 s silence + 1 s tone must measure the tone, not the silence."""
    sil = str(tmp_path / "sil.wav")
    tone = str(tmp_path / "tone.wav")
    both = str(tmp_path / "both.wav")
    _silence(sil, 1.0)
    _tone(tone, 1.0)
    _concat([sil, tone], both)

    got = audio_mod.loudness(both)

    # The bug returned exactly -70.0 (ebur128's first progress line).
    assert got == got, "loudness returned NaN"
    assert got > -40.0, (
        f"loudness() read {got} LUFS — that is the first progress line "
        f"(leading silence), not the Summary block")


def test_loudness_is_close_to_ffmpeg_summary(tmp_path, audio_mod):
    """The number must match what ebur128's Summary says on its own."""
    tone = str(tmp_path / "t.wav")
    _tone(tone, 2.0, amp=0.25)
    got = audio_mod.loudness(tone)

    out = subprocess.run([FF, "-hide_banner", "-nostats", "-i", tone,
                          "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summ = None
    seen = False
    for line in out.splitlines():
        if "Summary:" in line:
            seen = True
        if seen and "I:" in line and "LUFS" in line:
            summ = float(line.split("I:")[1].split("LUFS")[0].strip())
            break
    assert summ is not None
    assert abs(got - summ) < 0.2, f"engine {got} vs ffmpeg {summ}"


# --------------------------------------------------------------------------
# 2. Silence must never be boosted.
# --------------------------------------------------------------------------
def test_silence_is_never_boosted(tmp_path, audio_mod):
    """The old loop pushed +12 dB twice into an already-silent mix."""
    v, i, r, out = (str(tmp_path / n) for n in
                    ("v.wav", "i.wav", "r.wav", "mix.wav"))
    for p in (v, i, r):
        _silence(p, 1.0)
    audio_mod.master_two_pass(v, i, r, 1.0, out, lufs=-14.0)

    got = audio_mod.loudness(out)
    assert got != got or got <= -60.0, (
        f"a silent mix came out at {got} LUFS — the correction invented signal")


# --------------------------------------------------------------------------
# 3. The two-pass must land on target.
# --------------------------------------------------------------------------
def test_master_two_pass_lands_on_target(tmp_path, audio_mod):
    v, i, r, out = (str(tmp_path / n) for n in
                    ("v.wav", "i.wav", "r.wav", "mix.wav"))
    _tone(v, 2.0, freq=440, amp=0.6)
    _tone(i, 2.0, freq=58, amp=0.4)
    _tone(r, 2.0, freq=200, amp=0.05)
    target = -14.0
    audio_mod.master_two_pass(v, i, r, 2.0, out, lufs=target)

    got = audio_mod.loudness(out)
    assert got == got
    assert abs(got - target) <= 1.5, f"landed at {got}, target {target}"


# --------------------------------------------------------------------------
# 4. A render has to be reproducible — the random room tone made CI flaky.
# --------------------------------------------------------------------------
def test_room_tone_is_reproducible(tmp_path, audio_mod):
    a = str(tmp_path / "room_a.wav")
    b = str(tmp_path / "room_b.wav")
    audio_mod.build_room(1.0, out=a, seed=1)
    audio_mod.build_room(1.0, out=b, seed=1)
    ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
    hb = hashlib.sha256(open(b, "rb").read()).hexdigest()
    assert ha == hb, "room tone differs between runs — renders are not reproducible"


# --------------------------------------------------------------------------
# 5. Every caller uses the one shared second pass.
# --------------------------------------------------------------------------
def test_second_pass_filter_is_measured(tmp_path, audio_mod):
    tone = str(tmp_path / "t.wav")
    _tone(tone, 2.0, amp=0.3)
    af = audio_mod.loudnorm_second_pass(tone, -14.0)
    assert af, "loudnorm_second_pass returned None for a measurable file"
    assert "measured_I=" in af and "linear=true" in af, (
        "the second pass is not using loudnorm's measured values / linear mode")
