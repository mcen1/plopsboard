#!/bin/env python3
import csv
import mysql.connector as mariadb
import os

def getRSO():
  username=os.environ['DB_USERNAME']
  password=os.environ['DB_PASSWORD']
  mariadb_connection = mariadb.connect(host=os.environ['DB_HOSTNAME'],user=username, password=password, database=os.environ['DB_DATABASE'])
  cursor = mariadb_connection.cursor()
  cursor.execute("select * from historyofbadness order by date")
  myguys={}
  hanging=[]
  singlesites=["AND, KS","ARL, TX","BED, OH","BRT, ONT","CHI, IL","CIN, OH","COL, OH","CRS, MD","DAV, NC","ELK, IN","GRN ST, NC","GRM, ONT","GRV, OH","HOL, MI","HWD, IL","LAW, GA","MAT, IL","MEM, TN","MEN, WI","MSS, ONT","ONT, CA","POR, OR","ROC SW, IL","SNF, NC","SOH, IL"]
  for thing in cursor.fetchall():
    site=thing[0]
    date=thing[1]
    issue=thing[2]
    type=thing[3]
    if type=="r" and ("VM" in issue or "GATEWAY" in issue or ("ESX1" in issue and "ESX2" in issue) or ("ESX" in issue and site in singlesites)):
      if site not in myguys:
        myguys[site]=[]
      myguys[site].append(type+"_"+date)
      if site not in hanging:
        hanging.append(site)
    if type=="c":
      if site not in myguys:
        myguys[site]=[]
      myguys[site].append(type+"_"+date)
      if site in hanging:
        hanging.remove(site)


  mariadb_connection.close()
  myreport={}
  import datetime
  for thing in myguys:
    recording=False
    cumtotal=0
    for dater in myguys[thing]:
      if dater.startswith("r"):
        recording=True
        starttime=dater.replace("r_","")
      elif dater.startswith("c") and recording:
        if thing not in myreport:
          myreport[thing]={}
        recording=False
        endtime=dater.replace("c_","")
        indval=endtime[0:7]
        if indval not in myreport[thing]:
          myreport[thing][indval]={"total":0}
        d1 = datetime.datetime.strptime(starttime, '%Y/%m/%d %H:%M:%S')
        d2 = datetime.datetime.strptime(endtime, '%Y/%m/%d %H:%M:%S')
        diff = int(600+(d2 - d1).total_seconds())
        myreport[thing][indval]["total"]=myreport[thing][indval]["total"]+diff

  daterep={}
  for thing in myreport:
    for dateo in myreport[thing]:
      if dateo not in daterep:
        daterep[dateo]=[]
      daterep[dateo].append(thing+": "+str(round(myreport[thing][dateo]["total"]/60))+" minutes of outage")
  mylist=sorted(daterep,reverse=True)
  myret=(mylist,myreport)
  return myret

#myret=getRSO()

#print("myret1:"+str(myret[1]))
#for thing in  myret[0]:
#  print("Month: "+str(thing))
#  for dateo in myret[1]:
    #print("looking at: dateo:'"+dateo+"' thing:'"+thing+"'")
    #print(myret[1][dateo][thing])
#    try:
#      print(str(dateo)+": "+str(round(myret[1][dateo][thing]["total"]/60))+" minutes of outage")
#      print(myret[1][thing].split(":")[0]+"</td><td>"+myret[1][thing].split(":")[1]+"\n")
#    except:
#      pass

