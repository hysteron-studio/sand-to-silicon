"""17 - The Gas. Tungsten hexafluoride (WF6, 99.9995% pure) streams from a showerhead into
a contact hole and is reduced to metal, WF6 + 3 H2 -> W + 6 HF: molecules are stippled
octahedral glyphs, the plug grows as columnar tungsten grains in accent, and among 200,000
molecules exactly one (5 ppm) is a foreign one, ringed."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "17 - The Gas", "title": "The Gas", "seed": SEED,
  "gas": "WF6", "purity_pct": 99.9995, "impurity_ppm_max": 5,
  "reaction": "WF6 + 3 H2 -> W + 6 HF",
  "contact": {"width_nm": 30, "depth_nm": 150, "aspect_ratio": 5},
  "mapping": {
    "molecules": "every stipple pair is a WF6 molecule (W dot + 6 F ticks); 200,000 sampled positions -> 5 ppm = 1 foreign molecule, ringed",
    "flow": "molecules follow the streamlines of a showerhead jet funnelling into the contact",
    "plug": "the filled part of the contact as columnar tungsten grains in accent, grown from the walls and floor",
  },
  "sources": [
    "https://www.cgc-jp.com/products/detail/gases.html (WF6 >=99.9995% for contact plugs)",
    "https://www.cgc-jp.com/products/detail/etching.html",
  ],
}
cv = Canvas(SEED); rng = cv.rng
cx = OUT / 2
y_head, y_surf = 600, 1640
cw, cd = 300, 1500 * 0.6           # contact 30 nm x 150 nm scaled (AR 5 -> 300 x 900 px)
y_floor = y_surf + cd
# showerhead plate
cv.line([(MARGIN + 60, y_head), (OUT - MARGIN - 60, y_head)], 3.0)
cv.line([(MARGIN + 60, y_head - 46), (OUT - MARGIN - 60, y_head - 46)], 2.0)
cv.hatch_poly([(MARGIN + 60, y_head - 46), (OUT - MARGIN - 60, y_head - 46), (OUT - MARGIN - 60, y_head), (MARGIN + 60, y_head)], -45, 10, 1.0)
nozz = np.linspace(MARGIN + 140, OUT - MARGIN - 140, 17)
for x in nozz: cv.erase_poly([(x - 9, y_head - 47), (x + 9, y_head - 47), (x + 9, y_head + 2), (x - 9, y_head + 2)])
# dielectric with contact hole
diel = [(MARGIN, y_surf), (cx - cw / 2, y_surf), (cx - cw / 2, y_floor), (cx + cw / 2, y_floor), (cx + cw / 2, y_surf),
        (OUT - MARGIN, y_surf), (OUT - MARGIN, y_floor + 360), (MARGIN, y_floor + 360)]
cv.line(diel[:6], 2.6)
cv.hatch_poly(diel, 30, 15, 1.0)
cv.line([(MARGIN, y_floor + 360), (OUT - MARGIN, y_floor + 360)], 1.8)
# plug: columnar grains growing from walls and floor up to a fill level
fill = y_surf + cd * 0.38
plug = [(cx - cw / 2, fill), (cx + cw / 2, fill), (cx + cw / 2, y_floor), (cx - cw / 2, y_floor)]
cv.erase_poly(plug)
cv.line([plug[0], plug[3], plug[2], plug[1]], 2.6)
ng = 0
for x in np.linspace(cx - cw / 2 + 8, cx + cw / 2 - 8, 22):
    yy = y_floor
    while yy > fill + 8:
        L = rng.uniform(40, 140); y1 = max(fill + 4, yy - L)
        cv.seg(x + rng.normal(0, 1.5), yy, x + rng.normal(0, 1.5), y1, 3.2, 'accent'); yy = y1 - rng.uniform(4, 10); ng += 1
for k in range(6):                                      # grain boundaries across
    yb = rng.uniform(fill + 30, y_floor - 30); cv.line([(cx - cw / 2, yb), (cx + cw / 2, yb + rng.normal(0, 8))], 1.2, 'accent')
# growth front, a meniscus
cv.line([(cx - cw / 2 + 140 * (1 - math.cos(t)) / 2 * 0 + (cw) * t / math.pi, fill + 20 * math.sin(t)) for t in np.linspace(0, math.pi, 30)], 2.4, 'accent')
DATA["grain_segments"] = ng
# streamlines: from each nozzle down, converging into the contact mouth
def stream(x_start, frac):
    pts = []
    for t in np.linspace(0, 1, 120):
        y = y_head + t * (fill - y_head)
        pull = min(1, max(0, (y - y_head) / (y_surf - y_head))) ** 2.2
        target = cx + (x_start - cx) * 0.0 + (frac - 0.5) * (cw - 30)
        x = x_start + (target - x_start) * pull
        if y > y_surf: x = target
        pts.append((x, y))
    return pts
SL = []
for i, x in enumerate(nozz):
    for f in np.linspace(0.1, 0.9, 3):
        SL.append(stream(x + (f - 0.5) * 16, (i + f) / len(nozz)))
for s in SL[1::3]:
    cv.line(s, 0.5, val=150)
# molecules sampled along the streamlines
N_SAMPLES = 200_000; drawn = 0
which = rng.integers(0, len(SL), N_SAMPLES); pos = rng.random(N_SAMPLES) ** 0.8
foreign = int(rng.integers(0, N_SAMPLES))
for k in range(N_SAMPLES):
    if k % 55 != 0 and k != foreign: continue        # draw one in forty as a glyph; the rest stay as flow
    s = SL[which[k]]; i = int(pos[k] * (len(s) - 1)); x, y = s[i]
    x += rng.normal(0, 26 if y < y_surf - 120 else 5); y += rng.normal(0, 10)
    if y > fill - 6 or (y > y_surf - 10 and rng.random() < 0.75): continue
    a = rng.uniform(0, math.pi)
    cv.dot(x, y, 2.4)
    for m in range(6):
        b = a + m * math.pi / 3; cv.seg(x, y, x + 6 * math.cos(b), y + 6 * math.sin(b) * 0.7, 0.8)
    drawn += 1
    if k == foreign:
        cv.circle(x, y, 22, 2.0, 'accent'); cv.circle(x, y, 30, 1.0, 'accent'); DATA["foreign_molecule_xy"] = [round(x), round(y)]
DATA["molecule_glyphs_drawn"] = drawn
cv.plate_number(17)
write_data(17, DATA)
render(cv, 17, 'gas')
