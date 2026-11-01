"""Timeline — frame-exact shot list.

The rule that prevents every sync drift we have hit:
    build the shot list in FRAMES, derive seconds from it, never the reverse.
Audio is trimmed to the frame count, not the other way round.
"""
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

FPS = 30

@dataclass
class Beat:
    id: str
    image: str
    line: str = ""
    tag: str = ""
    narration: Optional[str] = None      # path to audio
    pad: float = 0.10                    # breath after the line
    frames: int = 0                      # computed
    start_frame: int = 0                 # computed
    move: int = 0                        # ken burns pattern index
    trans: str = "whip"                  # whip | cut | fade

@dataclass
class Timeline:
    beats: List[Beat] = field(default_factory=list)
    head_frames: int = int(0.6 * FPS)
    tail_frames: int = int(2.4 * FPS)
    fps: int = FPS
    mode: str = "free"                 # "free" (narration) | "grid" (music)
    grid: List[float] = field(default_factory=list)
    weights: List[float] = None
    total_frames: int = 0

    def build(self, lengths: dict) -> "Timeline":
        """free mode: shot length = narration + pad. Original behaviour."""
        cur = self.head_frames
        for i, b in enumerate(self.beats):
            nar = lengths.get(b.id, 0.0)
            b.frames = max(1, int(round((nar + b.pad) * self.fps)))
            b.start_frame = cur
            b.move = i % 6
            b.trans = "fade" if i == 0 else "whip"
            cur += b.frames
        self.total_frames = cur + self.tail_frames
        return self

    def build_on_grid(self) -> "Timeline":
        """grid mode: every shot is a whole number of beats.

        This is what makes cuts land on the music. In free mode a cut happens
        wherever the sentence ends; here it happens on a beat, and the picture
        is what moves to meet the audio.
        """
        import rhythm as R
        span = (self.grid[-1] - self.grid[0]) if len(self.grid) > 1 else 0.0
        shots = R.shot_lengths_from_grid(
            self.grid, len(self.beats), span, self.weights)
        cur = self.head_frames
        for i, (start_s, dur_s) in enumerate(shots):
            b = self.beats[i]
            b.frames = max(1, int(round(dur_s * self.fps)))
            b.start_frame = cur
            b.move = i % 6
            b.trans = "fade" if i == 0 else "cut"
            cur += b.frames
        for b in self.beats[len(shots):]:
            b.frames = max(1, int(round(0.5 * self.fps)))
            b.start_frame = cur
            cur += b.frames
        self.total_frames = cur + self.tail_frames
        return self

    def cut_times(self) -> List[float]:
        return [b.start_frame / self.fps for b in self.beats[1:]]

    @property
    def duration(self) -> float:
        return self.total_frames / self.fps

    def to_dict(self):
        return {"fps": self.fps, "mode": self.mode,
                "total_frames": self.total_frames,
                "duration": round(self.duration, 3),
                "beats": [asdict(b) for b in self.beats]}

    def save(self, path):
        json.dump(self.to_dict(), open(path, "w"), indent=1)

    @classmethod
    def from_job(cls, job: dict) -> "Timeline":
        beats = [Beat(**{k: v for k, v in b.items()
                         if k in Beat.__dataclass_fields__}) for b in job["beats"]]
        return cls(beats=beats,
                   head_frames=int(job.get("head_seconds", 0.6) * FPS),
                   tail_frames=int(job.get("tail_seconds", 2.4) * FPS),
                   mode=job.get("mode", "free"),
                   grid=job.get("grid", []),
                   weights=job.get("weights"))
