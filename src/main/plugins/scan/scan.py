import requests

from plugins.plugin import Plugin, Link
from server import Action, JsonPost, StaticResources


class ScanPlugin(Plugin):
    def __init__(self, config, plugin_root):
        Plugin.__init__(self, 'ScanPlugin')
        self.url = config['url']
        self.root = plugin_root

    def links(self) -> list[Link]:
        return [Link('Scan', '/scan/scan.html')]

    def actions(self) -> list[Action]:
        return [
            JsonPost('/scan', self.scan),
            StaticResources('/scan', '%s/web' % self.root)
        ]

    def scan(self, params, payload):
        self.logger.info('Requesting scanner')
        return requests.post('%s/scan' % self.url).json()
