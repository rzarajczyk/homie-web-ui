import logging
import json
from typing import List

import paho.mqtt.client as mqtt

from plugins.homie.devices import Devices
from plugins.homie.homietree import HomieTree
from plugins.plugin import Plugin, Link
from actions_server import Action, JsonPost, StaticResources, JsonGet


class HomiePlugin(Plugin):
    def __init__(self, config, plugin_root, url_root):
        Plugin.__init__(self, 'HomiePlugin')
        # self.url = config['url']
        self.root_dir = plugin_root
        self.root_url = url_root
        self.name = config['name']
        self.DEVICES_CONFIG = config['devices']
        self.SUBDEVICES = config['subdevices']

        MQTT_HOST = config['mqtt']['host']
        MQTT_PORT = config['mqtt']['port']
        MQTT_USER = config['mqtt']['user']
        MQTT_PASS = config['mqtt']['password']

        self.tree = HomieTree()
        self.logger = logging.getLogger('homie')

        self.client = mqtt.Client()
        self.client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(MQTT_HOST, MQTT_PORT)

        self.client.loop_start()

    def links(self) -> List[Link]:
        return [Link(self.name, f'{self.root_url}/devices.html')]

    def actions(self) -> List[Action]:
        return [
            JsonGet(f'{self.root_url}/init', self.get_init_data),
            JsonGet(f'{self.root_url}/devices', self.list_devices),
            JsonPost(f'{self.root_url}/set-property', self.set_property),
            StaticResources(f'{self.root_url}', f'{self.root_dir}/web')
        ]

    def get_init_data(self, params):
        return {
            'root': self.root_url
        }

    def list_devices(self, params):
        devices = Devices(self.tree, self.SUBDEVICES)
        devices.enrich(self.DEVICES_CONFIG)
        print('Will leave only with IDS: %s' % self.DEVICES_CONFIG.keys())
        devices.leave_only_ids(self.DEVICES_CONFIG.keys())
        return devices.to_json()

    def set_property(self, params, payload):
        payload_json = payload
        topic = "homie/%s/set" % payload_json['path'].replace('.', '/')
        value = payload_json['value']

        if value is False:
            value = "false"
        elif value is True:
            value = "true"

        self.logger.info("PUBLISHING:     %-70s | %s" % (topic, value))
        self.client.publish(topic, value)

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code %s" % str(rc))
        client.subscribe("homie/#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode(encoding='UTF-8')
        self.logger.debug("Received event: %-70s | %s" % (topic, payload))
        self.tree.accept_message(topic, payload)
