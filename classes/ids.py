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
    bug_report: int | None = None


@dataclass
class DataEntry:
    server: int
    roles: DataRoles
    channels: DataChannels


@dataclass
class BugReport:
    server: int
    channel: int


@dataclass
class IdBase:
    manage_servers: List[DataEntry]
    bug_report: BugReport
