#!/usr/bin/env python3
"""Fetch only legally usable media, and write the credit record with it.

Licence rule, hard-coded: CC0, Public Domain Mark, CC BY. Nothing else.
No "unknown licence", no NC, no ND. If search returns nothing clean we say
so and stop — we do not substitute a lower-quality right.

    python3 engine/scripts/fetch_assets.py --job jobs/demo.json --what images
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))
import tools as T

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--what", choices=["images", "audio", "both"], default="both")
    ap.add_argument("--assets", default=None)
    a = ap.parse_args()

    job = json.load(open(a.job))
    root = os.path.dirname(os.path.abspath(a.job))
    assets = a.assets or os.path.join(root, "assets")
    os.makedirs(assets, exist_ok=True)

    credits = []
    if a.what in ("images", "both"):
        for b in job.get("beats", []):
            q = b.get("query")
            if not q:
                continue
            recs = T.search_images(q, 8)
            if not recs:
                print(f"  [{b['id']}] no CC0/PD/CC BY image for: {q}")
                continue
            got = T.download(recs[0], assets)
            b["image"] = os.path.basename(got["path"])
            credits.append({"beat": b["id"], **{k: got[k] for k in
                            ("title", "creator", "license", "license_version", "source", "landing", "attribution")}})
            print(f"  [{b['id']}] {got['attribution'][:90]}")
    if a.what in ("audio", "both") and job.get("music_query"):
        recs = T.search_audio(job["music_query"], 8)
        if recs:
            got = T.download(recs[0], assets)
            job["music"] = os.path.basename(got["path"])
            credits.append({"role": "music", **{k: got[k] for k in
                            ("title", "creator", "license", "license_version", "source", "landing", "attribution")}})
            print(f"  [music] {got['attribution'][:90]}")

    json.dump(job, open(a.job, "w"), indent=1)
    json.dump(credits, open(os.path.join(assets, "credits.json"), "w"), indent=1)
    print(f"\ncredits written: {len(credits)}")

if __name__ == "__main__":
    main()
