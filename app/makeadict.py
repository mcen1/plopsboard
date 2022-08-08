#!/bin/env python3
import mysql.connector
import os

def niceWMFormat(mystring):
  return mystring.replace('|',"<br/>").replace(" sox_","<br>sox_").replace(",",", ")

def getWMInfo(mydict):
  myresult={
  "GCD Linux":{"Total":0,"Well-managed":0},
  "HPUX Support":{"Total":0,"Well-managed":0},
  "Stores UNIX":{"Total":0,"Well-managed":0}
  }
  for item in mydict["data"]:
    for idx,field in enumerate(mydict["data"][item]):
      myosowner=mydict["data"][item][4]
      if idx==2:
        myresult[myosowner]["Total"]=myresult[myosowner]["Total"]+1
        if "well-managed" in field.lower():
          myresult[myosowner]["Well-managed"]=myresult[myosowner]["Well-managed"]+1
  return myresult

def getPatchInfo(mydict):
  myresult={
  "GCD Linux":{"Total": 0,"Total (in and out of scope)":0,"Patched":0,"Unpatched":0,"Automated":0,"Business out of scope":0,"Obsolete OS":0},
  "HPUX Support":{"Total": 0,"Total (in and out of scope)":0,"Patched":0,"Unpatched":0,"Automated":0,"Business out of scope":0,"Obsolete OS":0},
  "GCS":{"Total": 0,"Total (in and out of scope)":0,"Patched":0,"Unpatched":0,"Automated":0,"Business out of scope":0,"Obsolete OS":0},
  "Stores UNIX":{"Total": 0,"Total (in and out of scope)":0,"Patched":0,"Unpatched":0,"Automated":0,"Business out of scope":0,"Obsolete OS":0},
  }
  for item in mydict["data"]:
    for idx,field in enumerate(mydict["data"][item]):
      if idx==1:
        myosowner=field
      if field=="auto":
        myresult[myosowner]["Automated"]=myresult[myosowner]["Automated"]+1
      if idx==2:
        myresult[myosowner]["Total (in and out of scope)"]=myresult[myosowner]["Total (in and out of scope)"]+1
        if "fully" in field.lower():
          myresult[myosowner]["Patched"]=myresult[myosowner]["Patched"]+1
          myresult[myosowner]["Total"]=myresult[myosowner]["Total"]+1
        elif "BUSINESS OUT OF SCOPE" in field:
          myresult[myosowner]["Business out of scope"]=myresult[myosowner]["Business out of scope"]+1
        elif "OUT OF SCOPE: Obsolete OS." in field:
          myresult[myosowner]["Obsolete OS"]=myresult[myosowner]["Obsolete OS"]+1
        elif "OUT OF SCOPE:" in field:
          unknownitem=True
        else:
          myresult[myosowner]["Unpatched"]=myresult[myosowner]["Unpatched"]+1
          myresult[myosowner]["Total"]=myresult[myosowner]["Total"]+1
  return myresult

def lilquery(query,hostname,username,password,database):
  mydb = mysql.connector.connect(
    host=hostname,
    user=username,
    password=password,
    database=database,
  )

  mycursor = mydb.cursor()
  mycursor.execute(query)
  myresult = mycursor.fetchall()
  return myresult

def makeASOXDict(tablename,query,hostname,username,password,database,sanitizemethod):
  mydict={"headers":[],"data":{}}
  mydb = mysql.connector.connect(
    host=hostname,
    user=username,
    password=password,
    database=database,
  )
  compliantmsg="MA01 AND MA02 SOX CHECKS ARE COMPLIANT."
  mycursor = mydb.cursor()
  myresult=["name","status","osowner","appsol","auditscope"]
  for header in myresult:
    mydict['headers'].append(header)
  mycursor.execute("%s" % query)
  myresult = mycursor.fetchall()
  index=0
  for x in myresult:
    myname=x[0]
    status=x[1]
    osowner=x[2]
    appsol=x[3]
    auditscope=x[4]
    mystatus=""
    if myname not in mydict["data"]:
      mydict["data"][myname]={"status":"","osowner":osowner,"appsol":appsol,"auditscope":auditscope}
    if status.lower()=="well-managed" or "sox" not in status.lower():
      mydict["data"][myname]["status"]=compliantmsg
    else:
      for item in status.split("|"):
        item=item.lower()
        if "sox" in item.lower():
          #if "cannot retrieve sox facts" in item.lower() or (" sox: sox report facts missing or failing. " in item.lower()):
          if "cannot retrieve sox facts" in item.lower() or (item.lower()==' sox: cannot retrieve sox facts .') or (item.lower().strip()=="sox: sox report facts missing or failing. [-10]"):
            mystatus="CANNOT RETRIEVE SOX FACTS FOR SERVER. Error: '"+str(item)+"' SOX status is unknown."
            mydict["data"][myname]["status"]=mystatus
            break
          else:
            for soxfact in item.split("sox_"):
              factsplit=soxfact.lower().split("=")
              if "ma01" in factsplit[0] or "ma02" in factsplit[0]:
                if "=0" not in soxfact:
                  mystatus=mystatus+" "+soxfact.replace(","," , ")
            # if we've reached this point with an empty status, the only SOX
            # fact(s) that are failing are being filtered out, so adjust msg
            if mystatus=="":
              mystatus=compliantmsg
      mydict["data"][myname]["status"]=mystatus.replace("[-10]","").replace("custom_","").replace(","," , ")
  return mydict



def makeADict(tablename,query,hostname,username,password,database,sanitizemethod,passedheaders):
  mydict={"headers":[],"data":{}}
  mydb = mysql.connector.connect(
    host=hostname,
    user=username,
    password=password,
    database=database,
  )
  mycursor = mydb.cursor()
  if len(passedheaders)==0:
    mycursor.execute("SHOW COLUMNS FROM `%s`" % tablename)
    myresult = mycursor.fetchall()
    for header in myresult:
      mydict['headers'].append(header[0])
  else:
    mydict['headers']=passedheaders
  mycursor.execute("%s" % query)
  myresult = mycursor.fetchall()
  index=0
  for x in myresult:
    mydict["data"][index]=[]
    for y in x:
      if sanitizemethod==1:
        mydict["data"][index].append(niceWMFormat(str(y)))
      else:
        mydict["data"][index].append(str(y).replace(","," , "))
    index=index+1
  return mydict

def dumpCSV2(mydata):
  tosay=""
  for idx,row in enumerate(mydata["headers"]):
    comma=","
    if idx==len(mydata["headers"])-1:
      comma=""
    tosay=tosay+str(row)+comma
  tosay=tosay+"\n"
  for row in mydata["data"]:
    for idx,item in enumerate(mydata["data"][row]):
      comma=","
      if idx==len(mydata["data"][row])-1:
        comma=""
      tosay=tosay+item.replace("\r","").replace("\n","").replace("<br>","")+comma
    tosay=tosay+"\n"
  return tosay

def wmCSVDump(mydata):
  # specially formatted csv output as requested by a manager
  mystatus="Name,Application Solution,Score,Status,Profile,OS owner,CyberArk,Puppet,Active Directory,Patching,ITOP,Zabbix,Qualys,SOX,Obsolete\n"
  for item in mydata["data"]:
    name=mydata["data"][item][0]
    score=mydata["data"][item][1]
    bigstatus=str(mydata["data"][item][2]).replace("\r","").replace("\n","").replace('<br>','').replace(",","")
    profile=mydata["data"][item][3]
    osowner=mydata["data"][item][4]
    appsol=mydata["data"][item][5]
    cyberark="OK"
    puppet="OK"
    ad="OK"
    patching="OK"
    itop="OK"
    zabbix="OK"
    qualys="OK"
    sox="OK"
    obsolete="OK"
    appsol="OK"
    if "application" in bigstatus.lower():
      appsol="ERROR"
    if "cyberark" in bigstatus.lower():
      cyberark="ERROR"
    if "puppet" in bigstatus.lower():
      puppet="ERROR"
    if "active directory" in bigstatus.lower():
      ad="ERROR"
    if "patching" in bigstatus.lower():
      patching="ERROR"
    if "itop" in bigstatus.lower():
      itop="ERROR"
    if "zabbix" in bigstatus.lower():
      zabbix="ERROR"
    if "qualys" in bigstatus.lower():
      qualys="ERROR"
    if "sox" in bigstatus.lower():
      sox="ERROR"
    if "canonical" in bigstatus.lower():
      obsolete="ERROR"
    mystatus=mystatus+name+","+str(appsol).replace('[','').replace(']','').replace("'",'').replace(",",'')+","+str(score)+","+bigstatus.replace(","," ")+","+profile+","+osowner+","+cyberark+","+puppet+","+ad+","+patching+","+itop+","+zabbix+","+qualys+","+sox+","+obsolete+"\n"
  return mystatus



def dumpCSV(mydata):
  tosay=""
  for idx,row in enumerate(mydata["headers"]):
    comma=","
    if idx==len(mydata["headers"])-1:
      comma=""
    tosay=tosay+str(row)+comma
  tosay=tosay+"\n"
  for row in mydata["data"]:
    tosay=tosay+str(row)+","
    for idx,item in enumerate(mydata["data"][row]):
      comma=","
      if idx==len(mydata["data"][row])-1:
        comma=""
      tosay=tosay+str(mydata["data"][row][item]).replace("\r","").replace("\n","").replace("<br>","")+comma
    tosay=tosay+"\n"
  tosay=tosay
  return tosay

