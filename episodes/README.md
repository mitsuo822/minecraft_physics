# episodes

動画1本につき1ディレクトリ（`EP001_<短い名前>/`）。

```
EP001_free_fall/
  episode.yaml     # どの実験を使うか、関門の承認記録、各工程の状態（orchestra が書く）
  research.md      # 調査
  review_*.md      # 審査の判定
  runlog.jsonl     # 実行台帳（工程ごとの時間・費用・結果）
  script.md        # 台本（実測結果を見てから書く）
  ledger.json      # movie に渡す制作台帳（自動生成）
  shorts/          # ショートの台本・台帳
```

新しい回は `python -m orchestra new` で作る（`_template/` をコピーする）。
