"""07 - The Blueprint. A reticle-limited die floorplan recursively partitioned through six
levels of design hierarchy; leaves are hatched at real metal pitches; nets are routed in the
channels and the verified ones are inked in the accent."""
import math, heapq, numpy as np
from style import *
# v1 prototype plate II; renumbered to master-sequence #7

SEED = None  # private, not published
DATA = {
  "piece": "07 - The Blueprint", "seed": SEED,
  "die_mm": [26, 33], "die_area_mm2": 858, "die_note": "max single-exposure field of a 0.33-NA EUV scanner (reticle limit)",
  "metal_stack": {"node": "Intel 4 (VLSI 2022)", "layers_total": 18, "regular": 16, "thick_top": 2,
                  "pitch_nm": {"M0": 30, "M1": 50, "M2": 45, "M3": 50, "M4": 45}},
  "hierarchy_levels": ["die", "cluster", "core", "unit", "block", "cell"],
  "mapping": {
    "die outline": "26:33 aspect, 1 mm = 66 px",
    "recursive partition": "slicing floorplan, 6 hierarchy levels; channel width halves per level",
    "hatching": "each leaf is assigned a lower metal layer M0-M4; hatch pitch = pitch_nm x 0.24 px, direction alternates H/V by layer parity (M0/M2/M4 horizontal, M1/M3 vertical)",
    "macros": "leaves drawn as cross-hatched grids = SRAM macros (both directions)",
    "routing": "nets routed by Dijkstra in the channels with a bend penalty (Manhattan)",
    "verified": "nets that pass a deterministic checksum 'sign-off' (3 of 4 on average) are accent; the rest stay ink and dashed = not yet signed off",
    "bumps": "18 concentric seal/pad rings echo the 18-layer metal stack",
  },
  "sources": [
    "https://www.asml.com/en/products/euv-lithography-systems/twinscan-nxe3400c (26 x 33 mm field)",
    "https://www.realworldtech.com/intel-4/3/ (Intel 4: 18 metal layers, M0 30 nm, M1 50, M2 45, M3 50, M4 45)",
    "https://semiwiki.com/semiconductor-manufacturers/intel/314047-intel-4-presented-at-vlsi/",
  ],
}
cv = Canvas(SEED); rng = cv.rng
PX_MM = 66
dw, dh = 26 * PX_MM, 33 * PX_MM
x0, y0 = (OUT - dw) / 2, (OUT - dh) / 2
pitch = DATA["metal_stack"]["pitch_nm"]
layers = list(pitch)

leaves = []
def split(x, y, w, h, depth, cluster, gap):
    if depth == 6 or (depth >= 3 and rng.random() < 0.18 * (depth - 2)) or min(w, h) < 70:
        leaves.append((x, y, w, h, depth, cluster)); return
    vertical = (w > h * 1.15) or (not (h > w * 1.15) and rng.random() < 0.5)
    n = 2 if rng.random() < 0.7 else 3
    cuts = np.sort(rng.uniform(0.28, 0.72, n - 1)) if n == 2 else np.array([rng.uniform(0.25, 0.4), rng.uniform(0.6, 0.75)])
    edges = np.concatenate([[0], cuts, [1]])
    for i in range(n):
        if vertical:
            xa, xb = x + w * edges[i], x + w * edges[i + 1]
            xa += gap / 2 if i > 0 else 0; xb -= gap / 2 if i < n - 1 else 0
            split(xa, y, xb - xa, h, depth + 1, cluster if depth else i, gap * 0.62)
        else:
            ya, yb = y + h * edges[i], y + h * edges[i + 1]
            ya += gap / 2 if i > 0 else 0; yb -= gap / 2 if i < n - 1 else 0
            split(x, ya, w, yb - ya, depth + 1, cluster if depth else i, gap * 0.62)

inset = 140
split(x0 + inset, y0 + inset, dw - 2 * inset, dh - 2 * inset, 0, 0, 110)

# ---- leaves: hatch at metal pitch
occ_res = 6
G = np.zeros((int(OUT / occ_res), int(OUT / occ_res)), bool)   # True = blocked
pins = []
for (x, y, w, h, depth, cl) in leaves:
    pad = 3 + rng.uniform(0, 3)
    xa, ya, xb, yb = x + pad, y + pad, x + w - pad, y + h - pad
    G[int(ya / occ_res):int(yb / occ_res) + 1, int(xa / occ_res):int(xb / occ_res) + 1] = True
    kind = rng.random()
    L = layers[int(rng.integers(0, len(layers)))]
    li = layers.index(L)
    p = pitch[L] * 0.24
    cv.line([(xa, ya), (xb, ya), (xb, yb), (xa, yb), (xa, ya)], 1.8, 'ink')
    if kind < 0.12:   # SRAM macro: cross grid
        for xx in np.arange(xa + p, xb, p * 1.5): cv.seg(xx, ya, xx, yb, 1.0, 'ink', 210)
        for yy in np.arange(ya + p, yb, p * 1.5): cv.seg(xa, yy, xb, yy, 1.0, 'ink', 210)
    elif kind < 0.86:
        horiz = (li % 2 == 0)
        dens = 0.75 + 0.25 * rng.random()
        if horiz:
            for yy in np.arange(ya + p, yb - 1, p):
                if rng.random() < dens:
                    # standard-cell rows: broken tracks
                    xs = np.sort(rng.uniform(xa, xb, int(rng.integers(0, 4)) * 2))
                    seg = [xa + 3] + list(xs) + [xb - 3]
                    for k in range(0, len(seg) - 1, 2): cv.seg(seg[k], yy, seg[k + 1], yy, 1.15, 'ink')
        else:
            for xx in np.arange(xa + p, xb - 1, p):
                if rng.random() < dens:
                    ys = np.sort(rng.uniform(ya, yb, int(rng.integers(0, 4)) * 2))
                    seg = [ya + 3] + list(ys) + [yb - 3]
                    for k in range(0, len(seg) - 1, 2): cv.seg(xx, seg[k], xx, seg[k + 1], 1.15, 'ink')
    # else: empty leaf (filler / whitespace)
    # pins on a random edge, just outside the block
    for _ in range(int(rng.integers(2, 5)) if min(xb - xa, yb - ya) > 30 else 0):
        e = rng.integers(0, 4)
        if e == 0: px, py = rng.uniform(xa + 10, xb - 10), ya - 11
        elif e == 1: px, py = rng.uniform(xa + 10, xb - 10), yb + 11
        elif e == 2: px, py = xa - 11, rng.uniform(ya + 10, yb - 10)
        else: px, py = xb + 11, rng.uniform(ya + 10, yb - 10)
        pins.append((px, py, cl, (xa, ya, xb, yb)))

# blocked outside die interior
H_, W_ = G.shape
Y, X = np.mgrid[0:H_, 0:W_] * occ_res
G = ndimage.binary_dilation(G, iterations=1)
G |= (X < x0 + 30) | (X > x0 + dw - 30) | (Y < y0 + 30) | (Y > y0 + dh - 30)

def route(a, b, used):
    sa = (int(a[1] / occ_res), int(a[0] / occ_res)); sb = (int(b[1] / occ_res), int(b[0] / occ_res))
    for s in (sa, sb):
        if G[s]: return None
    dist = {(sa, -1): 0}; prev = {}
    pq = [(0, sa, -1)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    while pq:
        c, s, dI = heapq.heappop(pq)
        if s == sb: break
        if c > dist.get((s, dI), 1e18): continue
        for k, (dy, dx) in enumerate(dirs):
            t = (s[0] + dy, s[1] + dx)
            if not (0 <= t[0] < H_ and 0 <= t[1] < W_) or G[t]: continue
            nc = c + 1 + (8 if dI not in (-1, k) else 0) + 9 * used[t]
            if nc < dist.get((t, k), 1e18):
                dist[(t, k)] = nc; prev[(t, k)] = (s, dI); heapq.heappush(pq, (nc, t, k))
    else:
        return None
    if s != sb: return None
    path = []; key = (s, dI)
    while key in prev:
        path.append(key[0]); key = prev[key]
    path.append(sa)
    return path[::-1]

used = np.zeros(G.shape, np.int32)
order = rng.permutation(len(pins))
nets = []
for i in range(0, len(order) - 1, 2):
    if len(nets) >= 34: break
    A, B = pins[order[i]], pins[order[i + 1]]
    if math.hypot(A[0] - B[0], A[1] - B[1]) < 350: continue
    if math.hypot(A[0] - B[0], A[1] - B[1]) > 1700: continue
    p = route(A, B, used)
    if p is None or len(p) < 4: continue
    for c in p: used[c] += 1
    # compress to corners
    pts = [p[0]]
    for k in range(1, len(p) - 1):
        if (p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1]) != (p[k + 1][0] - p[k][0], p[k + 1][1] - p[k][1]):
            pts.append(p[k])
    pts.append(p[-1])
    xy = [(q[1] * occ_res + occ_res / 2, q[0] * occ_res + occ_res / 2) for q in pts]
    verified = ((len(p) * 2654435761 + A[2]) % 4 != 0)   # deterministic 'sign-off' check
    nets.append((xy, verified, A, B))

nver = 0
for xy, ver, A, B in nets:
    if ver:
        nver += 1
        cv.line(xy, 4.0, "accent")
        for P in (A, B): cv.dot(xy[0][0], xy[0][1], 5.5, 'accent'); cv.dot(xy[-1][0], xy[-1][1], 5.5, 'accent')
    else:
        # dashed: not yet signed off
        for (xa, ya), (xb, yb) in zip(xy[:-1], xy[1:]):
            L_ = math.hypot(xb - xa, yb - ya); n = max(1, int(L_ / 16))
            for k in range(n):
                if k % 2 == 0:
                    t0, t1 = k / n, min((k + 1) / n, 1)
                    cv.seg(xa + (xb - xa) * t0, ya + (yb - ya) * t0, xa + (xb - xa) * t1, ya + (yb - ya) * t1, 2.0, 'ink')
        cv.circle(xy[0][0], xy[0][1], 6, 2.0); cv.circle(xy[-1][0], xy[-1][1], 6, 2.0)

# ---- die edge: 18 rings, one per metal layer (outer two heavier = thick top metals)
for k in range(18):
    o = 4 + k * 4.6
    w = 2.4 if k < 2 else 0.7
    cv.line([(x0 + o, y0 + o), (x0 + dw - o, y0 + o), (x0 + dw - o, y0 + dh - o), (x0 + o, y0 + dh - o), (x0 + o, y0 + o)], w, 'ink', 85 if k >= 2 else 255)
# corner crosses, like registration marks
for (cxm, cym) in ((x0 - 60, y0 - 60), (x0 + dw + 60, y0 - 60), (x0 - 60, y0 + dh + 60), (x0 + dw + 60, y0 + dh + 60)):
    cv.seg(cxm - 22, cym, cxm + 22, cym, 1.6); cv.seg(cxm, cym - 22, cxm, cym + 22, 1.6)

DATA["counts"] = {"leaves": len(leaves), "nets_routed": len(nets), "nets_verified": nver}
cv.plate_number(7)
write_data(7, DATA)
render(cv, 7, 'blueprint')
print(DATA["counts"])
