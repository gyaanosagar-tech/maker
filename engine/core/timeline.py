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

    def build(self, lengths: dict) -> "Timeline":
        """lengths: {beat_id: seconds} of each narration clip."""
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

    @property
    def duration(self) -> float:
        return self.total_frames / self.fps

    def to_dict(self):
        return {"fps": self.fps, "total_frames": self.total_frames,
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
                   tail_frames=int(job.get("tail_seconds", 2.4) * FPS))
