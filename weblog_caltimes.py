# this is to get the total runtimes of cal-only runs to a csv file
# so that can be used for more interesting analysis of image-only runs.

# this is mostly code also present in  weblogstats.py, 
# so maybe that could be consolidated somday.

import xml.etree.ElementTree as ET
from glob import glob
from bs4 import BeautifulSoup 
import pdb
from datetime import date
from astropy.table import Table
import numpy as np

# do we want to reload all information i.e. re-parse all weblog?
# if False, then it'll read from the csv to save time.
# but if you're adding features you want it to be True
reload=False


# get weblogs from disk area - only image and calimage have been untarred, 
# otherwise we'd have to filter out the cal ones.
rt='/lustre/naasc/sciops/comm/rindebet/pipeline/c7weblogs/calonly'

csvfile="calruntimes.tbl"
saved=sorted(glob(csvfile))

if len(saved)>0 and not reload:
   caltimes=Table.read(csvfile,format="ascii")
else:
   reload=True
   caltimes=Table(names=['mous','caltime'],dtype=['<U22',float])


runs=np.array(sorted(glob(rt+"uid_*weblog")))
z=np.where(np.array(['tmp' not in r for r in runs]))[0]
runs=runs[z]

# test
# runs=runs[0:5]


# don't re-parse directories already in the table.
if not reload:
   for mous in caltimes['mous']:
      z=np.where([mous in r for r in runs])[0]
      z.sort()
      for i,iz in enumerate(z):
         runs=np.delete(runs,iz-i)




def str2hrs(timestr):
   if "days" in timestr:
      x=timestr.split("days,")
   else:
      x=timestr.split("day,")
   if len(x)>1:
      thetime=int(x[0])*24.
   else:
      thetime=0.
   x=x[-1].split(":")
   return(thetime + int(x[0]) + int(x[1])/60 + int(x[2])/3600)




print(len(runs)," runs to process")
for run in runs:
    
   # get the mous, PID from the PPR

   PPRs=glob(run+'/html/PPR_uid*.xml')
   if len(PPRs)<1:
      print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
      print("ERROR: no PPR for ",run)
      continue

   PPR=PPRs[0]
   tree = ET.parse(PPR)
   root = tree.getroot()
   mous = root.find('ProjectStructure/OUSStatusRef').attrib['entityId']
   mous = mous.replace("/","_").replace(":","_")
   pid = root.find('ProjectSummary/ProposalCode').text

   if mous not in caltimes['mous']:
      print()
      print(run)

      # ---------------------------------------
      # PL version and total time from homepage

      index=glob(run+"/html/index.html")
      soup = BeautifulSoup(open(index[0]).read(), 'html.parser')
      for th in soup.findAll('th'):
         if "Pipeline Version" in th:
            plversion=th.findNext('td').text
         if "Execution Duration" in th:
            totaltimestr=th.findNext('td').text

      totaltime = str2hrs(totaltimestr)

      caltimes.add_row([mous,totaltime])

caltimes.write(csvfile,format="ascii",overwrite=True)
