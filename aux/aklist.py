from astropy.table import Table
import numpy as np
from glob import glob

# read amanda's table
t=Table.read("c7_12m.size_time.csv",format='ascii')
nvoxl=t['spw_nchan']*t['points_per_fov']*25
akmous=np.unique(t['member_ous_uid'].data)
akmous_filename=np.array([x.replace('/','_').replace(':','_') for x in akmous])


# weblogs on disk  (only image and calimage have been untarred in there, 
# otherwise we'd have to filter for that now)
rt='/lustre/naasc/sciops/comm/rindebet/pipeline/c7weblogs/weblogs/'

runs=np.array(sorted(glob(rt+"uid_*weblog")))
z=np.where(np.array(['tmp' not in r for r in runs]))[0]
runs=runs[z]

f=open("ak_missing.txt","wa")
print("missing weblogs:")
found=0
for x in akmous_filename:
    if np.max([x in y for y in runs])==True:
        found+=1
    else:
        f.write(x+"\n")
        print(x)
f.close()
