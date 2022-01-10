import pdb
import pickle
import numpy as np

pickleroot="weblogstats"
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




#===================================================================
import matplotlib.pyplot as pl
pl.ion()
pl.clf()


colorbys=["freq",None]  # freq or random/MOUS
symbols=["array","nEB"]  # array or nEB

xs     =(dirtyDR,cleanDR),(dirtyDRperscan,cleanDRperscan),
xtit   ="SNR","SNR per EB per ant per scan" # for the plot
filetit="SNR","SNRperscan" # for the plotfile

xs     =(dirtyDR,cleanDR),
xtit   ="SNR",
filetit="SNR",

colorby="freq"
symbols=["nEB"]


for k,x in enumerate(xs):
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
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='x')
         z=np.where(nant>15)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='o')
         pl.plot(x[0].min(),rmsrat.min(),'kx',label='7m')
         pl.plot(x[0].min(),rmsrat.min(),'ko',label='12m')
   
      elif symbol=="nEB":
         z=np.where(neb==1)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='x')
         z=np.where(neb>1)
         pl.scatter(x[0][z],rmsrat[z],c=c[z],vmin=c.min(),vmax=c.max(),cmap='jet',marker='o')
         pl.plot(x[0].min(),rmsrat.min(),'kx',label='1EB')
         pl.plot(x[0].min(),rmsrat.min(),'ko',label='>1EB')
   
      if colorby:
         cb=pl.colorbar(label=colorby)
         cb.ax.set_yticklabels(["%3i"%x for x in cb.get_ticks()**(1/powr)])
   
   
      for i in range(len(results)):
         myplot,=pl.plot([x[0][i],x[1][i]],[rmsrat[i],rmsrat[i]],color=pl.cm.jet((c[i]-c.min())/(c.max()-c.min())))
   
         if rmsrat[i] >200 or dirtyDRperant[i]>3000:
            pl.text(x[0][i],rmsrat[i],target[i],color=myplot.get_color())
            # pl.text(x[0][i],rmsrat[i],freq[i],color=myplot.get_color())
   
   
      pl.ylabel('cont rms / theoretical cont rms')
      pl.xlabel(xtit[k])
      pl.xscale("log")
      pl.yscale("log")
      pl.legend(loc="best",prop={"size":8})
   
      if colorby:
         pl.savefig("cont_bm2021_rmsratio_"+filetit[k]+"_"+symbol+"_"+colorby+".png")
      else:
         pl.savefig("cont_bm2021_rmsratio_"+filetit[k]+"_"+symbol+".png")



#---------------------------------------------------------------------------------------



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

pl.xlabel("SNR/EB/ant/scan")
pl.ylabel("fraction of MOUS")
pl.xscale("log")

#pl.gca().grid(True,linestyle='-.')
pl.legend(loc="best",prop={"size":10})

pl.subplots_adjust(hspace=0.4)
pl.savefig("contSNR_perscan_distrib.png")















