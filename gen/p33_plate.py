"""33 - The Plate. A single laser-drilled microvia in section, filled by bottom-up
electroplating: accelerator gathers at the floor and suppressor at the rim, so the copper
front rises from the bottom faster than it thickens on the walls - each of 24 growth fronts
an accent U-curve, flattening as it climbs until the via stands flush and void-free."""
import math, numpy as np
from scipy import ndimage
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "33 - The Plate", "title": "The Plate", "seed": SEED,
  "patent": "US 11,946,153 (void-free via filling and copper pillars for SiP / FOWLP / PoP)",
  "via": {"top_um": 80, "bottom_um": 55, "depth_um": 45},
  "fronts": 24, "bottom_to_wall_rate": 2.6, "field_to_wall_rate": 0.25,
  "mapping": {
    "scale": "17 px per um",
    "fronts": "copper at time t = (distance from wall < c t, x0.25 on the suppressed field) OR (height above floor < 2.6 c t); union smoothed (sigma = 30 px) -> nested U-curves",
    "additives": "suppressor dots crowding the field and rim, (accelerator implied by the faster floor rate)",
  },
  "sources": [
    "https://www.unicon.co.jp/english/product/plating/",
    "https://www.freepatentsonline.com/11946153.html",
  ],
}
cv = Canvas(SEED); rng = cv.rng
S = 17.0
tw, bw, dp = 80 * S / 2, 55 * S / 2, 45 * S
cx = OUT / 2; y_top = 1150; y_bot = y_top + dp
xL, xR = MARGIN, OUT - MARGIN; y_base = y_bot + 420
# dielectric with tapered hole
hole = [(cx - tw, y_top), (cx + tw, y_top), (cx + bw, y_bot), (cx - bw, y_bot)]
diel = [(xL, y_top), (cx - tw, y_top), (cx - bw, y_bot), (cx + bw, y_bot), (cx + tw, y_top), (xR, y_top), (xR, y_base), (xL, y_base)]
cv.hatch_poly(diel, 35, 15, 1.0)
cv.line(diel[:6], 2.6); cv.line([(xL, y_base), (xR, y_base)], 1.6)
# landing pad (copper below)
pad = [(cx - tw - 200, y_bot), (cx + tw + 200, y_bot), (cx + tw + 200, y_bot + 120), (cx - tw - 200, y_bot + 120)]
cv.erase_poly(pad); cv.hatch_poly(pad, -45, 4, 1.0); cv.line(pad + [pad[0]], 1.8)
# growth field on a coarse grid
g = 2; H, Wd = OUT // g, OUT // g
yy, xx = np.mgrid[0:H, 0:Wd] * g
inside = np.zeros((H, Wd), bool)
for r in range(int(y_top / g), int(y_bot / g)):
    y = r * g; t = (y - y_top) / dp; half = tw + (bw - tw) * t
    inside[r, int((cx - half) / g):int((cx + half) / g)] = True
open_field = inside | (yy < y_top)
Dw = ndimage.distance_transform_edt(open_field) * g          # distance from any solid wall/floor
hfl = y_bot - yy
win = (yy > y_top - 260) & (np.abs(xx - cx) < tw + 520)
for k in range(1, DATA["fronts"] + 1):
    c = k * 3.4
    wall = np.where(yy < y_top - 4, 0.25, 1.0)
    filled = ((Dw < c * wall) | (hfl < DATA["bottom_to_wall_rate"] * c * 3.2)) & open_field
    sm = ndimage.gaussian_filter(filled.astype(np.float32), 30 / g)
    sm = np.where(win, sm, 0)
    for line in contours(sm, 0.5, g, g):
        if len(line) > 20:
            cv.line(line, 3.2 if k % 6 == 0 else 1.8, 'accent')
# final flush top line (overburden after fill)
# additives: suppressor on the field/rim, accelerator on the front
for _ in range(500):
    x = rng.uniform(cx - tw - 500, cx + tw + 500); y = y_top - rng.uniform(80, 240)
    cv.dot(x, y, 2.0)
cv.plate_number(33)
write_data(33, DATA)
render(cv, 33, 'plate')
