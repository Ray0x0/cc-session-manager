import unicodedata

from .actions import clean_sessions, delete_session, preview_session, resume_session
from .models import SessionInfo
from .scanner import scan_all_sessions


def _vislen(s: str) -> int:
    """日本語などの全角文字を2幅として表示幅を計算する"""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _ljust(s: str, width: int) -> str:
    """表示幅を考慮して左詰めパディングする"""
    pad = width - _vislen(s)
    return s + " " * max(pad, 0)


def main() -> None:
    while True:
        sessions = scan_all_sessions()
        if not sessions:
            print("セッションが見つかりませんでした。")
            return

        _show_list(sessions)
        choice = input("\n番号を入力 (s:検索 / c:クリーン / q:終了) > ").strip()

        if choice == "q":
            break
        elif choice == "c":
            clean_sessions()
            continue
        elif choice == "s":
            sessions = _search(sessions)
            if not sessions:
                print("見つかりませんでした。")
                input("Enter で戻る...")
                continue
            _show_list(sessions)
            choice = input("\n番号を入力 > ").strip()

        session = _pick(sessions, choice)
        if session:
            _session_menu(session)


def _show_list(sessions: list[SessionInfo]) -> None:
    print()
    for i, s in enumerate(sessions, 1):
        title = s.display_title()
        # 表示幅20相当に切り詰め（全角考慮）
        title_cut = _cut(title, 28)
        proj = s.display_project()
        proj_cut = _cut(proj, 42)
        print(f"[{i:2}] {_ljust(title_cut, 28)}  {_ljust(proj_cut, 42)}  {s.display_date()}")


def _cut(s: str, max_width: int) -> str:
    """表示幅 max_width を超えないように文字列を切り詰める"""
    width = 0
    for i, c in enumerate(s):
        w = 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1
        if width + w > max_width:
            return s[:i]
        width += w
    return s


def _search(sessions: list[SessionInfo]) -> list[SessionInfo]:
    keyword = input("検索キーワード > ").strip().lower()
    return [
        s for s in sessions
        if keyword in s.title.lower() or keyword in s.project_dir.lower()
    ]


def _pick(sessions: list[SessionInfo], choice: str) -> SessionInfo | None:
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sessions):
            return sessions[idx]
    except ValueError:
        pass
    print("無効な番号です。")
    return None


def _session_menu(session: SessionInfo) -> None:
    while True:
        print(f"\n{'─'*50}")
        print(f"  {session.display_title()}")
        print(f"  {session.display_project()}")
        print(f"  最終更新: {session.display_date()}  |  メッセージ数: {session.message_count}")
        if session.first_message:
            print(f"  最初の発言: {session.first_message[:60]}")
        print(f"{'─'*50}")
        print("  [r] 再開  [p] プレビュー  [d] 削除  [b] 戻る")

        action = input("> ").strip().lower()

        if action == "r":
            resume_session(session)
            return
        elif action == "p":
            preview_session(session)
        elif action == "d":
            deleted = delete_session(session)
            if deleted:
                return
        elif action == "b":
            return
        else:
            print("r / p / d / b のいずれかを入力してください。")
