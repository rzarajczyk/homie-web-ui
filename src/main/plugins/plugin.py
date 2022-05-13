import logging

from actions_server import Action
from typing import List


class Link:
    def __init__(self, name, link, new_window=False):
        self.name = name
        self.link = link
        self.new_window = new_window


class Plugin:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def links(self) -> List[Link]:
        return []

    def actions(self) -> List[Action]:
        return []
