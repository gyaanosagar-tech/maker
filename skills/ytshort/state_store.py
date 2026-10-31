"""
state_store.py — jobs.json (queue), Master_Log.csv, LEARNING_LOG.md, lock.

GitHub Actions har run me fresh machine aata hai, isliye state repo ke `state/`
folder me likhi jaati hai aur workflow ke end me commit hoti hai.
"""
from __future__ import annotations

import csv
import fcntl
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import config

IST = timezone(timedelta(hours=5, minutes=30))

LOG_FIELDS = [
    "ts_ist", "job_id", "file", "filename", "title", "platform", "status",
    "remote_id", "url", "scheduled_for_ist", "playlist", "trial", "error",
]


def now_ist() -> datetime:
    return datetime.now(IST)


def ensure_dirs() -> None:
    for path in (config.STATE_DIR, config.TMP_DIR, config.ANALYSIS_DIR):
        os.makedirs(path, exist_ok=True)


def fmt(dt: datetime) -> str:
    return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M")


def parse_ist(raw: str) -> datetime | None:
    for pattern in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, pattern).replace(tzinfo=IST)
        except (ValueError, TypeError):
            continue
    return None


# ------------------------------------------------------------------ jobs
def load_jobs() -> list[dict]:
    ensure_dirs()
    if not os.path.exists(config.QUEUE_FILE):
        return []
    try:
        with open(config.QUEUE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError:
        return []


def save_jobs(jobs: list[dict]) -> None:
    ensure_dirs()
    tmp = config.QUEUE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, config.QUEUE_FILE)


def add_job(job: dict) -> dict:
    jobs = load_jobs()
    job.setdefault("id", uuid.uuid4().hex[:8])
    job.setdefault("status", "pending")
    job.setdefault("created_at", fmt(now_ist()))
    jobs.append(job)
    save_jobs(jobs)
    return job


def get_job(job_id: str) -> dict | None:
    return next((j for j in load_jobs() if j.get("id") == job_id), None)


def update_job(job_id: str, **changes) -> dict | None:
    jobs = load_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            job.update(changes)
            save_jobs(jobs)
            return job
    return None


def pending_jobs() -> list[dict]:
    return [j for j in load_jobs() if j.get("status") == "pending"]


def due_jobs(grace_minutes: int = 90, slots: list[str | None] = None) -> list[dict]:
    """
    Kaun sa job ab chalna chahiye.

    Ek job = ek video (job["file"]) ya bulk (job["items"]).
    Har item ka apna `when` ho sakta hai (bulk me alag-alag time).

    slots = cron ticks. Ek job sirf tab chalta hai jab uska minat cron tick ke
    bracket me aata ho (ya slot nikal chuka ho), taaki job ek hi baar chale.
    """
    now = now_ist()
    out = []
    for job in pending_jobs():
        for item in job_items(job):
            if item.get("_done"):
                continue
            when_raw = item.get("when") or job.get("when")
            if not when_raw:
                # on-demand job ("abhi upload karo") — time ka intezaar nahi
                out.append(job)
                break
            when = parse_ist(when_raw)
            if not when:
                # time parse nahi hua — turant chala do, chup-chaap skip mat karo
                out.append(job)
                break
            if now < when:
                continue
            if now > when + timedelta(minutes=grace_minutes):
                item["_missed"] = True
                out.append(job)
                break
            # cron bracket check: is tick ke 60 min me slot aaya?
            if slots and not _in_tick(when, now, slots):
                continue
            out.append(job)
            break
    return out


def _in_tick(slot: datetime, now: datetime, ticks: list[str | None]) -> bool:
    """Slot is cron tick ke window me hai? (har tick 1 ghanta, mm:10 pe)"""
    minutes = sorted({int(t.split(":")[1]) for t in ticks if t and ":" in t})
    if not minutes:
        return True
    m = minutes[0]
    tick_start = now.replace(minute=m, second=0, microsecond=0)
    return tick_start <= slot < tick_start + timedelta(hours=1)


def job_items(job: dict) -> list[dict]:
    """Bulk job ke items, ya single file — dono ek shape me."""
    if job.get("items"):
        return job["items"]
    return [{"file": job.get("file"), "when": job.get("when"),
             "platforms": job.get("platforms"), "text": job.get("text", {})}]


def job_files(job: dict) -> list[str]:
    return [i.get("file") for i in job_items(job) if i.get("file")]


STOP_FILE = None  # config.STATE_DIR/STOP.flag — emergency kill switch


def stop_flag_path() -> str:
    return stop_flag_path.__dict__.setdefault(
        "_p", os.path.join(config.STATE_DIR, "STOP.flag"))


def is_stopped() -> bool:
    """Emergency kill switch. File hai? -> sab upload band."""
    return os.path.exists(stop_flag_path())


def stop_all(reason: str = "") -> str:
    ensure_dirs()
    path = stop_flag_path()
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"{fmt(now_ist())} {reason}\n")
    return path


def resume_all() -> bool:
    path = stop_flag_path()
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def cancel_job(job_id: str) -> bool:
    return update_job(job_id, status="cancelled", cancelled_at=fmt(now_ist())) is not None


# ------------------------------------------------------------------ counters
def read_log() -> list[dict]:
    if not os.path.exists(config.MASTER_LOG):
        return []
    with open(config.MASTER_LOG, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def log_row(**row) -> None:
    ensure_dirs()
    new = not os.path.exists(config.MASTER_LOG)
    with open(config.MASTER_LOG, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_FIELDS, extrasaction="ignore")
        if new:
            writer.writeheader()
        row.setdefault("ts_ist", fmt(now_ist()))
        writer.writerow(row)


def is_done(file_ref: str, platform: str) -> bool:
    """Same file same platform pe pehle na chadhi ho."""
    return any(
        r.get("file") == file_ref and r.get("platform") == platform
        and r.get("status") in ("ok", "scheduled", "trial")
        for r in read_log()
    )


def count_today(platform: str, statuses=("ok", "scheduled", "trial")) -> int:
    today = now_ist().strftime("%Y-%m-%d")
    return sum(
        1 for r in read_log()
        if r.get("platform") == platform and r.get("status") in statuses
        and str(r.get("ts_ist", "")).startswith(today)
    )


def count_today_trial() -> int:
    today = now_ist().strftime("%Y-%m-%d")
    return sum(
        1 for r in read_log()
        if r.get("platform") == "instagram" and r.get("trial") == "yes"
        and str(r.get("ts_ist", "")).startswith(today)
    )


def slots_taken(platform: str) -> list[str]:
    return [r.get("scheduled_for_ist") for r in read_log()
            if r.get("platform") == platform and r.get("scheduled_for_ist")]


# ------------------------------------------------------------------ logs
def learn(note: str) -> None:
    ensure_dirs()
    new = not os.path.exists(config.LEARNING_LOG)
    with open(config.LEARNING_LOG, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# LEARNING_LOG\n\nHar run ki apni observations.\n\n")
        fh.write(f"- `{fmt(now_ist())}` — {note}\n")


def write_summary() -> str:
    path = os.path.join(config.STATE_DIR, "SUMMARY.md")
    ensure_dirs()
    rows = read_log()
    today = now_ist().strftime("%Y-%m-%d")
    lines = ["# Run Summary", "", f"Aaj: {today} · total rows: {len(rows)}", ""]
    lines += ["| Platform | Aaj | Total |", "|---|---|---|"]
    for p in ("youtube", "instagram", "facebook"):
        t = sum(1 for r in rows if r.get("platform") == p
                and str(r.get("ts_ist", "")).startswith(today)
                and r.get("status") in ("ok", "scheduled", "trial"))
        a = sum(1 for r in rows if r.get("platform") == p
                and r.get("status") in ("ok", "scheduled", "trial"))
        lines.append(f"| {p} | {t} | {a} |")
    pending = pending_jobs()
    if pending:
        lines += ["", "## Pending jobs", ""]
        for job in pending:
            lines.append(f"- `{job['id']}` {job.get('when', '')} · {len(job_files(job))} file")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


class RunLock:
    """Do run ek saath = double upload. Isliye lock."""

    def __init__(self, path: str | None = None):
        self.path = path or config.LOCK_FILE
        self.fh = None

    def __enter__(self):
        ensure_dirs()
        self.fh = open(self.path, "w")
        try:
            fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.fh.close()
            self.fh = None
            raise RuntimeError("Dusra run chal raha hai (lock busy) — skip")
        self.fh.write(str(os.getpid()))
        self.fh.flush()
        return self

    def __exit__(self, *exc):
        if self.fh:
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()
