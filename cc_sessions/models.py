from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SessionInfo:
    session_id: str
    title: str
    project_dir: str
    jsonl_path: Path
    last_updated: datetime
    first_message: str
    message_count: int

    def display_title(self) -> str:
        return self.title or f"（無題）{self.session_id[:8]}"

    def display_project(self) -> str:
        return self.project_dir or "（不明）"

    def display_date(self) -> str:
        return self.last_updated.strftime("%Y-%m-%d %H:%M")
