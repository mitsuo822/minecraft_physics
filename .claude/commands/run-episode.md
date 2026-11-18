---
description: 人の番・失敗・前提不足のどれかで止まるまで、回の工程を続けて進める。引数：回のID（例 EP001）
---
1. `.venv/Scripts/python -m orchestra run $ARGUMENTS` をバックグラウンドで実行し、終わるのを待つ（数時間かかることがある）。
2. 終わったら `episodes/<回>/runlog.jsonl` の今回の行を読み、実行した工程・かかった時間・費用（cost_usd）を表にする。
3. 止まった理由と、人がやること（承認なら確認すべきファイル）を伝える。
4. 関門を承認したり、episode.yaml を直接書き換えたりしない。
