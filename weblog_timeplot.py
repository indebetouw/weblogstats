import pdb
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
