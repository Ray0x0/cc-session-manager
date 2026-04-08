from pathlib import Path


def get_projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"


CLAUDE_CMD = "claude"

# handoffファイルを管理する対象プロジェクト
TARGET_PROJECTS = [
    {
        "name": "dev",
        "project_dir": Path.home() / "dev",
        "sessions_dir": Path.home() / "dev" / "sessions",
    },
    {
        "name": "life",
        "project_dir": Path.home() / "life",
        "sessions_dir": Path.home() / "life" / "sessions",
    },
]
