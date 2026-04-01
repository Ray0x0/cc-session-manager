# cc-session-manager

A CLI tool to list, preview, resume, and delete Claude Code sessions across all projects.

`claude --list` only shows sessions for the current directory. This tool solves that by scanning all sessions under `~/.claude/projects/` and showing them in one unified list.

Inspired by [chronologos/cc-sessions](https://github.com/chronologos/cc-sessions) (Rust, macOS/Linux only). This is a Python reimplementation with Windows support.

---

## Features

- List all Claude Code sessions across every project in one view
- Resume a session from any directory with `claude --resume`
- Preview conversation history
- Delete unwanted sessions (with confirmation)
- Search sessions by title or project path

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code) installed

## Installation

```bash
git clone https://github.com/Ray0x0/cc-session-manager.git
cd cc-session-manager
```

No additional packages required.

## Usage

```bash
python -m cc_sessions
```

```
[ 1] My Project Session        C:\Users\you\dev\my-project    2026-04-01 15:00
[ 2] Another Session           C:\Users\you\dev\other         2026-03-30 10:22
...

Enter number (s: search / q: quit) > 1

──────────────────────────────────────────────────
  My Project Session
  C:\Users\you\dev\my-project
  Last updated: 2026-04-01 15:00  |  Messages: 12
  First message: Tell me about...
──────────────────────────────────────────────────
  [r] Resume  [p] Preview  [d] Delete  [b] Back
```

## Platform

| Platform | Status |
|----------|--------|
| Windows 11 | ✅ Tested |
| macOS | ❓ Untested |
| Linux | ❓ Untested |

macOS/Linux should work in principle, but has not been verified. Feedback welcome.

## How it works

Claude Code stores sessions as `.jsonl` files under `~/.claude/projects/`. Each file contains the conversation history for one session. This tool scans those files directly — no external database or API calls.

## License

MIT
