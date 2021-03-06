import pdb
from glob import glob
from datetime import date
import pickle,os
import numpy as np
import matplotlib.pyplot as pl
from astropy.table import Table
pl.ion()
pl.clf()

plotroot="allc7"
plotroot="bm2021"
pickleroot=plotroot+"_stats"

saved=sorted(glob(pickleroot+".*pkl"))
today=date.today().strftime("%Y%m%d")

results=pickle.load(open(saved[-1],'rb'))

csvfile="calruntimes.tbl"
# for the image-only runs, get cal runtimes
if os.path.exists(csvfile):
   caltimes=Table.read(csvfile,format="ascii")
   for i,m in enumerate(caltimes['mous']):
       if m in results.keys():
           if "calimage" not in results[m]['procedure']:
               print("adding cal time to "+m+(": %f -> %f"%(results[m]['totaltime'], results[m]['totaltime']+ caltimes['caltime'][i])))
               results[m]['totaltime'] += caltimes['caltime'][i]
               results[m]['procedure'] = "calimage"




n=len(results)
totaltime=np.zeros(n)
imgtime=np.zeros(n)
cubetime=np.zeros(n)
fctime=np.zeros(n)
cube0=np.zeros(n)
cube1=np.zeros(n)
prod0=np.zeros(n)
prod1=np.zeros(n)
mous=np.zeros(n,dtype='S22')

for i,(k,v) in enumerate(results.items()):
    totaltime[i]=v['totaltime']
    imgtime[i]=v['imgtime']
    cubetime[i]=v['cubetime']
    fctime[i]=v['fctime']
    cube0[i]=v['predcubesize']
    cube1[i]=v['mitigatedcubesize']
    prod0[i]=v['initialprodsize']
    prod1[i]=v['mitigatedprodsize']
    mous[i]=k


u=np.argsort(totaltime)
totaltime=totaltime[u]
imgtime=imgtime[u]
cubetime=cubetime[u]
fctime=fctime[u]
mous=mous[u]
cube0=cube0[u]
cube1=cube1[u]
prod0=prod0[u]
prod1=prod1[u]

# scatter plot
pl.plot(totaltime, imgtime/totaltime,'.',label="all images")
pl.plot(totaltime,cubetime/totaltime,'.',label="cubes")
pl.xscale("log")
pl.legend(loc="best",prop={"size":10})
pl.ylabel("fraction of PL time in makeimages")
pl.xlabel("PL runtime in hrs")










# mitigation

# pl.clf()
# pl.plot(prod1/prod0,cube1/cube0,'.')

# use productsize to increase runtimes:
ff=prod0/prod1
# use maxcube instead?
# ff=cube0/cube1
# better would be to match with Amanda's stats and do an un-mitigation 
mitigated=(prod0>prod1) | (cube0>cube1)




# ----------------------------------------------------
# time histogram
nbin=8
lo=np.floor(np.log10(np.min(totaltime)))
# override
lo=0. # 1hr
lo=-0.5

hi=np.ceil(np.log10(np.max(totaltime)))
# override to make room for unmitigated:
# nbin=20
# hi=4.3

lbins=np.arange(nbin+1)/nbin *(hi-lo) +lo 
bins=10.**lbins
xbins=10.**( 0.5*(lbins[1:]+lbins[:-1]) )
ct,b=np.histogram(totaltime,bins=bins)


imgfrac=np.zeros([nbin,3]) 
imgbin=np.zeros(nbin)
cubefrac=np.zeros([nbin,3]) 
cubebin=np.zeros(nbin)

imgbin_unmit=np.zeros(nbin)
cubebin_unmit=np.zeros(nbin)

for i in range(nbin):
    z=np.where( (totaltime>=bins[i])*(totaltime<bins[i+1]) )[0]
    if len(z)>0:
        imgfrac[i]=np.quantile((imgtime/totaltime)[z],[0.5,0.25,0.75])
        cubefrac[i]=np.quantile((cubetime/totaltime)[z],[0.5,0.25,0.75])
        imgbin[i]=np.nansum(imgtime[z])
        cubebin[i]=np.nansum(cubetime[z])

    z=np.where( ((totaltime*ff)>=bins[i])*((totaltime*ff)<bins[i+1]) )[0]
    if len(z)>0:
        imgbin_unmit[i]=np.nansum((imgtime*ff)[z])
        cubebin_unmit[i]=np.nansum((cubetime*ff)[z])

pl.clf()
# pl.subplot(212)
z=np.where(ct>0)[0]
y2err=np.array([imgfrac[:,0]-imgfrac[:,1],imgfrac[:,2]-imgfrac[:,0]])
pl.errorbar(xbins[z],imgfrac[z,0],yerr=y2err[:,z],color='darkorange',label="all imaging")
y2err=np.array([cubefrac[:,0]-cubefrac[:,1],cubefrac[:,2]-cubefrac[:,0]])
pl.errorbar(xbins[z]*1.03,cubefrac[z,0],yerr=y2err[:,z],color='g',label="cube only")
pl.xscale("log")
pl.ylabel("fraction of time imaging")
# pl.xlim(1,1e3)
pl.xlabel("PL runtime (hrs)")
#pl.ylim(0,1)
#pl.plot(totaltime,imgtime/totaltime,',',color='darkorange')
z=np.where(mitigated)
#pl.plot(totaltime[z],(imgtime/totaltime)[z],'.',color='r',label="mitigated")
pl.legend(loc="best",prop={"size":8})

z=np.where(mitigated * ((imgtime/totaltime)<0.3) )[0]
print(mous[z])

pl.savefig(plotroot+"_timeplot_imgfraction.png")


pl.clf()
# histogram of hours "ct"
# binhrs=np.concatenate([[0],ct*xbins])
# pl.step(bins,binhrs,label="total")
# imgplot,=pl.step(bins,np.concatenate([[0],imgbin]),label="sci img")
# cubeplot,=pl.step(bins,np.concatenate([[0],cubebin]),label="cube img")
# pl.xscale("log")
# pl.ylabel("hrs/bin = # mous * runtime")
# pl.ylabel("# mous")
# pl.xlabel("PL runtime (hrs)")
# pl.legend(loc="best",prop={"size":8})
# xlfull=pl.xlim()
# pl.xlim(1,1e3)

# histogram of number of mous
ict,b=np.histogram(imgtime,bins=bins)
pl.step(bins,np.concatenate([[0],ct]),label="total")
imgplot,=pl.step(bins,np.concatenate([[0],ict]),label="sci img")
# cubeplot,=pl.step(bins,np.concatenate([[0],cubebin]),label="cube img")
pl.xscale("log")
pl.ylabel("# mous")
pl.xlabel("PL runtime (hrs)")
pl.legend(loc="best",prop={"size":8})

pl.savefig(plotroot+"_timeplot_distrib.png")


# pl.subplot(211)
# pl.step(bins,np.concatenate([[0],imgbin_unmit]) ,linestyle="--",color=imgplot.get_color())
# pl.step(bins,np.concatenate([[0],cubebin_unmit]),linestyle="--",color=cubeplot.get_color())
# pl.xlim(xlfull)
# 
# pl.subplot(212)
# pl.xlim(xlfull)
# 
# pl.savefig(plotroot+_"timeplot_distrib_unmitigated.png")





# -------------------------------------
# cumulative distributions, unmitigated at constant img/total
if True:
    unit="days"

    pl.clf()
    if unit=="days":
        fact=24
    else:
        fact=1.
    totplot,=pl.plot(totaltime/fact,np.cumsum(totaltime/fact),label='total',linewidth=3)
    imgplot,=pl.plot(totaltime/fact,np.cumsum(imgtime/fact),label='imaging',linewidth=3)
    
    unmittotal=totaltime.copy()
    z=np.where(ff>1)[0]
    unmittotal[z]=(imgtime*ff)[z]/.7  # just use flat 0.7 fraction for large projects
    
    if unit=="days":
        pl.ylabel("processing days in C7")
        pl.xlabel("processing days per MOUS")
    else:
        pl.ylabel("hours in C7")
        pl.xlabel("hours per MOUS")
    pl.legend(loc="best",prop={"size":8})
    pl.savefig(plotroot+"_timeplot_cumulative.linear.png")

    u2=np.argsort(unmittotal)
    pl.plot(unmittotal[u2]/fact,np.cumsum(unmittotal[u2]/fact),label='unmitigated total',linestyle=":",color=totplot.get_color())
    pl.plot(unmittotal[u2]/fact,np.cumsum((imgtime*ff)[u2]/fact),label='unmitigated imaging',linestyle="--",color=imgplot.get_color())
    pl.savefig(plotroot+"_timeplot_cumulative.linear.unmitigated.png")
    

    
#    pl.xscale("log")
#    pl.yscale("log")
#    pl.savefig(plotroot+"_timeplot_cumulative.log.png")
