"""工程を1つずつ進めるエンジン。

状態は episodes/<EP>/episode.yaml の steps と approvals に書く。
実行の記録は episodes/<EP>/runlog.jsonl に1工程1行で追記する（実行台帳）。
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

PIPELINE_FILE = Path(__file__).with_name("pipeline.yaml")
VERDICT_RE = re.compile(r"判定\s*[:：]\s*(条件付き合格|不合格|合格)")
MAX_ROUNDS = 2  # 審査で差し戻せる回数。超えたら人に渡す

# エージェントに前もって許可しておく操作（ファイルの編集は acceptEdits で許可される）
ALLOWED_TOOLS = [
    "Read", "Glob", "Grep", "WebSearch", "WebFetch",
    "Bash(python -m pytest)", "Bash(python -m pytest *)",
    "Bash(python -m lab *)", "Bash(python -m orchestra check *)",
    "Bash(git status)", "Bash(git diff *)", "Bash(git log *)",
]


class Outcome:
    """1工程を実行した結果。CLI の終了コードにもなる。"""
    DONE = 0          # 工程が終わった。次へ進める
    WAIT_HUMAN = 10   # 関門・人の作業で止まった
    FAILED = 20       # 失敗。人が見る必要がある
    BLOCKED = 30      # 前提が足りない（サーバ未起動、未実装など）
    RETRY = 40        # 審査で差し戻した。自動でやり直してよい
    FINISHED = 50     # 全工程が終わっている


@dataclass
class Result:
    code: int
    message: str


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def load_pipeline(path: Path = PIPELINE_FILE) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["steps"]


class Episode:
    def __init__(self, root: Path, ep_id: str):
        self.root = Path(root)
        dirs = sorted(p for p in (self.root / "episodes").glob(f"{ep_id}*") if p.is_dir())
        if not dirs:
            raise SystemExit(f"episodes/{ep_id}* が見つかりません")
        if len(dirs) > 1:
            raise SystemExit(f"{ep_id} に当てはまるフォルダが複数あります: {[d.name for d in dirs]}")
        self.dir = dirs[0]
        self.file = self.dir / "episode.yaml"
        self.reload()

    def reload(self) -> None:
        self.data = yaml.safe_load(self.file.read_text(encoding="utf-8")) or {}
        self.data.setdefault("approvals", {})
        if not isinstance(self.data.get("steps"), dict):
            self.data["steps"] = {}

    def save(self) -> None:
        self.file.write_text(yaml.safe_dump(self.data, allow_unicode=True, sort_keys=False),
                             encoding="utf-8", newline="\n")

    @property
    def id(self) -> str:
        return self.data["id"]

    def rel(self, p: Path) -> str:
        return Path(p).resolve().relative_to(self.root.resolve()).as_posix()

    def vars(self) -> dict:
        return {
            "episode": self.id,
            "ep": self.rel(self.dir),
            "exp": (self.data.get("experiment") or "").rstrip("/"),
            "mc_version": self.data.get("mc_version") or "TBD",
        }

    def fmt(self, s: str) -> str:
        return s.format(**self.vars())

    def state(self, step_id: str) -> dict:
        return self.data["steps"].setdefault(step_id, {"status": "pending"})

    def is_complete(self, step: dict) -> bool:
        if step["kind"] == "gate":
            return bool(self.data["approvals"].get(step["approval"]))
        return self.state(step["id"]).get("status") in ("done", "skipped")

    def log(self, rec: dict) -> None:
        with open(self.dir / "runlog.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def next_step(ep: Episode, steps: list[dict]) -> dict | None:
    for s in steps:
        if not ep.is_complete(s):
            return s
    return None


def _missing_outputs(ep: Episode, step: dict) -> list[str]:
    missing = [ep.fmt(p) for p in step.get("outputs", []) if not (ep.root / ep.fmt(p)).exists()]
    if step.get("outputs_glob") and not list(ep.root.glob(ep.fmt(step["outputs_glob"]))):
        missing.append(ep.fmt(step["outputs_glob"]))
    return missing


def _agent_prompt(ep: Episode, step: dict) -> str:
    v = ep.vars()
    outs = "\n".join(f"  - {ep.fmt(p)}" for p in step.get("outputs", [])) or "  - （指定なし）"
    lines = [
        f"エピソード {v['episode']} の工程「{step['title']}」（{step['id']}）を担当してください。",
        f"- エピソードのフォルダ: {v['ep']}（episode.yaml に方針と承認の記録がある）",
        f"- 実験のフォルダ: {v['exp'] or '（未定）'}",
        f"- MCのバージョン: {v['mc_version']}",
        "出力ファイル:",
        outs,
    ]
    fb = ep.state(step["id"]).get("feedback")
    if fb:
        lines.append(f"前回は審査で差し戻されました。まず {fb} を読み、止める指摘をすべて直してください。")
    lines.append("episode.yaml の steps と approvals は書き換えないでください（orchestra が管理します）。")
    lines.append("終わったら、やったことを3行以内で報告してください。")
    return "\n".join(lines)


def _child_env(root: Path) -> dict:
    """エージェントやコマンドの中の `python` が orchestra と同じ Python（venv）を指し、
    `python -m orchestra` が同じリポジトリを見るようにする。"""
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["ORCHESTRA_ROOT"] = str(root)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _last_json(stdout: str | None) -> dict:
    """claude -p の出力から結果のJSONを取り出す。前に警告の行が混ざっていてもよい
    （例: CLI が新しいモデルIDを知らないときの [claude-code:unrecognized_model]）。"""
    for line in reversed((stdout or "").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


def _run_agent(ep: Episode, step: dict, claude_cmd: list[str], dry_run: bool) -> Result:
    prompt = _agent_prompt(ep, step)
    cmd = [*claude_cmd, "-p", prompt, "--agent", step["agent"],
           "--permission-mode", "acceptEdits", "--output-format", "json",
           "--allowedTools", *ALLOWED_TOOLS]
    if dry_run:
        return Result(Outcome.DONE, f"[dry-run] {step['agent']} を呼ぶ\n{prompt}")
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ep.root, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=_child_env(ep.root), timeout=3 * 3600)
    info = _last_json(proc.stdout)
    ep.log({"at": now(), "step": step["id"], "kind": "agent", "agent": step["agent"],
            "sec": round(time.time() - t0, 1), "exit": proc.returncode,
            "cost_usd": info.get("total_cost_usd"), "is_error": info.get("is_error"),
            "result": (info.get("result") or proc.stdout or "")[-2000:],
            "stderr": proc.stderr[-2000:]})
    if proc.returncode != 0 or info.get("is_error"):
        return Result(Outcome.FAILED, f"エージェント {step['agent']} が失敗しました（終了コード {proc.returncode}）。"
                                      f" runlog.jsonl を見てください。\n{proc.stderr[-500:]}")
    return Result(Outcome.DONE, (info.get("result") or "").strip())


def _run_command(ep: Episode, step: dict, dry_run: bool) -> Result:
    if not step.get("command"):
        return Result(Outcome.BLOCKED, "この工程はまだ自動化されていません。\n" + ep.fmt(step.get("instructions", "")))
    missing_env = [k for k in step.get("needs_env", []) if not os.environ.get(k)]
    cmd = [sys.executable if c == "python" else ep.fmt(c) for c in step["command"]]
    if dry_run:
        return Result(Outcome.DONE, "[dry-run] " + " ".join(cmd))
    if missing_env:
        return Result(Outcome.BLOCKED, f"環境変数 {', '.join(missing_env)} がありません。\n"
                      + ep.fmt(step.get("instructions", "")))
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ep.root, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=_child_env(ep.root))
    out = (proc.stdout + proc.stderr)[-3000:]
    ep.log({"at": now(), "step": step["id"], "kind": "command", "cmd": cmd,
            "sec": round(time.time() - t0, 1), "exit": proc.returncode, "output": out})
    if proc.returncode != 0:
        return Result(Outcome.FAILED, f"コマンドが失敗しました（終了コード {proc.returncode}）:\n{out}")
    return Result(Outcome.DONE, out.strip()[-800:])


def _apply_verdict(ep: Episode, steps: list[dict], step: dict) -> Result | None:
    """審査ファイルの判定を読む。不合格なら on_fail の工程まで戻す。"""
    path = ep.root / ep.fmt(step["verdict"])
    m = VERDICT_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        return Result(Outcome.FAILED, f"{ep.fmt(step['verdict'])} に「判定: 合格／条件付き合格／不合格」の行がありません")
    verdict = m.group(1)
    st = ep.state(step["id"])
    st["verdict"] = verdict
    if verdict != "不合格":
        return None
    if not step.get("on_fail"):
        st["status"] = "failed"
        return Result(Outcome.FAILED, f"{step['title']}が不合格です。{ep.fmt(step['verdict'])} を読み、"
                                      f"直す工程を `python -m orchestra reset {ep.id} <工程>` で戻してください。")
    st["rounds"] = st.get("rounds", 0) + 1
    ids = [s["id"] for s in steps]
    back = step["on_fail"]
    for s in steps[ids.index(back): ids.index(step["id"]) + 1]:
        if s["kind"] != "gate":
            keep = {"rounds": ep.state(s["id"]).get("rounds")} if s["id"] == step["id"] else {}
            ep.data["steps"][s["id"]] = {"status": "pending", **{k: v for k, v in keep.items() if v}}
    ep.state(back)["feedback"] = ep.fmt(step["verdict"])
    if st.get("rounds", 0) > MAX_ROUNDS:
        ep.state(step["id"])["status"] = "failed"
        return Result(Outcome.FAILED, f"{step['title']}で{MAX_ROUNDS}回を超えて不合格になりました。"
                                      f" {ep.fmt(step['verdict'])} を読んで判断してください。")
    return Result(Outcome.RETRY, f"不合格のため「{back}」に差し戻しました（{st['rounds']}回目）。")


def run_step(ep: Episode, steps: list[dict], step: dict, claude_cmd: list[str],
             dry_run: bool = False) -> Result:
    kind = step["kind"]
    if kind in ("gate", "manual"):
        return Result(Outcome.WAIT_HUMAN, f"★ {step['title']}\n{ep.fmt(step.get('instructions', ''))}")

    st = ep.state(step["id"])
    if not dry_run:
        st.update(status="running", started=now())
        ep.save()
    res = _run_agent(ep, step, claude_cmd, dry_run) if kind == "agent" else _run_command(ep, step, dry_run)
    if dry_run:
        return res
    ep.reload()  # エージェントが episode.yaml の他の項目を変えている場合に備える
    st = ep.state(step["id"])
    if res.code != Outcome.DONE:
        st["status"] = "blocked" if res.code == Outcome.BLOCKED else "failed"
        st["ended"] = now()
        ep.save()
        return res
    missing = _missing_outputs(ep, step)
    if missing:
        st.update(status="failed", ended=now())
        ep.save()
        return Result(Outcome.FAILED, f"出力ファイルがありません: {', '.join(missing)}")
    st.update(status="done", ended=now())
    st.pop("feedback", None)
    if step.get("verdict"):
        verdict_res = _apply_verdict(ep, steps, step)
        ep.save()
        if verdict_res:
            return verdict_res
    ep.save()
    return res


def advance(root: Path, ep_id: str, claude_cmd: list[str], *, loop: bool, dry_run: bool = False,
            steps: list[dict] | None = None, log=print) -> int:
    """次の工程を実行する。loop=True なら関門・失敗・前提不足で止まるまで続ける。"""
    steps = steps or load_pipeline()
    while True:
        ep = Episode(root, ep_id)
        step = next_step(ep, steps)
        if step is None:
            log(f"{ep.id}: 全工程が終わっています。")
            return Outcome.FINISHED
        log(f"▶ {ep.id} 工程「{step['title']}」（{step['id']}）")
        res = run_step(ep, steps, step, claude_cmd, dry_run)
        if res.message:
            log(res.message)
        if res.code == Outcome.RETRY and loop:
            continue
        if res.code != Outcome.DONE or not loop or dry_run:
            return res.code


def approve(root: Path, ep_id: str, approval: str, by: str, note: str | None = None) -> None:
    ep = Episode(root, ep_id)
    if approval not in ep.data["approvals"]:
        raise SystemExit(f"承認の種類は {list(ep.data['approvals'])} のどれかです")
    ep.data["approvals"][approval] = {"by": by, "at": now(), **({"note": note} if note else {})}
    ep.save()
    ep.log({"at": now(), "step": approval, "kind": "approval", "by": by, "note": note})


def mark(root: Path, ep_id: str, step_id: str, status: str, reason: str | None = None,
         steps: list[dict] | None = None) -> None:
    steps = steps or load_pipeline()
    step = next((s for s in steps if s["id"] == step_id), None)
    if step is None:
        raise SystemExit(f"工程 {step_id} はありません: {[s['id'] for s in steps]}")
    if step["kind"] == "gate":
        raise SystemExit("関門は approve で進めてください")
    ep = Episode(root, ep_id)
    ep.data["steps"][step_id] = {"status": status, "ended": now(), **({"reason": reason} if reason else {})}
    ep.save()
    ep.log({"at": now(), "step": step_id, "kind": "manual-mark", "status": status, "reason": reason})


def reset(root: Path, ep_id: str, step_id: str, feedback: str | None = None,
          steps: list[dict] | None = None) -> list[str]:
    """工程をやり直す。その工程と、後ろにあるエージェント・プログラムの工程を未実行に戻す。
    関門の承認と人の作業（manual）は残す。"""
    steps = steps or load_pipeline()
    ids = [s["id"] for s in steps]
    if step_id not in ids:
        raise SystemExit(f"工程 {step_id} はありません: {ids}")
    ep = Episode(root, ep_id)
    reset_ids = [s["id"] for s in steps[ids.index(step_id):] if s["kind"] in ("agent", "command")]
    for sid in reset_ids:
        ep.data["steps"][sid] = {"status": "pending"}
    if feedback:
        ep.state(step_id)["feedback"] = feedback
    ep.save()
    ep.log({"at": now(), "step": step_id, "kind": "reset", "reset": reset_ids, "feedback": feedback})
    return reset_ids


def status_table(root: Path, ep_id: str, steps: list[dict] | None = None) -> str:
    steps = steps or load_pipeline()
    ep = Episode(root, ep_id)
    nxt = next_step(ep, steps)
    icon = {"done": "✓", "skipped": "－", "failed": "✗", "blocked": "■", "running": "…", "pending": " "}
    rows = [f"{ep.id}  {ep.data.get('title', '')}"]
    for s in steps:
        if s["kind"] == "gate":
            a = ep.data["approvals"].get(s["approval"])
            mark_ = "✓" if a else " "
            extra = f"{a['by']} {a['at'][:10]}" if a else ""
        else:
            st = ep.state(s["id"])
            mark_ = icon.get(st.get("status", "pending"), "?")
            extra = " ".join(x for x in [st.get("verdict", ""), st.get("reason", "")] if x)
        who = "人" if s["kind"] in ("gate", "manual") else (s.get("agent") or "プログラム")
        arrow = "→" if nxt is s else " "
        rows.append(f"{arrow}[{mark_}] {s['id']:<16} {s['title']:<22} {who:<16} {extra}")
    return "\n".join(rows)


def new_episode(root: Path, ep_id: str, slug: str, experiment: str, title: str = "",
                theme: str = "", series: str = "", mc_version: str = "TBD") -> Path:
    root = Path(root)
    if not re.fullmatch(r"EP\d{3}", ep_id):
        raise SystemExit("回のIDは EP001 の形にしてください")
    if not re.fullmatch(r"[a-z0-9_-]+", slug):
        raise SystemExit("スラッグは英小文字・数字・_・- だけにしてください")
    if list((root / "episodes").glob(f"{ep_id}_*")):
        raise SystemExit(f"{ep_id} はもうあります")
    dest = root / "episodes" / f"{ep_id}_{slug}"
    shutil.copytree(root / "episodes" / "_template", dest)
    f = dest / "episode.yaml"
    data = yaml.safe_load(f.read_text(encoding="utf-8"))
    data.update(id=ep_id, title=title, series=series, theme=theme,
                experiment=experiment.rstrip("/"), mc_version=mc_version)
    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    return dest
