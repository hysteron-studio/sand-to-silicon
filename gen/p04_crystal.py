"""04 - The Crystal. Diamond-cubic silicon drawn as a woven (100) bond projection,
pulled from a seed out of a counter-rotating melt."""
import math, numpy as np
from style import *
# v1 prototype plate I; renumbered to master-sequence #4

SEED = None  # private, not published
DATA = {
  "piece": "04 - The Crystal", "seed": SEED,
  "lattice_constant_A": 5.431, "structure": "diamond cubic (two interpenetrating FCC, basis (0,0,0),(1/4,1/4,1/4))",
  "projection_body": "[100] (wafer orientation <100>)", "projection_seed": "[111]",
  "melting_point_C": 1414, "melting_point_K": 1687,
  "pull_rate_mm_per_min": 0.4, "crystal_rotation_rpm": 8, "crucible_rotation_rpm": 4,
  "rotation_sense": "counter-rotating", "ingot_diameter_mm": 300,
  "derived_striation_pitch_um": 0.4 / 8 * 1000,
  "px_per_angstrom": 22,
  "mapping": {
    "bond spacing": "a*sqrt(2)/4 = 1.920 A -> 42.2 px",
    "over/under weave": "bonds rising to z=+a/4 drawn full, falling to z=-a/4 drawn broken (depth cue of the diamond basis)",
    "thermal gradient": "T(y) interpolated 800 C (top of drawing) -> 1414 C at the interface; strokes per bond 1->4 and positional jitter grow with T",
    "striations": "rotational striation pitch = pull/rotation = 50 um, drawn as faint accent arcs every 50 units",
    "melt": "accent streamlines spiralling counter to the crystal, angular-rate ratio 8:4 rpm",
  },
  "sources": [
    "https://chem.libretexts.org/ (Barron, Structures of Element and Compound Semiconductors: a(Si)=5.4310201 A)",
    "https://link.springer.com/article/10.1007/BF02026423 (a0 = 543102.018 fm)",
    "https://periodic-table.rsc.org/element/14/silicon (mp 1414 C / 1687 K)",
    "https://www.electrochem.org/dl/ma/201/pdfs/0564.pdf (300 mm CZ: crystal 5-14 rpm, crucible 6-12 rpm)",
    "Transient global modelling of O/C segregation in 300 mm CZ-Si (crystal 8 rpm, crucible 4 rpm, pull 0.4 mm/min)",
    "https://svmi.com/wp-content/uploads/2020/09/SV027.pdf (300 mm wafer, CZ, <100>)",
  ],
}


cv = Canvas(SEED); rng = cv.rng
fld = Field(np.random.default_rng(SEED), base=3)

a = 5.431 * DATA["px_per_angstrom"]   # unit cell px
d = a / 4                               # projected step between A and B sites
cx = OUT / 2
y_seed0, y_neck0, y_sh0, y_body0, y_int = 430, 600, 860, 1160, 2190
R = 500
Lft, Rgt, Bot = MARGIN, OUT - MARGIN, OUT - MARGIN

def radius(y):
    if y < y_neck0: return 22
    if y < y_sh0: return 9 + 2.5 * math.sin((y - y_neck0) / 19)        # Dash neck
    if y < y_body0:
        t = (y - y_sh0) / (y_body0 - y_sh0)
        return 9 + (R - 9) * (1 - (1 - t) ** 2.6)                         # shoulder (rounded crown)
    return R + 5 * math.sin(y / 53)                                    # diameter-control ripple

def interface_y(x, y_front):
    """growth front is convex toward the melt: y_front + sag*(1-(x/R)^2)"""
    r = (x - cx) / R
    return y_front + 0.2 * R * math.sqrt(max(1 - r * r, 0))   # same perspective as the melt ellipse

def temp(y):
    t = np.clip((y - y_seed0) / (y_int - y_seed0), 0, 1)
    return 800 + (1414 - 800) * t ** 1.6

# ---- seed: [111] projection (honeycomb of the diamond lattice viewed down <111>)
hx = d * 0.9
for j in range(int((y_neck0 - y_seed0) / (hx * 1.5)) + 1):
    for i in range(-2, 3):
        x0 = cx + i * hx * math.sqrt(3) + (j % 2) * hx * math.sqrt(3) / 2
        y0 = y_seed0 + j * hx * 1.5
        if abs(x0 - cx) > 22: continue
        pts = [(x0 + hx * math.cos(math.pi / 6 + k * math.pi / 3), y0 + hx * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(7)]
        cv.line(pts, 1.6, 'ink')

# ---- Dash neck: a single file of bonds, the dislocation-free bottleneck
yy = y_neck0
k = 0
while yy < y_sh0 + 20:
    xo = cx + 2.5 * math.sin(yy / 19)
    cv.seg(xo - d / 2, yy, xo + d / 2, yy + d, 1.7, 'ink'); cv.seg(xo + d / 2, yy, xo - d / 2, yy + d, 1.1, 'ink')
    yy += d; k += 1

# ---- body: woven [100] projection
ys = np.arange(y_neck0, y_int + 3 * d, d)
xs = np.arange(cx - (R // d + 3) * d, cx + R + 3 * d, d)
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        if (i + j) % 2: continue
        for dx, up in ((1, True), (-1, False)):
            x1, y1 = x + dx * d, y + d
            xm, ym = (x + x1) / 2, (y + y1) / 2
            r = radius(ym)
            if abs(xm - cx) > r: continue
            yi = interface_y(xm, y_int)
            if ym > yi: continue
            T = temp(ym); heat = (T - 800) / 614
            # near the interface the order is still being decided
            near = np.clip(1 - (yi - ym) / 140, 0, 1)
            if near > 0 and rng.random() < near * 0.55: continue
            edge = 1 - abs(xm - cx) / max(r, 1)
            if edge < 0.05 and rng.random() < 0.5: continue
            nstroke = 1 + int(heat * 3.0 + rng.random() * 0.7)
            jit = 0.25 + 5.0 * heat ** 2.5 + 6 * near
            layer = 'accent' if rng.random() < max(0, heat - 0.80) * 3.2 + near * 0.8 else 'ink'
            w = (1.5 + 1.2 * heat) if up else (1.0 + 0.8 * heat)
            for k in range(nstroke):
                o = (k - (nstroke - 1) / 2) * 2.6
                p0 = (x + o + rng.normal(0, jit * .35), y + rng.normal(0, jit * .35))
                p1 = (x1 + o + rng.normal(0, jit * .35), y1 + rng.normal(0, jit * .35))
                if up:
                    cv.seg(*p0, *p1, w, layer)
                else:  # passes under: broken at the crossing -> woven depth of the diamond basis
                    f = 0.30
                    cv.seg(p0[0], p0[1], p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f, w, layer)
                    cv.seg(p1[0] - (p1[0] - p0[0]) * f, p1[1] - (p1[1] - p0[1]) * f, p1[0], p1[1], w, layer)
            if heat < 0.7 and up:
                cv.dot(x, y, 2.2 + 2.6 * (1 - heat) ** 2)

# ---- rotational striations: the history of the growth front, one every 50 'um' (px)
for yf in np.arange(y_body0 - 60, y_int - 20, 50):
    xsamp = np.linspace(cx - R, cx + R, 160)
    pts = [(x, interface_y(x, yf)) for x in xsamp if abs(x - cx) < radius(interface_y(x, yf)) - 3]
    if len(pts) > 2:
        cv.line(pts, 1.6, 'accent', val=170)

# ---- the melt: counter-rotating streamlines in perspective, cropped by the print margin
RX, RY, ym0 = 1150, 230, y_int
for k in range(1300):
    r0 = (R + 12) / RX + (1 - (R + 12) / RX) * rng.random() ** 1.15
    th0 = rng.uniform(0, 2 * math.pi)
    pts = []
    L = rng.integers(30, 160)
    for s_ in range(L):
        th = th0 - s_ * 0.012 / max(r0, 0.4)                # crucible sense: opposite to crystal
        rr = r0 * (1 + 0.07 * fld(cx + 600 * r0 * math.cos(th), 1500 + 600 * math.sin(th))[0])
        x = cx + RX * rr * math.cos(th); y = ym0 + RY * rr * math.sin(th)
        if not (Lft <= x <= Rgt and y <= Bot): 
            if pts: cv.line(pts, w, 'accent'); pts = []
            continue
        # crystal occludes the far side of the melt
        if y < ym0 + 4 and abs(x - cx) < R + 10: 
            if pts: cv.line(pts, w, 'accent'); pts = []
            continue
        w = 0.9 + 2.6 * np.clip(1.1 - r0, 0.0, 1.0) ** 1.5   # hotter, heavier near the crucible centre
        pts.append((x, y))
    if len(pts) > 1:
        cv.line(pts, w, 'accent')
# meniscus ring around the growing crystal
th = np.linspace(0, 2 * math.pi, 400)
cv.line([(cx + (R + 6) * math.cos(t), y_int + 0.2 * (R + 6) * math.sin(t)) for t in th if 0 <= t <= math.pi], 2.8, 'ink')

# the solidification lens: dense hot hatching where liquid becomes lattice
for yy in np.arange(y_int - 2, y_int + 0.2 * R, 4.5):
    hw = R * math.sqrt(max(1 - ((yy - y_int) / (0.2 * R)) ** 2, 0)) if yy > y_int else R
    if hw < 6: continue
    xa = cx - hw + rng.uniform(0, 8); xb = cx + hw - rng.uniform(0, 8)
    pts = [(x, yy + rng.normal(0, 0.6)) for x in np.linspace(xa, xb, 40)]
    cv.line(pts, 1.1, 'accent', val=200)

# pull wire
cv.seg(cx, 200, cx, y_seed0, 1.4, 'ink')
cv.plate_number(4)
write_data(4, DATA)
render(cv, 4, 'crystal')
