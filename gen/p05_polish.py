"""05 - The Polish. A 300 mm prime wafer as a nanometre contour map: a few tens of nm of
dome, pad rings and nanotopography, the steep edge roll-off, and the 26 x 33 mm exposure
sites over which site flatness (SFQR) is judged; the worst site is hatched in accent."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "05 - The Polish", "seed": SEED,
  "wafer": {"diameter_mm": 300, "thickness_um": 775, "notch": "<110>, 1 mm"},
  "spec_context": {"SFQR_nm": "< 130 (production prime), < 80 (advanced)", "TTV_um": "< 1", "Ra_nm": "< 0.1",
                   "nanotopography": "P-V in 2 mm / 10 mm windows, wavelengths 0.1-20 mm, a few nm to hundreds of nm"},
  "polish": "double-side stock removal with 80-150 nm colloidal silica, final single-side touch polish with 20-50 nm silica",
  "model_surface": {"dome_nm": 38, "pad_ring_amplitude_nm": 4.0, "pad_ring_wavelength_mm": 9,
                    "nanotopography_rms_nm": 1.6, "nanotopography_band_mm": [2, 20], "edge_rolloff_nm": 160, "edge_rolloff_width_mm": 2.5, "wedge_nm": 6},
  "contour_interval_nm": 3, "edge_exclusion_mm": 2, "site_mm": [26, 33],
  "scale_px_per_mm": 7.65,
  "mapping": {
    "contours": "iso-height lines of the modelled front surface every 3 nm, every fifth (15 nm) heavier; the dark rim is the edge roll-off where ~55 contours crowd into 2.5 mm",
    "sites": "the full-site grid of 26 x 33 mm lithography fields inside 2 mm edge exclusion, accent hairlines",
    "worst site": "the site with the largest least-squares range (SFQR) is hatched in accent; values written to data",
  },
  "sources": [
    "https://jeez-semicon.com/blog/the-complete-guide-to-silicon-wafer-polishing/ (300 mm prime: SFQR < 0.13 um on 26x32 mm sites, TTV < 1 um, Ra < 0.1 nm; colloidal silica 80-150 nm DSP, 20-50 nm final)",
    "https://semiconductorx.com/wafer-production-polishing.html (DSP + final CMP, SFQR < 100-130 nm, 26 x 33 mm fields)",
    "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=822272 (NIST 300 mm flatness/nanotopography metrology)",
    "https://docest.com/doc/98843/background-statement-for-semi-draft-document-3335d (SEMI nanotopography: wavelengths < 20 mm, P-V few nm to hundreds of nm)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
k = DATA["scale_px_per_mm"]; cx = cy = OUT / 2
Rw = 150.0
Ng = 1500; res = 300.0 / Ng                          # 0.2 mm grid
yy, xx = (np.mgrid[0:Ng, 0:Ng] + 0.5) * res - 150.0
r = np.hypot(xx, yy)
m = DATA["model_surface"]
h = m["dome_nm"] * (1 - (r / Rw) ** 2)
h += m["pad_ring_amplitude_nm"] * np.sin(2 * math.pi * r / m["pad_ring_wavelength_mm"] + 0.7) * (0.6 + 0.4 * r / Rw)
# band-passed nanotopography 2-20 mm
n = rng.standard_normal((Ng, Ng)).astype(np.float32)
bp = ndimage.gaussian_filter(n, 2.0 / res / 2.355) - ndimage.gaussian_filter(n, 20.0 / res / 2.355)
bp = ndimage.gaussian_filter(n, 4.0 / res / 2.355) - ndimage.gaussian_filter(n, 20.0 / res / 2.355)
bp = bp / bp.std() * m["nanotopography_rms_nm"]
h += bp
h += 6.0 * (xx * 0.6 + yy * 0.8) / Rw          # residual carrier wedge, 6 nm
edge = Rw - r
h -= m["edge_rolloff_nm"] * np.exp(-np.clip(edge, 0, None) / (m["edge_rolloff_width_mm"] / 2.2))
# notch
nd = np.hypot(xx, yy - Rw)
inside = (r < Rw) & ~((nd < 1.4) & (np.abs(xx) < (yy - (Rw - 1.0)) + 0.01))
hm = np.where(inside, h, np.nan)

# --- contours
ci = DATA["contour_interval_nm"]
H = np.where(inside, h, -400.0)
lv = np.arange(math.floor(np.nanmin(hm) / ci) * ci, np.nanmax(hm) + ci, ci)
DATA["height_range_nm"] = [round(float(np.nanmin(hm)), 1), round(float(np.nanmax(hm)), 1)]
nl = 0
for L in lv:
    heavy = (round(L / ci) % 5 == 0)
    for c in contours(H, L, res * k, res * k, cx - 150 * k, cy - 150 * k):
        if len(c) < 4: continue
        cv.line(c, 1.5 if heavy else 0.75); nl += 1
DATA["contour_lines_drawn"] = nl
# wafer outline + notch
th = np.linspace(0, 2 * math.pi, 1600)
out = []
for t in th:
    x, y = Rw * math.cos(t), Rw * math.sin(t)
    if abs(x) < 1.6 and y > 0: y = Rw - 1.0 - (1.6 - abs(x)) * 0.0 - (1.0 - abs(x) / 1.6)
    out.append((cx + x * k, cy + y * k))
cv.line(out + [out[0]], 2.6)

# --- sites: 26 x 33 grid, centred, fully inside 2 mm edge exclusion
sw, sh = DATA["site_mm"]; ee = Rw - DATA["edge_exclusion_mm"]
sites = []
for i in range(-6, 7):
    for j in range(-5, 6):
        x0, y0 = i * sw - sw / 2, j * sh - sh / 2 + sh / 2
        corners = [(x0, y0), (x0 + sw, y0), (x0, y0 + sh), (x0 + sw, y0 + sh)]
        if all(math.hypot(a, b) <= ee for a, b in corners): sites.append((x0, y0))
def sfqr(x0, y0):
    sl = (xx >= x0) & (xx < x0 + sw) & (yy >= y0) & (yy < y0 + sh)
    X = np.stack([xx[sl], yy[sl], np.ones(sl.sum())], 1); z = h[sl]
    c, *_ = np.linalg.lstsq(X, z, rcond=None); res_ = z - X @ c
    return float(res_.max() - res_.min())
vals = [sfqr(*s) for s in sites]
worst = int(np.argmax(vals))
DATA["sites"] = len(sites); DATA["SFQR_nm"] = {"max": round(max(vals), 1), "median": round(float(np.median(vals)), 1), "min": round(min(vals), 1)}
for (x0, y0) in sites:
    P = [(cx + x0 * k, cy + y0 * k), (cx + (x0 + sw) * k, cy + y0 * k), (cx + (x0 + sw) * k, cy + (y0 + sh) * k), (cx + x0 * k, cy + (y0 + sh) * k)]
    cv.line(P + [P[0]], 1.1, 'accent')
x0, y0 = sites[worst]
P = [(cx + x0 * k, cy + y0 * k), (cx + (x0 + sw) * k, cy + y0 * k), (cx + (x0 + sw) * k, cy + (y0 + sh) * k), (cx + x0 * k, cy + (y0 + sh) * k)]
cv.line(P + [P[0]], 2.6, 'accent')
cv.hatch_poly(P, 45, 9, 1.3, 'accent')
# crosshair ticks at the wafer centre and the four quadrant marks
for a in range(4):
    t = a * math.pi / 2
    cv.seg(cx + (Rw + 6) * k * math.cos(t), cy + (Rw + 6) * k * math.sin(t), cx + (Rw + 14) * k * math.cos(t), cy + (Rw + 14) * k * math.sin(t), 1.6)

cv.plate_number(5)
write_data(5, DATA)
render(cv, 5, 'polish')
print(DATA["height_range_nm"], DATA["SFQR_nm"], len(sites), nl)
