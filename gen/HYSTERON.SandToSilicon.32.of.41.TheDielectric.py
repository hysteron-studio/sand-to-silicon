"""32 - The Dielectric. Eight build-up layers of a package substrate, cut into a staircase so
every level shows: in section, copper traces (dense ink hatch) sit in pale insulating film,
joined layer to layer by laser-drilled vias that taper downward; on each terrace the copper
routing of that layer runs back into depth; film boundaries in accent."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "32 - The Dielectric", "title": "The Dielectric", "seed": SEED,
  "film": "build-up insulating film (commercialised 1999, from amino-acid chemistry research)",
  "build_up_layers": 8, "copper_um": 15, "dielectric_um": 30, "via_top_um": 60, "via_bottom_um": 40,
  "note": "layer thicknesses and via sizes are typical published values for build-up substrates, not one product's spec",
  "mapping": {
    "scale": "2.6 px per um; each layer 45 um = 117 px tall",
    "staircase": "layer i starts i x 200 px further back, exposing a terrace of its top surface",
    "section": "copper trace sections as hatched rectangles, seeded; vias as tapered hatched trapezoids landing on the trace below",
    "terraces": "copper routing of each layer receding into depth; accent lines at every film boundary",
  },
  "sources": [
    "https://www.ajinomoto.com/innovation/our_innovation/buildupfilm",
    "https://www.ajinomoto.com/stories/the-ajinomoto-groups-unexpected-role-in-semiconductor-manufacturing-the-insulating-film-abf-born-from-aminoscience",
  ],
}
cv = Canvas(SEED); rng = cv.rng
s = 2.6; nL = 8; lt = 45 * s; cu = 15 * s
Wb = 1500.0; Db = 1800.0; step = 200.0; kx, ky = 0.36, -0.30
x0, y0b = 426.0, 2380.0
def P(x, y, z): return (x0 + x + kx * y, y0b + ky * y - z)
prev_traces = None
for i in range(nL):
    ya = i * step; z0 = i * lt; z1 = z0 + lt
    face = [P(0, ya, z0), P(Wb, ya, z0), P(Wb, ya, z1), P(0, ya, z1)]
    side = [P(Wb, ya, z0), P(Wb, Db, z0), P(Wb, Db, z1), P(Wb, ya, z1)]
    top = [P(0, ya, z1), P(Wb, ya, z1), P(Wb, Db, z1), P(0, Db, z1)]
    for q in (face, side, top): cv.erase_poly(q)
    cv.line(face + [face[0]], 2.0); cv.line([side[1], side[2], side[3]], 1.6)
    cv.line([face[0], face[1]], 1.8, 'accent'); cv.line([side[0], side[1]], 1.4, 'accent')
    cv.line([face[3], face[2], side[2]], 1.8, 'accent')
    # side face: layer copper line as hatch band
    cv.hatch_poly([P(Wb, ya, z1 - cu), P(Wb, Db, z1 - cu), P(Wb, Db, z1), P(Wb, ya, z1)], 90, 4, 0.9)
    # copper trace sections on the front face (top of this layer)
    xs = []; x = rng.uniform(20, 60)
    while x < Wb - 60:
        w = rng.choice([30, 40, 40, 60, 120]) * (1.0 - 0.07 * i) ; xs.append((x, w)); x += w + rng.uniform(25, 90)
    for xa, w in xs:
        r = [P(xa, ya, z1 - cu), P(xa + w, ya, z1 - cu), P(xa + w, ya, z1), P(xa, ya, z1)]
        cv.hatch_poly(r, 45, 3.4, 1.0); cv.line(r + [r[0]], 1.2)
    # vias from this layer's traces down to the previous layer's traces
    if prev_traces:
        for xa, w in xs:
            if w < 40 or rng.random() < 0.45: continue
            c = xa + w / 2
            if not any(pa <= c <= pa + pw for pa, pw in prev_traces): continue
            vt, vb = 60 * s / 2, 40 * s / 2
            v = [P(c - vb, ya, z0), P(c + vb, ya, z0), P(c + vt, ya, z1 - cu), P(c - vt, ya, z1 - cu)]
            cv.hatch_poly(v, 45, 3.4, 1.0); cv.line(v + [v[0]], 1.2)
    prev_traces = xs
    # terrace routing: traces run back from each section into depth
    depth_vis = step if i < nL - 1 else Db - ya
    for xa, w in xs:
        L = (0.92 if i < nL - 1 else rng.uniform(0.5, 0.95)) * depth_vis
        jog = rng.choice([0, 0, 1])
        a = P(xa + w / 2, ya, z1); b = P(xa + w / 2, ya + L, z1)
        if jog and L > 120:
            m = P(xa + w / 2, ya + L * 0.5, z1); dx = rng.choice([-60, 60]); m2 = P(xa + w / 2 + dx, ya + L * 0.5 + abs(dx), z1); e = P(xa + w / 2 + dx, ya + L, z1)
            cv.line([a, m, m2, e], max(1.4, w * 0.05))
        else:
            cv.line([a, b], max(1.4, w * 0.05))
cv.plate_number(32)
write_data(32, DATA)
render(cv, 32, 'dielectric')
