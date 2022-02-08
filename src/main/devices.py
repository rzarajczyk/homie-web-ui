from homietree import Node, HomieTree


class Property:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.unit = None
        self.datatype = None
        self.value = None
        self.format = None
        self.retained = None
        self.settable = None
        self.path = None


class Device:
    def __init__(self, id):
        self.id: str = id
        self.name: str = None
        self.properties: list[Property] = []
        self.icon = 'https://images.sftcdn.net/images/t_app-logo-xl,f_auto/p/b038a7e4-9b25-11e6-a4ee-00163ed833e7/12078914/android-device-manager-icon.png'
        self.hidden = False


class Devices:
    def __init__(self, tree: HomieTree):
        self.devices = []
        for node in tree.tree().children():
            self.devices += self.parse_device_node(node)

    def enrich(self, config):
        for device in self.devices:
            if device.id in config:
                self.enrich_device(device, config[device.id])

    def enrich_device(self, device, config):
        if 'icon' in config:
            device.icon = config['icon']
        if 'hidden' in config:
            device.hidden = config['hidden']

    def to_json(self):
        result = []
        for device in self.devices:
            properties = []
            for prop in device.properties:
                result_prop = {
                    'id': prop.id,
                    'name': prop.name,
                    'value': prop.value,
                    'unit': prop.unit,
                    'datatype': prop.datatype,
                    'format': prop.format,
                    'path': prop.path
                }
                properties.append(result_prop)
            result_device = {
                'id': device.id,
                'name': device.name,
                'icon': device.icon,
                'properties': properties
            }
            if not device.hidden:
                result.append(result_device)
        return {
            'devices': result
        }

    def parse_device_node(self, node: Node, path: str = ''):
        if node.id == 'homey':
            result = []
            for node in node.children():
                result += self.parse_device_node(node, 'homey.')
            return result
        else:
            device = Device(node.id)
            device.name = node.attributes.get('$name', None)
            self.parse_device_sub_nodes_and_properties(device, node, path + node.id)
            return [device]

    def parse_device_sub_nodes_and_properties(self, device, node, path):
        for expected_property in node.attributes.get('$properties', '').split(','):
            property_node = node.find_child(expected_property)
            if property_node is not None:
                prop = self.parse_property_node(property_node)
                if prop.name.startswith("%s - " % device.name):
                    prop.name = prop.name.replace("%s - " % device.name, '')
                prop.path = "%s.%s" % (path, prop.id)
                device.properties.append(prop)
        for expected_sub_node in node.attributes.get('$nodes', '').split(','):
            sub_node = node.find_child(expected_sub_node)
            if sub_node is not None:
                self.parse_device_sub_nodes_and_properties(device, sub_node, "%s.%s" % (path, expected_sub_node))

    def parse_property_node(self, node: Node):
        prop = Property(node.id)
        prop.name = node.attributes.get('$name', None)
        prop.unit = node.attributes.get('$unit', None)
        prop.format = node.attributes.get('$format', None)
        prop.datatype = node.attributes.get('$datatype', None)
        prop.value = node.value
        return prop
