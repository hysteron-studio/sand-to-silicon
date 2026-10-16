"""03 - The Purification. Plan of a 24-rod Siemens bell-jar reactor at the end of a run:
each U-shaped rod seen end-on as growth rings from an 8 mm slim rod to ~150 mm, hairpin
bridges carrying the heating current drawn in accent."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "03 - The Purification", "seed": SEED,
  "chemistry": "Si (MG) + 3HCl -> SiHCl3 + H2 ; distilled SiHCl3 + H2 -> Si + 3HCl on heated rods (Siemens CVD)",
  "rod_surface_C": 1100, "reactor": "24-rod bell jar (8 inner + 16 outer, 12 hairpin pairs), inner diameter 1720 mm",
  "slim_rod_diameter_mm": 8, "final_rod_diameter_mm": 150, "ring_step_mm_radius": 2.0,
  "purity": {"metallurgical_in_pct": 98.5, "electronic_grade_out": "9N-11N (99.9999999-99.999999999 %)"},
  "scale_px_per_mm": 1.28,
  "mapping": {
    "rods": "24 rods at true plan positions (inner ring r=330 mm x8, outer ring r=690 mm x16), true 150 mm final diameter",
    "growth rings": "one ink ring per 2 mm of radial growth from the 8 mm slim rod to the 150 mm rod (36 rings); the final surface is cauliflower-rough",
    "accent": "slim-rod cores and the 12 graphite-chucked hairpin bridges that close each rod pair's heating circuit",
    "gas": "faint ink streamlines of the TCS/H2 feed rising from 9 nozzles in the base plate, drawn as potential flow around the rods",
    "bell jar": "cooled steel wall, inner diameter 1720 mm",
  },
  "sources": [
    "https://www.sciencedirect.com/topics/engineering/purity-polysilicon (Siemens process ~1100 C, hairpin filaments, EG-Si 9N-11N, MG-Si ~98%)",
    "https://oa.upm.es/37804/1/ARamos_preprint_submit_JCG.pdf (1100-1150 C, seed rods < 1 cm, often 7-8 mm, grown to 13-20 cm)",
    "https://www.sciencedirect.com/science/article/abs/pii/S0017931015007498 (24-rod reactor, 8 inner + 16 outer, inner diameter 1720 mm)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
fld = Field(np.random.default_rng(SEED), base=4)
cx = cy = OUT / 2
k = DATA["scale_px_per_mm"]
Rj = 1720 / 2 * k                       # bell jar inner radius
rods = []
for i in range(8):  rods.append((330, 2 * math.pi * (i + 0.5) / 8))
for i in range(16): rods.append((690, 2 * math.pi * (i + 0.25) / 16))
P = [(cx + r * k * math.cos(a), cy + r * k * math.sin(a)) for r, a in rods]
Rr = 75 * k
# pairs: neighbours in the same ring
pairs = [(i, i + 1) for i in range(0, 8, 2)] + [(8 + i, 8 + i + 1) for i in range(0, 16, 2)]
DATA["hairpin_pairs"] = len(pairs)

# --- gas: streamlines of a uniform swirl + sources, deflected by rods (potential flow superposition)
nozzles = [(cx, cy)] + [(cx + 520 * k * math.cos(a), cy + 520 * k * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
def vel(x, y):
    u = v = 0.0
    for nx, ny in nozzles:
        dx, dy = x - nx, y - ny; r2 = dx * dx + dy * dy + 400
        u += 9000 * dx / r2; v += 9000 * dy / r2
    # gentle swirl
    dx, dy = x - cx, y - cy; r = math.hypot(dx, dy) + 1
    u += -dy / r * 3.2; v += dx / r * 3.2
    for px, py in P:   # doublet around each rod: flow skirts the cylinder
        dx, dy = x - px, y - py; r2 = dx * dx + dy * dy
        if r2 < (Rr + 6) ** 2: return None
        f = (Rr + 8) ** 2 / r2
        un, vn = u, v
        # remove radial component near the cylinder
        rr = math.sqrt(r2); ex_, ey_ = dx / rr, dy / rr
        dot = un * ex_ + vn * ey_
        u -= dot * ex_ * min(1, f * 1.0); v -= dot * ey_ * min(1, f * 1.0)
    return u, v
for s in range(520):
    nx, ny = nozzles[s % len(nozzles)]
    a = rng.uniform(0, 2 * math.pi); x, y = nx + 20 * math.cos(a), ny + 20 * math.sin(a)
    pts = [(x, y)]
    for _ in range(420):
        w = vel(x, y)
        if w is None: break
        u, v = w; n = math.hypot(u, v) + 1e-9
        x += 5 * u / n; y += 5 * v / n
        if math.hypot(x - cx, y - cy) > Rj - 14: break
        pts.append((x, y))
    if len(pts) > 6: cv.line(pts, 0.65, val=185)

# --- rods: growth rings
rng_r = np.arange(4, 75.01, DATA["ring_step_mm_radius"])
DATA["rings_per_rod"] = int(len(rng_r))
for (x, y) in P:
    cv.erase_circle(x, y, Rr + 6)
    ph = rng.uniform(0, 6.3, 6)
    for j, rmm in enumerate(rng_r):
        t = rmm / 75
        th = np.linspace(0, 2 * math.pi, 260)
        rough = (0.4 + 6.5 * t ** 3) * (0.5 * np.sin(11 * th + ph[0]) + 0.3 * np.sin(23 * th + ph[1]) + 0.2 * np.sin(41 * th + ph[2]))
        bias = 2.5 * t * np.sin(th - math.atan2(y - cy, x - cx))   # faster growth toward the hot centre
        rr = rmm * k + rough * 0.8 + bias
        pts = list(zip(x + rr * np.cos(th), y + rr * np.sin(th)))
        wdt = 0.55 + 0.75 * (j % 5 == 4) + (1.8 if rmm >= 74.9 else 0)
        cv.line(pts, wdt)
    # cauliflower surface bumps on the outer skin
    for a in np.linspace(0, 2 * math.pi, 70, endpoint=False):
        rb = Rr + rng.uniform(1, 5); bx, by = x + rb * math.cos(a), y + rb * math.sin(a)
        cv.circle(bx, by, rng.uniform(3, 7), 1.0)
    cv.erase_circle(x, y, 4 * k + 3)
    cv.dot(x, y, 4 * k, 'accent')                    # 8 mm slim rod

# --- hairpin bridges, seen from above: accent band joining each pair over the top
for i, j in pairs:
    (x0, y0), (x1, y1) = P[i], P[j]
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx_, ny_ = -uy, ux
    for o in np.linspace(-7, 7, 5):
        cv.seg(x0 + nx_ * o, y0 + ny_ * o, x1 + nx_ * o, y1 + ny_ * o, 1.4, 'accent')
    cv.seg(x0 + nx_ * 10, y0 + ny_ * 10, x1 + nx_ * 10, y1 + ny_ * 10, 1.5, "ink")
    cv.seg(x0 - nx_ * 10, y0 - ny_ * 10, x1 - nx_ * 10, y1 - ny_ * 10, 1.5, "ink")

# --- bell jar wall and base plate flange with bolt circle
for rr, w in ((Rj, 3.0), (Rj + 16, 1.4), (Rj + 46, 2.2)):
    th = np.linspace(0, 2 * math.pi, 900)
    cv.line(list(zip(cx + rr * np.cos(th), cy + rr * np.sin(th))), w)
for a in np.linspace(0, 2 * math.pi, 48, endpoint=False):
    bx, by = cx + (Rj + 31) * math.cos(a), cy + (Rj + 31) * math.sin(a)
    cv.circle(bx, by, 6, 1.3)
# cooling-water hatch between wall lines
for a in np.linspace(0, 2 * math.pi, 720, endpoint=False):
    cv.seg(cx + Rj * math.cos(a), cy + Rj * math.sin(a), cx + (Rj + 16) * math.cos(a + 0.004), cy + (Rj + 16) * math.sin(a + 0.004), 0.8)
for nx, ny in nozzles:
    cv.circle(nx, ny, 9, 1.6)

cv.plate_number(3)
write_data(3, DATA)
render(cv, 3, 'purification')
print(Rj, DATA["rings_per_rod"])
