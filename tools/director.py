#!/usr/bin/env python3
"""director — decide which skills a job needs, before any of them run.

The problem this solves: maker carries several skills (earshot, hyperframes,
openmontage) and a dozen engine modules, and they were sitting unused because
nothing connected a job's requirements to the tool that answers them.

The director reads a brief and returns a PLAN: an ordered list of steps, each
naming the skill, the exact command, why it is there, and the licence of the
thing being invoked.

Licence rule, enforced here and not by convention:
  permissive  -> may be imported or run in-process
  agpl        -> SUBPROCESS ONLY. Never imported. Never vendored into maker.

Usage:
    python3 tools/director.py --brief jobs/x/brief.json
    python3 tools/director.py --requirements hook,pacing,audio_check
"""
from __future__ import annotations
import argparse, json, os, sys

# ---------------------------------------------------------------- registry
SKILLS = {
    "earshot": {
        "what": "hears a film: describe, timeline, critique, forge SFX, match",
        "licence": "permissive",
        "install": "pip install -e skills/earshot  (CPU torch)",
        "answers": ["audio_check", "pacing", "sfx", "sync", "loudness", "hook"],
    },
    "hyperframes": {
        "what": "write HTML, render video — built for agents",
        "licence": "apache-2.0",
        "install": "npx hyperframes",
        "answers": ["render", "motion_graphics", "kinetic_text", "titles"],
    },
    "openmontage": {
        "what": "agentic video production pipelines",
        "licence": "agpl-3.0",
        "install": "clone only — SUBPROCESS, never imported",
        "answers": ["full_pipeline", "multi_scene", "agentic_edit"],
    },
    "engine/transition": {"what": "12 effects", "licence": "in-repo",
                          "answers": ["transition", "transitions"]},
    "engine/rhythm":     {"what": "beat + cut timing", "licence": "in-repo",
                          "answers": ["pacing", "cuts"]},
    "engine/burst":      {"what": "mid-video burst punches", "licence": "in-repo",
                          "answers": ["energy", "retention"]},
    "engine/grade":      {"what": "colour, contrast", "licence": "in-repo",
                          "answers": ["look"]},
    "engine/text":       {"what": "titles, rank lists, karaoke", "licence": "in-repo",
                          "answers": ["titles", "rank_list"]},
    "engine/qc":         {"what": "frame + loudness QC gate", "licence": "in-repo",
                          "answers": ["qc"]},
    "kokoro":            {"what": "voice, 54 voices, 330 MB, local", "licence": "apache-2.0",
                          "answers": ["voice"]},
}

# requirement -> ordered steps. Ordered because some steps must precede others.
PLAN = {
    "hook":        [("earshot", "describe --top 10", "what do the first 2 s actually sound like")],
    "voice":       [("kokoro", "create(voice=am_onyx, speed=1.2)", "speak the judgment lines")],
    "audio_check": [("earshot", "timeline --detail normal", "events, sections, loudness, beats, sync")],
    "pacing":      [("engine/rhythm", "cuts from beat times", "cut where the audio turns"),
                    ("earshot", "timeline --cues", "does the picture land on the sound")],
    "titles":      [("engine/text", "two-line title + rank list", "reference chrome")],
    "energy":      [("engine/burst", "auto_bursts", "mid-video punches, 15-25% of runtime")],
    "transitions": [("engine/transition", "pick per seam", "12 effects")],
    "look":        [("engine/grade", "per-shot grade", "match shots to each other")],
    "sfx":         [("earshot", "forge <spec>", "generate the SFX in code, no samples")],
    "render":      [("engine/build", "frames -> mp4", "or hyperframes if HTML-driven")],
    "qc":          [("engine/qc", "pass/fail gate", "-11 LUFS, no black frames, no clipping"),
                    ("earshot", "critique --fast", "scorecard against launch films")],
}

ORDER = ["hook", "voice", "titles", "pacing", "energy", "transition", "transitions",
         "look", "sfx", "render", "audio_check", "qc"]


def plan(requirements):
    unknown = [r for r in requirements if r not in PLAN]
    steps, seen, notes = [], set(), []
    for r in ORDER:
        if r not in requirements:
            continue
        for skill, cmd, why in PLAN[r]:
            key = (skill, cmd)
            if key in seen:
                continue
            seen.add(key)
            meta = SKILLS.get(skill, {})
            steps.append({
                "req": r, "skill": skill, "command": cmd, "why": why,
                "licence": meta.get("licence", "unknown"),
                "isolate": meta.get("licence") == "agpl-3.0",
            })
    if "audio_check" not in requirements and "qc" in requirements:
        notes.append("qc without audio_check: you are gating loudness without ever "
                     "hearing the mix. Add audio_check.")
    if "hook" not in requirements:
        notes.append("no hook step: nothing measures the first 2 s, which is where "
                     "retention is decided.")
    return {"requirements": requirements, "steps": steps,
            "unknown": unknown, "notes": notes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", help="job.json with a 'requirements' list")
    ap.add_argument("--requirements", help="comma separated")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.brief:
        req = json.load(open(a.brief)).get("requirements", [])
    elif a.requirements:
        req = [x.strip() for x in a.requirements.split(",") if x.strip()]
    else:
        ap.error("need --brief or --requirements")

    p = plan(req)
    if a.json:
        print(json.dumps(p, indent=2))
        return 0

    print(f"requirements: {', '.join(p['requirements'])}\n")
    for i, s in enumerate(p["steps"], 1):
        flag = "  [AGPL — subprocess only]" if s["isolate"] else ""
        print(f"{i:2}. {s['skill']:<20} {s['command']}{flag}")
        print(f"    because: {s['why']}  ({s['licence']})")
    for n in p["notes"]:
        print(f"\n! {n}")
    for u in p["unknown"]:
        print(f"\n? unknown requirement: {u}  (add it to PLAN)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
