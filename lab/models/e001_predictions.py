"""E001 の予想値の表を、experiment.yaml と mc_constants.yaml から作る。

    python -m lab.models.e001_predictions

出力は experiments/E001_free_fall/model.md の「予想値」節に貼る（tests/test_models_free_fall.py が一致を確かめる）。
数字はすべてここで計算する。文書に手で書かない。
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml

from . import free_fall_mc as mc
from . import free_fall_real as real

ROOT = Path(__file__).resolve().parents[2]
E001 = ROOT / "experiments/E001_free_fall/experiment.yaml"

# 人の終端速度の例: FAI の「約 200 km/h」（腹這い姿勢）【二次】。比べる相手の例として使うだけ。
SKYDIVER_VT_MS = 200 / 3.6

# 終端に「届いた」とみなす割合の例（どこまで届けば終端と言えるかを、高さの必要量で示すため）
REACH_FRACTIONS = (0.95, 0.99)

BEGIN = "<!-- BEGIN predictions (python -m lab.models.e001_predictions) -->"
END = "<!-- END predictions -->"


def spawn_heights(exp: dict) -> dict[str, float]:
    """対象 id → 落とす高さ（地面 = setup.origin からのブロック数）。"""
    out: dict[str, float] = {}
    for s in exp["procedure"]:
        for eid in s.get("spawn", []):
            out[eid] = float(s["at"][1])
    return out


def drop_height(exp: dict) -> float:
    """全対象に共通の高さ。対象ごとに高さが違う設計なら止める（表の前提が1つでなくなるため）。"""
    hs = set(spawn_heights(exp).values())
    if len(hs) != 1:
        raise ValueError(f"落とす高さが1つではありません: {sorted(hs)}")
    return hs.pop()


def targets(exp: dict, *, predicted_only: bool = True) -> list[tuple[str, str, str]]:
    """(id, label, 種類キー)。predicted_only なら、落下の予想を出さない対象（entity の predict: false）を除く。"""
    ents = {e["id"]: e for e in exp["setup"]["entities"]}
    return [(t, ents[t].get("label", t), mc.entity_key(ents[t]["summon"])) for t in exp["measure"]["targets"]
            if not predicted_only or ents[t].get("predict", True)]


def unpredicted(exp: dict) -> list[tuple[str, str]]:
    """落下の予想を出さない対象の (id, label)。"""
    have = {t for t, _, _ in targets(exp)}
    return [(t, label) for t, label, _ in targets(exp, predicted_only=False) if t not in have]


def table(exp_path: Path = E001) -> str:
    exp = yaml.safe_load(exp_path.read_text(encoding="utf-8"))
    consts = mc.load_constants()
    h = drop_height(exp)
    tps = mc.TICKS_PER_SEC
    tg = targets(exp)
    by_type: dict[str, list[str]] = {}
    for _, label, key in tg:
        by_type.setdefault(key, []).append(label)

    L = [BEGIN, "",
         f"前提: 高さ {h:g} ブロック、初速0、1ブロック={mc.BLOCK_M:g} m、1秒={tps} tick。"
         f"MC定数の確度: {consts['confidence']}（mc_version: {consts['mc_version']}）", "",
         "### MC: 種類ごとの定数と地球比（モデルの予想）", "",
         "地球比は3通りの定義で出す（どれで言うかは台本で決め、定義を画面に出す）。", "",
         "| 種類 | この種類の対象 | 順序 | g（ブロック/tick²） | ①g パラメータ（m/s²） | ①地球比（9.80665） | ①地球比（9.8） "
         "| ②1tick目のMotion変化（m/s²） | ②地球比（9.80665） | ③連続時間の等価加速度（m/s²） | ③地球比（9.80665） |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, labels in by_type.items():
        p = mc.predict(key, h, consts)
        L.append(f"| {key} | {'・'.join(labels)} | {p.order} | {p.g:g} | {p.g_ms2:.4g} | {p.ratio(real.G_EARTH):.3f} | "
                 f"{p.ratio(real.G_EARTH_ROUND):.3f} | {p.first_dv_ms2:.4g} | {p.first_dv_ms2 / real.G_EARTH:.3f} | "
                 f"{p.continuous_accel_ms2:.4g} | {p.continuous_accel_ms2 / real.G_EARTH:.3f} |")

    L += ["", "### MC: 対象ごとの落下（モデルの予想）", "",
          "同じ種類の対象は、モデルでは y(t) が tick ごとに完全に同じになる（入力に質量がないため）。", "",
          "| 対象 | 種類 | 1tick目の落下（ブロック） | 終端Motion（m/s） | 終端で1tickに動く距離（m/s） | 時定数（s） "
          "| 着地tick | 着地時刻（s） | 着地直前のMotion（m/s） | 終端に対する割合 | 着地直前の地面からの高さ（ブロック） | その次の1tickの移動（ブロック） |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, label, key in tg:
        p = mc.predict(key, h, consts)
        L.append(f"| {label} | {key} | {p.first_tick_drop:g} | {mc.speed_ms(p.terminal_motion):.4g} | "
                 f"{mc.speed_ms(p.terminal_step):.4g} | {p.time_constant_s:.3g} | {p.landing_tick} | "
                 f"{p.landing_tick / tps:.2f} | {mc.speed_ms(p.max_motion):.3g} | {p.terminal_fraction:.0%} | "
                 f"{p.gap_before_landing:.2f} | {p.next_step_before_landing:.2f} |")
    skipped = unpredicted(exp)
    if skipped:
        L += ["", "落下の予想を出さない対象（experiment.yaml の `predict: false`。「重さか種類か」の比較に入れない）: "
              + "、".join(label for _, label in skipped)]

    L += ["", "### MC: 終端速度に届くまでに要る高さ（モデルの予想）", "",
          "| 種類 | " + " | ".join(f"終端の{f:.0%}に届く tick / 落下距離（ブロック）" for f in REACH_FRACTIONS) + " |",
          "|---|" + "---|" * len(REACH_FRACTIONS)]
    for key in by_type:
        c = consts["types"][key]
        cells = []
        for f in REACH_FRACTIONS:
            t, dist = mc.reach_fraction(f, c["g"], c["d"], c["order"])
            cells.append(f"{t} / {dist:.0f}")
        L.append(f"| {key} | " + " | ".join(cells) + " |")

    L += ["", "### 現実（同じ高さを m として）", "",
          "| 条件 | 終端速度（m/s） | 着地時刻（s） | 着地の速さ（m/s） |", "|---|---|---|---|",
          f"| 真空、g=9.80665 | – | {real.fall_time_vacuum(h):.3f} | {math.sqrt(2 * real.G_EARTH * h):.3g} |",
          f"| 真空、g=9.8 | – | {real.fall_time_vacuum(h, real.G_EARTH_ROUND):.3f} | "
          f"{math.sqrt(2 * real.G_EARTH_ROUND * h):.3g} |",
          f"| 空気中、人の腹這い（FAI 約200 km/h【二次】） | {SKYDIVER_VT_MS:.3g} | "
          f"{real.fall_time_quadratic_drag(h, SKYDIVER_VT_MS):.2f} | "
          f"{real.quadratic_drag(h, real.fall_time_quadratic_drag(h, SKYDIVER_VT_MS), SKYDIVER_VT_MS)[1]:.3g} |",
          "", END]
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # Windows の既定（cp932）では「²」を出力できない
    print(table())
