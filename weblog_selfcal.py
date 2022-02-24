import pdb
import pickle
import numpy as np
from glob import glob
from datetime import date

plotroot="bm2021"
plotroot="allc7"

pickleroot=plotroot+"_stats"

saved=sorted(glob(pickleroot+".*pkl"))
today=date.today().strftime("%Y%m%d")

results=pickle.load(open(saved[-1],'rb'))



# better - these are using the findCont selection and effBW correction:
predrms=np.array([v['webpredrms'] for v in results.values()])
contBW=np.array([v['webcontBW'] for v in results.values()])

# these are the same - the achieved clean rms
contrms=np.array([v['webcontrms'] for v in results.values()])

# dirtyDR = dirty peak / ("final theoretical sens" = with fC selection and effBW correction)
dirtyDR=np.array([v['webdirtyDR'] for v in results.values()])
cleanpk=np.array([v['webcontpk'] for v in results.values()])
# use same sensitivity for clean DR - clean vs dirty DR thus only reflects increase in peak
cleanDR=cleanpk/predrms

# achieved vs theoretical noise
rmsrat =contrms/predrms


neb=np.array([v['nEB'] for v in results.values()])
nant=np.array([v['nant'] for v in results.values()])

freq=np.array([v['webfreq'] for v in results.values()])
beam=np.array([v['webbm'] for v in results.values()])

plversion=np.array([v['plversion'] for v in results.values()])
project=np.array([v['project'] for v in results.values()])

nscan=np.array([v['nscan'] for v in results.values()])
freq=np.array([v['webfreq'] for v in results.values()])
target=np.array([v['reptgt'] for v in results.values()])
npt=np.array([v['npt'] for v in results.values()])

dirtyDRperant =dirtyDR/np.sqrt(neb*(nant-3))
cleanDRperant =cleanDR/np.sqrt(neb*(nant-3))

dirtyDRperscan=dirtyDRperant/np.sqrt(nscan)
cleanDRperscan=cleanDRperant/np.sqrt(nscan)

cleanDRperEB =cleanDR/np.sqrt(neb)

mous=list(results.keys())



#===================================================================
import matplotlib.pyplot as pl
pl.ion()
pl.clf()


colorbys=["freq",None]  # freq or random/MOUS
symbols=["array","nEB"]  # array or nEB

xs     =(dirtyDR,cleanDR),(dirtyDRperscan,cleanDRperscan),
xtit   ="SNR","SNR per EB per ant per scan" # for the plot
filetit="SNR","SNRperscan" # for the plotfile

# xs     =(dirtyDR,cleanDR),
# xtit   ="SNR",
# filetit="SNR",

colorby="freq"
symbols=["nEB"]


for k,x in enumerate(xs):
   print("-----")
   for symbol in symbols:
      pl.clf()
   
      if colorby=="freq":
         powr=0.5
         c=freq**powr
      else:
         c=np.arange(n) # index or MOUS
         powr=1
   
      if symbol=="array":
         z=np.where(nant<15)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='x',s=3)
         z=np.where(nant>15)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='o',s=3)
         pl.plot(x[0].max()*2,rmsrat.min(),'kx',markersize=3,label='7m')
         pl.plot(x[0].max()*2,rmsrat.min(),'ko',markersize=3,label='12m')
   
      elif symbol=="nEB":
         z=np.where(neb==1)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='x',s=3)
         z=np.where(neb>1)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='o',s=3)
         pl.plot(x[0].max()*2,rmsrat.min(),'kx',markersize=3,label='1EB')
         pl.plot(x[0].max()*2,rmsrat.min(),'ko',markersize=3,label='>1EB')
   
      if colorby:
         cb=pl.colorbar(label=colorby)
         cb.ax.set_yticklabels(["%3i"%x for x in cb.get_ticks()**(1/powr)])
   
   
      for i in range(len(results)):
         myplot,=pl.plot([x[0][i],x[1][i]],[rmsrat[i],rmsrat[i]],color=pl.cm.jet((c[i]-c.min())/(c.max()-c.min())))
   
         # for BM, we don't have as many bright so dirtyDR>1000; 
         # for all C7 use 5000 here:
         if rmsrat[i] >200 or dirtyDRperant[i]>1000:
            if rmsrat[i]>500:
               pl.text(x[0][i],rmsrat[i],target[i],color=myplot.get_color())
            # pl.text(x[0][i],rmsrat[i],freq[i],color=myplot.get_color())
            # print("%6i %-5.2f %14s %24s %12s %1i %2i %3i"%(x[0][i],rmsrat[i],target[i],mous[i],project[i],neb[i],nscan[i],npt[i]))
            print("{:>6.0f} {:>6.2f} {:>14s} {:>24s} {:>12s} {:1} {:>2} {:>3}".format(x[0][i],rmsrat[i],target[i],mous[i],project[i],neb[i],nscan[i],npt[i]))
   
   
      pl.ylabel('cont rms / theoretical cont rms')
      pl.xlabel(xtit[k])
      pl.xlim(.1,1e5)
      pl.ylim(.5,1e5)
      pl.xscale("log")
      pl.yscale("log")
      pl.legend(loc="best",prop={"size":8})
   
      if colorby:
         pl.savefig(plotroot+"_cont_rmsratio_"+filetit[k]+"_"+symbol+"_"+colorby+".png")
      else:
         pl.savefig(plotroot+"_cont_rmsratio_"+filetit[k]+"_"+symbol+".png")



#-----------------------------------------------------------------------------


if False:

    pl.clf()
    pl.subplot(212)
    # >1EB and per-EB SNR>10 might be able to have some EB-EB at least checks 
    
    order=np.argsort(cleanDRperEB)[::-1]
    y=cleanDRperEB[order]
    neby=neb[order]
    ntot=len(y)
    x=np.arange(ntot)/ntot
    pl.plot(y,x,'k:',alpha=0.2)
    
    z=np.where(neby>1)[0]
    n=len(z)
    x=np.arange(n)/ntot
    
    z2=np.where(y[z]<10)[0].min()
    pl.plot([10,10],[0,x[z2]],"k:")
    pl.plot(y[z],x,label='>1EB; SNR>10: %2ipct'%(x[z2]*100))
    
    pl.ylim(0,0.6)
    pl.xlim(1,1e5)
    pl.xlabel("SNR/EB")
    pl.ylabel("fraction of MOUS")
    pl.xscale("log")
    pl.legend(loc="best",prop={"size":10})
    
    
    # perEB/per-ant SNR>1 may be amenable to single-gain self-cal
    # single fields with perEB/per-ant SNR>3 may be amenable to sub-scan self-cal
    
    pl.subplot(211)
    order=np.argsort(dirtyDRperscan)[::-1]
    y=dirtyDRperscan[order]
    npty=npt[order]
    projy=project[order]
    
    
    z=np.where(npty==1)[0]
    n=len(z)
    x=np.arange(n)/ntot
    z2=np.where(y[z]<3)[0].min()
    myplot,=pl.plot(y[z],x,label='1fld, SNR>3: %2ipct'%(x[z2]*100))
    pl.plot([3,3],[0,x[z2]],":",color=myplot.get_color())
    
    x=np.arange(ntot)/ntot
    z2=np.where(y<1)[0].min()
    myplot,=pl.plot(y,x,label='SNR>1: %2ipct'%(x[z2]*100))
    pl.plot([1,1],[0,x[z2]],":",color=myplot.get_color())
    
    pl.xlim(.1,1e4)
    pl.xlabel("SNR/EB/ant/scan")
    pl.ylabel("fraction of MOUS")
    pl.xscale("log")
    
    #pl.gca().grid(True,linestyle='-.')
    pl.legend(loc="best",prop={"size":10})
    
    pl.subplots_adjust(hspace=0.4)
    pl.savefig(plotroot+"_contSNR_perscan_distrib.png")

















#-----------------------------------------------------------------------------

pl.clf()
pl.plot(3e8/(freq*1e9)*206265/beam*.574, dirtyDRperscan,'.')
# TH approximates L80 to be .574 lam/d
pl.xscale("log")
pl.yscale("log")
pl.xlabel(r"0.574$\lambda/\theta$ [m]")
pl.ylabel("dirty SNR/ant/scan")
pl.plot(pl.xlim(),[1,1],'k')
pl.xlim(20,1e4)
pl.savefig(plotroot+"_contSNR_L80.png")
