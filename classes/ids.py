from dataclasses import dataclass
from typing import List


@dataclass
class Roles:
    admin: List[int]
    faq_management: List[int]


@dataclass
class Channels:
    bug_report: List[int]


@dataclass
class DataRoles:
    admin: int
    faq_management: int


@dataclass
class DataChannels:
    bug_report: int


@dataclass
class DataEntry:
    server: int
    roles: DataRoles
    channels: DataChannels
