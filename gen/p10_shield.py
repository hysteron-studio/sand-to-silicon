"""10 - The Shield. Section through a pellicled EUV mask: falling particles stop on a
carbon-nanotube membrane held ~2 mm above the pattern; 6-degree EUV rays cross it twice and
lose 6% each pass - of 100 rays, 94 reach the mask and 88 return (absorbed ones end in accent)."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "10 - The Shield", "seed": SEED,
  "membrane": {"type": "carbon-nanotube (CNT) network", "thickness_nm": "<= 50 (preferably <= 20-30)", "EUV_transmission_single_pass": 0.94},
  "standoff_mm": 2.0, "chief_ray_angle_deg": 6, "rays_drawn": 100,
  "derived": {"double_pass_transmission": round(0.94 ** 2, 4)},
  "mapping": {
    "membrane": "a horizontal band of seeded random fibre curves (CNT bundles) in accent spanning the frame",
    "particles": "a log-normal particle field falling (with motion strokes) and coming to rest on the membrane; none below it",
    "rays": "100 parallel rays at 6 deg to the normal; 6 terminate at the membrane on the way down (accent tick), the 94 survivors reflect from the mask (return path dashed) and 6 of those (rounded from 94 x 0.06 = 5.6) stop on the way back up, leaving 88",
    "mask": "absorber lines on the multilayer over hatched low-expansion glass, drawn untouched - the pellicle's whole purpose",
    "scale": "not to scale: the stand-off is shown far larger than the 50 nm membrane would allow at true proportion",
  },
  "sources": [
    "https://patents.justia.com/patent/12287569 (Mitsui CNT pellicle film: 1-50 nm, preferably <= 20-30 nm; >= 80-90% EUV transmission; pellicle ~2 mm above the mask)",
    "https://jp.mitsuichemicals.com/en/release/2024/2024_0528_1/index.htm (Mitsui CNT pellicle production facilities)",
    "https://www.imec-int.com/en/press/imec-and-mitsui-chemicals-sign-strategic-partnership-agreement-commercialize-cnt-pellicle (imec/Mitsui CNT pellicle, >= 94% transmission)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
fld = Field(np.random.default_rng(SEED), base=3)
L, R = MARGIN, OUT - MARGIN
y_mem = 1330; y_mask = 2140; y_sub1 = 2470
fx0, fx1 = 470, OUT - 470          # frame inner edges

# ---- mask: glass, multilayer, absorber lines
glass = [(L + 40, y_mask + 30), (R - 40, y_mask + 30), (R - 40, y_sub1), (L + 40, y_sub1)]
cv.hatch_poly(glass, 62, 15, 1.0)
cv.line(glass + [glass[0]], 2.2)
for k in range(8):
    cv.seg(L + 40, y_mask + 6 + 3 * k, R - 40, y_mask + 6 + 3 * k, 0.9 if k % 2 else 1.5)
x = L + 70; pitch = 64
while x < R - 90:
    w = pitch * (0.42 if rng.random() > 0.15 else 0.7)
    cv.poly([(x, y_mask - 26), (x + w, y_mask - 26), (x + w, y_mask + 4), (x, y_mask + 4)])
    x += pitch
# ---- frame posts
for xa, xb in ((fx0 - 70, fx0), (fx1, fx1 + 70)):
    post = [(xa, y_mem - 6), (xb, y_mem - 6), (xb, y_mask - 32), (xa, y_mask - 32)]
    cv.erase_poly(post); cv.hatch_poly(post, 45, 9, 1.2); cv.line(post + [post[0]], 2.2)
    cv.seg(xa - 10, y_mask - 32, xb + 10, y_mask - 32, 3.0)    # adhesive

# ---- rays: 100 parallel at 6 deg
a = math.radians(6)
nR = 100
xs = np.linspace(fx0 + 60, fx1 - 260, nR)
idx = rng.permutation(nR)
down_stop = set(idx[:6]); up_stop = set(idx[6:12])
DATA["rays"] = {"incident": nR, "absorbed_down": 6, "reach_mask": nR - 6, "absorbed_up": 6, "return": nR - 12}
y_top = MARGIN + 30
def dash(x0, y0, x1, y1, on=14, off=10):
    L_ = math.hypot(x1 - x0, y1 - y0); n_ = int(L_ / (on + off))
    for k in range(n_ + 1):
        t0 = k * (on + off) / L_; t1 = min(1, t0 + on / L_)
        if t0 >= 1: break
        cv.seg(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0, x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1, 0.6, val=170)
for i, x0 in enumerate(xs):
    xm = x0 + (y_mem - y_top) * math.tan(a)
    xk = x0 + (y_mask - 26 - y_top) * math.tan(a)
    if i in down_stop:
        cv.seg(x0, y_top, xm, y_mem - 18, 0.6, val=170)
        cv.dot(xm, y_mem - 26, 7, 'accent')
        continue
    cv.seg(x0, y_top, xk, y_mask - 26, 0.6, val=170)
    xu = xk + (y_mask - 26 - y_mem) * math.tan(a)
    if i in up_stop:
        dash(xk, y_mask - 26, xu, y_mem + 18)
        cv.dot(xu, y_mem + 26, 7, 'accent')
        continue
    xt = xk + (y_mask - 26 - y_top) * math.tan(a)
    dash(xk, y_mask - 26, xt, y_top)

# ---- the membrane: CNT bundle network in accent
cv.erase_poly([(fx0, y_mem - 15), (fx1, y_mem - 15), (fx1, y_mem + 15), (fx0, y_mem + 15)])
nf = 0
for f in range(520):
    x = rng.uniform(fx0 - 40, fx1); y = y_mem + rng.uniform(-12, 12)
    ang = rng.normal(0, 0.05); pts = []
    for s in range(rng.integers(40, 160)):
        ang += rng.normal(0, 0.03) - (y - y_mem) * 0.0025
        x += 5 * math.cos(ang); y += 5 * math.sin(ang)
        if x > fx1 or x < fx0: break
        pts.append((x, min(max(y, y_mem - 14), y_mem + 14)))
    if len(pts) > 3: cv.line(pts, rng.uniform(0.8, 1.9), 'accent'); nf += 1
cv.seg(fx0, y_mem - 15, fx1, y_mem - 15, 0.9); cv.seg(fx0, y_mem + 15, fx1, y_mem + 15, 0.9)

# ---- particles: falling and resting
resting = []
for p in range(1100):
    r = float(np.clip(rng.lognormal(1.55, 0.55), 2.0, 26))
    x = rng.uniform(fx0 + 20, fx1 - 20)
    if rng.random() < 0.45:
        y = y_mem - 15 - r * 0.8
        if any(abs(x - q) < r + s_ for q, s_ in resting): continue
        resting.append((x, r))
    else:
        y = y_top + 60 + (y_mem - y_top - 140) * rng.random() ** 0.7
    n = rng.integers(5, 9); a0 = rng.uniform(0, 6.3)
    P = [(x + r * rng.uniform(0.6, 1.2) * math.cos(a0 + 2 * math.pi * i / n), y + r * rng.uniform(0.6, 1.2) * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
    cv.erase_poly(P); cv.poly(P) if r < 6 else cv.line(P + [P[0]], 1.6)
    if r >= 6: cv.hatch_poly(P, 45, 3.4, 1.0)
    if y < y_mem - 40:   # motion strokes
        for k in range(2):
            o = rng.uniform(-r * 0.6, r * 0.6)
            cv.seg(x + o, y - r - 4, x + o, y - r - 4 - rng.uniform(20, 80) * (r / 6) ** 0.5, 0.8)
DATA["particles"] = {"resting_on_membrane": len(resting), "membrane_fibres": nf}

cv.plate_number(10)
write_data(10, DATA)
render(cv, 10, 'shield')
print(DATA["particles"], DATA["rays"])
