"""模擬サーバで E001 の全工程（実行 → CSV → 解析 → グラフ）を通す試験。
模擬サーバの物理は予想値で動くので、ここで確かめているのは「道具が正しく値を取り出せるか」であって、
MCの物理そのものではない。"""
from pathlib import Path

import pytest

from lab import parse
from lab.analyze import analyze
from lab.models import free_fall_mc as mc
from lab.plot import plot_run
from lab.rcon import Rcon, RconError
from lab.runner import Experiment, Runner
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
    with FakeRconServer("test", ground=exp.origin[1]) as srv, Rcon(srv.host, srv.port, "test") as conn:
        run_dir = Runner(exp, conn, log=lambda *_: None).run(tmp_path, mc_version="fake")

    result = analyze(run_dir)
    t = result["targets"]
    # 予想値どおりの物理を入れた模擬サーバなので、当てはめで同じ値が戻るはず
    assert t["pig"]["repeats"][0]["fit"]["g_ms2"] == pytest.approx(32.0, rel=1e-6)
    assert t["pig"]["repeats"][0]["fit"]["order"] == "move_then_accel"
    assert t["item"]["repeats"][0]["fit"]["order"] == "accel_then_move"
    assert t["anvil"]["repeats"][0]["landing_how"] == "消滅"   # 落下するブロックは着地で消える
    assert all(x["vs_expected"]["status"] == "予想どおり" for x in t.values())
    # 繰り返しで結果が変わらない（決定的）
    lt = t["pig"]["summary"]["landing_tick"]
    assert lt["min"] == lt["max"]
    assert result["landing_order"][0]["target"] == "pig"
    for name in ("measurements.csv", "results.json", "summary.md", "theory.csv", "meta.json"):
        assert (run_dir / name).exists()
    for p in plot_run(run_dir):
        assert p.stat().st_size > 10_000
