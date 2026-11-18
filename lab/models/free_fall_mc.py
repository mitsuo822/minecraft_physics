"""MC内部の落下モデル（1tickごとの漸化式）と、計測値からの当てはめ。

単位: 位置はブロック、速度はブロック/tick、時間はtick。
現実の単位への換算は「1ブロック=1m、1秒=20tick」という前提（慣習。Mojang の定義ではない【未確認】）。

漸化式（v は上向き正。tick の終わりに Motion として保存される値）:
  move_then_accel : y' = y + v,        v' = (v - g)(1 - d)            生物（位置→加速→抵抗）
  accel_then_move : y' = y + (v - g),  v' = (v - g)(1 - d)            アイテム・落下ブロック（加速→位置→抵抗）
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

TICKS_PER_SEC = 20
BLOCK_M = 1.0   # 1ブロックの長さ [m]（前提）
ORDERS = ("move_then_accel", "accel_then_move")


def load_constants() -> dict:
    return yaml.safe_load((Path(__file__).with_name("mc_constants.yaml")).read_text(encoding="utf-8"))


def entity_key(summon: str) -> str:
    return summon.split(":")[-1]


# --- 単位換算 -------------------------------------------------------------

def speed_ms(v_block_per_tick: float) -> float:
    """ブロック/tick → m/s"""
    return v_block_per_tick * BLOCK_M * TICKS_PER_SEC


def accel_ms2(a_block_per_tick2: float) -> float:
    """ブロック/tick² → m/s²"""
    return a_block_per_tick2 * BLOCK_M * TICKS_PER_SEC ** 2


# --- 漸化式 ---------------------------------------------------------------

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
    """tick の終わりの Motion の固定点 v = (v - g)(1 - d) の大きさ（ブロック/tick）。どちらの順序でも同じ。"""
    return g * (1 - d) / d


def terminal_step(g: float, d: float, order: str) -> float:
    """終端状態で 1 tick に実際に動く距離（ブロック/tick）。順序で変わる。

    move_then_accel は保存された Motion で動くので g(1-d)/d、
    accel_then_move は Motion - g で動くので g(1-d)/d + g = g/d。
    """
    vt = terminal_velocity(g, d)
    if order == "move_then_accel":
        return vt
    if order == "accel_then_move":
        return vt + g
    raise ValueError(order)


def landing_tick(height: float, g: float, d: float, order: str, max_ticks: int = 100_000) -> int:
    """高さ height [ブロック] を初速0で落ち、地面に達する最初の tick。"""
    for t, y, _ in simulate(height, 0.0, g, d, order, max_ticks, ground=0.0):
        if t > 0 and y <= 0.0:
            return t
    raise ValueError("max_ticks 以内に着地しない")


def time_constant_s(d: float) -> float:
    """速度と終端速度の差が 1/e になる時間 [s]。差は毎tick (1-d) 倍になる（=速度に比例する抵抗）。"""
    return -1.0 / (TICKS_PER_SEC * math.log(1 - d))


def next_step_distance(v: float, g: float, order: str) -> float:
    """tick の終わりの Motion が v のとき、次の1tickに下へ動く距離（ブロック）。"""
    if order == "move_then_accel":
        return -v
    if order == "accel_then_move":
        return -(v - g)
    raise ValueError(order)


def last_airborne(height: float, g: float, d: float, order: str) -> tuple[int, float, float]:
    """着地する直前の tick の (t, 地面からの高さ, Motion.y)。計測で取れる最後の空中の状態。"""
    lt = landing_tick(height, g, d, order)
    return simulate(height, 0.0, g, d, order, lt - 1)[-1]


def reach_fraction(frac: float, g: float, d: float, order: str, max_ticks: int = 100_000) -> tuple[int, float]:
    """静止から落ちて、Motion の大きさが終端の frac 倍に初めて届く (tick, それまでの落下距離 ブロック)。"""
    vt = terminal_velocity(g, d)
    y, v = 0.0, 0.0
    for t in range(1, max_ticks + 1):
        y, v = step(y, v, g, d, order)
        if -v >= frac * vt:
            return t, -y
    raise ValueError("max_ticks 以内に届かない")


@dataclass
class Prediction:
    """1種類のエンティティについて、モデルから出る予想値。"""
    type: str
    g: float
    d: float
    order: str
    height: float

    @property
    def g_ms2(self) -> float:
        """コード上の重力パラメータを m/s² にしたもの。"""
        return accel_ms2(self.g)

    @property
    def first_dv_ms2(self) -> float:
        """静止から1tick目に Motion が変わる量を m/s² にしたもの = g(1-d)。計測で素朴に差分を取るとこちらが出る。"""
        return accel_ms2(self.g * (1 - self.d))

    def ratio(self, g_earth: float) -> float:
        return self.g_ms2 / g_earth

    @property
    def first_tick_drop(self) -> float:
        """1tick目に動く距離（ブロック）。生物は0、アイテム・落下ブロックは g。"""
        y1 = simulate(0.0, 0.0, self.g, self.d, self.order, 1)[1][1]
        return 0.0 - y1

    @property
    def terminal_motion(self) -> float:
        return terminal_velocity(self.g, self.d)

    @property
    def terminal_step(self) -> float:
        return terminal_step(self.g, self.d, self.order)

    @property
    def continuous_accel_ms2(self) -> float:
        """連続時間の dv/dt = a − v/τ に直したときの a [m/s²] = 終端速度 ÷ 時定数。地球比の3つ目の定義。"""
        return speed_ms(self.terminal_motion) / self.time_constant_s

    @property
    def landing_tick(self) -> int:
        return landing_tick(self.height, self.g, self.d, self.order)

    @property
    def time_constant_s(self) -> float:
        return time_constant_s(self.d)

    @property
    def last_airborne(self) -> tuple[int, float, float]:
        return last_airborne(self.height, self.g, self.d, self.order)

    @property
    def max_motion(self) -> float:
        """着地前に到達する最大の Motion の大きさ（ブロック/tick）= 着地直前の tick の値。実測できるのはここまで。"""
        return -self.last_airborne[2]

    @property
    def terminal_fraction(self) -> float:
        return self.max_motion / self.terminal_motion

    @property
    def gap_before_landing(self) -> float:
        """着地直前の tick の、地面からの高さ（ブロック）。"""
        return self.last_airborne[1]

    @property
    def next_step_before_landing(self) -> float:
        """着地直前の tick の Motion から、次の1tickに動く距離（ブロック）。gap_before_landing 以上なら次で着く。"""
        return next_step_distance(self.last_airborne[2], self.g, self.order)


def predict(type_key: str, height: float, consts: dict | None = None) -> Prediction:
    c = (consts or load_constants())["types"][type_key]
    return Prediction(type=type_key, g=c["g"], d=c["d"], order=c["order"], height=height)


# --- 当てはめ --------------------------------------------------------------

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
        return accel_ms2(self.g)

    @property
    def terminal_ms(self) -> float:
        """当てはめた g, d から式で出す終端速度。**測った速さではない**（計算値）。"""
        return speed_ms(terminal_velocity(self.g, self.d)) if self.d > 0 else float("inf")

    @property
    def g_if_drag_then_accel(self) -> float:
        """処理順が「抵抗→加速」（v' = v(1-d) - g）だった場合の g の読み方。

        速度の列だけではこの順序と「加速→抵抗」を区別できない（どちらも v' = a v + b）。
        「加速→抵抗」として読んだ g（self.g）が予想より 1/(1-d) 倍大きく出たら、この値が予想と合うかを見る。
        """
        return self.g * (1 - self.d)


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
