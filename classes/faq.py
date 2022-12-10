from dataclasses import dataclass
from typing import List


@dataclass
class FaqEntry:
    tags: List[str]
    title: str
    description: str | None = None
    image: str | None = None
    modification_time: int = 0
