import logging


class Node:
    def __init__(self, id: str):
        self.id: str = id
        self.value: str = None
        self.attributes: dict = {}
        self.nodes: dict = {}

    def get_or_create_child(self, id: str):
        if id not in self.nodes:
            self.nodes[id] = Node(id)
        return self.nodes[id]

    def find_child(self, id: str):
        if id not in self.nodes:
            return None
        return self.nodes[id]

    def children(self):
        return self.nodes.values()

    def debug(self, indent=''):
        properties = ', '.join(["%s=%s" % (attr, self.attributes[attr]) for attr in self.attributes])
        print("%s # %s (%s) => %s" % (indent, self.id, properties, self.value))
        for child_id in self.nodes:
            self.nodes[child_id].debug(indent + '    ')


class HomieTree:
    def __init__(self):
        self.root = Node('ROOT')
        self.logger = logging.getLogger("devices")

    def tree(self):
        return self.root

    def accept_message(self, topic, payload):
        try:
            parts = topic.split("/")
            parts = parts[1:] if len(parts) > 0 and parts[0] == 'homie' else parts

            meta_index = find_meta_index(parts)

            if meta_index < 0:
                get_node(parts, self.root).value = payload
            else:
                meta_name = parts[meta_index]
                parts = parts[0:meta_index]
                get_node(parts, self.root).attributes[meta_name] = payload
        except Exception as e:
            self.logger.exception("Problem processing topic: %s" % topic, e)


def get_node(path, root) -> Node:
    if len(path) == 0:
        return root
    else:
        id = path.pop(0)
        root = root.get_or_create_child(id)
        return get_node(path, root)


def find_meta_index(parts):
    for i, value in enumerate(parts):
        if value.startswith('$'):
            return i
    return -1
