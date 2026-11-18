"""MCのコマンド応答の読み取り。

応答の例（Java版、英語ロケールのサーバ）:
    "Pig has the following entity data: [0.5d, 196.0d, 0.5d]"
    "Pig has the following entity data: 1b"
    "No entity was found"
    "The time is 12345"
書式はバージョンで変わりうる【未確認】。合わない場合はここを直す。
"""
from __future__ import annotations

import re

_NUM = r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?"
_DOUBLE = re.compile(rf"({_NUM})d")
_BYTE = re.compile(rf"({_NUM})b\s*$")
_INT = re.compile(rf"({_NUM})\s*$")


class ParseError(ValueError):
    pass


def is_no_entity(resp: str) -> bool:
    return "No entity was found" in resp or "Found no elements" in resp


def _payload(resp: str) -> str:
    if "entity data:" not in resp:
        raise ParseError(f"エンティティのデータではない応答です: {resp!r}")
    return resp.split("entity data:", 1)[1].strip()


def parse_vec3(resp: str) -> tuple[float, float, float]:
    vals = [float(m) for m in _DOUBLE.findall(_payload(resp))]
    if len(vals) != 3:
        raise ParseError(f"3つの数値を読めません: {resp!r}")
    return vals[0], vals[1], vals[2]


def parse_byte(resp: str) -> int:
    m = _BYTE.search(_payload(resp))
    if not m:
        raise ParseError(f"byte値を読めません: {resp!r}")
    return int(float(m.group(1)))


def parse_gametime(resp: str) -> int:
    m = _INT.search(resp.strip())
    if not m or "time" not in resp.lower():
        raise ParseError(f"ゲーム時刻を読めません: {resp!r}")
    return int(float(m.group(1)))
