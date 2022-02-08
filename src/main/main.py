import logging
import os
import shutil
from logging import config as logging_config

import paho.mqtt.client as mqtt
import yaml

from devices import Devices
from homietree import HomieTree
from server import start_server

ROOT = os.environ.get('APP_ROOT', ".")

########################################################################################################################
# logging configuration

LOGGER_CONFIGURATION = "%s/config/logging.yaml" % ROOT
if not os.path.isfile(LOGGER_CONFIGURATION):
    shutil.copy("%s/config-defaults/logging.yaml" % ROOT, LOGGER_CONFIGURATION)

with open(LOGGER_CONFIGURATION, 'r') as f:
    config = yaml.full_load(f)
    logging_config.dictConfig(config)

LOGGER = logging.getLogger("main")

########################################################################################################################
# application configuration

CONFIGURATION = "%s/config/application.yaml" % ROOT
if not os.path.isfile(CONFIGURATION):
    shutil.copy("%s/config-defaults/application.yaml" % ROOT, CONFIGURATION)

with open(CONFIGURATION, 'r') as f:
    config = yaml.full_load(f)

    MQTT_HOST = config['mqtt']['host']
    MQTT_PORT = config['mqtt']['port']
    MQTT_USER = config['mqtt']['user']
    MQTT_PASS = config['mqtt']['password']

    DEVICES_CONFIG = config['devices']

########################################################################################################################

tree = HomieTree()


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("homie/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    tree.accept_message(topic, payload)


def list_devices():
    # tree.tree().debug('')
    devices = Devices(tree)
    devices.enrich(DEVICES_CONFIG)
    return devices.to_json()


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT)

client.loop_start()

GET_ACTIONS = {
    '/devices': list_devices
}
POST_ACTIONS = {}

server = start_server(8080, GET_ACTIONS, POST_ACTIONS)
server.serve_forever()
