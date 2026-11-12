"""Generate ALU_cs.jelib: Charlie's Lab 5 cells + TRI + 4-bit add/sub ALU (one-row layout)."""
import math, re, sys

SRC = sys.argv[1]   # Lab5.jelib
OUT = sys.argv[2]   # ALU_cs.jelib
LIB = 'ALU_cs'
TS = '1794500000000'  # fixed creation/modify stamp (ms)


# --------------------------------------------------------------------------- helpers
class Cell:
    def __init__(self, name, view, tech):
        self.name, self.view, self.tech = name, view, tech
        self.lines, self.arcs, self.exports, self.n = [], [], [], 0
        self.lines.append('Ngeneric:Facet-Center|art@0||0|0||||AV')

    def uid(self, p):
        self.n += 1
        return f'{p}@{self.n}'

    def node(self, proto, x, y, w='', h='', orient='', extra='', name=None, pfx='n'):
        name = name or self.uid(pfx)
        self.lines.append(f'N{proto}|{name}||{fmt(x)}|{fmt(y)}|{w}|{h}|{orient}|{extra}')
        return name

    def inst(self, proto, x, y, name):
        self.lines.append(f'I{proto}|{name}||{fmt(x)}|{fmt(y)}|||D5G4;')
        return name

    def arc(self, proto, h, t, width='1', name=None, named=False, flags=None, size=2):
        # h, t = (node, port, x, y)
        name = name or self.uid('net')
        ang = angle(h, t)
        td = f'D5G{size};' if named else ''
        fl = flags if flags is not None else f'S{ang}'
        self.arcs.append(f'A{proto}|{name}|{td}|{width}|{fl}|{h[0]}|{h[1]}|{fmt(h[2])}|{fmt(h[3])}|{t[0]}|{t[1]}|{fmt(t[2])}|{fmt(t[3])}')

    def label(self, x, y, text, size=2):
        self.lines.append(f'Ngeneric:Invisible-Pin|{self.uid("txt")}||{fmt(x)}|{fmt(y)}|1|1|||ART_message(D5G{size};)S{text}')

    def export(self, name, node, port, ch, td='D5G2;'):
        self.exports.append(f'E{name}||{td}|{node}|{port}|{ch}')

    def text(self):
        hdr = f'C{self.name};1{{{self.view}}}||{self.tech}|{TS}|{TS}|'
        if self.view == 'ic':
            hdr += 'E'
        return '\n'.join([f'# Cell {self.name};1{{{self.view}}}', hdr] + self.lines + self.arcs + self.exports + ['X', ''])


def fmt(v):
    v = float(v)
    return str(int(v)) if v == int(v) else repr(v)


def angle(h, t):
    dx, dy = h[2] - t[2], h[3] - t[3]
    if dx == 0 and dy == 0:
        return 0
    return int(round(math.degrees(math.atan2(dy, dx)) % 360)) * 10


# --------------------------------------------------------------------------- TRI layout
def tri_lay():
    c = Cell('TRI', 'lay', 'mocmos')
    PY, NY, VDD, GND = 34, -32, 48, -46
    pc, nc = {}, {}
    for x in (8, 24, 40, 56, 72, 88, 104):
        pc[x] = c.node('Metal-1-P-Active-Con', x, PY, '', '1', pfx='pact')
        nc[x] = c.node('Metal-1-N-Active-Con', x, NY, '', '1', pfx='nact')
    pm, nm = {}, {}
    for x in (16, 48, 80, 96):
        pm[x] = c.node('P-Transistor', x, PY, '3', '', 'R', pfx='pmos')
        nm[x] = c.node('N-Transistor', x, NY, '3', '', 'R', pfx='nmos')
        for row, tr, con, y, typ in ((pm, pm[x], pc, PY, 'P'), (nm, nm[x], nc, NY, 'N')):
            c.arc(f'{typ}-Active', (tr, 'diff-top', x - 3.75, y), (con[x - 8], '', x - 8, y), width='3', flags='S0')
            c.arc(f'{typ}-Active', (tr, 'diff-bottom', x + 3.75, y), (con[x + 8], '', x + 8, y), width='3', flags='S1800')
    poly = lambda x, y: c.node('Metal-1-Polysilicon-1-Con', x, y, pfx='pcon')
    pD, pE, pA_p, pA_n, pB = poly(16, -20), poly(48, -20), poly(80, 12), poly(80, -12), poly(96, 0)
    P = 'Polysilicon-1'
    for x, con, cy in ((16, pD, -20), (48, pE, -20), (96, pB, 0)):
        c.arc(P, (pm[x], 'poly-left', x, PY - 5), (con, '', x, cy), width='')
        c.arc(P, (con, '', x, cy), (nm[x], 'poly-right', x, NY + 5), width='')
    c.arc(P, (pm[80], 'poly-left', 80, PY - 5), (pA_p, '', 80, 12), width='')
    c.arc(P, (pA_n, '', 80, -12), (nm[80], 'poly-right', 80, NY + 5), width='')
    via = lambda x, y: c.node('Metal-1-Metal-2-Con', x, y, pfx='via')
    v_db, v_db2, v_enb, v_enb2, v_en, v_en2, v_y = via(24, 0), via(90, 0), via(56, 12), via(76, 12), via(48, -12), via(76, -12), via(104, 20)
    M1, M2 = 'Metal-1', 'Metal-2'
    # inverter outputs (db at x=24, enb at x=56) and Y (x=104): vertical m1 from P contact to N contact
    for x, v, vy in ((24, v_db, 0), (56, v_enb, 12), (104, v_y, 20)):
        c.arc(M1, (pc[x], '', x, PY), (v, '', x, vy))
        c.arc(M1, (v, '', x, vy), (nc[x], '', x, NY))
    # gate wiring
    pinD = c.node('Metal-1-Pin', 4, -20, '1', '1', pfx='pin')
    c.arc(M1, (pinD, '', 4, -20), (pD, '', 16, -20))
    pinEn = c.node('Metal-2-Pin', 0, -12, '1', '1', pfx='pin')
    c.arc(M2, (pinEn, '', 0, -12), (v_en, '', 48, -12))
    c.arc(M1, (v_en, '', 48, -12), (pE, '', 48, -20))
    c.arc(M2, (v_en, '', 48, -12), (v_en2, '', 76, -12))
    c.arc(M1, (v_en2, '', 76, -12), (pA_n, '', 80, -12))
    c.arc(M2, (v_enb, '', 56, 12), (v_enb2, '', 76, 12))
    c.arc(M1, (v_enb2, '', 76, 12), (pA_p, '', 80, 12))
    c.arc(M2, (v_db, '', 24, 0), (v_db2, '', 90, 0))
    c.arc(M1, (v_db2, '', 90, 0), (pB, '', 96, 0))
    # rails
    well = c.node('Metal-1-N-Well-Con', 56, VDD, '7', '2', pfx='well')
    sub = c.node('Metal-1-P-Well-Con', 56, GND, '7', '2', pfx='substr')
    for y, mid, cons in ((VDD, well, pc), (GND, sub, nc)):
        pts = []
        for x in (0, 8, 40, 72, 112):
            pts.append((c.node('Metal-1-Pin', x, y, '3', '3', pfx='rpin'), x))
        seq = sorted(pts + [(mid, 56)], key=lambda p: p[1])
        for (a, xa), (b, xb) in zip(seq, seq[1:]):
            c.arc(M1, (a, '', xa, y), (b, '', xb, y), width='3')
        for nmn, x in pts:
            if x in (8, 40, 72):
                c.arc(M1, (cons[x], '', x, PY if y == VDD else NY), (nmn, '', x, y))
    c.node('N-Well-Node', 56, 46, '124', '38', pfx='plnode')
    c.node('P-Well-Node', 56, -44, '124', '38', pfx='plnode')
    c.export('D', pinD, '', 'I')
    c.export('En', pinEn, '', 'I')
    c.export('Y', v_y, '', 'O')
    c.export('gnd', sub, '', 'G')
    c.export('vdd', well, '', 'P')
    return c


# --------------------------------------------------------------------------- schematic helpers
TATTR = '|ATTR_length(D5G0.5;X-0.5;Y-1.5;)D2.0|ATTR_width(D5G1;X0.5;Y-1.5;)D6.0|SIM_spice_model(D5G1;Y-4.5;)S{m}'


def sch_tr(c, typ, x, y):
    if typ == 'P':
        n = c.node('Transistor', x, y, '', '', 'YR', '2' + TATTR.format(m='PMOS'), pfx='pmos')
        return n, {'g': (x - 1, y), 's': (x + 2, y + 2), 'd': (x + 2, y - 2)}
    n = c.node('Transistor', x, y, '', '', 'R', TATTR.format(m='NMOS'), pfx='nmos')
    return n, {'g': (x - 1, y), 's': (x + 2, y - 2), 'd': (x + 2, y + 2)}


def wire(c, a, b, name=None, size=2):
    c.arc('wire', a, b, width='', name=name, named=bool(name), flags=str(angle(a, b)), size=size)


def wpin(c, x, y):
    return c.node('Wire_Pin', x, y, pfx='pin')


def stub(c, port, dx, net, size=2):
    """named wire stub from a port (node,portname,x,y) to a new pin dx away"""
    p = wpin(c, port[2] + dx, port[3])
    wire(c, port, (p, '', port[2] + dx, port[3]), name=net, size=size)
    return p


def vdd(c, x, y):
    n = c.node('Power', x, y, pfx='pwr')
    return (n, '', x, y)


def gnd(c, x, y):
    n = c.node('Ground', x, y, pfx='gnd')
    return (n, '', x, y + 2)


def conn(c, x, y, net, direction, size=2):
    """Off-page connector exported as `net`. Returns the port the wire attaches to."""
    n = c.node('Off-Page', x, y, pfx='conn')
    if direction == 'I':   # arrow points right, wire leaves from the right (y) port
        c.export(net, n, 'a', 'I', f'D5G{size};X-2.5;')
        return (n, 'y', x + 2, y)
    c.export(net, n, 'y', 'O', f'D5G{size};X2.5;')
    return (n, 'a', x - 2, y)


# --------------------------------------------------------------------------- TRI schematic + icon
def tri_sch():
    c = Cell('TRI', 'sch', 'schematic')
    T, PT = {}, {}
    for k, typ, x, y in (('Pd', 'P', 0, 8), ('Nd', 'N', 0, -8), ('Pe', 'P', 14, 8), ('Ne', 'N', 14, -8),
                         ('Pa', 'P', 32, 14), ('Pb', 'P', 32, 6), ('Nb', 'N', 32, -6), ('Na', 'N', 32, -14)):
        T[k], PT[k] = sch_tr(c, typ, x, y)
    P = lambda k, t: (T[k], t, *PT[k][t])
    pin = lambda x, y: (wpin(c, x, y), '', x, y)
    # D input -> D inverter gates
    d_in = conn(c, -10, 0, 'D', 'I')
    pg = pin(-1, 0)
    wire(c, d_in, pg, 'D')
    wire(c, P('Pd', 'g'), pg)
    wire(c, pg, P('Nd', 'g'))
    # D inverter output = D_bar
    pdb = pin(2, 0)
    wire(c, P('Pd', 'd'), pdb)
    wire(c, pdb, P('Nd', 'd'), 'D_bar', size=1.5)
    # En input -> En inverter gates and the bottom nmos of the stack
    en_in = conn(c, -10, -20, 'En', 'I')
    p1, p2, p3, p4 = pin(13, -20), pin(13, 0), pin(28, -20), pin(28, -14)
    wire(c, en_in, p1, 'En')
    wire(c, p1, P('Ne', 'g'))
    wire(c, P('Pe', 'g'), p2)
    wire(c, p2, P('Ne', 'g'))
    wire(c, p1, p3)
    wire(c, p3, p4)
    wire(c, p4, P('Na', 'g'))
    # En inverter output = En_bar
    peb = pin(16, 0)
    wire(c, P('Pe', 'd'), peb)
    wire(c, peb, P('Ne', 'd'), 'En_bar', size=1.5)
    for k, (x, y) in (('Pd', (2, 13)), ('Pe', (16, 13)), ('Pa', (34, 19))):
        wire(c, P(k, 's'), vdd(c, x, y))
    for k, (x, y) in (('Nd', (2, -15)), ('Ne', (16, -15)), ('Na', (34, -21))):
        wire(c, P(k, 's'), gnd(c, x, y))
    # output stack
    wire(c, P('Pa', 'd'), P('Pb', 's'))
    py = pin(34, 0)
    wire(c, P('Pb', 'd'), py)
    wire(c, py, P('Nb', 'd'))
    wire(c, P('Nb', 's'), P('Na', 'd'))
    stub(c, P('Pa', 'g'), -5, 'En_bar', size=1.5)
    stub(c, P('Pb', 'g'), -5, 'D_bar', size=1.5)
    stub(c, P('Nb', 'g'), -5, 'D_bar', size=1.5)
    wire(c, py, conn(c, 44, 0, 'Y', 'O'), 'Y')
    c.label(1, -27, 'D inverter', 1.5)
    c.label(15, -27, 'En inverter', 1.5)
    c.label(33, -27, 'output stack', 1.5)
    c.label(16, 27, 'Tri-state buffer:  Y = D when En = 1,  Y floats (Hi-Z) when En = 0', 2)
    return c


def icon(name, ins, outs, label, w=None):
    """Simple box icon: inputs on the left, outputs on the right, 4 units apart."""
    c = Cell(name, 'ic', 'artwork')
    n = max(len(ins), len(outs))
    h = 4 * n + 2
    w = w or 12
    c.node('Box', 0, 0, str(w), str(h), pfx='art')
    c.label(0, 0, label, 2)
    ports = {}
    for side, names in ((-1, ins), (1, outs)):
        y0 = 2 * (len(names) - 1)
        for i, nm in enumerate(names):
            y = y0 - 4 * i
            xb, xw = side * (w / 2 + 3), side * w / 2
            b = c.node('schematic:Bus_Pin', xb, y, pfx='pin')
            p = c.node('schematic:Wire_Pin', xw, y, pfx='pin')
            c.arc('schematic:wire', (b, '', xb, y), (p, '', xw, y), width='', flags=str(angle((b, '', xb, y), (p, '', xw, y))))
            td = f'D5G1.5;X{-side * 2.5};' if side < 0 else f'D5G1.5;X{side * 2.5};'
            c.exports.append(f'E{nm}||{td}|{b}||{"I" if side < 0 else "O"}')
            ports[nm] = (xb, y)
    return c, ports


# icon port offsets of the existing Lab 5 icons (read from Lab5.jelib)
XOR_P = {'A': (2.5, -5), 'B': (2.5, -9), 'Y': (15.5, -7)}
FA_P = {'A': (-12, 4), 'B': (-12, 0), 'Cin': (-12, -4.5), 'Cout': (12, -2.5), 'S': (12, 3)}


# --------------------------------------------------------------------------- ALU4 schematic
def alu_sch(tri_p):
    """Bits left to right; data path drawn as real wires, Sub/En as labelled control stubs."""
    c = Cell('ALU4', 'sch', 'schematic')
    pin = lambda x, y: (wpin(c, x, y), '', x, y)
    prev_cout = None
    for i in range(4):
        X = 100 * i
        xo = c.inst('XOR;1{ic}', X - 40, 20, f'xor@{i}')
        fa = c.inst('FA;1{ic}', X, 0, f'fa@{i}')
        tr = c.inst('TRI;1{ic}', X + 30, 14, f'tri@{i}')
        XP = lambda p: (xo, p, X - 40 + XOR_P[p][0], 20 + XOR_P[p][1])
        FP = lambda p: (fa, p, X + FA_P[p][0], FA_P[p][1])
        TP = lambda p: (tr, p, X + 30 + tri_p[p][0], 14 + tri_p[p][1])
        # A_i -> XOR -> FA.A
        wire(c, conn(c, X - 48, 15, f'A{i}', 'I'), XP('A'), f'A{i}')
        stub(c, XP('B'), -5, 'Sub')
        j1, j2 = pin(X - 18, 13), pin(X - 18, 4)
        wire(c, XP('Y'), j1)
        wire(c, j1, j2)
        wire(c, j2, FP('A'))
        # B_i -> FA.B
        wire(c, conn(c, X - 24, 0, f'B{i}', 'I'), FP('B'), f'B{i}')
        # carry in
        if i == 0:
            stub(c, FP('Cin'), -5, 'Sub')
        else:
            k1, k2 = pin(X - 16, -2.5), pin(X - 16, -4.5)
            wire(c, prev_cout, k1, f'C{i}')
            wire(c, k1, k2)
            wire(c, k2, FP('Cin'))
        # sum -> tri-state -> output S_i
        s1, s2 = pin(X + 16, 3), pin(X + 16, 16)
        wire(c, FP('S'), s1)
        wire(c, s1, s2)
        wire(c, s2, TP('D'))
        stub(c, TP('En'), -4, 'En')
        wire(c, TP('Y'), conn(c, X + 46, 14, f'S{i}', 'O'), f'S{i}')
        prev_cout = FP('Cout')
        # captions
        c.label(X - 3, 31, f'bit {i}', 3)
        c.label(X - 31, 6.5, 'A xor Sub', 1.5)
        c.label(X, -10.5, 'full adder', 1.5)
        for txt, lx, ly in (('A', -4.5, 4), ('B', -4.5, 0), ('Cin', -3.5, -4.5), ('S', 4.5, 3), ('Cout', 3, -2.5)):
            c.label(X + lx, ly, txt, 1.2)
        c.label(X + 30, 7, 'tri-state', 1.5)
    wire(c, prev_cout, conn(c, 324, -2.5, 'Cout', 'O'), 'Cout')
    # control inputs
    wire(c, conn(c, -70, -18, 'Sub', 'I'), pin(-60, -18), 'Sub')
    wire(c, conn(c, -70, -24, 'En', 'I'), pin(-60, -24), 'En')
    c.label(150, 46, '4-bit Arithmetic Unit', 4)
    c.label(150, 40, 'Sub = 0:  S = A + B          Sub = 1:  S = B + ~A + 1  (= B - A)          En = 1: S driven,  En = 0: S is Hi-Z', 2)
    c.label(150, -20, 'C1 to C3 = ripple carries.   Sub also feeds the bit-0 carry-in (the +1).   Wires with the same name are connected.', 1.5)
    return c


# --------------------------------------------------------------------------- ALU4 layout (one row)
def alu_lay():
    c = Cell('ALU4', 'lay', 'mocmos')
    M1, M2 = 'Metal-1', 'Metal-2'
    via = lambda x, y: (c.node('Metal-1-Metal-2-Con', x, y, pfx='via'), '', x, y)
    pin1 = lambda x, y: (c.node('Metal-1-Pin', x, y, '1', '1', pfx='pin'), '', x, y)
    pin2 = lambda x, y: (c.node('Metal-2-Pin', x, y, '1', '1', pfx='pin'), '', x, y)
    YSUB, YEN, YBOT, YTOP, YCOUT, YT1 = -110, -118, -126, 110, 90, 72
    X0 = 40
    rails = {'vdd': [], 'gnd': []}
    subtaps, entaps = [], []
    prev_cout = None
    for i in range(4):
        X = X0 + i * 990
        Xx, Xf = X + 20, X + 272
        Xt = Xf + 590
        xa = c.inst('XOR;1{lay}', Xx, 1, f'XOR_bit{i}')
        fa = c.inst('FA;1{lay}', Xf, 0, f'FA_bit{i}')
        tr = c.inst('TRI;1{lay}', Xt, 1, f'TRI_bit{i}')
        rails['vdd'] += [(xa, 'vdd', Xx + 88, 49), (fa, 'vdd', Xf + 88, 49), (tr, 'vdd', Xt + 56, 49)]
        rails['gnd'] += [(xa, 'gnd', Xx + 88, -45), (fa, 'gnd', Xf + 88, -45), (tr, 'gnd', Xt + 56, -45)]
        # Sub -> XOR.B   (vertical m2 at X, from Sub bus up to y=-11)
        vb, vt = via(X, YSUB), via(X, -11)
        c.arc(M2, vb, vt)
        c.arc(M1, vt, (xa, 'B', Xx + 4, -11))
        subtaps.append(vb)
        # A_i -> XOR.A   (m2 from bottom pin up to y=-19)
        pa, va = pin2(X + 8, YBOT), via(X + 8, -19)
        c.arc(M2, pa, va)
        c.arc(M1, va, (xa, 'A', Xx + 12, -19))
        c.export(f'A{i}', pa[0], '', 'I')
        # XOR.Y -> FA.A  (up out of XOR, over at y=72, down in gap to y=-58)
        vy1, vy2 = via(Xx + 128, 28), via(Xx + 128, YT1)
        c.arc(M1, (xa, 'Y', Xx + 128, 23), vy1)
        c.arc(M2, vy1, vy2)
        vA1, vA2 = via(Xf - 44, YT1), via(Xf - 44, -58)
        c.arc(M1, vy2, vA1)
        c.arc(M2, vA1, vA2)
        c.arc(M1, vA2, (fa, 'A', Xf - 16, -58))
        # B_i -> FA.B
        pb, vB = pin2(Xf - 52, YBOT), via(Xf - 52, -66)
        c.arc(M2, pb, vB)
        c.arc(M1, vB, (fa, 'B', Xf - 24, -66))
        c.export(f'B{i}', pb[0], '', 'I')
        # carry in
        vC = via(Xf - 60, -74)
        c.arc(M1, vC, (fa, 'Cin', Xf - 32, -74))
        if i == 0:
            vCb = via(Xf - 60, YSUB)
            c.arc(M2, vCb, vC)
            subtaps.append(vCb)
        else:
            vCt = via(Xf - 60, YCOUT)
            c.arc(M2, vCt, vC)
            c.arc(M1, prev_cout, vCt)
        # FA.S -> TRI.D
        vS1, vS2 = via(Xf + 560, 82), via(Xf + 560, -19)
        c.arc(M1, (fa, 'S', Xf + 546, 82), vS1)
        c.arc(M2, vS1, vS2)
        c.arc(M1, vS2, (tr, 'D', Xt + 4, -19))
        # En -> TRI.En
        vE, pE = via(Xf + 568, YEN), pin2(Xf + 568, -11)
        c.arc(M2, vE, pE)
        c.arc(M2, pE, (tr, 'En', Xt, -11))
        entaps.append(vE)
        # TRI.Y -> output pin at top
        py = pin2(Xt + 104, YTOP)
        c.arc(M2, (tr, 'Y', Xt + 104, 21), py)
        c.export(f'S{i}', py[0], '', 'O')
        prev_cout = (fa, 'Cout', Xf + 546, YCOUT)
        last_x = Xt + 140
    # carry out of bit 3
    pc = pin1(last_x, YCOUT)
    c.arc(M1, prev_cout, pc)
    c.export('Cout', pc[0], '', 'O')
    # Sub / En buses along the bottom
    ps, pe = pin1(X0 - 30, YSUB), pin1(X0 - 30, YEN)
    taps = sorted(subtaps, key=lambda t: t[2])
    for a, b in zip([ps] + taps, taps):
        c.arc(M1, a, b)
    for a, b in zip([pe] + entaps, entaps):
        c.arc(M1, a, b)
    c.export('Sub', ps[0], '', 'I')
    c.export('En', pe[0], '', 'I')
    # rails: chain every cell's vdd/gnd port, exported at the left end
    for net, y, ch in (('vdd', 49, 'P'), ('gnd', -45, 'G')):
        p = c.node('Metal-1-Pin', X0 - 30, y, '3', '3', pfx='rail')
        seq = [(p, '', X0 - 30, y)] + rails[net]
        for a, b in zip(seq, seq[1:]):
            c.arc(M1, a, b, width='3')
        c.export(net, p, '', ch)
    return c


# --------------------------------------------------------------------------- sim schematics
def sim_cell(name, alu_p, card):
    c = Cell(name, 'sch', 'schematic')
    inst = c.inst('ALU4;1{ic}', 0, 0, 'alu@0')
    for nm, (px, py) in alu_p.items():
        stub(c, (inst, nm, px, py), -10 if px < 0 else 10, nm)
    items = ','.join(card)
    c.lines.append(f'Ngeneric:Invisible-Pin|card@0||0|-34|1|1|||SIM_spice_card(D5G1;)S[{items}]')
    return c


def card_common():
    return ['vdd vdd 0 DC 5', '.include C5_models.txt']


def card_demo():
    # 9 test vectors, 40 ns each, then En low for the last 40 ns.
    T = 40
    vecs = [  # (sub, A, B)
        (0, 3, 5), (0, 7, 9), (0, 15, 1), (0, 10, 10),
        (1, 3, 5), (1, 5, 3), (1, 6, 6), (1, 0, 9), (1, 15, 2)]
    vecs.append(vecs[-1])  # hold last vector while En goes low
    def pwl(bitvals):
        out = []
        for k, b in enumerate(bitvals):
            v = 5 * b
            out.append(f'{k * T + (0.2 if k else 0)}n {v}')
            out.append(f'{(k + 1) * T}n {v}')
        return 'PWL(' + ' '.join(out) + ')'
    card = card_common()
    for i in range(4):
        card.append(f'va{i} a{i} 0 ' + pwl([(a >> i) & 1 for s, a, b in vecs]))
        card.append(f'vb{i} b{i} 0 ' + pwl([(b >> i) & 1 for s, a, b in vecs]))
    card.append('vsub sub 0 ' + pwl([s for s, a, b in vecs]))
    card.append('ven en 0 ' + pwl([1] * (len(vecs) - 1) + [0]))
    card.append('vmid mid 0 DC 2.5')
    for i in range(4):
        card.append(f'rl{i} s{i} mid 100k')
    card.append('rlc cout mid 100k')
    card.append(f'.tran 0 {len(vecs) * T}n 0 50p')
    return card


def card_all():
    # exhaustive: B0..B3, A0..A3, Sub count in binary, 20 ns per vector, 512 vectors
    T = 20
    card = card_common()
    order = [f'b{i}' for i in range(4)] + [f'a{i}' for i in range(4)] + ['sub']
    for k, nm in enumerate(order):
        per = T * 2 ** (k + 1)
        card.append(f'v{nm} {nm} 0 PULSE(0 5 {per // 2 - 0.1}n 0.2n 0.2n {per // 2 - 0.2}n {per}n)')
    card.append('ven en 0 DC 5')
    card.append(f'.tran 0 {512 * T}n 0 100p')
    return card


# --------------------------------------------------------------------------- assemble
def main():
    src = open(SRC).read()
    head, _, body = src.partition('# Cell ')
    head = head.replace('HLab5|9.08', f'H{LIB}|9.08')
    blocks = re.split(r'(?m)^# Cell ', body)
    keep = []
    for b in blocks:
        cellname = b.split(';', 1)[0]
        if cellname in ('FA', 'NAND', 'NOT', 'XOR'):
            if b.startswith('FA;1{lay}'):
                b = b.replace('ES||D5G2;|pin@3||O', 'ES|Sum|D5G2;|pin@3||O')
            keep.append('# Cell ' + b)
    tic, tri_p = icon('TRI', ['D', 'En'], ['Y'], 'TRI', w=10)
    ains = [f'A{i}' for i in range(4)] + [f'B{i}' for i in range(4)] + ['Sub', 'En']
    aouts = [f'S{i}' for i in range(4)] + ['Cout']
    aic, alu_p = icon('ALU4', ains, aouts, 'ALU4', w=16)
    new = [aic, alu_lay(), alu_sch(tri_p),
           sim_cell('ALU4_sim', alu_p, card_demo()),
           sim_cell('ALU4_sim_all', alu_p, card_all()),
           tic, tri_lay(), tri_sch()]
    out = head + ''.join(keep).rstrip('\n') + '\n\n' + '\n'.join(c.text() for c in new)
    open(OUT, 'w').write(out)
    print('wrote', OUT)


main()
