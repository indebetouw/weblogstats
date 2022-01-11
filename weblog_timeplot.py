import pdb
from glob import glob
from datetime import date
import pickle
import numpy as np
import matplotlib.pyplot as pl
pl.ion()
pl.clf()

pickleroot="weblogstats"
saved=sorted(glob(pickleroot+".*pkl"))
today=date.today().strftime("%Y%m%d")

results=pickle.load(open(saved[-1],'rb'))



totaltime=np.array([v['totaltime'] for v in results.values()])
imgtime=np.array([v['imgtime'] for v in results.values()])
cubetime=np.array([v['cubetime'] for v in results.values()])
fctime=np.array([v['fctime'] for v in results.values()])

u=np.argsort(totaltime)
totaltime=totaltime[u]
imgtime=imgtime[u]
cubetime=cubetime[u]
fctime=fctime[u]

# scatter plot
pl.plot(totaltime, imgtime/totaltime,'.',label="all images")
pl.plot(totaltime,cubetime/totaltime,'.',label="cubes")
pl.xscale("log")
pl.legend(loc="best",prop={"size":10})
pl.ylabel("fraction of PL time in makeimages")
pl.xlabel("PL runtime in hrs")

# cumulative distributions
pl.clf()
pl.plot(totaltime,np.cumsum(totaltime),label='total')
pl.plot(totaltime,np.cumsum(totaltime-imgtime),label='not imaging')
pl.plot(totaltime,np.cumsum(imgtime),label='imaging')
pl.ylabel("hours in C7")
pl.xlabel("hours per MOUS")


# time distribution
nbin=15
lo=np.floor(np.log10(np.min(totaltime)))
# override
lo=0. # 1hr

hi=np.ceil(np.log10(np.max(totaltime)))
lbins=np.arange(nbin+1)/nbin *(hi-lo) +lo 
bins=10.**lbins
xbins=10.**( 0.5*(lbins[1:]+lbins[:-1]) )
ct,b=np.histogram(totaltime,bins=bins)


imgfrac=np.zeros([nbin,3]) 
imgbin=np.zeros(nbin)
cubefrac=np.zeros([nbin,3]) 
cubebin=np.zeros(nbin)
for i in range(nbin):
    z=np.where( (totaltime>=bins[i])*(totaltime<bins[i+1]) )[0]
    if len(z)>0:
        imgfrac[i]=np.quantile((imgtime/totaltime)[z],[0.5,0.25,0.75])
        cubefrac[i]=np.quantile((cubetime/totaltime)[z],[0.5,0.25,0.75])
        imgbin[i]=np.nansum(imgtime[z])
        cubebin[i]=np.nansum(cubetime[z])

pl.clf()
pl.subplot(211)
binhrs=np.concatenate([[0],ct*xbins])
pl.step(bins,binhrs,label="total")
imgplot,=pl.step(bins,np.concatenate([[0],imgbin]),label="sci img")
cubeplot,=pl.step(bins,np.concatenate([[0],cubebin]),label="cube img")
pl.xscale("log")
pl.ylabel("hrs/bin = # mous * runtime")
#pl.xlabel("PL runtime (hrs)")
pl.legend(loc="best",prop={"size":8})
xl=pl.xlim()


pl.subplot(212)
z=np.where(ct>0)[0]
y2err=np.array([imgfrac[:,0]-imgfrac[:,1],imgfrac[:,2]-imgfrac[:,0]])
pl.errorbar(xbins[z],imgfrac[z,0],yerr=y2err[:,z],color=imgplot.get_color())
y2err=np.array([cubefrac[:,0]-cubefrac[:,1],cubefrac[:,2]-cubefrac[:,0]])
pl.errorbar(xbins[z]*1.03,cubefrac[z,0],yerr=y2err[:,z],color=cubeplot.get_color())
pl.xscale("log")
pl.ylabel("fraction of time")
pl.xlim(xl)
pl.xlabel("PL runtime (hrs)")
