"""16 - The Etch. A cryogenic high-aspect-ratio etch drawn as an axonometric block: a 10 um
deep stack of 238 alternating oxide/nitride layers (42 nm each) pierced by a row of memory
holes at 50:1 (200 nm wide, 10 um deep), walls straight to within 0.1%; directional ions
fall as vertical accent streaks and the ones that enter a hole run all the way to the floor."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "16 - The Etch", "title": "The Etch", "seed": SEED,
  "aspect_ratio": 50, "depth_um": 10.0, "hole_diameter_nm": 200, "hole_pitch_nm": 640,
  "layers": 238, "layer_thickness_nm": 42, "cd_deviation_top_to_bottom_pct": 0.1,
  "mapping": {
    "block": "front face height = 10 um = 1620 px, so a 200 nm hole is 32 px wide: the 50:1 ratio is drawn to scale",
    "layers": "238 engraved layer boundaries (alternating oxide/nitride, every nitride layer a slightly heavier line)",
    "holes": "front row cut in half through the hole axis; top face carries the hex array of hole mouths",
    "ions": "vertical accent streaks; streaks that land in a mouth continue as an accent axis down the hole",
  },
  "sources": [
    "https://newsroom.lamresearch.com/introducing-lam-cryogenic-etching (>50:1, up to 10 um, CD deviation <0.1%)",
    "https://www.lamresearch.com/products/our-solutions/cryogenic-etching/",
  ],
}
cv = Canvas(SEED); rng = cv.rng
H = 1620.0; S = H / 10000.0                     # px per nm
d = DATA["hole_diameter_nm"] * S; pitch = DATA["hole_pitch_nm"] * S
Wf = 1380.0; Dd = 1000.0; kx, ky = 0.43, -0.25   # depth axis
x0, y0 = 595.0, 1060.0
def P(x, y, z=0.0): return (x0 + x + kx * y, y0 + ky * y + z)
# --- right side face and top face outlines + layers
front = [P(0, 0), P(Wf, 0), P(Wf, 0, H), P(0, 0, H)]
side = [P(Wf, 0), P(Wf, Dd), P(Wf, Dd, H), P(Wf, 0, H)]
top = [P(0, 0), P(Wf, 0), P(Wf, Dd), P(0, Dd)]
nl = DATA["layers"]
for i in range(1, nl):
    z = H * i / nl; w = 1.5 if i % 2 else 0.45
    v = 170 if i % 2 else 255
    cv.line([P(Wf, 0, z), P(Wf, Dd, z)], w, val=v)
    cv.line([P(0, 0, z), P(Wf, 0, z)], w, val=v)
for poly in (front, side, top):
    cv.line(poly + [poly[0]], 2.6)
# --- holes on the cut front face
xs = np.arange(pitch * 0.9, Wf - pitch * 0.5, pitch)
DATA["holes_in_front_row"] = len(xs)
for x in xs:
    taper = d * 0.001 / 2                           # 0.1% CD change, below a pixel
    slot = [P(x - d / 2, 0, 0), P(x + d / 2, 0, 0), P(x + d / 2 - taper, 0, H - d / 2), P(x - d / 2 + taper, 0, H - d / 2)]
    cv.erase_poly(slot + [P(x, 0, H)])
    for t in (-1, 1):
        cv.line([P(x + t * d / 2, 0, 0), P(x + t * (d / 2 - taper), 0, H - d / 2)], 1.6)
    cv.line([P(x + d / 2 * math.cos(a), 0, H - d / 2 + d / 2 * math.sin(a)) for a in np.linspace(0, math.pi, 16)], 1.6)
# --- hole mouths on the top face (hex array), clipped to the top face
th = np.linspace(0, 2 * math.pi, 28)
mouths = []
for j, yy in enumerate(np.arange(0, Dd - d, pitch * math.sqrt(3) / 2)):
    off = 0 if j % 2 == 0 else pitch / 2
    for x in xs + off:
        if x + d / 2 > Wf - 2 or (j > 0 and yy - d / 2 < 0): continue
        if j == 0:
            pts = [P(x + d / 2 * math.cos(a), max(0.0, d / 2 * math.sin(a))) for a in np.linspace(0, math.pi, 16)]
        else:
            pts = [P(x + d / 2 * math.cos(a), yy + d / 2 * math.sin(a)) for a in th]
        cv.poly(pts, val=150); cv.line(pts, 1.3)
        mouths.append((x, yy))
DATA["mouths_drawn"] = len(mouths)
# --- ions
ions = 0; hits = 0
for _ in range(700):
    if rng.random() < 0.28:
        x, yy = mouths[rng.integers(len(mouths))]; inside = True
    else:
        x, yy = rng.uniform(5, Wf - 5), rng.uniform(5, Dd - 5); inside = False
    px, py = P(x, yy)
    L = rng.uniform(30, 120); top_y = py - rng.uniform(10, 380) * rng.random()
    if top_y - L < MARGIN + 10: continue
    cv.seg(px, top_y - L, px, top_y, rng.uniform(1.0, 1.8), 'accent'); ions += 1
    if inside and yy == 0:
        hits += 1
for x in xs:                                         # the accent axis down every front-row hole
    zz = 0.0
    while zz < H - d / 2:
        L = rng.uniform(25, 110); a, b = P(x, 0, zz); cv.seg(a, b, a, min(b + L, P(x, 0, H - d / 2)[1]), 1.3, 'accent')
        zz += L + rng.uniform(15, 60)
    cv.dot(*P(x, 0, H - d * 0.35), 3.2, 'accent')
DATA["ion_streaks"] = ions
cv.plate_number(16)
write_data(16, DATA)
render(cv, 16, 'etch')
