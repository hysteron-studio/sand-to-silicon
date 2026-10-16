"""13 - The Light. A tin droplet stream meets the laser at the first focus of the collector;
13.5 nm wavefronts leave the plasma, reflect from a 40-bilayer Mo/Si stack and converge on
the intermediate focus. The two families of wavefronts interfere as moire."""
import math, numpy as np
from style import *
# v1 prototype plate III; renumbered to master-sequence #13

SEED = None  # private, not published
DATA = {
  "piece": "13 - The Light", "seed": SEED,
  "wavelength_nm": 13.5, "bilayer_period_nm": 6.9, "bilayers": 40, "mo_fraction_gamma": 0.4,
  "mo_thickness_nm": 2.76, "si_thickness_nm": 4.14, "ru_cap_nm": 2.5, "peak_reflectivity": 0.70,
  "tin_droplet_diameter_um": 25, "droplet_rate_hz": 50000, "droplet_speed_m_s": 70,
  "derived_droplet_spacing_mm": 70 / 50000 * 1000,
  "derived_spacing_to_diameter": (70 / 50000 * 1e6) / 25,
  "px_per_nm_optics": 2.4, "px_per_nm_mirror": 1.55,
  "mapping": {
    "wavefront spacing": "13.5 nm x 2.4 = 32.4 px; emitted fronts centred on the plasma, reflected fronts centred on the intermediate focus",
    "reflected opacity": "drawn at 70% of emitted ink density = peak Mo/Si reflectivity",
    "mirror": "40 concentric bilayers; each Mo band = 2.76 nm (ink), Si = 4.14 nm (paper), Ru cap 2.5 nm on the inner face; period 6.9 nm x 2.4 px",
    "droplets": "spacing/diameter = 56 (1.4 mm at 70 m/s / 50 kHz vs 25 um); left to right: sphere -> pre-pulse pancake -> plasma",
  },
  "sources": [
    "https://www.asml.com/en/technology/lithography-principles/light-and-lasers (13.5 nm; ~25 um tin droplets, 70 m/s, 50,000 per second; pre-pulse pancake)",
    "Active multilayer mirrors for reflectance tuning at EUV wavelengths (J. Phys. D 2012): Mo/Si period 6.9 nm, Mo = 40%, R ~69.5-70.3%",
    "https://www.osti.gov/servlets/purl/802924 (standard Mo/Si, 40 bilayers, period 6.9 nm; 70% at 13.5 nm)",
    "https://docs.rs/oxiphoton (standard EUVL mirror: 40 Mo/Si bilayers + 2.5 nm Ru cap)",
    "Light sources for HVM EUV lithography (review): ~30 um droplets at 50 kHz, ellipsoidal collector, intermediate focus",
  ],
}
cv = Canvas(SEED); rng = cv.rng
k = DATA["px_per_nm_optics"]
lam = 13.5 * k
P = np.array([1500.0, 1520.0])     # plasma at first focus
IF = np.array([1500.0, 430.0])     # intermediate focus
Rm = 560.0                          # inner radius of collector (around P)
a0, a1 = math.radians(14), math.radians(166)   # mirror spans the lower bowl (angles measured downward)

def arc(c, r, t0, t1, n=None):
    n = n or max(16, int(abs(t1 - t0) * r / 6))
    t = np.linspace(t0, t1, n)
    return list(zip(c[0] + r * np.cos(t), c[1] + r * np.sin(t)))

# ---- mirror: Ru cap + 40 Mo/Si bilayers (ink = Mo)
km = DATA['px_per_nm_mirror']
r = Rm
# Ru cap
for s in np.arange(0, 2.5 * km, 1.2):
    cv.line(arc(P, r + s, a0, a1), 1.6, 'ink')
r += 2.5 * km
for b in range(40):
    mo = 2.76 * km; si = 4.14 * km
    # Si first (paper), then Mo (ink) - from the surface inward
    r += si
    for s in np.arange(0, mo, 1.1):
        wob = 0.0
        cv.line(arc(P, r + s, a0 - 0.002 * b, a1 + 0.002 * b), 1.5, 'ink')
    r += mo
R_out = r
# substrate hatching below the stack (ULE glass): oblique short hatches
for t in np.linspace(a0 + 0.01, a1 - 0.01, 380):
    rr0 = R_out + 12; rr1 = rr0 + 34 + 14 * math.sin(t * 9)
    cv.seg(P[0] + rr0 * math.cos(t), P[1] + rr0 * math.sin(t), P[0] + rr1 * math.cos(t + 0.03), P[1] + rr1 * math.sin(t + 0.03), 1.0, 'ink', 170)

# ---- rim points and converging cone
rimL = P + Rm * np.array([math.cos(a1), math.sin(a1)])
rimR = P + Rm * np.array([math.cos(a0), math.sin(a0)])
for rim in (rimL, rimR):
    cv.seg(rim[0], rim[1], IF[0], IF[1], 1.4, 'ink', 200)
coneL = math.atan2(rimL[1] - IF[1], rimL[0] - IF[0]); coneR = math.atan2(rimR[1] - IF[1], rimR[0] - IF[0])

# ---- emitted wavefronts from the plasma (accent, full strength) inside the collector
for i in range(1, int(Rm / lam)):
    rr = i * lam
    cv.line(arc(P, rr, 0, 2 * math.pi), 5.2, 'accent')
# ---- reflected wavefronts converging on IF: clipped to the cone, 70% density
dmax = np.linalg.norm(rimL - IF)
for i in range(1, int(dmax / lam) + 1):
    rr = i * lam
    cv.line(arc(IF, rr, coneR, coneL), 5.2, 'accent', val=int(255 * 0.70))

# ---- droplet stream, left to right along the plasma height
sp_ratio = DATA["derived_spacing_to_diameter"]   # 56
dia = 5.0
spacing = dia * sp_ratio                           # 280 px
xs = P[0] - spacing * np.arange(1, 6)
for x in xs:
    if x > MARGIN: cv.dot(x, P[1], dia / 2 + 1, 'ink')
# pre-pulse pancake just before the focus
cv.poly([(P[0] - 0.45 * spacing + 4 * math.cos(t), P[1] + 34 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)], 'ink')
# trajectory hairline
cv.seg(MARGIN, P[1], P[0] - 0.45 * spacing - 10, P[1], 0.8, 'ink', 140)
# plasma: dense stipple burst in accent
n = 9000
rr = np.abs(rng.standard_cauchy(n)) * 7
rr = rr[rr < 120]; n = len(rr)
th = rng.uniform(0, 2 * math.pi, n)
for x, y in zip(P[0] + rr * np.cos(th), P[1] + rr * np.sin(th)):
    cv.dot(x, y, 1.3, 'ink')
cv.dot(P[0], P[1], 8, 'accent')
# IF: a small aperture
cv.circle(IF[0], IF[1], 10, 1.6, 'ink')
cv.seg(IF[0] - 60, IF[1], IF[0] - 18, IF[1], 2.2); cv.seg(IF[0] + 18, IF[1], IF[0] + 60, IF[1], 2.2)

cv.plate_number(13)
write_data(13, DATA)
render(cv, 13, 'light')
