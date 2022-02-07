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


class Device:
    def __init__(self, id):
        self.id: str = id
        self.name: str = None
        self.properties: list[Property] = []


class Devices:
    def __init__(self, tree: HomieTree):
        self.devices = []
        self.parse(tree)

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
                    'format': prop.format
                }
                properties.append(result_prop)
            result_device = {
                'id': device.id,
                'name': device.name,
                'properties': properties
            }
            result.append(result_device)
        return {
            'devices': result
        }

    def parse(self, tree: HomieTree):
        self.devices = []
        for node in tree.tree().children():
            self.devices += self.parse_device_node(node)

    def parse_device_node(self, node: Node):
        if node.id == 'homey':
            result = []
            for node in node.children():
                result += self.parse_device_node(node)
            return result
        else:
            device = Device(node.id)
            device.name = node.attributes.get('$name', None)
            self.parse_device_sub_nodes_and_properties(device, node)
            return [device]

    def parse_device_sub_nodes_and_properties(self, device, node):
        for expected_property in node.attributes.get('$properties', '').split(','):
            property_node = node.find_child(expected_property)
            if property_node is not None:
                prop = self.parse_property_node(property_node)
                device.properties.append(prop)
        for expected_sub_node in node.attributes.get('$nodes', '').split(','):
            sub_node = node.find_child(expected_sub_node)
            if sub_node is not None:
                self.parse_device_sub_nodes_and_properties(device, sub_node)

    def parse_property_node(self, node: Node):
        prop = Property(node.id)
        prop.name = node.attributes.get('$name', None)
        prop.unit = node.attributes.get('$unit', None)
        prop.format = node.attributes.get('$format', None)
        prop.datatype = node.attributes.get('$datatype', None)
        prop.value = node.value
        return prop
