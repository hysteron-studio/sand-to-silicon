"""41 - The Intelligence. A tiny frozen transformer reads 'from matter to mind'. Its four causal
attention maps are blended into a flow field; streamlines live only below the diagonal, because
a token may attend only to what came before it."""
import math, hashlib, numpy as np
from style import *
# v1 prototype plate VI; renumbered to master-sequence #41
from scipy import ndimage

SEED = None  # private, not published
TEXT = "from matter to mind"
D_MODEL, HEADS = 16, 4
DK = D_MODEL // HEADS

wr = np.random.default_rng(SEED)
vocab = sorted(set(TEXT))
tok = np.array([vocab.index(c) for c in TEXT]); n = len(tok)
E = wr.normal(0, 1, (len(vocab), D_MODEL))
pos = np.arange(n)[:, None]; i2 = np.arange(D_MODEL // 2)[None, :]
PE = np.zeros((n, D_MODEL)); PE[:, 0::2] = np.sin(pos / 10000 ** (2 * i2 / D_MODEL)); PE[:, 1::2] = np.cos(pos / 10000 ** (2 * i2 / D_MODEL))
X = E[tok] + PE
X = (X - X.mean(1, keepdims=True)) / (X.std(1, keepdims=True) + 1e-6)   # layer norm
Wq = wr.normal(0, 1 / math.sqrt(D_MODEL), (HEADS, D_MODEL, DK))
Wk = wr.normal(0, 1 / math.sqrt(D_MODEL), (HEADS, D_MODEL, DK))
mask = np.triu(np.ones((n, n), bool), 1)
A = np.zeros((HEADS, n, n))
for h in range(HEADS):
    S = (X @ Wq[h]) @ (X @ Wk[h]).T / math.sqrt(DK) * 2.0   # temperature 0.5 sharpens the frozen maps
    S[mask] = -1e9
    S = S - S.max(1, keepdims=True)
    A[h] = np.exp(S) / np.exp(S).sum(1, keepdims=True)

DATA = {
  "piece": "41 - The Intelligence", "seed": SEED, "text": TEXT, "tokens": list(TEXT), "n_tokens": n,
  "model": {"type": "single attention layer, causal", "d_model": D_MODEL, "heads": HEADS, "d_k": DK,
            "embedding": "seeded N(0,1), char-level vocab of %d" % len(vocab), "positional": "sinusoidal (Vaswani et al. 2017)",
            "attention": "softmax(Q K^T / sqrt(d_k) * 2) with causal mask", "trainable": False},
  "attention_argmax_per_head": {f"h{h}": [int(j) for j in A[h].argmax(1)] for h in range(HEADS)},
  "attention_rounded": {f"h{h}": np.round(A[h], 3).tolist() for h in range(HEADS)},
  "mapping": {
    "square": "query position i runs down, key position j runs across (19 x 19); the upper triangle (future tokens) is masked and stays blank paper",
    "flow angle": "theta = 2*pi*(A0 - A1) + pi*(A2 - A3) + pi/4, bicubic-interpolated over the triangle",
    "line weight": "proportional to total attention mass at the point (sum over heads)",
    "accent": "streamlines that begin in a cell where some head puts > 55% of its attention (its argmax key for that query; row 0 excluded since it can only see itself)",
    "ticks": "19 ticks on the left and bottom edges at token positions; spaces drawn as gaps",
    "frozen": "weights are seeded and never updated - the drawing is one forward pass, inference not training",
  },
  "sources": [
    "Vaswani et al., 'Attention Is All You Need' (2017), arXiv:1706.03762 - scaled dot-product attention, sinusoidal positions, causal masking in the decoder",
    "Blueprint section C.6: training adjusts weights; once frozen, inference reuses them",
  ],
}

cv = Canvas(SEED); rng = cv.rng
L0 = MARGIN + 40; S_ = OUT - 2 * L0
cell = S_ / n
# smooth fields over the square
up = lambda M: ndimage.zoom(M, (S_ / 4) / n, order=3)
Af = np.stack([up(A[h]) for h in range(HEADS)])
res = Af.shape[1]
theta_f = 2 * math.pi * (Af[0] - Af[1]) + math.pi * (Af[2] - Af[3]) + math.pi / 4
mass_f = np.clip(Af.sum(0), 0, None)
Af = np.clip(Af, 0, None)

def sample(F, x, y):
    u = (x - L0) / S_ * (res - 1); v = (y - L0) / S_ * (res - 1)
    return ndimage.map_coordinates(F, [[v], [u]], order=1)[0]

def inside(x, y):
    # lower-left triangle incl. the diagonal cells (j <= i)
    return L0 <= x <= L0 + S_ and L0 <= y <= L0 + S_ and (x - L0) <= (y - L0) + cell * 0.5

occ_r = 7.0
occ = np.zeros((int(OUT / occ_r) + 1, int(OUT / occ_r) + 1), bool)
argcells = set((i, int(A[h, i].argmax())) for h in range(HEADS) for i in range(n) if A[h, i].max() > 0.55 and i > 0)

starts = [(L0 + (gx + rng.random()) * 18, L0 + (gy + rng.random()) * 18) for gx in range(int(S_ / 18)) for gy in range(int(S_ / 18))]
rng.shuffle(starts)
nlines = 0
for (sx, sy) in starts:
    if not inside(sx, sy) or occ[int(sy / occ_r), int(sx / occ_r)]: continue
    trace = {}
    for direction in (1, -1):
        x, y = sx, sy; pts_ = []
        for step in range(400):
            th = sample(theta_f, x, y)
            x += direction * 3.5 * math.cos(th); y += direction * 3.5 * math.sin(th)
            if not inside(x, y): break
            if occ[int(y / occ_r), int(x / occ_r)] and step > 1: break
            pts_.append((x, y))
        trace[direction] = pts_
    pts = trace[-1][::-1] + [(sx, sy)] + trace[1]
    if len(pts) < 8: continue
    for (x, y) in pts:
        occ[int(y / occ_r), int(x / occ_r)] = True
    m = sample(mass_f, sx, sy)
    w = 1.2 + 4.5 * min(m / 1.2, 1.0) ** 1.3
    i = min(int((sy - L0) / cell), n - 1); j = min(int((sx - L0) / cell), n - 1)
    layer = 'accent' if (i, j) in argcells else 'ink'
    cv.line(pts, w, layer)
    nlines += 1

# causal boundary and frame ticks
cv.seg(L0, L0, L0 + S_, L0 + S_, 1.2, 'ink', 200)
for k in range(n):
    if TEXT[k] == ' ': continue
    t = L0 + (k + 0.5) * cell
    cv.seg(L0 - 34, t, L0 - 14, t, 2.0)            # queries
    cv.seg(t, L0 + S_ + 14, t, L0 + S_ + 34, 2.0)  # keys
DATA["counts"] = {"streamlines": nlines, "accent_cells": len(argcells)}
cv.plate_number(41)
write_data(41, DATA)
render(cv, 41, 'intelligence')
print(DATA["counts"])
