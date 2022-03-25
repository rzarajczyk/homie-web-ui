from plugins.plugin import Plugin
from actions_server import Action, StaticResources


class TtsPlugin(Plugin):
    def __init__(self, config, plugin_root):
        Plugin.__init__(self, 'TtsPlugin')
        self.root = plugin_root

    def actions(self) -> list[Action]:
        return [StaticResources('/tts', '%s/web' % self.root)]

