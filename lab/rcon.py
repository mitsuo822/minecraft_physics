"""Minecraft の RCON クライアント（依存ライブラリなし）。

プロトコル: 各パケットは
    int32 長さ(LE) | int32 リクエストID | int32 種別 | 本文(UTF-8) | 0x00 | 0x00
種別: 3=ログイン, 2=コマンド, 0=応答。ログイン失敗時は応答のIDが -1 になる。

注意: MCは 4096 バイトを超える応答を複数パケットに分けて返す。この実験で使う
`data get entity ... Pos` などの応答は短いので、1パケット分だけ読む。
"""
from __future__ import annotations

import socket
import struct

LOGIN = 3
COMMAND = 2


class RconError(RuntimeError):
    pass


class Rcon:
    def __init__(self, host: str, port: int, password: str, timeout: float = 5.0):
        self.host, self.port, self.password, self.timeout = host, port, password, timeout
        self._sock: socket.socket | None = None
        self._next_id = 1

    def __enter__(self) -> "Rcon":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def connect(self) -> None:
        self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        req_id = self._send(LOGIN, self.password)
        resp_id, _, _ = self._recv()
        if resp_id == -1 or resp_id != req_id:
            raise RconError("RCON のログインに失敗しました（パスワードを確認してください）")

    def close(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    def command(self, cmd: str) -> str:
        """コマンドを1つ送り、応答の本文を返す。先頭の / は付けても付けなくてもよい。"""
        req_id = self._send(COMMAND, cmd.lstrip("/"))
        resp_id, _, body = self._recv()
        if resp_id != req_id:
            raise RconError(f"応答のIDが一致しません: 送信 {req_id}, 受信 {resp_id}")
        return body

    # --- 内部 ---
    def _send(self, kind: int, body: str) -> int:
        if self._sock is None:
            raise RconError("接続していません")
        req_id = self._next_id
        self._next_id += 1
        payload = struct.pack("<ii", req_id, kind) + body.encode("utf-8") + b"\x00\x00"
        self._sock.sendall(struct.pack("<i", len(payload)) + payload)
        return req_id

    def _recv_exact(self, n: int) -> bytes:
        assert self._sock is not None
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise RconError("サーバが接続を切りました")
            buf += chunk
        return buf

    def _recv(self) -> tuple[int, int, str]:
        (length,) = struct.unpack("<i", self._recv_exact(4))
        data = self._recv_exact(length)
        resp_id, kind = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode("utf-8", errors="replace")
        return resp_id, kind, body
