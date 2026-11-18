"""計測結果（measurements.csv）を解析し、results.json / summary.md / theory.csv を出す。"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import yaml

from .models import free_fall_mc as mc
from .models import free_fall_real as real

TPS = mc.TICKS_PER_SEC


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


def analyze_track(rows: list[dict]) -> dict:
    """1回の繰り返しの、1つの追跡対象。"""
    rows = sorted(rows, key=lambda r: r["tick"])
    airborne = [(r["tick"], r["y"], r["vy"]) for r in rows if r["exists"] and r["on_ground"] == 0]
    landed = next((r for r in rows if r["tick"] > 0 and (not r["exists"] or r["on_ground"] == 1)), None)
    y0 = airborne[0][1] if airborne else None
    out: dict = {
        "type": mc.entity_key(rows[0]["type"]),
        "y0": y0,
        "landing_tick": landed["tick"] if landed else None,
        "landing_how": None if not landed else ("消滅" if not landed["exists"] else "着地"),
        "airborne_ticks": len(airborne),
        "max_fall_speed_ms": max((-v for _, _, v in airborne), default=0.0) * TPS,
    }
    f = mc.fit(airborne)
    if f:
        out["fit"] = {
            "g_block_per_tick2": f.g, "d": f.d, "order": f.order,
            "g_ms2": f.g_ms2, "g_ratio_earth": f.g_ms2 / real.G_EARTH,
            "terminal_ms": f.terminal_ms,
            "rms_velocity": f.rms_velocity, "rms_position": f.rms_position, "n_pairs": f.n_pairs,
        }
    return out


def _spread(vals: list[float]) -> dict:
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"mean": None, "min": None, "max": None}
    return {"mean": statistics.fmean(vals), "min": min(vals), "max": max(vals)}


def compare_expected(fit: dict | None, expected: dict | None, rel_tol: float = 0.01) -> dict:
    if not fit or not expected:
        return {"status": "比較できない"}
    g_err = abs(fit["g_block_per_tick2"] - expected["g"]) / expected["g"]
    d_err = abs(fit["d"] - expected["d"]) / expected["d"]
    order_ok = expected.get("order") in (None, "unknown") or expected["order"] == fit["order"]
    ok = g_err <= rel_tol and d_err <= rel_tol and order_ok
    return {"status": "予想どおり" if ok else "予想と違う", "g_rel_err": g_err, "d_rel_err": d_err,
            "order_expected": expected.get("order"), "order_measured": fit["order"]}


def analyze(run_dir: str | Path) -> dict:
    run_dir = Path(run_dir)
    rows = load_rows(run_dir)
    exp = yaml.safe_load((run_dir / "experiment.snapshot.yaml").read_text(encoding="utf-8"))
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8")) if (run_dir / "meta.json").exists() else {}
    labels = {e["id"]: e.get("label", e["id"]) for e in exp["setup"]["entities"]}
    ground_y = float(exp["setup"].get("origin", [0, 0, 0])[1])
    consts = mc.load_constants()["types"]

    groups: dict[str, dict[int, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        groups[r["target"]][r["repeat"]].append(r)

    targets = {}
    for tid in exp["measure"]["targets"]:
        per_rep = {rep: analyze_track(rs) for rep, rs in sorted(groups[tid].items())}
        first = per_rep[min(per_rep)]
        expected = consts.get(first["type"])
        fits = [p.get("fit") for p in per_rep.values()]
        targets[tid] = {
            "label": labels.get(tid, tid),
            "type": first["type"],
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
            "vs_expected": compare_expected(first.get("fit"), expected),
        }

    def mean_landing(tid: str) -> float:
        v = targets[tid]["summary"]["landing_tick"]["mean"]
        return v if v is not None else float("inf")

    order = sorted(targets, key=mean_landing)
    y0s = [t["repeats"][min(t["repeats"])]["y0"] for t in targets.values() if t["repeats"][min(t["repeats"])]["y0"] is not None]
    height = (statistics.fmean(y0s) - ground_y) if y0s else None
    result = {
        "experiment": exp["id"],
        "mc_version": meta.get("mc_version") or exp.get("mc_version"),
        "constants_confidence": mc.load_constants().get("confidence"),
        "ground_y": ground_y,
        "drop_height_blocks": height,
        "real_vacuum_fall_time_s": real.fall_time_vacuum(height) if height else None,
        "landing_order": [{"target": t, "label": targets[t]["label"],
                           "landing_tick": targets[t]["summary"]["landing_tick"]["mean"]} for t in order],
        "targets": targets,
    }
    (run_dir / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_theory_csv(run_dir, result, ground_y)
    (run_dir / "summary.md").write_text(summary_markdown(result), encoding="utf-8")
    return result


def write_theory_csv(run_dir: Path, result: dict, ground_y: float) -> None:
    """動画のグラフ用: 当てはめた MC モデルと、現実（真空）の理論曲線。"""
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


def summary_markdown(r: dict) -> str:
    L = [f"# {r['experiment']} 計測結果", "",
         f"- MCバージョン: {r['mc_version']}",
         f"- 落下の高さ: {r['drop_height_blocks']:.1f} ブロック" if r["drop_height_blocks"] else "- 落下の高さ: 不明",
         f"- 予想値の確度: {r['constants_confidence']}（knowledge/mechanics/重力と空気抵抗.md）", "",
         "## 着地の順番", ""]
    for i, o in enumerate(r["landing_order"], 1):
        lt = o["landing_tick"]
        L.append(f"{i}. {o['label']}: {lt:.1f} tick（{lt / TPS:.2f} 秒）" if lt is not None else f"{i}. {o['label']}: 着地せず")
    if r["real_vacuum_fall_time_s"]:
        L.append(f"\n参考: 現実の真空中なら、どれも {r['real_vacuum_fall_time_s']:.2f} 秒で同時に着地する。")
    L += ["", "## 当てはめた値", "",
          "| 対象 | 種類 | g（ブロック/tick²） | g（m/s²） | 地球の何倍 | 空気抵抗 d | 順序 | 終端速度（m/s） | 予想との比較 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in r["targets"].values():
        f = t["repeats"][min(t["repeats"])].get("fit")
        if not f:
            L.append(f"| {t['label']} | {t['type']} | – | – | – | – | – | – | 当てはめ不可 |")
            continue
        L.append(f"| {t['label']} | {t['type']} | {f['g_block_per_tick2']:.4f} | {f['g_ms2']:.2f} | {f['g_ratio_earth']:.2f} | "
                 f"{f['d']:.4f} | {f['order']} | {f['terminal_ms']:.1f} | {t['vs_expected']['status']} |")
    L += ["", "## 注意", "",
          "- 繰り返しの間で値がばらついていないかは results.json の `summary` を見る。",
          "- 位置の残差（rms_position）が両方の順序で大きいときは、モデルの式そのものが合っていない。",
          "- この表の値を【実測】として knowledge に書く前に、MCのバージョンを確認する。"]
    return "\n".join(L) + "\n"
