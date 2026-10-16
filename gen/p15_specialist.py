"""15 - The Specialist Film. Ball-and-stick engraving of one heteroleptic zirconium precursor,
CpZr(NMe2)3, caught on a hydroxylated ZrO2 surface after its first half-cycle: two Zr-O bonds
formed (accent), two HNMe2 by-products drifting away, Cp and one NMe2 still attached."""
import math, numpy as np
from style import *

SEED = None  # private, not published
DATA = {
  "piece": "15 - The Specialist Film", "seed": SEED,
  "precursor": "CpZr(NMe2)3, tris(dimethylamino)cyclopentadienyl zirconium, C11H23N3Zr, 288.5 g/mol",
  "use": "ALD of high-k ZrO2 for DRAM capacitor dielectrics (replaced homoleptic Zr(NEtMe)4)",
  "ALD_growth_per_cycle_A": {"with O3 at 230 C (QCM)": 0.55, "reported at 300 C": 0.9},
  "first_half_cycle": "-OH* x2 + CpZr(NMe2)3 -> (-O-)2ZrCp(NMe2)* + 2 HNMe2 (QCM ratio 0.64 +/- 0.03; DFT barriers 0.22 and 0.16 eV)",
  "geometry_A": {"Zr-N": 2.09, "Zr-Cp_centroid": 2.22, "Cp_C-C": 1.40, "N-C": 1.45, "C-H": 1.09, "Zr-O": 2.0, "surface_OH_per_nm2": 4.5},
  "px_per_angstrom": 185,
  "mapping": {
    "molecule": "the surface species O2ZrCp(NMe2)* as engraved spheres (Zr, O, N, C, H at scaled covalent radii) and cylinder bonds, depth-sorted; tone by Lambert shading from upper left",
    "accent": "the zirconium atom being delivered and its two new Zr-O bonds to the surface",
    "by-products": "the two released HNMe2 molecules drawn lighter, moving away",
    "surface": "a small hydroxylated ZrO2 slab fragment (front row cut away to show the section): remaining OH groups at roughly the 4.5 per nm2 density used in the DFT model",
  },
  "note": "Precursor class shown as an example of specialist ALD chemistry; not a claim about any specific supplier's product.",
  "sources": [
    "https://pubs.rsc.org/en/content/articlehtml/2025/ma/d4ma00966e (CpZr(NMe2)3 ALD of ZrO2: two NMe2 released, O2ZrCp(NMe2)* surface species, Zr-N 2.09 A, OH 4.5 nm-2, GPC ~0.9 A at 300 C, used in DRAM)",
    "https://www.sciencedirect.com/science/article/pii/S016943322300781X (CpZr(NMe2)3 for high-k DRAM capacitor dielectrics)",
    "https://www.adeka.co.jp/en/ir/library/pdf/250227_semiconductor_jigyo_e.pdf (ADEKA: ALD high-k materials for DRAM capacitors)",
  ],
}

cv = Canvas(SEED); rng = cv.rng
S = DATA["px_per_angstrom"]
ox, oy = OUT / 2 + 30, 1450
yaw, pitch = math.radians(28), math.radians(14)
def proj(p):
    x, y, z = p
    x1 = x * math.cos(yaw) + z * math.sin(yaw); z1 = -x * math.sin(yaw) + z * math.cos(yaw)
    y2 = y * math.cos(pitch) - z1 * math.sin(pitch); z2 = y * math.sin(pitch) + z1 * math.cos(pitch)
    return ox + x1 * S, oy - y2 * S, z2
RAD = {"Zr": 0.82, "O": 0.52, "N": 0.48, "C": 0.44, "H": 0.24}
atoms, bonds = [], []
def add(el, p, tag='mol'):
    atoms.append((el, np.array(p, float), tag)); return len(atoms) - 1
def bond(i, j, kind='ink'): bonds.append((i, j, kind))
def methyl(Ni, Cpos, away):
    c = add("C", Cpos, atoms[Ni][2]); bond(Ni, c)
    u = np.array(Cpos) - atoms[Ni][1]; u /= np.linalg.norm(u)
    a = np.cross(u, [0.3, 1, 0.2]); a /= np.linalg.norm(a); b = np.cross(u, a)
    for k in range(3):
        t = 2 * math.pi * k / 3 + away
        d = u * 0.34 + 0.94 * (a * math.cos(t) + b * math.sin(t))
        h = add("H", np.array(Cpos) + 1.09 * d / np.linalg.norm(d), atoms[Ni][2]); bond(c, h)
    return c

zr = add("Zr", (0, 0, 0))
cpc = np.array([0, 2.22, 0])
ring = []
for k in range(5):
    t = 2 * math.pi * k / 5
    ring.append(add("C", cpc + [1.19 * math.cos(t), 0, 1.19 * math.sin(t)]))
for k in range(5):
    bond(ring[k], ring[(k + 1) % 5])
    t = 2 * math.pi * k / 5
    h = add("H", cpc + [2.27 * math.cos(t), 0.08, 2.27 * math.sin(t)]); bond(ring[k], h)
    bond(zr, ring[k], 'thin')
# remaining NMe2
n1 = add("N", (2.0, 0.25, 0.45)); bond(zr, n1)
v = atoms[n1][1] - atoms[zr][1]; v /= np.linalg.norm(v)
perp = np.array([0, 0, 1.0])
for sgn in (1, -1):
    d = 0.5 * v + sgn * 0.866 * np.cross(v, perp) / np.linalg.norm(np.cross(v, perp))
    methyl(n1, atoms[n1][1] + 1.45 * d, sgn * 0.4)
# two new Zr-O bonds to the surface
oA = add("O", (-0.9, -1.78, 0.95), 'surf'); oB = add("O", (-0.9, -1.78, -0.95), 'surf')
bond(zr, oA, 'accent'); bond(zr, oB, 'accent')
# ZrO2 slab: O top layer, Zr below, OH groups remaining at 4.5 / nm2 (spacing ~4.7 A)
for i in range(-2, 2):
    for kz in (0, 1):
        x, z = i * 2.6 + (kz % 2) * 1.3, kz * 2.6
        if abs(x + 0.9) < 1.0 and abs(z) < 1.4: continue
        o = add("O", (x, -1.78, z), 'surf')
        zz = add("Zr", (x + 1.3, -2.95, z + 0.9), 'surf'); bond(o, zz)
        if kz == 0 and abs(x) > 2.0:
            h = add("H", (x, -1.78 + 0.97, z), 'surf'); bond(o, h)
        o2 = add("O", (x, -4.1, z), 'surf'); bond(zz, o2)
# the two released HNMe2, drifting away
def hnme2(c, rot):
    n = add("N", c, 'gone'); h = add("H", np.array(c) + [0, 1.01, 0], 'gone'); bond(n, h)
    for sgn in (1, -1):
        t = rot + sgn * 2.0
        methyl(n, np.array(c) + 1.45 * np.array([math.cos(t), -0.35, math.sin(t)]), sgn)
hnme2((-4.3, 4.3, 1.5), 0.3); hnme2((4.4, 4.5, -1.2), 2.6)
DATA["atoms_drawn"] = len(atoms); DATA["bonds_drawn"] = len(bonds)

# ---- draw: bonds and atoms depth-sorted, far first
items = []
for i, (el, p, tag) in enumerate(atoms):
    x, y, z = proj(p); items.append((z, 'a', i))
for (i, j, kind) in bonds:
    z = 0.5 * (proj(atoms[i][1])[2] + proj(atoms[j][1])[2]) + 0.05
    items.append((z, 'b', (i, j, kind)))
items.sort(key=lambda t: -t[0])
for z, typ, ref in items:
    if typ == 'a':
        el, p, tag = atoms[ref]
        x, y, _ = proj(p)
        r = RAD[el] * S * (0.9 if tag == 'gone' else 1.0)
        layer = 'accent' if (ref == zr) else 'ink'
        if tag == 'gone':
            cv.erase_circle(x, y, r + 1); cv.circle(x, y, r, 1.4)
            cv.hatch_poly([(x + (r - 2) * math.cos(t), y + (r - 2) * math.sin(t)) for t in np.linspace(0, 6.28, 40)], 32, 9, 0.6)
        else:
            if layer == 'accent':
                cv.sphere(x, y, r, 'accent', spacing=7, wmax=4.2, outline=3.4)
                cv.circle(x, y, r + 10, 1.6, 'accent')
            else:
                cv.sphere(x, y, r, layer, spacing=max(3.6, r / 10))
    else:
        i, j, kind = ref
        (x0, y0, _), (x1, y1, _) = proj(atoms[i][1]), proj(atoms[j][1])
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1: continue
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        w = 0.13 * S if kind != 'thin' else 0.05 * S
        if kind == 'thin':
            # Cp-Zr eta5 contacts: dashed hairlines
            for t in np.arange(0.12, 0.88, 0.08):
                cv.seg(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, x0 + (x1 - x0) * (t + 0.04), y0 + (y1 - y0) * (t + 0.04), 1.2)
            continue
        layer = 'accent' if kind == 'accent' else 'ink'
        poly = [(x0 + nx * w, y0 + ny * w), (x1 + nx * w, y1 + ny * w), (x1 - nx * w, y1 - ny * w), (x0 - nx * w, y0 - ny * w)]
        cv.erase_poly(poly)
        cv.seg(*poly[0], *poly[1], 1.6, layer); cv.seg(*poly[2], *poly[3], 1.6, layer)
        for o in np.linspace(-0.7, 0.9, 6)[3:]:
            cv.seg(x0 - nx * w * o, y0 - ny * w * o, x1 - nx * w * o, y1 - ny * w * o, 0.9, layer)
        if kind == 'accent':
            for o in np.linspace(-0.6, 0.6, 5):
                cv.seg(x0 - nx * w * o, y0 - ny * w * o, x1 - nx * w * o, y1 - ny * w * o, 1.4, 'accent')

cv.plate_number(15)
write_data(15, DATA)
render(cv, 15, 'specialist')
print(len(atoms), len(bonds))
