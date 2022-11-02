from dataclasses import dataclass


@dataclass
class AlgoliaResult:
    url: str
    description: str
    heading: str
