from glob import glob
import pdb
import numpy as np

rt='/lustre/naasc/sciops/comm/rindebet/pipeline/c7weblogs/weblogs/'
imgruns=np.array(sorted(glob(rt+"uid_*image.weblog")))
calruns=np.array(sorted(glob(rt+"*cal.weblog.tgz")))

calonly=np.zeros(len(calruns),dtype=bool)
for i,cr in enumerate(calruns):
    mous=cr.split("/")[-1].split(".")[1]
    print(mous)
    z=np.where([mous in ir for ir in imgruns])[0]
    if len(z)==0:
        calonly[i]=True

z=np.where(calonly)[0]
print(calruns[z])
