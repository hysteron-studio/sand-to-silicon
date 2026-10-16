"""01 - The Ore. A terminated quartz crystal whose front prism face is drawn as its own
alpha-quartz SiO4 framework (true unit cell, true Si-O bonds); twenty accent marks are the
IOTA-STD impurity budget of ~20 ppm, one mark per ppm."""
import math, numpy as np
from skimage.measure import points_in_poly
from style import *

SEED = None  # private, not published
A, C = 4.9134, 5.4052
IMP = {"Al": 14, "Ti": 1.2, "Na": 1.0, "K": 0.7, "Ca": 0.6, "Li": 0.5, "Fe": 0.3}
DATA = {
  "piece": "01 - The Ore", "seed": SEED,
  "mineral": "alpha-quartz, SiO2, trigonal, space group P3(2)21",
  "lattice_A": {"a": A, "c": C}, "Si_site": "3a (0.4697, 0, 0)", "O_site": "6c (0.4135, 0.2669, 0.1191)",
  "Si_O_bond_cutoff_A": 1.70, "r_face_angle_to_c_deg": 38.2,
  "purity": "IOTA Standard >99.998% SiO2, ~20 ppm total of 12 monitored elements",
  "impurities_ppm_IOTA_STD": IMP,
  "px_per_angstrom": 17.5,
  "mapping": {
    "front prism face": "the real alpha-quartz framework projected along the viewing direction (c vertical): Si as filled dots, O as open dots, Si-O bonds < 1.70 A; line weight by depth",
    "side prism faces": "horizontal growth striations perpendicular to c, the field mark of natural quartz; tone from a light source upper left",
    "termination": "three visible rhombohedral faces at 38.2 deg to c",
    "accent": "one mark per ppm of IOTA-STD impurity: 14 Al, 1 Ti, 1 Na, 1 K, 1 Ca, 1 Li (rounded) and a small mark for 0.3 ppm Fe = 20 marks",
    "broken base": "crystal snapped from its pegmatite matrix",
  },
  "sources": [
    "https://www.sibelco.com/en/materials/high-purity-quartz (IOTA HPQ from Spruce Pine, used for CZ crucibles)",
    "https://www.magneticseparatormachine.com/news/high-purity-quartz-sand-industry-s-structure-purity-standard-technological-obstacles-and-application-171914.html (IOTA-STD: 12 elements < 20 ppm, K/Na/Li < 1 ppm)",
    "https://greentechminerals.com.au/our-product/global-market/ (IOTA standard 20 ppm, >99.998% SiO2)",
    "Levien, Prewitt & Weidner (1980) Am. Mineral. 65, 920 - alpha-quartz a=4.9134, c=5.4052 A, Si x=0.4697, O (0.4135,0.2669,0.1191)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
S = DATA["px_per_angstrom"]

# ---------------- camera: c axis vertical, rotate about c then tilt to see the cap
phi, tilt, lean = math.radians(14), math.radians(13), math.radians(7)
def view(P):
    P = np.atleast_2d(P).astype(float)
    x, y, z = P[:, 0], P[:, 1], P[:, 2]          # z = up (c axis)
    x1 = x * math.cos(phi) - y * math.sin(phi); y1 = x * math.sin(phi) + y * math.cos(phi)
    # y1 = depth (towards viewer negative); tilt about screen-x
    z2 = z * math.cos(tilt) + y1 * math.sin(tilt); d2 = -z * math.sin(tilt) + y1 * math.cos(tilt)
    sx_, sy_ = x1, -z2
    lx = sx_ * math.cos(lean) - sy_ * math.sin(lean); ly = sx_ * math.sin(lean) + sy_ * math.cos(lean)
    return np.stack([lx, ly, d2], 1)              # screen x, screen y (down), depth

cx, base_y = OUT / 2 - 90, 2470
Rh = 600                    # corner radius of the hexagonal prism (px)
Hp = 1300                   # prism length
ap = Rh * math.cos(math.pi / 6)
Ht = ap / math.tan(math.radians(38.2))            # cap height: r faces at 38.2 deg to c
ang = [math.radians(30 + 60 * k) for k in range(6)]
bot = [np.array([Rh * math.cos(a), Rh * math.sin(a), 0.0]) for a in ang]
top = [np.array([Rh * math.cos(a), Rh * math.sin(a), Hp]) for a in ang]
apex = np.array([0, 0, Hp + Ht])
oy = 0
def scr(P):
    v = view(P)
    return v[:, 0] + cx, v[:, 1] + base_y
def pts(Ps):
    v = view(np.array(Ps)); return [(x + cx, y + base_y) for x, y in v[:, :2]]

vdir = np.array([0, 0, 1.0])
def visible(face3d):
    P = np.array(face3d); n = np.cross(P[1] - P[0], P[2] - P[0])
    cen = P.mean(0)
    if np.dot(n, cen) < 0: n = -n                      # outward
    nv = view(n[None])[0]
    return nv[2] < 0, n / np.linalg.norm(n)            # depth axis: negative = towards viewer

Lgt = np.array([-0.6, -0.5, 0.62]); Lgt /= np.linalg.norm(Lgt)   # world light, upper left front

faces = []
for k in range(6):
    f = [bot[k], bot[(k + 1) % 6], top[(k + 1) % 6], top[k]]
    vis, n = visible(f)
    if vis: faces.append(('prism', k, f, n))
for k in range(6):
    f = [top[k], top[(k + 1) % 6], apex]
    vis, n = visible(f)
    if vis: faces.append(('cap', k, f, n))

# jagged broken base shared by prism faces
def jag(p0, p1, n=7):
    out = []
    for i in range(n + 1):
        t = i / n
        p = p0 + (p1 - p0) * t
        if 0 < i < n: p = p + np.array([0, 0, rng.uniform(0, 120)])
        out.append(p)
    return out
jag_cache = {}

def tone(n):
    nv = view(n[None])[0]
    lam = max(0, -(nv[0] * -0.62 + nv[1] * -0.55 + nv[2] * -0.56))
    return lam

front = min((f for f in faces if f[0] == 'prism'), key=lambda f: view(np.array(f[2]).mean(0)[None])[0][2])
outline_polys = []
for kind, k, f, n in faces:
    if kind == 'prism':
        key = k
        if key not in jag_cache: jag_cache[key] = jag(f[0], f[1])
        poly3 = jag_cache[key] + [f[2], f[3]]
    else:
        poly3 = f
    poly = pts(poly3); outline_polys.append(poly)
    lam = np.dot(n, Lgt)
    if kind == 'prism' and f is not front[2]:
        # horizontal striations: lines between the two vertical edges at irregular heights
        b0, b1, t1, t0 = f
        z = 0.0
        dens = 1 - np.clip(lam, -0.2, 1) * 0.75
        while z < Hp:
            z += rng.exponential(5 + 22 * (1 - dens)) + 3
            if z >= Hp: break
            p0 = b0 + (t0 - b0) * z / Hp; p1 = b1 + (t1 - b1) * z / Hp
            # skip above the jagged base line
            seg = pts([p0, p1])
            w = 0.7 + 1.6 * dens * rng.uniform(0.5, 1.2)
            a = rng.uniform(0, 0.15); b = rng.uniform(0.85, 1.0)
            if rng.random() < 0.25: a, b = rng.uniform(0, .5), rng.uniform(.5, 1)
            q0 = (seg[0][0] + (seg[1][0] - seg[0][0]) * a, seg[0][1] + (seg[1][1] - seg[0][1]) * a)
            q1 = (seg[0][0] + (seg[1][0] - seg[0][0]) * b, seg[0][1] + (seg[1][1] - seg[0][1]) * b)
            if z < 150:   # stay above the break
                continue
            cv.line([q0, q1], w, 'ink', jitter=0.4)
    elif kind == 'cap':
        dens = 1 - np.clip(lam, -0.2, 1) * 0.8
        e = np.array(pts([f[0], f[1]]))
        angd = math.degrees(math.atan2(e[1][1] - e[0][1], e[1][0] - e[0][0]))
        cv.hatch_poly(poly, angd + 90 + rng.uniform(-8, 8), 7 + 16 * (1 - dens), 0.8 + 1.4 * dens, 'ink', jitter=0.3)

# ---------------- the framework on the front face
fpoly = outline_polys[[i for i, f in enumerate(faces) if f[2] is front[2]][0]]
ops = [lambda x, y, z: (x, y, z), lambda x, y, z: (-y, x - y, z + 2 / 3), lambda x, y, z: (-x + y, -x, z + 1 / 3),
       lambda x, y, z: (y, x, -z), lambda x, y, z: (x - y, -y, -z + 1 / 3), lambda x, y, z: (-x, -x + y, -z + 2 / 3)]
def orbit(p):
    s = set()
    for o in ops:
        q = tuple(round(v % 1.0, 5) % 1.0 for v in o(*p)); s.add(q)
    return sorted(s)
si_f = orbit((0.4697, 0.0, 0.0)); o_f = orbit((0.4135, 0.2669, 0.1191))
DATA["atoms_per_cell"] = {"Si": len(si_f), "O": len(o_f)}
a1 = np.array([A, 0, 0]); a2 = np.array([-A / 2, A * math.sqrt(3) / 2, 0]); a3 = np.array([0, 0, C])
def cart(f, i, j, k): return (f[0] + i) * a1 + (f[1] + j) * a2 + (f[2] + k) * a3
N = 9; NZ = 16
Si = np.array([cart(f, i, j, k) for f in si_f for i in range(-N, N) for j in range(-N, N) for k in range(-1, NZ)])
O = np.array([cart(f, i, j, k) for f in o_f for i in range(-N, N) for j in range(-N, N) for k in range(-1, NZ)])
# keep a thin slab just inside the front face: depth measured along the face normal
fn = front[3]; fp = np.array(front[2]).mean(0)
def slab(P, scale):
    W3 = P * scale
    W3[:, 2] += 60
    c0 = np.array([fp[0], fp[1], 0]); dvec = (W3 - c0) @ fn
    return W3, dvec
from scipy.spatial import cKDTree
SiW, dSi = slab(Si, S); OW, dO = slab(O, S)
# shift lattice so the face centre is near the lattice origin
keepSi = (dSi > -1.15 * C * S) & (dSi < 0); keepO = (dO > -1.15 * C * S - 30) & (dO < 30)
SiW, dSi = SiW[keepSi], dSi[keepSi]; OW_k, dO_k = OW[keepO], dO[keepO]
tree = cKDTree(OW_k)
fpoly_np = np.array(fpoly)
vs = view(SiW); vo = view(OW_k)
sx, sy = vs[:, 0] + cx, vs[:, 1] + base_y; ox, oy_ = vo[:, 0] + cx, vo[:, 1] + base_y
inSi = points_in_poly(np.stack([sx, sy], 1), fpoly_np)
# shrink polygon for a clean inner margin
cen = fpoly_np.mean(0); inner = cen + (fpoly_np - cen) * 0.94
inSi = points_in_poly(np.stack([sx, sy], 1), inner)
dmin, dmax = dSi.min(), dSi.max()
nb = 0
for i in np.nonzero(inSi)[0]:
    dep = (dSi[i] - dmin) / (dmax - dmin + 1e-6)      # 1 = nearest the surface
    for j in tree.query_ball_point(SiW[i], 1.70 * S):
        p = (ox[j], oy_[j])
        if not points_in_poly(np.array([p]), inner)[0]: continue
        cv.seg(sx[i], sy[i], p[0], p[1], 0.9 + 2.0 * dep, 'ink'); nb += 1
    cv.dot(sx[i], sy[i], 3.2 + 3.0 * dep)
drawnO = set()
for i in np.nonzero(inSi)[0]:
    for j in tree.query_ball_point(SiW[i], 1.70 * S):
        if j in drawnO: continue
        drawnO.add(j)
        if not points_in_poly(np.array([(ox[j], oy_[j])]), inner)[0]: continue
        cv.erase_circle(ox[j], oy_[j], 4.2); cv.circle(ox[j], oy_[j], 4.2, 1.3, 'ink')
DATA["drawn"] = {"Si": int(inSi.sum()), "Si_O_bonds": nb, "O": len(drawnO)}

# ---------------- outline the habit, heavier on the silhouette
for poly in outline_polys:
    cv.line(poly + [poly[0]], 2.0, 'ink', jitter=0.3)
# silhouette re-stroked
allp = np.vstack(outline_polys)
from scipy.spatial import ConvexHull
# broken base underside: short dark hatching under the jagged line
for kind, k, f, n in faces:
    if kind != 'prism': continue
    jp = pts(jag_cache[k])
    for (x0, y0), (x1, y1) in zip(jp[:-1], jp[1:]):
        # conchoidal ripples: nested arcs hanging from each fracture segment
        L = math.hypot(x1 - x0, y1 - y0)
        for r_ in np.arange(0.25, 1.0, 0.16):
            th = np.linspace(0.15, math.pi - 0.15, 18)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ang0 = math.atan2(y1 - y0, x1 - x0)
            arc = [(mx + math.cos(ang0) * (-math.cos(t)) * L / 2 * r_ - math.sin(ang0) * (-math.sin(t)) * L * 0.18 * r_,
                    my + math.sin(ang0) * (-math.cos(t)) * L / 2 * r_ + math.cos(ang0) * (-math.sin(t)) * L * 0.18 * r_) for t in th]
            cv.line(arc, 1.0, 'ink', jitter=0.4)

# ---------------- 20 impurity marks, one per ppm
marks = []
for el, ppm in IMP.items():
    n = max(1, int(round(ppm)))
    for _ in range(n): marks.append((el, ppm / n))
polys_np = [np.array(p) for p in outline_polys]
placed = []
while len(placed) < len(marks):
    x, y = rng.uniform(cx - Rh - 300, cx + Rh + 300), rng.uniform(base_y - Hp - Ht - 200, base_y - 160)
    if not any(points_in_poly(np.array([(x, y)]), p)[0] for p in polys_np): continue
    if any((x - a) ** 2 + (y - b) ** 2 < 120 ** 2 for a, b in placed): continue
    placed.append((x, y))
for (el, v), (x, y) in zip(marks, placed):
    r = 7 if v >= 0.5 else 4
    cv.erase_circle(x, y, r + 5)
    cv.dot(x, y, r, 'accent'); cv.circle(x, y, r + 9, 1.6, 'accent')
DATA["impurity_marks"] = [{"element": e, "ppm_each": round(v, 2), "xy": [round(x), round(y)]} for (e, v), (x, y) in zip(marks, placed)]

cv.plate_number(1)
write_data(1, DATA)
render(cv, 1, 'ore')
print(DATA["drawn"], len(marks))
