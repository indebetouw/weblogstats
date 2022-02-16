import pickle
import numpy as np
from datetime import date
import matplotlib.pyplot as pl
from glob import glob
pl.ion()


plotroot="allc7"
#plotroot="bm2021"
pickleroot=plotroot+"_stats"

saved=sorted(glob(pickleroot+".*pkl"))
today=date.today().strftime("%Y%m%d")

results=pickle.load(open(saved[-1],'rb'))

n=len(results)
mit_field=np.zeros(n)
nfield=np.zeros(n)
mit_spw=np.zeros(n)
nspw=np.zeros(n)

for i,(k,v) in enumerate(results.items()):
    nfield[i]=v['nscience']
    if v['mit_field']=='default':
        mit_field[i]=nfield[i]
    else:
        mit_field[i]=len(v['mit_field'].split())

    nspw[i]=v['nspw']
    if v['mit_spw']=='default':
        mit_spw[i]=nspw[i]
    else:
        mit_spw[i]=len(v['mit_spw'].split())




mit_size=np.array([v['mitigatedprodsize'] for v in results.values()])
initialsize=np.array([v['initialprodsize'] for v in results.values()])
mitigated=np.array([v['mitigated'] for v in results.values()])
pl.clf()
pl.hist(np.log10(mit_size/(mit_field*mit_spw)),bins=20,range=[np.log10(.004),2])
pl.xlabel("log GB/src/spw")
pl.ylabel("number of mous")
pl.savefig("size_per_src_spw.png")


pl.clf()
z=np.where((mitigated==False)*(nspw>0))[0]
pl.plot((mit_field*mit_spw)[z],mit_size[z],'.',label="unmitigated")
pl.xlabel("src*spw")
pl.ylabel("product size [GB]")

mitprod=(mit_field<nfield)|(mit_spw<nspw)
z=np.where((mitigated==True)*(nspw>0)*(mitprod==False))[0]
myplot,=pl.plot((nfield*nspw)[z],initialsize[z],'.',label="mitigated (maxcube)")
for iz in z:
    pl.arrow((nfield*nspw)[iz],initialsize[iz],
             dx=(mit_field*mit_spw)[iz]-(nfield*nspw)[iz],
             dy=mit_size[iz]-initialsize[iz],width=.01,
             color=myplot.get_color(),alpha=0.2)

mitprod=(mit_field<nfield)|(mit_spw<nspw)
z=np.where((mitigated==True)*(nspw>0)*mitprod)[0]
myplot,=pl.plot((nfield*nspw)[z],initialsize[z],'.',label="mitigated (product)")
#pl.plot((nfield*nspw)[z],np.zeros(len(z))+600,'^',color=myplot.get_color())
for iz in z:
    #pl.plot([(mit_field*mit_spw)[iz],(nfield*nspw)[iz]],
    #        [mit_size[iz],initialsize[iz]],color=myplot.get_color(),alpha=0.2)
    pl.arrow((nfield*nspw)[iz],initialsize[iz],
             dx=(mit_field*mit_spw)[iz]-(nfield*nspw)[iz],
             dy=mit_size[iz]-initialsize[iz],width=.01,
             color=myplot.get_color(),alpha=0.2)
#myplot,=pl.plot((mit_field*mit_spw)[z],mit_size[z],'.',color='k')
pl.xscale("log")
pl.yscale("log")
pl.xlim(0.8,800)
pl.legend(loc="best",prop={"size":10})
