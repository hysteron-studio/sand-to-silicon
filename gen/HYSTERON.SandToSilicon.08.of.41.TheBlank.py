"""08 - The Blank. A 6025 EUV mask blank (152 x 152 x 6.35 mm low-expansion glass) in
axonometric view, its surface scanned line by line and found clean; the 104 x 132 mm image
field in accent; a loupe opens the front corner to the 40 Mo/Si pairs, Ru cap and absorber."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "08 - The Blank", "seed": SEED,
  "substrate": {"format": "6025 (6 x 6 x 0.25 in)", "size_mm": 152, "thickness_mm": 6.35,
                "material": "low-thermal-expansion SiO2-TiO2 glass, mean CTE within 0 +/- 5 ppb/K", "flatness_nm_PV": "30-50"},
  "multilayer": {"pairs": 40, "period_nm": 7.0, "Mo_nm": 2.8, "Si_nm": 4.2},
  "capping": {"material": "Ru", "nm": 2.5}, "absorber": {"material": "Ta-based (TaBN/TaN)", "nm": 60},
  "image_field_mm": [104, 132], "wafer_field_mm": [26, 33], "reduction": 4,
  "scale": {"plate_px_per_mm": 6.7, "loupe_px_per_nm": 2.6},
  "mapping": {
    "plate": "true proportions of the 152 x 152 x 6.35 mm substrate in 25-degree dimetric projection",
    "scan raster": "a serpentine inspection path at 2 mm pitch (76 passes, every fifth heavier) covering the whole surface, with no defect marked",
    "accent field": "the 104 x 132 mm area that a 4x scanner reduces to one 26 x 33 mm wafer field",
    "loupe": "front corner opened at 2.6 px per nm: glass, 40 Mo (2.8 nm, solid) / Si (4.2 nm, open) pairs, 2.5 nm Ru cap in accent, 60 nm Ta-based absorber cross-hatched",
  },
  "sources": [
    "https://eureka.patsnap.com/patent-US8029950B2 (AGC: 152 mm square, 6.35 mm thick SiO2-TiO2 LTE glass, Mo/Si multilayer, Ru cap, ~60 nm Ta-based absorber)",
    "https://www.agcem.com/products/euv-mask-blanks/ (AGC EUV mask blanks)",
    "https://euvlitho.com/2022/P31.pdf (40 Mo/Si bilayers, 7 nm period, 2.5 nm Ru cap)",
    "https://euvlsymposium.lbl.gov/pdf/2016/Oral/Tue_S2-1.pdf (substrate flatness target 30 nm; CTE 0 +/- 5 ppb/K)",
    "https://www.euvlitho.com/2021/P3.pdf (4x reduction: 26 x 33 mm wafer field = 104 x 132 mm on the 6-inch reticle)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
s = DATA["scale"]["plate_px_per_mm"]; th_ = math.radians(25)
cx, y_top = OUT / 2, 400
Lp, T = 152.0, 6.35
def Pp(x, y, z=0.0):
    return (cx + (x - y) * s * math.cos(th_), y_top + (x + y) * s * math.sin(th_) - z * s + T * s)

# top face raster: one line per mm, parallel to x
# serpentine inspection path, 2 mm pitch, U-turns at the edges
for j in range(76):
    y = 1.0 + 2 * j
    cv.line([Pp(2.0, y, T), Pp(Lp - 2.0, y, T)], 1.25 if j % 5 == 0 else 0.8)
    if j < 75:
        xe = Lp - 2.0 if j % 2 == 0 else 2.0; sgn = 1 if j % 2 == 0 else -1
        arc = [Pp(xe + sgn * 1.0 * math.sin(t), y + 1 - math.cos(t), T) for t in np.linspace(0, math.pi, 12)]
        cv.line(arc, 0.8)
# side faces: front-right (y = 152) and front-left (x = 152) - vertical engraving
for x in np.arange(0.5, Lp, 0.9):
    cv.seg(*Pp(x, Lp, T), *Pp(x, Lp, 0), 0.9)
for y in np.arange(0.5, Lp, 0.6):
    cv.seg(*Pp(Lp, y, T), *Pp(Lp, y, 0), 1.3)
# outline + chamfers
top = [Pp(0, 0, T), Pp(Lp, 0, T), Pp(Lp, Lp, T), Pp(0, Lp, T)]
cv.line(top + [top[0]], 2.4)
cv.line([Pp(Lp, 0, T), Pp(Lp, 0, 0), Pp(Lp, Lp, 0), Pp(0, Lp, 0), Pp(0, Lp, T)], 2.4)
cv.seg(*Pp(Lp, Lp, T), *Pp(Lp, Lp, 0), 2.4)
for c in (0.6,):
    cv.line([Pp(c, c, T), Pp(Lp - c, c, T), Pp(Lp - c, Lp - c, T), Pp(c, Lp - c, T), Pp(c, c, T)], 0.8)

# image field 104 x 132, centred (132 along x)
fw, fh = DATA["image_field_mm"][1], DATA["image_field_mm"][0]
x0, y0 = (Lp - fw) / 2, (Lp - fh) / 2
F = [Pp(x0, y0, T), Pp(x0 + fw, y0, T), Pp(x0 + fw, y0 + fh, T), Pp(x0, y0 + fh, T)]
cv.line(F + [F[0]], 3.2, 'accent')
g = 1.6
G = [Pp(x0 - g, y0 - g, T), Pp(x0 + fw + g, y0 - g, T), Pp(x0 + fw + g, y0 + fh + g, T), Pp(x0 - g, y0 + fh + g, T)]
cv.line(G + [G[0]], 1.6, 'accent')
# 4 x 4 subdivision ticks: the field is the wafer field magnified four times
for i in range(1, 4):
    xa = x0 + fw * i / 4; ya = y0 + fh * i / 4
    cv.line([Pp(xa, y0 - 3, T), Pp(xa, y0 + 2, T)], 1.4, 'accent'); cv.line([Pp(xa, y0 + fh - 2, T), Pp(xa, y0 + fh + 3, T)], 1.4, 'accent')
    cv.line([Pp(x0 - 3, ya, T), Pp(x0 + 2, ya, T)], 1.4, 'accent'); cv.line([Pp(x0 + fw - 2, ya, T), Pp(x0 + fw + 3, ya, T)], 1.4, 'accent')

# ---- loupe on the front corner
corner = Pp(Lp, Lp, T * 0.5)
Lc = (cx, 2080); Rl = 560
cv.line([corner, (Lc[0], Lc[1] - Rl)], 1.2)
cv.circle(*corner, 16, 1.6)
k = DATA["scale"]["loupe_px_per_nm"]
def band(ya, yb, n=40):
    """polygon of the horizontal band [ya, yb] clipped to the loupe circle"""
    cxl, cyl = Lc
    ya, yb = max(ya, cyl - Rl + 0.5), min(yb, cyl + Rl - 0.5)
    if yb <= ya: return None
    ys = np.linspace(ya, yb, n)
    left = [(cxl - math.sqrt(Rl * Rl - (y - cyl) ** 2), y) for y in ys]
    right = [(cxl + math.sqrt(Rl * Rl - (y - cyl) ** 2), y) for y in ys[::-1]]
    return left + right
stack_top = Lc[1] - Rl + 90          # air above the absorber
y = stack_top
ab = band(y, y + 60 * k)
cv.hatch_poly(ab, 45, 9, 1.4); cv.hatch_poly(ab, -45, 9, 1.4)
y += 60 * k
ru = band(y, y + 2.5 * k); cv.poly(ru, 'accent'); y += 2.5 * k
for p in range(40):
    y += 4.2 * k                         # Si: left open
    mo = band(y, y + 2.8 * k)
    if mo:
        wav = [(xx, yy + 0.6 * math.sin(xx / 37 + p)) for xx, yy in mo]
        cv.poly(wav)
    y += 2.8 * k
DATA["loupe_stack_px"] = round(y - stack_top, 1)
sub = band(y + 3, Lc[1] + Rl)
if sub: cv.hatch_poly(sub, 60, 16, 1.0)
# loupe rim
th = np.linspace(0, 2 * math.pi, 600)
cv.line(list(zip(Lc[0] + Rl * np.cos(th), Lc[1] + Rl * np.sin(th))), 3.0)
cv.line(list(zip(Lc[0] + (Rl + 14) * np.cos(th), Lc[1] + (Rl + 14) * np.sin(th))), 1.2)

cv.plate_number(8)
write_data(8, DATA)
render(cv, 8, 'blank')
print(Pp(Lp, Lp, 0), DATA["loupe_stack_px"])
