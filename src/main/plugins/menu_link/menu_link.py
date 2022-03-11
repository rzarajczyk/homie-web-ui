from plugins.plugin import Plugin, Link


class MenuLinkPlugin(Plugin):
    def __init__(self, config, plugin_root):
        Plugin.__init__(self, 'MenuLink')
        self.name = config['name']
        self.url = config['url']
        self.new_window = config.get('new-window', True)

    def links(self) -> list[Link]:
        return [Link(self.name, self.url, self.new_window)]
