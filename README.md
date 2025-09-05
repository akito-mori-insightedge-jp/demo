# 勤怠アプリ (Flask + SQLite)

シンプルな勤怠打刻アプリです。社員名を入力して出勤(Clock In)/退勤(Clock Out)できます。記録一覧も閲覧可能です。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py  # http://127.0.0.1:5000
```

## 主要機能

- 出勤/退勤の打刻
- 社員名ごとの当日ステータス表示
- 勤怠記録一覧表示

## 環境変数 (任意)

- `FLASK_DEBUG=1` でデバッグモード
- `DATABASE_URL` を設定すると外部DBに接続可能 (未設定時は SQLite `attendance.db`)

## テスト

```bash
pytest -q
```

## ライセンス

MIT

