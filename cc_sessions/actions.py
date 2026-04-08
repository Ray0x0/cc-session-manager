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


def clean_sessions() -> None:
    """孤立セッションを検出し、一括削除を提案する"""
    from .scanner import scan_all_sessions, scan_active_session_ids

    active_ids = scan_active_session_ids()
    all_sessions = scan_all_sessions()

    if not all_sessions:
        print("セッションが見つかりませんでした。")
        return

    protected = []
    orphaned = []

    for s in all_sessions:
        if s.session_id in active_ids:
            protected.append(s)
        else:
            orphaned.append(s)

    if protected:
        print("\n紐づきあり（保護）:")
        for s in protected:
            print(f"  - {s.display_title()} → {s.session_id[:8]} — {s.display_date()}")

    if not orphaned:
        print("\n孤立セッションはありません。")
        return

    print(f"\n孤立セッション（削除候補）: {len(orphaned)}件")
    for i, s in enumerate(orphaned, 1):
        print(f"  {i}. {s.display_title()} — {s.session_id[:8]} — {s.display_date()} （{s.display_project()}）")

    ans = input(f"\n{len(orphaned)}件を一括削除しますか？ (yes と入力で削除) > ").strip()
    if ans != "yes":
        print("キャンセルしました。")
        return

    deleted = 0
    for s in orphaned:
        try:
            s.jsonl_path.unlink()
            folder = s.jsonl_path.parent / s.session_id
            if folder.exists():
                shutil.rmtree(folder)
            deleted += 1
        except OSError as e:
            print(f"  削除失敗: {s.session_id[:8]} — {e}")

    print(f"\n{deleted}件を削除しました。")


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
