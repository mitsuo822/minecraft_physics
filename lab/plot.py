"""解析用のグラフ（PNG）。動画用の動くグラフは movie 側の Remotion で theory.csv / measurements.csv から作る。

配色: 系列は固定順のカテゴリ色（dataviz の既定パレットの1〜3番。3色すべての組み合わせで
色覚の検査を通過済み）。3番目はコントラストが弱いので、線の端に名前を直接書く。
現実の理論線は系列色を使わず、無彩色の破線にする。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .analyze import TPS, load_rows  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE, INK, INK2, GRID, NEUTRAL = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#7a7975"
FONTS = ["Yu Gothic", "Meiryo", "Noto Sans CJK JP", "IPAGothic", "IPAexGothic", "DejaVu Sans"]


def _available_fonts() -> list[str]:
    from matplotlib import font_manager
    have = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in FONTS if f in have] or ["DejaVu Sans"]


def _style(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=13, pad=12)
    ax.set_xlabel(xlabel, color=INK2)
    ax.set_ylabel(ylabel, color=INK2)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2)


MARKERS = ["o", "s", "^"]   # 色に頼らない区別（重なった系列も見分けられるように）


def _place_labels(fig, ax, items: list[tuple[float, float, str, str]]) -> None:
    """線の端に名前を直接書く。同じ位置に来る系列は1つのラベルにまとめ、ぶつかるラベルは上にずらす。"""
    xr = ax.get_xlim()[1] - ax.get_xlim()[0]
    yr = ax.get_ylim()[1] - ax.get_ylim()[0]
    merged: list[list] = []
    for x, y, text, color in items:
        for m in merged:
            if abs(m[0] - x) < xr * 0.01 and abs(m[1] - y) < yr * 0.01:
                m[2] += "・" + text
                break
        else:
            merged.append([x, y, text, color])
    anns = []
    for x, y, text, color in merged:
        ax.plot([x], [y], marker="o", markersize=6, color=color, markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=4)
        anns.append(ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points", va="center",
                                color=INK, fontsize=10, annotation_clip=False))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    placed = []
    for ann in sorted(anns, key=lambda a: a.xy[1]):
        for _ in range(20):
            bb = ann.get_window_extent(renderer)
            if not any(bb.overlaps(p) for p in placed):
                break
            dx, dy = ann.xyann
            ann.xyann = (dx, dy + bb.height * 72 / fig.dpi + 2)
            fig.canvas.draw()
        placed.append(ann.get_window_extent(renderer))


def plot_run(run_dir: str | Path, repeat: int = 0) -> list[Path]:
    run_dir = Path(run_dir)
    plt.rcParams["font.family"] = _available_fonts()
    result = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    rows = [r for r in load_rows(run_dir) if r["repeat"] == repeat]
    with (run_dir / "theory.csv").open(encoding="utf-8") as f:
        theory = list(csv.DictReader(f))
    ground_y = result["ground_y"]
    outs = []

    # 1) 高さ - 時間
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150, facecolor=SURFACE)
    t_real = [float(r["t_sec"]) for r in theory]
    h_real = [float(r["real_vacuum_height"]) for r in theory]
    ax.plot(t_real, h_real, linestyle=(0, (5, 4)), linewidth=2, color=NEUTRAL, label="現実（真空）の予想")
    end_real = next((i for i, h in enumerate(h_real) if h <= 0), len(h_real) - 1)
    labels = [(t_real[end_real], h_real[end_real], "現実（真空）", NEUTRAL)]
    for i, (tid, t) in enumerate(result["targets"].items()):
        color = SERIES[i % len(SERIES)]
        mine = [r for r in rows if r["target"] == tid and r["exists"] and r["on_ground"] == 0]
        if not mine:
            continue
        ts = [r["tick"] / TPS for r in mine]
        hs = [r["y"] - ground_y for r in mine]
        col = f"mc_{tid}_height"
        if theory and col in theory[0]:
            mt = [(float(r["t_sec"]), float(r[col])) for r in theory if r[col] != ""]
            ax.plot([a for a, _ in mt], [b for _, b in mt], linewidth=1.2, color=color, alpha=0.6)
        ax.plot(ts, hs, linestyle="none", marker=MARKERS[i % 3], markersize=5, markevery=max(1, len(ts) // 25),
                color=color, markeredgecolor=SURFACE, markeredgewidth=0.8, label=f"{t['label']}（実測）")
        labels.append((ts[-1], hs[-1], t["label"], color))
    _style(ax, f"{result['experiment']}: 落下の高さ（実測の点とMCモデルの線）", "時間（秒）", "地面からの高さ（ブロック = m）")
    ax.set_ylim(bottom=0)
    ax.set_xlim(right=ax.get_xlim()[1] * 1.12)
    _place_labels(fig, ax, labels)
    ax.legend(frameon=False, labelcolor=INK, loc="upper right")
    fig.tight_layout()
    p = run_dir / "plot_height.png"
    fig.savefig(p, facecolor=SURFACE)
    plt.close(fig)
    outs.append(p)

    # 2) 落下の速さ - 時間
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150, facecolor=SURFACE)
    vmax = 0.0
    labels = []
    for i, (tid, t) in enumerate(result["targets"].items()):
        color = SERIES[i % len(SERIES)]
        mine = [r for r in rows if r["target"] == tid and r["exists"] and r["on_ground"] == 0]
        if not mine:
            continue
        ts = [r["tick"] / TPS for r in mine]
        vs = [-r["vy"] * TPS for r in mine]
        vmax = max(vmax, max(vs))
        ax.plot(ts, vs, linewidth=2, color=color, label=t["label"], marker=MARKERS[i % 3], markersize=5,
                markevery=max(1, len(ts) // 12), markeredgecolor=SURFACE, markeredgewidth=0.8)
        labels.append((ts[-1], vs[-1], f"{t['label']} {vs[-1]:.1f} m/s", color))
        term = t["summary"]["terminal_ms"]["mean"]
        if term:
            ax.axhline(term, color=color, linewidth=1, linestyle=(0, (2, 3)), alpha=0.7)
    t_end = max(float(r["t_sec"]) for r in theory)
    ax.plot([0, t_end], [0, 9.80665 * t_end], linestyle=(0, (5, 4)), linewidth=2, color=NEUTRAL, label="現実（真空）")
    _style(ax, f"{result['experiment']}: 落下の速さ（点線は当てはめた終端速度）", "時間（秒）", "下向きの速さ（m/s）")
    ax.set_ylim(0, vmax * 1.2 if vmax else 1)
    ax.set_xlim(right=ax.get_xlim()[1] * 1.2)
    _place_labels(fig, ax, labels)
    ax.legend(frameon=False, labelcolor=INK, loc="upper left")
    fig.tight_layout()
    p = run_dir / "plot_speed.png"
    fig.savefig(p, facecolor=SURFACE)
    plt.close(fig)
    outs.append(p)
    return outs
