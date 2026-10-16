"""29 - The Stack. Sixteen thinned DRAM dies above a base die, drawn exploded in axonometric;
a central curtain of 2048 TSVs (HBM4 interface width, 32 channels x 64) pierces every level."""
import math, numpy as np
from style import *
# v1 prototype plate V; renumbered to master-sequence #29

SEED = None  # private, not published
DATA = {
  "piece": "29 - The Stack", "seed": SEED,
  "standard": "JEDEC JESD270-4 HBM4", "interface_bits": 2048, "channels": 32, "bits_per_channel": 64,
  "pseudo_channels_per_channel": 2, "stack_heights_allowed": [4, 8, 12, 16], "dram_dies": 16, "base_die": 1,
  "hbm3_interface_bits": 1024, "hbm3e_12high_note": "SK hynix 12-high HBM3E: dies 40% thinner than 8-high, same package height",
  "die_thickness_um_drawn": 30, "die_thickness_note": "~30 um order (wafer thinning to 30 um, plate IV); exact HBM die thickness not public",
  "mapping": {
    "levels": "16 DRAM slabs + 1 base die, axonometric, exploded so the vertical interconnect is visible",
    "TSV curtain": "2048 data TSVs on the die spine: 32 channel bundles x 64 TSVs (8 x 8), drawn as accent hairlines in every gap",
    "pseudo-channels": "each bundle split into two 8x4 halves by a small gap (2 pseudo-channels)",
    "die faces": "DRAM bank grid (4 x 4 banks per quadrant) hatched on each top face; side faces horizontal hatching",
    "base die": "slab ~2x thicker; beneath it 2048 ink ticks in 32 groups = the interface",
    "section": "the stack is cut along one TSV row (plane through the bundle centres): section faces carry 45-degree hatching, cut TSVs are copper columns in accent; all TSVs behind the plane show as hairlines in every gap",
  },
  "sources": [
    "https://www.businesswire.com/news/home/20250416843598/en/ (JEDEC JESD270-4 HBM4: 2048-bit, 32 channels, 4/8/12/16-high)",
    "https://en.wikipedia.org/wiki/High_Bandwidth_Memory (HBM3 1024-bit, 16 channels)",
    "https://news.skhynix.com/en/sk-hynix-begins-volume-production-of-the-world-first-12-layer-hbm3e/ (12-high HBM3E, TSV, dies 40% thinner)",
    "Manufacturable 300mm Wafer Thinning for 3D Interconnect Applications, MRS Proc. (30 um)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
X0, X1 = 760.0, 2240.0           # die width in elevation
YB = 2480.0                      # bottom of base die
SLAB, GAP, BASE = 90.0, 24.0, 140.0
levels = [('base', YB - BASE, YB)]
y = YB - BASE
for k in range(16):
    y -= GAP
    levels.append((f'dram{k+1}', y - SLAB, y)); y -= SLAB
# warpage: each die bows a little (smile / cry), the bonding has to absorb it
bow = [0.0] + list(rng.normal(0, 11.0, 16))
def by(x, k):
    t = (x - (X0 + X1) / 2) / ((X1 - X0) / 2)
    return bow[k] * (1 - t * t)

# real HBM dies put the TSV field in a central spine: 32 bundles in 4 groups of 8
bp, gg = 15.0, 22.0
tot = 31 * bp + 3 * gg
bund_x = [(X0 + X1) / 2 - tot / 2 + ch * bp + (ch // 8) * gg for ch in range(32)]
cols = [bx + (i - 3.5) * 1.6 for bx in bund_x for i in range(8)]   # 8 visible columns per bundle (8 deep behind)

xs = np.linspace(X0, X1, 300)
for k, (name, ytop, ybot) in enumerate(levels):
    h = ybot - ytop
    # horizontal hatching: silicon slab
    step = 3.6 if name != 'base' else 3.0
    for yy in np.arange(ytop + 1.5, ybot - 1, step):
        cv.line([(x, yy + by(x, k)) for x in xs], 1.0, 'ink', 215)
    cv.line([(x, ytop + by(x, k)) for x in xs], 2.0, 'ink')
    cv.line([(x, ybot + by(x, k)) for x in xs], 2.0, 'ink')
    cv.seg(X0, ytop + by(X0, k), X0, ybot + by(X0, k), 2.0); cv.seg(X1, ytop + by(X1, k), X1, ybot + by(X1, k), 2.0)
    # TSVs through the slab (base die is routed, TSVs land on it)
    for cx_ in cols:
        if name == 'base':
            cv.seg(cx_, ytop + by(cx_, k), cx_, ytop + 22 + by(cx_, k), 1.4, 'accent')
        else:
            # erase hatch under the copper column, then draw copper
            ImageDraw.Draw(cv.layers['ink']).line([(cx_ * SS, (ytop + by(cx_, k) + 2) * SS), (cx_ * SS, (ybot + by(cx_, k) - 2) * SS)], fill=0, width=int(2.2 * SS))
            cv.seg(cx_, ytop + by(cx_, k), cx_, ybot + by(cx_, k), 1.0, 'accent', 205)
    # the gap above this die: micro-bump columns joining it to the next
    if k < len(levels) - 1:
        yu = levels[k + 1][2]
        for cx_ in cols:
            y_low = ytop + by(cx_, k); y_up = yu + by(cx_, k + 1)
            cv.seg(cx_, y_up, cx_, y_low, 1.0, 'accent', 255)
        for bx in bund_x:
            for i in range(0, 8):
                x_ = bx + (i - 3.5) * 2.4
            # bump caps as small ink ticks at both ends of each bundle
            cv.seg(bx - 6, ytop + by(bx, k) - 3, bx + 6, ytop + by(bx, k) - 3, 2.4, 'ink')
            cv.seg(bx - 6, yu + by(bx, k + 1) + 3, bx + 6, yu + by(bx, k + 1) + 3, 2.4, 'ink')

# the interface: 2048 ticks under the base die, 32 groups of 64
for i in range(2048):
    ch, b = divmod(i, 64)
    x = X0 + 10 + (X1 - X0 - 20) * (i + ch * 6) / (2047 + 31 * 6)
    L = 30 if b in (0, 63) else 16
    cv.seg(x, YB + 10, x, YB + 10 + L, 0.55, 'ink', 230)

DATA["mapping"] = {
  "levels": "elevation of 16 DRAM slabs + 1 base die (base drawn ~2x thicker); vertical scale exaggerated so the bonds are visible",
  "warpage": "each DRAM die bows by N(0, 11 px) (exaggerated) from the seed - the warpage the bonding must absorb",
  "TSVs": "2048 data TSVs = 32 channel bundles x 64 (8 across x 8 deep), placed in a central spine (4 groups of 8 bundles); each bundle drawn as 8 accent columns piercing every slab and gap",
  "bumps": "ink caps at each die interface on every bundle",
  "interface": "2048 ink ticks under the base die in 32 groups of 64 (HBM4 2048-bit)",
}
cv.plate_number(29)
write_data(29, DATA)
render(cv, 29, 'stack')
