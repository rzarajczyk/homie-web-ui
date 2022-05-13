from actions_server import JsonGet, Redirect, StaticResources, http_server
from bootstrap.bootstrap import start_service

from plugins.homie.homie import HomiePlugin
from plugins.menu_link.menu_link import MenuLinkPlugin
from plugins.plugin import Link
from plugins.scan.scan import ScanPlugin
from plugins.toyota.toyota import ToyotaPlugin
from plugins.tts.tts import TtsPlugin

config, logger, timezone = start_service()

PLUGINS_CONFIG = config['plugins']

PLUGIN_CLASSES = {
    'scan': ScanPlugin,
    'menu-link': MenuLinkPlugin,
    'tts': TtsPlugin,
    'toyota': ToyotaPlugin,
    'homie': HomiePlugin
}

PLUGINS = []

for plugin_id in PLUGINS_CONFIG:
    plugin_type = PLUGINS_CONFIG[plugin_id]['type']
    plugin_class = PLUGIN_CLASSES[plugin_type]
    plugin = plugin_class(PLUGINS_CONFIG[plugin_id], './src/main/plugins/%s' % plugin_type.replace('-', '_'))
    PLUGINS.append(plugin)


def navigation(params):
    links = []
    links += [Link('Home', '/index.html')]
    for plugin in PLUGINS:
        links += plugin.links()
    return {
        'navigation': links
    }


ACTIONS = [
    JsonGet('/navigation', navigation),
    Redirect('/', '/index.html'),
    StaticResources('/', './src/web')
]

for plugin in PLUGINS:
    ACTIONS += plugin.actions()

server = http_server(8080, ACTIONS)
try:
    server.start(block_caller_thread=True)
finally:
    logger.info('Closing server')
    server.stop()
