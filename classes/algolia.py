from dataclasses import dataclass
from enum import Enum


class AlgoliaResultType(Enum):
    mainHeader = 'file'
    subHeader = 'heading'
    content = 'content'

@dataclass
class AlgoliaResult:
    header: str
    description: str | None
    highlight: list[str]
    url: str
    type: AlgoliaResultType
