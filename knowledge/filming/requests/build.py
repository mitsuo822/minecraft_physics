"""取得依頼のページを作る。

    python knowledge/filming/requests/build.py

requests.yaml（正本）と ../sources.yaml から、次の生成物を同じフォルダに書き出す。
  取得依頼.html          人が開くページ（ブラウザでそのまま開ける）
  urls_A.txt など        優先度ごとの動画URLの一覧（一括ダウンロード用）

--fragment <path> を付けると、<html> や <head> を持たない断片（Claude のアーティファクト用）も書き出す。
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TIER_ORDER = ["A", "B", "C"]
WANT_LABEL = {"subs": "字幕", "info": "概要欄", "video": "映像"}
TOOL_LABEL = {
    "flashback": "Flashback", "replaymod": "ReplayMod", "cmdcam": "CMDCam", "cinemalya": "Cinemalya",
    "vanilla": "バニラ（Java版）", "bedrock_camera": "統合版 /camera", "bedrock_addon": "統合版アドオン",
    "other_mod": "ほかのmod", "unknown": "道具は不明", "live_action": "実写",
}
LANG_LABEL = {"ja": "日本語", "en": "英語", "de": "ドイツ語"}


def e(text) -> str:
    return html.escape(str(text), quote=True)


def load():
    req = yaml.safe_load((HERE / "requests.yaml").read_text(encoding="utf-8"))
    src = yaml.safe_load((HERE.parent / "sources.yaml").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in src["sources"]}
    for v in req["videos"]:
        if v["source"] not in by_id:
            raise SystemExit(f"sources.yaml にない動画: {v['source']}")
    listed = {v["source"] for v in req["videos"]}
    missing = [s["id"] for s in src["sources"] if s["kind"] == "youtube" and s["id"] not in listed]
    if missing:
        raise SystemExit(f"requests.yaml に載っていない動画: {missing}")
    return req, by_id


def chips(resolves) -> str:
    if not resolves:
        return ""
    return '<span class="refs">解決したい項目: ' + " ".join(f"<code>{e(r)}</code>" for r in resolves) + "</span>"


def tier_badge(tier: str) -> str:
    return f'<span class="tier tier-{e(tier.lower())}" title="優先度 {e(tier)}">{e(tier)}</span>'


def item(item_id: str, tier: str, title_html: str, meta_html: str, body_html: str) -> str:
    cid = "chk-" + item_id
    return (
        f'<li class="item" data-id="{e(item_id)}">'
        f'<input type="checkbox" id="{e(cid)}" class="done" aria-label="保存した">'
        f"{tier_badge(tier)}"
        f'<div class="item-body"><div class="item-title">{title_html}</div>'
        f'<div class="item-meta">{meta_html}</div>{body_html}</div></li>'
    )


def video_item(v, by_id, tiers) -> str:
    s = by_id[v["source"]]
    vid = s["id"][3:]
    want = " ".join(f'<span class="want">{e(WANT_LABEL[w])}</span>' for w in tiers[v["tier"]]["want"])
    read = "概要欄は確認済み" if s.get("read") == "page" else "題名だけ確認済み"
    meta = " ・ ".join(
        x for x in [
            e(s.get("channel", "")), e(TOOL_LABEL.get(s.get("tool"), s.get("tool", ""))),
            e(LANG_LABEL.get(s.get("lang"), s.get("lang", ""))), e(s.get("published", "")), read,
        ] if x
    )
    body = f'<div class="wants">欲しいもの: {want}</div>'
    look = v.get("look_for") or s.get("topic")
    if look:
        label = "知りたいこと" if v.get("look_for") else "主題"
        body += f'<p class="look"><span class="k">{label}</span>{e(look)}</p>'
    body += f'<div class="foot"><code class="path">youtube/{e(vid)}/</code>{chips(v.get("resolves"))}</div>'
    title = f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])}</a>'
    return item(s["id"], v["tier"], title, meta, body)


def generic_item(x, kind_label: str) -> str:
    title = e(x["title"])
    if x.get("url"):
        title = f'<a href="{e(x["url"])}" target="_blank" rel="noopener">{title}</a>'
    meta = kind_label
    body = ""
    for key, label in [("hint", "探し方"), ("want", "欲しいもの"), ("how", "保存のしかた"), ("look_for", "知りたいこと")]:
        if x.get(key):
            body += f'<p class="look"><span class="k">{label}</span>{e(x[key])}</p>'
    foot = ""
    if x.get("save_as"):
        foot += f'<code class="path">{e(x["save_as"])}</code>'
    foot += chips(x.get("resolves"))
    if foot:
        body += f'<div class="foot">{foot}</div>'
    return item(x["id"], x["tier"], title, meta, body)


def section(sec_id: str, heading: str, lede: str, inner: str) -> str:
    return (
        f'<section id="{e(sec_id)}" class="sec"><div class="sec-head"><h2>{e(heading)}</h2>'
        f'<span class="count" data-count-for="{e(sec_id)}"></span></div>'
        f'<p class="lede">{lede}</p>{inner}</section>'
    )


def build(req, by_id):
    tiers = req["meta"]["tiers"]
    root = req["meta"]["save_root"]
    vids = {t: [v for v in req["videos"] if v["tier"] == t] for t in TIER_ORDER}
    urls = {t: [by_id[v["source"]]["url"] for v in vids[t]] for t in TIER_ORDER}

    # --- 動画 ---
    video_html = ""
    for t in TIER_ORDER:
        want = "・".join(WANT_LABEL[w] for w in tiers[t]["want"])
        rows = "".join(video_item(v, by_id, tiers) for v in vids[t])
        url_box = (
            f'<details class="urls"><summary>優先度{t}のURLをまとめて取り出す（{len(urls[t])}本）</summary>'
            f'<div class="urls-row"><button type="button" class="copy" data-copy="urls-{t}">コピー</button>'
            f'<span class="copied" data-copied-for="urls-{t}" hidden>コピーしました</span>'
            f'<span class="note">同じ内容が <code>urls_{t}.txt</code> にもあります</span></div>'
            f'<textarea id="urls-{t}" readonly rows="6" spellcheck="false">{e(chr(10).join(urls[t]))}</textarea></details>'
        )
        block = (
            f'<div class="tier-block" id="videos-{t}"><h3>{tier_badge(t)} {e(tiers[t]["label"])}'
            f'<span class="h3-note">{len(vids[t])}本 ・ 欲しいもの: {e(want)}</span></h3>{url_box}<ul class="items">{rows}</ul></div>'
        )
        if t == "C":
            block = f'<details class="fold"><summary>優先度C（{len(vids[t])}本）を開く</summary>{block}</details>'
        video_html += block

    def listing(key, kind_label):
        xs = sorted(req[key], key=lambda x: TIER_ORDER.index(x["tier"]))
        return '<ul class="items">' + "".join(generic_item(x, kind_label) for x in xs) + "</ul>"

    n_video = len(req["videos"])
    n_other = sum(len(req[k]) for k in ["find_videos", "web", "source_code", "in_game", "notes"])
    tree = (
        f"{root}/\n"
        "  youtube/<動画ID>/      <動画ID>.info.json  <動画ID>.ja.vtt  <動画ID>.mp4\n"
        "  web/                  MC-184359.pdf  flashback_discord.md ...\n"
        "  src/                  Flashback/  Cinemalya/ ...（git clone）\n"
        "  flashback_ui/         versions.txt  01_keyframe_types.png ...\n"
        "  flashback_files/      リプレイの保存フォルダの中身\n"
        "  notes/                examples.md"
    )
    out = f'{root}/youtube/%(id)s/%(id)s.%(ext)s'
    cmd_all = (
        "yt-dlp -a knowledge/filming/requests/urls_B.txt --skip-download --write-info-json "
        f'--write-subs --write-auto-subs --sub-langs "ja,en" --sub-format vtt -o "{out}"'
    )
    cmd_a = (
        'yt-dlp -a knowledge/filming/requests/urls_A.txt -f "bv*[height<=720]+ba/b[height<=720]" '
        "--merge-output-format mp4 --write-info-json --write-subs --write-auto-subs "
        f'--sub-langs "ja,en" --sub-format vtt -o "{out}"'
    )

    head = (
        "<title>カメラワーク取得依頼</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        f"<style>{CSS}</style>\n"
    )
    body = f"""
<div class="page">
<header class="top">
  <p class="eyebrow">minecraft_physics / knowledge / filming / requests</p>
  <h1>カメラワーク調査の取得依頼</h1>
  <p class="intro">2026-11-19 の調査で、AIの側からは読めなかった資料の一覧です。手元のPCで保存してもらえれば、あとでAIが読んで <code>knowledge/filming/</code> の知見を更新します。動画は字幕と概要欄があれば中身を読めます。映像まで欲しいのは優先度Aの{len(vids['A'])}本だけです。</p>
  <dl class="stats">
    <div><dt>動画</dt><dd>{n_video}<small>本</small></dd><dd class="sub">A {len(vids['A'])} ・ B {len(vids['B'])} ・ C {len(vids['C'])}</dd></div>
    <div><dt>動画以外</dt><dd>{n_other}<small>件</small></dd><dd class="sub">Web・ソース・画面・メモ</dd></div>
    <div><dt>保存済みの印</dt><dd><span id="done-total">0</span><small> / {n_video + n_other}</small></dd><dd class="sub">このブラウザに記憶します</dd></div>
  </dl>
  <nav class="toc" aria-label="目次">
    <a href="#rules">保存の決まり</a><a href="#videos">動画</a><a href="#find">探してほしい動画</a>
    <a href="#web">Webページ</a><a href="#src">ソースコード</a><a href="#ingame">実機の画面</a><a href="#notes">あなたのメモ</a><a href="#after">保存したら</a>
  </nav>
</header>

<section id="rules" class="sec">
  <div class="sec-head"><h2>保存の決まり</h2></div>
  <p class="lede">保存先は、リポジトリ直下の <code>{e(root)}/</code> です。<code>media/</code> は git の管理外なので、ここに置いたものはリポジトリに入りません。</p>
  <pre class="tree">{e(tree)}</pre>
  <div class="cols">
    <div>
      <h3 class="plain">動画1本につき欲しいもの</h3>
      <ul class="plainlist">
        <li><b>字幕</b>（.vtt か .srt）。その動画の元の言語の字幕で足ります。手動の字幕がなければ自動生成のものを。</li>
        <li><b>概要欄</b>とチャプター。<code>info.json</code> でも、テキストに貼ったものでも構いません。</li>
        <li><b>映像</b>（優先度Aだけ）。720pで足ります。AIは動画を再生できないので、あとで数秒おきの静止画を切り出して、カメラの動きを見ます。</li>
      </ul>
    </div>
    <div>
      <h3 class="plain">優先度</h3>
      <ul class="plainlist tiers">
        <li>{tier_badge('A')} 字幕・概要欄・映像。カメラの動きや設定画面を目で確かめたいもの。</li>
        <li>{tier_badge('B')} 字幕・概要欄。話の内容がわかれば足りるもの。</li>
        <li>{tier_badge('C')} 余裕があれば字幕・概要欄。統合版の話や、入門の重複。</li>
      </ul>
    </div>
  </div>
  <details class="fold">
    <summary>yt-dlp を使う場合の例</summary>
    <p class="small">リポジトリの直下で実行します。Bの行は字幕と概要欄だけを取ります（<code>urls_B.txt</code> を <code>urls_A.txt</code> や <code>urls_C.txt</code> に変えれば同じ形で使えます）。Aの行は映像も取ります。字幕がうまく取れない動画は、元の言語だけで十分です。</p>
    <p class="label">字幕と概要欄だけ</p>
    <pre class="cmd">{e(cmd_all)}</pre>
    <p class="label">映像も（優先度A）</p>
    <pre class="cmd">{e(cmd_a)}</pre>
  </details>
  <p class="caution">保存した動画と字幕は、手元で調べるためだけに使います。リポジトリに入れない、ほかの人に配らない、映像や音声を自分たちの動画に使わない、の3つを守ります。</p>
</section>

{section('videos', '動画', f'題名を確認できた{n_video}本です。左のチェックは「保存した」の印です。<span class="nojs">知りたいこと</span>は、AIがその動画を読むときに探す内容です。', video_html)}
{section('find', '探してほしい動画', 'AIの側では特定できなかったものです。いちばん上の「作例」は、あなたの目で選んでもらうことに意味があります。', listing('find_videos', '探してほしい動画'))}
{section('web', 'Webページ', 'クラウドのセッションからは開けなかったページです。PDFかテキストで保存してください。', listing('web', 'Webページ'))}
{section('src', 'ソースコード', 'modの公式の説明には操作の細部が書かれていません。ソースを読めば、カメラの経路をファイルで与えられるかがわかります。', listing('source_code', 'ソースコード'))}
{section('ingame', '実機の画面とファイル', 'MCとFlashbackを入れた後で、スクリーンショットを撮ってください。画面の項目名がわかれば、推測で書いた部分を確かな記述に置き換えられます。', listing('in_game', '実機'))}
{section('notes', 'あなたのメモ', '動画を見て気づいたことは、字幕からは拾えません。短いメモで十分です。', listing('notes', 'メモ'))}

<section id="after" class="sec">
  <div class="sec-head"><h2>保存したら</h2></div>
  <ol class="steps">
    <li>ファイルを <code>{e(root)}/</code> の決まった場所に置きます。全部そろっていなくて構いません。</li>
    <li>そのPCで Claude Code を開き、こう頼みます。<br><span class="say">「knowledge/filming/requests/requests.yaml の依頼分を {e(root)}/ に保存した。読んで knowledge/filming を更新して」</span></li>
    <li>AIは、読んだ項目の <code>status</code> を <code>used</code> に変え、知見の確度（未確認 → 二次や一次）を上げます。</li>
  </ol>
  <p class="small">クラウドのセッションからは <code>media/</code> が見えません（git の管理外のため）。読ませるには、保存したPCで実行するか、そのフォルダをセッションにつなぎます。</p>
  <p class="small">このページは <code>requests.yaml</code> から作った生成物です。依頼を足す・直すときは <code>requests.yaml</code> を編集して、<code>python knowledge/filming/requests/build.py</code> を実行します。</p>
</section>
</div>
<script>{JS}</script>
"""
    return head, body, urls


CSS = """
/* layout: 1カラムの作業リスト。各行は「チェック / 優先度の札 / 本文」の3列。狭い幅では本文だけが折り返す */
:root{
  --bg:#f5f7f4; --surface:#ffffff; --fg:#1c2420; --muted:#5a6861; --line:#d7ded8;
  --accent:#1c6b58; --accent-soft:#e1efe9; --code-bg:#ebefe9;
  --tier-a:#b0431a; --tier-b:#1c6b58; --tier-c:#6a7670; --warn-bg:#fbf1dc; --warn-fg:#6b4a08;
  --font-body:"Hiragino Sans","Yu Gothic UI","Yu Gothic",Meiryo,"Noto Sans JP",system-ui,sans-serif;
  --font-mono:ui-monospace,"Cascadia Mono",Consolas,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#131816; --surface:#1a201d; --fg:#e5ebe7; --muted:#98a69e; --line:#2b3530;
  --accent:#6ac5ab; --accent-soft:#1d312a; --code-bg:#212a25;
  --tier-a:#f0895c; --tier-b:#6ac5ab; --tier-c:#8c9992; --warn-bg:#33290f; --warn-fg:#f0d28a; color-scheme:dark } }
:root[data-theme="dark"]{
  --bg:#131816; --surface:#1a201d; --fg:#e5ebe7; --muted:#98a69e; --line:#2b3530;
  --accent:#6ac5ab; --accent-soft:#1d312a; --code-bg:#212a25;
  --tier-a:#f0895c; --tier-b:#6ac5ab; --tier-c:#8c9992; --warn-bg:#33290f; --warn-fg:#f0d28a; color-scheme:dark }
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font-body);font-size:15px;line-height:1.75;-webkit-text-size-adjust:100%}
.page{max-width:60rem;margin:0 auto;padding-block:2rem 4rem;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:2.5rem}
a{color:var(--accent);text-underline-offset:.18em}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
code{font-family:var(--font-mono);font-size:.9em;background:var(--code-bg);padding:.08em .35em;border-radius:4px;overflow-wrap:anywhere}
h1,h2,h3{margin:0;line-height:1.35;text-wrap:balance}
h1{font-size:1.75rem;font-weight:800;letter-spacing:.01em}
h2{font-size:1.25rem;font-weight:800}
h3{font-size:1rem;font-weight:700;display:flex;flex-wrap:wrap;align-items:center;gap:.5rem}
h3.plain{display:block;margin-bottom:.4rem}
p{margin:0}
.top{display:flex;flex-direction:column;gap:1rem}
.eyebrow{font-family:var(--font-mono);font-size:.78rem;color:var(--muted);letter-spacing:.02em;overflow-wrap:anywhere}
.intro{max-width:44em}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.75rem;margin:0}
.stats>div{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:.8rem 1rem;min-width:0}
.stats dt{font-size:.8rem;color:var(--muted)}
.stats dd{margin:0;font-size:1.7rem;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.3}
.stats dd small{font-size:.85rem;font-weight:600;color:var(--muted)}
.stats dd.sub{font-size:.8rem;font-weight:400;color:var(--muted)}
.toc{display:flex;flex-wrap:wrap;gap:.4rem .5rem}
.toc a{font-size:.85rem;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:.15rem .75rem;background:var(--surface);color:var(--fg)}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
.sec{display:flex;flex-direction:column;gap:.9rem;min-width:0}
.sec-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.75rem;border-bottom:2px solid var(--fg);padding-bottom:.35rem}
.count{font-size:.85rem;color:var(--muted);font-variant-numeric:tabular-nums}
.lede{color:var(--muted);max-width:46em}
.lede code{color:var(--fg)}
.tier-block{display:flex;flex-direction:column;gap:.6rem;min-width:0}
.h3-note{font-size:.82rem;font-weight:400;color:var(--muted)}
.items{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.item{display:grid;grid-template-columns:1.4rem 1.7rem minmax(0,1fr);gap:.2rem .7rem;align-items:start;padding:.8rem 0;border-top:1px solid var(--line)}
.item:first-child{border-top:0}
.done{width:1.15rem;height:1.15rem;margin:.32rem 0 0;accent-color:var(--accent)}
.tier{display:inline-grid;place-items:center;width:1.6rem;height:1.6rem;border-radius:5px;font-family:var(--font-mono);font-size:.85rem;font-weight:700;border:1.5px solid currentColor;line-height:1;flex:none}
.item>.tier{margin-top:.12rem}
.tier-a{color:var(--tier-a)} .tier-b{color:var(--tier-b)} .tier-c{color:var(--tier-c)}
.item-body{min-width:0;display:flex;flex-direction:column;gap:.3rem}
.item-title{font-weight:700;overflow-wrap:anywhere}
.item-meta{font-size:.82rem;color:var(--muted);overflow-wrap:anywhere}
.wants{font-size:.82rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:.3rem;align-items:center}
.want{border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:4px;padding:0 .45rem;font-size:.8rem}
.look{font-size:.92rem}
.k{display:inline-block;font-size:.72rem;font-weight:700;color:var(--accent);background:var(--accent-soft);border-radius:4px;padding:0 .4rem;margin-right:.5rem;vertical-align:.08em}
.foot{display:flex;flex-wrap:wrap;gap:.3rem .9rem;align-items:center;font-size:.8rem;color:var(--muted)}
.path{color:var(--fg)}
.refs code{margin-left:.15rem}
.item.is-done .item-title,.item.is-done .item-title a{color:var(--muted);text-decoration:line-through}
.item.is-done .look,.item.is-done .wants,.item.is-done .foot{opacity:.55}
details.fold,details.urls{border:1px solid var(--line);border-radius:8px;background:var(--surface);padding:.5rem .8rem;min-width:0}
details.fold>summary,details.urls>summary{cursor:pointer;font-weight:700;font-size:.9rem}
details.urls>summary{font-weight:600;font-size:.85rem;color:var(--muted)}
details[open]>summary{margin-bottom:.6rem}
details.fold>.tier-block{margin-top:.4rem}
.urls-row{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem;margin-bottom:.5rem;font-size:.82rem;color:var(--muted)}
button.copy{font:inherit;font-size:.85rem;font-weight:700;color:var(--surface);background:var(--accent);border:0;border-radius:6px;padding:.25rem .9rem;cursor:pointer}
.copied{color:var(--accent);font-weight:700}
textarea{width:100%;font-family:var(--font-mono);font-size:.78rem;line-height:1.5;color:var(--fg);background:var(--code-bg);border:1px solid var(--line);border-radius:6px;padding:.5rem;resize:vertical}
pre{margin:0;font-family:var(--font-mono);font-size:.8rem;line-height:1.6;background:var(--code-bg);border:1px solid var(--line);border-radius:8px;padding:.8rem 1rem;overflow-x:auto}
pre.cmd{white-space:pre-wrap;overflow-wrap:anywhere}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(17rem,1fr));gap:1.2rem 2rem}
.cols>div{min-width:0}
.plainlist{margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:.35rem}
.plainlist.tiers{list-style:none;padding-left:0}
.plainlist.tiers li{display:grid;grid-template-columns:1.7rem minmax(0,1fr);gap:.6rem;align-items:start}
.small{font-size:.85rem;color:var(--muted);max-width:48em}
.small code{color:var(--fg)}
.label{font-size:.8rem;font-weight:700;margin-top:.6rem;margin-bottom:.25rem}
.caution{background:var(--warn-bg);color:var(--warn-fg);border-radius:8px;padding:.7rem 1rem;font-size:.9rem}
.steps{margin:0;padding-left:1.4rem;display:flex;flex-direction:column;gap:.6rem;max-width:48em}
.say{display:inline-block;margin-top:.3rem;background:var(--accent-soft);border-radius:6px;padding:.3rem .7rem;font-size:.92rem;overflow-wrap:anywhere}
.nojs{font-weight:700;color:var(--fg)}
@media (max-width:30rem){ h1{font-size:1.45rem} .item{grid-template-columns:1.3rem 1.6rem minmax(0,1fr);gap:.2rem .5rem} }
"""

JS = """
(function(){
  var KEY='camera-requests:v1';
  var state={};
  try{ state=JSON.parse(localStorage.getItem(KEY)||'{}')||{}; }catch(err){ state={}; }
  function save(){ try{ localStorage.setItem(KEY,JSON.stringify(state)); }catch(err){} }
  function refresh(){
    var total=0;
    document.querySelectorAll('.sec').forEach(function(sec){
      var boxes=sec.querySelectorAll('.done'); if(!boxes.length) return;
      var n=0; boxes.forEach(function(b){ if(b.checked) n++; });
      total+=n;
      var c=sec.querySelector('.count'); if(c) c.textContent='保存済み '+n+' / '+boxes.length;
    });
    var t=document.getElementById('done-total'); if(t) t.textContent=total;
  }
  document.querySelectorAll('.item').forEach(function(li){
    var box=li.querySelector('.done'); if(!box) return;
    var id=li.getAttribute('data-id');
    if(state[id]){ box.checked=true; }
    li.classList.toggle('is-done',box.checked);
    box.addEventListener('change',function(){
      if(box.checked){ state[id]=1; } else { delete state[id]; }
      li.classList.toggle('is-done',box.checked); save(); refresh();
    });
  });
  document.querySelectorAll('button.copy').forEach(function(btn){
    btn.addEventListener('click',function(){
      var id=btn.getAttribute('data-copy'); var ta=document.getElementById(id); if(!ta) return;
      var note=document.querySelector('[data-copied-for="'+id+'"]');
      function ok(){ if(note){ note.hidden=false; setTimeout(function(){ note.hidden=true; },1800); } }
      function fallback(){ ta.focus(); ta.select(); }
      if(navigator.clipboard&&navigator.clipboard.writeText){
        navigator.clipboard.writeText(ta.value).then(ok,fallback);
      } else { fallback(); }
    });
  });
  refresh();
})();
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fragment", help="アーティファクト用の断片HTMLの出力先")
    args = ap.parse_args()
    req, by_id = load()
    head, body, urls = build(req, by_id)
    standalone = (
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head}</head>\n<body>{body}</body>\n</html>\n"
    )
    (HERE / "取得依頼.html").write_text(standalone, encoding="utf-8")
    for t, us in urls.items():
        (HERE / f"urls_{t}.txt").write_text("\n".join(us) + "\n", encoding="utf-8")
    if args.fragment:
        Path(args.fragment).write_text(head + body, encoding="utf-8")
    print("動画", {t: len(us) for t, us in urls.items()}, "→", HERE / "取得依頼.html")


if __name__ == "__main__":
    main()
