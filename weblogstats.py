import xml.etree.ElementTree as ET
from glob import glob
from bs4 import BeautifulSoup 
import pdb
from datetime import date
import pickle, re
import numpy as np
import sys
# sys.path.append("/home/casa/contrib/AIV/science/analysis_scripts/")
sys.path.append("/lustre/naasc/sciops/comm/rindebet/AIV/science/analysis_scripts/")
import analysisUtils as aU


# do we want to reload all information i.e. re-parse all weblog?
# if False, then it'll read from the pickle to save time.
# but if you're adding features you want it to be True
reload=False


# get weblogs from disk area - only image and calimage have been untarred, 
# otherwise we'd have to filter out the cal ones.
rt='/lustre/naasc/sciops/comm/rindebet/pipeline/c7weblogs/weblogs/'

pickleroot="weblogstats"
saved=sorted(glob(pickleroot+".*pkl"))
today=date.today().strftime("%Y%m%d")

if len(saved)>0 and not reload:
   results=pickle.load(open(saved[-1],'rb'))
else:
   reload=True
   results={}

runs=np.array(sorted(glob(rt+"uid_*weblog")))
z=np.where(np.array(['tmp' not in r for r in runs]))[0]
runs=runs[z]

# test
# runs=runs[0:45]


# don't re-parse directories already in the pickle.
if not reload:
   for mous in results.keys():
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

   if mous not in results.keys():
      print()
      print(run)

      nant = 0
      neb=0
      predtgt=''  # the rep tgt
      nscan = 0
      # stats for SNR (selfcal investigation)
      webpredrms=0
      webcontrms=0
      webcontpk=0
      webcontBW=0

      # stats for runtimes
      allimagetime=0.
      cubeimagetime=0.
      contimagetime=0.
      fctime=0.

      # neb from PPR
      neb=len(root.find('ProcessingRequests/ProcessingRequest/DataSet/SchedBlockSet/SchedBlockIdentifier').findall("AsdmIdentifier"))


      # ---------------------------------------
      # PL version and total time from homepage

      index=glob(run+"/html/index.html")
      soup = BeautifulSoup(open(index[0]).read(), 'html.parser')
      for th in soup.findAll('th'):
         if "Pipeline Version" in th:
            plversion=th.findNext('td').text
         if "Execution Duration" in th:
            totaltimestr=th.findNext('td').text
      if "CASA56" in plversion:
         plversion="C7"
      elif "2020" in plversion:
         plversion="2020"
      elif "2021" in plversion:
         plversion="2021"
      else:
         print("bad plversion ",plversion)
         pdb.set_trace()

      totaltime = str2hrs(totaltimestr)



      # ----------------------------------------------------
      # imaging stages:
      # what number each stage is depends on the version and recipe
      # TODO add renorm recipes here

      procedure=root.find('ProcessingRequests/ProcessingRequest/ProcessingProcedure/ProcedureTitle').text

      if procedure.split("_")[1]=='image':
         precheckstage="4"
         checksizestage="5"
         contimstage="12"
         cubeimstage="14"
      else:
         if plversion=="2020":
            precheckstage="24"
            checksizestage="25"
            contimstage="35"
            cubeimstage="37"
         elif plversion=="2021":
            precheckstage="24"
            checksizestage="25"
            contimstage="36"
            cubeimstage="38"
         else:
            precheckstage="22"
            checksizestage="23"
            contimstage="33"
            cubeimstage="35"

      imprecheck=glob(run+"/html/stage"+precheckstage+"/t2-4m_details.html")
      checksizepages=glob(run+"/html/stage"+checksizestage+"/t2-4m_details.html")
      contimpages=glob(run+"/html/stage"+contimstage+"/t2-4m_details.html")
      cubeimpages=glob(run+"/html/stage"+cubeimstage+"/t2-4m_details.html")



      # check the cube imaging to make sure we got that stage right

      soup = BeautifulSoup(open(cubeimpages[0]).read(), 'html.parser')
      
      # this stage is not the one we want.  so pooh.
      if not 'Tclean' in soup.div.h1.text.split()[1]:
         print("something wrong with stages")
         continue
      


      # ===========================================
      # get task runtimes from "by task" page
      
      index=glob(run+"/html/t1-4.html")
      soup = BeautifulSoup(open(index[0]).read(), 'html.parser')
      stages = soup.findAll("a",href=True)
      for s in stages:
         if "hif_makeimages" in s.text:
            timestr=s.findNext("td").findNext("td").findNext("td").text
            allimagetime += str2hrs(timestr)

            if cubeimstage in s.text:
               cubeimagetime = str2hrs(timestr)

            if contimstage in s.text:
               contimagetime = str2hrs(timestr)

         if "hif_findcont" in s.text:
            # this is an overestimate - need just time in tclean
            # timestr=s.findNext("td").findNext("td").findNext("td").text
            # allimagetime += str2hrs(timestr)
            # fctime = str2hrs(timestr)
            
            # instead, use aU
            stageno=s.text.split(".")[0]
            clog=run+"/html/stage"+stageno+"/casapy.log"
            fc_im_sec=0
            # aU.findImageSpwsFromCasalog(clog) doesn't do virtual spws
            # for that its better to use the image names:
            vspws=[]
            with open(clog,'r') as f:
               for line in f:
                  if re.search("Executing tclean",line):
                     fname=line.split("imagename='")[1].split("'")[0]
                     vspw=fname.split("spw")[1].split(".")[0]
                     vspws.append(int(vspw))
            for sspw in vspws: 
               fc_im_sec += aU.timeTclean(clog,spw=str(sspw),style="findcont",quiet=True)
            fctime = fc_im_sec/3600
            allimagetime += fctime

            
      # -----------------------------------------------
      # rep tgt from imageprecheck

      soup = BeautifulSoup(open(imprecheck[0]).read(), 'html.parser')
      predtgt = soup.h4.next_sibling.replace("\n","").split()[-1]



      # -----------------------------------------------------------
      # SNR, freq, rms for rep tgt only, from cont imaging

      soup = BeautifulSoup(open(contimpages[0]).read(), 'html.parser')
            
      x=soup.table.tbody.find_all('tr')
      offset=0
      # deal with warnings
      if x[0].has_attr('class'): 
         if 'warning' in x[0]['class'] or 'danger' in x[0]['class']:
            x=soup.find_all('table')[1].tbody.find_all('tr')
      
      #if x[0]['class']=='jumptarget': # multiple targets
      if x[0].has_attr('class'): 
         tblockitems=soup.ul.find_all('li') # target block is first <ul>
         jumpto=''
         for titem in tblockitems:
            tgt=titem.a.text.split()[0]
            if tgt==predtgt:
               jumpto=titem.a['href'][1:] # strip leading \#
         if len(jumpto)<1:
            print("ERROR: ",predtgt,' not found in aggcont weblog page')
            pdb.set_trace()
         for i in range(len(x)):
            if x[i].has_attr('class'):
               if x[i]['class'][0]=='jumptarget':
                  if x[i]['id']==jumpto:
                     offset=i+1
                     
      # TODO this will be different for C7PL and PL2020 poop - for C7PL its offset+3, and need to check the offsetting code too

      if plversion=="2020" or plversion=="2021":
         webfreq=float(x[offset+2].td.text.split()[0][:-3])

      else:  # C7PL
         webfreq=float(x[offset].findAll('td')[3].text.split()[0][:-3])
         offset=offset-2

      if 'theoretical' not in x[offset+5].th.text:
         print("something wrong with parsing",x[offset+5])
         pdb.set_trace()

      webpredrms=float(x[offset+5].td.text.split()[0])
      if x[offset+5].td.text.split()[1][0]=='m':
         webpredrms=webpredrms/1000 # mJy to Jy
      if x[offset+5].td.text.split()[1][0]=='u':
         webpredrms=webpredrms/1e6 # uJy to Jy

      webdirtyDR=float(x[offset+6].td.text.split()[3][:-2])

      webcontrms=float(x[offset+8].td.text.split()[0])
      if x[offset+8].td.text.split()[1][0]=='m':
         webcontrms=webcontrms/1000 # mJy to Jy
      if x[offset+8].td.text.split()[1][0]=='u':
         webcontrms=webcontrms/1e6 # uJy to Jy

      webcontpk=float(x[offset+9].td.text.split()[0]) # Jy
      if x[offset+9].td.text.split()[3][0]=='m':
         webcontpk=webcontpk/1000 # mJy to Jy
      if x[offset+9].td.text.split()[3][0]=='u':
         webcontpk=webcontpk/1e6 # uJy to Jy

      webcontBW=float(x[offset+11].td.text.split()[0]) # assume GHz
      
      



      # -------------------------------------------------------------------
      # be lazy and find #scans only in first EB
      # get nant while we're here too - if its >40, assume we're dealing with 12m

      session0=glob(run+"/html/session*")[0]
      ms0=glob(session0+"/uid*ms")[0]

      soup = BeautifulSoup(open(ms0+"/t2-2-3.html").read(), 'html.parser')
      nant = len(soup.table.tbody.find_all('tr'))

      # mosaic from fields details
      soup = BeautifulSoup(open(ms0+"/t2-2-1.html").read(), 'html.parser')
      sources = soup.table.findAll('tr')[2:]
      npt=-1
      for source in sources:
         sname=source.findAll('td')[1].text.strip("'")
         if predtgt in sname:
            npt=int(source.findAll('td')[7].text)
      if npt<=0:
         print("can't find npt for ",predtgt)
         pdb.set_trace()

      # nscans
      soup = BeautifulSoup(open(ms0+"/t2-2-6.html").read(), 'html.parser')
      sciscans=soup.table.tbody.find_all('tr')
      sciscantgt=[x.find_all('td')[5].text.strip("'").strip('"') for x in sciscans]
      z=np.where([predtgt in x for x in sciscantgt])[0]
      nscan=len(z)
      if nscan==0:
         print("can't find ",predtgt)
         pdb.set_trace()




      # -----------------------------------------------------------
      # checkproductsize info

      soup = BeautifulSoup(open(checksizepages[0]).read(), 'html.parser')

      mitigationstring=soup.p.text # first <p> should be the header - TODO if there are warnings, make sure there isn't a mess here.
      x=mitigationstring.split("\n")
      allowedcubesize   = float(x[1].split()[-2])
      allowedcubelimit  = float(x[3].split()[-2])
      predcubesize      = float(x[5].split()[-2])
      mitigatedcubesize = float(x[7].split()[-2])
      allowedprodsize   = float(x[9].split()[-2])
      initialprodsize   = float(x[11].split()[-2])
      mitigatedprodsize = float(x[15].split()[-2])

      x=soup.table.tbody.find_all('tr')
      # deal with warnings
      if x[0].has_attr('class'): 
         if 'warning' in x[0]['class'] or 'danger' in x[0]['class']:
            x=soup.find_all('table')[1].tbody.find_all('tr')
 
      # for AK this is x, a list of the mitigation parameters
      # [<td>default</td>,
      #  <td>default</td>,
      #  <td>default</td>,
      #  <td>default</td>,
      #  <td>default</td>]

      results[mous]={'project':pid,
                     'plversion':plversion,
                     'nant':nant,
                     'totaltime':totaltime,
                     'imgtime':allimagetime,
                     'cubetime':cubeimagetime,
                     'aggtime':contimagetime,
                     "fctime":fctime,
                     'nant':nant,
                     'nEB':neb,
                     'npt':npt, # for reptgt 
                     'nscan':nscan, # for reptgt 
                     'reptgt':predtgt,
                     'webpredrms':webpredrms,    # predicted agg cont rms
                     'webcontrms':webcontrms,    # achieved agg cont rms
                     'webcontBW':webcontBW,  
                     'webfreq':webfreq,  
                     'webdirtyDR':webdirtyDR,
                     'webcontpk':webcontpk,      # achieved agg cont pk
                     'allowedcubesize'  :allowedcubesize  , 
                     'allowedcubelimit' :allowedcubelimit , 
                     'predcubesize'     :predcubesize     , 
                     'mitigatedcubesize':mitigatedcubesize, 
                     'allowedprodsize'  :allowedprodsize  , 
                     'initialprodsize'  :initialprodsize  , 
                     'mitigatedprodsize':mitigatedprodsize 

      }


pickle.dump(results,open(pickleroot+"."+today+".pkl",'wb'))
