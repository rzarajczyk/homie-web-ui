import json
import logging
import os
import shutil
from logging import config as logging_config

import paho.mqtt.client as mqtt
import yaml

from devices import Devices
from homietree import HomieTree
from server import start_server, JsonGet, JsonPost, Redirect, StaticResources

########################################################################################################################
# logging configuration

with open("logging.yaml", 'r') as f:
    config = yaml.full_load(f)
    logging_config.dictConfig(config)

LOGGER = logging.getLogger("main")
LOGGER.info("Starting application!")

########################################################################################################################
# application configuration

with open('config/homie-web-ui.yaml', 'r') as f:
    config = yaml.full_load(f)

    MQTT_HOST = config['mqtt']['host']
    MQTT_PORT = config['mqtt']['port']
    MQTT_USER = config['mqtt']['user']
    MQTT_PASS = config['mqtt']['password']

    DEVICES_CONFIG = config['devices']

    SUBDEVICES = config['subdevices']

########################################################################################################################

tree = HomieTree()


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("homie/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    LOGGER.info("Received event: %-70s | %s" % (topic, payload))
    tree.accept_message(topic, payload)


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT)


def list_devices(params):
    # tree.tree().debug('')
    devices = Devices(tree, SUBDEVICES)
    devices.enrich(DEVICES_CONFIG)
    return devices.to_json()


def set_property(params, payload):
    payload_json = json.loads(payload)
    topic = "homie/%s/set" % payload_json['path'].replace('.', '/')
    value = payload_json['value']

    if value is False:
        value = "false"
    elif value is True:
        value = "true"

    LOGGER.info("PUBLISHING:     %-70s | %s" % (topic, value))
    client.publish(topic, value)


client.loop_start()

ACTIONS = [
    JsonGet('/devices', list_devices),
    JsonPost('/set-property', set_property),
    Redirect('/', '/index.html'),
    StaticResources('/', './src/web')
]

server = start_server(80, ACTIONS)
server.serve_forever()
