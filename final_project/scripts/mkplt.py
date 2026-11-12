import sys
V = "(' ',1,-0.5,1,5.5)"
N = "(' ',0,-1,2,17)"
N32 = "(' ',0,-2,4,34)"
A = "u(V(a0)-2.5)+2*u(V(a1)-2.5)+4*u(V(a2)-2.5)+8*u(V(a3)-2.5)"
B = "u(V(b0)-2.5)+2*u(V(b1)-2.5)+4*u(V(b2)-2.5)+8*u(V(b3)-2.5)"
SV = "u(V(s0)-2.5)+2*u(V(s1)-2.5)+4*u(V(s2)-2.5)+8*u(V(s3)-2.5)"


def plt(panes_top_down, x):
    panes = panes_top_down[::-1]  # LTspice lists panes bottom-up
    out = ['[Transient Analysis]', '{', '   Npanes: %d' % len(panes)]
    tid = 268959746
    for traces, y in panes:
        tr = ' '.join('{%d,0,"%s"}' % (tid + i, t) for i, t in enumerate(traces))
        tid += len(traces)
        lo, tick, hi = y.strip('()').split(',')[2:]
        out += ['   {', '      traces: %d %s' % (len(traces), tr), '      X: %s' % x,
                '      Y[0]: %s' % y, "      Y[1]: ('_',0,1e+308,0,-1e+308)",
                "      Volts: (' ',0,0,1,%s,%s,%s)" % (lo, tick, hi), '      Log: 0 0 0', '   }']
    out.append('}')
    return '\n'.join(out) + '\n'


A, B, SV = "V(a)", "V(b)", "V(s)"
demo = [(['V(sub)', 'V(en)'], V), ([A, B], N), ([SV], N), (['V(s3)'], V), (['V(s2)'], V),
        (['V(s1)'], V), (['V(s0)'], V), (['V(cout)'], V)]
xd = "('n',0,0,4e-08,4e-07)"
allv = [(['V(sub)'], V), ([A, B], N), ([SV], N), (['V(cout)'], V)]
xa = "('µ',0,0,1e-06,1.024e-05)"
worst = [(['V(b0)', 'V(s0)', 'V(s1)', 'V(s2)', 'V(s3)', 'V(cout)'], V)]
xw = "('n',0,0,5e-10,5e-09)"
d = sys.argv[1]
for n in ['ALU4_sim', 'ALU4_lay_sim']:
    open(f'{d}/{n}.plt', 'w').write(plt(demo, xd))
for n in ['ALU4_sim_all', 'ALU4_lay_sim_all']:
    open(f'{d}/{n}.plt', 'w', encoding='latin-1').write(plt(allv, xa))
for n in ['ALU4_worst', 'ALU4_lay_worst']:
    open(f'{d}/{n}.plt', 'w').write(plt(worst, xw))
