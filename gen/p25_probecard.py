"""25 - The Probe Card. A field of MEMS micro-cantilever probes seen from just above the
wafer: 9 rows of 13 springs receding in perspective, each a post, a beam and a tip poised
over its own pad; in one diagonal band the card has come down, the tips touch and the beams
flex, and their pads light in accent."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "25 - The Probe Card", "title": "The Probe Card", "seed": SEED,
  "probe_type": "MEMS micro-cantilever", "full_wafer_mm": 300, "rows": 9, "cols": 13,
  "note": "the maker publishes no pin count; geometry (beam ~ 6x tip height, overtravel ~ 1/3 tip height) is illustrative",
  "mapping": {
    "perspective": "rows recede with scale 0.42 + 0.58 (r/8)^1.3; drawn back to front with occlusion",
    "probe": "post + beam + hooked tip; beam length 0.62 x pitch, tip 0.42 h, gap 0.32 h",
    "contact": "probes inside a seeded diagonal band touch down: beam drawn bent by the overtravel, pad in accent",
  },
  "sources": ["https://www.jem-net.co.jp/en/products/probe (MEMS micro-cantilever probe cards, full 300 mm wafer probing)"],
}
cv = Canvas(SEED); rng = cv.rng
rows, cols = DATA["rows"], DATA["cols"]
vx, vy = OUT / 2, -400                                  # vanishing point
base_y = 2500; touched = 0
band_c, band_w = rng.uniform(-0.15, 0.15), 0.13
for r in range(rows - 1, -1, -1):
    k = 0.42 + 0.58 * (r / (rows - 1)) ** 1.3          # scale (front row = 1)
    y = vy + (base_y - vy) * k
    pitch = 172 * k; x0 = vx - pitch * (cols - 1) / 2
    h = 150 * k
    for c in range(cols):
        L = 0.62 * pitch; x = x0 + c * pitch - L / 2
        u = c / (cols - 1) - r / (rows - 1) * 0.9
        touch = abs(u - 0.05 - band_c) < band_w
        # pad
        pw, ph = 30 * k, 9 * k
        pad = [(x + L - pw, y), (x + L + pw, y), (x + L + pw * 0.8, y - ph), (x + L - pw * 0.8, y - ph)]
        cv.erase_poly(pad)
        if touch: cv.poly(pad, 'accent'); touched += 1
        else: cv.line(pad + [pad[0]], 1.2 * k)
        # probe: post, long beam, short tip; the tip sits over the pad centre
        tipL = 0.42 * h; gap = 0.32 * h
        top = y - ph * 0.5 - gap - tipL
        ot = gap if touch else 0
        post = [(x - 8 * k, top - 0.7 * h), (x + 8 * k, top - 0.7 * h), (x + 8 * k, top + 7 * k), (x - 8 * k, top + 7 * k)]
        cv.erase_poly(post); cv.line(post + [post[0]], 1.5 * k); cv.hatch_poly(post, 90, 3.6 * k, 0.9 * k)
        beam = [(x + t * L, top + ot * (t ** 2) * (3 - 2 * t)) for t in np.linspace(0, 1, 16)]
        ex, ey = beam[-1]
        cv.line(beam, 3.0 * k); cv.line([(px, py + 6 * k) for px, py in beam], 1.1 * k)
        tip_y = ey + tipL
        cv.line([(ex - 5 * k, ey + 6 * k), (ex, tip_y), (ex + 5 * k, ey + 6 * k)], 2.0 * k)
        if touch:
            cv.line([(ex + 40 * k * math.cos(a), tip_y + 12 * k * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)], 2.2 * k, 'accent')
            for a in np.linspace(-2.6, -0.5, 4):
                cv.seg(ex + 18 * k * math.cos(a), tip_y + 18 * k * math.sin(a), ex + 34 * k * math.cos(a), tip_y + 34 * k * math.sin(a), 1.6 * k, 'accent')
DATA["touching"] = touched
cv.plate_number(25)
write_data(25, DATA)
render(cv, 25, 'probecard')
