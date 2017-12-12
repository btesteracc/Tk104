#!/usr/bin/env python
from __future__ import print_function
import sys
import json
import datetime
import re
import logging
import ssl
import paho.mqtt.client as mqtt
from python_utils import converters

import receiver_config as conf

#logging.basicConfig(filename="/var/log/gsmtrack_receiver.log", level=logging.DEBUG,
#format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%d-%m %H:%M")
logging.basicConfig(level=logging.INFO)


def get_date_from_line(dateline):
    if dateline != "":
        format_str = "T:%y/%m/%d %H:%M\n"
        try:
            #return datetime.datetime.strptime(dateline, format_str).isoformat()
            return datetime.datetime.strptime(dateline, format_str).timestamp()
        except ValueError:
            #return datetime.datetime.now().isoformat()
            return datetime.datetime.now().timestamp()

#InFilename="/var/spool/gammu/inbox/"+sys.argv[1]
def get_data():
    in_filename = sys.argv[1]
    with open(in_filename, 'r') as in_file:
        content = in_file.readlines()
    in_file.close()
    devicename = sys.argv[1].split("_")[3]
    conf.topic += devicename[1:]
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
        data["lat"] = converters.to_float(content[1], regexp=True)
        data["lon"] = converters.to_float(content[2], regexp=True)
        data["batt"] = converters.to_int(content[-1], regexp=True)
        data["desc"] = content[6]+content[3]
        data["tst"] = get_date_from_line(content[7])
        #checked i.O.

    elif (content[0].startswith("lat")) and (content[0].find("lon") != -1):
        grids = re.findall("([-+]?\d{1,2}[.]\d+)", content[0])
        data["lat"] = float(grids[0])
        data["lon"] = float(grids[1])
        data["batt"] = converters.to_int(content[3], regexp=True)
        data["tst"] = get_date_from_line(content[2])
        #checked i.O.

    elif content[0].startswith("lat") and content[1].startswith("long"):
        data["lat"] = converters.to_float(content[0], regexp=True)
        data["lon"] = converters.to_float(content[1], regexp=True)
        data["batt"] = converters.to_int(content[4], regexp=True)
        data["tst"] = get_date_from_line(content[3])
        #checked i.O.

    elif content[0].startswith("Lac"):
        grids = re.findall("([-+]?\d{1,2}[.]\d+)\,([-+]?\d{1,2}[.]\d+)", content[4])
        data["lat"] = float(grids[0][0])
        data["lon"] = float(grids[0][1])
        data["desc"] = content[0]+content[4]
        data["tst"] = get_date_from_line(content[1])
        #checked i.O.
    return data


def send_data(json_data):
    if (json_data['tst'] != 0) and (json_data['lat'] != 0.0) and (json_data['lon'] != 0.0):
        datastr = json.dumps(json_data)
        logging.info(conf.topic)
        logging.info(datastr)
        mqttc = mqtt.Client()
        context = ssl.create_default_context()
        mqttc.tls_set_context(context)
        mqttc.connect(conf.hostname, port=conf.port)
        mqttc.publish(conf.topic, payload=datastr)
        mqttc.disconnect()
        logging.info("Datensatz gesendet")
    else:
        logging.info("Fehler im Format")


CONTENT = get_data()
JSON_DATA = check_case_and_format_to_json(CONTENT)
send_data(JSON_DATA)
