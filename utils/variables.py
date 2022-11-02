'''
Utility for accessing ids defined in `ids.json`
'''

from dataclasses import dataclass
from typing import List

import json5 as json
from dataclass_wizard import fromdict

from classes.ids import Channels, DataEntry, Roles


class Ids:

    def __init__(self, path: str) -> None:
        # open path and access data
        with open(path, 'r', encoding='utf-8') as f:
            data = [
                fromdict(DataEntry, i) for i in json.load(f)  # type: ignore
            ]

        self.servers: List[int] = [i.server for i in data]
        self.roles: Roles = Roles(
            admin=[i.roles.admin for i in data],
            faq_management=[i.roles.faq_management for i in data])

        self.channels: Channels = Channels(
            bug_report=[i.channels.bug_report for i in data])


@dataclass
class Texts:
    EMBED_FOOTER = 'brought to you by {}'


@dataclass
class Consts:
    CONFIG_PATH = 'config/config.json'
