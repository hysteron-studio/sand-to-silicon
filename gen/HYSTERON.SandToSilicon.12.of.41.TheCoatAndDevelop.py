"""12 - The Coat & Develop. A puddle of resist dispensed on a spinning 300 mm wafer, drawn
as a time-lapse of its spreading front: the front grows as (1 + 4Kh0^2 t)^(1/4) from thin-film
spin-coating theory while the wafer turns, so its fingering instabilities wind into spirals."""
import math, numpy as np
from style import *

SEED = None  # private, not published
rho, eta, h0 = 1000.0, 0.006, 1.9e-3       # kg/m3, Pa s, m (dispensed puddle; illustrative EBP parameters)
rpm = 3000; w = rpm * 2 * math.pi / 60
K = rho * w * w / (3 * eta)
DATA = {
  "piece": "12 - The Coat & Develop", "seed": SEED,
  "wafer_mm": 300, "spin_rpm": rpm, "resist_viscosity_Pa_s": eta, "initial_puddle_mm": h0 * 1e3, "density_kg_m3": rho,
  "model": "Emslie-Bonner-Peck thin-film spin-off: dh/dt = -2 K h^3, K = rho w^2 / (3 eta) -> h(t) = h0 / sqrt(1 + 4 K h0^2 t); final thickness scales as w^(-1/2)",
  "derived": {"K_per_m2_s": round(K, 1), "4Kh0^2_per_s": round(4 * K * h0 * h0, 3)},
  "developer": "2.38 wt% TMAH (0.26 N)",
  "fingers": 34,
  "mapping": {
    "fronts": "9 snapshots of the spreading resist front (ink, heavier with time), radius r_f(t) = r0 (1 + 4 K h0^2 t)^(1/4) from volume conservation with h(t), each rotated by w t with the wafer",
    "spirals": "the 34 finger tips followed continuously (accent): they turn with the wafer while the front advances, so each traces a spiral",
    "fingers": "34 seeded fingering lobes whose amplitude grows along the run; because the front turns with the wafer the finger tips trace spirals",
    "wafer": "300 mm wafer, notch, vacuum chuck rings at centre; the edge bead is the heavy accent ring at the rim",
    "thinning": "hairline concentric rings inside the first front, spaced by the EBP thickness decay",
  },
  "sources": [
    "https://www.microchemicals.com/dokumente/application_notes/spin_coating_photoresist.pdf (thickness ~ w^-1/2, spin dynamics, edge bead)",
    "https://www.ossila.com/pages/spin-coating (Emslie-Bonner-Peck model)",
    "https://microsi.com/wp-content/uploads/2015/06/SPIE-05-ShinEtsu-300mm-Paper.pdf (300 mm resist coating; 2.38% TMAH development)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
cx = cy = OUT / 2
k = 7.6                     # px per mm
Rw = 150 * k
# --- wafer
th = np.linspace(0, 2 * math.pi, 1600)
rim = []
for t in th:
    x, y = math.cos(t), math.sin(t)
    rr = Rw - (9 * max(0, 1 - abs(t - math.pi / 2) / 0.012))     # notch at 6 o'clock
    rim.append((cx + rr * x, cy + rr * y))
cv.line(rim + [rim[0]], 2.8)
# edge bead (accent) just inside the rim
for o in (5, 9, 13):
    cv.line(list(zip(cx + (Rw - o) * np.cos(th), cy + (Rw - o) * np.sin(th))), 2.2 if o == 9 else 1.0, 'accent')
# chuck rings
for r in (34, 52, 70, 88):
    cv.line(list(zip(cx + r * k * 0.35 * np.cos(th), cy + r * k * 0.35 * np.sin(th))), 1.0)

# --- fronts
NF = DATA["fingers"]
amp = rng.uniform(0.5, 1.0, NF); ph = rng.uniform(-0.25, 0.25, NF)
def finger(phi):
    phi = np.mod(phi, 2 * math.pi)
    out = np.zeros_like(phi)
    for i in range(NF):
        c = 2 * math.pi * (i + 0.5 + ph[i]) / NF
        d = np.angle(np.exp(1j * (phi - c)))
        out += amp[i] * np.exp(-(d / (0.32 * 2 * math.pi / NF)) ** 2)
    return out
r0 = 22 * k
T_end = None
# choose time span so the base front reaches 0.93 Rw: (1+a t)^(1/4) = 0.93 Rw / r0
a = 4 * K * h0 * h0
t_end = (((0.93 * Rw) / r0) ** 4 - 1) / a
DATA["derived"]["front_reaches_edge_s"] = round(t_end, 3)
DATA["derived"]["wafer_turns_during_spread"] = round(w * t_end / (2 * math.pi), 2)
# finger-tip pathlines: each tip turns with the wafer while the front advances -> spirals
tt = np.linspace(0, t_end, 900)
rf_t = r0 * (1 + a * tt) ** 0.25
A_t = 0.004 + 0.16 * (tt / t_end) ** 0.9
for i in range(NF):
    c = 2 * math.pi * (i + 0.5 + ph[i]) / NF
    rr = np.minimum(rf_t * (1 + A_t * amp[i] * 0.92), Rw - 16)
    ang = c + w * tt
    cv.line(list(zip(cx + rr * np.cos(ang), cy + rr * np.sin(ang))), 2.0, 'accent')
# a few front snapshots, heavier with time
nT = 9
rad = np.linspace(r0 * 1.25, 0.93 * Rw, nT)                 # snapshots evenly spaced in radius
times = ((rad / r0) ** 4 - 1) / a
phis = np.linspace(0, 2 * math.pi, 1800)
for j, t in enumerate(times):
    rf = r0 * (1 + a * t) ** 0.25
    A = 0.004 + 0.16 * (t / t_end) ** 0.9
    rot = w * t
    r = np.minimum(rf * (1 + A * finger(phis - rot)), Rw - 16)
    pts = list(zip(cx + r * np.cos(phis), cy + r * np.sin(phis)))
    cv.line(pts + [pts[0]], 1.0 + 2.2 * (j / (nT - 1)) ** 1.3, 'ink')
DATA["drawn"] = {"tip_spirals": NF, "front_snapshots": nT}
# --- inside the first front: EBP thinning rings
for j in range(1, 14):
    t = t_end * 0.002 * j ** 2
    hh = h0 / math.sqrt(1 + a * t)
    rr = r0 * (hh / h0) ** 1.3
    cv.line(list(zip(cx + rr * np.cos(th), cy + rr * np.sin(th))), 0.7)
# --- nozzle seen from above
cv.erase_circle(cx, cy, 30); cv.circle(cx, cy, 26, 2.2); cv.circle(cx, cy, 10, 1.4); cv.dot(cx, cy, 4)

cv.plate_number(12)
write_data(12, DATA)
render(cv, 12, 'coat')
print(DATA["derived"])
