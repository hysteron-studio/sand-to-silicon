"""24 - The Probe. Wafer sort seen from above: a 300 mm wafer of 10 x 8 mm dies, most already
probed (failures inked with a dot, as on plate 26), and the current touchdown - sixteen dies at
once - reached by a sunburst of probe needles from the card's ring: one engraved needle per
25 of the 50,000 contacts."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "24 - The Probe", "title": "The Probe", "seed": SEED,
  "contacts_max": 50000, "contact_force_kg_max": 400, "needles_drawn_per_contact": 1 / 25,
  "wafer_mm": 300, "die_mm": [10, 8], "dies_per_touchdown": 16, "yield_assumed": 0.86,
  "mapping": {
    "wafer": "300 mm circle with 3 mm edge exclusion; full dies only",
    "sort": "dies before the touchdown are probed; each fails with p = 0.14 (seeded) and is inked",
    "needles": "2,000 needles (50,000 / 25) from the probe-card ring to the pad rows on the perimeters of the 4 x 4 touchdown, in accent",
  },
  "sources": [
    "https://www3.advantest.com/documents/11348/82944f90-4e57-4e2a-bf24-ec8d55e522a4 (up to 50,000 contacts, up to 400 kg)",
    "https://www.advantest.com/en/products/semiconductor-test-system/soc/v93000/",
  ],
}
cv = Canvas(SEED); rng = cv.rng
C = OUT / 2; R = (OUT - 2 * MARGIN) / 2 - 10; s = R / 150.0
cv.circle(C, C, R, 3.0); cv.circle(C, C, R - 3 * s, 0.8)
# notch
cv.erase_circle(C, C + R, 14); cv.line([(C + 14 * math.cos(a), C + R + 14 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 20)], 2.0)
dw, dh = 10 * s, 8 * s
dies = []
for j in range(-20, 21):
    for i in range(-16, 17):
        x0, y0 = C + i * dw - dw / 2 + dw / 2, C + j * dh
        cs = [(x0, y0), (x0 + dw, y0), (x0, y0 + dh), (x0 + dw, y0 + dh)]
        if all(math.hypot(x - C, y - C) < R - 3 * s for x, y in cs): dies.append((x0, y0, i, j))
order = sorted(dies, key=lambda d: (d[3], d[2] if d[3] % 2 == 0 else -d[2]))
TD = [(i, j) for i in (-1, 0, 1, 2) for j in (-1, 0, 1, 2)]
td = [d for d in order if (d[2], d[3]) in TD]
k_td = order.index(td[0]); fails = 0
for k, (x0, y0, i, j) in enumerate(order):
    cv.line([(x0, y0), (x0 + dw, y0), (x0 + dw, y0 + dh), (x0, y0 + dh), (x0, y0)], 1.4)
    if k < k_td and (i, j) not in TD:
        for m in range(1, 5): cv.seg(x0 + 5, y0 + m * dh / 5, x0 + dw - 5, y0 + m * dh / 5, 0.45)
        if rng.random() < 0.14: cv.dot(x0 + dw / 2, y0 + dh / 2, dh * 0.24); fails += 1
DATA["gross_dies"] = len(dies); DATA["probed_before_touchdown"] = k_td; DATA["inked_failures"] = fails
# touchdown block
bx0 = min(d[0] for d in td); by0 = min(d[1] for d in td); bx1 = bx0 + 4 * dw; by1 = by0 + 4 * dh
cv.erase_poly([(bx0 - 4, by0 - 4), (bx1 + 4, by0 - 4), (bx1 + 4, by1 + 4), (bx0 - 4, by1 + 4)])
for x0, y0, i, j in td:
    cv.line([(x0, y0), (x0 + dw, y0), (x0 + dw, y0 + dh), (x0, y0 + dh), (x0, y0)], 2.0)
# probe card ring and needles
cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2; Rr = 600
cv.circle(cx, cy, Rr, 2.4); cv.circle(cx, cy, Rr + 22, 1.2)
needles = 2000
for n in range(needles):
    x0, y0, i, j = td[n % 16]
    side = (n // 16) % 4; t = rng.uniform(0.06, 0.94)
    px = x0 + (t * dw if side in (0, 2) else (3 if side == 3 else dw - 3)); py = y0 + (t * dh if side in (1, 3) else (3 if side == 0 else dh - 3))
    a = math.atan2(py - cy, px - cx) + rng.normal(0, 0.05)
    qx, qy = cx + Rr * math.cos(a), cy + Rr * math.sin(a)
    cv.seg(qx, qy, px, py, 0.5, 'accent')
    cv.dot(px, py, 1.2, 'accent')
DATA["needles_drawn"] = needles
cv.plate_number(24)
write_data(24, DATA)
render(cv, 24, 'probe')
