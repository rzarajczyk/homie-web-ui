import requests
from typing import List

from plugins.plugin import Plugin, Link
from actions_server import Action, JsonPost, StaticResources, JsonGet


class ScanPlugin(Plugin):
    def __init__(self, config, plugin_root):
        Plugin.__init__(self, 'ScanPlugin')
        self.url = config['url']
        self.root = plugin_root

    def links(self) -> List[Link]:
        return [Link('Scan', '/scan/scan.html')]

    def actions(self) -> List[Action]:
        return [
            JsonGet('/scan/ready', self.scanner_ready),
            JsonPost('/scan/scan', self.scan),
            StaticResources('/scan', '%s/web' % self.root)
        ]

    def scan(self, params, payload):
        self.logger.info('Requesting scanner')
        response = requests.post('%s/scan' % self.url)
        response.raise_for_status()
        return response.json()

    def scanner_ready(self, params):
        self.logger.info('Checking scanner readiness')
        response = requests.get('%s/print/info' % self.url)
        return {'ready': response.status_code == 200}
