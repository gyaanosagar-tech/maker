import sys, os, json, time
sys.path.insert(0, "../../engine/core")
from rankshort import RankShort
import burst as BU
from PIL import Image

spec = json.load(open("job.json"))
rs = RankShort(spec, "build")
fd = "build/frames"; os.makedirs(fd, exist_ok=True)

# counts: C 114, D 120, A 72, B 127  -> seams at 3.8s, 7.8s, 10.2s
BURSTS = [(3.72, "flash", 0.26), (7.72, "glitch", 0.30), (10.15, "flash", 0.26)]
bt = {int(a*30)+i: (s, d, i/30.0) for a, s, d in BURSTS for i in range(int(d*30)+1)}

t=time.time(); n=0
for k, p in enumerate(rs.build(fd)):
    if k in bt:
        s, d, tt = bt[k]
        im = Image.open(p).convert("RGB"); im = BU.apply(im, s, tt, d, intensity=0.9)
        im.save(p, compress_level=1); im.close()
    n+=1
    if n % 100 == 0: print(f"  {n}f {time.time()-t:.0f}s", flush=True)
print("total:", n, f"({n/30:.1f}s)")
print("out:", rs.encode("base.mp4", bed=spec["bed"], lufs=spec["lufs"]))
