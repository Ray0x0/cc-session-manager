from pathlib import Path


def get_projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"


CLAUDE_CMD = "claude"
