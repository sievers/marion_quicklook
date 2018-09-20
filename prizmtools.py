import numpy
import scio
import glob
import time
import datetime

def read_field_many_fast(dirs,tag,dtype='float64',return_missing=False):
    ndir=len(dirs)
    all_dat=[None]*ndir
    missing=[]
    ndat=0
    for i in range(ndir):
        try:
            fname=dirs[i]+'/'+tag
            all_dat[i]=numpy.fromfile(fname,dtype=dtype)
            ndat=ndat+len(all_dat[i])
        except:
            missing.append(fname)
    if ndat>0:
        dat=numpy.zeros(ndat,dtype=dtype)
        ii=0
        for i in range(ndir):
            if not(all_dat[i] is None):
                nn=len(all_dat[i])
                if nn>0:
                    dat[ii:ii+nn]=all_dat[i]
                    ii+=nn
        if return_missing:
            return dat,missing
        else:
            return dat
    else:
        if return_missing:
            return None,missing
        else:
            return None
    
#============================================================

def read_pol_fast(dirs,tag):
    ndir=len(dirs)
    fnames=[None]*ndir
    for i in range(ndir):
        fnames[i]=dirs[i]+'/'+tag
    t0=time.time()
    all_dat=scio.read_files(fnames)
    t1=time.time()
    print 'read files in ',t1-t0
    ndat=0
    for dat in all_dat:
        if not(dat is None):
            ndat=ndat+dat.shape[0]
            nchan=dat.shape[1]

    if ndat>0:
        big_dat=numpy.zeros([ndat,nchan])
        ii=0
        for dat in all_dat:
            if not(dat is None):
                nn=dat.shape[0]
                big_dat[ii:(ii+nn),:]=dat
                ii=ii+nn
    else:
        print 'no files found in read_pol_fast.'
        big_dat=None
    return big_dat
    
