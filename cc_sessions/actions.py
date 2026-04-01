import json
import shutil
import subprocess
from pathlib import Path

from .config import CLAUDE_CMD
from .models import SessionInfo


def resume_session(session: SessionInfo) -> None:
    project_path = Path(session.project_dir)
    if not project_path.exists():
        print(f"\n⚠ プロジェクトフォルダが見つかりません: {session.project_dir}")
        input("Enter で戻る...")
        return

    print(f"\n「{session.display_title()}」を再開します...")
    subprocess.run(
        [CLAUDE_CMD, "--resume", session.session_id],
        cwd=str(project_path),
    )


def preview_session(session: SessionInfo) -> None:
    print(f"\n{'='*60}")
    print(f"  {session.display_title()}")
    print(f"  {session.display_project()}  |  {session.display_date()}")
    print(f"{'='*60}\n")

    try:
        with open(session.jsonl_path, encoding="utf-8") as f:
            turns = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                t = obj.get("type", "")

                if t == "user":
                    content = obj.get("message", {}).get("content", "")
                    text = _extract_text(content)
                    if text:
                        print(f"[あなた]\n{text[:300]}\n")
                        turns += 1

                elif t == "assistant":
                    content = obj.get("message", {}).get("content", [])
                    text = _extract_text(content)
                    if text:
                        print(f"[Claude]\n{text[:300]}\n")

                if turns >= 5:
                    print("（以降省略）")
                    break

    except OSError:
        print("ファイルを読み込めませんでした。")

    input("\nEnter で戻る...")


def delete_session(session: SessionInfo) -> bool:
    print(f"\n削除対象: {session.display_title()}")
    print(f"  ファイル: {session.jsonl_path}")
    folder = session.jsonl_path.parent / session.session_id
    if folder.exists():
        print(f"  フォルダ: {folder}")

    ans = input("\n本当に削除しますか？ (yes と入力で削除) > ").strip()
    if ans != "yes":
        print("キャンセルしました。")
        return False

    try:
        session.jsonl_path.unlink()
        if folder.exists():
            shutil.rmtree(folder)
        print("削除しました。")
        return True
    except OSError as e:
        print(f"削除に失敗しました: {e}")
        return False


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", "").strip())
        return "\n".join(parts)
    return ""
