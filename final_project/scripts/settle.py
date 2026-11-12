import sys, numpy as np
sys.path.insert(0, sys.argv[2]); from ltspice_raw import read_raw
_,o=read_raw(sys.argv[1]); t=np.asarray(o["time"])
o={k.lower():np.asarray(v) for k,v in o.items()}
sig=[o[f'v({n})'] for n in ['s0','s1','s2','s3','cout']]
ds=[]
for k in range(1,512):
    e=20e-9*k; m=(t>=e)&(t<e+19e-9); tt=t[m]; last=0
    for v in sig:
        b=v[m]>2.5; ch=np.nonzero(b[1:]!=b[:-1])[0]
        if len(ch): last=max(last,tt[ch[-1]+1]-e)
    ds.append(last)
ds=np.array(ds); i=ds.argmax(); print(f'worst {ds.max()*1e9:.2f} ns at vector {i+1}, median(of switching) {np.median(ds[ds>0])*1e9:.2f} ns')
