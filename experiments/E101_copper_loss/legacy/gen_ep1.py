"""第1話「速くするほど、銅線は近くしか届かない」のデータパックを生成する。

物理モデル（すべて画面と概要欄に出典を出す前提）:
- 銅配線の損失 α = FOM × f_N [dB/インチ]
    FOM = 0.1 dB/インチ/GHz（低損失基板の経験則, Bogatin, EDN Rule of Thumb #9）
    f_N = ナイキスト周波数（データの最も速い繰り返しの基本周波数）
    注意: 実際は導体損(√fに比例)と誘電損(fに比例)の和で、厳密にはfに比例しない
- 受信限界 = IEEE 802.3 のチャネル挿入損失の上限（コネクタ等を含む全体の値）
- 光ファイバーの損失 = 0.33 dB/km（G.652.D, 1310 nm の典型値）
- 1ブロック = 1インチ（2.54 cm）
- 信号の進む速さは全レーン同じ（演出で差をつけない）

使い方: python gen_ep1.py  （ワールドのデータパックを上書き生成する）
"""
import math
import os
import shutil

WORLD = os.path.join(os.environ["APPDATA"], ".minecraft", "saves", "physics-lab")
PACK = os.path.join(WORLD, "datapacks", "photon_lab")
FN = os.path.join(PACK, "data", "photon", "function")
EP1 = os.path.join(FN, "ep1")

LENGTH = 60  # ブロック = インチ
FOM = 0.1  # dB / inch / GHz
FIBER_DB_PER_KM = 0.33
INCH_M = 0.0254

LANES = [
    dict(key="g1", name="1 Gbps 銅線", z=0, kind="cu", fN=0.5, budget=None,
         std="参考: 低速な信号"),
    dict(key="g25", name="25 Gbps 銅線", z=4, kind="cu", fN=12.89, budget=35.0,
         std="IEEE 802.3bj (100GBASE-KR4)"),
    dict(key="g100", name="100 Gbps 銅線", z=8, kind="cu", fN=26.5625, budget=28.0,
         std="IEEE 802.3ck (100GBASE-KR1)"),
    dict(key="opt", name="100 Gbps 光ファイバー", z=12, kind="opt"),
]

IDENT = "left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f]"


def alpha(lane):
    """1インチあたりの損失 [dB]"""
    if lane["kind"] == "cu":
        return FOM * lane["fN"]
    return FIBER_DB_PER_KM * INCH_M / 1000.0


def amp(db):
    """損失 dB から電圧振幅の比を出す"""
    return 10 ** (-db / 20.0)


def fmt_db(db, kind):
    if kind == "opt":
        return f"-{db:.4f} dB"
    return f"-{db:.1f} dB"


def fmt_amp(a):
    p = a * 100
    if p >= 99.99 and p < 100:
        return "振幅 99.99%"
    if p >= 10:
        return f"振幅 {p:.0f}%"
    if p >= 1:
        return f"振幅 {p:.1f}%"
    if p >= 0.01:
        return f"振幅 {p:.2f}%"
    return "振幅 1万分の1未満"


def text(s, color="white", bold=False):
    b = ",bold:true" if bold else ""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'{{text:"{s}",color:"{color}"{b}}}'


def display(x, y, z, s, color="white", bold=False, scale=1.0, width=200, tags=("ep1",)):
    tag_list = ",".join(f'"{t}"' for t in tags)
    tr = ""
    if scale != 1.0:
        tr = f",transformation:{{{IDENT},scale:[{scale}f,{scale}f,{scale}f]}}"
    x, y, z = (round(v, 3) for v in (x, y, z))
    return (f"summon text_display ~{x:g} ~{y:g} ~{z:g} {{Tags:[{tag_list}],billboard:\"center\","
            f"line_width:{width},text:{text(s, color, bold)}{tr}}}")


def lane_block(lane, i):
    """i 番目のブロック（遠い側の端で i インチ）の色"""
    if lane["kind"] == "opt":
        return "light_blue_stained_glass"
    db = alpha(lane) * i
    budget = lane["budget"]
    if budget is not None and db > budget:
        return "gray_concrete"
    if db < 3:
        return "lime_concrete"
    if db < 10:
        return "yellow_concrete"
    if db < 20:
        return "orange_concrete"
    return "red_concrete"


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def build_at():
    L = ["# 生成ファイル（gen_ep1.py）。基準マーカーの位置で実行される",
         "fill ~-14 ~ ~-8 ~70 ~10 ~18 air",
         "fill ~-14 ~-1 ~-8 ~70 ~-1 ~18 smooth_quartz"]
    for lane in LANES:
        z = lane["z"]
        L.append(f"# --- {lane['name']} ---")
        for i in range(1, LENGTH + 1):
            L.append(f"setblock ~{i} ~ ~{z} {lane_block(lane, i)}")
        if lane["kind"] == "cu":
            L.append(f"setblock ~0 ~ ~{z} iron_block")
            L.append(f"setblock ~{LENGTH + 1} ~ ~{z} iron_block")
        else:
            L.append(f"setblock ~0 ~ ~{z} sea_lantern")
            L.append(f"setblock ~{LENGTH + 1} ~ ~{z} daylight_detector")
        if lane.get("budget"):
            reach = lane["budget"] / alpha(lane)
            x = math.floor(reach) + 1  # 損失が上限を超える最初のブロック
            L.append(f"setblock ~{x} ~1 ~{z} red_stained_glass")
            L.append(f"setblock ~{x} ~2 ~{z} red_stained_glass")
    write(os.path.join(EP1, "build_at.mcfunction"), L + [
        "function photon:ep1/labels",
        "scoreboard players set #psend ep1 0",
        "tp @p ~30 ~16 ~-26 facing ~30 ~ ~6",
        'tellraw @p [{text:"[photon_lab] 第1話のセット完成。",color:"aqua"},'
        '{text:"/function photon:ep1/send",color:"yellow"},'
        '{text:" で全レーンに同時に信号を送ります",color:"aqua"}]',
    ])


def labels():
    L = ["# 生成ファイル（gen_ep1.py）。看板と数値表示"]
    # タイトルと前提条件
    L.append(display(30, 9, 18, "速くするほど、銅線は近くしか届かない", bold=True, scale=3.5, width=400))
    notes = [
        "1ブロック = 1インチ（2.54 cm）。信号の進む速さは全レーン同じにしています",
        "銅線の損失: 0.1 dB/インチ/GHz（低損失基板の経験則、Bogatin）× ナイキスト周波数",
        "受信限界: IEEE 802.3 のチャネル損失の上限。コネクタ等も含む全体の値なので、実際に配線へ使える距離はもっと短い",
        "光ファイバーの損失: 0.33 dB/km（G.652.D、波長1310 nm の典型値）",
    ]
    for k, s in enumerate(notes):
        L.append(display(30, 7.2 - 0.6 * k, 18, s, color="#DDDDDD", scale=1.3, width=600))

    for lane in LANES:
        z = lane["z"] + 0.5
        a = alpha(lane)
        if lane["kind"] == "cu":
            L.append(display(-7, 1.9, z, lane["name"], color="#FF9A3C", bold=True, scale=1.5))
            L.append(display(-7, 1.2, z, f"ナイキスト {lane['fN']:g} GHz → {a:.2f} dB/インチ", width=300))
            if lane["budget"]:
                reach = lane["budget"] / a
                L.append(display(-7, 0.6, z, f"受信限界 {lane['budget']:g} dB（{lane['std']}）", color="#FFB0B0", width=300))
                x = math.floor(reach) + 1
                L.append(display(x + 0.5, 3.0, z, f"ここで受信限界 {lane['budget']:g} dB", color="#FF5050", bold=True, width=300))
                L.append(display(x + 0.5, 2.6, z, f"届くのは約 {reach:.0f} インチ（{reach * 2.54:.0f} cm）まで", color="#FF8080", width=300))
            else:
                L.append(display(-7, 0.6, z, lane["std"], color="#BBBBBB", width=300))
            for i in range(5, LENGTH + 1, 5):
                db = a * i
                over = lane["budget"] is not None and db > lane["budget"]
                c = "#888888" if over else "white"
                L.append(display(i + 0.5, 1.6, z, fmt_db(db, "cu"), color=c))
                L.append(display(i + 0.5, 1.2, z, fmt_amp(amp(db)), color=c))
        else:
            L.append(display(-7, 1.9, z, lane["name"], color="#5AC8FA", bold=True, scale=1.5))
            L.append(display(-7, 1.2, z, f"損失 {FIBER_DB_PER_KM} dB/km。データを速くしても損失はほぼ同じ", width=300))
            L.append(display(-7, 0.6, z, "ただし両端で電気⇔光の変換が必要（電力を使う）", color="#FFE14D", width=300))
            L.append(display(0.5, 1.8, z, "電気→光", color="#FFE14D", bold=True))
            L.append(display(LENGTH + 1.5, 1.8, z, "光→電気", color="#FFE14D", bold=True))
            for i in range(20, LENGTH + 1, 20):
                db = a * i
                L.append(display(i + 0.5, 1.6, z, fmt_db(db, "opt")))
                L.append(display(i + 0.5, 1.2, z, fmt_amp(amp(db))))
    write(os.path.join(EP1, "labels.mcfunction"), L)


def pulse_frames():
    """x = 1..LENGTH+1 の各位置で、全レーンの信号を粒子で描く"""
    for x in range(1, LENGTH + 2):
        L = [f"# 生成ファイル。信号が {x} インチ地点にあるときの描画"]
        for lane in LANES:
            z = lane["z"] + 0.5
            if x == LENGTH + 1:
                continue
            db = alpha(lane) * x
            a = amp(db)
            if lane["kind"] == "opt":
                L.append(f"particle dust{{color:[0.35,0.8,1.0],scale:1.5}} ~{x + 0.5} ~0.5 ~{z} 0.05 0.05 0.05 0 4 force")
                continue
            if a < 0.02:
                continue  # 小さすぎて見えない
            over = lane["budget"] is not None and db > lane["budget"]
            col = "[0.55,0.55,0.55]" if over else "[1.0,0.6,0.15]"
            s = max(0.15, 1.5 * a)
            L.append(f"particle dust{{color:{col},scale:{s:.2f}}} ~{x + 0.5} ~1.0 ~{z} 0.05 0.05 0.05 0 4 force")
        if x == LENGTH + 1:
            for lane in LANES:
                z = lane["z"] + 0.5
                db = alpha(lane) * LENGTH
                budget = lane.get("budget")
                ok = budget is None or db <= budget
                p = "happy_villager" if ok else "smoke"
                L.append(f"particle {p} ~{x + 0.5} ~1.2 ~{z} 0.3 0.3 0.3 0 15 force")
        write(os.path.join(EP1, "pulse", f"x{x}.mcfunction"), L)


def results():
    L = ["# 生成ファイル。60インチ先の受信結果",
         "scoreboard players set #psend ep1 0",
         'tellraw @a {text:"―― 60インチ（152 cm）先での結果 ――",color:"aqua"}']
    for lane in LANES:
        db = alpha(lane) * LENGTH
        if lane["kind"] == "opt":
            msg = f"{lane['name']}: {fmt_db(db, 'opt')} → 受信OK（ただし両端の変換に電力が必要）"
            L.append(f'tellraw @a {text(msg, "#5AC8FA")}')
            continue
        if lane["budget"] is None:
            msg = f"{lane['name']}: {fmt_db(db, 'cu')} → 損失は小さい"
            L.append(f'tellraw @a {text(msg, "#7CFC00")}')
        elif db <= lane["budget"]:
            msg = f"{lane['name']}: {fmt_db(db, 'cu')}（限界 {lane['budget']:g} dB）→ 受信OK"
            L.append(f'tellraw @a {text(msg, "#7CFC00")}')
        else:
            reach = lane["budget"] / alpha(lane)
            msg = (f"{lane['name']}: {fmt_db(db, 'cu')}（限界 {lane['budget']:g} dB）→ 受信不能。"
                   f"信号はゼロではないが、受信機が読めない。届くのは約 {reach:.0f} インチまで")
            L.append(f'tellraw @a {text(msg, "#FF6060")}')
    write(os.path.join(EP1, "pulse", "done.mcfunction"), L)


def static_files():
    write(os.path.join(PACK, "pack.mcmeta"), [
        "{", '  "pack": {', '    "description": "Photon Lab: 物理をマイクラで",',
        '    "max_format": 121,', '    "min_format": 121', "  }", "}"])
    write(os.path.join(PACK, "data", "minecraft", "tags", "function", "load.json"),
          ['{', '  "values": ["photon:load"]', '}'])
    write(os.path.join(PACK, "data", "minecraft", "tags", "function", "tick.json"),
          ['{', '  "values": ["photon:tick"]', '}'])
    write(os.path.join(FN, "load.mcfunction"), [
        "scoreboard objectives add ep1 dummy",
        "scoreboard players set #psend ep1 0",
        'tellraw @a [{text:"[photon_lab] 読み込み完了。",color:"aqua"},'
        '{text:"/function photon:ep1/build",color:"yellow"},{text:" で第1話のセットを作ります",color:"aqua"}]'])
    write(os.path.join(FN, "tick.mcfunction"), [
        "execute if score #psend ep1 matches 1 as @e[type=marker,tag=ep1_origin,limit=1] at @s run function photon:ep1/pulse/advance"])
    write(os.path.join(FN, "studio.mcfunction"), [
        "# 撮影用: 昼で固定・晴れ・モブなし（26.x のゲームルール名）",
        "time set noon", "weather clear",
        "gamerule advance_time false", "gamerule advance_weather false", "gamerule spawn_mobs false"])
    write(os.path.join(EP1, "build.mcfunction"), [
        "# 前回のセットがあれば同じ場所に建て直す。なければ足元に建てる",
        "execute unless entity @e[type=marker,tag=ep1_origin] align xyz run summon marker ~ ~ ~ {Tags:[\"ep1\",\"ep1_origin\"]}",
        "kill @e[tag=ep1,tag=!ep1_origin]",
        "execute as @e[type=marker,tag=ep1_origin,limit=1] at @s run function photon:ep1/build_at"])
    write(os.path.join(EP1, "build_here.mcfunction"), [
        "# 足元にセットを建て直す（前のセットのブロックは残る）",
        "kill @e[tag=ep1]",
        "execute align xyz run summon marker ~ ~ ~ {Tags:[\"ep1\",\"ep1_origin\"]}",
        "execute as @e[type=marker,tag=ep1_origin,limit=1] at @s run function photon:ep1/build_at"])
    write(os.path.join(EP1, "send.mcfunction"), [
        "# 全レーンに同時に信号を送る",
        "scoreboard players set #px ep1 0",
        "scoreboard players set #psend ep1 1"])
    write(os.path.join(EP1, "pulse", "advance.mcfunction"), [
        "scoreboard players add #px ep1 1",
        "execute store result storage photon:ep1 p.x int 1 run scoreboard players get #px ep1",
        "function photon:ep1/pulse/frame with storage photon:ep1 p",
        f"execute if score #px ep1 matches {LENGTH + 1}.. run function photon:ep1/pulse/done"])
    write(os.path.join(EP1, "pulse", "frame.mcfunction"), [
        "$function photon:ep1/pulse/x$(x)"])


def main():
    if os.path.isdir(EP1):
        shutil.rmtree(EP1)  # 以前の生成物（第1話のみ）を消して作り直す
    static_files()
    build_at()
    labels()
    pulse_frames()
    results()
    for lane in LANES:
        a = alpha(lane)
        line = f"{lane['name']}: {a:.6g} dB/inch, 60inch = {a * LENGTH:.4g} dB"
        if lane.get("budget"):
            line += f", reach = {lane['budget'] / a:.1f} inch"
        print(line)


if __name__ == "__main__":
    main()
