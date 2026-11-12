import struct,sys,re
def read_raw(path):
    b=open(path,'rb').read()
    # header utf-16le until "Binary:\n"
    marker='Binary:\n'.encode('utf-16-le')
    i=b.find(marker); hdr=b[:i].decode('utf-16-le'); data=b[i+len(marker):]
    nv=int(re.search(r'No\. Variables:\s*(\d+)',hdr).group(1)); npnt=int(re.search(r'No\. Points:\s*(\d+)',hdr).group(1))
    names=re.findall(r'^\t(\d+)\t(\S+)\t',hdr,re.M); names=[n for _,n in names]
    flags=re.search(r'Flags:\s*(.*)',hdr).group(1)
    out={n:[] for n in names}
    rec=8+4*(nv-1)
    if len(data)<rec*npnt: rec=8*nv  # double
    for k in range(npnt):
        off=k*rec
        if rec==8*nv: vals=struct.unpack_from('<%dd'%nv,data,off)
        else:
            t=struct.unpack_from('<d',data,off)[0]; rest=struct.unpack_from('<%df'%(nv-1),data,off+8); vals=(t,)+rest
        for n,v in zip(names,vals): out[n].append(v)
    out['time']=[abs(x) for x in out[names[0]]]
    return hdr,out
if __name__=='__main__':
    hdr,o=read_raw(sys.argv[1]); print(hdr[:600]); print(list(o)[:40], len(o['time']))
