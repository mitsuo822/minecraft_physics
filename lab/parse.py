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


# コマンドが失敗したときの応答に出る文字列【未確認・記憶。Java版、英語ロケール】。合わない応答が出たらここに足す
_ERROR_MARKS = ("<--[HERE]", "Unknown or incomplete command", "Incorrect argument", "Unknown game rule",
                "Unknown block", "Unknown item", "Unknown entity", "Invalid", "Unable to", "Expected ",
                "Can't ", "Cannot ", "Failed to")
# 後片付けで「対象がない」ときの応答。後片付けでは失敗に数えない
BENIGN_EMPTY = ("No entity was found", "No blocks were filled")


def is_command_error(resp: str) -> bool:
    """コマンドの応答が失敗を示すか。execute if の "Test failed" は判定の結果なので失敗に数えない。"""
    return any(m in resp for m in _ERROR_MARKS)


def execute_test_result(resp: str) -> bool | None:
    """execute if ... の応答: Test passed → True、Test failed → False、どちらでもない → None。"""
    if "Test passed" in resp:
        return True
    if "Test failed" in resp:
        return False
    return None


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
