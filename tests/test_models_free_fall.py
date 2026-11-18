"""E001 の理論モデル（現実とMC）の試験。

- 次元の確認: 単位系を変えても物理量が正しく変換されること（長さ・時間・質量のスケーリング）
- 既知値の再現: 出典（Minecraft Wiki、research.md）にある値をモデルが出すこと
- model.md の予想値の表がコードの出力と一致すること（文書に手書きの数字を置かない）
"""
import math
from pathlib import Path

import pytest

from lab.models import e001_predictions as pred
from lab.models import free_fall_mc as mc
from lab.models import free_fall_real as real

ROOT = Path(__file__).resolve().parents[1]


# --- 現実: 次元 ---------------------------------------------------------

@pytest.mark.parametrize("lam,tau,mu", [(100.0, 1.0, 1.0), (1.0, 60.0, 1.0), (1.0, 1.0, 1000.0), (3.28, 0.5, 2.2)])
def test_real_dimensions_by_scaling(lam, tau, mu):
    """長さを lam 倍、時間を tau 倍、質量を mu 倍の単位で書き直しても、結果が次元どおりに変わる。"""
    m, rho, cd, area, g, h = 90.0, 1.2, 1.0, 0.7, real.G_EARTH, 256.0
    g2 = g * lam / tau ** 2
    vt = real.terminal_velocity(m, rho, cd, area, g)
    vt2 = real.terminal_velocity(m * mu, rho * mu / lam ** 3, cd, area * lam ** 2, g2)
    assert vt2 == pytest.approx(vt * lam / tau, rel=1e-12)                 # [L/T]
    assert real.fall_time_vacuum(h * lam, g2) == pytest.approx(real.fall_time_vacuum(h, g) * tau, rel=1e-12)  # [T]
    assert real.fall_time_quadratic_drag(h * lam, vt2, g2) == pytest.approx(
        real.fall_time_quadratic_drag(h, vt, g) * tau, rel=1e-9)
    y, v = real.quadratic_drag(h, 3.0, vt, g)
    y2, v2 = real.quadratic_drag(h * lam, 3.0 * tau, vt2, g2)
    assert (y2, v2) == (pytest.approx(y * lam, rel=1e-9), pytest.approx(v * lam / tau, rel=1e-9))


# --- 現実: 既知値・極限 ---------------------------------------------------

def test_real_vacuum_known_values():
    # research.md §1: 256 m を真空で落ちる時間 7.226 s（g=9.80665）/ 7.228 s（g=9.8）
    assert real.fall_time_vacuum(256) == pytest.approx(7.226, abs=5e-4)
    assert real.fall_time_vacuum(256, real.G_EARTH_ROUND) == pytest.approx(7.228, abs=5e-4)
    y, v = real.vacuum(256, real.fall_time_vacuum(256))
    assert y == pytest.approx(0, abs=1e-9) and v == pytest.approx(math.sqrt(2 * real.G_EARTH * 256))


def test_real_drag_limits():
    # 終端速度が非常に大きければ真空と同じ、時間が十分たてば終端速度に達する
    assert real.fall_time_quadratic_drag(256, 1e5) == pytest.approx(real.fall_time_vacuum(256), rel=1e-6)
    assert real.quadratic_drag(0, 1e-4, 50)[1] == pytest.approx(real.G_EARTH * 1e-4, rel=1e-6)
    assert real.quadratic_drag(0, 60, 50)[1] == pytest.approx(50, rel=1e-9)
    # 空気中は真空より必ず遅い
    assert real.fall_time_quadratic_drag(256, 55) > real.fall_time_vacuum(256)
    # 逆関数になっている
    t = real.fall_time_quadratic_drag(256, 40)
    assert real.quadratic_drag(256, t, 40)[0] == pytest.approx(0, abs=1e-9)


def test_terminal_velocity_definition():
    # 終端速度では抵抗 ½ρC_dAv² が重さ mg とつり合う
    m, rho, cd, area = 90.0, 1.225, 1.0, 0.7
    vt = real.terminal_velocity(m, rho, cd, area)
    assert 0.5 * rho * cd * area * vt ** 2 == pytest.approx(m * real.G_EARTH, rel=1e-12)


# --- MC: 次元・換算 ------------------------------------------------------

def test_mc_unit_conversion():
    assert mc.accel_ms2(1.0) == mc.BLOCK_M * mc.TICKS_PER_SEC ** 2      # ブロック/tick² → m/s²
    assert mc.speed_ms(1.0) == mc.BLOCK_M * mc.TICKS_PER_SEC            # ブロック/tick → m/s
    # g [ブロック/tick²] は「1tickあたりの速度変化」なので、g·(1-d)/d に 1tick を掛けた量 = ブロック/tick
    assert mc.speed_ms(mc.terminal_velocity(0.08, 0.02)) == pytest.approx(78.4)


# --- MC: 出典の既知値（Minecraft Wiki "Entity"、research.md §2）------------

@pytest.mark.parametrize("key,vt,vt_ms", [("pig", 3.92, 78.4), ("falling_block", 1.96, 39.2), ("item", 1.96, 39.2)])
def test_mc_terminal_known(key, vt, vt_ms):
    c = mc.load_constants()["types"][key]
    assert mc.terminal_velocity(c["g"], c["d"]) == pytest.approx(vt)
    assert mc.speed_ms(mc.terminal_velocity(c["g"], c["d"])) == pytest.approx(vt_ms)


@pytest.mark.parametrize("key,g_ms2,ratio", [("pig", 32.0, 3.2631), ("falling_block", 16.0, 1.6316)])
def test_mc_ratio_known(key, g_ms2, ratio):
    p = mc.predict(key, 256)
    assert p.g_ms2 == pytest.approx(g_ms2)
    assert p.ratio(real.G_EARTH) == pytest.approx(ratio, abs=1e-4)


def test_mc_step_distance_and_first_tick():
    # research.md §2: 終端で1tickに動く距離 生物 3.92、落下ブロック・アイテム 2.00
    assert mc.predict("pig", 256).terminal_step == pytest.approx(3.92)
    assert mc.predict("item", 256).terminal_step == pytest.approx(2.00)
    # 生物は位置→加速なので1tick目は動かない。アイテムは加速→位置なので g だけ動く
    assert mc.predict("pig", 256).first_tick_drop == 0
    assert mc.predict("item", 256).first_tick_drop == pytest.approx(0.04)


def test_mc_terminal_is_fixed_point_and_reached():
    for order in mc.ORDERS:
        ys = mc.simulate(0, 0, 0.08, 0.02, order, 2000)
        assert -ys[-1][2] == pytest.approx(mc.terminal_velocity(0.08, 0.02), rel=1e-12)
        assert ys[-2][1] - ys[-1][1] == pytest.approx(mc.terminal_step(0.08, 0.02, order), rel=1e-9)


def test_mc_drag_is_linear_in_speed():
    # 終端速度との差が毎tick (1-d) 倍 → 抵抗は速さに比例（現実の空気の2乗とは違う）
    vt = mc.terminal_velocity(0.08, 0.02)
    s = mc.simulate(0, 0, 0.08, 0.02, "move_then_accel", 10)
    gaps = [vt + v for _, _, v in s]
    for a, b in zip(gaps, gaps[1:]):
        assert b / a == pytest.approx(0.98, rel=1e-12)
    assert mc.time_constant_s(0.02) == pytest.approx(-1 / (20 * math.log(0.98)))


def test_mc_landing_ticks_match_notes():
    # notes.md の模擬サーバの結果（256 ブロック）: 豚 110 tick、金床・鉄インゴット 176 tick
    assert mc.predict("pig", 256).landing_tick == 110
    assert mc.predict("falling_block", 256).landing_tick == 176
    assert mc.predict("item", 256).landing_tick == 176


def _closed_form_drop(n: int, g: float, d: float, order: str) -> float:
    """n tick 後の落下量の閉じた式（初速0）。漸化式を使わない独立の計算。"""
    q = 1 - (1 - d) ** n
    if order == "move_then_accel":
        return g * (1 - d) / d * (n - q / d)
    return g / d * (n - (1 - d) * q / d)


@pytest.mark.parametrize("key", ["pig", "falling_block", "item"])
def test_closed_form_matches_recursion(key):
    c = mc.load_constants()["types"][key]
    for t, y, _ in mc.simulate(0.0, 0.0, c["g"], c["d"], c["order"], 300):
        assert -y == pytest.approx(_closed_form_drop(t, c["g"], c["d"], c["order"]), abs=1e-9)


def test_review_hand_values():
    # review_design.md §0・S2・S3 の手計算（3.92·[n − 50(1 − 0.98ⁿ)]、2n − 98(1 − 0.98ⁿ)）
    assert _closed_form_drop(109, 0.08, 0.02, "move_then_accel") == pytest.approx(252.95, abs=5e-3)
    assert _closed_form_drop(110, 0.08, 0.02, "move_then_accel") == pytest.approx(256.44, abs=5e-3)
    assert _closed_form_drop(175, 0.04, 0.02, "accel_then_move") == pytest.approx(254.86, abs=5e-3)
    assert _closed_form_drop(176, 0.04, 0.02, "accel_then_move") == pytest.approx(256.80, abs=5e-3)
    pig, anvil = mc.predict("pig", 256), mc.predict("falling_block", 256)
    assert mc.speed_ms(pig.max_motion) == pytest.approx(69.7, abs=0.05)       # S2: 豚は終端の 89%
    assert pig.terminal_fraction == pytest.approx(0.89, abs=0.005)
    assert mc.speed_ms(anvil.max_motion) == pytest.approx(38.1, abs=0.05)     # 金床は 97%
    assert anvil.terminal_fraction == pytest.approx(0.97, abs=0.005)
    assert anvil.gap_before_landing == pytest.approx(1.14, abs=5e-3)          # S3: 着地直前は地面の上 1.14
    # 地球比の3つ目の定義（§3-9）: 終端速度 ÷ 時定数 = 31.68 m/s²、3.230 倍
    assert pig.continuous_accel_ms2 == pytest.approx(31.68, abs=5e-3)
    assert pig.continuous_accel_ms2 / real.G_EARTH == pytest.approx(3.230, abs=5e-4)
    # S2: 終端の 95% / 99% に届くまで（生物）約149 tick・約400 ブロック / 約228 tick・約700 ブロック
    t95, d95 = mc.reach_fraction(0.95, 0.08, 0.02, "move_then_accel")
    t99, d99 = mc.reach_fraction(0.99, 0.08, 0.02, "move_then_accel")
    assert (t95, t99) == (149, 228)
    assert d95 == pytest.approx(400, rel=0.01) and d99 == pytest.approx(700, rel=0.01)


@pytest.mark.parametrize("key", ["pig", "cow", "armor_stand", "falling_block", "item"])
def test_landing_check_passes_on_prediction(key):
    """S3: experiment.yaml の金床の確認項目（次の1tickで地面に届く位置で消えた）が、予想どおりの値で通る。
    古い項目（地面から1ブロック以内）は、予想どおりでも外れていた。"""
    p = mc.predict(key, 256)
    assert p.gap_before_landing <= p.next_step_before_landing
    assert p.gap_before_landing > 0
    if key == "falling_block":
        assert p.gap_before_landing > 1.0   # 古い確認項目は予想どおりでも外れる
        assert p.landing_tick < 600         # 時間切れ（600 tick【二次】）より前


def test_reach_fraction_is_monotonic_and_consistent():
    c = mc.load_constants()["types"]["pig"]
    t, dist = mc.reach_fraction(0.5, c["g"], c["d"], c["order"])
    s = mc.simulate(0.0, 0.0, c["g"], c["d"], c["order"], t)
    assert -s[t][2] >= 0.5 * mc.terminal_velocity(c["g"], c["d"]) > -s[t - 1][2]
    assert dist == pytest.approx(-s[t][1])


def test_fit_drag_then_accel_reading():
    """「抵抗→加速」（v' = v(1-d) - g）の列を当てはめると g が 1/(1-d) 倍に出る。g_if_drag_then_accel で元に戻る。"""
    g, d, v, samples = 0.08, 0.02, 0.0, []
    y = 100.0
    for t in range(60):
        samples.append((t, y, v))
        y, v = y + v, v * (1 - d) - g
    f = mc.fit(samples)
    assert f.d == pytest.approx(d, rel=1e-9)
    assert f.g == pytest.approx(g / (1 - d), rel=1e-9)
    assert f.g_if_drag_then_accel == pytest.approx(g, rel=1e-9)


def test_every_target_has_constants_and_same_type_agrees():
    """S1: 全対象の種類に定数があり、生物・落下ブロック・アイテムのそれぞれに比べる組がある。"""
    import yaml
    exp = yaml.safe_load((ROOT / "experiments/E001_free_fall/experiment.yaml").read_text(encoding="utf-8"))
    consts = mc.load_constants()["types"]
    by_type: dict[str, list[str]] = {}
    for tid, _, key in pred.targets(exp):
        assert key in consts, f"{tid} の種類 {key} が mc_constants.yaml にない"
        by_type.setdefault(key, []).append(tid)
    # 同じ種類で重さの印象が違う組が、生物・落下ブロック・アイテムのそれぞれにある
    groups: dict[str, int] = {}
    for key, ids in by_type.items():
        groups[consts[key]["group"]] = groups.get(consts[key]["group"], 0) + len(ids)
    assert groups["生物"] >= 3 and groups["落下するブロック"] >= 2 and groups["アイテム"] >= 3


def _exp() -> dict:
    import yaml
    return yaml.safe_load((ROOT / "experiments/E001_free_fall/experiment.yaml").read_text(encoding="utf-8"))


def test_groups_are_same_type_and_exclude_noai():
    """C2: analysis.groups の各組は同じ種類のグループで2つ以上。予想を出さない対象（NoAI の豚）は組に入らない。"""
    exp = _exp()
    ents = {e["id"]: e for e in exp["setup"]["entities"]}
    consts = mc.load_constants()["types"]
    no_pred = {tid for tid, _ in pred.unpredicted(exp)}
    assert no_pred == {"pig_noai"}
    for g in exp["analysis"]["groups"]:
        assert len(g["members"]) >= 2
        assert not set(g["members"]) & no_pred
        kinds = {consts[mc.entity_key(ents[m]["summon"])]["group"] for m in g["members"]}
        assert len(kinds) == 1, f"{g['name']} に違うグループの種類が混ざっている"
    # NoAI の豚は終了条件から外れ、別の問いとして扱われる
    assert no_pred <= set(exp["measure"]["until"]["not_required_to_land"])
    assert {s["id"] for s in exp["analysis"]["separate"]} == no_pred
    # 予想の表に NoAI の豚の着地 tick が出ない
    body = pred.table()
    assert "| 豚（NoAI） |" not in body


def test_auto_checks_are_implemented():
    """experiment.yaml の checks（auto: true）と lab/analyze.py の判定が1対1に対応する。"""
    from lab.analyze import CHECKS
    ids = [c["id"] for c in _exp()["analysis"]["checks"] if c.get("auto")]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(CHECKS)


def test_version_and_commands_for_26_3():
    """C1・C3: mc_version が揃っていて、ゲームルール名が新しい書式、金床の確認がタグ。"""
    import yaml
    exp = _exp()
    ep = yaml.safe_load((ROOT / "episodes/EP001_free_fall/episode.yaml").read_text(encoding="utf-8"))
    assert exp["mc_version"] == ep["mc_version"] == str(mc.load_constants()["mc_version"]) == "26.3"
    for name in exp["world"]["gamerules"]:
        assert name == name.lower(), f"ゲームルール名 {name} は 1.21.11 以降の書式（snake_case）でない"
    cmds = [s["cmd"] for s in exp["procedure"] if "cmd" in s]
    assert any("#minecraft:anvil" in c for c in cmds)
    assert not any(c.endswith(" minecraft:anvil") for c in cmds)


def test_mc_mass_does_not_appear():
    # MCモデルの入力に質量はない（種類の定数だけで決まる）
    assert set(mc.load_constants()["types"]["falling_block"]) == {"g", "d", "order", "group"}


# --- 文書とコードの一致 ----------------------------------------------------

def test_model_md_table_is_generated():
    md = (ROOT / "experiments/E001_free_fall/model.md").read_text(encoding="utf-8")
    start, end = md.index(pred.BEGIN), md.index(pred.END) + len(pred.END)
    assert md[start:end].strip() == pred.table().strip(), \
        "model.md の予想値の表が古い。python -m lab.models.e001_predictions の出力を貼り直す"


def test_experiment_yaml_has_no_hand_written_predictions():
    import yaml
    exp = yaml.safe_load((ROOT / "experiments/E001_free_fall/experiment.yaml").read_text(encoding="utf-8"))
    for key in ("expected", "prediction", "predictions_values"):
        assert key not in exp
    assert pred.drop_height(exp) == 256
