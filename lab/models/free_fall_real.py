"""現実の自由落下。

- 真空: y = y0 - g t^2 / 2,  v = g t
- 空気抵抗（速度の2乗に比例）あり、終端速度 vt を与える:
    v = vt tanh(g t / vt),  落下距離 = vt^2 / g * ln cosh(g t / vt)
- 終端速度: vt = sqrt(2 m g / (rho C_d A))
単位は SI（m, s, kg）。式は力学の標準形（出典ページは未取得【未確認】。model.md 参照）。
"""
from __future__ import annotations

import math

G_EARTH = 9.80665  # m/s^2（標準重力加速度。定義値とされる。一次資料は未取得【未確認】）
G_EARTH_ROUND = 9.8  # m/s^2（台本でよく使う概数）


def vacuum(y0: float, t: float, g: float = G_EARTH) -> tuple[float, float]:
    """(高さ m, 下向きの速さ m/s)"""
    return y0 - 0.5 * g * t * t, g * t


def quadratic_drag(y0: float, t: float, vt: float, g: float = G_EARTH) -> tuple[float, float]:
    """(高さ m, 下向きの速さ m/s)。初速0、抵抗は速さの2乗に比例、終端速度 vt [m/s]。"""
    k = g * t / vt
    return y0 - vt * vt / g * math.log(math.cosh(k)), vt * math.tanh(k)


def fall_time_vacuum(h: float, g: float = G_EARTH) -> float:
    """高さ h [m] を初速0で落ちる時間 [s]。"""
    return math.sqrt(2 * h / g)


def fall_time_quadratic_drag(h: float, vt: float, g: float = G_EARTH) -> float:
    """quadratic_drag の逆: h = vt^2/g ln cosh(g t/vt) を t について解く [s]。"""
    return vt / g * math.acosh(math.exp(h * g / (vt * vt)))


def terminal_velocity(m: float, rho: float, cd: float, area: float, g: float = G_EARTH) -> float:
    """vt = sqrt(2 m g / (rho C_d A)) [m/s]。m [kg], rho [kg/m^3], C_d [無次元], A [m^2]。"""
    return math.sqrt(2 * m * g / (rho * cd * area))
