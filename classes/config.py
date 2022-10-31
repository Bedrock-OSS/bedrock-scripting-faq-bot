from dataclasses import dataclass


@dataclass
class Config:
    allow_bug_reports: bool
    bug_report_cooldown: int
