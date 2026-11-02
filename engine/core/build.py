"""build — job in, mp4 + evidence out.

The pipeline, in the order that matters:

  1. resolve media   (skills → tools.search_images / search_audio / local)
  2. voice           (local tts, or supplied files; never invented timings)
  3. timeline        (frames first, seconds derived)
  4. frames          (compose per beat)
  5. audio           (voice, impacts on cuts, room, optional bed)
  6. encode + QC     (probe the result; refuse to report success on a bad file)
  7. evidence        (timeline.json, credits.json, qc.json, report.txt)

Everything is written to out/<job>/ so a failure leaves a trail.
"""
import json, os, sys, traceback

import timeline as TL
import audio as AU
import render as RD
import qc as QC
import compose as CP
import tools as TOOLS
import burst as BU
import grid as G

from PIL import Image

def _short_credit(c: dict) -> str:
    """On-frame credit: creator + licence. Full text goes in credits.json."""
    who = (c.get("creator") or "unknown").strip()
    lic = (c.get("license") or "").strip()
    if len(who) > 28:
        who = who[:26].rstrip() + "…"
    return f"{who} · {lic}" if lic else who

def run(job_path: str, workroot: str = "out", fmt: str = None) -> dict:
    job = json.load(open(job_path))
    name = job.get("name") or os.path.splitext(os.path.basename(job_path))[0]
    out = os.path.join(workroot, name)
    frames = os.path.join(out, "frames")
    os.makedirs(frames, exist_ok=True)
    report = [f"job: {name}", f"format: {fmt or job.get('format', 'short')}", ""]

    tl = TL.Timeline.from_job(job)
    report.append(f"beats: {len(tl.beats)}")

    # ---- 1. media
    assets = job.get("assets_dir") or os.path.join(
        os.path.dirname(os.path.abspath(job_path)), "assets")

    # credits were written by fetch_assets at download time — read them back,
    # don't invent them at the end.
    src_credits = {}
    cp = os.path.join(assets, "credits.json")
    if os.path.exists(cp):
        try:
            for c in json.load(open(cp)):
                if c.get("beat"):
                    src_credits[c["beat"]] = c
        except Exception:
            pass
    credits, missing = [], []
    for b in tl.beats:
        p = b.image if os.path.isabs(b.image) else os.path.join(assets, b.image)
        if not os.path.exists(p):
            missing.append(b.image)
            b.image = None
        else:
            b.image = p
        if b.id in src_credits:
            credits.append(src_credits[b.id])
    if missing:
        raise FileNotFoundError(f"missing images: {missing} — run scripts/fetch_assets.py")
    report.append(f"images ok: {len(tl.beats) - len(missing)}/{len(tl.beats)}")

    # ---- 2. voice
    lengths = {}
    narration = []
    for b in tl.beats:
        if b.narration and os.path.exists(b.narration):
            lengths[b.id] = AU.dur(b.narration)
    if tl.mode == "grid":
        if not tl.grid and job.get("music"):
            import fx
            mp = job["music"] if os.path.isabs(job["music"]) else os.path.join(assets, job["music"])
            if os.path.exists(mp):
                tl.grid = fx.beat_times(mp)
                report.append(f"beat grid: {len(tl.grid)} beats detected")
        tl.build_on_grid()
    else:
        tl.build(lengths)
    for b in tl.beats:
        if b.narration and os.path.exists(b.narration):
            narration.append((b.narration, b.start_frame / tl.fps))
    report.append(f"duration: {tl.duration:.2f}s  ({tl.total_frames} frames @ {tl.fps})")

    # ---- bursts: the kinetic punches in the middle of the video
    bursts = BU.schedule(job.get("bursts", []))
    if job.get("auto_bursts"):
        ab = job["auto_bursts"]
        styles = ab.get("styles", ["flash", "glitch", "invert"])
        every = float(ab.get("every", 2.5))
        dur = float(ab.get("dur", 0.5))
        t = float(ab.get("start", tl.body_start if hasattr(tl, "body_start") else 2.0))
        i = 0
        while t < tl.duration - 1.2:
            bursts.append({"at": round(t, 3), "dur": dur,
                           "style": styles[i % len(styles)],
                           "hits": BU.default_hits(styles[i % len(styles)]),
                           "intensity": float(ab.get("intensity", 0.8)),
                           "word": ab.get("words", [""])[0] if ab.get("words") else ""})
            t += every
            i += 1
        bursts = BU.schedule(bursts)
    if bursts:
        report.append("bursts: " + ", ".join(
            f'{b["style"]}@{b["at"]:.2f}s' for b in bursts))

    # ---- 3-4. frames
    total_frames = tl.total_frames
    cache = {}
    for i, b in enumerate(tl.beats):
        src = Image.open(b.image).convert("RGB")
        cache[i] = src
    report.append("rendering frames...")
    for f in range(total_frames):
        idx = 0
        for i, b in enumerate(tl.beats):
            if f >= b.start_frame:
                idx = i
        b = tl.beats[idx]
        local = (f - b.start_frame) / max(1, b.frames - 1)
        local = max(0.0, min(1.0, local))
        c = src_credits.get(b.id)
        credit = _short_credit(c) if c else ""
        img = CP.frame_for(b, cache[idx], local, idx, len(tl.beats), credit=credit)
        # transitions on the first 8 frames of a beat
        if idx > 0 and f - b.start_frame < 8:
            import transition as TR
            img = TR.whip_pan(img, (f - b.start_frame) / 8.0, 1 if idx % 2 else -1, 0.42)
        if f < tl.head_frames:
            import transition as TR
            img = TR.fade_from_black(img, f / max(1, tl.head_frames - 1))
        if f > total_frames - tl.tail_frames:
            import transition as TR
            img = TR.fade_to_black(img, (f - (total_frames - tl.tail_frames)) / max(1, tl.tail_frames - 1))

        # kinetic burst on top of the composed frame
        if bursts:
            t_now = f / tl.fps
            b, bt = BU.active(bursts, t_now)
            if b is not None:
                subs = [cache[j] for j in range(len(cache))] if b["style"] == "stack" else None
                img = BU.apply(img, b["style"], bt, b["dur"],
                               intensity=b["intensity"], word=b["word"],
                               seed=f, subs=subs)
        img.save(os.path.join(frames, f"f{f:05d}.png"), compress_level=1)
    report.append(f"frames written: {total_frames}")

    # ---- 5. audio
    voice = os.path.join(out, "voice.wav")
    AU.build_voice(narration, tl.duration, voice)
    cut_times = tl.cut_times()
    imp = os.path.join(out, "impacts.wav")
    AU.build_impacts(cut_times, tl.duration, out=imp)
    room = os.path.join(out, "room.wav")
    AU.build_room(tl.duration, out=room)
    bed = job.get("music")
    if bed and not os.path.isabs(bed):
        bed = os.path.join(assets, bed)
    if bed and not os.path.exists(bed):
        report.append(f"WARNING music not found: {bed} — mixing without it")
        bed = None
    mixed = os.path.join(out, "mix.wav")
    AU.master_two_pass(voice, imp, room, tl.duration, mixed,
                       lufs=job.get("lufs", -14.0), bed=bed,
                       bed_gain=job.get("music_gain", 0.17),
                       impact_gain=job.get("impact_gain", 0.42),
                       room_gain=job.get("room_gain", 0.30),
                       voice_gain=job.get("voice_gain", 1.0))
    report.append(f"mix: voice + {len(cut_times)} impacts + room" + (" + bed" if bed else ""))

    # ---- 6. encode + QC
    mp4 = os.path.join(out, f"{name}.mp4")
    RD.encode(frames, tl.fps, mp4, audio=mixed, crf=job.get("crf", 19))
    check = QC.check(mp4, expect_frames=total_frames, fps=tl.fps)
    report.append(f"encoded: {check['size_mb']} MB  {check['duration']:.2f}s")
    report.append(f"qc: {'PASS' if check['ok'] else 'FAIL — ' + '; '.join(check['problems'])}")

    # ---- 7. evidence
    tl.save(os.path.join(out, "timeline.json"))
    json.dump(credits, open(os.path.join(out, "credits.json"), "w"), indent=1)
    json.dump(check, open(os.path.join(out, "qc.json"), "w"), indent=1)
    RD.cleanup(frames)

    summary = {"name": name, "file": mp4, "ok": check["ok"],
               "duration": check["duration"], "size_mb": check["size_mb"],
               "lufs": check.get("lufs"), "frames": check.get("frames"),
               "beats": len(tl.beats), "problems": check["problems"]}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    open(os.path.join(out, "report.txt"), "w").write("\n".join(report) + "\n")
    return summary

if __name__ == "__main__":
    try:
        r = run(sys.argv[1])
        print("\n".join(f"{k}: {v}" for k, v in r.items()))
        sys.exit(0 if r["ok"] else 1)
    except Exception:
        traceback.print_exc()
        sys.exit(2)
