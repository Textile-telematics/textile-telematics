#!/usr/bin/env python

from PIL import Image
import paho.mqtt.client as mqtt
import os
from datetime import datetime
import argparse
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("--host")
parser.add_argument("--port")
parser.add_argument("--username")
parser.add_argument("--password")
parser.add_argument("--test")
args=parser.parse_args()

mqtt_host = args.host or "slab.org"
mqtt_username = args.username or "tue"
mqtt_password = args.password
mqtt_port = 1883

is_test = args.test

testmode_prefix = "test/" if is_test else ""


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
path = Path("records")
path.mkdir(parents=True, exist_ok=True)

fn = f"{path}/{timestamp}.png"
width = 1320
height = 1
black = (0,0,0,255)
white = (255,255,255,255)
image = None

topic = f"{testmode_prefix}pattern"


def add_line(row):
    global image
    if os.path.isfile(fn):
        orig = Image.open(fn)
        height = orig.height + 1
        image = Image.new("RGB", (width, height), (255, 255, 255))
        image.paste(orig, (0,1))
        orig.close()
    else:
        height = 1
        image = Image.new("RGB", (width, height), (255, 255, 255))

    for i in range(0,min(width,len(row))):
        print(row)
        color = white if row[i] == '1' else black
        print(color)
        image.putpixel((i,0), color)
    image.save(fn)
    image.close()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    #client.subscribe("/tc2/footswitch")
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == topic:
        add_line(list(str(msg.payload)))

# mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# mqttc.on_connect = on_connect
# mqttc.on_message = on_message
# mqttc.username_pw_set(username=credentials.mqtt_username,password=credentials.mqtt_password)
# #mqttc.tls_set()
# mqttc.connect(credentials.mqtt_server, 1883, 60)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=mqtt_username, password=mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
run = True
while run:
    rc = mqttc.loop(timeout=1.0)
    if rc != 0:
        print("mqtt error")
        run = False
