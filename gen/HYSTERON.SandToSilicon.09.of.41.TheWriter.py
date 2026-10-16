"""09 - The Writer. A multi-beam mask writer as an electron-optical schematic: the full
512 x 512 aperture array (262,144 beamlets, every one drawn) is demagnified through a
crossover onto the mask, where a curvilinear pattern is written pixel by pixel in accent."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "09 - The Writer", "seed": SEED,
  "beamlets": 262144, "array": [512, 512], "beam_energy_keV": 50,
  "beam_size_nm": {"MBM-1000": 10, "MBM-3000": 12}, "array_field_um": 82,
  "current_density_A_per_cm2": {"MBM-1000": 2.0, "MBM-3000": 3.6},
  "dose_example_uC_per_cm2": 200, "MBM-3000_write_time_h": 10.5,
  "mapping": {
    "aperture array": "all 262,144 apertures drawn as dots on a 512 x 512 grid in oblique view (2.2 px pitch; the grid's moire is real)",
    "blanking": "a seeded 3% of apertures are blanked (open rings) as the pattern requires",
    "beams": "the array's boundary and a sampled 1-in-32 lattice of beamlets converge through a crossover (demagnification) and re-expand onto the writing field",
    "written field": "16 staggered contacts reshaped curvilinear with broken sub-resolution assist rings (ILT-style), rasterised into 96 x 96 beam pixels; per-pixel dose in 4 grey levels shown as accent stipple density",
  },
  "sources": [
    "https://eipbn.org/abstracts/2018/papers/9B-1.pdf (MBM-1000: 512 x 512 = 262,144 beams, 10 nm beam, 2 A/cm2, 82 um field, 50 kV)",
    "https://www.ebeam.org/docs/GH-E-0155-EBI2018-NuFlare_forweb.pdf (NuFlare MBM-1000 overview, pixel-level dose correction)",
    "https://exa.ai/library/publication/w97wpcjyp9q (MBM-3000: 50 keV, 12 nm beamlets, 3.6 A/cm2, doubled beam count)",
    "https://sah.borca.ai/papers/272740033 (MBM-3000 progress: 10.5 h at 200 uC/cm2)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
cx = OUT / 2
# oblique square: u along x, v receding
CA, SA = math.cos(math.radians(25)), math.sin(math.radians(25))
def Q(u, v, yc, half):
    """u,v in [-1,1] -> screen; 25-degree dimetric view of a horizontal square (as plate 08)"""
    return (cx + (u - v) * half * CA, yc + (u + v) * half * SA)
# ---- aperture plate
yA, hA = 800, 640
corners = [Q(-1, -1, yA, hA), Q(1, -1, yA, hA), Q(1, 1, yA, hA), Q(-1, 1, yA, hA)]
# plate thickness on the two visible front faces
th = 30
for a_, b_ in ((corners[1], corners[2]), (corners[2], corners[3])):
    for t in np.linspace(0, 1, 90):
        x = a_[0] + (b_[0] - a_[0]) * t; y = a_[1] + (b_[1] - a_[1]) * t
        cv.seg(x, y, x, y + th, 0.8)
    cv.line([a_, (a_[0], a_[1] + th), (b_[0], b_[1] + th), b_], 1.8)
BEAMS_LATER = True
inset = 0.9
N = 512
g = (np.arange(N) + 0.5) / N * 2 - 1
U, V = np.meshgrid(g * inset, g * inset)
X = cx + (U - V) * hA * CA; Y = yA + (U + V) * hA * SA
blank = rng.random((N, N)) < 0.03
yX = 1640
yF, hF = 2260, 400
xo = (cx + 0, yX)
sel = [(i, j) for i in range(0, N, 32) for j in range(0, N, 32)]
sel += [(i, 0) for i in range(0, N, 16)] + [(i, N - 1) for i in range(0, N, 16)] + [(0, j) for j in range(0, N, 16)] + [(N - 1, j) for j in range(0, N, 16)]
for (i, j) in sel:
    p0 = (X[j, i], Y[j, i] + 6)
    u, v = g[i] * inset, g[j] * inset
    p1 = Q(-u * 0.92, -v * 0.92, yF, hF)               # image inverted through the crossover
    w = 0.55 if (0 < i < N - 1 and 0 < j < N - 1) else 0.9
    cv.line([p0, (xo[0] + (p0[0] - xo[0]) * 0.02, xo[1] + rng.normal(0, 1))], w)
    cv.line([(xo[0] + (p1[0] - xo[0]) * 0.02, xo[1]), p1], w)
cv.erase_poly(corners)                                  # the plate hides the beams above it
cv.line(corners + [corners[0]], 2.4)
# paint apertures directly as a raster for speed: tiny dots
from PIL import ImageDraw
d = cv.d['ink']
for x, y, bl in zip(X.ravel(), Y.ravel(), blank.ravel()):
    if bl: continue
    d.point((x * SS, y * SS), fill=255); d.point((x * SS + 1, y * SS), fill=255)
for x, y in zip(X[blank], Y[blank]):
    d.ellipse([(x - 0.9) * SS, (y - 0.9) * SS, (x + 0.9) * SS, (y + 0.9) * SS], outline=200)
DATA["blanked"] = int(blank.sum())

# ---- crossover and writing field
Fc = [Q(-1, -1, yF, hF), Q(1, -1, yF, hF), Q(1, 1, yF, hF), Q(-1, 1, yF, hF)]
# crossover: projection lens rings
for r_ in (120, 150):
    th_ = np.linspace(0, 2 * math.pi, 300)
    cv.line(list(zip(cx + r_ * 2.0 * np.cos(th_), yX + r_ * 0.28 * np.sin(th_))), 1.6)
cv.circle(*xo, 6, 1.6, 'accent')

# ---- the written field: curvilinear pattern rasterised to beam pixels
cv.erase_poly(Fc)
cv.line(Fc + [Fc[0]], 2.4)
P_ = 96
yy_, xx_ = np.mgrid[0:P_, 0:P_].astype(float)
contacts = np.zeros((P_, P_), bool)
for ci_ in range(4):
    for cj_ in range(4):
        x0_, y0_ = 12 + ci_ * 24 + (cj_ % 2) * 6, 12 + cj_ * 24
        contacts |= (np.abs(xx_ - x0_) / 5.2) ** 2.4 + (np.abs(yy_ - y0_) / 4.6) ** 2.4 < 1
dd = ndimage.distance_transform_edt(~contacts)
wob = ndimage.gaussian_filter(rng.standard_normal((P_, P_)), 3); wob /= np.abs(wob).max()
main = ndimage.binary_opening(dd < 1.5 + 1.2 * wob, iterations=1) | contacts
main = ndimage.gaussian_filter(main.astype(float), 1.2) > 0.5          # rounded, curvilinear
assist = (np.abs(dd - (8.0 + 1.5 * wob)) < 1.05) & (wob > -0.45)        # broken assist rings
mask = main | assist
DATA["pattern"] = "16 staggered contacts with curvilinear (ILT-style) shapes and broken sub-resolution assist rings, from seeded noise"
# dose levels: edge pixels get partial dose (pixel-level dose correction)
dist_in = ndimage.distance_transform_edt(mask); dist_out = ndimage.distance_transform_edt(~mask)
dose = ndimage.gaussian_filter(mask.astype(float), 0.6)       # pixel-level dose: edge pixels get partial dose
lv = np.where(mask, np.maximum(np.round(dose * 4) / 4, 0.25), 0.0)
DATA["pixels"] = {"grid": [P_, P_], "written": int((lv > 0).sum()), "partial_dose": int(((lv > 0) & (lv < 1)).sum())}
for a in range(P_):
    for b in range(P_):
        if lv[b, a] <= 0: continue
        u0, u1 = -1 + 2 * a / P_, -1 + 2 * (a + 1) / P_
        v0, v1 = -1 + 2 * b / P_, -1 + 2 * (b + 1) / P_
        cell = [Q(u0, v0, yF, hF), Q(u1, v0, yF, hF), Q(u1, v1, yF, hF), Q(u0, v1, yF, hF)]
        if lv[b, a] >= 1:
            cv.poly(cell, 'accent')
        else:
            cxp = sum(p[0] for p in cell) / 4; cyp = sum(p[1] for p in cell) / 4
            for _ in range(int(lv[b, a] * 8)):
                cv.dot(cxp + rng.uniform(-4, 4), cyp + rng.uniform(-1.5, 1.5), 1.1, 'accent')
# pixel grid hairlines on the field
for t in range(0, P_ + 1, 8):
    cv.line([Q(-1 + 2 * t / P_, -1, yF, hF), Q(-1 + 2 * t / P_, 1, yF, hF)], 0.6)
    cv.line([Q(-1, -1 + 2 * t / P_, yF, hF), Q(1, -1 + 2 * t / P_, yF, hF)], 0.6)
# substrate edge under the field
cv.line([Fc[3], (Fc[3][0], Fc[3][1] + 40), (Fc[2][0], Fc[2][1] + 40), Fc[2]], 1.8)
cv.line([Fc[1], (Fc[1][0], Fc[1][1] + 40), (Fc[2][0], Fc[2][1] + 40)], 1.8)

cv.plate_number(9)
write_data(9, DATA)
render(cv, 9, 'writer')
print(DATA["blanked"], DATA["pixels"])
