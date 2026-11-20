# knowledge — 知見の蓄積先

Minecraft 固有の知見（MC の物理の仕様、mod、MC の撮影技術、Mojang の規約、マイクラ動画の市場）を、**出典つきで**話題ごとに1ファイルにまとめたもの。
チャンネルを問わない動画制作の知見（YouTube のポリシー、企画、台本、音声、編集、投稿、分析）は
[movie の knowledge/](https://github.com/mitsuo822/movie/blob/main/knowledge/README.md) にある。

| ディレクトリ | 中身 |
|---|---|
| `mechanics/` | MCの物理の仕様（重力、空気抵抗、摩擦、爆発、流体、光、レッドストーン、音、tick…）。1つの現象につき1ファイル |
| `mods/` | 計測・物理の mod の機能、対応バージョン |
| `filming/` | MCの撮影技術（録画mod、カメラ、シェーダー、録画設定、ワールド内の演出、時間制御） |
| `rights/` | Mojang の利用ガイドライン、MC の音楽、mod・シェーダーの利用条件 |
| `market/` | マイクラ動画の市場、参考チャンネル、企画の型、既存の物理動画（ネタ被りの確認） |

- 調査日: 2026-11-19〜20（`mechanics/` と `filming/` の一部は既存の内容を更新）。mod の対応バージョンや規約はよく変わるので、使う前に各ファイルの「参照先」の原文を確かめる。
- `mechanics/` の値の多くは minecraft.wiki などによる【二次】。**動画で断言してよいのは【実測】か【一次】だけ**（`CLAUDE.md`）なので、実験で【実測】に上げてから使う。

## 工程ごとに読むファイル

| 工程 | 読むファイル |
|---|---|
| **P0 環境決め** | [バージョン対応表](mods/バージョン対応表.md)、[物理系mod](mods/物理系mod.md)、[mod・シェーダーの利用条件](rights/mod・シェーダーの利用条件.md)、[シェーダーと画質mod](filming/シェーダーと画質mod.md) |
| **① テーマ選定** | [既存のマイクラ物理動画](market/既存のマイクラ物理動画.md)、[科学・物理・検証系の参考チャンネル](market/科学・物理・検証系の参考チャンネル.md)、[伸びている企画パターン](market/伸びている企画パターン.md)、[日本のマイクラ動画ジャンル](market/日本のマイクラ動画ジャンル.md)、[視聴者層とマイクラ動画の規模](market/視聴者層とマイクラ動画の規模.md)、下の「テーマと物理のファイル」 |
| **② 実験設計・③ 計測** | `mechanics/` の該当ファイル、[Carpet](mods/Carpet.md)、[計測と可視化のmod](mods/計測と可視化のmod.md)、[時間とtick](mechanics/時間とtick.md)、[時間制御とスロー](filming/時間制御とスロー.md) |
| **⑤ 撮影** | [Flashback](filming/Flashback.md)、[ReplayMod](filming/ReplayMod.md)、[カメラワーク技法](filming/カメラワーク技法.md)、[縦型撮影](filming/縦型撮影.md)、[録画設定](filming/録画設定.md)、[シェーダーと画質mod](filming/シェーダーと画質mod.md)、[ワールド内の演出](filming/ワールド内の演出.md)、[時間制御とスロー](filming/時間制御とスロー.md) |
| **⑥ 編集・⑦ 投稿**（MC固有の権利） | [Mojang利用ガイドライン](rights/Mojang利用ガイドライン.md)、[マイクラ音楽の使用](rights/マイクラ音楽の使用.md)、[mod・シェーダーの利用条件](rights/mod・シェーダーの利用条件.md) |

工程の番号は [README の制作の流れ](../README.md) に合わせている。台本・編集・投稿の一般的な知見は movie 側を読む。

## テーマと物理のファイル

`themes/backlog.yaml` の候補ごとに、まず読む `mechanics/`・`mods/` のファイル。どのテーマも、先行例は [既存のマイクラ物理動画](market/既存のマイクラ物理動画.md) で確かめる。

| テーマ | ファイル |
|---|---|
| T01 重力 / T02 ガリレオ / T03 終端速度 | [重力と空気抵抗](mechanics/重力と空気抵抗.md) |
| T04 摩擦 | [摩擦と滑りやすさ](mechanics/摩擦と滑りやすさ.md) |
| T05 矢の最適角 | [投射物](mechanics/投射物.md) |
| T06 アルキメデスの原理 / T18 水が流れきるまで | [流体](mechanics/流体.md) |
| T07 TNTの爆風 / T15 TNTキャノン | [爆発](mechanics/爆発.md)、[投射物](mechanics/投射物.md) |
| T08 明るさと逆2乗 | [光](mechanics/光.md) |
| T09 音速 | [音と振動](mechanics/音と振動.md) |
| T10 レッドストーンの速さ | [レッドストーン信号](mechanics/レッドストーン信号.md)、[時間とtick](mechanics/時間とtick.md) |
| T11 ニュートンのゆりかご / T12 フーコーの振り子 / T14 Createの永久機関 | [物理系mod](mods/物理系mod.md) |
| T13 エラトステネス | [世界の形と大きさ](mechanics/世界の形と大きさ.md) |
| T16 砂の安息角 | [既存のマイクラ物理動画](market/既存のマイクラ物理動画.md)（T16 の節） |
| T17 現実の重力にしたら | [重力と空気抵抗](mechanics/重力と空気抵抗.md)、[物理系mod](mods/物理系mod.md) |

## 書き方

確度（【実測】/【一次】/【二次】/【未確認】）の意味は `CLAUDE.md` を参照。**MC に関係する事実には mc_version を付ける**（Java版と統合版を区別する）。

ファイルの形、「」の使い方（原文そのままの引用だけ）、検証の手順は movie の [knowledge/README.md](https://github.com/mitsuo822/movie/blob/main/knowledge/README.md) と同じ。照合・検査の道具は movie の [tools/knowledge/](https://github.com/mitsuo822/movie/blob/main/tools/knowledge/README.md) にある。

```markdown
# <題名>

> 対象: <範囲> ／ 使う場面: <工程> ／ 調査日: YYYY-MM-DD ／ mc_version: <前提とするバージョン>

## 要点
- <結論の一文>（mc_version）【二次】[S1]

## 詳細 … ／ ## このチャンネルでの使い方（提案） … ／ ## わかっていないこと・要確認 … ／ ## 参照先 …
```

実験で確かめたことは、該当ファイルの事実を【実測】に上げ、根拠に実験ID（例: E001）を書く。【未確認】や【二次】の項目は、実験で【実測】に上げるのが基本の流れ。

## 一覧

`python3 -I ../movie/tools/knowledge/make_index.py knowledge`（movie を隣に置いた場合）で、各ファイル冒頭の「対象」から作り直せる。

<!-- BEGIN:index -->

### `filming/`（8）

| ファイル | 対象 |
|---|---|
| [Flashback](filming/Flashback.md) | Flashback（作者 Moulberry）の録画・エディタ・キーフレームの種類・書き出しの機能、シェーダーと Sodium への対応、対応バージョン、ライセンス、Replay… |
| [ReplayMod](filming/ReplayMod.md) | Replay Mod（ReplayMod）の録画・再生・カメラパス・レンダリングの機能、対応バージョン、Iris/Sodium との互換、ファイル、既知の制限、自動化に使える仕組み… |
| [カメラワーク技法](filming/カメラワーク技法.md) | Minecraft Java版を中心に、カメラを動かす技法（キーフレームのカメラパス、周回、ロール、FOV、補間、エンティティの追従）と、それを実現する道具（Replay Mod… |
| [シェーダーと画質mod](filming/シェーダーと画質mod.md) | Java版の画質を上げる mod（Sodium、Iris、Distant Horizons）と、動画でよく使われるシェーダーパック（Complementary Reimagined… |
| [ワールド内の演出](filming/ワールド内の演出.md) | 撮影する映像の中に、文字・目印・軌跡・数値を出すバニラの仕組み。 |
| [時間制御とスロー](filming/時間制御とスロー.md) | ゲームの時間の進み方を変える方法。 |
| [縦型撮影](filming/縦型撮影.md) | ショート用の 9:16（と 1:1）の映像を Minecraft Java版から作る方法。 |
| [録画設定](filming/録画設定.md) | Java版を録画するときのゲーム内の設定（HUD の非表示、FOV、画面の揺れ、GUI の大きさ、描画距離、シネマティックカメラ、fps の上限）と、OBS Studio の録画設… |

### `market/`（5）

| ファイル | 対象 |
|---|---|
| [伸びている企画パターン](market/伸びている企画パターン.md) | マイクラ動画で再生される企画の型（迷信・都市伝説の検証、『Minecraft, But』、100日、リアル物理mod、物理シミュレーション、数の多い実験・まとめ、比較・最速、謎の分… |
| [既存のマイクラ物理動画](market/既存のマイクラ物理動画.md) | `themes/backlog.yaml` のテーマ T01〜T18 と同じ題材を扱った既存の YouTube 動画（日本語・英語）。 |
| [日本のマイクラ動画ジャンル](market/日本のマイクラ動画ジャンル.md) | 日本語のMinecraft動画が、ニコニコ動画の時代からYouTubeの時代までどう広がってきたかと、いま見られているジャンル（グループ実況、茶番・アニメ、検証・小ネタ、建築、統合… |
| [科学・物理・検証系の参考チャンネル](market/科学・物理・検証系の参考チャンネル.md) | マイクラ×科学・物理・数学・検証・テクニカルの参考チャンネル（日本語・英語）と、マイクラ以外の科学・数学チャンネルがマイクラを扱った回。 |
| [視聴者層とマイクラ動画の規模](market/視聴者層とマイクラ動画の規模.md) | YouTube 上の Minecraft 動画の規模（公式の再生回数の節目・年間の数値）、Minecraft の販売本数・月間プレイヤー数、日本の市場の数値、プレイヤー・視聴者の年… |

### `mechanics/`（10）

| ファイル | 対象 |
|---|---|
| [レッドストーン信号](mechanics/レッドストーン信号.md) | レッドストーン信号の時間と強さ。 |
| [世界の形と大きさ](mechanics/世界の形と大きさ.md) | ワールドの縦の範囲（建築の上限・下限、奈落）、横の端（ワールドボーダー、3,000万ブロックの境界、ファーランド）、太陽・月の動き（場所で変わるか）、スーパーフラットの既定の層と高… |
| [光](mechanics/光.md) | MC の光の仕組み。 |
| [投射物](mechanics/投射物.md) | 矢（弓・クロスボウ・ディスペンサー）、トライデント、雪玉・卵・エンダーパール、ポーション・経験値瓶、花火ロケットの、初速・ばらつき・クリティカル・軌道の計算・水中での振る舞い。 |
| [摩擦と滑りやすさ](mechanics/摩擦と滑りやすさ.md) | ブロックの滑りやすさ（slipperiness / friction）の値と、それが地上の移動の計算でどう使われるか。 |
| [時間とtick](mechanics/時間とtick.md) | MC の時間の単位。 |
| [流体](mechanics/流体.md) | 水と溶岩が広がる速さ（tick 数）と距離、流れの向きの決まり方、水流・溶岩流がエンティティを押す速さ、水中・溶岩中での浮き沈みと減速、気泡の柱、水源の増え方。 |
| [爆発](mechanics/爆発.md) | 爆発がブロックを壊す仕組み（光線・威力・爆発耐性）、エンティティに与える速度とダメージの式、露出度、TNT の導火線と着火時の初速、TNT キャノンの原理。 |
| [重力と空気抵抗](mechanics/重力と空気抵抗.md) | エンティティの種類ごとの重力加速度・空気抵抗・1tickの中での処理の順序・終端速度と、それを変える属性（gravity など）。 |
| [音と振動](mechanics/音と振動.md) | 音の届く範囲と距離による減衰、音が遅れて届く例（花火）、スカルクセンサーと調律されたスカルクセンサーが受け取る振動（伝わる速さ、範囲、強さ、周波数、遮り方）。 |

### `mods/`（4）

| ファイル | 対象 |
|---|---|
| [Carpet](mods/Carpet.md) | Carpet mod（gnembon/fabric-carpet）のうち、物理の計測・実験の再現・ワールド内の可視化に使える機能（/player、/log、/distance、/i… |
| [バージョン対応表](mods/バージョン対応表.md) | 2026-11-19 時点の最新の Java Edition と、計測・撮影の基盤に使う mod（Fabric API、Carpet、Flashback、Replay Mod、So… |
| [物理系mod](mods/物理系mod.md) | Minecraft の物理を扱う・変える mod（Create、Create Aeronautics と Sable、Valkyrien Skies 2、Physics Mod、重… |
| [計測と可視化のmod](mods/計測と可視化のmod.md) | 画面に座標・速度・明るさなどを出す道具（MiniHUD、バニラの F3 デバッグ画面とデバッグレンダラー）と、実験装置を作る・置き直す道具（Litematica、WorldEdit… |

### `rights/`（3）

| ファイル | 対象 |
|---|---|
| [Mojang利用ガイドライン](rights/Mojang利用ガイドライン.md) | Minecraft Usage Guidelines（利用ガイドライン）と Minecraft EULA のうち、YouTube 動画の制作・収益化・チャンネル名・タイトル・サムネ… |
| [mod・シェーダーの利用条件](rights/mod・シェーダーの利用条件.md) | 撮影・計測に使う予定の mod・シェーダーパックについて、ライセンスの種類と、動画・配信での利用、再配布（配布ワールド・modpack）、クレジットに関する条件を、各 mod の公… |
| [マイクラ音楽の使用](rights/マイクラ音楽の使用.md) | Minecraft の BGM（C418、Lena Raine ほか）・レコード（music disc）の曲・ゲーム内の音を YouTube 動画で使うときの、Mojang の公式… |
<!-- END:index -->
