"""26 - The Cut. A 300 mm wafer of reticle-sized dies; the backside grinding arcs show through
the dicing streets; every die carries 26 strata (775 um / 30 um) of which only the top one
survives the thinning. Below, the wafer in section."""
import math, numpy as np
from style import *
# v1 prototype plate IV; renumbered to master-sequence #26

SEED = None  # private, not published
DATA = {
  "piece": "26 - The Cut", "seed": SEED,
  "wafer_diameter_mm": 300, "wafer_thickness_um": 775, "thickness_tolerance_um": 25,
  "thinned_thickness_um": 30, "thinning_ratio": round(30 / 775, 4),
  "strata_per_die": round(775 / 30, 1),
  "edge_exclusion_mm": 3, "notch": "SEMI notch, <110>",
  "die_mm": [10, 11], "die_note": "illustrative DRAM-class die (memory dies feed plate V); not a specific product",
  "street_um": 60, "street_note": "streets drawn ~13x exaggerated (60 um would be 0.4 px)",
  "probe_ink_fraction": 0.09,
  "px_per_mm": 6.6667,
  "mapping": {
    "disc": "300 mm = 2000 px; 3 mm edge exclusion ring; notch at 6 o'clock",
    "dies": "26 x 33 mm grid; partial edge dies drawn as outline only (lost)",
    "strata": "26 horizontal lines per die (775/30); only line 1 at full ink, lines 2-26 fade to 0 -> the 745 um ground away",
    "grind arcs": "backgrind wheel marks (arcs through the centre) in accent, visible in the streets",
    "section": "cross-section 775 um tall (0.25 px/um); top 30 um solid ink, the rest hatched and fading",
    "ink dots": "~9% of dies receive a probe ink dot (fails), deterministic from seed",
  },
  "sources": [
    "https://svmi.com/wp-content/uploads/2020/09/SV027.pdf (300 mm, 775 +/-25 um, notch <110>, edge exclusion 3 mm)",
    "SEMI M1 / SEMI 3D10 (300 mm nominal 775 um)",
    "Manufacturable 300mm Wafer Thinning for 3D Interconnect Applications, MRS Proc. (backgrind to 30 um bonded to handle)",
    "https://www.asml.com/en/products/euv-lithography-systems/twinscan-nxe3400c (26 x 33 mm field)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
pxmm = 7.0
DATA["px_per_mm"] = pxmm
Rw = 150 * pxmm
excl = 3 * pxmm
dw, dh = 10 * pxmm, 11 * pxmm
st = 5.0
TILT = 0.42                      # wafer plane seen obliquely: y' = y * TILT
CX, CY0 = 1500.0, 860.0
N_STRATA = 26                    # 775 / 30
GAP = 50.0
def P(u, v, k=0):
    return (CX + u, CY0 + k * GAP + v * TILT)

# ---- the 25 ground-away strata, from the bottom up so upper ones sit on top
for k in range(N_STRATA - 1, 0, -1):
    fade = (1 - k / N_STRATA) ** 1.15
    # grind marks: concentric arcs about one wheel centre per stratum (rotating by the golden angle)
    phi = k * 2.39996 + 0.7
    wc = np.array([1.05 * Rw * math.cos(phi), 1.05 * Rw * math.sin(phi)])
    for rr_ in np.arange(0.25 * Rw, 2.1 * Rw, 12 + 8 * (1 - fade)):
        d0 = math.hypot(*wc)
        t0 = math.atan2(-wc[1], -wc[0])
        t = np.linspace(t0 - 1.6, t0 + 1.6, 900)
        u = wc[0] + rr_ * np.cos(t); v = wc[1] + rr_ * np.sin(t)
        vis = (u ** 2 + v ** 2 < Rw ** 2) & (u ** 2 + (v + GAP / TILT) ** 2 > Rw ** 2)
        brk = rng.random(len(t)) < (1 - fade) * 0.06
        seg = []
        for uu, vv, ok, bk in zip(u, v, vis, brk):
            if ok and not (bk or (seg == [] and rng.random() < (1 - fade) * 0.5)):
                seg.append(P(uu, vv, k))
            elif seg:
                if len(seg) > 1: cv.line(seg, 0.9 + 1.8 * fade, 'accent', int(50 + 205 * fade))
                seg = []
        if len(seg) > 1: cv.line(seg, 0.9 + 1.8 * fade, 'accent', int(50 + 205 * fade))
    # swarf: the ground silicon as dust drifting below the deepest strata
    if k > N_STRATA * 0.55:
        n = int(500 * (k / N_STRATA))
        uu = rng.uniform(-Rw, Rw, n); vv = rng.uniform(0, Rw, n)
        okk = (uu ** 2 + vv ** 2 < Rw ** 2) & (uu ** 2 + (vv + GAP / TILT) ** 2 > Rw ** 2)
        for a_, b_ in zip(uu[okk], vv[okk]):
            x, y = P(a_, b_, k); cv.dot(x, y + rng.uniform(0, 30), 1.3, 'ink', 150)
    # front rim of the stratum
    th = np.linspace(0.0, math.pi, 500)
    rim = [P(Rw * math.cos(t), Rw * math.sin(t), k) for t in th]
    keep = [rng.random() > (1 - fade) * 0.55 for _ in rim]
    seg = []
    for p, ok in zip(rim, keep):
        if ok: seg.append(p)
        elif seg:
            if len(seg) > 1: cv.line(seg, 1.0 + 1.2 * fade, 'ink', int(90 + 165 * fade))
            seg = []
    if len(seg) > 1: cv.line(seg, 1.0 + 1.2 * fade, 'ink', int(90 + 165 * fade))
    # side walls
    for sgn in (-1, 1):
        cv.seg(CX + sgn * Rw, CY0 + (k - 1) * GAP, CX + sgn * Rw, CY0 + k * GAP, 0.8, 'ink', int(60 + 120 * fade))

# ---- top 30 um: the surviving wafer, cut into dies (erase anything beneath)
for L in cv.layers.values():
    dd = ImageDraw.Draw(L)
    pts = [P(Rw * math.cos(t), Rw * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 800)]
    dd.polygon([(x * SS, y * SS) for x, y in pts], fill=0)
nx = int(2 * Rw / dw) + 2; ny = int(2 * Rw / dh) + 2
ox = -dw / 2 - dw * (nx // 2); oy = -dh / 2 - dh * (ny // 2)
good = lost = inked = 0
for i in range(nx + 1):
    for j in range(ny + 1):
        ua, va = ox + i * dw + st / 2, oy + j * dh + st / 2
        ub, vb = ua + dw - st, va + dh - st
        cs = [(ua, va), (ub, va), (ua, vb), (ub, vb)]
        din = [math.hypot(u, v) < Rw - excl for u, v in cs]
        anyin = any(math.hypot(u, v) < Rw for u, v in cs)
        if all(din):
            good += 1
            quad = [P(ua, va), P(ub, va), P(ub, vb), P(ua, vb), P(ua, va)]
            cv.line(quad, 1.1, 'ink', 230)
            # the one surviving stratum: a heavy top edge on each die
            cv.seg(*P(ua + 1, va + 2), *P(ub - 1, va + 2), 2.4, 'ink')
            if rng.random() < DATA["probe_ink_fraction"]:
                inked += 1
                x, y = P((ua + ub) / 2, (va + vb) / 2)
                cv.d['ink'].ellipse([(x - 7) * SS, (y - 7 * TILT) * SS, (x + 7) * SS, (y + 7 * TILT) * SS], fill=255)
        elif anyin:
            lost += 1
            for (p, q) in (((ua, va), (ub, va)), ((ub, va), (ub, vb)), ((ub, vb), (ua, vb)), ((ua, vb), (ua, va))):
                ts = np.linspace(0, 1, 40)
                pts = [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in ts]
                pts = [P(*pp) for pp in pts if math.hypot(*pp) < Rw - 3]
                if len(pts) > 1: cv.line(pts, 0.8, 'ink', 120)
# wafer edge + notch (6 o'clock) + exclusion ring
th = np.linspace(0, 2 * math.pi, 1600)
notch = math.pi / 2
pts = []
for t in th:
    rr = Rw
    dt = abs((t - notch + math.pi) % (2 * math.pi) - math.pi)
    if dt < 0.012: rr = Rw - pxmm * (1 - dt / 0.012)
    pts.append(P(rr * math.cos(t), rr * math.sin(t)))
cv.line(pts, 3.0, 'ink')
cv.line([P((Rw - excl) * math.cos(t), (Rw - excl) * math.sin(t)) for t in th], 0.8, 'ink', 150)
# front wall of the surviving 30 um (thin solid band)
cv.line([P(Rw * math.cos(t), Rw * math.sin(t)) for t in np.linspace(0, math.pi, 600)], 2.0, 'ink')
cv.line([(x, y + 30 * GAP / 775 * 26 / 26 * 0.0 + 2.6) for x, y in [P(Rw * math.cos(t), Rw * math.sin(t)) for t in np.linspace(0, math.pi, 600)]], 2.0, 'ink')

DATA["mapping"] = {
  "disc": "300 mm wafer at 7 px/mm, viewed obliquely (vertical scale 0.42); notch at 6 o'clock; 3 mm edge-exclusion ring",
  "dies": "10 x 11 mm grid on the surviving top layer; partial edge dies drawn faint (lost)",
  "strata": "775 um / 30 um = 26 strata: the top one survives as the die map, the 25 below are stacked crescents that fade and break apart with depth (the 745 um ground away)",
  "grind arcs": "backgrind wheel marks (arcs through the wafer centre, wheel radius ~ wafer radius) in the accent, density and opacity fall with depth",
  "ink dots": "~9% of dies receive a probe ink dot (fails), deterministic from seed",
}
DATA["counts"] = {"good_dies": good, "edge_dies_lost": lost, "probe_inked": inked}
cv.plate_number(26)
write_data(26, DATA)
render(cv, 26, 'cut')
print(DATA["counts"])
