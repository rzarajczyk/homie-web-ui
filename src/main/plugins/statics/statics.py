from typing import List

from plugins.plugin import Plugin
from actions_server import Action, StaticResources


class StaticsPlugin(Plugin):
    def __init__(self, config, plugin_root, url_root):
        Plugin.__init__(self, 'StaticsPlugin')
        self.root_dir = plugin_root
        self.root_url = url_root

    def actions(self) -> List[Action]:
        return [StaticResources(f'{self.root_url}', '%s/web' % self.root_dir)]

