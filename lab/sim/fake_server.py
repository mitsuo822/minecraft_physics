"""模擬RCONサーバ: 本物のMCがない環境で、計測の流れ（runner → CSV → 解析 → グラフ）を試すためのもの。

物理は lab/models/mc_constants.yaml の「予想値」で動かしている。**これで出た数字は実測ではない。**
本物との違い: 当たり判定・衝突の細部・跳ね返り・ダメージ・AIは再現しない。地面は y = ground の平面だけ。
本物と同じく、`tick step 1` の1tickは非同期に進む（応答を返したあと、次のコマンドを数回受け取ってから進む）。
止めていないとき（tick unfreeze 後）は、コマンドを realtime_cmds_per_tick 回受け取るごとに1tick進む（通常速度の代わり）。
NoAI:1b の生物は動かさない（審査者の記憶による予想【未確認】。E001 で実測する）。
着地した落下ブロックは、その位置にブロックとして残る（`execute if block` と `fill ... air` に応える）。
"""
from __future__ import annotations

import math
import re
import socket
import struct
import threading

from ..models import free_fall_mc as mc

_SUMMON = re.compile(r"^summon (\S+) (\S+) (\S+) (\S+)\s*(\{.*\})?$")
_TAGS = re.compile(r'Tags:\[([^\]]*)\]')
_DATA = re.compile(r"^data get entity @e\[tag=([\w]+),limit=1\] (\w+)$")
_KILL = re.compile(r"^kill @e\[tag=([\w]+)\]$")
_BLOCKNAME = re.compile(r'BlockState:\{Name:"(?:minecraft:)?(\w+)"')
_IFBLOCK = re.compile(r"^execute if block (-?\d+) (-?\d+) (-?\d+) (#?)(?:minecraft:)?(\w+)$")
_FILL = re.compile(r"^fill (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (-?\d+) (?:minecraft:)?air$")
_TAG_MEMBERS = {"anvil": {"anvil", "chipped_anvil", "damaged_anvil"}}


class World:
    def __init__(self, ground: float, step_delay_cmds: int = 2, realtime_cmds_per_tick: int = 8):
        self.ground = ground
        self.consts = mc.load_constants()["types"]
        self.entities: list[dict] = []
        self.blocks: dict[tuple[int, int, int], str] = {}
        self.frozen = False
        self.gametime = 1000
        self.pending_steps = 0
        self.step_delay = step_delay_cmds
        self._countdown = 0
        self.realtime_cmds_per_tick = realtime_cmds_per_tick
        self._rt_count = 0

    def _tick(self) -> None:
        self.gametime += 1
        alive = []
        for e in self.entities:
            c = self.consts.get(e["type"], {"g": 0.08, "d": 0.02, "order": "move_then_accel"})
            if not e["on_ground"] and not e["noai"]:
                y, v = mc.step(e["y"], e["vy"], c["g"], c["d"], c["order"])
                if y <= self.ground:
                    y, v = self.ground, 0.0
                    e["on_ground"] = 1
                    if e["type"] == "falling_block":   # 着地するとブロックになって消える
                        self.blocks[(math.floor(e["x"]), int(self.ground), math.floor(e["z"]))] = e["block"]
                        continue
                e["y"], e["vy"] = y, v
            alive.append(e)
        self.entities = alive

    def handle(self, cmd: str) -> str:
        cmd = cmd.strip().lstrip("/")
        if self.pending_steps:
            self._countdown -= 1
            if self._countdown <= 0:
                while self.pending_steps:
                    self._tick()
                    self.pending_steps -= 1
        if not self.frozen:
            self._rt_count += 1
            if self._rt_count >= self.realtime_cmds_per_tick:
                self._rt_count = 0
                self._tick()
        if cmd == "tick freeze":
            self.frozen = True
            return "The game is frozen"
        if cmd == "tick unfreeze":
            self.frozen = False
            return "The game is running"
        if cmd.startswith("tick step"):
            n = int(cmd.split()[-1]) if len(cmd.split()) > 2 else 1
            self.pending_steps += n
            self._countdown = self.step_delay
            return f"Stepping {n} tick(s)"
        if cmd == "time query gametime":
            return f"The time is {self.gametime}"
        if m := _SUMMON.match(cmd):
            typ, x, y, z, nbt = m.groups()
            tags = [t.strip().strip('"') for t in _TAGS.search(nbt or "").group(1).split(",")] if nbt and _TAGS.search(nbt) else []
            bm = _BLOCKNAME.search(nbt or "")
            self.entities.append({"type": typ.split(":")[-1], "x": float(x), "y": float(y), "z": float(z),
                                  "vy": 0.0, "on_ground": 0, "tags": tags, "noai": "NoAI:1b" in (nbt or ""),
                                  "block": bm.group(1) if bm else None})
            return f"Summoned new {typ.split(':')[-1].replace('_', ' ').title()}"
        if m := _IFBLOCK.match(cmd):
            x, y, z, is_tag, name = m.groups()
            have = self.blocks.get((int(x), int(y), int(z)))
            ok = have is not None and (have in _TAG_MEMBERS.get(name, {name}) if is_tag else have == name)
            return "Test passed" if ok else "Test failed"
        if m := _FILL.match(cmd):
            x1, y1, z1, x2, y2, z2 = map(int, m.groups())
            hit = [k for k in self.blocks if min(x1, x2) <= k[0] <= max(x1, x2) and min(y1, y2) <= k[1] <= max(y1, y2)
                   and min(z1, z2) <= k[2] <= max(z1, z2)]
            for k in hit:
                del self.blocks[k]
            return f"Successfully filled {len(hit)} block(s)" if hit else "No blocks were filled"
        if cmd.startswith("gamerule "):
            _, name, value = cmd.split()
            return f"Gamerule {name} is now set to: {value}"
        if m := _KILL.match(cmd):
            n = len(self.entities)
            self.entities = [e for e in self.entities if m.group(1) not in e["tags"]]
            return f"Killed {n - len(self.entities)} entities"
        if m := _DATA.match(cmd):
            tag, path = m.groups()
            e = next((e for e in self.entities if tag in e["tags"]), None)
            if e is None:
                return "No entity was found"
            name = e["type"].replace("_", " ").title()
            if path == "Pos":
                return f"{name} has the following entity data: [{e['x']!r}d, {e['y']!r}d, {e['z']!r}d]"
            if path == "Motion":
                return f"{name} has the following entity data: [0.0d, {e['vy']!r}d, 0.0d]"
            if path == "OnGround":
                return f"{name} has the following entity data: {e['on_ground']}b"
            return "Found no elements matching " + path
        return ""   # gamerule / fill / forceload / time set など: 何もしない


class FakeRconServer:
    def __init__(self, password: str = "test", ground: float = -60.0, host: str = "127.0.0.1", port: int = 0):
        self.password = password
        self.world = World(ground)
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind((host, port))
        self._srv.listen(1)
        self.host, self.port = self._srv.getsockname()
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def __enter__(self) -> "FakeRconServer":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._srv.close()

    @staticmethod
    def _read(conn: socket.socket, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                raise ConnectionError
            buf += chunk
        return buf

    @staticmethod
    def _write(conn: socket.socket, req_id: int, kind: int, body: str) -> None:
        payload = struct.pack("<ii", req_id, kind) + body.encode("utf-8") + b"\x00\x00"
        conn.sendall(struct.pack("<i", len(payload)) + payload)

    def _serve(self) -> None:
        try:
            while True:
                conn, _ = self._srv.accept()
                with conn:
                    try:
                        authed = False
                        while True:
                            (length,) = struct.unpack("<i", self._read(conn, 4))
                            data = self._read(conn, length)
                            req_id, kind = struct.unpack("<ii", data[:8])
                            body = data[8:-2].decode("utf-8")
                            if kind == 3:
                                authed = body == self.password
                                self._write(conn, req_id if authed else -1, 2, "")
                            elif kind == 2 and authed:
                                self._write(conn, req_id, 0, self.world.handle(body))
                    except ConnectionError:
                        pass
        except OSError:
            return


def main() -> None:
    import argparse
    import time

    ap = argparse.ArgumentParser(description="模擬RCONサーバ（試験用）")
    ap.add_argument("--port", type=int, default=25575)
    ap.add_argument("--password", default="test")
    a = ap.parse_args()
    with FakeRconServer(a.password, port=a.port) as s:
        print(f"模擬RCONサーバ: {s.host}:{s.port}（Ctrl+C で終了）")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
