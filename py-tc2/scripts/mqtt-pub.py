#!/usr/bin/python3

import paho.mqtt.publish as publish
import json
import credentials

# publish.single("/pattern", "1001101010", hostname=credentials.mqtt_server, auth={"username":credentials.mqtt_username,"password":credentials.mqtt_password})
publish.single("/tc2/footswitch", "6", hostname=credentials.mqtt_server, auth={"username":credentials.mqtt_username,"password":credentials.mqtt_password})

