# セッション管理ツール（cc-session-manager）

## 目的

Claude Codeのセッションを全プロジェクト横断で一覧・検索・再開・削除できるCLIツール。
`claude --list`はカレントディレクトリのセッションしか表示しないため、複数リポジトリを跨いだ作業でセッションが埋もれる問題を解消する。

## 技術スタック

- Python（標準ライブラリ中心、外部パッケージは最小限）
- ターミナルUI（番号入力式）
- データソース: `~/.claude/projects/` 配下の .jsonl ファイル

## フォルダ構成

```
cc-session-manager/
  cc_sessions/
    __init__.py
    __main__.py      ← 起動口（python -m cc_sessions）
    scanner.py       ← .jsonlファイルの探索・読み取り
    models.py        ← セッション情報の入れ物（SessionInfo）
    ui.py            ← 一覧表示・操作メニュー
    actions.py       ← 再開・プレビュー・削除の実行
    config.py        ← パス解決・設定値
  pyproject.toml
```

## データ構造

### セッションの保存場所

```
~/.claude/projects/
  C--Users-ykoba-dev/              ← プロジェクトパス（区切りを--に置換）
    55aa1664-xxxx.jsonl             ← メインセッションファイル（対象）
    55aa1664-xxxx/                  ← セッションの付随データ
      subagents/                    ← サブエージェントのログ（対象外）
    memory/                         ← プロジェクトメモリ（対象外）
```

### .jsonl から取得する情報

| 行のtype | 取得する情報 |
|---|---|
| `custom-title` | セッション名（`customTitle`フィールド） |
| `system`（bridge_status） | `cwd`（元のプロジェクトパス）, `sessionId`, `timestamp` |
| `user` | 最初の発言（プレビュー用） |

### SessionInfo データクラス

- session_id: セッションID（UUID）
- title: セッション名
- project_dir: 元のプロジェクトパス
- jsonl_path: .jsonlファイルの絶対パス
- last_updated: 最終更新日時（ファイルのmtime）
- first_message: ユーザーの最初の発言
- message_count: メッセージ数

## UIフロー

```
起動
  ↓
[全セッション読み込み・一覧表示]（最終更新順・新しい順）
  ↓
番号で選択 / s:検索 / q:終了
  ↓
[セッション詳細画面]
  タイトル / プロジェクト / 最終更新 / 最初の発言 / メッセージ数
  
  [r] 再開  [p] プレビュー  [d] 削除  [b] 戻る
```

## 実装フェーズ

### Phase 1: 基盤（読み取りのみ）
1. config.py — パス解決
2. models.py — SessionInfo データクラス
3. scanner.py — .jsonl 探索・パース
4. 動作確認: scan_all_sessions() で全セッション情報を表示

### Phase 2: 最小UIで一覧・再開
5. ui.py — input() ベースの番号選択UI
6. actions.py — resume_session() を実装
7. __main__.py — エントリーポイント
8. 動作確認: 一覧から claude --resume が起動するか

### Phase 3: プレビュー・削除・検索
9. actions.py に preview_session() 追加
10. actions.py に delete_session() 追加（確認プロンプト付き）
11. ui.py に検索機能追加
12. 動作確認: 全機能が動くか

### Phase 4: UI改善（任意）
13. questionary 導入で矢印キー選択に差し替え
14. 表示の色付け・フォーマット改善

## 安全策

- 壊れた .jsonl は1行ずつ try/except で処理（クラッシュしない）
- 大きなファイルは必要な情報を取得したら読み取りを打ち切る
- subagents/ 配下・memory/ 配下は対象外
- 削除前に必ず確認プロンプトを出す
- 削除対象は .jsonl と同名フォルダのみ（それ以外に触れない）
- 再開前にプロジェクトディレクトリの存在を確認する

## 注意点

- セッション並列実行ツールとは別の独立したツール
- 独自DBは持たない（~/.claude/projects/ のみ参照）
- Windows 11 で動作すること
- パスは pathlib.Path で統一
