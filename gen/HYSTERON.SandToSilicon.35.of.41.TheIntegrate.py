"""35 - The Integrate. A silicon interposer 3.3 times the size of one lithography field, in
plan: four ghosted 26 x 33 mm reticle tiles show how it had to be stitched, two logic dies
sit in the centre, eight memory stacks line the two sides, and between them run the dense
bands of wires (1,024 per stack, drawn one in sixteen) in accent."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "35 - The Integrate", "title": "The Integrate", "seed": SEED,
  "interposer_reticles": 3.3, "reticle_mm": [26, 33], "reticle_mm2": 858, "interposer_mm": [52.0, 54.5],
  "interposer_mm2": 2834, "logic_dies": 2, "logic_die_mm": [23, 25], "hbm_stacks": 8, "hbm_mm": [11, 11],
  "wires_per_stack": 1024, "wires_drawn_per_stack": 64,
  "mapping": {
    "scale": "34 px per mm",
    "ghost": "2 x 2 reticle fields, dashed, behind everything",
    "dies": "logic dies hatched as ruled compute blocks; memory stacks drawn as their 12 stacked die edges",
    "wires": "64 accent lines per stack, routed as a band to the facing die edge",
  },
  "sources": ["https://3dfabric.tsmc.com/english/dedicatedFoundry/technology/cowos.htm (CoWoS-S up to 3.3x reticle; CoWoS-L 3.5x in volume production since 2024)"],
}
cv = Canvas(SEED); rng = cv.rng
s = 34.0; Wm, Hm = DATA["interposer_mm"]
X0 = (OUT - Wm * s) / 2; Y0 = (OUT - Hm * s) / 2 - 10
def R(x, y): return (X0 + x * s, Y0 + y * s)
def rect(x0, y0, x1, y1, w=2.0, layer='ink'):
    p = [R(x0, y0), R(x1, y0), R(x1, y1), R(x0, y1)]; cv.line(p + [p[0]], w, layer); return p
# ghost reticles: dashed
for gx in range(2):
    for gy in range(2):
        x0, y0 = gx * 26, gy * 33 - (66 - Hm) / 2
        for (a, b) in [((x0, y0), (x0 + 26, y0)), ((x0 + 26, y0), (x0 + 26, y0 + 33)), ((x0 + 26, y0 + 33), (x0, y0 + 33)), ((x0, y0 + 33), (x0, y0))]:
            n = 60
            for k in range(0, n, 2):
                p0 = R(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n); p1 = R(a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                cv.seg(*p0, *p1, 1.0)
outer = rect(0, 0, Wm, Hm, 3.0)
# logic dies
lw, lh = DATA["logic_die_mm"]
dies = [(Wm / 2 - lw / 2, Hm / 2 - lh - 0.6), (Wm / 2 - lw / 2, Hm / 2 + 0.6)]
for x0, y0 in dies:
    p = rect(x0, y0, x0 + lw, y0 + lh, 2.4)
    for bx in range(6):
        for by in range(5):
            q = [R(x0 + 0.8 + bx * (lw - 1.6) / 6 + 0.2, y0 + 0.8 + by * (lh - 1.6) / 5 + 0.2), R(x0 + 0.8 + (bx + 1) * (lw - 1.6) / 6 - 0.2, y0 + 0.8 + by * (lh - 1.6) / 5 + 0.2),
                 R(x0 + 0.8 + (bx + 1) * (lw - 1.6) / 6 - 0.2, y0 + 0.8 + (by + 1) * (lh - 1.6) / 5 - 0.2), R(x0 + 0.8 + bx * (lw - 1.6) / 6 + 0.2, y0 + 0.8 + (by + 1) * (lh - 1.6) / 5 - 0.2)]
            cv.hatch_poly(q, 0 if (bx + by) % 2 else 90, 8, 0.7); cv.line(q + [q[0]], 1.0)
# memory stacks
hw = 10.0; gap = (Hm - 4 * hw) / 5
stacks = []
for side in (0, 1):
    xs = 1.2 if side == 0 else Wm - 1.2 - hw
    for k in range(4):
        ys = gap + k * (hw + gap); stacks.append((xs, ys, side))
        for m in range(12):
            d = m * 0.22; rect(xs + d, ys + d, xs + hw - d, ys + hw - d, 1.6 if m == 0 else 0.7)
# wire bands
for xs, ys, side in stacks:
    x_from = xs + hw if side == 0 else xs
    x_to = dies[0][0] if side == 0 else dies[0][0] + lw
    y_c = ys + hw / 2
    die_y0 = dies[0][1] if y_c < Hm / 2 else dies[1][1]
    yt_c = min(max(y_c, die_y0 + 3), die_y0 + lh - 3)
    for w in range(64):
        f = (w - 31.5) / 64
        y1 = y_c + f * hw * 0.8; y2 = yt_c + f * 5.5
        xm1 = x_from + (x_to - x_from) * 0.35; xm2 = x_from + (x_to - x_from) * 0.65
        pts = [R(x_from, y1), R(xm1, y1), R(xm2, y2), R(x_to, y2)]
        cv.line(pts, 1.5, 'accent')
cv.plate_number(35)
write_data(35, DATA)
render(cv, 35, 'integrate')
