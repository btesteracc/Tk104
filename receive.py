#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import json
import datetime
import paho.mqtt.client as mqtt
import re
import logging
import ssl

import receiver_config as conf

#logging.basicConfig(filename="/var/log/gsmtrack_receiver.log", level=logging.DEBUG,
#format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%d-%m %H:%M")
logging.basicConfig(level=logging.INFO)


def get_date_from_line(dateline):
    if dateline!=0:
        format="T:%y/%m/%d %H:%M\n"
        try:
            date_obj=datetime.datetime.strptime(content[dateline],format)
        except ValueError:
            date_obj=datetime.datetime.now()
        return date_obj.strftime(format)
    

#InFilename="/var/spool/gammu/inbox/"+sys.argv[1]
def get_data():
    InFilename=sys.argv[1]
    with open(InFilename,'r') as InFile:
        content=InFile.readlines()
    InFile.close()
    devicename=sys.argv[1].split("_")[3]
    conf.topic+=devicename[1:]
    return content

def check_case_and_format_to_json(content):
    data = {
        "_type": "location",
        "alt": 0,
        "batt": 0,
        "desc": "",
        "event": "",
        "lat": 0.0,
        "lon": 0.0,
        "tid": "bp",
        "tst": 0
    }
    if content[0].startswith("Last") and content[1].startswith("lat"):
        data["lat"]=float(content[1][4:])
        data["lon"]=float(content[2][4:])
        data["batt"]=int(content[-1][4:-2])
        data["desc"]=content[6]+content[3]
        data["tst"]=get_date_from_line(7)
        #checked i.O.

    elif (content[0].startswith("lat")) and (content[0].find("lon")!=-1):
        grids=re.findall("([-+]?\d{1,2}[.]\d+)",content[0])
        data["lat"]=float(grids[0])
        data["lon"]=float(grids[1])
        data["batt"]=int(content[3][4:-3])
        data["tst"] = get_date_from_line(2)
        #checked i.O.

    elif content[0].startswith("lat") and content[1].startswith("long"):
        data["lat"]=float(content[0][4:])
        data["lon"]=float(content[1][5:])
        data["batt"]=int(content[4][4:-2])
        data["tst"] = get_date_from_line(3)
        #checked i.O.

    elif content[0].startswith("Lac"):
        grids=re.findall("([-+]?\d{1,2}[.]\d+)\,([-+]?\d{1,2}[.]\d+)",content[4])
        data["lat"]=float(grids[0][0])
        data["lon"]=float(grids[0][1])
        data["desc"]=content[0]+content[4]
        data["tst"] = get_date_from_line(1)
        #checked i.O.
    return data


def send_data(json_data):
    if (json_data['tst']!=0) and (json_data['lat']!=0.0) and (json_data['lon']!=0.0):
        datastr=json.dumps(json_data)
        logging.info(conf.topic)
        logging.info(datastr)
        mqttc = mqtt.Client()
        context = ssl.create_default_context()
        mqttc.tls_set_context(context)
        mqttc.connect(conf.hostname,port=conf.port)

        mqttc.publish(conf.topic,payload=datastr)
        mqttc.disconnect
        logging.info("Datensatz gesendet")
    else:
        logging.info("Fehler im Format")


content = get_data()
json_data = check_case_and_format_to_json(content)
send_data(json_data)

