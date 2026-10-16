"""Shared visual system for 'Sand to Silicon - From Matter to Mind'.

Ground: warm unbleached paper. Ink: warm sepia-black. One accent per plate that
travels across 41 plates from the heat of matter (vermilion) to the cool of the mind (ultramarine).
All marks are rasterised supersampled, then given ink bleed, dry-brush break-up and
paper grain with numpy. No AI, no external images.
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

OUT = 3000          # final size
SS = 2              # supersampling factor
W = OUT * SS
MARGIN = int(0.11 * OUT)  # print margin (final px)

PAPER = np.array([238, 231, 216], np.float32)   # warm unbleached paper
INK = np.array([30, 27, 24], np.float32)        # sepia-black ink
# ---- the travelling accent: a 41-step journey from heat/matter to mind -----------------
# Anchors (plate: sRGB). The six approved prototypes keep their exact v1 colours at their
# master-sequence positions; everything between is interpolated in CIE L*a*b*.
ANCHORS = {
    1: (150, 40, 38),     # oxide crimson  - raw ore, iron-stained quartz
    4: (184, 52, 32),     # vermilion      - silicon melt, 1414 C       (v1 plate I)
    7: (196, 104, 34),    # burnt orange   - the engineer's red pencil  (v1 plate II)
    13: (176, 138, 36),   # ochre          - tin plasma light            (v1 plate III)
    26: (104, 120, 64),   # oxidised olive - the ground surface          (v1 plate IV)
    29: (42, 108, 112),   # deep teal      - the vertical memory         (v1 plate V)
    41: (30, 50, 120),    # ultramarine    - the frozen mind             (v1 plate VI)
}


def _srgb2lab(c):
    c = np.asarray(c, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def _lab2srgb(lab):
    L, a, b = lab
    fy = (L + 16) / 116; fx = fy + a / 500; fz = fy - b / 200
    f = np.array([fx, fy, fz])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * np.array([0.95047, 1.0, 1.08883])
    Mi = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    c = np.clip(Mi @ xyz, 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return tuple(int(round(v * 255)) for v in c)


def _palette():
    ks = sorted(ANCHORS)
    out = {}
    for n in range(1, 42):
        if n in ANCHORS:
            out[n] = tuple(ANCHORS[n]); continue
        k0 = max(k for k in ks if k < n); k1 = min(k for k in ks if k > n)
        t = (n - k0) / (k1 - k0)
        out[n] = _lab2srgb((1 - t) * _srgb2lab(ANCHORS[k0]) + t * _srgb2lab(ANCHORS[k1]))
    return out


ACCENTS = _palette()   # ACCENTS[n] for master-sequence plate n = 1..41
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Canvas:
    """Two supersampled masks: 'ink' and 'accent' (0..255)."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.layers = {k: Image.new('L', (W, W), 0) for k in ('ink', 'accent')}
        self.d = {k: ImageDraw.Draw(v) for k, v in self.layers.items()}

    # coordinates are in final-pixel units (0..3000)
    def line(self, pts, width=2.0, layer='ink', val=255, jitter=0.0):
        if len(pts) < 2:
            return
        p = np.asarray(pts, np.float64) * SS
        if jitter:
            p = p + self.rng.normal(0, jitter * SS, p.shape)
        w = max(1, int(round(width * SS)))
        self.d[layer].line([tuple(q) for q in p], fill=int(val), width=w, joint='curve' if w > 3 else None)

    def seg(self, x0, y0, x1, y1, width=2.0, layer='ink', val=255):
        w = max(1, int(round(width * SS)))
        self.d[layer].line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=int(val), width=w)

    def dot(self, x, y, r, layer='ink', val=255):
        r *= SS; x *= SS; y *= SS
        self.d[layer].ellipse([x - r, y - r, x + r, y + r], fill=int(val))

    def circle(self, x, y, r, width=2.0, layer='ink', val=255):
        w = max(1, int(round(width * SS)))
        r *= SS; x *= SS; y *= SS
        self.d[layer].ellipse([x - r, y - r, x + r, y + r], outline=int(val), width=w)

    def poly(self, pts, layer='ink', val=255):
        self.d[layer].polygon([(x * SS, y * SS) for x, y in pts], fill=int(val))

    def stipple(self, xs, ys, r=1.0, layer='ink', val=255):
        for x, y in zip(xs, ys):
            self.dot(x, y, r, layer, val)

    def plate_number(self, n, layer='ink'):
        """Master-sequence number (1-41) in small engraved arabic numerals, bottom-right
        inside the margin. Glyphs are stroked polylines, no font."""
        h = 34; wd = 0.58 * h; gap = 0.36 * h
        digits = str(int(n))
        x = OUT - MARGIN - (len(digits) * wd + (len(digits) - 1) * gap)
        y = OUT - MARGIN * 0.48 - h / 2           # top of glyph box (baseline at y+h)
        for ch in digits:
            for stroke in _digit_strokes(ch):
                self.line([(x + u * wd, y + v * h) for u, v in stroke], 2.6, layer)
            x += wd + gap


    # ---- helpers added for the 41-plate build (v2) -------------------------------------
    def hatch_poly(self, poly, angle=45.0, spacing=8.0, width=1.2, layer='ink', val=255, jitter=0.0, wfun=None):
        """Parallel engraving hatch clipped to a (possibly concave) polygon, even-odd rule.
        wfun(x, y) -> width multiplier lets tone vary along a line."""
        P = np.asarray(poly, np.float64)
        a = math.radians(angle); d = np.array([math.cos(a), math.sin(a)]); nrm = np.array([-d[1], d[0]])
        proj = P @ nrm
        E = list(zip(P, np.roll(P, -1, 0)))
        for off in np.arange(proj.min() + spacing / 2, proj.max(), spacing):
            ts = []
            for p0, p1 in E:
                s0, s1 = p0 @ nrm - off, p1 @ nrm - off
                if (s0 > 0) == (s1 > 0) or s0 == s1: continue
                q = p0 + (p1 - p0) * (s0 / (s0 - s1))
                ts.append(q @ d)
            ts.sort()
            for t0, t1 in zip(ts[0::2], ts[1::2]):
                p0 = off * nrm + t0 * d; p1 = off * nrm + t1 * d
                if wfun is None:
                    self.line([tuple(p0), tuple(p1)], width, layer, val, jitter)
                else:
                    n = max(2, int((t1 - t0) / 6))
                    pts = [p0 + (p1 - p0) * k / n for k in range(n + 1)]
                    for q0, q1 in zip(pts[:-1], pts[1:]):
                        w = width * float(wfun(*(0.5 * (q0 + q1))))
                        if w > 0.25: self.seg(q0[0], q0[1], q1[0], q1[1], w, layer, val)

    def erase_poly(self, pts):
        for d in self.d.values():
            d.polygon([(x * SS, y * SS) for x, y in pts], fill=0)

    def erase_circle(self, x, y, r):
        for d in self.d.values():
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=0)

    def paint(self, arr, layer='ink', scale=1.0):
        """Max-composite a float [0,1] array (any size, resampled to the canvas) into a layer."""
        a = np.clip(np.asarray(arr, np.float32) * scale, 0, 1)
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((W, W), Image.BILINEAR)
        cur = np.asarray(self.layers[layer], np.uint8)
        self.layers[layer] = Image.fromarray(np.maximum(cur, np.asarray(im)))
        self.d[layer] = ImageDraw.Draw(self.layers[layer])

    def sphere(self, x, y, r, layer='ink', light=(-0.55, -0.65), spacing=None, wmax=None, outline=2.2):
        """Engraved ball: erase what is behind, outline, then hatching whose weight follows Lambert shade."""
        self.erase_circle(x, y, r + 1.5)
        self.circle(x, y, r, outline, layer)
        sp = spacing or max(3.2, r / 9.0); wm = wmax or min(sp * 0.62, 3.2)
        L = np.array([light[0], light[1], 0.55]); L /= np.linalg.norm(L)
        def shade(px, py):
            u, v = (px - x) / r, (py - y) / r
            q = 1 - u * u - v * v
            if q <= 0: return 1.0
            nz = math.sqrt(q)
            lam = max(0.0, u * L[0] + v * L[1] + nz * L[2])
            return float(np.clip(1.05 - lam, 0, 1)) ** 1.4
        th = np.linspace(0, 2 * math.pi, 64, endpoint=False)
        poly = [(x + (r - 0.5) * math.cos(t), y + (r - 0.5) * math.sin(t)) for t in th]
        self.hatch_poly(poly, 32, sp, wm, layer, wfun=shade)


def contours(field, level, scale_x=1.0, scale_y=1.0, off_x=0.0, off_y=0.0):
    """Iso-lines of a 2-D array as lists of (x, y) canvas points (skimage marching squares)."""
    from skimage import measure
    out = []
    for c in measure.find_contours(np.asarray(field, np.float64), level):
        out.append([(off_x + p[1] * scale_x, off_y + p[0] * scale_y) for p in c])
    return out


def _arc(cx, cy, rx, ry, a0, a1, n=24):
    t = np.linspace(math.radians(a0), math.radians(a1), n)
    return list(zip(cx + rx * np.cos(t), cy + ry * np.sin(t)))   # y down; angles clockwise on screen


def _digit_strokes(ch):
    """Unit-box (0..1 x 0..1, y down) stroke paths for 0-9."""
    if ch == '0': return [_arc(.5, .5, .5, .5, 0, 360, 40)]
    if ch == '1': return [[(.22, .2), (.56, 0), (.56, 1)], [(.26, 1), (.86, 1)]]
    if ch == '2': return [_arc(.5, .27, .46, .27, 200, 380, 20) + [(.9, .45), (0.05, 1), (1, 1)]]
    if ch == '3': return [_arc(.48, .25, .42, .25, 200, 450, 22), _arc(.48, .73, .5, .27, 270, 520, 22)]
    if ch == '4': return [[(.72, 1), (.72, 0), (0, .7), (1, .7)]]
    if ch == '5': return [[(.9, 0), (.14, 0), (.08, .45)] + _arc(.47, .68, .48, .32, 225, 495, 24)]
    if ch == '6': return [_arc(.52, .70, .46, .30, 0, 360, 30), [(0.06, .7)] + _arc(.6, .55, .54, .55, 180, 265, 14)]
    if ch == '7': return [[(0, 0), (1, 0), (.36, 1)]]
    if ch == '8': return [_arc(.5, .24, .38, .24, 0, 360, 28), _arc(.5, .73, .48, .27, 0, 360, 30)]
    if ch == '9': return [_arc(.48, .30, .46, .30, 0, 360, 30), [(.94, .3)] + _arc(.4, .45, .54, .55, 0, 85, 14)]
    raise ValueError(ch)


def fbm(shape, rng, octaves=5, base=4, persistence=0.55):
    """Smooth fractal value noise in [-1,1]-ish, numpy only."""
    h, w = shape
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.standard_normal((n + 1, n + 1)).astype(np.float32)
        im = Image.fromarray(g).resize((w, h), Image.BICUBIC)
        out += amp * np.asarray(im)
        tot += amp
        amp *= persistence
    out /= tot
    return out / (np.abs(out).max() + 1e-6)


class Field:
    """Sampleable smooth noise field on the final canvas (for flow, wobble)."""
    def __init__(self, rng, res=512, octaves=4, base=3):
        self.res = res
        self.g = fbm((res, res), rng, octaves, base)

    def __call__(self, x, y):
        u = np.clip(np.asarray(x) / OUT * (self.res - 1), 0, self.res - 1)
        v = np.clip(np.asarray(y) / OUT * (self.res - 1), 0, self.res - 1)
        return ndimage.map_coordinates(self.g, [np.atleast_1d(v), np.atleast_1d(u)], order=1)


def paper(rng):
    s = (OUT, OUT)
    base = np.ones(s + (3,), np.float32) * PAPER
    mott = fbm(s, rng, 6, 3, 0.6)                       # cloudy mottling
    grain = rng.standard_normal(s).astype(np.float32)
    grain = ndimage.gaussian_filter(grain, 0.7)
    fib = ndimage.gaussian_filter(rng.standard_normal(s).astype(np.float32), (0.6, 6.0))  # laid fibres
    lum = 1 + 0.018 * mott + 0.020 * grain / (grain.std() + 1e-6) + 0.010 * fib / (fib.std() + 1e-6)
    base *= lum[..., None]
    # faint warm vignette, like an aged sheet
    yy, xx = np.mgrid[0:OUT, 0:OUT] / OUT - 0.5
    vig = 1 - 0.05 * (xx ** 2 + yy ** 2) * 2
    base *= vig[..., None]
    return base, grain


def finish_mask(img, rng, bleed=1.0, dry=0.18):
    """Downsample, add ink bleed and dry-brush break-up. Returns float 0..1."""
    m = np.asarray(img.resize((OUT, OUT), Image.LANCZOS), np.float32) / 255.0
    if bleed > 0:
        b = ndimage.gaussian_filter(m, bleed * 1.6)
        m = np.maximum(m, 0.55 * b)            # soft halo where ink wicks into fibres
    if dry > 0:
        n = ndimage.gaussian_filter(rng.standard_normal(m.shape).astype(np.float32), 1.1)
        n = n / (n.std() + 1e-6)
        m = m * np.clip(1 - dry * np.maximum(n, 0) * 0.9, 0, 1)
    return np.clip(m, 0, 1)


def render(cv, n, name, extra=None):
    rng = np.random.default_rng(None if cv.seed is None else cv.seed + 7)
    pap, grain = paper(rng)
    ink = finish_mask(cv.layers['ink'], rng, bleed=1.0, dry=0.22)
    acc = finish_mask(cv.layers['accent'], rng, bleed=1.3, dry=0.15)
    out = pap.copy()
    # multiply-style ink on paper, density modulated by paper tooth
    tooth = 1 - 0.10 * np.clip(grain / (grain.std() + 1e-6), 0, None) * 0.5
    for m, col, dens in ((acc, np.array(ACCENTS[n], np.float32), 0.92), (ink, INK, 0.94)):
        a = (m * dens * tooth)[..., None]
        out = out * (1 - a) + out * (col / PAPER) * a
    out = np.clip(out, 0, 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGB')
    os.makedirs(f'{ROOT}/images', exist_ok=True)
    os.makedirs(f'{ROOT}/previews', exist_ok=True)
    im.save(f'{ROOT}/images/{n:02d}.png', optimize=True)
    im.resize((1200, 1200), Image.LANCZOS).save(f'{ROOT}/previews/{n:02d}.png')
    return im


def plate_title(n):
    """Plate name (e.g. 'The Ore') from the art-brief table so text and art agree."""
    import re
    import json
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'titles.json')))[str(n)]


def write_data(n, data):
    os.makedirs(f'{ROOT}/data', exist_ok=True)
    data = {**data, "title": data.get("title") or plate_title(n)}
    data = {k: data[k] for k in (["piece", "title"] + [k for k in data if k not in ("piece", "title")]) if k in data}
    with open(f'{ROOT}/data/{n:02d}.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
