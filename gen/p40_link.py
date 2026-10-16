"""40 - The Link. A 64 GT/s PAM4 lane before and after a retimer, as two engraved eye
diagrams: on the left, 360 traces after a channel with 36 dB of loss at Nyquist - the three
eyes nearly shut by smear, jitter and noise; between them a small accent retimer; on the
right, the same symbols re-timed and re-driven, three clean open eyes."""
import math, numpy as np
from scipy import signal
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "40 - The Link", "title": "The Link", "seed": SEED,
  "rate_GTps": 64, "modulation": "PAM4", "baud_GBd": 32, "ui_ps": 31.25, "nyquist_GHz": 16, "loss_compensated_dB": 36,
  "mapping": {
    "symbols": "seeded PAM4 stream (-3, -1, +1, +3), 64 samples per UI",
    "channel": "left: pulse response with ISI from a 36 dB-at-Nyquist channel approximated by a 3-pole low-pass, partially equalised, plus RJ 0.025 UI and noise; right: retimed output, 1-pole edge, RJ 0.01 UI",
    "eyes": "360 two-UI traces per eye, overlaid as engraved strands; left ink, right accent",
    "retimer": "small accent die with pins between the eyes",
  },
  "sources": [
    "https://www.asteralabs.com/news/astera-labs-expands-widely-deployed-field-tested-retimer-portfolio-with-industrys-lowest-power-pcie-6-x-cxl-3-x-solution/ (64 GT/s, 36 dB)",
    "https://www.asteralabs.com/the-long-and-short-of-ai-building-scalable-data-centers-in-the-pcie-6-x-era/ (reach)",
  ],
}
cv = Canvas(SEED); rng = cv.rng
spu = 64; nsym = 3000
sym = rng.choice([-3, -1, 1, 3], nsym).astype(float)
def wave(lp_order, fc, rj, noise, ctle):
    t_edges = np.arange(nsym) * spu + rng.normal(0, rj * spu, nsym)
    n = nsym * spu; x = np.zeros(n)
    idx = np.clip(t_edges.astype(int), 0, n - 1)
    d = np.diff(np.r_[0, sym]); x[idx] += d; x = np.cumsum(x)
    b, a = signal.butter(lp_order, fc / (spu / 2))
    y = signal.lfilter(b, a, x)
    if ctle: y = y + ctle * np.gradient(y) * spu / 3
    y += rng.normal(0, noise, n)
    return y
yL = wave(3, 0.30, 0.025, 0.07, 0.9)
yR = wave(1, 0.9, 0.01, 0.03, 0.0)
def eye(y, ox, oy, w, h, layer, width):
    off = int(spu * 0.5); nt = 0
    for k in range(40, 40 + 360):
        s0 = k * spu + off
        seg = y[s0 - spu: s0 + spu]
        xs = ox + np.linspace(0, w, seg.size); ys = oy + h / 2 - seg / 4.2 * h / 2
        cv.line(list(zip(xs[::2], ys[::2])), width, layer); nt += 1
    return nt
w, h = 960, 1180; yo = (OUT - h) / 2
for ox in (MARGIN, OUT - MARGIN - w):
    cv.line([(ox, yo), (ox + w, yo), (ox + w, yo + h), (ox, yo + h), (ox, yo)], 1.4)
    for k in range(1, 4): cv.seg(ox + k * w / 4, yo, ox + k * w / 4, yo + 14, 1.0); cv.seg(ox + k * w / 4, yo + h - 14, ox + k * w / 4, yo + h, 1.0)
    for k in range(1, 8): cv.seg(ox, yo + k * h / 8, ox + 14, yo + k * h / 8, 1.0); cv.seg(ox + w - 14, yo + k * h / 8, ox + w, yo + k * h / 8, 1.0)
eye(yL, MARGIN, yo, w, h, 'ink', 0.45)
eye(yR, OUT - MARGIN - w, yo, w, h, 'accent', 0.45)
# retimer
cx, cy = OUT / 2, OUT / 2; r = 70
q = [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
cv.poly(q, 'accent'); 
for k in range(-3, 4):
    for s in (-1, 1):
        cv.seg(cx + s * r, cy + k * 18, cx + s * (r + 22), cy + k * 18, 2.2, 'accent')
        cv.seg(cx + k * 18, cy + s * r, cx + k * 18, cy + s * (r + 22), 2.2, 'accent')
cv.seg(MARGIN + w + 20, cy, cx - r - 40, cy, 1.4); cv.seg(cx + r + 40, cy, OUT - MARGIN - w - 20, cy, 1.4)
cv.plate_number(40)
write_data(40, DATA)
render(cv, 40, 'link')
