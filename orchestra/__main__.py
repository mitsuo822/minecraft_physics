"""使い方（リポジトリのルートで実行する）:

    python -m orchestra new EP002 --slug ice-friction --experiment experiments/E004_ice_friction --theme T04 --series A
    python -m orchestra status EP002           # 工程表を表示
    python -m orchestra next EP002             # 次の工程を1つだけ実行
    python -m orchestra run EP002              # 関門・人の作業・失敗で止まるまで続けて実行
    python -m orchestra run EP002 --dry-run    # 何が実行されるかだけ表示
    python -m orchestra approve EP002 design --by 和田    # 関門の承認（theme / design / publish）
    python -m orchestra done EP002 capture     # 人の作業が終わった
    python -m orchestra skip EP002 measure --reason "解説だけの回"
    python -m orchestra reset EP002 script --feedback episodes/EP002_x/review_final.md
    python -m orchestra check EP002            # 台帳の数字チェック

エージェントは `claude -p --agent <名前>` で呼ぶ。別のコマンドを使うときは環境変数 ORCHESTRA_CLAUDE に書く。
終了コード: 0=工程完了 10=人の番 20=失敗 30=前提不足 40=差し戻し 50=全工程完了
"""
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import sys
from pathlib import Path

from . import engine
from .check import check_ledger

def _root() -> Path:
    """作業するリポジトリのルート。ORCHESTRA_ROOT、カレントディレクトリ、このパッケージの親の順に探す。"""
    for cand in (os.environ.get("ORCHESTRA_ROOT"), Path.cwd()):
        if cand and (Path(cand) / "episodes").is_dir():
            return Path(cand)
    return Path(__file__).resolve().parent.parent


ROOT = _root()


def claude_cmd() -> list[str]:
    raw = os.environ.get("ORCHESTRA_CLAUDE")
    if raw:
        return shlex.split(raw, posix=os.name != "nt")
    exe = shutil.which("claude")
    if not exe:
        raise SystemExit("claude コマンドが見つかりません（Claude Code をインストールしてください）")
    return [exe]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(prog="python -m orchestra", description="動画1本の工程を進める")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="新しい回を作る")
    p.add_argument("episode")
    p.add_argument("--slug", required=True)
    p.add_argument("--experiment", required=True, help="experiments/Exxx_名前（まだ無くてもよい）")
    p.add_argument("--title", default="")
    p.add_argument("--theme", default="")
    p.add_argument("--series", default="")
    p.add_argument("--mc-version", default="TBD")

    for name, hlp in [("status", "工程表"), ("check", "台帳の機械チェック")]:
        sub.add_parser(name, help=hlp).add_argument("episode")
    for name, hlp in [("next", "次の工程を1つ実行"), ("run", "止まるまで続けて実行")]:
        p = sub.add_parser(name, help=hlp)
        p.add_argument("episode")
        p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("approve", help="関門を承認する")
    p.add_argument("episode")
    p.add_argument("approval", help="theme / design / publish")
    p.add_argument("--by", required=True)
    p.add_argument("--note")

    for name in ("done", "skip"):
        p = sub.add_parser(name, help="人の作業が終わった" if name == "done" else "工程を飛ばす")
        p.add_argument("episode")
        p.add_argument("step")
        p.add_argument("--reason", required=(name == "skip"))

    p = sub.add_parser("reset", help="工程をやり直す（後ろの自動工程も戻す）")
    p.add_argument("episode")
    p.add_argument("step")
    p.add_argument("--feedback", help="直す理由が書いてあるファイル")

    a = ap.parse_args(argv)

    if a.cmd == "new":
        dest = engine.new_episode(ROOT, a.episode, a.slug, a.experiment, a.title, a.theme, a.series, a.mc_version)
        print(f"作成: {dest.relative_to(ROOT).as_posix()}")
        print(engine.status_table(ROOT, a.episode))
        return 0
    if a.cmd == "status":
        print(engine.status_table(ROOT, a.episode))
        return 0
    if a.cmd == "check":
        ep = engine.Episode(ROOT, a.episode)
        ng = check_ledger(ep.dir / "ledger.json")
        print("OK" if not ng else f"NG {len(ng)}件")
        for line in ng:
            print(f"- {line}")
        return 1 if ng else 0
    if a.cmd in ("next", "run"):
        code = engine.advance(ROOT, a.episode, [] if a.dry_run else claude_cmd(),
                              loop=(a.cmd == "run"), dry_run=a.dry_run)
        if not a.dry_run:
            print()
            print(engine.status_table(ROOT, a.episode))
        return code
    if a.cmd == "approve":
        engine.approve(ROOT, a.episode, a.approval, a.by, a.note)
        print(engine.status_table(ROOT, a.episode))
        return 0
    if a.cmd in ("done", "skip"):
        engine.mark(ROOT, a.episode, a.step, "done" if a.cmd == "done" else "skipped", a.reason)
        print(engine.status_table(ROOT, a.episode))
        return 0
    if a.cmd == "reset":
        ids = engine.reset(ROOT, a.episode, a.step, a.feedback)
        print(f"未実行に戻した工程: {', '.join(ids)}")
        print(engine.status_table(ROOT, a.episode))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
