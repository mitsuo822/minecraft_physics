"""experiment.yaml を読み、tickを1つずつ進めながら計測する。

流れ（繰り返し1回分）:
  1. `tick freeze` で世界を止め、ゲームルール・forceload・後片付け・下準備を行う
  2. t = 0, 1, 2, ... について
       a. procedure のうち tick == t のものを実行（召喚など）
       b. 追跡対象の Pos / Motion / OnGround を読んで1行記録
       c. 終了条件を満たしたら終わり
       d. `tick step 1` を送り、ゲーム時刻が1進むのを待つ
  3. 追跡対象を消して後片付け

tick t の行は「t回 tick が進んだあとの状態」。t=0 は召喚した直後で、物理はまだ1回も動いていない。

注意【未確認】: 止めている間は `time query gametime` が進まず、`tick step 1` の1tickでだけ1進む、
という前提で待ち合わせている。E001 の最初の実機実行でこれを確かめる。
"""
from __future__ import annotations

import csv
import json
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol

import yaml

from . import parse

ROOT_TAG = "mcphys"
CSV_FIELDS = ["repeat", "tick", "target", "type", "exists", "x", "y", "z", "vx", "vy", "vz", "on_ground", "gametime"]


class CommandSender(Protocol):
    def command(self, cmd: str) -> str: ...


@dataclass
class Entity:
    id: str
    summon: str
    nbt: str = ""

    @property
    def tag(self) -> str:
        return f"track_{self.id}"

    @property
    def selector(self) -> str:
        return f"@e[tag={self.tag},limit=1]"


@dataclass
class Experiment:
    path: Path
    raw: dict
    entities: dict[str, Entity] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "Experiment":
        path = Path(path)
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        exp = cls(path=path, raw=raw)
        for e in raw.get("setup", {}).get("entities", []):
            exp.entities[e["id"]] = Entity(id=e["id"], summon=e["summon"], nbt=e.get("nbt", "") or "")
        return exp

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def dir(self) -> Path:
        return self.path.parent

    @property
    def origin(self) -> tuple[float, float, float]:
        o = self.raw.get("setup", {}).get("origin", [0, 0, 0])
        return float(o[0]), float(o[1]), float(o[2])

    @property
    def measure(self) -> dict:
        return self.raw.get("measure", {})


def summon_command(ent: Entity, x: float, y: float, z: float) -> str:
    tags = f'Tags:["{ROOT_TAG}","{ent.tag}"]'
    nbt = f"{{{tags},{ent.nbt}}}" if ent.nbt.strip() else f"{{{tags}}}"
    name = ent.summon if ":" in ent.summon else f"minecraft:{ent.summon}"
    return f"summon {name} {x:.3f} {y:.3f} {z:.3f} {nbt}"


def expand_step(exp: Experiment, step: dict) -> list[str]:
    """procedure の1項目を、送るコマンドの列にする。"""
    if "cmd" in step:
        return [step["cmd"]]
    if "spawn" in step:
        ox, oy, oz = exp.origin
        ax, ay, az = step.get("at", [0, 0, 0])
        sx, sy, sz = step.get("spacing", [0, 0, 0])
        cmds = []
        for i, eid in enumerate(step["spawn"]):
            ent = exp.entities[eid]
            # ブロックの中心に置く（+0.5）
            cmds.append(summon_command(ent, ox + ax + sx * i + 0.5, oy + ay + sy * i, oz + az + sz * i + 0.5))
        return cmds
    raise ValueError(f"procedure の項目を解釈できません: {step}")


def setup_commands(exp: Experiment) -> list[str]:
    cmds = ["tick freeze"]
    for k, v in (exp.raw.get("world", {}).get("gamerules") or {}).items():
        cmds.append(f"gamerule {k} {str(v).lower()}")
    if t := exp.raw.get("world", {}).get("time"):
        cmds.append(f"time set {t}")
    if fl := exp.raw.get("setup", {}).get("forceload"):   # [[x1, z1], [x2, z2]]
        (x1, z1), (x2, z2) = fl
        cmds.append(f"forceload add {x1} {z1} {x2} {z2}")
    cmds += cleanup_commands(exp)
    return cmds


def cleanup_commands(exp: Experiment) -> list[str]:
    return [f"kill @e[tag={ROOT_TAG}]"] + list(exp.raw.get("setup", {}).get("prepare", []) or [])


class Runner:
    def __init__(self, exp: Experiment, conn: CommandSender, *, step_timeout: float = 3.0,
                 log: Callable[[str], None] = print, sleep: Callable[[float], None] = time.sleep):
        self.exp, self.conn, self.step_timeout, self.log, self.sleep = exp, conn, step_timeout, log, sleep

    def send(self, cmd: str) -> str:
        return self.conn.command(cmd)

    def gametime(self) -> int:
        return parse.parse_gametime(self.send("time query gametime"))

    def step_one(self, before: int) -> int:
        self.send("tick step 1")
        deadline = time.monotonic() + self.step_timeout
        while True:
            now = self.gametime()
            if now >= before + 1:
                if now > before + 1:
                    raise RuntimeError(f"1tickのはずが {now - before} tick 進みました。止まっていない可能性があります")
                return now
            if time.monotonic() > deadline:
                raise RuntimeError("tick step のあと、ゲーム時刻が進みません。"
                                   "サーバが一時停止していないか（pause-when-empty-seconds）を確認してください")
            self.sleep(0.002)

    def sample(self, repeat: int, t: int, gt: int) -> list[dict]:
        rows = []
        for eid in self.exp.measure["targets"]:
            ent = self.exp.entities[eid]
            row = {"repeat": repeat, "tick": t, "target": eid, "type": ent.summon, "gametime": gt,
                   "exists": 0, "x": "", "y": "", "z": "", "vx": "", "vy": "", "vz": "", "on_ground": ""}
            pos = self.send(f"data get entity {ent.selector} Pos")
            if not parse.is_no_entity(pos):
                row["x"], row["y"], row["z"] = parse.parse_vec3(pos)
                row["vx"], row["vy"], row["vz"] = parse.parse_vec3(self.send(f"data get entity {ent.selector} Motion"))
                row["on_ground"] = parse.parse_byte(self.send(f"data get entity {ent.selector} OnGround"))
                row["exists"] = 1
            rows.append(row)
        return rows

    @staticmethod
    def finished(rows: list[dict]) -> bool:
        return all((not r["exists"]) or r["on_ground"] == 1 for r in rows)

    def run_once(self, repeat: int) -> list[dict]:
        for cmd in setup_commands(self.exp):
            self.send(cmd)
        max_ticks = int(self.exp.measure.get("until", {}).get("max_ticks", 600))
        schedule: dict[int, list[str]] = {}
        for step in self.exp.raw.get("procedure", []):
            schedule.setdefault(int(step["tick"]), []).extend(expand_step(self.exp, step))
        last_cmd_tick = max(schedule) if schedule else 0

        gt = self.gametime()
        out: list[dict] = []
        for t in range(max_ticks + 1):
            for cmd in schedule.get(t, []):
                resp = self.send(cmd)
                self.log(f"  [t={t}] {cmd} -> {resp.strip()[:80]}")
            rows = self.sample(repeat, t, gt)
            out.extend(rows)
            if t > last_cmd_tick and self.finished(rows):
                self.log(f"  全対象が着地/消滅: t={t}")
                break
            gt = self.step_one(gt)
        else:
            self.log(f"  max_ticks={max_ticks} に達しました")
        for cmd in cleanup_commands(self.exp):
            self.send(cmd)
        return out

    def run(self, out_root: Path | None = None, *, mc_version: str | None = None, unfreeze: bool = True) -> Path:
        repeats = int(self.exp.measure.get("repeats", 1))
        run_dir = (out_root or self.exp.dir / "results") / datetime.now().strftime("run_%Y%m%d_%H%M%S")
        run_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy(self.exp.path, run_dir / "experiment.snapshot.yaml")
        started = time.monotonic()
        with (run_dir / "measurements.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            for r in range(repeats):
                self.log(f"繰り返し {r + 1}/{repeats}")
                w.writerows(self.run_once(r))
        if unfreeze:
            self.send("tick unfreeze")
        meta = {
            "experiment": self.exp.id,
            "mc_version": mc_version or self.exp.raw.get("mc_version"),
            "profile": self.exp.raw.get("profile"),
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "wall_seconds": round(time.monotonic() - started, 2),
            "repeats": repeats,
        }
        (run_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return run_dir
