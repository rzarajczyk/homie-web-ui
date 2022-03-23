import json
import logging
from logging import config as logging_config

import paho.mqtt.client as mqtt
import yaml

from devices import Devices
from homietree import HomieTree
from plugins.menu_link.menu_link import MenuLinkPlugin
from plugins.plugin import Link
from plugins.scan.scan import ScanPlugin
from plugins.toyota.toyota import ToyotaPlugin
from plugins.tts.tts import TtsPlugin
from server import JsonGet, JsonPost, Redirect, StaticResources, http_server

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

    PLUGINS_CONFIG = config['plugins']
########################################################################################################################

PLUGIN_CLASSES = {
    'scan': ScanPlugin,
    'menu-link': MenuLinkPlugin,
    'tts': TtsPlugin,
    'toyota': ToyotaPlugin
}

PLUGINS = []

for plugin_id in PLUGINS_CONFIG:
    plugin_type = PLUGINS_CONFIG[plugin_id]['type']
    plugin_class = PLUGIN_CLASSES[plugin_type]
    plugin = plugin_class(PLUGINS_CONFIG[plugin_id], './src/main/plugins/%s' % plugin_type.replace('-', '_'))
    PLUGINS.append(plugin)

tree = HomieTree()


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("homie/#")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    LOGGER.debug("Received event: %-70s | %s" % (topic, payload))
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


def navigation(params):
    links = []
    links += [Link('Smart Home', '/index.html')]
    for plugin in PLUGINS:
        links += plugin.links()
    return {
        'navigation': links
    }


client.loop_start()

ACTIONS = [
    JsonGet('/navigation', navigation),
    JsonGet('/devices', list_devices),
    JsonPost('/set-property', set_property),
    Redirect('/', '/index.html'),
    StaticResources('/', './src/web')
]

for plugin in PLUGINS:
    ACTIONS += plugin.actions()

server = http_server(80, ACTIONS)
try:
    server.start(block_caller_thread=True)
finally:
    LOGGER.info('Closing server')
    server.stop()
