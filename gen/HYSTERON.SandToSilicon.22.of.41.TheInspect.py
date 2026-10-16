"""22 - The Inspect. Die-to-die comparison as an optical inspector does it: twenty identical
dies engraved from one seeded layout, five of them carrying a tiny difference (missing line,
bridge, particle, extra via, break) ringed in accent; along the bottom, the difference
images - each die minus its neighbour - are empty except for the defect."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "22 - The Inspect", "title": "The Inspect", "seed": SEED,
  "dies": 20, "defects": 5, "method": "die-to-die comparison, deep-UV broadband plasma illumination",
  "mapping": {
    "layout": "one 380 px die layout from the seed: standard-cell rows, gate fingers, metal straps, a memory block",
    "dies": "drawn 20 times on a 5 x 4 grid at identical coordinates (sub-pixel stage jitter only)",
    "defects": "5 seeded single-feature differences, ringed in accent",
    "difference strip": "5 tiles = die minus neighbour; only the defect remains, in accent",
  },
  "sources": [
    "https://www.kla.com/products/chip-manufacturing/defect-inspection-review (broadband plasma patterned-wafer inspection)",
    "https://bbp.kla.com/",
  ],
}
cv = Canvas(SEED); rng = cv.rng
D = 380
L = np.zeros((D, D), bool)
# memory block
L[20:150, 20:170][::6, :] = True
L[20:150, 20:170][:, ::14] |= True
# standard-cell rows
y = 170
while y < D - 30:
    x = 14
    while x < D - 20:
        w = int(rng.integers(12, 40))
        for g in range(x + 3, x + w - 2, 5): L[y + 4:y + 26, g:g + 2] = True
        L[y:y + 2, x:x + w] = True; L[y + 28:y + 30, x:x + w] = True
        x += w + int(rng.integers(2, 6))
    y += 36
L[20:150, 190:360][::9, :] = True
for k in range(6): L[20:150, 200 + k * 28:203 + k * 28] = True
L[0:2, :] = L[-2:, :] = L[:, 0:2] = L[:, -2:] = True
cols, rows = 5, 4; gap = (OUT - 2 * MARGIN - cols * D) / (cols - 1)
x0, y0 = MARGIN, MARGIN + 20
big = np.zeros((OUT, OUT), np.float32); acc = np.zeros((OUT, OUT), np.float32)
dies = [(c, r) for r in range(rows) for c in range(cols)]
bad = rng.choice(len(dies), 5, replace=False)
kinds = ["missing", "bridge", "particle", "extra", "break"]
diffs = []
for i, (c, r) in enumerate(dies):
    M = L.copy()
    if i in bad:
        k = kinds[list(bad).index(i)]
        cy, cx = int(rng.integers(40, D - 40)), int(rng.integers(40, D - 40))
        if k == "missing": M[cy - 3:cy + 4, cx - 30:cx + 30] = False
        if k == "bridge": M[cy:cy + 22, cx:cx + 6] = True
        if k == "particle": yy, xx = np.mgrid[-9:10, -9:10]; M[cy - 9:cy + 10, cx - 9:cx + 10] |= (xx ** 2 + yy ** 2 < 75)
        if k == "extra": M[cy:cy + 10, cx:cx + 10] = True
        if k == "break": M[cy - 14:cy + 14, cx:cx + 10] = False
        diffs.append((M ^ L, (c, r), (cy, cx), k))
    X0 = int(x0 + c * (D + gap)); Y0 = int(y0 + r * (D + 70))
    big[Y0:Y0 + D, X0:X0 + D] = M
    if i in bad:
        cy, cx = diffs[-1][2]
        cv.circle(X0 + cx, Y0 + cy, 44, 5.0, 'accent'); cv.circle(X0 + cx, Y0 + cy, 54, 1.6, 'accent')
cv.paint(big, 'ink', 0.85)
DATA["defect_list"] = [{"die": list(cr), "kind": k} for _, cr, _, k in diffs]
# difference strip
ty = y0 + rows * (D + 70) + 60; T = 300; tg = (OUT - 2 * MARGIN - 5 * T) / 4
for j, (Dm, cr, (cy, cx), k) in enumerate(diffs):
    tx = int(MARGIN + j * (T + tg)); sub = np.zeros((D, D), np.float32); sub[Dm] = 1
    sub = ndimage.binary_dilation(sub, iterations=4).astype(np.float32)
    s = ndimage.zoom(sub, T / D, order=0)
    acc[int(ty):int(ty) + s.shape[0], tx:tx + s.shape[1]] = s
    cv.line([(tx, ty), (tx + T, ty), (tx + T, ty + T), (tx, ty + T), (tx, ty)], 1.4)
    cv.circle(tx + cx * T / D, ty + cy * T / D, 30, 2.0, 'accent')
    for q in range(1, 6):
        cv.line([(tx + q * T / 6, ty + T - 6), (tx + q * T / 6, ty + T)], 1.0)
cv.paint(acc, 'accent', 1.0)
cv.plate_number(22)
write_data(22, DATA)
render(cv, 22, 'inspect')
