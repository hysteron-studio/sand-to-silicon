"""06 - The Architecture. A full GH100-class accelerator drawn as a rose-window plan:
8 GPC sectors, 72 TPC spokes, 144 SMs, 576 tensor cores (accent) and 18,432 FP32 lanes
(dots), around a two-partition L2 crossbar, ringed by 12 memory controllers and 6 HBM stacks."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "06 - The Architecture", "seed": SEED,
  "reference_design": "NVIDIA GH100 (full die), as published in the H100 architecture whitepaper",
  "GPC": 8, "TPC_per_GPC": 9, "SM_per_TPC": 2, "SM": 144, "FP32_per_SM": 128, "FP32_total": 18432,
  "tensor_cores_per_SM": 4, "tensor_cores_total": 576, "L2_MB": 60, "L2_partitions": 2,
  "memory_controllers": 12, "memory_controller_bits": 512, "HBM_stacks": 6, "NVLink_links": 18,
  "mapping": {
    "sectors": "8 GPCs = 8 sectors of 45 deg, separated by construction lines",
    "spokes": "9 TPCs per GPC = 72 radial spokes; each spoke carries its 2 SMs as two annular cells",
    "SM cells": "each SM holds 128 FP32 lanes as an 8 x 16 polar dot grid and 4 tensor cores as accent blocks at its outer edge",
    "core": "L2 as a circle split into its two partitions; every SM is wired to it by one crossbar line",
    "outer rings": "12 memory controllers as 12 arc segments (512-bit each = 512 ticks per arc, drawn every 8th), 6 HBM stacks as stacked bars, 18 NVLink ports as small rings on the outermost construction circle",
    "construction": "compass arcs and radial guide lines left visible, like an architect's setting-out",
  },
  "sources": [
    "https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/ (8 GPCs, 72 TPCs, 2 SMs/TPC, 144 SMs, 128 FP32/SM, 4 Tensor Cores/SM = 576, 6 HBM stacks, 12 x 512-bit memory controllers, 60 MB L2, partitioned crossbar)",
    "https://resources.nvidia.com/en-us-hopper-architecture (H100 whitepaper; NVLink 4 with 18 links)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
cx = cy = OUT / 2
r_l2, r_xb0, r_xb1 = 210, 250, 400
r_sm = [(430, 640), (668, 880)]
r_gpc, r_mc0, r_mc1, r_hbm0, r_hbm1 = 905, 950, 1000, 1045, 1160
nS, nT = 8, 9
spokes = nS * nT
dth = 2 * math.pi / spokes
pad = 0.12 * dth
a0 = -math.pi / 2

def P(r, t): return (cx + r * math.cos(t), cy + r * math.sin(t))
def arc(r, t0, t1, n=40): return [P(r, t) for t in np.linspace(t0, t1, n)]

# construction: faint compass circles and guide rays
for r in (r_l2, r_xb1, r_sm[0][0], r_sm[1][1], r_gpc, r_mc1, r_hbm1 + 8):
    cv.line(arc(r, 0, 2 * math.pi, 600), 0.6, val=150)
for g in range(nS):
    t = a0 + g * 2 * math.pi / nS
    cv.seg(*P(60, t), *P(r_hbm1 - 4, t), 1.0, val=200)

# SMs
sm_id = 0; lanes = 0; tcs = 0
for s in range(spokes):
    t0 = a0 + s * dth + pad; t1 = a0 + (s + 1) * dth - pad
    tm = 0.5 * (t0 + t1)
    for (ri, ro) in r_sm:
        cell = arc(ri, t0, t1, 12) + arc(ro - 30, t1, t0, 12)
        cv.line(cell + [cell[0]], 1.3)
        # 128 lanes: 8 across x 16 along
        for i in range(8):
            for j in range(16):
                tt = t0 + (i + 0.5) / 8 * (t1 - t0)
                rr = ri + 8 + (j + 0.5) / 16 * (ro - 30 - ri - 16)
                cv.dot(*P(rr, tt), 1.35); lanes += 1
        # 4 tensor cores at the outer edge (accent)
        for q in range(4):
            ta = t0 + (q + 0.08) / 4 * (t1 - t0); tb = t0 + (q + 0.92) / 4 * (t1 - t0)
            blk = arc(ro - 24, ta, tb, 5) + arc(ro, tb, ta, 5)
            cv.poly(blk, 'accent'); tcs += 1
        # crossbar wire from this SM to L2
        cv.line([P(ri, tm), P(r_xb1, tm + 0.02 * math.sin(s)), P(r_xb0, tm)], 0.7, val=210)
        sm_id += 1
    # TPC spoke centre line between its two SMs
    cv.seg(*P(r_sm[0][1] - 26, tm), *P(r_sm[1][0] + 2, tm), 1.2)
DATA["drawn"] = {"SM": sm_id, "FP32_lanes": lanes, "tensor_cores": tcs}

# crossbar ring: dense radial hatch
for t in np.linspace(0, 2 * math.pi, 720, endpoint=False):
    cv.seg(*P(r_xb0, t), *P(r_xb0 + 22, t), 0.7)
cv.line(arc(r_xb0, 0, 2 * math.pi, 400), 1.6); cv.line(arc(r_xb0 + 22, 0, 2 * math.pi, 400), 1.0)
# L2: two partitions, concentric engraving
for side in (0, 1):
    for r in np.arange(18, r_l2, 9):
        cv.line(arc(r, a0 + math.pi * side + 0.04, a0 + math.pi * (side + 1) - 0.04, 90), 0.8 + 0.6 * (r % 45 < 9))
cv.line(arc(r_l2, 0, 2 * math.pi, 400), 2.4)
cv.seg(*P(r_l2, a0), *P(r_l2, a0 + math.pi), 2.4)

# GPC boundary arcs (heavy) per sector
for g in range(nS):
    ta = a0 + g * 2 * math.pi / nS + 0.012; tb = a0 + (g + 1) * 2 * math.pi / nS - 0.012
    cv.line(arc(r_gpc, ta, tb, 60), 2.6)
    cv.line(arc(r_sm[0][0] - 14, ta, tb, 60), 1.6)
    cv.seg(*P(r_sm[0][0] - 14, ta), *P(r_gpc, ta), 1.6); cv.seg(*P(r_sm[0][0] - 14, tb), *P(r_gpc, tb), 1.6)

# 12 memory controllers, 512 bits each (tick every 8 bits)
for m in range(12):
    ta = a0 + m * 2 * math.pi / 12 + 0.02; tb = a0 + (m + 1) * 2 * math.pi / 12 - 0.02
    cv.line(arc(r_mc0, ta, tb, 60), 1.6); cv.line(arc(r_mc1, ta, tb, 60), 1.6)
    cv.seg(*P(r_mc0, ta), *P(r_mc1, ta), 1.6); cv.seg(*P(r_mc0, tb), *P(r_mc1, tb), 1.6)
    for b in range(0, 512, 8):
        t = ta + (b + 4) / 512 * (tb - ta)
        cv.seg(*P(r_mc0 + 6, t), *P(r_mc1 - 6, t), 0.6)
# 6 HBM stacks, each pairs with two controllers: 8 stacked dies + base die
for hb in range(6):
    tm = a0 + (hb + 0.5) * 2 * math.pi / 6
    half = 0.16
    for lyr in range(9):
        r = r_hbm0 + 8 + lyr * 12.5
        cv.line(arc(r, tm - half, tm + half, 40), 2.4 if lyr == 0 else 1.3)
    cv.seg(*P(r_hbm0, tm - half), *P(r_hbm1, tm - half), 1.8); cv.seg(*P(r_hbm0, tm + half), *P(r_hbm1, tm + half), 1.8)
    # wide interface: accent bundle from stack to its two controllers
    for o in np.linspace(-half * 0.9, half * 0.9, 24):
        cv.seg(*P(r_mc1 + 2, tm + o), *P(r_hbm0 + 2, tm + o), 0.8, 'accent')
# 18 NVLink ports as notches outside
for n in range(18):
    t = a0 + n * 2 * math.pi / 18
    cv.erase_circle(*P(r_hbm1 + 8, t), 9); cv.circle(*P(r_hbm1 + 8, t), 6, 1.8); cv.dot(*P(r_hbm1 + 8, t), 2.0)

cv.plate_number(6)
write_data(6, DATA)
render(cv, 6, 'architecture')
print(DATA["drawn"])
