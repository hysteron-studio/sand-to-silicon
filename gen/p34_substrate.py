"""34 - The Substrate. The 22 wiring layers of an AI package substrate fanned out like a deck
of cards around one corner: the top layer carries the fine bump field where the chips land,
each layer below routes coarser (line and space widening from 3 um to 25 um), and the
bottom layer is the ball grid that meets the board."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "34 - The Substrate", "title": "The Substrate", "seed": SEED,
  "layers": 22, "layer_range_trade_press": [20, 26], "line_space_um_top": 3, "line_space_um_bottom": 25,
  "mapping": {
    "fan": "layer i (0 = bottom ball grid, 21 = top bump field) rotated by (21 - i) x 3.3 deg about the shared corner; drawn bottom-up, each layer hiding the one beneath",
    "routing": "seeded Manhattan traces whose pitch grows geometrically from 18 px (top) to 70 px (bottom), standing for 3 -> 25 um line/space",
    "top": "bump field in accent (hex grid)", "bottom": "ball grid array in accent",
  },
  "sources": [
    "https://www.ibiden.com/company/2026/02/notice-regarding-capital-investment-plan-for-high-performance-ic-package-substrates.html",
    "https://patents.us/US12702023 (fine line/space <= 3 um)",
    "https://eastasiabrief.com/semiconductors/ibiden-shinko-ramp-high-layer-fc-bga-lines-ai-43 (20-26 layers, trade press)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
nL = DATA["layers"]; side = 1.0
def rot(pts, a):
    c, s = math.cos(a), math.sin(a); return [(x * c - y * s, x * s + y * c) for x, y in pts]
sq = [(0, 0), (side, 0), (side, -side), (0, -side)]
angs = [-math.radians((nL - 1 - i) * 3.3) for i in range(nL)]
allp = np.array([p for a in angs for p in rot(sq, a)])
mn, mx = allp.min(0), allp.max(0)
sc = min((OUT - 2 * MARGIN - 40) / (mx[0] - mn[0]), (OUT - 2 * MARGIN - 40) / (mx[1] - mn[1]))
ox = MARGIN + 20 - mn[0] * sc + ((OUT - 2 * MARGIN - 40) - (mx[0] - mn[0]) * sc) / 2
oy = MARGIN + 20 - mn[1] * sc + ((OUT - 2 * MARGIN - 40) - (mx[1] - mn[1]) * sc) / 2
L = side * sc
def T(pts, a): return [(ox + x, oy + y) for x, y in rot(pts, a)]
ntr = 0
for i in range(nL):
    a = angs[i]
    poly = T([(x * L, y * L) for x, y in sq], a)
    cv.erase_poly(poly); cv.line(poly + [poly[0]], 1.8)
    f = i / (nL - 1)
    pitch = 70 * (18 / 70) ** f
    if i == 0:
        for gx in np.arange(pitch, L - pitch / 2, pitch):
            for gy in np.arange(pitch, L - pitch / 2, pitch):
                (x, y), = T([(gx, -gy)], a); cv.circle(x, y, pitch * 0.32, 1.8, 'accent'); cv.dot(x, y, pitch * 0.12, 'accent')
        continue
    if i == nL - 1:
        hp = 26
        for r, gy in enumerate(np.arange(hp, L - hp / 2, hp * 0.866)):
            for gx in np.arange(hp + (hp / 2 if r % 2 else 0), L - hp / 2, hp):
                c = abs(gx - L * 0.5) < L * 0.33 and abs(gy - L * 0.5) < L * 0.36
                if c:
                    (x, y), = T([(gx, -gy)], a); cv.dot(x, y, 6.2, 'accent')
        continue
    horiz = i % 2 == 0
    for k, off in enumerate(np.arange(pitch, L - pitch / 2, pitch)):
        t0 = rng.uniform(0, L * 0.3); t1 = rng.uniform(L * 0.6, L)
        jog_at = rng.uniform(t0 + 30, t1 - 30) if rng.random() < 0.5 else None
        pts = [(t0, off)]
        if jog_at:
            d = rng.choice([-1, 1]) * pitch * 0.5
            pts += [(jog_at, off), (jog_at + abs(d), off + d), (t1, off + d)]
        else:
            pts += [(t1, off)]
        pts = [(min(max(u, 4), L - 4), min(max(v, 4), L - 4)) for u, v in pts]
        local = [(u, -v) if horiz else (v, -u) for u, v in pts]
        cv.line(T(local, a), max(0.9, pitch * 0.09)); ntr += 1
        (x, y), = T([local[-1]], a); cv.circle(x, y, max(2.5, pitch * 0.18), 1.0)
DATA["traces_drawn"] = ntr
cv.plate_number(34)
write_data(34, DATA)
render(cv, 34, 'substrate')
