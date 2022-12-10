'''
Utility for accessing ids defined in `ids.json`
'''

from dataclasses import dataclass
from typing import List

import json5 as json
from dataclass_wizard import fromdict

from classes.ids import BugReport, Channels, DataEntry, IdBase, Roles

from discord import ActivityType


class Ids:

    def __init__(self, path: str) -> None:
        # open path and access data
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
            data: IdBase = fromdict(IdBase, d)  # type: ignore
            # data = [
            #     fromdict(DataEntry, i) for i in json.load(f)  # type: ignore
            # ]

        self.servers: List[int] = [i.server for i in data.manage_servers]
        self.roles: Roles = Roles(
            admin=[i.roles.admin for i in data.manage_servers],
            faq_management=[
                i.roles.faq_management for i in data.manage_servers
            ])

        # self.channels: Channels = Channels(
        #     bug_report=[i.channels.bug_report for i in data.manage_servers])

        self.bug_report = BugReport(server=data.bug_report.server,
                                    channel=data.bug_report.channel)


@dataclass
class Texts:
    EMBED_FOOTER = 'brought to you by {}'


@dataclass
class Consts:
    CONFIG_PATH = 'config/config.json'


@dataclass
class Presences:
    presences: tuple[tuple[ActivityType, str], ...] = (
        (ActivityType.watching, 'the chat. For Support, join Bedrock-OSS!'),
        (ActivityType.watching,
         "the chat. It's open source! Visit github.com/Bedrock-OSS!"),
        (ActivityType.watching, '{} servers'),
        (ActivityType.playing, 'with {} users'),
        (ActivityType.listening, 'to your commands'),
    )
