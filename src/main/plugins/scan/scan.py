import requests
from typing import List

from plugins.plugin import Plugin, Link
from actions_server import Action, JsonPost, StaticResources, JsonGet


class ScanPlugin(Plugin):
    def __init__(self, config, plugin_root, url_root):
        Plugin.__init__(self, 'ScanPlugin')
        self.url = config['url']
        self.root_dir = plugin_root
        self.root_url = url_root

    def links(self) -> List[Link]:
        return [Link('Scan', f'{self.root_url}/scan.html')]

    def actions(self) -> List[Action]:
        return [
            JsonGet(f'{self.root_url}/ready', self.scanner_ready),
            JsonPost(f'{self.root_url}/scan', self.scan),
            StaticResources(f'{self.root_url}', '%s/web' % self.root_dir)
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
