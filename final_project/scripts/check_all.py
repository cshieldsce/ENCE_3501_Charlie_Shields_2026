"""Check every vector of sim/ALU4_sim_all.raw against S = A + B (Sub=0) / S = B + ~A + 1 (Sub=1).

Run LTspice first:  ltspice -b sim/ALU4_sim_all.spi
Then:               python3 scripts/check_all.py sim/ALU4_sim_all.raw
Vector k (0..511) is applied at t = 20k ns: B = k[3:0], A = k[7:4], Sub = k[8].
"""
import bisect, sys
from ltspice_raw import read_raw

_, o = read_raw(sys.argv[1])
t = [x * 1e9 for x in o['time']]
outs = ['V(s0)', 'V(s1)', 'V(s2)', 'V(s3)', 'V(cout)']
bad = 0
for k in range(512):
    b, a, sub = k & 15, (k >> 4) & 15, k >> 8
    exp = a + b if sub == 0 else b + (15 - a) + 1
    i = bisect.bisect_left(t, 20 * k + 19)          # sample 1 ns before the next vector
    got = sum((o[n][i] > 2.5) << j for j, n in enumerate(outs))
    if got != exp:
        bad += 1
        print(f'FAIL sub={sub} A={a} B={b}: got {got:05b}, expected {exp:05b}')
print(f'{512 - bad}/512 vectors correct')
