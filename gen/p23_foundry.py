"""23 - The Foundry. Gate-all-around nanosheet transistors as an isometric city: three
stacked silicon sheets (5 nm thick, 10 nm apart) run through gate walls at a 48 nm contacted
gate pitch, row after row; the gates that wrap every sheet on all four sides are the accent,
the sheets and substrate are ink."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "23 - The Foundry", "title": "The Foundry", "seed": SEED,
  "architecture": "gate-all-around nanosheet (first generation, replacing FinFET)",
  "volume_production": "4Q 2025",
  "contacted_gate_pitch_nm": 48, "gate_length_nm": 14, "sheets": 3, "sheet_thickness_nm": 5,
  "sheet_spacing_nm": 10, "sheet_width_nm": 30, "row_pitch_nm": 70, "gates": 14, "rows": 9,
  "note": "pitch and sheet dimensions are representative published values for 2 nm-class GAA, not a foundry specification",
  "mapping": {
    "projection": "isometric, 2.3 px per nm; painter's order back-to-front",
    "sheets": "thin ink boxes threaded through every gate, side faces hatched",
    "gates": "accent walls, hatched on both visible faces",
  },
  "sources": [
    "https://www.tsmc.com/english/dedicatedFoundry/technology/logic/l_2nm (N2 nanosheet, volume production 4Q25)",
    "https://www.tomshardware.com/tech-industry/semiconductors/tsmc-begins-quietly-volume-production-of-2nm-class-chips-first-gaa-transistor-for-tsmc-claims-up-to-15-percent-improvement-at-iso-power",
  ],
}
cv = Canvas(SEED); rng = cv.rng
s = 2.3; c30 = math.cos(math.radians(30))
G, R = DATA["gates"], DATA["rows"]; cpp, lg = 48, 14; rp, sw = 70, 30
X = G * cpp + 20; Y = R * rp
cx = OUT / 2 + (Y - X) * c30 * s / 2 * 1.0 - 0; cy = 1000
def P(x, y, z): return (cx + (x - y) * c30 * s, cy + (x + y) * 0.5 * s - z * s)
def box(x0, x1, y0, y1, z0, z1, layer, hx=None, hy=None, top_h=None, w=1.6):
    A = P(x0, y1, z1); B = P(x1, y1, z1); C = P(x1, y0, z1); Dd = P(x0, y0, z1)
    E = P(x1, y1, z0); F = P(x1, y0, z0); Gg = P(x0, y1, z0)
    hexa = [Dd, C, F, E, Gg, A]
    cv.erase_poly(hexa)
    yface = [A, B, E, Gg]; xface = [B, C, F, E]; top = [A, B, C, Dd]
    if hy: cv.hatch_poly(yface, hy[0], hy[1], hy[2], layer)
    if hx: cv.hatch_poly(xface, hx[0], hx[1], hx[2], layer)
    if top_h: cv.hatch_poly(top, top_h[0], top_h[1], top_h[2], layer)
    cv.line(hexa + [hexa[0]], w, layer); cv.line([A, B, C], w * 0.8, layer); cv.line([B, E], w * 0.8, layer)
# substrate slab
box(-30, X + 30, -30, Y + 20, -60, -8, 'ink', hx=(90, 7, 0.9), hy=(90, 10, 0.9), w=2.2)
zs = [8, 23, 38]
nb = 0
for i in range(G + 1):
    gx = 10 + i * cpp
    if i < G:
        box(gx, gx + lg, -10, Y, -8, 64, 'accent', hx=(60, 6, 1.0), hy=(90, 9, 1.0), w=1.8); nb += 1
    if i < G:
        for j in range(R):
            yb = j * rp + (rp - sw) / 2
            # fin foot under the stack
            box(gx + lg, gx + cpp, yb, yb + sw, -8, 0, 'ink', hy=(0, 4, 0.8), w=1.1)
            for z in zs:
                box(gx + lg, gx + cpp, yb, yb + sw, z, z + 5, 'ink', hy=(0, 3.2, 0.7), w=1.2); nb += 1
DATA["boxes_drawn"] = nb
cv.plate_number(23)
write_data(23, DATA)
render(cv, 23, 'foundry')
