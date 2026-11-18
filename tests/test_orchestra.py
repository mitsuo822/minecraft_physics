"""orchestra の試験。エージェントは tests/fake_claude.py に差し替える（Claude は呼ばない）。"""
import json
import shutil
import sys
from pathlib import Path

import pytest

from orchestra import engine
from orchestra.check import check_ledger
from orchestra.engine import Outcome

REPO = Path(__file__).resolve().parent.parent
FAKE = [sys.executable, str(Path(__file__).with_name("fake_claude.py"))]


@pytest.fixture
def root(tmp_path, monkeypatch):
    shutil.copytree(REPO / "episodes" / "_template", tmp_path / "episodes" / "_template")
    engine.new_episode(tmp_path, "EP900", "test", "experiments/E900_test", title="試験", theme="T01", series="A")
    monkeypatch.delenv("MC_RCON_PASSWORD", raising=False)
    monkeypatch.setenv("FAKE_PROMPTS", str(tmp_path / "prompts.jsonl"))
    return tmp_path


def verdicts(root, *vs):
    (root / "verdicts.txt").write_text("\n".join(vs), encoding="utf-8")
    return str(root / "verdicts.txt")


def run(root):
    return engine.advance(root, "EP900", FAKE, loop=True, log=lambda *_: None)


def prompts(root):
    return [json.loads(l) for l in (root / "prompts.jsonl").read_text(encoding="utf-8").splitlines()]


def test_full_pipeline_stops_only_at_human_steps(root, monkeypatch):
    monkeypatch.setenv("FAKE_VERDICTS", verdicts(root, "不合格", "合格"))

    assert run(root) == Outcome.WAIT_HUMAN                       # 関門1
    engine.approve(root, "EP900", "theme", "試験者")
    assert run(root) == Outcome.WAIT_HUMAN                       # 調査→設計→審査で不合格→設計→審査→関門2
    calls = [p["agent"] for p in prompts(root)]
    assert calls == ["researcher", "physics-modeler", "physics-reviewer", "physics-modeler", "physics-reviewer"]
    assert "review_design.md" in prompts(root)[3]["prompt"]       # 2回目の設計には差し戻し理由が渡る

    engine.approve(root, "EP900", "design", "試験者")
    assert run(root) == Outcome.BLOCKED                          # サーバのパスワードが無い
    engine.mark(root, "EP900", "measure", "skipped", "試験")
    assert run(root) == Outcome.WAIT_HUMAN                       # 台本→チェック→最終審査→撮影（人）
    ep = engine.Episode(root, "EP900")
    assert ep.state("check")["status"] == "done"
    assert ep.state("final_review")["verdict"] == "合格"

    engine.mark(root, "EP900", "capture", "done")
    assert run(root) == Outcome.BLOCKED                          # movie 側が未実装
    engine.mark(root, "EP900", "build", "done")
    assert run(root) == Outcome.WAIT_HUMAN                       # 概要欄→QC→関門3
    engine.approve(root, "EP900", "publish", "試験者")
    assert run(root) == Outcome.FINISHED

    log = (next((root / "episodes").glob("EP900_*")) / "runlog.jsonl").read_text(encoding="utf-8")
    assert log.count('"kind": "agent"') == 9


def test_review_gives_up_after_max_rounds(root, monkeypatch):
    monkeypatch.setenv("FAKE_VERDICTS", verdicts(root, *["不合格"] * 5))
    engine.approve(root, "EP900", "theme", "試験者")
    assert run(root) == Outcome.FAILED
    calls = [p["agent"] for p in prompts(root)]
    assert calls.count("physics-reviewer") == engine.MAX_ROUNDS + 1


def test_next_runs_one_step_and_dry_run_changes_nothing(root):
    engine.approve(root, "EP900", "theme", "試験者")
    assert engine.advance(root, "EP900", FAKE, loop=False, dry_run=True, log=lambda *_: None) == Outcome.DONE
    assert engine.Episode(root, "EP900").state("research")["status"] == "pending"
    assert engine.advance(root, "EP900", FAKE, loop=False, log=lambda *_: None) == Outcome.DONE
    ep = engine.Episode(root, "EP900")
    assert ep.state("research")["status"] == "done"
    assert ep.state("design")["status"] == "pending"


def test_reset_keeps_approvals_and_human_steps(root, monkeypatch):
    engine.approve(root, "EP900", "theme", "試験者")
    run(root)
    engine.approve(root, "EP900", "design", "試験者")
    engine.mark(root, "EP900", "measure", "skipped", "試験")
    run(root)
    engine.mark(root, "EP900", "capture", "done")
    ids = engine.reset(root, "EP900", "script", feedback="メモ.md")
    assert ids[:3] == ["script", "check", "final_review"]
    ep = engine.Episode(root, "EP900")
    assert ep.state("capture")["status"] == "done"
    assert ep.data["approvals"]["design"]
    assert engine.next_step(ep, engine.load_pipeline())["id"] == "script"


def test_check_ledger_finds_unsupported_numbers(tmp_path):
    led = {
        "cast": [{"id": "host"}],
        "sections": [{"id": "s", "lines": [
            {"id": "l1", "speaker": "host", "text": "重力は３２ m/s²、終端速度は78.4 m/s"},
            {"id": "l2", "speaker": "nobody", "text": "2人で見よう"},
        ], "visuals": [{"id": "v1", "sync": {"start_line": "l9"}}]}],
        "facts": [
            {"id": "f1", "text": "32 m/s²", "confidence": "実測"},
            {"id": "f2", "text": "終端速度 78.4 m/s", "confidence": "未確認"},
        ],
    }
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps(led, ensure_ascii=False), encoding="utf-8")
    ng = check_ledger(p)
    assert any("78.4" in x for x in ng)          # 【未確認】の数字は断言できない
    assert not any("数字 32" in x for x in ng)   # 全角の３２も【実測】の32として通る
    assert any("nobody" in x for x in ng)
    assert any("l9" in x for x in ng)
    assert len(ng) == 3
