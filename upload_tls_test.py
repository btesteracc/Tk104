import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import ssl
userid ={'username':"bjoern",'password':"30212"}
topic="owntracks/GSM/GSM_TEST2"
hostname="mosquitto.bwithafocus.net"
port=8883
mqttc=mqtt.Client()
context=ssl.create_default_context()
mqttc.tls_set_context(context)
mqttc.username_pw_set("bjoern",password="30212")
datastr='{"_type":"location","tid":"21","acc":600,"batt":20,"conn":"w","doze":false,"lat":48.1396409,"lon":11.5127613,"tst":1491157063}'
mqttc.connect(hostname,port=port)
mqttc.publish(topic,payload=datastr)
mqttc.disconnect
