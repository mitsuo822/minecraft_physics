"""現実の自由落下。

- 真空: y = y0 - g t^2 / 2
- 空気抵抗（速度の2乗に比例）あり、終端速度 vt を与える:
    v = vt tanh(g t / vt),  落下距離 = vt^2 / g * ln cosh(g t / vt)
単位は m, s。
"""
from __future__ import annotations

import math

G_EARTH = 9.80665  # m/s^2（標準重力加速度、定義値）


def vacuum(y0: float, t: float, g: float = G_EARTH) -> tuple[float, float]:
    """(高さ, 下向きの速さ)"""
    return y0 - 0.5 * g * t * t, g * t


def quadratic_drag(y0: float, t: float, vt: float, g: float = G_EARTH) -> tuple[float, float]:
    k = g * t / vt
    return y0 - vt * vt / g * math.log(math.cosh(k)), vt * math.tanh(k)


def fall_time_vacuum(h: float, g: float = G_EARTH) -> float:
    return math.sqrt(2 * h / g)
