#!/usr/bin/python3

# (c) 2024 Alex McLean and Pei-Ying Lin

# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# <http://www.gnu.org/licenses/>.

import paho.mqtt.client as mqtt
import argparse, json
from CATextile import CATextile
import numpy as np
import time



parser=argparse.ArgumentParser()
parser.add_argument("--host")
parser.add_argument("--port")
parser.add_argument("--username")
parser.add_argument("--password")
parser.add_argument("--rule")
parser.add_argument("--interval")
args=parser.parse_args()


interval = args.interval or 2.0   # seconds
last_call = time.monotonic()

mqtt_host = args.host or "slab.org"
mqtt_username = args.username or "tue"
mqtt_password = args.password
mqtt_port = 1883

subscribe_topics = ["test/weaving/draft/full","weaving/draft/full","test/ca/start","test/ca/stop","ca/start","ca/stop"]

## pattern variables
threading = []
tieup = []
treadling = []

mutate = False


cat = CATextile()
rule = args.rule or 110  #defualt favorite rule


## mqtt connect
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for topic in subscribe_topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    global mutate, tieup, threading, treadling
    topic = msg.topic
    data = msg.payload.decode()
    match topic:
        case "test/ca/start":
            mutate = True
        case "test/ca/stop":
            mutate = False
        case "ca/start":
            mutate = True
        case "ca/stop":
            mutate = False
        case "test/weaving/draft/full":
            data = json.loads(msg.payload)
            threading = data['threading']
            tieup = data['tieup']
            treadling = data['treadling']
            print(f"{topic}:{data}")
        case "weaving/draft/full":
            data = json.loads(msg.payload)
            threading = data['threading']
            tieup = data['tieup']
            treadling = data['treadling']
            print(f"{topic}:{data}")

def CAmutate(name, matrix):

    print(f"matrix:{matrix}")
    print("here!")
    new_matrix = np.array(matrix)
    new_matrix = cat.evolveMatrix(new_matrix, rule)
    print(f"cat_matrix:{new_matrix}")
    data = {"tieup": new_matrix.tolist(), "threading":threading, "treadling":treadling}
    payload_json = json.dumps(data)
    mqttc.publish("test/weaving/draft/full", payload_json) #only publish to the test/ channel for the moment


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=mqtt_username, password=mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

print("Waiting for data..")
run = True
while run:
    rc = mqttc.loop(timeout=0)
    if rc != 0:
        print("mqtt error")
        run = False
    # blocks for up to 1/20th of a second
    now = time.monotonic()
    if mutate:
        if now - last_call >= interval:
            print("mutate")
            #TODO: check if there's already a tieup available. If not, request for it.
            CAmutate("tieup",tieup)
            last_call = now


