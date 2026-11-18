"""計測結果（measurements.csv ほか）を解析し、results.json / summary.md / theory.csv を出す。

experiment.yaml の analysis が正本。ここでは次をそのとおりに計算する:
  - analysis.checks のうち auto: true の項目（CHECKS に同じ id の関数がある。試験で対応を確かめる）
  - analysis.groups / across: 組の y(t)・Motion.y(t) が tick ごとに一致するか
  - analysis.separate: 別の問い（NoAI の豚が落ちたか）
  - 当てはめ（g, d, 順序）と予想の比較、到達した最大の速さ【実測】、地球比の3つの定義

summary.md の列名は、計測した値に【実測】、当てはめや式から出した値に（計算値）を付けて分ける。
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import yaml

from . import parse
from .models import e001_predictions as pred
from .models import free_fall_mc as mc
from .models import free_fall_real as real

TPS = mc.TICKS_PER_SEC
SAME_TOL = 1e-9          # 「完全に一致」の許容（応答の小数の読み取りの丸めだけ）。experiment.yaml analysis.groups の注記
POS_TOL = 1e-6           # 召喚した高さ・地面の高さとの一致
REL_TOL = 0.01           # 予想との比較（experiment.yaml analysis.compare）
OK, NG, WARN, NONE = "合格", "不合格", "注意", "未実施"
MEASURED, CALC = "【実測】", "（計算値）"


def _f(v: str) -> float | None:
    return float(v) if v not in ("", None) else None


def load_rows(run_dir: Path) -> list[dict]:
    with (run_dir / "measurements.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["repeat"], r["tick"], r["exists"] = int(r["repeat"]), int(r["tick"]), int(r["exists"])
        r["on_ground"] = int(r["on_ground"]) if r["on_ground"] not in ("", None) else None
        for k in ("x", "y", "z", "vx", "vy", "vz"):
            r[k] = _f(r[k])
    return rows


def load_commands(run_dir: Path) -> list[dict] | None:
    p = run_dir / "commands.jsonl"
    if not p.exists():
        return None
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_realtime(run_dir: Path) -> list[dict] | None:
    p = run_dir / "realtime.csv"
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("poll", "tick_lo", "tick_hi", "exists"):
            r[k] = int(r[k])
        r["on_ground"] = int(r["on_ground"]) if r["on_ground"] not in ("", None) else None
    return rows


# --- 1つの対象・1回の繰り返し ------------------------------------------------

def analyze_track(rows: list[dict], ground_y: float, const: dict | None) -> dict:
    rows = sorted(rows, key=lambda r: r["tick"])
    air = [r for r in rows if r["exists"] and r["on_ground"] == 0]
    airborne = [(r["tick"], r["y"], r["vy"]) for r in air]
    landed = next((r for r in rows if r["tick"] > 0 and (not r["exists"] or r["on_ground"] == 1)), None)
    t0 = next((r for r in rows if r["tick"] == 0), None)
    by_tick = {r["tick"]: r for r in air}
    out: dict = {
        "type": mc.entity_key(rows[0]["type"]),
        "exists_t0": bool(t0 and t0["exists"]),
        "y0": t0["y"] if t0 and t0["exists"] else None,
        "vy0": t0["vy"] if t0 and t0["exists"] else None,
        "landing_tick": landed["tick"] if landed else None,
        "landing_how": None if not landed else ("消滅" if not landed["exists"] else "着地"),
        "landing_y": landed["y"] if landed and landed["exists"] else None,
        "airborne_ticks": len(airborne),
        # 【実測】tick の終わりの Motion.y の最大の大きさ、1tick ごとの Pos.y の差の最大
        "max_fall_speed_ms": max((-v for _, _, v in airborne), default=0.0) * TPS,
        "max_fall_step_ms": max((a[1] - b[1] for a, b in zip(airborne, airborne[1:]) if b[0] == a[0] + 1),
                                default=0.0) * TPS,
        "horizontal_drift": max((max(abs(r["x"] - air[0]["x"]), abs(r["z"] - air[0]["z"])) for r in air), default=0.0),
        "series": {t: [y, v] for t, y, v in airborne},
    }
    if 0 in by_tick and 1 in by_tick:
        out["first_tick_drop"] = by_tick[0]["y"] - by_tick[1]["y"]                 # 【実測】
        out["first_dv_ms2"] = mc.accel_ms2(by_tick[0]["vy"] - by_tick[1]["vy"])    # 【実測】の差分（換算は前提つき）
    if airborne:
        t_last, y_last, v_last = airborne[-1]
        out["last_airborne"] = {"tick": t_last, "gap": y_last - ground_y, "vy": v_last}
        if const and const.get("order") in mc.ORDERS:
            out["last_airborne"]["next_step"] = mc.next_step_distance(v_last, const["g"], const["order"])
    f = mc.fit(airborne)
    if f:
        out["fit"] = {
            "g_block_per_tick2": f.g, "d": f.d, "order": f.order,
            "g_ms2": f.g_ms2, "g_ratio_earth": f.g_ms2 / real.G_EARTH,
            "terminal_ms": f.terminal_ms,
            "time_constant_s": mc.time_constant_s(f.d) if 0 < f.d < 1 else None,
            "g_if_drag_then_accel": f.g_if_drag_then_accel,
            "rms_velocity": f.rms_velocity, "rms_position": f.rms_position, "n_pairs": f.n_pairs,
        }
    return out


def _spread(vals: list) -> dict:
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"mean": None, "min": None, "max": None}
    return {"mean": statistics.fmean(vals), "min": min(vals), "max": max(vals)}


def compare_expected(fit: dict | None, expected: dict | None, rel_tol: float = REL_TOL) -> dict:
    if not fit or not expected:
        return {"status": "比較できない"}
    g_err = abs(fit["g_block_per_tick2"] - expected["g"]) / expected["g"]
    d_err = abs(fit["d"] - expected["d"]) / expected["d"]
    order_ok = expected.get("order") in (None, "unknown") or expected["order"] == fit["order"]
    ok = g_err <= rel_tol and d_err <= rel_tol and order_ok
    out = {"status": "予想どおり" if ok else "予想と違う", "g_rel_err": g_err, "d_rel_err": d_err,
           "order_expected": expected.get("order"), "order_measured": fit["order"]}
    if not ok and d_err <= rel_tol:
        alt = abs(fit["g_if_drag_then_accel"] - expected["g"]) / expected["g"]
        out["g_rel_err_if_drag_then_accel"] = alt
        if alt <= rel_tol:
            out["note"] = "「抵抗→加速」と読めば g が予想と合う（model.md §2.3）"
    return out


def series_match(a: dict, b: dict, tol: float = SAME_TOL) -> dict:
    """2つの y(t)・Motion.y(t)（空中の tick → [y, vy]）が tick ごとに一致するか。空中の tick の集合も同じであること。"""
    a = {int(k): v for k, v in a.items()}
    b = {int(k): v for k, v in b.items()}
    common = sorted(set(a) & set(b))
    dy = max((abs(a[t][0] - b[t][0]) for t in common), default=None)
    dv = max((abs(a[t][1] - b[t][1]) for t in common), default=None)
    first = next((t for t in common if abs(a[t][0] - b[t][0]) > tol or abs(a[t][1] - b[t][1]) > tol), None)
    same_ticks = set(a) == set(b)
    if first is None and not same_ticks:
        first = min(set(a) ^ set(b))
    return {"match": bool(common) and same_ticks and first is None, "n_ticks": len(common),
            "max_dy": dy, "max_dvy": dv, "first_mismatch_tick": first, "same_airborne_ticks": same_ticks}


# --- 確認項目（experiment.yaml analysis.checks の auto: true） --------------------

def _r(status: str, detail: str) -> dict:
    return {"status": status, "detail": detail}


def check_server_version(ctx: dict, spec: dict) -> dict:
    """計測したサーバの版（起動ログから読んだもの）が experiment.yaml の mc_version と同じか。"""
    meta = ctx.get("meta") or {}
    want = str(ctx["exp"].get("mc_version"))
    got = meta.get("server_version")
    if got == "fake":
        return _r(NONE, "模擬サーバ（版の確認なし。数字は実測ではない）")
    if not got:
        return _r(NG, f"サーバの版の証拠がない（{meta.get('server_version_source', 'meta.json に記録なし')}）")
    if got != want:
        return _r(NG, f"サーバの起動ログは {got}、experiment.yaml は {want}")
    return _r(OK, f"起動ログ: {meta.get('server_version_line', got)}")


def check_setup_ok(ctx: dict, spec: dict) -> dict:
    cmds = ctx["commands"]
    if cmds is None:
        return _r(NONE, "commands.jsonl がない（応答を記録していない計測）")
    bad = [c for c in cmds if c["error"]]
    if bad:
        return _r(NG, "; ".join(f"{c['cmd']} -> {c['response'].strip()[:80]}" for c in bad[:5]))
    return _r(OK, f"{len(cmds)} 件の応答に失敗なし")


def check_spawned(ctx: dict, spec: dict) -> dict:
    miss = [f"{tid}（繰り返し{rep}）" for tid, t in ctx["targets"].items()
            for rep, p in t["repeats"].items() if not p["exists_t0"]]
    return _r(NG, "t=0 にいない: " + "、".join(miss)) if miss else _r(OK, "全対象が t=0 に存在")


def check_t0_state(ctx: dict, spec: dict) -> dict:
    bad = []
    for tid, t in ctx["targets"].items():
        y_exp = ctx["ground_y"] + ctx["spawn_heights"][tid]
        for rep, p in t["repeats"].items():
            if p["y0"] is None or abs(p["y0"] - y_exp) > POS_TOL or abs(p["vy0"] or 0.0) > SAME_TOL:
                bad.append(f"{tid}（繰り返し{rep}: y={p['y0']}, Motion.y={p['vy0']}）")
    return _r(NG, "、".join(bad)) if bad else _r(OK, "全対象で t=0 の Motion.y=0、y=召喚した高さ")


def check_deterministic(ctx: dict, spec: dict) -> dict:
    bad = []
    for tid, t in ctx["targets"].items():
        reps = list(t["repeats"].values())
        if len({p["landing_tick"] for p in reps}) > 1:
            bad.append(f"{tid}: 着地tickが違う")
            continue
        for p in reps[1:]:
            if not series_match(reps[0]["series"], p["series"])["match"]:
                bad.append(f"{tid}: y(t) が違う")
                break
    n = len(next(iter(ctx["targets"].values()))["repeats"]) if ctx["targets"] else 0
    if n < 2:
        return _r(NONE, "繰り返しが1回しかない")
    return _r(NG, "、".join(bad)) if bad else _r(OK, f"{n} 回とも着地tickと y(t) が一致")


def check_horizontal(ctx: dict, spec: dict) -> dict:
    warn_only = set(spec.get("warn_only", []))
    ng, warn = [], []
    for tid, t in ctx["targets"].items():
        drift = max(p["horizontal_drift"] for p in t["repeats"].values())
        if drift > SAME_TOL:
            (warn if tid in warn_only else ng).append(f"{tid}（最大 {drift:.3g} ブロック）")
    if ng:
        return _r(NG, "水平に動いた: " + "、".join(ng + warn))
    if warn:
        return _r(WARN, "AI のある生物が水平に動いた（縦の比較は続ける。結論にその旨を書く）: " + "、".join(warn))
    return _r(OK, "空中で水平の位置が変わらない")


def check_landing_gap(ctx: dict, spec: dict) -> dict:
    bad, ok = [], []
    for tid, t in ctx["targets"].items():
        if t["type"] != "falling_block":
            continue
        for rep, p in t["repeats"].items():
            la = p.get("last_airborne")
            if p["landing_how"] != "消滅" or not la or "next_step" not in la:
                bad.append(f"{tid}（繰り返し{rep}: 消滅していない）")
            elif not (0 < la["gap"] <= la["next_step"]):
                bad.append(f"{tid}（繰り返し{rep}: 高さ {la['gap']:.3f} > 次の移動 {la['next_step']:.3f}）")
            else:
                ok.append(tid)
    if not bad and not ok:
        return _r(NONE, "落下ブロックの対象がない")
    return _r(NG, "、".join(bad)) if bad else _r(OK, "金床・砂とも、次の1tickで地面に届く位置で消えた")


def check_block_placed(ctx: dict, spec: dict) -> dict:
    cmds = ctx["commands"]
    if cmds is None:
        return _r(NONE, "commands.jsonl がない")
    tests = [c for c in cmds if c.get("check") and c["phase"] == "procedure"]
    if not tests:
        return _r(NONE, "procedure に check 付きのコマンドがない")
    bad = []
    for c in tests:
        res = parse.execute_test_result(c["response"])
        if res is not True:
            bad.append(f"{c['check']}（繰り返し{c['repeat']}: {c['response'].strip()[:40] or '応答なし'}）")
        t = ctx["targets"].get(c["check"])
        if t:
            lt = t["repeats"].get(c["repeat"], {}).get("landing_tick")
            if lt is None or lt >= c["tick"]:
                bad.append(f"{c['check']}（繰り返し{c['repeat']}: 消滅 tick {lt} が tick {c['tick']} より前でない）")
    return _r(NG, "、".join(bad)) if bad else _r(OK, f"{len(tests)} 件とも Test passed、消滅は確認の tick より前")


def check_ground_y(ctx: dict, spec: dict) -> dict:
    bad, n = [], 0
    for tid, t in ctx["targets"].items():
        for rep, p in t["repeats"].items():
            if p["landing_how"] == "着地":
                n += 1
                if abs(p["landing_y"] - ctx["ground_y"]) > POS_TOL:
                    bad.append(f"{tid}（繰り返し{rep}: y={p['landing_y']}）")
    if n == 0:
        return _r(NONE, "OnGround で着地した対象がない")
    return _r(NG, "、".join(bad)) if bad else _r(OK, f"着地時の y がすべて {ctx['ground_y']:g}")


def realtime_windows(rt: list[dict], skip: set[str]) -> dict[str, dict]:
    """通常速度での着地 tick の幅。空中を見た問い合わせ → 着地 tick ≥ tick_lo + 1、着地を見た → ≤ tick_hi。"""
    out = {}
    for tid in sorted({r["target"] for r in rt} - skip):
        mine = [r for r in rt if r["target"] == tid]
        air = [r["tick_lo"] + 1 for r in mine if r["exists"] and r["on_ground"] == 0]
        land = [r["tick_hi"] for r in mine if not r["exists"] or r["on_ground"] == 1]
        lo = max(air, default=0)
        hi = min(land, default=None)
        out[tid] = {"lo": lo, "hi": hi, "width": None if hi is None else hi - lo + 1}
    return out


def check_realtime(ctx: dict, spec: dict) -> dict:
    rt = ctx["realtime"]
    if rt is None:
        return _r(NONE, "realtime.csv がない（measure.realtime_check を実行していない）")
    max_w = int(ctx["exp"]["measure"].get("realtime_check", {}).get("max_window_ticks", 3))
    wins = realtime_windows(rt, ctx["skip_landing"])
    ctx["realtime_windows"] = wins
    bad, wide = [], []
    for tid, w in wins.items():
        lt = ctx["targets"][tid]["repeats"][min(ctx["targets"][tid]["repeats"])]["landing_tick"]
        w["tick_step_landing"] = lt
        if w["hi"] is None:
            bad.append(f"{tid}: 通常速度で着地しなかった")
        elif w["width"] > max_w:
            wide.append(f"{tid}: 幅 {w['width']} tick")
        elif not (w["lo"] <= (lt if lt is not None else -1) <= w["hi"]):
            bad.append(f"{tid}: 通常速度 {w['lo']}〜{w['hi']}、tick step {lt}")
    if bad:
        return _r(NG, "、".join(bad))
    if wide:
        return _r(NG, f"判定できない（幅が {max_w} tick を超えた。RCON が遅い）: " + "、".join(wide))
    return _r(OK, f"{len(wins)} 対象とも、tick step の着地 tick が通常速度の幅に入る")


CHECKS = {
    "server_version": check_server_version, "setup_ok": check_setup_ok, "spawned": check_spawned, "t0_state": check_t0_state,
    "deterministic": check_deterministic, "horizontal": check_horizontal, "landing_gap": check_landing_gap,
    "block_placed": check_block_placed, "ground_y": check_ground_y, "realtime": check_realtime,
}


def run_checks(ctx: dict) -> list[dict]:
    out = []
    for spec in ctx["exp"].get("analysis", {}).get("checks", []):
        if isinstance(spec, str):
            spec = {"id": None, "auto": False, "text": spec}
        if spec.get("auto") and spec.get("id") in CHECKS:
            res = CHECKS[spec["id"]](ctx, spec)
        elif spec.get("auto"):
            res = _r(NG, f"自動の判定が lab/analyze.py にない（id: {spec.get('id')}）")
        else:
            res = _r(NONE, "人が判定する")
        out.append({"id": spec.get("id"), "text": spec.get("text", ""), **res})
    return out


# --- 全体 ----------------------------------------------------------------------

def _group_results(targets: dict, specs: list[dict]) -> list[dict]:
    out = []
    for g in specs or []:
        members = [m for m in g["members"] if m in targets]
        base = members[0]
        s0 = targets[base]["repeats"][min(targets[base]["repeats"])]["series"]
        pairs = {m: series_match(s0, targets[m]["repeats"][min(targets[m]["repeats"])]["series"]) for m in members[1:]}
        out.append({"name": g["name"], "members": members, "base": base, "pairs": pairs,
                    "match": all(p["match"] for p in pairs.values()) and len(members) >= 2})
    return out


def _separate_results(targets: dict, specs: list[dict]) -> list[dict]:
    out = []
    for s in specs or []:
        t = targets.get(s["id"])
        if not t:
            continue
        p = t["repeats"][min(t["repeats"])]
        ys = [v[0] for v in p["series"].values()]
        fell = p["landing_tick"] is not None or (bool(ys) and p["y0"] is not None and
                                                 max(abs(y - p["y0"]) for y in ys) > SAME_TOL)
        res = {"id": s["id"], "label": t["label"], "question": s.get("question"), "fell": fell,
               "max_drop": (p["y0"] - min(ys)) if ys and p["y0"] is not None else None,
               "airborne_ticks": p["airborne_ticks"]}
        if fell and s.get("ref") in targets:
            ref = targets[s["ref"]]
            res["ref"] = s["ref"]
            res["vs_ref"] = series_match(ref["repeats"][min(ref["repeats"])]["series"], p["series"])
        out.append(res)
    return out


def _earth_ratios(targets: dict, members_by_type: dict[str, list[str]]) -> list[dict]:
    out = []
    for key, ids in members_by_type.items():
        p = targets[ids[0]]["repeats"][min(targets[ids[0]]["repeats"])]
        f = p.get("fit")
        row = {"type": key, "targets": ids,
               "r1_fit_g": f["g_ms2"] / real.G_EARTH if f else None,
               "r2_first_dv": p["first_dv_ms2"] / real.G_EARTH if "first_dv_ms2" in p else None,
               "r3_continuous": (f["terminal_ms"] / f["time_constant_s"] / real.G_EARTH)
               if f and f.get("time_constant_s") else None}
        out.append(row)
    return out


def analyze(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    rows = load_rows(run_dir)
    exp = yaml.safe_load((run_dir / "experiment.snapshot.yaml").read_text(encoding="utf-8"))
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8")) if (run_dir / "meta.json").exists() else {}
    ents = {e["id"]: e for e in exp["setup"]["entities"]}
    ground_y = float(exp["setup"].get("origin", [0, 0, 0])[1])
    consts_all = mc.load_constants()
    consts = consts_all["types"]
    heights = pred.spawn_heights(exp)
    height = pred.drop_height(exp)
    ana = exp.get("analysis", {})
    separate_ids = {s["id"] for s in ana.get("separate", []) or []}

    groups: dict[str, dict[int, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        groups[r["target"]][r["repeat"]].append(r)

    targets = {}
    for tid in exp["measure"]["targets"]:
        key = mc.entity_key(ents[tid]["summon"])
        predicted = ents[tid].get("predict", True)
        expected = consts.get(key) if predicted else None
        per_rep = {rep: analyze_track(rs, ground_y, consts.get(key)) for rep, rs in sorted(groups[tid].items())}
        first = per_rep[min(per_rep)]
        fits = [p.get("fit") for p in per_rep.values()]
        prediction = None
        if expected and expected.get("order") in mc.ORDERS:
            pr = mc.predict(key, height, consts_all)
            prediction = {"landing_tick": pr.landing_tick, "first_tick_drop": pr.first_tick_drop,
                          "max_motion_ms": mc.speed_ms(pr.max_motion), "terminal_ms": mc.speed_ms(pr.terminal_motion)}
        targets[tid] = {
            "label": ents[tid].get("label", tid),
            "type": key,
            "predicted": bool(predicted),
            "repeats": per_rep,
            "summary": {
                "landing_tick": _spread([p["landing_tick"] for p in per_rep.values()]),
                "g_ms2": _spread([f["g_ms2"] for f in fits if f]),
                "d": _spread([f["d"] for f in fits if f]),
                "terminal_ms": _spread([f["terminal_ms"] for f in fits if f]),
                "max_fall_speed_ms": _spread([p["max_fall_speed_ms"] for p in per_rep.values()]),
                "orders": sorted({f["order"] for f in fits if f}),
            },
            "expected": expected,
            "prediction": prediction,
            "vs_expected": compare_expected(first.get("fit"), expected),
        }

    ctx = {"exp": exp, "meta": meta, "targets": targets, "ground_y": ground_y, "spawn_heights": heights,
           "commands": load_commands(run_dir), "realtime": load_realtime(run_dir),
           "skip_landing": set(exp["measure"].get("until", {}).get("not_required_to_land", []) or [])}
    checks = run_checks(ctx)
    ok_to_conclude = all(c["status"] in (OK, WARN) for c in checks)

    members_by_type: dict[str, list[str]] = {}
    for tid, t in targets.items():
        if t["predicted"]:
            members_by_type.setdefault(t["type"], []).append(tid)

    def mean_landing(tid: str) -> float:
        v = targets[tid]["summary"]["landing_tick"]["mean"]
        return v if v is not None else float("inf")

    order = sorted((t for t in targets if t not in separate_ids), key=mean_landing)
    result = {
        "experiment": exp["id"],
        "mc_version": meta.get("mc_version") or exp.get("mc_version"),
        "constants_confidence": consts_all.get("confidence"),
        "ground_y": ground_y,
        "drop_height_blocks": height,
        "real_vacuum_fall_time_s": real.fall_time_vacuum(height),
        "checks": checks,
        "ok_to_conclude": ok_to_conclude,
        "realtime_windows": ctx.get("realtime_windows"),
        "groups": _group_results(targets, ana.get("groups")),
        "across": _group_results(targets, ana.get("across")),
        "separate": _separate_results(targets, ana.get("separate")),
        "separate_ids": sorted(separate_ids),
        "earth_ratios": _earth_ratios(targets, members_by_type),
        "landing_order": [{"target": t, "label": targets[t]["label"],
                           "landing_tick": targets[t]["summary"]["landing_tick"]["mean"]} for t in order],
        "targets": targets,
    }
    (run_dir / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_theory_csv(run_dir, result, ground_y)
    (run_dir / "summary.md").write_text(summary_markdown(result), encoding="utf-8")
    return result


def write_theory_csv(run_dir: Path, result: dict, ground_y: float) -> None:
    """動画のグラフ用: 当てはめた MC モデルと、現実（真空）の理論曲線（どちらも計算値）。"""
    height = result["drop_height_blocks"] or 0.0
    n = max((t["summary"]["landing_tick"]["max"] or 0) for t in result["targets"].values()) + 5
    curves = {}
    for tid, t in result["targets"].items():
        rep = t["repeats"][min(t["repeats"])]
        if rep.get("fit") and rep["y0"] is not None:
            f = rep["fit"]
            curves[tid] = {s[0]: s[1] for s in mc.simulate(rep["y0"], 0.0, f["g_block_per_tick2"], f["d"], f["order"], n, ground_y)}
    with (run_dir / "theory.csv").open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["tick", "t_sec", "real_vacuum_height"] + [f"mc_{tid}_height" for tid in curves])
        for k in range(n + 1):
            ts = k / TPS
            h_real = max(real.vacuum(height, ts)[0], 0.0)
            w.writerow([k, f"{ts:.3f}", f"{h_real:.4f}"] +
                       [f"{curves[tid][k] - ground_y:.4f}" if k in curves[tid] else "" for tid in curves])


# --- summary.md ---------------------------------------------------------------

def _num(v, fmt: str) -> str:
    return "–" if v is None else format(v, fmt)


def summary_markdown(r: dict) -> str:
    fake = str(r["mc_version"]) == "fake"
    L = [f"# {r['experiment']} 計測結果", "",
         f"- MCバージョン: {r['mc_version']}",
         f"- 落下の高さ: {r['drop_height_blocks']:g} ブロック",
         f"- 予想値の確度: {r['constants_confidence']}（knowledge/mechanics/重力と空気抵抗.md）",
         f"- 列名の決まり: {MEASURED} = 計測した値（換算は 1ブロック=1 m、20 tick/s の前提つき）、"
         f"{CALC} = 当てはめや式から出した値。台本で【実測】と書けるのは {MEASURED} の列だけ",
         ""]
    if fake:
        L += ["> **模擬サーバの結果。{0} の列も実測ではない**（物理は予想値で動いている）。".format(MEASURED), ""]

    L += ["## 確認項目（experiment.yaml analysis.checks）", "",
          f"判定: **{'結論を出してよい' if r['ok_to_conclude'] else '結論を出さない'}**"
          "（「不合格」「未実施」が1つでもあれば出さない）", "",
          "| id | 状態 | 内容 | 詳細 |", "|---|---|---|---|"]
    for c in r["checks"]:
        L.append(f"| {c['id']} | {c['status']} | {c['text']} | {c['detail']} |")

    L += ["", "## 同じ種類の組: y(t)・Motion.y(t) が tick ごとに一致するか " + MEASURED, "",
          "| 組 | 対象 | 一致 | 比べた tick 数 | y の最大差（ブロック） | Motion.y の最大差（ブロック/tick） |",
          "|---|---|---|---|---|---|"]
    labels = {tid: t["label"] for tid, t in r["targets"].items()}
    for g in r["groups"] + r["across"]:
        n = min((p["n_ticks"] for p in g["pairs"].values()), default=0)
        dy = max((p["max_dy"] or 0 for p in g["pairs"].values()), default=None)
        dv = max((p["max_dvy"] or 0 for p in g["pairs"].values()), default=None)
        L.append(f"| {g['name']} | {'・'.join(labels[m] for m in g['members'])} | {'一致' if g['match'] else '不一致'} | "
                 f"{n} | {_num(dy, '.3g')} | {_num(dv, '.3g')} |")

    if r["separate"]:
        L += ["", "## 別の問い（「重さか種類か」の比較に入れない。【MCの仕様】として別に扱う）", "",
              f"| 対象 | 問い | 落ちたか {MEASURED} | 召喚した高さからの最大の落下（ブロック） {MEASURED} | 落ちた場合、比べる相手と y(t) が一致 |",
              "|---|---|---|---|---|"]
        for s in r["separate"]:
            vs = s.get("vs_ref")
            L.append(f"| {s['label']} | {s['question']} | {'落ちた' if s['fell'] else '落ちなかった'} | "
                     f"{_num(s['max_drop'], '.3g')} | "
                     f"{'–' if not vs else (labels[s['ref']] + ('と一致' if vs['match'] else 'と不一致'))} |")

    L += ["", "## 着地", "",
          f"| 対象 | 種類 | 着地tick {MEASURED} | 着地時刻（s） {MEASURED} | 判定のしかた | 3回の幅 {MEASURED} | 着地tick（予想・計算値） |",
          "|---|---|---|---|---|---|---|"]
    for tid in [o["target"] for o in r["landing_order"]] + r["separate_ids"]:
        t = r["targets"][tid]
        p = t["repeats"][min(t["repeats"])]
        lt, s = p["landing_tick"], t["summary"]["landing_tick"]
        pr = t["prediction"]
        L.append(f"| {t['label']} | {t['type']} | {_num(lt, 'd') if lt is not None else '着地せず'} | "
                 f"{_num(lt / TPS if lt is not None else None, '.2f')} | {p['landing_how'] or '–'} | "
                 f"{_num(s['min'], 'g')}〜{_num(s['max'], 'g')} | {pr['landing_tick'] if pr else '予想なし'} |")
    L.append(f"\n参考{CALC}: 現実の真空中なら、同じ高さ（m として）をどれも {r['real_vacuum_fall_time_s']:.2f} 秒で同時に落ちる。")

    L += ["", "## 落下の速さ（E001 では終端速度は測らない）", "",
          f"| 対象 | 1tick目の落下（ブロック） {MEASURED} | 1tick目の落下（予想・計算値） | "
          f"到達した最大の速さ・Motion（m/s） {MEASURED} | 到達した最大の速さ・Pos の差（m/s） {MEASURED} | "
          f"終端速度（m/s）{CALC}（当てはめた g, d から） | 終端に対する割合 {CALC} |",
          "|---|---|---|---|---|---|---|"]
    for tid, t in r["targets"].items():
        if not t["predicted"]:
            continue
        p = t["repeats"][min(t["repeats"])]
        f = p.get("fit")
        term = f["terminal_ms"] if f else None
        frac = p["max_fall_speed_ms"] / term if term else None
        pr = t["prediction"]
        L.append(f"| {t['label']} | {_num(p.get('first_tick_drop'), '.4g')} | {_num(pr and pr['first_tick_drop'], 'g')} | "
                 f"{p['max_fall_speed_ms']:.1f} | {p['max_fall_step_ms']:.1f} | {_num(term, '.1f')} | {_num(frac, '.0%')} |")

    L += ["", f"## 当てはめた値 {CALC}", "",
          f"| 対象 | 種類 | g（ブロック/tick²）{CALC} | 空気抵抗 d {CALC} | 順序 {CALC} | 予想との比較（相対 {REL_TOL:.0%} 以内） |",
          "|---|---|---|---|---|---|"]
    for t in r["targets"].values():
        f = t["repeats"][min(t["repeats"])].get("fit")
        if not f:
            L.append(f"| {t['label']} | {t['type']} | – | – | – | 当てはめ不可 |")
            continue
        vs = t["vs_expected"]
        L.append(f"| {t['label']} | {t['type']} | {f['g_block_per_tick2']:.4f} | {f['d']:.4f} | {f['order']} | "
                 f"{vs['status']}{'（' + vs['note'] + '）' if vs.get('note') else ''} |")

    L += ["", f"## 地球比（9.80665 m/s² に対する倍率。3つの定義。どれも 1ブロック=1 m、20 tick/s の前提つき）", "",
          f"| 種類 | 対象 | ①当てはめた g パラメータ {CALC} | ②1tick目の Motion の変化（{MEASURED}の差分を換算） | "
          f"③連続時間の等価加速度 {CALC}（終端÷時定数） |", "|---|---|---|---|---|"]
    for e in r["earth_ratios"]:
        L.append(f"| {e['type']} | {'・'.join(labels[i] for i in e['targets'])} | {_num(e['r1_fit_g'], '.3f')} | "
                 f"{_num(e['r2_first_dv'], '.3f')} | {_num(e['r3_continuous'], '.3f')} |")

    L += ["", "## 注意", "",
          "- 終端速度の列は当てはめからの計算値。どの対象も着地までに終端に届かないので、測った速さではない。",
          "- 地球比は小数2桁目が定義で変わる。台本では定義と前提を画面に書き、根拠の精度に丸める。",
          "- 繰り返しの間で値がばらついていないかは results.json の `summary` を見る。",
          "- 位置の残差（rms_position）が両方の順序で大きいときは、モデルの式そのものが合っていない。",
          "- 送ったコマンドと応答の全文は commands.jsonl にある。"]
    return "\n".join(L) + "\n"
