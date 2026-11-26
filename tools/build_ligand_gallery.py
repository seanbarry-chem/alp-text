"""Idealized 3D geometries for the ligand gallery (Simulation 2.9, chapters/01b-fundamentals.qmd).

Usage:  pip install rdkit numpy  &&  python tools/build_ligand_gallery.py
Writes chapters/data/ligand-gallery.json. To add a molecule, build it below and add its key
to galInfo in the chapter.

Metal centres are placed analytically; organic fragments are embedded with RDKit
and attached rigidly. Geometries are illustrative, not optimized structures."""
import numpy as np, json
from rdkit import Chem
from rdkit.Chem import AllChem
rng = np.random.default_rng(3)

def unit(v): v=np.asarray(v,float); return v/np.linalg.norm(v)

def embed(smi, seed=11):
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    ps = AllChem.ETKDGv3(); ps.randomSeed = seed
    assert AllChem.EmbedMolecule(m, ps) == 0, smi
    try: AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    except Exception: AllChem.UFFOptimizeMolecule(m, maxIters=2000)
    X = m.GetConformer().GetPositions()
    return m, X

def rot_to(a, b):
    a, b = unit(a), unit(b); v = np.cross(a, b); c = a @ b
    if np.linalg.norm(v) < 1e-8:
        if c > 0: return np.eye(3)
        p = unit(np.cross(a, [1, 0, 0] if abs(a[0]) < .9 else [0, 1, 0]))
        return 2 * np.outer(p, p) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))

def axis_rot(axis, t):
    k = unit(axis); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(t) * K + (1 - np.cos(t)) * K @ K

class Mol:
    def __init__(s): s.el = []; s.X = []
    def add(s, e, x): s.el.append(e); s.X.append(np.asarray(x, float)); return len(s.el) - 1
    def attach(s, smi, anchor, direction, L):
        """smi has one [2H] marking the bond to the anchor. Attaching atom goes to anchor+L*dir."""
        m, X = embed(smi)
        mk = [a.GetIdx() for a in m.GetAtoms() if a.GetIsotope() == 2][0]
        at = m.GetAtomWithIdx(mk).GetNeighbors()[0].GetIdx()
        d = unit(direction); target = np.asarray(anchor) + L * d
        R = rot_to(X[mk] - X[at], -d)
        Y = (X - X[at]) @ R.T
        keep = [i for i in range(len(X)) if i != mk]
        best, bestY = -1, None
        for t in np.linspace(0, 2 * np.pi, 48, endpoint=False):
            Z = Y @ axis_rot(d, t).T + target
            if s.X:
                dm = np.min(np.linalg.norm(Z[keep][:, None, :] - np.array(s.X)[None], axis=2))
            else: dm = 9
            if dm > best: best, bestY = dm, Z
        for i in keep:
            s.add(m.GetAtomWithIdx(i).GetSymbol(), bestY[i])
    def methyl(s, C, away):
        """Add 3 H to carbon C pointing away from 'away' direction (unit, from C outward)."""
        a = unit(away); p = unit(np.cross(a, [0.3, 1, 0.2]))
        for k in range(3):
            q = axis_rot(a, 2 * np.pi * k / 3) @ p
            s.add("H", np.asarray(C) + 1.09 * (0.334 * a + 0.943 * q))
    def xyz(s, title):
        X = np.array(s.X); X -= X.mean(0)
        return f"{len(s.el)}\n{title}\n" + "\n".join(f"{e} {x:.3f} {y:.3f} {z:.3f}" for e, (x, y, z) in zip(s.el, X))

T = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) / np.sqrt(3)       # tetrahedral
O6 = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
TP = np.array([[1, 0, 0], [-.5, .866, 0], [-.5, -.866, 0]])
out = {}

def mono(metal, ligs, dirs, title, key):
    m = Mol(); m.add(metal, [0, 0, 0])
    for (smi, L), d in zip(ligs, dirs):
        if smi in ("Cl", "F"): m.add(smi, L * unit(d))
        else: m.attach(smi, [0, 0, 0], d, L)
    out[key] = m.xyz(title)

mono("Al", [("[2H]C", 1.96)] * 3, TP, "AlMe3 (monomer)", "AlMe3")
mono("Ti", [("Cl", 2.17)] * 4, T, "TiCl4", "TiCl4")
mono("W", [("F", 1.83)] * 6, O6, "WF6", "WF6")
mono("Zn", [("[2H]CC", 1.95)] * 2, [[0, 0, 1], [0, 0, -1]], "ZnEt2", "ZnEt2")
mono("Ti", [("[2H]N(C)C", 1.92)] * 4, T, "Ti(NMe2)4 (TDMAT)", "TDMAT")
mono("Ti", [("[2H]OC(C)C", 1.79)] * 4, T, "Ti(OiPr)4 (TTIP)", "TTIP")
mono("Zn", [("[2H]N([Si](C)(C)C)[Si](C)(C)C", 1.83)] * 2, [[0, 0, 1], [0, 0, -1]], "Zn[N(SiMe3)2]2", "Znbtsa")

# Al2X6 dimers (D2h): Al on x axis, bridges on y, terminals in xz plane
def al2(term, bridge, key, title):
    m = Mol(); dAl = 2.60 if bridge == "Me" else 3.21
    rb = 2.14 if bridge == "Me" else 2.25; rt = 1.96 if term == "Me" else 2.06
    yb = np.sqrt(rb ** 2 - (dAl / 2) ** 2)
    A = [np.array([dAl / 2, 0, 0]), np.array([-dAl / 2, 0, 0])]
    for a in A: m.add("Al", a)
    for sgn in (1, -1):
        B = np.array([0, sgn * yb, 0])
        if bridge == "Me": m.add("C", B); m.methyl(B, [0, sgn, 0])
        else: m.add("Cl", B)
    for a in A:
        for sz in (1, -1):
            d = unit([np.sign(a[0]) * 0.55, 0, sz * 0.83])
            P = a + rt * d
            if term == "Me": m.add("C", P); m.methyl(P, d)
            else: m.add("Cl", P)
    out[key] = m.xyz(title)
al2("Me", "Me", "Al2Me6", "Al2Me6 (TMA dimer, 3c-2e bridges)")
al2("Cl", "Cl", "Al2Cl6", "Al2Cl6 (3c-4e bridges)")

# DMAI dimer [Me2Al(mu-OiPr)]2
m = Mol(); A = [np.array([1.42, 0, 0]), np.array([-1.42, 0, 0])]
for a in A: m.add("Al", a)
for sgn in (1, -1):
    O = np.array([0, sgn * 1.24, 0]); m.add("O", O)
    m.attach("[2H]C(C)C", O, [0, sgn, 0], 1.45)
for a in A:
    for sz in (1, -1):
        d = unit([np.sign(a[0]) * 0.55, 0, sz * 0.83]); P = a + 1.96 * d
        m.add("C", P); m.methyl(P, d)
out["DMAI"] = m.xyz("[Me2Al(OiPr)]2 (DMAI dimer)")

# RuCp2 (eclipsed sandwich)
m = Mol(); m.add("Ru", [0, 0, 0])
for z in (1.82, -1.82):
    for k in range(5):
        t = 2 * np.pi * k / 5
        m.add("C", [1.21 * np.cos(t), 1.21 * np.sin(t), z]); m.add("H", [2.28 * np.cos(t), 2.28 * np.sin(t), z * 1.02])
out["RuCp2"] = m.xyz("RuCp2 (ruthenocene)")

# chelates: embed a BF2 or BMe2 analogue, strip boron + its substituents, fit donors to target positions
def chelate(m, smi, donors_sym, d1, d2, r):
    mol, X = embed(smi)
    B = [a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() == "B"][0]
    drop = {B} | {n.GetIdx() for n in mol.GetAtomWithIdx(B).GetNeighbors() if n.GetSymbol() not in donors_sym}
    drop |= {h.GetIdx() for i in list(drop) for h in mol.GetAtomWithIdx(i).GetNeighbors() if h.GetSymbol() == "H"}
    drop |= {h.GetIdx() for i in list(drop) if mol.GetAtomWithIdx(i).GetSymbol() == "C"
             for h in mol.GetAtomWithIdx(i).GetNeighbors() if h.GetSymbol() == "H"}
    D = [n.GetIdx() for n in mol.GetAtomWithIdx(B).GetNeighbors() if n.GetSymbol() in donors_sym]
    P = np.array([X[B], X[D[0]], X[D[1]]]); Q = np.array([[0, 0, 0], r * unit(d1), r * unit(d2)])
    # Kabsch fit of (B, D1, D2) onto (M, target1, target2)
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    U, S, Vt = np.linalg.svd(Pc.T @ Qc); dd = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, dd]) @ U.T
    Y = (X - P.mean(0)) @ R.T + Q.mean(0)
    # shift the ligand rigidly along the bisector so the M-donor distance is r
    bis = unit(unit(d1) + unit(d2)); cur = np.linalg.norm(Y[D[0]])
    for _ in range(20):
        cur = np.linalg.norm(Y[D[0]]); Y = Y + (r - cur) * bis
    for i, a in enumerate(mol.GetAtoms()):
        if i not in drop: m.add(a.GetSymbol(), Y[i])

acacB = "CC1=CC(C)=[O+][B-](F)(F)O1"
m = Mol(); m.add("Al", [0, 0, 0])
for (i, j) in [(0, 2), (1, 4), (3, 5)]:
    chelate(m, acacB, {"O"}, O6[i], O6[j], 1.89)
out["Alacac3"] = m.xyz("Al(acac)3")

amdB = "CC1=[N+](C(C)C)[B-](F)(F)N1C(C)C"
m = Mol(); m.add("Al", [0, 0, 0])
bite = np.deg2rad(69)
d1 = [np.cos(bite / 2), np.sin(bite / 2), 0]; d2 = [np.cos(bite / 2), -np.sin(bite / 2), 0]
chelate(m, amdB, {"N"}, d1, d2, 1.93)
for sz in (1, -1):
    m.attach("[2H]CC", [0, 0, 0], [-0.6, 0, 0.8 * sz], 1.97)
out["AlAMDEt2"] = m.xyz("Al(iPrAMD)Et2")

# Me3Au(PMe3): square planar Au(III)
m = Mol(); m.add("Au", [0, 0, 0])
for d in ([1, 0, 0], [0, 1, 0], [0, -1, 0]):
    P = 2.06 * np.array(d, float); m.add("C", P); m.methyl(P, d)
m.attach("[2H][P+](C)(C)C", [0, 0, 0], [-1, 0, 0], 2.36)
out["Me3AuPMe3"] = m.xyz("Me3Au(PMe3)")

# Cu(NHC)(btsa): linear Cu(I); carbene from an imidazolium with marker H at C2
m = Mol(); m.add("Cu", [0, 0, 0])
m.attach("[2H]c1n(C(C)C)cc[n+]1C(C)C", [0, 0, 0], [0, 0, 1], 1.90)
m.attach("[2H]N([Si](C)(C)C)[Si](C)(C)C", [0, 0, 0], [0, 0, -1], 1.88)
out["CuNHC"] = m.xyz("Cu(iPr2-NHC)[N(SiMe3)2]")

# sanity: shortest non-bonded contacts
for k, v in out.items():
    L = v.split("\n")[2:]; el = [l.split()[0] for l in L]; X = np.array([[float(t) for t in l.split()[1:]] for l in L])
    D = np.linalg.norm(X[:, None] - X[None], axis=2) + np.eye(len(X)) * 9
    hh = [D[i, j] for i in range(len(X)) for j in range(i) if el[i] == "H" and el[j] == "H"]
    print(f"{k:10s} n={len(X):3d} min all={D.min():.2f} min H..H={min(hh) if hh else 0:.2f}")
import pathlib
out_path = pathlib.Path(__file__).resolve().parents[1] / "chapters" / "data" / "ligand-gallery.json"
json.dump(out, open(out_path, "w"), indent=0)
print("wrote", out_path)
