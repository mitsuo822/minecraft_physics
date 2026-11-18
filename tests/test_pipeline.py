"""模擬サーバで E001 の全工程（実行 → CSV → 解析 → グラフ）を通す試験。
模擬サーバの物理は予想値で動くので、ここで確かめているのは「道具が正しく値を取り出せるか」であって、
MCの物理そのものではない。"""
from pathlib import Path

import pytest

from lab import parse
from lab.analyze import analyze, load_rows
from lab.models import free_fall_mc as mc
from lab.plot import plot_run
from lab.rcon import Rcon, RconError
from lab.runner import Experiment, Runner, read_server_version
from lab.sim.fake_server import FakeRconServer

E001 = Path(__file__).resolve().parents[1] / "experiments/E001_free_fall/experiment.yaml"


def test_parse_responses():
    assert parse.parse_vec3("Pig has the following entity data: [0.5d, 196.0d, -1.0E-4d]") == (0.5, 196.0, -1.0e-4)
    assert parse.parse_byte("Pig has the following entity data: 1b") == 1
    assert parse.parse_gametime("The time is 12345") == 12345
    assert parse.is_no_entity("No entity was found")
    with pytest.raises(parse.ParseError):
        parse.parse_vec3("Unknown command")


def test_wrong_password_is_rejected():
    with FakeRconServer("right") as srv:
        with pytest.raises(RconError):
            Rcon(srv.host, srv.port, "wrong").connect()


@pytest.mark.parametrize("order", mc.ORDERS)
def test_fit_recovers_parameters(order):
    samples = mc.simulate(100.0, 0.0, 0.08, 0.02, order, 60)
    f = mc.fit(samples)
    assert f.g == pytest.approx(0.08, rel=1e-9)
    assert f.d == pytest.approx(0.02, rel=1e-9)
    assert f.order == order


def test_e001_end_to_end(tmp_path):
    exp = Experiment.load(E001)
    exp.raw["measure"]["repeats"] = 2
    # 本物のサーバと同じく、起動ログに版の行がある状態を作る（K1: 版の証拠は起動ログから読む）
    log = tmp_path / "latest.log"
    log.write_text(f"[11:00:00] [Server thread/INFO]: Starting minecraft server version {exp.raw['mc_version']}\n",
                   encoding="utf-8")
    with FakeRconServer("test", ground=exp.origin[1]) as srv, Rcon(srv.host, srv.port, "test") as conn:
        run_dir = Runner(exp, conn, log=lambda *_: None).run(tmp_path, mc_version="fake",
                                                            server_version=read_server_version(log))

    result = analyze(run_dir)
    t = result["targets"]
    # 予想値どおりの物理を入れた模擬サーバなので、当てはめで同じ値が戻るはず
    assert t["pig"]["repeats"][0]["fit"]["g_ms2"] == pytest.approx(32.0, rel=1e-6)
    assert t["pig"]["repeats"][0]["fit"]["order"] == "move_then_accel"
    assert t["item"]["repeats"][0]["fit"]["order"] == "accel_then_move"
    assert t["anvil"]["repeats"][0]["landing_how"] == "消滅"   # 落下するブロックは着地で消える
    assert all(x["vs_expected"]["status"] == "予想どおり" for x in t.values() if x["predicted"])
    assert t["pig_noai"]["vs_expected"]["status"] == "比較できない"    # 予想を出さない対象
    # 繰り返しで結果が変わらない（決定的）
    lt = t["pig"]["summary"]["landing_tick"]
    assert lt["min"] == lt["max"]
    assert result["landing_order"][0]["target"] == "pig"
    for name in ("measurements.csv", "results.json", "summary.md", "theory.csv", "meta.json",
                 "commands.jsonl", "realtime.csv"):
        assert (run_dir / name).exists()
    for p in plot_run(run_dir):
        assert p.stat().st_size > 10_000

    # checks がすべて自動で判定され、模擬サーバ（予想どおりの物理）では合格する
    assert {c["status"] for c in result["checks"]} == {"合格"}
    assert result["ok_to_conclude"]
    assert all(g["match"] for g in result["groups"] + result["across"])
    # NoAI の豚は別の問い。模擬サーバは「落ちない」予想で動かしている。着地の順番に入らない
    (sep,) = result["separate"]
    assert sep["id"] == "pig_noai" and sep["fell"] is False
    assert "pig_noai" not in [o["target"] for o in result["landing_order"]]
    # 終了条件から外したので、max_ticks まで走らない
    assert max(r["tick"] for r in load_rows(run_dir)) < 400

    # summary.md: 【実測】と（計算値）を列名で分ける（C4）
    md = (run_dir / "summary.md").read_text(encoding="utf-8")
    assert "到達した最大の速さ・Motion（m/s） 【実測】" in md
    assert "終端速度（m/s）（計算値）" in md
    assert "| 終端速度（m/s） |" not in md and "地球の何倍" not in md
    assert "①当てはめた g パラメータ" in md and "②1tick目の Motion の変化" in md and "③連続時間の等価加速度" in md
    assert "模擬サーバの結果" in md


def test_failed_setup_command_stops_conclusion(tmp_path):
    """setup のコマンドが失敗したら（ゲームルール名が版に合わない等）、結論を出さない。"""
    import json
    exp = Experiment.load(E001)
    exp.raw["measure"]["repeats"] = 2
    exp.raw["measure"].pop("realtime_check")
    with FakeRconServer("test", ground=exp.origin[1]) as srv, Rcon(srv.host, srv.port, "test") as conn:
        run_dir = Runner(exp, conn, log=lambda *_: None).run(tmp_path, mc_version="fake")
    first = analyze(run_dir)
    assert {c["id"]: c["status"] for c in first["checks"]}["realtime"] == "未実施"   # 通常速度の確認なし → 結論を出さない
    assert not first["ok_to_conclude"]
    with (run_dir / "commands.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({"repeat": 0, "phase": "setup", "tick": None, "cmd": "gamerule doMobSpawning false",
                            "response": "Incorrect argument for command\n...doMobSpawning<--[HERE]",
                            "error": True, "check": None}) + "\n")
    result = analyze(run_dir)
    status = {c["id"]: c["status"] for c in result["checks"]}
    assert status["setup_ok"] == "不合格" and not result["ok_to_conclude"]


def test_command_error_detection():
    assert parse.is_command_error("Unknown or incomplete command, see below for error\n...<--[HERE]")
    assert not parse.is_command_error("Gamerule advance_time is now set to: false")
    assert not parse.is_command_error("No entity was found")       # 後片付けで対象がない
    assert not parse.is_command_error("Test failed")                # execute if の判定結果
    assert parse.execute_test_result("Test passed") is True
    assert parse.execute_test_result("Test failed") is False


def test_anvil_tag_accepts_damaged_anvil():
    """C3: 着地で傷んだ金床でも #minecraft:anvil なら通る（模擬サーバのタグの扱いの確認）。"""
    from lab.sim.fake_server import World
    w = World(ground=-60)
    w.blocks[(0, -60, 0)] = "chipped_anvil"
    assert w.handle("execute if block 0 -60 0 #minecraft:anvil") == "Test passed"
    assert w.handle("execute if block 0 -60 0 minecraft:anvil") == "Test failed"


def test_series_match_and_realtime_windows():
    from lab.analyze import realtime_windows, series_match
    a = {0: [196.0, 0.0], 1: [196.0, -0.0784]}
    assert series_match(a, dict(a))["match"]
    assert not series_match(a, {0: [196.0, 0.0]})["match"]                  # 空中の tick が違う
    assert not series_match(a, {0: [196.0, 0.0], 1: [196.0, -0.0785]})["match"]
    rt = [{"poll": 0, "tick_lo": 107, "tick_hi": 108, "target": "pig", "exists": 1, "on_ground": 0},
          {"poll": 1, "tick_lo": 109, "tick_hi": 110, "target": "pig", "exists": 1, "on_ground": 1}]
    w = realtime_windows(rt, set())["pig"]
    assert (w["lo"], w["hi"], w["width"]) == (108, 110, 3)
