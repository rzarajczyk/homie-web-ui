from enum import Enum, auto

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


class CommandPosition(Enum):
    DEFAULT = auto()
    SMALLER = auto()
    LEFT_HALF = auto()
    RIGHT_HALF = auto()


class CommandDisplay(Enum):
    DEFAULT = auto()
    ICON_ONLY = auto()


class Command:
    def __init__(self, id):
        self.id = id
        self.name = None
        self.path = None
        self.icon = None
        self.position = CommandPosition.DEFAULT
        self.display = CommandDisplay.DEFAULT
        self.header = None
        self.datatype = None
        self.argname = "Argument"


class Device:
    def __init__(self, id):
        self.id: str = id
        self.name: str = None
        self.properties: list[Property] = []
        self.icon = 'https://images.sftcdn.net/images/t_app-logo-xl,f_auto/p/b038a7e4-9b25-11e6-a4ee-00163ed833e7/12078914/android-device-manager-icon.png'
        self.hidden = False
        self.commands: list[Command] = []
        self.header = None


class Devices:
    def __init__(self, tree: HomieTree):
        self.devices = []
        for node in tree.tree().children():
            self.devices += self.parse_device_node(node)

    def enrich(self, config):
        for device in self.devices:
            if device.id in config:
                self.enrich_device(device, config[device.id])
            else:
                self.enrich_device(device, {})
        order = [device_id for device_id in config]
        self.devices.sort(key=lambda d: order.index(d.id) if d.id in order else 999999)

    def enrich_device(self, device, config):
        for prop in list(device.properties):
            if prop.settable == "true" and prop.retained != "true":
                command = Command(prop.id)
                command.name = prop.name
                command.path = prop.path
                command.datatype = prop.datatype
                device.commands.append(command)
                device.properties.remove(prop)
        if 'icon' in config:
            device.icon = config['icon']
        if 'hidden' in config:
            device.hidden = config['hidden']
        if 'header' in config:
            device.header = config['header']
        if 'commands' in config:
            for command_id in config['commands']:
                for device_command in device.commands:
                    if device_command.id == command_id:
                        if 'icon' in config['commands'][command_id]:
                            device_command.icon = config['commands'][command_id]['icon']
                        if 'position' in config['commands'][command_id]:
                            device_command.position = CommandPosition[config['commands'][command_id]['position']]
                        if 'display' in config['commands'][command_id]:
                            device_command.display = CommandDisplay[config['commands'][command_id]['display']]
                        if 'header' in config['commands'][command_id]:
                            device_command.header = config['commands'][command_id]['header']
                        if 'text' in config['commands'][command_id]:
                            device_command.name = config['commands'][command_id]['text']
                        if 'argname' in config['commands'][command_id]:
                            device_command.argname = config['commands'][command_id]['argname']
            order = [command_id for command_id in config['commands']]
            device.commands.sort(key=lambda cmd: order.index(cmd.id) if cmd.id in order else 999999)
        if 'properties' in config:
            for property_id in config['properties']:
                for device_property in device.properties:
                    if device_property.id == property_id:
                        if 'text' in config['properties'][property_id]:
                            device_property.name = config['properties'][property_id]['text']

    def to_json(self):
        result = []
        for device in self.devices:
            properties = []
            commands = []
            for command in device.commands:
                result_command = {
                    'id': command.id,
                    'name': command.name,
                    'path': command.path,
                    'icon': command.icon,
                    'datatype': command.datatype,
                    'position': command.position.name,
                    'display': command.display.name,
                    'header': command.header,
                    'argname': command.argname
                }
                commands.append(result_command)
            for prop in device.properties:
                result_prop = {
                    'id': prop.id,
                    'name': prop.name,
                    'value': prop.value,
                    'unit': prop.unit,
                    'datatype': prop.datatype,
                    'format': prop.format,
                    'settable': prop.settable == "true",
                    'retained': prop.retained == "true",
                    'path': prop.path
                }
                properties.append(result_prop)
            result_device = {
                'id': device.id,
                'name': device.name,
                'icon': device.icon,
                'header': device.header,
                'properties': properties,
                'commands': commands
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
        prop.settable = node.attributes.get('$settable', None)
        prop.retained = node.attributes.get('$retained', None)
        prop.value = node.value
        return prop
