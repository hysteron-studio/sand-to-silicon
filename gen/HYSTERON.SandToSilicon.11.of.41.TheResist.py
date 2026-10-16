"""11 - The Resist. A 96 x 96 nm patch of EUV chemically amplified resist under a
16 nm half-pitch line image at 30 mJ/cm2: every photon is a dot (~20 per nm2 at full
intensity), absorbed ones are accent rings, and the printed edges come out ragged from
shot noise and acid blur alone."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
E_ph = 92 * 1.602176634e-19
dose = 30e-3                                   # J/cm2
ph_per_nm2 = dose / 1e14 / E_ph
DATA = {
  "piece": "11 - The Resist", "seed": SEED,
  "photon_energy_eV": 92, "wavelength_nm": 13.5, "dose_mJ_per_cm2": 30,
  "photons_per_nm2_at_full_intensity": round(ph_per_nm2, 2),
  "pattern": {"half_pitch_nm": 16, "pitch_nm": 32, "image_contrast": 0.8},
  "film": {"thickness_nm": 35, "absorption_per_um": 4.5, "absorbed_fraction": round(1 - math.exp(-4.5 * 0.035), 3)},
  "acids_per_absorbed_photon": 2.5, "acid_diffusion_length_nm": 7.0,
  "patch_nm": 96, "field": "circular field of view, 96 nm diameter", "px_per_nm": 24,
  "mapping": {
    "dots": "every incident photon on the patch, Poisson-sampled from the aerial image I(x) = 0.5 + 0.4 cos(2 pi x / 32 nm) at 30 mJ/cm2 (ink points)",
    "accent rings": "photons absorbed in the 35 nm film (absorbed fraction 1 - exp(-alpha t)); each releases a Poisson(2.5) number of photo-acids",
    "edges": "acid map blurred by the 7 nm diffusion length; the development threshold is set so half the area clears; the iso-line is the printed resist edge, its raggedness is pure stochastics",
    "hatching": "resist that remains after development (positive tone: exposed regions dissolve)",
  },
  "sources": [
    "Photon energy E = hc/lambda = 91.8 eV at 13.5 nm; 30 mJ/cm2 / 92 eV = 20.4 photons per nm2 (computed)",
    "https://escholarship.org/uc/item/8q3089t2 (EUV shot noise and secondary electrons in resists)",
    "https://exa.ai/library/publication/t33bdv8gyq5 (CAR EUV stochastics; acid diffusion length ~7.0-7.6 nm at 30 mJ/cm2 for 11 nm hp)",
    "https://www.jstage.jst.go.jp/article/photopolymer/26/5/26_649/_pdf/-char/en (EUV resist design for 15 nm half pitch and below)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
S = DATA["px_per_nm"]; P = DATA["patch_nm"]
x0 = y0 = (OUT - P * S) / 2
I = lambda x: 0.5 + 0.4 * np.cos(2 * math.pi * (x - 8) / 32)     # bright (exposed) at x = 8, 40, 72 nm
# photons
lam_total = ph_per_nm2 * P * P * 0.5
n_ph = rng.poisson(lam_total)
px = rng.uniform(0, P, n_ph * 2); keep = rng.random(n_ph * 2) < I(px) / 0.9
px = px[keep][:n_ph]; py = rng.uniform(0, P, len(px))
incirc = (px - P / 2) ** 2 + (py - P / 2) ** 2 < (P / 2 - 0.15) ** 2
absorbed = rng.random(len(px)) < DATA["film"]["absorbed_fraction"]
DATA["counts"] = {"incident_photons_in_view": int(incirc.sum()), "absorbed_in_view": int((absorbed & incirc).sum()), "simulated_square_photons": int(len(px))}
d = cv.d['ink']
for x, y in zip(px[~absorbed & incirc], py[~absorbed & incirc]):
    X, Y = (x0 + x * S) * SS, (y0 + y * S) * SS
    d.point((X, Y), fill=200); d.point((X + 1, Y), fill=200); d.point((X, Y + 1), fill=200)
# acids
res = 0.25
G = int(P / res)
acid = np.zeros((G, G), np.float32)
na = 0
for x, y in zip(px[absorbed], py[absorbed]):
    for _ in range(rng.poisson(DATA["acids_per_absorbed_photon"])):
        ax = (x + rng.normal(0, 1.5)) % P; ay = (y + rng.normal(0, 1.5)) % P
        acid[int(ay / res), int(ax / res)] += 1; na += 1
DATA["counts"]["acids"] = na
blur = ndimage.gaussian_filter(acid, DATA["acid_diffusion_length_nm"] / math.sqrt(2) / res, mode='wrap')
thr = float(np.median(blur))
remain = blur < thr
# hatch remaining resist
hy, hx = np.mgrid[0:G, 0:G]
hatch = (((hx + hy) % 12) < 2).astype(np.float32)
big = np.zeros((OUT, OUT), np.float32)
from PIL import Image as _I
rm = np.asarray(_I.fromarray((remain * 255).astype(np.uint8)).resize((P * S, P * S), _I.NEAREST)) / 255.0
hh = np.zeros((P * S, P * S), np.float32)
yy, xx = np.mgrid[0:P * S, 0:P * S]
hh[((xx - yy) % 14) < 2] = 0.95
hh[((xx - yy) % 14) >= 2] = 0.0
hh *= ((xx - P * S / 2) ** 2 + (yy - P * S / 2) ** 2 < (P * S / 2 - 3) ** 2)
big[int(y0):int(y0) + P * S, int(x0):int(x0) + P * S] = rm * hh
cv.paint(big, 'ink')
# edges
Rc = P * S / 2; ccx, ccy = x0 + Rc, y0 + Rc
for c in contours(blur, thr, res * S, res * S, x0, y0):
    seg = []
    for p in c:
        if (p[0] - ccx) ** 2 + (p[1] - ccy) ** 2 < (Rc - 3) ** 2: seg.append(p)
        else:
            if len(seg) > 3: cv.line(seg, 3.2)
            seg = []
    if len(seg) > 3: cv.line(seg, 3.2)
# absorbed photons as accent rings on top
for x, y in zip(px[absorbed & incirc], py[absorbed & incirc]):
    cv.circle(x0 + x * S, y0 + y * S, 3.4, 1.2, 'accent')
# patch frame and nm ticks along the bottom (every 8 nm, heavier every 32)
th = np.linspace(0, 2 * math.pi, 900)
cv.line(list(zip(ccx + Rc * np.cos(th), ccy + Rc * np.sin(th))), 2.6)
cv.line(list(zip(ccx + (Rc + 18) * np.cos(th), ccy + (Rc + 18) * np.sin(th))), 1.0)
# nm scale around the rim: a tick every 4 nm of arc-projected x, heavier at each 32 nm pitch
for t in range(0, P + 1, 4):
    h = 30 if t % 32 == 8 else (16 if t % 8 == 0 else 8)
    xt = x0 + t * S
    yb = ccy + math.sqrt(max(0, (Rc + 18) ** 2 - (xt - ccx) ** 2))
    cv.seg(xt, yb + 8, xt, yb + 8 + h, 1.3)

cv.plate_number(11)
write_data(11, DATA)
render(cv, 11, 'resist')
print(DATA["photons_per_nm2_at_full_intensity"], DATA["counts"])
