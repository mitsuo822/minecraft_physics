# lab

実験の実行・計測・解析のコード。使い方は `python -m lab --help`、サーバの準備は `mc/server/README.md`。

| ファイル | 役割 |
|---|---|
| `rcon.py` | RCON クライアント（依存なし） |
| `parse.py` | コマンド応答の読み取り。MCのバージョンで書式が違えばここを直す |
| `runner.py` | `experiment.yaml` を読み、`tick freeze` → 1tickずつ `tick step` しながら毎tick計測し、`measurements.csv` に書く |
| `analyze.py` | 当てはめ（g・空気抵抗・更新の順序）、着地順、予想値との比較 → `results.json`, `summary.md`, `theory.csv` |
| `plot.py` | 確認用のグラフ（PNG）。動画用の動くグラフは movie 側で作る |
| `models/free_fall_mc.py` | MC内部の落下の漸化式と当てはめ |
| `models/free_fall_real.py` | 現実の落下（真空、2乗の空気抵抗） |
| `models/mc_constants.yaml` | 予想値（【未確認】）。実測で確かめたら更新する |
| `sim/fake_server.py` | 模擬RCONサーバ。本物がない環境で全工程を試すためのもの。**出る数字は実測ではない** |

## 当てはめの考え方

どちらの更新の順序でも、速度は `v(t+1) = a·v(t) + b`（`a = 1 − d`, `b = −g(1 − d)`）という1次式になるので、
毎tickの Motion から最小二乗で g と d が決まる。順序（位置を先に動かすか、加速が先か）は、
位置の増え方 `y(t+1) − y(t)` が `v(t)` と `v(t+1)/a` のどちらに一致するかで判定する。
