"""MC内部の落下モデル（1tickごとの漸化式）と、計測値からの当てはめ。

単位: 位置はブロック、速度はブロック/tick、時間はtick。1ブロック=1m、1秒=20tick。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

TICKS_PER_SEC = 20
ORDERS = ("move_then_accel", "accel_then_move")


def load_constants() -> dict:
    return yaml.safe_load((Path(__file__).with_name("mc_constants.yaml")).read_text(encoding="utf-8"))


def entity_key(summon: str) -> str:
    return summon.split(":")[-1]


def step(y: float, v: float, g: float, d: float, order: str) -> tuple[float, float]:
    if order == "move_then_accel":
        return y + v, (v - g) * (1 - d)
    if order == "accel_then_move":
        v1 = v - g
        return y + v1, v1 * (1 - d)
    raise ValueError(order)


def simulate(y0: float, v0: float, g: float, d: float, order: str, n: int,
             ground: float | None = None) -> list[tuple[int, float, float]]:
    """t=0..n の (t, y, vy)。ground を与えると、そこに達した時点で止める（衝突の細部は再現しない）。"""
    out = [(0, y0, v0)]
    y, v = y0, v0
    for t in range(1, n + 1):
        y, v = step(y, v, g, d, order)
        if ground is not None and y <= ground:
            out.append((t, ground, 0.0))
            break
        out.append((t, y, v))
    return out


def terminal_velocity(g: float, d: float) -> float:
    """固定点 v = (v - g)(1 - d) の大きさ（ブロック/tick）。どちらの順序でも同じ。"""
    return g * (1 - d) / d


@dataclass
class Fit:
    g: float                 # ブロック/tick^2
    d: float
    order: str
    rms_velocity: float      # 速度の漸化式の残差（ブロック/tick）
    rms_position: dict       # 順序ごとの位置の残差（ブロック）
    n_pairs: int

    @property
    def g_ms2(self) -> float:
        return self.g * TICKS_PER_SEC ** 2

    @property
    def terminal_ms(self) -> float:
        return terminal_velocity(self.g, self.d) * TICKS_PER_SEC if self.d > 0 else float("inf")


def fit(samples: list[tuple[int, float, float]], min_speed: float = 0.0) -> Fit | None:
    """空中にある連続した (t, y, vy) の列から g, d, 順序を求める。

    どちらの順序でも速度は v_{t+1} = a v_t + b（a = 1 - d, b = -g(1 - d)）なので、最小二乗で a, b を出す。
    順序は位置の増え方で見分ける:
      move_then_accel: y_{t+1} - y_t = v_t
      accel_then_move: y_{t+1} - y_t = v_{t+1} / a
    """
    pairs = [(s0, s1) for s0, s1 in zip(samples, samples[1:])
             if s1[0] == s0[0] + 1 and abs(s0[2]) >= min_speed]
    if len(pairs) < 3:
        return None
    xs = [p[0][2] for p in pairs]
    ys = [p[1][2] for p in pairs]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    b = my - a * mx
    rms_v = (sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys)) / n) ** 0.5
    res = {
        "move_then_accel": [(p1[1] - p0[1]) - p0[2] for p0, p1 in pairs],
        "accel_then_move": [(p1[1] - p0[1]) - p1[2] / a for p0, p1 in pairs],
    }
    rms_p = {k: (sum(r * r for r in v) / n) ** 0.5 for k, v in res.items()}
    order = min(rms_p, key=rms_p.get)
    return Fit(g=-b / a, d=1 - a, order=order, rms_velocity=rms_v, rms_position=rms_p, n_pairs=n)
