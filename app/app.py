from flask import Flask
from flask import render_template
from flask import make_response
from flask import redirect 
from flask import request
from flask import jsonify
from makeadict import *
from decodeoidc import *
from rsotally import *
import os
TEMPLATE_DIR = os.path.abspath('./templates')
STATIC_DIR = os.path.abspath('./static')
app = Flask(__name__,template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=7070)

@app.route('/')
def index():
  clientheaders=decodeOIDC(request.headers)
  return render_template("index.html", **locals())

@app.route('/token')
def tokena():
  clientheaders=str(request.headers)
  return clientheaders

@app.route('/health')
def returnhealth():
  return {"status":"ok"}

@app.route('/uids')
def uidPage():
  myquery='SELECT id,CAST(uid AS INTEGER) FROM ad WHERE CAST(uid AS INTEGER)>0 ORDER BY CAST(uid AS INTEGER) ASC'
  alluids=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  myquery='SELECT CAST(uid AS INTEGER) FROM ad WHERE CAST(uid AS INTEGER)>0 ORDER BY CAST(uid AS INTEGER) ASC'
  occupieduids=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  occupiedlist=[]
  for item in occupieduids:
    occupiedlist.append(item[0])
  validuids=[]
  for i in range(3000, 6000):
    if i not in occupiedlist:
      validuids.append(i)
  validuids=str(validuids).replace("[","").replace("]","").replace(",","<br>")

  return render_template("uids.html", **locals())


#TODO: to achieve this
@app.route('/os_users')
def access_list():
  mydict=makeADict("os_users","select * from os_users",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],0,["Server","UserId","Full Name","Type","Shell","Found In","Last Password Change","Updated At"])
  return render_template("os_user.html", **locals())


@app.route('/os_users.csv')
def access_list_csv():
  mydict=makeADict("os_users","select * from os_users",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],0,["Server","UserId","Full Name","Type","Shell","Found In","Last Password Change","Updated At"])
  clientheaders=decodeOIDC(request.headers)
  mycsv=dumpCSV2(mydict)
  response = make_response(mycsv)
  cd = 'attachment; filename=os_users.csv'
  response.headers['Content-Disposition'] = cd
  response.mimetype='text/csv'
  return response


@app.route('/patching')
def patchingpage():
  mydict=makeADict("patching2","select server,osowner,status,appsol,rdsched,automated from patching2",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],0,["server","osowner","status","appsol","rdsched","automated"])
  myinfo=getPatchInfo(mydict)
  clientheaders=decodeOIDC(request.headers)
  myquery="select status from meta where tablename='patching2'"
  updatedate=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  return render_template("patching.html", **locals())

@app.route('/patching.csv')
def patchcsv():
  mydict=makeADict("patching2","select server,osowner,status,appsol,rdsched,automated from patching2",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],0,["server","osowner","status","appsol","rdsched","automated"])
  clientheaders=decodeOIDC(request.headers)
  mycsv=dumpCSV2(mydict)
  response = make_response(mycsv)
  cd = 'attachment; filename=patching.csv'
  response.headers['Content-Disposition'] = cd
  response.mimetype='text/csv'
  return response

@app.route('/sox2csv.csv',methods=['POST'])
def sox2csvgo():
#beepo
  data = request.form.to_dict(flat=False)
  tosay=",".join(data["Header"])
  tosay=tosay+"\n"
  cols=len(data["Header"][0].split(","))
  fields=len(data["String"][0].split(","))
  report=data["String"][0].split(",")
  rows=fields/(cols+1)
# 2,aomtrac.sherwin.com,MA01 AND MA02 SOX CHECKS ARE COMPLIANT.,GCD Linux,AOM Trac,[],3
  i=0
  p=0
  while i<rows:
    o=0
    p=p+1
    while o<cols:
      tosay=tosay+str(report[p]).replace("\n"," ").replace("\r"," ")+","
      o=o+1
      p=p+1
    tosay=tosay+"\n"
    i=i+1
  response = make_response(tosay)
  cd = 'attachment; filename=sox2csv.csv'
  response.headers['Content-Disposition'] = cd
  response.mimetype='text/csv'
  #print(f"data is: {data}")
  return response

@app.route('/sox')
def soxpage():
  mydict=makeASOXDict("wellmanaged3","select name,status,osowner,appsol,auditscope from wellmanaged3",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],1)
  clientheaders=decodeOIDC(request.headers)
  myquery="select status from meta where tablename='wellmanaged3'"
  updatedate=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  return render_template("sox.html", **locals())

@app.route('/sox.csv')
def soxcsv():
  mydict=makeASOXDict("wellmanaged3","select name,status,osowner,appsol from wellmanaged3",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],1)
  clientheaders=decodeOIDC(request.headers)
  mycsv=dumpCSV(mydict)
  response = make_response(mycsv)
  cd = 'attachment; filename=sox.csv'
  response.headers['Content-Disposition'] = cd 
  response.mimetype='text/csv'
  return response

# select name,provisioning,rating,datacenter,vcenter from clusters where (name like '%Lnx%' and (vcenter like '%swvcrw%' or vcenter like '%swvcak%')) order by vcenter,rating,datacenter,provisioning,name ;

@app.route('/clustercolors')
def clustercolorspage():
  mydict=makeADict("clusters","select name,provisioning,rating,datacenter,vcenter from clusters where (name like '%Lnx%' and (vcenter like '%swvcrw%' or vcenter like '%swvcak%')) order by vcenter,rating,datacenter,provisioning,name",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],0,["name","provisioning","rating","datacenter","vcenter"])
  clientheaders=decodeOIDC(request.headers)
  return render_template("clustercolors.html", **locals())

@app.route('/subnet')
def subnetpage():
  return render_template("subnet.html")

@app.route('/adsearch')
def adsearchpage():
  return render_template("adsearch.html")

@app.route('/searchip', methods = ['POST'])
def ipsearch():
  subnetsearch=request.form.get('term').replace(';','').replace('*','')
  myquery="select distinct * from networks where name like '%"+subnetsearch+"%'"
  mydict=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])

  return render_template("searchip.html", **locals())

@app.route('/searchad', methods = ['POST'])
def searchadpage():
  myterm=request.form.get('term').replace(';','').replace('*','')
  myquery="select * from ad where name like '%"+myterm+"%' or id like '%"+myterm+"%' or email like '%"+myterm+"%' or cc like '%"+myterm+"%' or uid like '%"+myterm+"%'"
  mydict=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  return render_template("searchad.html", **locals())

@app.route('/patcharchive', methods = ['GET'])
def getpatcharch():
  myquery="select * from patcharchive order by archivedate desc"
  myarchives=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  return render_template("patcharchive.html", **locals())


@app.route('/wm')
def wmpage():
  mydict=makeADict("wellmanaged3","select * from wellmanaged3",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],1,[])
  myinfo=getWMInfo(mydict)
  clientheaders=decodeOIDC(request.headers)
  myquery="select status from meta where tablename='wellmanaged3'"
  updatedate=lilquery(myquery, os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'])
  return render_template("wm.html", **locals())

@app.route('/wm.csv')
def wmcsv():
  mydict=makeADict("wellmanaged3","select * from wellmanaged3",os.environ['DB_HOSTNAME'],os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'],os.environ['DB_DATABASE'],1,[])
  clientheaders=decodeOIDC(request.headers)
  mycsv=wmCSVDump(mydict)
  response = make_response(mycsv)
  cd = 'attachment; filename=wm.csv'
  response.headers['Content-Disposition'] = cd
  response.mimetype='text/csv'
  return response

@app.route('/rso')
def rsopage():
  mydict=getRSO()
  clientheaders=decodeOIDC(request.headers)
  return render_template("rsotally.html", **locals())

