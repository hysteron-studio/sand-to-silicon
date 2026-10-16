"""39 - The Server. One liquid-cooled rack-scale system in engraved elevation: 18 compute trays
(72 accelerators, 36 CPUs, every outline drawn) above and below 9 switch trays, a spine of
chip-to-chip copper down the back (one line per accelerator), and two coolant loops (accent)
threading every tray from the supply manifold to the return."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "39 - The Server", "title": "The Server", "seed": SEED,
  "gpus": 72, "cpus": 36, "compute_trays": 18, "switch_trays": 9, "domain_bandwidth_TBps": 130, "per_gpu_TBps": 1.8,
  "cooling": "liquid",
  "mapping": {
    "rack": "elevation; top and bottom power shelves, 10 compute trays, 9 switch trays, 8 compute trays",
    "compute tray": "4 accelerator outlines (with HBM sites) + 2 CPU outlines",
    "switch tray": "2 switch chips and a row of port cages",
    "spine": "72 vertical copper lines at the left, one per accelerator, tapping its tray",
    "coolant": "supply and return manifolds on the right, every tray looped through its 6 chips; accent",
  },
  "sources": [
    "https://www.nvidia.com/en-us/data-center/gb200-nvl72/ (72 GPUs, 36 CPUs, liquid-cooled, 130 TB/s NVLink domain)",
    "https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/overview.html (1.8 TB/s per GPU)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
rw = 1320; x0 = (OUT - rw) / 2; x1 = x0 + rw; yT = MARGIN + 10; yB = OUT - MARGIN - 10
cv.line([(x0, yT), (x1, yT), (x1, yB), (x0, yB), (x0, yT)], 3.2)
cv.line([(x0 + 26, yT), (x0 + 26, yB)], 1.4); cv.line([(x1 - 26, yT), (x1 - 26, yB)], 1.4)
for y in np.arange(yT + 20, yB, 22):
    cv.dot(x0 + 13, y, 2.4); cv.dot(x1 - 13, y, 2.4)
slots = ['P', 'P'] + ['C'] * 10 + ['S'] * 9 + ['C'] * 8 + ['P', 'P']
H = (yB - yT - 20) / len(slots)
xi0, xi1 = x0 + 150, x1 - 170
sup, ret = x1 - 120, x1 - 70
gpu_ports = []; trays = []
for k, t in enumerate(slots):
    y = yT + 10 + k * H; yc = y + H / 2
    cv.line([(x0 + 40, y + 4), (x1 - 40, y + 4), (x1 - 40, y + H - 4), (x0 + 40, y + H - 4), (x0 + 40, y + 4)], 1.4)
    if t == 'P':
        for xx in np.arange(x0 + 70, x1 - 60, 36): cv.seg(xx, y + 12, xx, y + H - 12, 1.0)
        continue
    if t == 'S':
        for cxx in (xi0 + 230, xi0 + 560):
            q = [(cxx - 70, yc - H * 0.3), (cxx + 70, yc - H * 0.3), (cxx + 70, yc + H * 0.3), (cxx - 70, yc + H * 0.3)]
            cv.line(q + [q[0]], 1.4); cv.hatch_poly(q, 45, 5, 0.7)
        for xx in np.arange(xi0 + 700, xi1, 16): cv.line([(xx, yc - 9), (xx + 11, yc - 9), (xx + 11, yc + 9), (xx, yc + 9), (xx, yc - 9)], 0.9)
        trays.append((yc, [xi0 + 230, xi0 + 560]))
        continue
    # compute tray: CPU, GPU, GPU, CPU, GPU, GPU
    chips = []
    xs = np.linspace(xi0 + 40, xi1 - 40, 6)
    for j, cxx in enumerate(xs):
        if j in (0, 3):
            w = 46; q = [(cxx - w, yc - H * 0.28), (cxx + w, yc - H * 0.28), (cxx + w, yc + H * 0.28), (cxx - w, yc + H * 0.28)]
            cv.line(q + [q[0]], 1.3)
        else:
            w = 62; q = [(cxx - w, yc - H * 0.34), (cxx + w, yc - H * 0.34), (cxx + w, yc + H * 0.34), (cxx - w, yc + H * 0.34)]
            cv.line(q + [q[0]], 1.8)
            for s in (-1, 1):
                for m in range(4): cv.line([(cxx + s * (w - 16), yc - H * 0.3 + m * H * 0.15), (cxx + s * (w - 4), yc - H * 0.3 + m * H * 0.15), (cxx + s * (w - 4), yc - H * 0.3 + m * H * 0.15 + H * 0.12), (cxx + s * (w - 16), yc - H * 0.3 + m * H * 0.15 + H * 0.12)], 0.8)
            q2 = [(cxx - w + 22, yc - H * 0.2), (cxx + w - 22, yc - H * 0.2), (cxx + w - 22, yc + H * 0.2), (cxx - w + 22, yc + H * 0.2)]
            cv.hatch_poly(q2, 45, 4.5, 0.8)
            gpu_ports.append((cxx - w, yc))
        chips.append(cxx)
    trays.append((yc, chips))
DATA["gpus_drawn"] = len(gpu_ports)
# spine: one line per GPU, from the tray down/up to a common bus at the left
for k, (gx, gy) in enumerate(gpu_ports):
    sx = x0 + 50 + (k % 72) * 1.25
    cv.line([(gx, gy + (k % 4 - 1.5) * 3), (sx + 8, gy + (k % 4 - 1.5) * 3), (sx, gy)], 0.6)
for k in range(72):
    sx = x0 + 50 + k * 1.25
    cv.seg(sx, yT + 10 + 2 * H, sx, yB - 10 - 2 * H, 0.5)
# coolant manifolds + loops
cv.seg(sup, yT + 10 + 2 * H, sup, yB - 10 - 2 * H, 6.0, 'accent'); cv.seg(ret, yT + 10 + 2 * H, ret, yB - 10 - 2 * H, 6.0, 'accent')
for yc, chips in trays:
    yl = yc + H * 0.08; yr = yc - H * 0.08
    pts = [(sup, yl)] + [(c, yl) for c in chips[::-1]] + [(chips[0] - 30, yl), (chips[0] - 30, yr)] + [(c, yr) for c in chips] + [(ret, yr)]
    cv.line(pts, 2.6, 'accent')
    for c in chips: cv.circle(c, yc, 7, 1.4, 'accent')
cv.plate_number(39)
write_data(39, DATA)
render(cv, 39, 'server')
