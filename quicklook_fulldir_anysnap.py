import numpy
from matplotlib import pyplot as plt
import sys
import os
import glob
import prizmtools
import argparse



if __name__=='__main__':
    parser=argparse.ArgumentParser()

    #parser.add_argument('dir','Root directory containing data to be plotted')
    parser.add_argument('dir',help='Directory containing data.')
    parser.add_argument('-P','--prizm',default=0,action='count',help='Default to PRIZM data')
    parser.add_argument('-p','--pols',default='0 1 2 3',help='Polarizations to look at (quote it you want more than one, e.g. --pols "1 2")')
    parser.add_argument('-F','--numax',type=float,default=125.0,help='Maximum frequency in the data')
    parser.add_argument('-o','--outdir',default='./',help='Directory to place plots in')
    parser.add_argument('-D','--makedir',action='count',default=0,help='Make the output directory if it doesn\'t exist')
    parser.add_argument('-C','--add_ctime',action='count',default=0,help='Make the output directory if it doesn\'t exist')
    parser.add_argument('-v','--vmin',type=float,default=4.5,help='Minimum amplitude in colorscale')
    parser.add_argument('-V','--vmax',type=float,default=8.5,help='Maximum amplitude in colorscale')
    args=parser.parse_args()


    prizm=args.prizm>0
        
    pols=numpy.fromstring(args.pols,dtype='int',sep=' ')
    pols.sort()
    print 'pols is now ',pols
    if prizm:
        if pols.max()>1:
            print 'cutting requested pols to max of 1 since you said this is PRIZM data.'
            pols=pols[pols<2]
    

    vmin=args.vmin
    vmax=args.vmax

    #assert(1==0)
    #mydir='/Users/sievers/shisa/data/marion_2018/data_singlesnap/15341/'
    mydir=args.dir
    print mydir
    

        

    outdir=args.outdir
    if args.add_ctime>0:
        tailtag=os.path.basename(os.path.normpath(mydir))
        outdir=outdir+'/'+tailtag
    if args.makedir>0:
        if os.path.isdir(outdir):
            print 'outdir exists'
        else:
            print 'making directory ',outdir
            os.makedirs(outdir)
        
    numax=args.numax
    if prizm:
        if (numax!=250.):
            print 'setting default prizm max frequency to 250'
            numax=250.

    tags=mydir.split('/')
    if len(tags[-1])>0:
        frag=tags[-1]
    else:
        frag=tags[-2]

        
    print 'my arg is ',mydir
    fnames=glob.glob(mydir+'/'+frag+'*[0-9]')
    fnames.sort()
    print 'len(fnames) is ',len(fnames)

    for pol in pols:
        if prizm:
            outtag='pol'+repr(pol)
        else:
            outtag='pol'+repr(pol)+repr(pol)
        tag=outtag+'.scio'
        print 'tag is ',outtag

        dat=prizmtools.read_pol_fast(fnames,tag)
        nchan=dat.shape[1]
        dnu=numax/1.0/nchan
        nu=numpy.arange(nchan)*dnu+0.5*dnu #get frequency bin centers
        plt.clf()
        myext=numpy.asarray([0,numax,dat.shape[0],0])
        plt.imshow(numpy.log10(dat),vmin=vmin,vmax=vmax,extent=myext);
        plt.colorbar()
        plt.axis('auto')
        plt.axis('tight')
        plt.title('Amplitude, ' + outtag)
        outname=outdir+'/'+outtag+'.png'
        print 'outname is',outname
        plt.savefig(outname)
    for i in range(len(pols)):
        for j in range(i+1,len(pols)):
            if prizm:
                outtag='cross_'
                tag=outtag+'real.scio'
                dat_r=prizmtools.read_pol_fast(fnames,tag)
                tag=outtag+'imag.scio'
                dat_i=prizmtools.read_pol_fast(fnames,tag)
            else:
                outtag='pol'+repr(pols[i])+repr(pols[j])
                print 'going to do cross spectra on ',outtag
                tag=outtag+'r.scio'
                dat_r=prizmtools.read_pol_fast(fnames,tag)
                tag=outtag+'i.scio'
                dat_i=prizmtools.read_pol_fast(fnames,tag)
            amp=numpy.sqrt(dat_r**2+dat_i**2)
            phase=numpy.arctan2(dat_r,dat_i)
            phase[phase<0]=phase[phase<0]+2*numpy.pi
            plt.clf();
            plt.imshow(phase,vmin=0,vmax=2*numpy.pi,extent=myext)
            plt.axis('auto')
            plt.axis('tight')
            plt.colorbar()
            plt.title('Phase, ' + outtag)
            outname=outdir+'/'+outtag+'_phase.png'
            plt.savefig(outname)
            
            plt.clf();
            plt.imshow(numpy.log10(amp),vmin=vmin,vmax=vmax,extent=myext);
            plt.axis('auto')
            plt.axis('tight')
            plt.colorbar()
            plt.title('Amplitude, ' + outtag)
            outname=outdir+'/'+outtag+'_amp.png'
            plt.savefig(outname)
            



    if prizm:
        time_sys_start=prizmtools.read_field_many_fast(fnames,'time_start.raw')
    else:
        time_sys_start=prizmtools.read_field_many_fast(fnames,'time_sys_start.raw')
        time_rtc_start=prizmtools.read_field_many_fast(fnames,'time_rtc_start.raw')
        #time_rtc_start=time_rtc_start-time_rtc_start[0]
        time_rtc_start=time_rtc_start/1000.

    t0=time_sys_start[0]
    time_sys_start=time_sys_start-t0


    plt.clf()
    plt.plot(time_sys_start)
    if not(prizm):
        time_rtc_start=time_rtc_start-t0
        plt.plot(time_rtc_start)
    plt.xlabel('Time since '+repr(t0))
    plt.title('Observing Time of Spectra')
    plt.savefig(outdir+'/start_times.png')


    fpga_temp=prizmtools.read_field_many_fast(fnames,'fpga_temp.raw')
    print 'fpga_temp shape is ',fpga_temp.shape
    plt.clf();
    if prizm:
        plt.plot(time_sys_start,fpga_temp,'*')
    else:
        plt.plot(time_rtc_start,fpga_temp,'*')
    plt.title('FPGA Temperature')
    plt.xlabel('Time since '+repr(t0))
    plt.savefig(outdir+'/fpga_temp.png')

    if prizm:
        overflow1=prizmtools.read_field_many_fast(fnames,'fft_of_cnt.raw')    
    else:
        overflow1=prizmtools.read_field_many_fast(fnames,'pfb0_fft_of.raw')    
        overflow2=prizmtools.read_field_many_fast(fnames,'pfb1_fft_of.raw')    


    plt.ion();
    plt.clf();
    plt.plot(overflow1,'*')
    if prizm:
        plt.legend(['FFT Overflow'])
    else:
        plt.plot(overflow2,'rx')
        plt.legend(['pfb0 overflow','pfb1 overflow'])
    plt.savefig(outdir+'/overflows.png')
