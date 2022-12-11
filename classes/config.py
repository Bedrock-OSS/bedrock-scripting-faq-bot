from dataclasses import dataclass


@dataclass
class Config:
    allow_feedback: bool
    feedback_cooldown: int
    algolia_app_id: str
    algolia_auth_key: str
    algolia_index_name: str
