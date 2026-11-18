# lab

実験の実行・計測・理論モデルのコード（Python、未実装）。予定している構成:

```
lab/
  rcon.py          # サーバにRCONでコマンドを送る
  runner.py        # experiment.yaml を読み、tick freeze/step で手順を実行する
  logger.py        # 毎tick、追跡対象の Pos / Motion を取得してCSVに保存する
  models/          # 理論モデル（現実の物理 / MC内部の式）
  plot.py          # 実測と理論を重ねたグラフ（動画に入れる素材）を出す
```

詳しくは `docs/MC実行基盤.md`。
