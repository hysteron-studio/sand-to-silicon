"""14 - The Film. Cross-section of five high-aspect-ratio trenches lined by atomic layer
deposition: 100 TMA/H2O cycles at 1.1 A per cycle = 11 nm, every tenth cycle engraved as
one line that follows every wall and floor with the same thickness - conformality."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "14 - The Film", "seed": SEED,
  "process": "thermal ALD of Al2O3 from trimethylaluminium (TMA) and H2O, ~200 C",
  "growth_per_cycle_A": 1.1, "cycles": 100, "film_nm": 11.0,
  "trench": {"width_nm": 40, "depth_nm": 480, "aspect_ratio": 12, "count": 5, "pitch_nm": 100},
  "px_per_nm": 3.6,
  "mapping": {
    "geometry": "five trenches 40 nm wide and 480 nm deep (AR 12) in silicon, drawn to true proportion at 3.6 px/nm",
    "film": "iso-distance lines of the substrate surface every 10 cycles (10 x 1.1 A = 1.1 nm -> 4 px), 10 lines in accent, every 5th heavier; identical thickness on top, walls and floor",
    "gas": "precursor molecules above the surface as paired dots (TMA) and single dots (H2O), thinning with depth inside each trench (Knudsen transport)",
    "substrate": "silicon engraved with diagonal hatching",
  },
  "sources": [
    "https://pubs.aip.org/avs/jva/article-abstract/35/1/01B101/246298/Anomalously-high-alumina-atomic-layer-deposition (TMA/H2O Al2O3 saturated GPC ~1.1 A/cycle)",
    "https://pubs.rsc.org/en/content/articlehtml/2020/cp/d0cp03358h (ALD conformality in high-aspect-ratio channels)",
    "https://export.arxiv.org/pdf/2210.00749v2.pdf (modelling ALD conformality in AR ~50 NAND-like structures)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
S = DATA["px_per_nm"]
tw, td, pitch = 40 * S, 480 * S, 100 * S
n = 5
total = (n - 1) * pitch + tw
x_left = (OUT - total) / 2
y_surf = 700
# substrate mask at 1 px resolution
H = np.zeros((OUT, OUT), bool)
H[int(y_surf):OUT - MARGIN - 60, MARGIN:OUT - MARGIN] = True
for i in range(n):
    x0 = int(x_left + i * pitch)
    H[int(y_surf):int(y_surf + td), x0:int(x0 + tw)] = False
    # rounded trench floor
    yy, xx = np.mgrid[0:int(tw), 0:int(tw)]
    r = tw / 2
    cap = (xx - r + 0.5) ** 2 + (yy) ** 2 < r * r
    cap = cap[:H[int(y_surf + td):int(y_surf + td + tw), x0:int(x0 + tw)].shape[0]]
    H[int(y_surf + td):int(y_surf + td + tw), x0:int(x0 + tw)] &= ~cap
DT = ndimage.distance_transform_edt(~H)          # distance from the substrate into the open space
# substrate hatch via mask
yy, xx = np.mgrid[0:OUT, 0:OUT]
hatch = ((((xx + yy) % 19) < 2) & H).astype(np.float32)
cv.paint(hatch, 'ink', 0.9)
# substrate outline
for c in contours(H.astype(float), 0.5):
    if len(c) > 10: cv.line(c, 2.4)
# ALD film: one line per 10 cycles
step = 10 * DATA["growth_per_cycle_A"] / 10 * S
nl = 0
win = (xx > MARGIN + 2) & (xx < OUT - MARGIN - 2) & (yy > y_surf - 200) & (yy < y_surf + td + tw)
F = np.where(win, DT, 1e6).astype(np.float32)
for k in range(1, DATA["cycles"] // 10 + 1):
    for c in contours(F, k * step):
        if len(c) > 10:
            cv.line(c, 2.0 if k % 5 == 0 else 1.1, 'accent'); nl += 1
DATA["film_lines"] = DATA["cycles"] // 10
# precursor gas above and in the trenches
mol = 0
for _ in range(2600):
    x = rng.uniform(MARGIN + 10, OUT - MARGIN - 10)
    y = rng.uniform(MARGIN + 20, y_surf + td + 20)
    if y > y_surf - 30:
        # inside a trench? probability falls with depth
        inside = [i for i in range(n) if x_left + i * pitch + 30 < x < x_left + i * pitch + tw - 30]
        if not inside or y > y_surf + td: continue
        if rng.random() > math.exp(-(y - y_surf) / (td * 0.45)): continue
    elif y > y_surf - 60: continue
    if rng.random() < 0.5:
        a = rng.uniform(0, 6.3); d = 7
        cv.dot(x, y, 3.0); cv.dot(x + d * math.cos(a), y + d * math.sin(a), 2.2)
    else:
        cv.dot(x, y, 2.4)
    mol += 1
DATA["molecules_drawn"] = mol
cv.plate_number(14)
write_data(14, DATA)
render(cv, 14, 'film')
print(nl, mol, y_surf + td)
