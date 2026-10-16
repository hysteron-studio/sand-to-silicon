"""27 - The Temporary Bond. The edge of a debonding stack, magnified 580 times: a 50 um device
wafer, face down in adhesive on a 700 um glass carrier, is released by a 308 nm excimer line
beam fired up through the glass; behind the scanning beam the release layer is spent, and
the thin wafer lifts free and curls away."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "27 - The Temporary Bond", "title": "The Temporary Bond", "seed": SEED,
  "laser_nm": 308, "wafer_um": 50, "carrier_um": 700, "adhesive_um": 20, "release_layer_um": 0.5, "wafer_sizes_mm": [200, 300],
  "mapping": {
    "scale": "0.58 px per um, about 4 mm of the edge; all thicknesses drawn to that scale (release layer exaggerated to a line)",
    "carrier": "glass with sparse engraved reflections",
    "laser": "a vertical bundle of accent rays rising through the glass at the scan position; pulses already fired are accent ticks along the bond line, one per 0.1 mm",
    "release": "left of the beam the wafer separates; the gap grows and the free end rises on a parabola (a stiff sheet peeled from one edge)",
  },
  "sources": [
    "https://www.suss.com/en/products-solutions/bonding-solutions/temporary-bonding/xbc300-gen2 (308 nm laser debond, wafers <=50 um, 200/300 mm)",
    "https://www.suss.com/en/products-solutions/bonding-solutions/temporary-bonding",
  ],
}
cv = Canvas(SEED); rng = cv.rng
s = 0.58
xL, xR = MARGIN, OUT - MARGIN
y_bond = 1760
car = DATA["carrier_um"] * s; adh = DATA["adhesive_um"] * s; waf = DATA["wafer_um"] * s
# carrier (below bond line)
cv.line([(xL, y_bond), (xR, y_bond)], 2.2)
cv.line([(xL, y_bond + car), (xR, y_bond + car)], 2.6)
for k in range(60):
    x = rng.uniform(xL, xR - 200); L = rng.uniform(60, 260)
    yy = rng.uniform(y_bond + 40, y_bond + car - 40)
    cv.seg(x, yy, x + L, yy - L * 0.18, 0.6)
for x in np.arange(xL, xR, 9): cv.seg(x, y_bond + car, x - 20, y_bond + car + 20, 0.6)   # cut texture under
# release layer and adhesive
x_scan = xL + 0.58 * (xR - xL)
cv.line([(x_scan, y_bond - 2), (xR, y_bond - 2)], 2.4, 'accent')
cv.hatch_poly([(x_scan, y_bond - 3), (xR, y_bond - 3), (xR, y_bond - 3 - adh), (x_scan, y_bond - 3 - adh)], 0, 3.0, 0.8)
# bonded wafer to the right
yw = y_bond - 3 - adh
cv.line([(x_scan, yw), (xR, yw)], 1.8); cv.line([(x_scan, yw - waf), (xR, yw - waf)], 1.8)
cv.hatch_poly([(x_scan, yw), (xR, yw), (xR, yw - waf), (x_scan, yw - waf)], -45, 7, 0.8)
# laser bundle
for k in range(70):
    x = x_scan + rng.uniform(-18, 18)
    cv.seg(x, y_bond + car + 150 - rng.uniform(0, 90), x, y_bond, 0.9, 'accent')
# fired pulses: ticks along the bond line on the released side
pulses = 0
for x in np.arange(x_scan - 0.1 * 1000 * s, xL, -0.1 * 1000 * s):
    cv.seg(x, y_bond - 8, x, y_bond + 8, 1.6, 'accent'); cv.dot(x, y_bond, 2.6, 'accent'); pulses += 1
DATA["pulse_ticks"] = pulses
# released wafer: lifts from the scan point and rises to the left
xs = np.linspace(x_scan, xL, 500)
d = x_scan - xs
lift = np.where(d < 70, 0, 0.00052 * np.clip(d - 70, 0, None) ** 2)
mid = list(zip(xs, yw - lift))
ang = np.arctan(np.gradient(-lift, -d + 1e-9))
low = mid; up = [(x - math.sin(t) * waf * 0, y - waf) for (x, y), t in zip(mid, ang)]
cv.line(low, 1.8); cv.line(up, 1.8)
cv.hatch_poly(low + up[::-1], -45, 7, 0.8)
# devices: bumps on the wafer underside, embedded in adhesive on the bonded side, free on the lifted side
for x in np.arange(xL + 20, xR - 10, 46):
    yb = np.interp(x, xs[::-1], (yw - lift)[::-1]) if x < x_scan else yw
    cv.line([(x - 10 + 20 * t, yb + 10 * math.sin(math.pi * t)) for t in np.linspace(0, 1, 10)], 1.4)
# adhesive residue on the lifted underside
for (x, y) in mid[::4]:
    if x > xL: cv.dot(x + rng.normal(0, 3), y + rng.uniform(2, 12), 1.3)
for x in np.arange(xL, x_scan - 10, 16):
    cv.seg(x, y_bond - 2, x + 6, y_bond - 2, 1.2, 'accent')
cv.plate_number(27)
write_data(27, DATA)
render(cv, 27, 'tempbond')
