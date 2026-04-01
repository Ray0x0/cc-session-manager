import json
from datetime import datetime
from pathlib import Path

from .config import get_projects_dir
from .models import SessionInfo


def scan_all_sessions() -> list[SessionInfo]:
    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        return []

    sessions = []
    for jsonl_path in _find_session_files(projects_dir):
        info = _parse_jsonl(jsonl_path)
        if info:
            sessions.append(info)

    sessions.sort(key=lambda s: s.last_updated, reverse=True)
    return sessions


def _find_session_files(projects_dir: Path) -> list[Path]:
    results = []
    for project_folder in projects_dir.iterdir():
        if not project_folder.is_dir():
            continue
        for f in project_folder.glob("*.jsonl"):
            results.append(f)
    return results


def _parse_jsonl(path: Path) -> SessionInfo | None:
    title = ""
    project_dir = ""
    session_id = path.stem
    first_message = ""
    message_count = 0
    last_updated = datetime.fromtimestamp(path.stat().st_mtime)

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                t = obj.get("type", "")

                if t == "custom-title" and not title:
                    title = obj.get("customTitle", "")

                elif t == "system" and obj.get("subtype") == "bridge_status":
                    if not project_dir:
                        project_dir = obj.get("cwd", "")
                    if not session_id:
                        session_id = obj.get("sessionId", path.stem)

                elif t == "user":
                    message_count += 1
                    if not first_message:
                        content = obj.get("message", {}).get("content", "")
                        if isinstance(content, str):
                            first_message = content[:80]
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    first_message = block.get("text", "")[:80]
                                    break

                if title and project_dir and first_message:
                    break

    except OSError:
        return None

    return SessionInfo(
        session_id=session_id,
        title=title,
        project_dir=project_dir,
        jsonl_path=path,
        last_updated=last_updated,
        first_message=first_message,
        message_count=message_count,
    )
