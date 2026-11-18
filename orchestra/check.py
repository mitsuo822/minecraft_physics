"""制作台帳（ledger.json）の機械チェック。

確かめること:
1. 台詞の話者が cast にいる
2. visuals の sync が実在する台詞IDを指している
3. facts の確度が 実測／一次／二次／未確認 のどれか
4. 台詞に出てくる数字が、確度【実測】【一次】の facts に載っている
   （10以下の整数は「2人」「3つ」などの普通の言い回しに出るので対象外）

書式の正本は movie リポジトリの docs/制作台帳.md。
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

CONFIDENCES = {"実測", "一次", "二次", "未確認"}
ASSERTABLE = {"実測", "一次"}
NUM_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")


def numbers(text: str) -> set[str]:
    text = unicodedata.normalize("NFKC", text)
    out = set()
    for m in NUM_RE.findall(text):
        s = m.replace(",", "")
        if "." not in s and int(s) <= 10:
            continue
        out.add(repr(float(s)))
    return out


def check_ledger(path: Path) -> list[str]:
    try:
        led = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path} がありません"]
    except json.JSONDecodeError as e:
        return [f"{path} がJSONとして読めません: {e}"]

    ng: list[str] = []
    cast = {c.get("id") for c in led.get("cast", [])}
    facts = led.get("facts", [])
    allowed: set[str] = set()
    for f in facts:
        conf = f.get("confidence")
        if conf not in CONFIDENCES:
            ng.append(f"facts {f.get('id')}: 確度「{conf}」は {sorted(CONFIDENCES)} のどれでもない")
        if conf in ASSERTABLE:
            allowed |= numbers(f.get("text", ""))

    line_ids = set()
    for sec in led.get("sections", []):
        for ln in sec.get("lines", []):
            lid = ln.get("id")
            line_ids.add(lid)
            if ln.get("speaker") not in cast:
                ng.append(f"{sec.get('id')}/{lid}: 話者「{ln.get('speaker')}」が cast にいない")
            for n in sorted(numbers(ln.get("text", "")) - allowed):
                ng.append(f"{sec.get('id')}/{lid}: 数字 {n.rstrip('0').rstrip('.')} の根拠が"
                          f"【実測】【一次】の facts にない —「{ln.get('text')}」")
    for sec in led.get("sections", []):
        for v in sec.get("visuals", []):
            start = (v.get("sync") or {}).get("start_line")
            if start and start not in line_ids:
                ng.append(f"{sec.get('id')}/{v.get('id')}: sync.start_line「{start}」という台詞がない")
    if not led.get("sections"):
        ng.append("sections が空")
    return ng
