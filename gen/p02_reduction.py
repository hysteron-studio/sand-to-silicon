"""02 - The Reduction. Section through a submerged-arc furnace: quartz lumps and carbon
reductant in the molar ratio of SiO2 + 2C -> Si + 2CO; every quartz lump consumed in an
electrode crater releases two CO streams and one drop to the silicon pool."""
import math, numpy as np
from skimage.measure import points_in_poly
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "02 - The Reduction", "seed": SEED,
  "reaction": "SiO2 + 2C -> Si + 2CO",
  "furnace": "three-phase submerged-arc furnace, three pre-baked carbon electrodes, shell ~10 m",
  "reaction_zone_C": 2000, "electrical_energy_MWh_per_t_Si": [11, 13],
  "mg_si_purity_pct": [98.5, 99.5], "quartz_per_t_Si_t": 2.7,
  "scale_px_per_m": 230, "electrode_diameter_m": 1.4, "quartz_lump_mm": [10, 150], "reductant_mm": [5, 40],
  "mapping": {
    "charge": "particle field: angular open polygons = quartz lumps, filled black chips = carbon reductant; counts held at 1 SiO2 : 2 C",
    "craters": "a cavity under each electrode tip; temperature rises toward 2000 C, particles shrink and thin as they approach",
    "CO": "for every quartz lump removed by a crater, two accent streamlines (CO) rise through the charge",
    "silicon": "one accent drop per consumed lump falls to the tapped silicon pool (horizontal accent hatching)",
    "electrodes": "three electrodes of a three-phase triangle; the rear one drawn lighter",
  },
  "sources": [
    "https://www.pyrometallurgy.co.za/Pyro2011/Papers/083-Xakalashe.pdf (shell ~10 m, three pre-baked carbon electrodes, ~2000 C, MG-Si 98.5-99.5%)",
    "https://www.sciencedirect.com/science/article/abs/pii/S0959652618311880 (SiO2 + 2C = Si + 2CO; 11-13 MWh electrical per t Si)",
    "https://hubblo.org/media/pdf/silicon-to-wafer.pdf (2.7 t quartz per t MG-Si)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
fld = Field(np.random.default_rng(SEED), base=3)
cx = OUT / 2
L, R = MARGIN + 20, OUT - MARGIN - 20
top, floor = 1000, 2560          # charge surface, hearth
pool_top = 2380
# --- furnace lining: refractory brick courses
wall = 70
for side in (-1, 1):
    x0 = L if side < 0 else R - wall
    for y in np.arange(top - 120, floor + wall, 34):
        cv.seg(x0, y, x0 + wall, y, 1.1)
        off = 0 if int((y - top) / 34) % 2 else wall / 2
        for xx in np.arange(x0 + off, x0 + wall, wall):
            cv.seg(xx, y, xx, y + 34, 1.1)
    cv.seg(x0 + (wall if side < 0 else 0), top - 120, x0 + (wall if side < 0 else 0), floor, 2.4)
for x in np.arange(L, R + 1, 70):
    for y in (floor, floor + 34):
        cv.seg(x, y, min(x + 70, R), y, 1.1)
    cv.seg(x, floor, x, floor + 34 if (x // 70) % 2 else floor + 68, 1.1)
cv.seg(L, floor + 68, R, floor + 68, 2.4)
iL, iR = L + wall, R - wall

# --- electrodes (front-left, rear-centre, front-right)
S_ = DATA["scale_px_per_m"]; ED = DATA["electrode_diameter_m"] * S_
E0 = [(cx - 640, 1.0), (cx, 0.55), (cx + 640, 1.0)]
craters = [(x, pool_top - 0.82 * (340 if w == 1 else 280) + 30, 340 if w == 1 else 280) for x, w in E0]
E = [(x, cy_ - 0.82 * r + 95, w) for (x, w), (_, cy_, r) in zip(E0, craters)]   # tip sits inside the crater roof

def in_crater(x, y):
    for ex, ey, r in craters:
        if ((x - ex) / r) ** 2 + ((y - ey) / (r * 0.82)) ** 2 < 1: return True
    return False
def crater_dist(x, y):
    return min(math.hypot((x - ex) / r, (y - ey) / (r * 0.82)) for ex, ey, r in craters)
def under_electrode(x, y):
    for ex, ty, w in E:
        if abs(x - ex) < ED * (1 if w == 1 else 0.86) / 2 + 8 and y < ty + 10: return True
    return False

# --- charge: Poisson-disc-ish particle field, ratio 1 quartz : 2 carbon
parts = []
grid = {}
def ok(x, y, r):
    gx, gy = int(x // 40), int(y // 40)
    for i in range(gx - 2, gx + 3):
        for j in range(gy - 2, gy + 3):
            for (px, py, pr) in grid.get((i, j), []):
                if (px - x) ** 2 + (py - y) ** 2 < (pr + r + 1.5) ** 2: return False
    return True
tries = 0; nq = nc = 0
while tries < 260000:
    tries += 1
    x = rng.uniform(iL + 8, iR - 8); y = rng.uniform(top + 8, pool_top - 10)
    surf = top + 22 * math.sin(x / 210) + 30 * fld(x, 600)[0]
    if y < surf: continue
    want_q = nc >= 2 * nq
    r = (rng.uniform(1.2, 16) if want_q else rng.uniform(0.6, 4.6)) * (1 + 0.6 * rng.random())
    cd = crater_dist(x, y)
    r *= np.clip(0.35 + 0.65 * (cd - 1) / 1.2, 0.35, 1)        # hotter -> smaller, sintering
    if under_electrode(x, y) or cd < 1: continue
    if not ok(x, y, r): continue
    parts.append((x, y, r, 'q' if want_q else 'c'))
    grid.setdefault((int(x // 40), int(y // 40)), []).append((x, y, r))
    if want_q: nq += 1
    else: nc += 1
for x, y, r, k in parts:
    if k == 'q':
        n = rng.integers(4, 7); a0 = rng.uniform(0, 6.3)
        P = [(x + r * rng.uniform(0.7, 1.15) * math.cos(a0 + 2 * math.pi * i / n), y + r * rng.uniform(0.7, 1.15) * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
        cv.line(P + [P[0]], 1.0 + 0.04 * r)
        if r > 9 and rng.random() < 0.6:       # a facet line on bigger lumps
            i = rng.integers(0, n); cv.line([P[i], (x, y)], 0.8)
    else:
        n = rng.integers(4, 6); a0 = rng.uniform(0, 6.3)
        P = [(x + r * rng.uniform(0.6, 1.2) * math.cos(a0 + 2 * math.pi * i / n), y + r * rng.uniform(0.6, 1.2) * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
        cv.poly(P)
DATA["drawn_charge"] = {"quartz_lumps": nq, "carbon_pieces": nc}

# --- consumed lumps: the same density inside the craters, counted, not drawn
area = 0; consumed_q = 0
for ex, ey, r in craters:
    a = math.pi * r * r * 0.82
    consumed_q += int(round(nq * a / ((iR - iL) * (pool_top - top))))
DATA["consumed_in_craters"] = {"quartz_lumps": consumed_q, "drawn_as": "one Si drop + two CO streams per 10 lumps"}
consumed_q = int(round(consumed_q / 10))

# crater walls: sintered crust, dense hatching around the cavity
for ex, ey, r in craters:
    th = np.linspace(0, 2 * math.pi, 220)
    cv.line([(ex + r * math.cos(t), ey + 0.82 * r * math.sin(t)) for t in th], 2.2, jitter=1.2)
    for k in range(5):
        rr = r * (1.02 + 0.03 * k)
        seg = [(ex + rr * math.cos(t), ey + 0.82 * rr * math.sin(t)) for t in th if rng.random() > 0.15]
        for p0, p1 in zip(seg[:-1], seg[1:]):
            if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 20: cv.seg(*p0, *p1, 0.9)
# --- electrodes
for ex, ty, w in sorted(E, key=lambda e: e[2]):
    ed = ED * (1 if w == 1 else 0.86)
    x0, x1 = ex - ed / 2, ex + ed / 2
    cv.erase_poly([(x0, MARGIN), (x1, MARGIN), (x1, ty), (x0, ty)])
    cv.seg(x0, MARGIN + 40, x0, ty, 2.6 * w); cv.seg(x1, MARGIN + 40, x1, ty, 2.6 * w)
    tip = [(x0 + (x1 - x0) * t, ty + 26 * math.sin(math.pi * t) + rng.normal(0, 1.5)) for t in np.linspace(0, 1, 40)]
    cv.line(tip, 2.6 * w)
    # cylindrical shading: vertical engraving lines denser at the edges
    for t in np.linspace(-0.97, 0.97, 46):
        xx = ex + t * ed / 2
        wv = (0.5 + 1.5 * abs(t) ** 2.2 + (0.6 if t > 0.3 else 0)) * w
        yb = ty + 26 * math.sqrt(max(0, 1 - t * t)) - 4
        cv.seg(xx, MARGIN + 40, xx, yb, wv)
    # contact clamps
    for yy in (MARGIN + 160, MARGIN + 260):
        cv.erase_poly([(x0 - 30, yy), (x1 + 30, yy), (x1 + 30, yy + 44), (x0 - 30, yy + 44)])
        cv.line([(x0 - 30, yy), (x1 + 30, yy), (x1 + 30, yy + 44), (x0 - 30, yy + 44), (x0 - 30, yy)], 2.0 * w)
    # the arc: short branching accent strokes from tip to crater floor
    for k in range(9):
        p = [ex + rng.normal(0, ed * 0.18), ty + 30]
        pts_ = [tuple(p)]
        for s in range(10):
            p[0] += rng.normal(0, 14); p[1] += rng.uniform(14, 26)
            pts_.append(tuple(p))
        cv.line(pts_, 1.8 * w, 'accent')

# --- silicon pool with accent hatching, and the drops falling into it
cv.seg(iL, pool_top, iR, pool_top, 2.2)
for y in np.arange(pool_top + 8, floor - 2, 9):
    cv.seg(iL + 4, y, iR - 4, y + rng.normal(0, 0.6), 1.5, 'accent')
per = [consumed_q // 3 + (1 if i < consumed_q % 3 else 0) for i in range(3)]
DATA["drops_per_crater"] = per
for (ex, ey, r), n in zip(craters, per):
    for i in range(n):
        x = ex + rng.uniform(-0.55, 0.55) * r; y = rng.uniform(ey - 0.1 * r, pool_top - 30)
        if ((x - ex) / r) ** 2 + ((y - ey) / (0.82 * r)) ** 2 > 0.8: continue
        if y > pool_top - 20: continue
        cv.dot(x, y, 3.2, 'accent')
        cv.seg(x, y - 3, x, y - rng.uniform(10, 28), 1.2, 'accent')
# --- CO: two rising streamlines per consumed lump, curling up through the charge
co = 0
for (ex, ey, r), n in zip(craters, per):
    for i in range(2 * n):
        th = rng.uniform(math.pi * 1.05, math.pi * 1.95)
        x, y = ex + 0.95 * r * math.cos(th), ey + 0.82 * 0.95 * r * math.sin(th)
        pts_ = []
        for s in range(260):
            if y < top - 110 or under_electrode(x, y - 2): break
            ang = -math.pi / 2 + 0.9 * fld(x + 37 * i, y)[0] + 0.45 * math.sin(y / 90 + i * 1.7)
            x += 6 * math.cos(ang); y += 6 * math.sin(ang)
            x = min(max(x, iL + 6), iR - 6)
            pts_.append((x, y))
        if len(pts_) > 3:
            cv.line(pts_, 1.5, 'accent', jitter=0.5); co += 1
DATA["drawn_CO_streams"] = co
# tap hole and stream at the lower right
th_y = pool_top + 90
cv.erase_poly([(iR - 2, th_y - 16), (R + 4, th_y - 16), (R + 4, th_y + 16), (iR - 2, th_y + 16)])
cv.line([(iR, th_y - 16), (R + 2, th_y - 16)], 2.0); cv.line([(iR, th_y + 16), (R + 2, th_y + 16)], 2.0)
for y in np.arange(th_y - 10, th_y + 12, 7):
    cv.seg(iR, y, R + 2, y, 1.4, 'accent')

cv.plate_number(2)
write_data(2, DATA)
render(cv, 2, 'reduction')
print(DATA["drawn_charge"], DATA["consumed_in_craters"], co)
