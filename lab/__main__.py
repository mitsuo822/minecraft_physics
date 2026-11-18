"""使い方:

    # 実験を実行して計測（結果は experiments/<実験>/results/run_*/ に出る）→ 続けて解析・グラフ
    python -m lab run experiments/E001_free_fall/experiment.yaml --mc-version 1.21.x

    # 既存の計測結果を解析し直す
    python -m lab analyze experiments/E001_free_fall/results/run_20261118_120000

    # 送るコマンドを表示するだけ（サーバに接続しない）
    python -m lab run experiments/E001_free_fall/experiment.yaml --dry-run

    # 本物のサーバの代わりに模擬サーバで試す（数字は実測ではない）
    python -m lab run experiments/E001_free_fall/experiment.yaml --fake

接続先: --host / --port、パスワードは環境変数 MC_RCON_PASSWORD（または --password）。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .analyze import analyze
from .plot import plot_run
from .rcon import Rcon
from .runner import Experiment, Runner, cleanup_commands, expand_step, setup_commands, read_server_version


def _post(run_dir: Path) -> None:
    analyze(run_dir)
    for p in plot_run(run_dir):
        print(f"グラフ: {p}")
    print((run_dir / "summary.md").read_text(encoding="utf-8"))


def cmd_run(a: argparse.Namespace) -> int:
    exp = Experiment.load(a.experiment)
    if a.dry_run:
        for c in setup_commands(exp) + cleanup_commands(exp):
            print(c)
        for step in exp.raw.get("procedure", []):
            for c in expand_step(exp, step):
                print(f"[t={step['tick']}] {c}")
        return 0
    out_root = Path(a.out) if a.out else None
    if a.fake:
        from .sim.fake_server import FakeRconServer
        with FakeRconServer("test", ground=exp.origin[1]) as srv, Rcon(srv.host, srv.port, "test") as conn:
            print("※ 模擬サーバで実行します。数字は実測ではありません。")
            run_dir = Runner(exp, conn, log=print).run(out_root or Path(a.fake_out), mc_version="fake",
                                                     server_version={"server_version": "fake",
                                                                     "server_version_source": "模擬サーバ"})
    else:
        password = a.password or os.environ.get("MC_RCON_PASSWORD")
        if not password:
            print("RCONのパスワードを MC_RCON_PASSWORD か --password で指定してください", file=sys.stderr)
            return 2
        sv = read_server_version(a.server_log)
        print(f"サーバの版: {sv.get('server_version') or '不明'}（{sv.get('server_version_line') or sv['server_version_source']}）")
        with Rcon(a.host, a.port, password) as conn:
            run_dir = Runner(exp, conn, log=print).run(out_root, mc_version=a.mc_version,
                                                       unfreeze=not a.keep_frozen, server_version=sv)
    print(f"計測結果: {run_dir}")
    _post(run_dir)
    return 0


def cmd_analyze(a: argparse.Namespace) -> int:
    _post(Path(a.run_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lab", description="MC物理実験の実行・計測・解析")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="実験を実行して計測し、解析する")
    r.add_argument("experiment")
    r.add_argument("--host", default="127.0.0.1")
    r.add_argument("--port", type=int, default=25575)
    r.add_argument("--password")
    r.add_argument("--mc-version", help="サーバのMCバージョン（記録用）")
    r.add_argument("--server-log", default="mc/server/logs/latest.log",
                   help="サーバの起動ログ。ここから実際の版を読んで meta.json に残す")
    r.add_argument("--out", help="結果の出力先（既定: 実験のディレクトリの results/）")
    r.add_argument("--keep-frozen", action="store_true", help="終わったあとも tick freeze のままにする")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--fake", action="store_true", help="模擬サーバで実行（試験用）")
    r.add_argument("--fake-out", default="media/fake_runs", help="--fake のときの出力先（git外）")
    r.set_defaults(func=cmd_run)
    an = sub.add_parser("analyze", help="計測結果を解析し直す")
    an.add_argument("run_dir")
    an.set_defaults(func=cmd_analyze)
    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
