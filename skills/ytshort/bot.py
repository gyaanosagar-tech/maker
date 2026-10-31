#!/usr/bin/env python3
"""
bot.py — poora system ka control panel.

  bot.py upload "<drive-link-ya-file>" --job job.json --now
  bot.py upload "<drive-link>" --job job.json --at "2026-10-26 18:00"
  bot.py bulk jobs/weekly.json              # har item ka apna time
  bot.py bulk jobs/weekly.json --at "2026-10-26 18:00"   # sab ek time
  bot.py list                               # kya pending hai
  bot.py cancel <id>
  bot.py run --publish                      # due jobs chalao (cron yahi chalata hai)
  bot.py insights                           # performance CSV + report

job.json format (text main likhta hoon):
{
  "title": "...", "description": "...", "tags": ["..."], "caption": "...",
  "playlist": "Bihar Vlogs",
  "platforms": ["youtube", "instagram", "facebook"]
}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timedelta

import config
import drive_helper
import instagram_uploader as ig
import state_store
import textkit
import youtube_uploader as yt
from state_store import IST, fmt, now_ist

PLATFORMS = ("youtube", "instagram", "facebook")


# ------------------------------------------------------------------ helpers
def load_job_file(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def parse_when(raw: str | None) -> datetime | None:
    """now / in 2h / 18:30 / '2026-10-26 18:00' -> IST datetime (ya None = abhi)"""
    if not raw or raw.strip().lower() in ("now", "abhi"):
        return None
    raw = raw.strip().lower()
    now = now_ist()

    if raw.startswith("in "):
        chunk = raw[3:].strip()
        unit, amount = chunk[-1], float(chunk[:-1])
        delta = {"m": timedelta(minutes=amount), "h": timedelta(hours=amount),
                 "d": timedelta(days=amount)}.get(unit)
        if delta is None:
            raise ValueError("'in 2h' / 'in 30m' / 'in 1d' format use karo")
        return (now + delta).replace(second=0, microsecond=0)

    for pattern in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%d-%m-%Y %H:%M"):
        try:
            parsed = datetime.strptime(raw, pattern).replace(tzinfo=IST)
            if parsed <= now:
                raise ValueError(f"'{raw}' past me hai (abhi {fmt(now)} IST)")
            return parsed
        except ValueError as exc:
            if "past" in str(exc):
                raise
            continue

    try:
        clock = datetime.strptime(raw, "%H:%M").time()
        candidate = now.replace(hour=clock.hour, minute=clock.minute, second=0, microsecond=0)
        return candidate if candidate > now else candidate + timedelta(days=1)
    except ValueError:
        raise ValueError(f"'{raw}' samajh nahi aaya. Use: now | in 2h | 18:30 | '2026-10-26 18:00'")


def warn_slot_clash(platforms: tuple[str, ...], when: datetime | None) -> None:
    """Same platform pe same minute do job — API error deta hai, isliye warn."""
    if not when:
        return
    taken = {s for s in state_store.slots_taken("youtube") if s}
    taken |= {j.get("when") for j in state_store.pending_jobs() if j.get("when")}
    if fmt(when) in taken:
        print(f"!! WARN {fmt(when)} IST pe pehle se ek job hai — dono ek saath honge")


# ------------------------------------------------------------------ upload
def do_upload(ref: str, text: dict, when: datetime | None, platforms: tuple[str, ...],
              publish: bool = True, trial: bool | None = None) -> dict:
    """
    Ek video teeno jagah.
    when = None -> turant. when = future -> YT/FB native schedule, IG queue (cron) se.
    """
    if state_store.is_stopped():
        raise RuntimeError("STOP.flag laga hua hai — sab upload band. `bot.py resume` chalao.")

    if not str(text.get("privacy") or "").strip():
        raise yt.PrivacyNotSet(
            'privacy nahi likha — upload rok diya. '
            'Job me daalo: "privacy": "public" | "private" | "unlisted" | "scheduled"'
        )

    file_ref, local_path, filename, cleanup = drive_helper.resolve(ref)
    built = textkit.build(text, filename)
    result: dict = {"file": file_ref, "filename": filename, "steps": {}, "text": built}
    temp_files: list[str] = [local_path] if cleanup else []

    # background music (jo aap bologe wahi track)
    if text.get("music"):
        local_path = _add_music(local_path, text, built, temp_files)

    for warning in textkit.warnings(built):
        print(f"!! {warning}")

    # ---------------- YouTube
    if "youtube" in platforms:
        try:
            if state_store.is_done(file_ref, "youtube"):
                result["steps"]["youtube"] = "skipped (pehle chadh chuki)"
            else:
                if state_store.count_today("youtube") >= config.VIDEOS_PER_DAY:
                    raise RuntimeError(
                        f"YT quota guard: {config.VIDEOS_PER_DAY} video/day "
                        f"(10,000 units ÷ 1650). Kal ke liye schedule karo."
                    )
                slot = when if (when and yt.publish_at_ok(when)) else None
                if when and not slot:
                    print("[youtube] slot bahut paas — turant public kar rahe hain")
                if state_store.is_stopped():
                    raise RuntimeError("beech me STOP mila — YouTube upload roka")
                video_id = yt.upload(local_path, built, publish_at_ist=slot)
                state = yt.verify(video_id)
                status = "scheduled" if state.get("publishAt") else "ok"
                state_store.log_row(
                    job_id=text.get("_job_id", ""), file=file_ref, filename=filename,
                    title=built["title"], platform="youtube", status=status,
                    remote_id=video_id, url=f"https://youtu.be/{video_id}",
                    scheduled_for_ist=fmt(slot) if slot else fmt(now_ist()),
                    playlist=yt.resolve_playlist(built) or "",
                    error="" if state.get("privacy") else str(state)[:200],
                )
                result["steps"]["youtube"] = f"{status} {video_id}"
        except Exception as exc:
            result["steps"]["youtube"] = _fail(file_ref, filename, built, "youtube", exc)

    # ---------------- Instagram
    if "instagram" in platforms:
        try:
            if state_store.is_done(file_ref, "instagram"):
                result["steps"]["instagram"] = "skipped (pehle chadh chuki)"
            elif when and (when - now_ist()) > timedelta(minutes=20):
                # IG me native scheduling nahi — queue me daalo, cron slot pe chala dega
                result["steps"]["instagram"] = f"queued for {fmt(when)} (cron publish karega)"
            else:
                result["steps"]["instagram"] = _post_ig(file_ref, filename, local_path, built, trial)
        except Exception as exc:
            result["steps"]["instagram"] = _fail(file_ref, filename, built, "instagram", exc)

    # ---------------- Facebook
    if "facebook" in platforms:
        try:
            if not config.FB_PAGE_IDS:
                raise RuntimeError("FB_PAGE_IDS khaali hai")
            if state_store.is_done(file_ref, "facebook"):
                result["steps"]["facebook"] = "skipped (pehle chadh chuki)"
            else:
                fb_when = int(when.timestamp()) if (when and (when - now_ist()) > timedelta(minutes=10)) else None
                vid = ig.post_fb_video(
                    config.FB_PAGE_IDS[0], local_path,
                    description=built["fb_description"], title=built["title"],
                    scheduled_publish_time=fb_when,
                )
                state_store.log_row(
                    job_id=text.get("_job_id", ""), file=file_ref, filename=filename,
                    title=built["title"], platform="facebook",
                    status="scheduled" if fb_when else "ok", remote_id=vid,
                    scheduled_for_ist=fmt(when) if when else fmt(now_ist()),
                )
                result["steps"]["facebook"] = f"{'scheduled' if fb_when else 'ok'} {vid}"
        except Exception as exc:
            result["steps"]["facebook"] = _fail(file_ref, filename, built, "facebook", exc)

    for path in temp_files:
        try:
            os.remove(path)
        except OSError:
            pass
    return result


def _add_music(local_path: str, text: dict, built: dict, temp_files: list[str]) -> str:
    """Job file me "music": "song.mp3" ho to video me mix karo (ffmpeg)."""
    import music as musicmod

    music_path = text["music"]
    if not os.path.exists(music_path):
        print(f"!! music file nahi mili: {music_path} — bina music ke ja raha hai")
        return local_path
    mixed = musicmod.attach(
        local_path, music_path,
        volume=float(text.get("music_volume", 0.25)),
        keep_original=bool(text.get("keep_original_audio", True)),
    )
    temp_files.append(mixed)
    credit = musicmod.credit_line(music_path, text.get("music_artist"))
    built["description"] = (built["description"].rstrip() + "\n\n" + credit)[:textkit.YT_DESC_MAX]
    built["fb_description"] = built["description"]
    if credit not in built["caption"]:
        built["caption"] = (built["caption"].rstrip() + "\n\n" + credit)[:textkit.IG_CAPTION_MAX]
    return mixed


def _post_ig(file_ref: str, filename: str, local_path: str, built: dict,
             trial: bool | None) -> str:
    """IG publish — trial allowed hai ya nahi wo account se tay hota hai."""
    ig_id = config.IG_USER_IDS[0]
    allowed, note = ig.trial_allowed(ig_id)
    print(f"[ig] {note}")
    use_trial = bool(allowed and trial)
    info = ig.post_reel(ig_id, local_path, built["caption"], trial=use_trial)
    state_store.log_row(
        job_id="", file=file_ref, filename=filename, title=built["title"],
        platform="instagram",
        status="trial" if info["trial"] else "ok",
        remote_id=info["media_id"], scheduled_for_ist=fmt(now_ist()),
        trial="yes" if info["trial"] else "no",
    )
    return f"{'trial' if info['trial'] else 'ok'} {info['media_id']} ({info['size_mb']}M)"


def _fail(file_ref: str, filename: str, built: dict, platform: str, exc: Exception) -> str:
    msg = str(exc).splitlines()[0][:300]
    print(f"[{platform}] FAIL: {msg}")
    state_store.log_row(file=file_ref, filename=filename, title=built["title"],
                        platform=platform, status="error", error=msg)
    state_store.learn(f"{platform} fail ({filename}): {msg}")
    return f"error: {msg}"


# ------------------------------------------------------------------ commands
def cmd_upload(args) -> int:
    text = load_job_file(args.job) if args.job else {}
    if args.title:
        text["title"] = args.title
    if args.caption:
        text["caption"] = args.caption
    if args.tags:
        text["tags"] = args.tags
    if args.playlist:
        text["playlist"] = args.playlist

    when = parse_when(args.at)
    platforms = tuple(p.strip() for p in args.platforms.split(",") if p.strip())
    bad = [p for p in platforms if p not in PLATFORMS]
    if bad:
        return _usage(f"unknown platform {bad}")

    warn_slot_clash(platforms, when)

    if not args.publish:
        file_ref = drive_helper.extract_id(args.file) or "local-file"
        built = textkit.build(text, os.path.basename(args.file))
        try:
            privacy = yt.resolve_privacy(built, when)
        except yt.PrivacyNotSet as exc:
            privacy = f"BLOCKED — {exc}"
        print(json.dumps({
            "would_upload": args.file, "file_ref": file_ref,
            "privacy": privacy,
            "when": fmt(when) if when else "turant",
            "platforms": platforms, "text": built,
            "warnings": textkit.warnings(built),
            "yt_notify_subscribers": config.NOTIFY_SUBSCRIBERS,
            "playlist": yt.resolve_playlist(built) if not args.offline else text.get("playlist"),
        }, indent=2, ensure_ascii=False))
        print("\n(dry-run: kuch upload nahi hua — asli ke liye --publish)")
        return 0

    result = do_upload(args.file, text, when, platforms, publish=True, trial=args.trial)
    print(json.dumps(result["steps"], indent=2, ensure_ascii=False))
    return 0 if not any(str(v).startswith("error") for v in result["steps"].values()) else 1


def cmd_bulk(args) -> int:
    data = load_job_file(args.file)
    items = data if isinstance(data, list) else data.get("items", [])
    if not items:
        return _usage("bulk file me list of items chahiye")

    shared = {} if isinstance(data, list) else data.get("defaults", {})
    when_arg = parse_when(args.at) if args.at else None
    total = len(items)
    print(f"{total} video · platforms={args.platforms} · "
          f"{'sab @ ' + fmt(when_arg) if when_arg else 'har item ka apna time'}")

    # trial split (agar account allow karta hai)
    allowed, note = ig.trial_allowed(config.IG_USER_IDS[0]) if config.IG_USER_IDS else (False, "IG_USER_IDS khaali")
    print(f"[ig] {note}")
    flags = textkit.daily_plan(total, config.TRIAL_RATIO, allowed)
    if any(flags):
        print(f"[ig] trial split: {sum(flags)} trial / {total - sum(flags)} normal "
              f"(index {[i for i, f in enumerate(flags) if f]})")

    planned = []
    for idx, item in enumerate(items):
        when = when_arg or parse_when(item.get("when"))
        planned.append({"idx": idx, "when": when, "trial": flags[idx]})

    if not args.publish:
        print(json.dumps([
            {"file": i.get("file"),
             "when": fmt(planned[n]["when"]) if planned[n]["when"] else "turant",
             "trial": planned[n]["trial"]}
            for n, i in enumerate(items)
        ], indent=2, ensure_ascii=False))
        print("(dry-run: queue me kuch nahi daala — asli ke liye --publish)")
        return 0

    state_store.add_job({
        "kind": "bulk",
        "status": "pending" if any(p["when"] for p in planned) else "done",
        "items": [
            {
                "file": item.get("file"),
                "when": fmt(planned[i]["when"]) if planned[i]["when"] else fmt(now_ist()),
                "platforms": item.get("platforms") or [p.strip() for p in args.platforms.split(",")],
                "text": {**shared, **{k: v for k, v in item.items()
                                      if k not in ("file", "when", "platforms")}},
                "trial": planned[i]["trial"],
            }
            for i, item in enumerate(items)
        ],
    })

    rc = 0
    for i, item in enumerate(items):
        when = planned[i]["when"]
        if when and (when - now_ist()) > timedelta(minutes=20):
            print(f"[{i+1}/{total}] {item.get('file')} -> queue me @ {fmt(when)}")
            continue   # cron chalayega
        print(f"[{i+1}/{total}] {item.get('file')} -> abhi")
        res = do_upload(item.get("file"), {**shared, **{k: v for k, v in item.items()
                                                       if k not in ("file", "when", "platforms")}},
                        None, tuple(item.get("platforms") or args.platforms.split(",")),
                        trial=planned[i]["trial"])
        print(json.dumps(res["steps"], indent=2, ensure_ascii=False))
        if any(str(v).startswith("error") for v in res["steps"].values()):
            rc = 1
    return rc


def cmd_run(args) -> int:
    """Cron yahi chalata hai: due jobs, IG ke pending slot, aur (optional) insights."""
    slots = [args.slot] if args.slot else None
    jobs = state_store.due_jobs(slots=slots)
    if not jobs:
        print("Koi due job nahi.")
    for job in jobs:
        for item in state_store.job_items(job):
            when = state_store.parse_ist(item.get("when") or job.get("when"))
            if item.get("_missed"):
                print(f"!! {item.get('file')}: window nikal gaya (grace 90 min) — skip")
                state_store.learn(f"job {job.get('id')}: missed window for {item.get('file')}")
                continue
            if when and when > now_ist():
                continue
            platforms = tuple(item.get("platforms") or PLATFORMS)
            print(f"\n--- {item.get('file')} @ {fmt(now_ist())} ({'/'.join(platforms)})")
            merged = {**job.get("text", {}), **item.get("text", {})}
            res = do_upload(
                item.get("file"), merged, None, platforms, trial=item.get("trial"),
            )
            print(json.dumps(res["steps"], indent=2, ensure_ascii=False))
            item["_done"] = True
        state_store.update_job(job["id"], status="done", finished_at=fmt(now_ist()))

    if args.insights:
        import insights

        print(json.dumps(insights.collect(), indent=2))
        print(insights.write_report())

    print(state_store.write_summary())
    return 0


def cmd_list(args) -> int:
    jobs = state_store.load_jobs()
    if not jobs:
        print("Queue khaali hai.")
        return 0
    for job in jobs:
        if args.status and job.get("status") not in args.status.split(","):
            continue
        marker = {"pending": "⏳", "done": "✅", "cancelled": "🚫"}.get(job.get("status"), "?")
        files = state_store.job_files(job)
        print(f"{marker} {job.get('id')}  {job.get('kind', 'single')}  "
              f"{len(files)} file  {job.get('when', '')}")
        for item in state_store.job_items(job)[:10]:
            print(f"     - {item.get('file')}  @ {item.get('when')}  "
                  f"trial={'yes' if item.get('trial') else 'no'}  "
                  f"{'✓' if item.get('_done') else ''}")
    return 0


def cmd_cancel(args) -> int:
    ok = state_store.cancel_job(args.job_id)
    print("Cancelled." if ok else "Job nahi mila.")
    return 0 if ok else 1


def cmd_stop(args) -> int:
    path = state_store.stop_all(args.reason or "")
    print(f"STOP laga diya: {path}")
    print("Ab koi upload nahi hoga — cron uthega par kuch nahi karega.")
    return 0


def cmd_resume(args) -> int:
    if state_store.resume_all():
        print("STOP hata diya — uploads phir se chalenge.")
        return 0
    print("STOP.flag tha hi nahi.")
    return 0


def cmd_insights(args) -> int:
    import insights

    print(json.dumps(insights.collect(days=args.days), indent=2))
    path = insights.write_report()
    print(f"report: {path}")
    return 0


def _usage(msg: str) -> int:
    print(f"!! {msg}")
    return 2


# ------------------------------------------------------------------ CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Drive -> YT + IG + FB, aapke bole hisaab se")
    sub = ap.add_subparsers(dest="cmd", required=True)

    up = sub.add_parser("upload", help="ek video")
    up.add_argument("file", help="Drive link/ID ya local path")
    up.add_argument("--job", help="text wali JSON file")
    up.add_argument("--at", help="now | 18:30 | '2026-10-26 18:00' | 'in 2h'")
    up.add_argument("--platforms", default="youtube,instagram,facebook")
    up.add_argument("--title")
    up.add_argument("--caption")
    up.add_argument("--tags")
    up.add_argument("--playlist")
    up.add_argument("--trial", action="store_true", help="IG pe trial reel (200+ followers chahiye)")
    up.add_argument("--publish", action="store_true")
    up.add_argument("--offline", action="store_true", help="network/creds ke bina preview")
    up.set_defaults(func=cmd_upload)

    bl = sub.add_parser("bulk", help="5-10 file ek saath")
    bl.add_argument("file", help="items wali JSON")
    bl.add_argument("--at", help="sab ek hi time pe")
    bl.add_argument("--platforms", default="youtube,instagram,facebook")
    bl.add_argument("--publish", action="store_true")
    bl.set_defaults(func=cmd_bulk)

    rn = sub.add_parser("run", help="due jobs chalao (cron)")
    rn.add_argument("--publish", action="store_true")
    rn.add_argument("--slot", help="cron tick jaise 10:10 (test ke liye)")
    rn.add_argument("--insights", action="store_true")
    rn.set_defaults(func=cmd_run)

    ls = sub.add_parser("list", help="queue dekho")
    ls.add_argument("--status")
    ls.set_defaults(func=cmd_list)

    cn = sub.add_parser("cancel", help="job cancel")
    cn.add_argument("job_id")
    cn.set_defaults(func=cmd_cancel)

    st = sub.add_parser("stop", help="sab upload turant band (kill switch)")
    st.add_argument("--reason", default="")
    st.set_defaults(func=cmd_stop)

    rs = sub.add_parser("resume", help="STOP hatao, uploads wapas chalu")
    rs.set_defaults(func=cmd_resume)

    ins = sub.add_parser("insights", help="performance data")
    ins.add_argument("--days", type=int, default=30)
    ins.set_defaults(func=cmd_insights)

    args = ap.parse_args(argv)
    state_store.ensure_dirs()

    if args.cmd in ("upload", "bulk") and getattr(args, "publish", False):
        problems = config.missing()
        if problems:
            print("!! Config adhura — publish rok diya:")
            for p in problems:
                print("   -", p)
            return 2

    try:
        lock = state_store.RunLock()
        lock.__enter__()
    except RuntimeError as exc:
        print(exc)
        return 0
    try:
        return args.func(args)
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        lock.__exit__(None, None, None)


if __name__ == "__main__":
    sys.exit(main())
