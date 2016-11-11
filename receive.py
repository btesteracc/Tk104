#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import json
import datetime
import paho.mqtt.publish as mqtt
import re

import receiver_config as conf

data={
    "_type" : "location",
    "acc"   : 0,
    "alt"   : 0,
    "batt"  : 0,
    "cog"   : 0,
    "desc"  : "",
    "event" : "",
    "lat"   : 0.0,
    "lon"   : 0.0,
    "rad"   : 0,
    "t"     : "x",
    "tid"   : "bp",
    "tst"   : 0,
    "vacc"  : 0,
    "vel"   : 0,
    "p"     : 0
}
dateline=0
InFilename="/var/spool/gammu/inbox/"+sys.argv[1]
with open(InFilename,'r') as InFile:
    content=InFile.readlines()
InFile.close()
Devicename=sys.argv[1].split("_")[3]
conf.topic+=Devicename[1:]
if content[0].startswith("Last") and content[1].startswith("lat"):
    data["lat"]=float(content[1][4:])
    data["lon"]=float(content[2][4:])
    data["batt"]=int(content[-1][4:-2])
    data["desc"]=content[6]+content[3]
    dateline=7
    #checked i.O.

elif (content[0].startswith("lat")) and (content[0].find("lon")!=-1):
    grids=re.findall("([-+]?\d{1,2}[.]\d+)",content[0])
    data["lat"]=float(grids[0])
    data["lon"]=float(grids[1])
    data["batt"]=int(content[3][4:-2])
    dateline=2
    #checked i.O.

elif content[0].startswith("lat") and content[1].startswith("long"):
    data["lat"]=float(content[0][4:])
    data["lon"]=float(content[1][5:])
    data["batt"]=int(content[4][4:-2])
    dateline=3
    #checked i.O.

elif content[0].startswith("Lac"):
    dateline=1
    grids=re.findall("([-+]?\d{1,2}[.]\d+)\,([-+]?\d{1,2}[.]\d+)",content[4])
    data["lat"]=float(grids[0][0])
    data["lon"]=float(grids[0][1])
    data["desc"]=content[0]+content[4]
    #checked i.O.

if dateline!=0:
    format="T:%y/%m/%d %H:%M\n"
    try:
        date_obj=datetime.datetime.strptime(content[dateline],format)
    except ValueError:
        date_obj=datetime.datetime.now()
    data['tst'] = date_obj.strftime('%s')

if (data['tst']!=0) and (data['lat']!=0.0) and (data['lon']!=0.0):
    datastr=json.dumps(data)
    #Zum Testen auskommentiert am 01.11.2016
    # Ziel ist es mal den ganzen Tag Daten zum empfangen und diese nur lokal abzulegen

    #mqtt.single(conf.topic,payload=datastr,auth=conf.userid,port=conf.port,hostname=conf.hostname)

    #aus diesem Grund wird die Datei auch unter var/spool/gammu abglegt und nicht mehr im tmp Verzeichnis
    #with open("/tmp/receive.txt",'a') as OutFile:
    with open("/var/spool/gammu/"+Devicename[1:],'a') as OutFile:
        OutFile.write(datastr+'\n')
    OutFile.close()
    OutFile.close()
