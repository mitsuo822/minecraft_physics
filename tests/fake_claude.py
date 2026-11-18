"""テスト用の `claude` の代わり。プロンプトの「出力ファイル:」に並んだファイルを作り、JSONで結果を返す。

審査の判定は環境変数 FAKE_VERDICTS のファイルから1行ずつ取り出す（無ければ「合格」）。
受け取ったプロンプトは FAKE_PROMPTS のファイルに追記する。
"""
import json
import os
import sys
from pathlib import Path

LEDGER = {
    "ledger_version": "0.1",
    "episode": {"id": "EP900"},
    "cast": [{"id": "host"}, {"id": "guest"}],
    "sections": [{"id": "hook", "lines": [
        {"id": "l001", "speaker": "guest", "text": "生物は32 m/s²で落ちるの？"},
        {"id": "l002", "speaker": "host", "text": "3つの物で確かめよう"},
    ], "visuals": [{"id": "v1", "kind": "chart", "sync": {"start_line": "l001"}}]}],
    "facts": [{"id": "f01", "text": "生物の重力加速度は 32 m/s²", "confidence": "実測"}],
}


def next_verdict() -> str:
    f = os.environ.get("FAKE_VERDICTS")
    if not f or not Path(f).exists():
        return "合格"
    lines = Path(f).read_text(encoding="utf-8").splitlines()
    if not lines:
        return "合格"
    Path(f).write_text("\n".join(lines[1:]), encoding="utf-8")
    return lines[0]


def main() -> None:
    args = sys.argv[1:]
    prompt = args[args.index("-p") + 1]
    agent = args[args.index("--agent") + 1]
    if os.environ.get("FAKE_PROMPTS"):
        with open(os.environ["FAKE_PROMPTS"], "a", encoding="utf-8") as f:
            f.write(json.dumps({"agent": agent, "prompt": prompt}, ensure_ascii=False) + "\n")
    outs, on = [], False
    for line in prompt.splitlines():
        if line.startswith("出力ファイル:"):
            on = True
            continue
        if on and line.startswith("  - "):
            outs.append(line[4:].strip())
        elif on:
            on = False
    for o in outs:
        p = Path(o)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.name == "ledger.json":
            p.write_text(json.dumps(LEDGER, ensure_ascii=False), encoding="utf-8")
        elif p.name.startswith(("review_", "qc")):
            p.write_text(f"# 審査\n\n判定: {next_verdict()}\n", encoding="utf-8")
        else:
            p.write_text(f"# {agent} が作成\n", encoding="utf-8")
    print('[claude-code:unrecognized_model] {"model":"x"}')  # 本物の CLI が出すことのある警告の行
    print(json.dumps({"result": f"{agent}: {len(outs)}件を書きました", "total_cost_usd": 0.0, "is_error": False},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
