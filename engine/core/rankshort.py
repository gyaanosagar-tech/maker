"""rankshort — the Type-2 ranking short, built the way the references do it.

What this adds over compose.py:
    - persistent numbered list on the left, filling in as clips play
    - two-line title bar, colour change on line 2
    - thin progress bar at the bottom
    - a spoken judgment line per clip (baked text on screen, audio separate)
    - burst punches between clips
    - -11 LUFS master

The list and the title are on screen from the FIRST frame. That is the thing
that holds a viewer: they stay to see what #1 is.
"""
import os, json, subprocess


def FF():
    return os.environ.get('FFMPEG', 'ffmpeg')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import text as T
import grade as GR
import grid as G
import audio as AU


def _fit(role, s, maxw, start):
    return T.fit(role, s, maxw, start)


class RankShort:
    def __init__(self, spec: dict, out_dir: str):
        self.s = spec
        self.out = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.W, self.H = G.W, G.H
        self.fps = spec.get("fps", 30)

    # ---------------------------------------------------------------- drawing

    def _title_bar(self, img, d):
        l1 = self.s.get("title_line1", "")
        l2 = self.s.get("title_line2", "")
        c1 = tuple(self.s.get("title_color1", (255, 255, 255)))
        c2 = tuple(self.s.get("title_color2", (232, 26, 26)))
        y = int(self.H * 0.028)
        pad = 46
        band = Image.new("RGBA", (self.W, int(self.H * 0.13)), (0, 0, 0, 255))
        img.alpha_composite(band, (0, 0))
        f1 = _fit("headline", l1, self.W - pad * 2, 62)
        f2 = _fit("headline", l2, self.W - pad * 2, 62)
        w1 = d.textlength(l1, font=f1); w2 = d.textlength(l2, font=f2)
        d.text(((self.W - w1) / 2, y), l1, font=f1, fill=c1 + (255,))
        d.text(((self.W - w2) / 2, y + f1.size * 1.06), l2, font=f2, fill=c2 + (255,))

    def _rank_list(self, img, d, items, revealed):
        x = int(self.W * 0.045)
        y0 = int(self.H * 0.20)
        step = int(self.H * 0.062)
        fn = T.font("body", 44)
        fl = T.font("body", 34)
        for i, it in enumerate(items):
            on = i < revealed
            y = y0 + i * step
            num = str(i + 1)
            col = (255, 255, 255, 255) if on else (255, 255, 255, 70)
            d.text((x, y), num + ".", font=fn, fill=col,
                   stroke_width=4, stroke_fill=(0, 0, 0, 200))
            if on and it.get("label"):
                d.text((x + 46, y + 6), it["label"], font=fl,
                       fill=(255, 255, 255, 235), stroke_width=4,
                       stroke_fill=(0, 0, 0, 210))

    def _progress(self, img, d, frac):
        h = 8
        y = self.H - h - 4
        d.rectangle([0, y, self.W, y + h], fill=(0, 0, 0, 160))
        d.rectangle([0, y, int(self.W * frac), y + h], fill=(232, 26, 26, 255))

    def _handle(self, img, d):
        h = self.s.get("handle", "")
        if not h:
            return
        f = T.font("body", 34)
        w = d.textlength(h, font=f)
        d.text(((self.W - w) / 2, self.H - 96), h, font=f,
               fill=(255, 255, 255, 120))

    def _credit(self, img, d):
        c = self.s.get("credit", "")
        if not c:
            return
        f = T.font("credit", 26)
        w = d.textlength(c, font=f)
        d.text(((self.W - w) / 2, self.H - 58), c, font=f,
               fill=(255, 255, 255, 150))

    def _judgment(self, img, d, line):
        """The spoken line, on screen while it is spoken."""
        if not line:
            return
        f, lines = T.wrap("headline", line, int(self.W * 0.88), 74, 2)
        y = int(self.H * 0.62)
        for i, ln in enumerate(lines):
            if not ln:
                continue
            w = d.textlength(ln, font=f)
            x = (self.W - w) / 2
            d.text((x + 5, y + i * f.size * 1.1 + 5), ln, font=f, fill=(0, 0, 0, 220))
            d.text((x, y + i * f.size * 1.1), ln, font=f, fill=(255, 255, 255, 250))

    # ---------------------------------------------------------------- frame

    def frame(self, clip_img, idx, total_items, revealed, progress, line):
        img = clip_img.convert("RGBA")
        d = ImageDraw.Draw(img)
        self._title_bar(img, d)
        self._rank_list(img, d, self.s.get("items", []), revealed)
        self._judgment(img, d, line)
        self._progress(img, d, progress)
        self._handle(img, d)
        self._credit(img, d)
        return img.convert("RGB")

    # ---------------------------------------------------------------- build

    def build(self, frame_dir=None):
        """Yield frames. With frame_dir, write each PNG and yield the path —
        a 60 s 1080x1920 short does not fit in RAM on a 2 GB box."""
        shots = self.s["shots"]
        items = self.s.get("items", [])
        k = 0
        for si, sh in enumerate(shots):
            src_dir = sh["dir"]
            names = sorted(os.listdir(src_dir))
            n = len(names)
            for fi, name in enumerate(names):
                im = Image.open(os.path.join(src_dir, name)).convert("RGB")
                line = sh.get("line", "") if fi < n * 0.55 else ""
                fr = self.frame(im, si, len(items), sh.get("reveal", si + 1),
                                (si + fi / max(1, n)) / len(shots), line)
                im.close()
                if frame_dir:
                    p = os.path.join(frame_dir, f"f{k:05d}.png")
                    fr.save(p, compress_level=1)
                    yield p
                else:
                    yield fr
                k += 1

    def encode(self, out_mp4, bed=None, lufs=-11.0):
        """Frames -> video, then a measured, two-pass loudness master."""
        fd = os.path.join(self.out, "frames")
        os.makedirs(fd, exist_ok=True)
        n = len([p for p in os.listdir(fd) if p.endswith(".png")])
        dur = n / float(self.fps)

        wav = os.path.join(self.out, "bed.wav")
        if bed and os.path.exists(bed):
            subprocess.run([FF(), "-y", "-stream_loop", "-1", "-i", bed,
                            "-t", f"{dur:.3f}", "-ar", "48000", "-ac", "2",
                            "-af", "volume=0.55", wav], capture_output=True)
        else:
            subprocess.run([FF(), "-y", "-f", "lavfi", "-i",
                            f"anullsrc=r=48000:cl=stereo:d={dur:.3f}", wav],
                           capture_output=True)

        tmp = os.path.join(self.out, "pre.mp4")
        subprocess.run([FF(), "-y", "-framerate", str(self.fps),
                        "-i", os.path.join(fd, "f%05d.png"), "-i", wav,
                        "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", tmp], capture_output=True)

        cur = tmp
        for _ in range(5):
            got = AU.loudness(cur)
            if got == got and abs(got - lufs) <= 0.6:
                break
            delta = max(-14.0, min(14.0, lufs - (got if got == got else lufs)))
            nxt = os.path.join(self.out, f"tune{_}.mp4")
            r = subprocess.run([FF(), "-y", "-i", cur, "-c:v", "copy", "-af",
                                f"volume={delta:.2f}dB,loudnorm=I={lufs}:TP=-1.5:LRA=11",
                                "-c:a", "aac", "-b:a", "192k", nxt],
                               capture_output=True)
            if r.returncode != 0 or not os.path.exists(nxt):
                break
            cur = nxt
        subprocess.run([FF(), "-y", "-i", cur, "-c", "copy", "-movflags",
                        "+faststart", out_mp4], capture_output=True)
        return out_mp4
