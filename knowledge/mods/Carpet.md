# Carpet mod（計測・再現・可視化に使う機能）

> 対象: Carpet mod（gnembon/fabric-carpet）のうち、物理の計測・実験の再現・ワールド内の可視化に使える機能（/player、/log、/distance、/info、/counter、ルール、Scarpet）と、対応バージョン・ライセンス。
> 使う場面: 実験の設計（`experiment.yaml` を書く前）、計測方式の選択、撮影前の準備、`mc/mods.yaml` を書くとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition（Modrinth の互換性欄は Java Edition だけ）。ソースコードは master ブランチ（26.4-snapshot-8 向け、取得日 2026-11-19）を読んだ。Modrinth の対応表は 1.14.4〜26.3。GitHub Wiki は更新日不明で、古いバージョンの説明が混じる（例: Carpet 独自の /tick）。
> 関連: [計測と可視化のmod.md](計測と可視化のmod.md), [バージョン対応表.md](バージョン対応表.md), [../filming/時間制御とスロー.md](../filming/時間制御とスロー.md), [../filming/ワールド内の演出.md](../filming/ワールド内の演出.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../mechanics/投射物.md](../mechanics/投射物.md), [../mechanics/爆発.md](../mechanics/爆発.md)

## 要点
- Carpet の Modrinth のプラットフォーム欄は Fabric だけで、ライセンスは MIT。Modrinth の互換性欄は Java Edition 1.14.4〜26.3（2026-11-19 取得）。【一次】[S1]
- GitHub の master ブランチは `minecraft_version=26.4-snapshot-8`、`mod_version = 26.4-beta-6`（2026-11-19 取得）。mod の版番号が MC のバージョンと同じ 26.4 で始まる。【一次】[S3]
- master の CarpetServer が登録するコマンドは profile / counter / log / spawn / player / info / distance / perimeterinfo / draw / script / MobAI などで、**Carpet 独自の /tick は登録されていない**（MobAI が `/track` であることはルール `commandTrackAI` の説明による）。一方、Modrinth の説明文と GitHub Wiki には古い `/tick warp` 等の説明が残っている。【一次】[S4][S5][S1]／Wiki【二次】[S6]
- `/player` で偽プレイヤーを出し、use（右クリック）・attack・jump などを once / continuous / interval（tick 間隔）で実行させられる。出現位置・向き・ディメンション・ゲームモードも指定できる。【一次】[S8]
- use を止めたときと、interval の実行していない tick では `releaseUsingItem`（手に持ったアイテムの使用をやめる処理）が呼ばれる。ソースのコメントは弓に触れている。【一次】[S9]
- `/log projectiles`・`/log fallingBlocks` は、対象の寿命が終わったときに 1tick ごとの位置と motion（速度）をチャットに出す。記録されるのは、ログ用のヘルパーが作られた時点で購読者がオンラインにいたものだけ（ヘルパーが作られるタイミングは未確認）。【一次】[S11]／1tick ごとの説明は Wiki【二次】[S6]
- `/log explosions full` は爆発ごとに威力・ブロックへの影響・巻き込んだエンティティの位置と速度変化 `dV` を出す。Wiki のコマンド一覧には載っていない。【一次】[S10][S13]
- TNT の着火時のランダムな初速を消す・水平角を固定する・爆発の乱数範囲を固定するルールがある（`tntPrimerMomentumRemoved`、`hardcodeTNTangle`、`tntRandomRange`）。【一次】[S5]
- 内蔵のスクリプト言語 Scarpet で、毎 tick の処理（`__on_tick`、エンティティの `on_tick` / `on_move`）と、位置・motion の取得と、ワールドの scripts フォルダへのファイル書き出し（json / text など）ができる。【一次】[S14]
- Scarpet の `draw_shape` で線・箱・球・円柱・多角形・文字ラベルをワールドに描ける。Carpet の入ったクライアントで正しく描かれ、入っていないクライアントにはダストパーティクルで送られる。【一次】[S14]
- 拡張 mod として carpet-extra、Carpet TIS Addition（LGPL-3.0-only）などがある。スナップショット向けの最小版として quick-carpet もある。【一次】[S2][S16]

## 詳細

### 概要・入手・ライセンス
Modrinth の題名の下の説明は次のとおり。【一次】[S1]
> 「Take full control over your vanilla game」[S1]
> 「Carpet is a mod for vanilla Minecraft that allows you to take full control of what matters from a technical perspective of the game.」[S1]

| 項目 | 値（2026-11-19 取得） | 確度・出典 |
|---|---|---|
| プラットフォーム | Fabric | 【一次】[S1] |
| 対応している環境 | サーバー側／クライアントとサーバー | 【一次】[S1] |
| ライセンス | MIT | 【一次】[S1] |
| ダウンロード数・フォロワー | 11.8M・2.7K（Modrinth の表示） | 【一次】[S1] |
| 公開・更新 | 4年前に公開、2か月前に更新（Modrinth の相対表示） | 【一次】[S1] |
| 古い MC 向け | 1.13 は gnembon/carpetmod、1.12 は gnembon/carpetmod112 | 【一次】[S1][S2] |

導入は他の Fabric mod と同じで、jar を `mods` フォルダに入れる（README）。【一次】[S2]

### 対応バージョン
| 情報源 | 内容 | 確度・出典 |
|---|---|---|
| Modrinth の互換性欄 | 26.3、26.2、26.1.x、1.21.x、1.20.x、1.19.x、1.18.x、1.17.1、1.16.x、1.15.x、1.14.4 | 【一次】[S1] |
| master の gradle.properties | `minecraft_version=26.4-snapshot-8`、`loader_version=0.20.1`、`mod_version = 26.4-beta-6` | 【一次】[S3] |
| 同ファイルの別ブランチ設定 | `release-extra-branch = false`、`release-extra-branch-name = 1.21.10` | 【一次】[S3] |
| 26.3 向けのリリース（Modrinth の版のページ /version/yt9oDFOj） | 版名『Carpet 26.3』、種類はリリース、対応 MC は 26.3、プラットフォームは Fabric、変更履歴は「support for Minecraft 26.3」。公開日は 2026-09-18（ページに埋め込まれたデータの値。画面の表示は「2 か月前」） | 【一次】[S17] |

- Modrinth のバージョン一覧のページは本文が JS で読み込まれ、個別のリリースのファイル名・公開日は読めなかった（2026-11-19）。【一次】[S1] 個別の版のページは読めた（上の表の 26.3 の行。[バージョン対応表.md](バージョン対応表.md) と同じ出典）。【一次】[S17]
- 他の mod との揃い具合は [バージョン対応表.md](バージョン対応表.md) に任せる。

### ルールの設定（/carpet）と既定値
GitHub Wiki のコマンド一覧によると、`/carpet list` でルールの一覧、`/carpet [rule] [value]` で変更、`/carpet setDefault [rule]` でワールドの `carpet.conf` に既定値として保存する。【二次】[S6]
> 「Lists the default configuration for this world stored in carpet.conf」[S6]

計測に関係するルールの既定値（master のソース）。【一次】[S5]　GitHub Wiki の設定一覧にも同じルールの説明が載っている。【二次】[S7]

| ルール | 既定値 | 内容 | 確度・出典 |
|---|---|---|---|
| `commandPlayer` | `ops` | /player を使える権限 | 【一次】[S5] |
| `commandLog` | `true` | /log | 【一次】[S5] |
| `commandDistance` | `true` | /distance | 【一次】[S5] |
| `commandInfo` | `true` | /info | 【一次】[S5] |
| `commandScript` | `true` | /script（Scarpet） | 【一次】[S5] |
| `commandScriptACE` | `ops` | アプリの読み込みや `/script run` をできる権限 | 【一次】[S5] |
| `commandDraw` | `ops` | /draw | 【一次】[S5] |
| `hopperCounters` | `false` | /counter とホッパーカウンター | 【一次】[S5] |
| `defaultLoggers` | `none` | 新しく入ったプレイヤーに自動で付けるログ | 【一次】[S5] |
| `commandTick` | `ops` | 説明文は「Enables /tick command to control game clocks」 | 【一次】[S5] |

- `commandTick` のルールは master の CarpetSettings に残っているが、master の CarpetServer のコマンド登録には TickCommand が無い。このルールが現在何を制御しているかは読めた範囲ではわからない。【一次】[S4][S5]

### /player（偽プレイヤー）
> 「Create fake players that act almost exactly like real players.」[S6]

master の PlayerCommand で登録されているサブコマンド。【一次】[S8]

| サブコマンド | 内容 | 確度・出典 |
|---|---|---|
| `spawn` / `spawn at <pos> facing <rot> in <dim> in <gamemode>` | 出現。`in <gamemode>` は gamemaster 権限が必要 | 【一次】[S8] |
| `use` / `attack` / `jump` / `drop` / `dropStack` / `swapHands` | 動作。各々 `once` / `continuous` / `interval <ticks>` を付けられる（付けないと once） | 【一次】[S8] |
| `drop all` / `mainhand` / `offhand` / `<slot>` | どのスロットを落とすか | 【一次】[S8] |
| `look north/south/east/west/up/down`、`look at <pos>`、`look <rotation>` | 向き | 【一次】[S8] |
| `turn left/right/back` | 90°・180° 回る | 【一次】[S8] |
| `move forward/backward/left/right`、`move`（止める） | 移動入力 | 【一次】[S8] |
| `sneak` / `unsneak` / `sprint` / `unsprint` | しゃがみ・ダッシュ | 【一次】[S8] |
| `hotbar <1-9>`、`mount`、`mount anything`、`dismount`、`kill`、`shadow`、`stop` | その他 | 【一次】[S8] |

- `shadow` は自分を偽プレイヤーに置き換えるもので、Wiki では「This only works on servers ( not single player)」とされる。【二次】[S6]
- 移動入力は、しゃがみ中は 0.3、それ以外は 1.0 を前後・左右の入力値に掛けて、プレイヤーの移動入力（`zza`・`xxa`）に入れる。【一次】[S9]
- 動作の実行: `once` は1回で終わり、`continuous` は毎 tick 続け、`interval N` は N tick ごとに実行する。【一次】[S9]
- use の動作では、実行しない tick（interval の合間）と `stop` のときに、手に持ったアイテムの使用をやめる処理（`releaseUsingItem`）が呼ばれる。ソースのコメントは弓に触れている。【一次】[S9]
> 「need to allow entity to tick, otherwise won't have effect (bow)」[S9]
- `stop` は全動作を止め、移動入力・しゃがみ・ダッシュも解除する。【一次】[S9]

### /log（ロガー）
master の LoggerRegistry に登録されているロガー。【一次】[S10]。説明は Wiki。【二次】[S6]

| ロガー | オプション | 内容 | 確度・出典 |
|---|---|---|---|
| `tnt` | brief / full | TNT の着火位置・初速の向き・爆発位置 | 【一次】[S10]／説明は【二次】[S6] |
| `projectiles` | brief / full | 投射物の 1tick ごとの位置（寿命の終わりに表示） | 【一次】[S10]／説明は【二次】[S6] |
| `fallingBlocks` | brief / full | 落下ブロックの 1tick ごとの位置（寿命の終わりに表示） | 【一次】[S10]／説明は【二次】[S6] |
| `explosions` | brief / full | 爆発ごとの位置・威力・巻き込んだエンティティ（Wiki に記載なし） | 【一次】[S10][S13] |
| `pathfinding` | 2 / 5 / 10 | 経路探索（Wiki は未記入） | 【一次】[S10]／説明は【二次】[S6] |
| `tps` | — | TPS と MSPT をプレイヤーリスト（TAB）に表示 | 【一次】[S10]／説明は【二次】[S6] |
| `mobcaps` | dynamic / overworld / nether / end | モブの上限をプレイヤーリストに表示 | 【一次】[S10]／説明は【二次】[S6] |
| `counter` | 16色 | ホッパーカウンターをプレイヤーリストに表示 | 【一次】[S10]／説明は【二次】[S6] |
| `packets` | — | パケット数をプレイヤーリストに表示 | 【一次】[S10]／説明は【二次】[S6] |

> 「Logs projectiles history of positions per tick during their lifetime (at the end).」[S6]
> 「When tnt goes boom, tells you where, when, how, why, who and what」[S6]

**軌跡ログ（projectiles・fallingBlocks）の中身**（TrajectoryLogHelper）。【一次】[S11]
> 「A generic log helper for logging the trajectory of things like blocks and throwables.」[S11]
- 1tick ごとに位置（x, y, z）と motion（速度ベクトル）を記録し、寿命の終わりにまとめて出力する。【一次】[S11]
- brief: 1tick を1つの記号で並べ（1行に最大20tick）、記号にマウスを乗せると Tick 番号・x・y・z・mx・my・mz が `%f`（小数6桁）で出る。【一次】[S11]
- full: 1tick を1行で、`tick: N pos` の後に位置、`mot` の後に motion を出す（位置と motion の書式は Messenger.dblt で、括弧や桁数は未読）。【一次】[S11]
- 記録するかどうかは、ヘルパーが作られた時点（コンストラクタ）にロガーの購読者がオンラインにいるかで決まる。ヘルパーが作られた後に購読しても、その対象は記録されない。ヘルパーがエンティティの生成時に作られるかはミックスインを読んでいないため未確認。【一次】[S11]

**TNT ログ**（TNTLogHelper）。【一次】[S12]
> 「Runs when the TNT is primed. Expects the position and motion angle of the TNT.」[S12]
- brief は `P`（着火位置）・初速のベクトル・`E`（爆発位置）。full はさらに同じ tick 内の通し番号 `#` とゲーム時刻 `@` を付ける。【一次】[S12]

**爆発ログ**（ExplosionLogHelper）。【一次】[S13]
- brief: tick ごとの通し番号、爆発位置、ブロックに影響するか。【一次】[S13]
- full: さらに `affects blocks`、`creates fire`、`power`、`destruction`（破壊の種類）、`affected entities`（各エンティティの位置、`dV`、種類、同じものの回数）。【一次】[S13]

### /distance・/info・/counter・/draw
- `/distance from [start] to [end]` で2点間の距離を出す。`from` だけで始点を覚え、`to` で終点までを出す。座標を省くと実行者の位置。【二次】[S6]
> 「Returns the Spherical, Cylindrical and Manhattan distance between the specified coordinates」[S6]
- `/info block [coordinate]` でブロックの情報を出す。`/info entity` は Wiki で「removed from Carpet a long time ago」とされる。【二次】[S6]
- `hopperCounters` を有効にすると、羊毛ブロックに向けたホッパーが通ったアイテムを数え、`/counter <color>` で照会、`/counter <color> reset` でリセットできる。【一次】[S5]
> 「Counters are global and shared between players, 16 channels available」[S5]
> 「Items counted are destroyed, count up to one stack per tick per hopper」[S5]
- `/draw sphere [center] [radius] [block]` で球をブロックで作る。Wiki には、後から多くの形が追加されたのでゲーム内の補完を見るよう注記がある。【二次】[S6]

### 時間の制御（Carpet の /tick は古いバージョンの機能）
- GitHub Wiki には Carpet の /tick（health、entities、freeze、step、rate、warp、superHot）が載っている。【二次】[S6]
> 「This will stop the processing of entities, world clocks, block updates, and redstone while still letting the player move freely.」[S6]
> 「Changes the rate at which things happen in the game. The default value is 20.0.」[S6]
- master の CarpetServer はこの TickCommand を登録していない（`/profile` は登録されている）。【一次】[S4]　バニラの /tick を使った時間の制御は [../filming/時間制御とスロー.md](../filming/時間制御とスロー.md) に任せる。
- `smoothClientAnimations`（既定 true）はクライアント側のルールで、説明は「smooth client animations with low tps settings」「works only in SP, and will slow down players」。【一次】[S5]
- `/profile` は「Enables /profile command to monitor game performance」で、既定は true。【一次】[S5]

### 実験の条件を変えるルール（使うなら必ず明記する）
master の CarpetSettings の定義。【一次】[S5]

| ルール | 既定値 | 説明 | 計測への関係（提案を含む） | 確度・出典 |
|---|---|---|---|---|
| `tntPrimerMomentumRemoved` | false | 「Removes random TNT momentum when primed」 | 着火時のランダムな初速を消す | 【一次】[S5] |
| `hardcodeTNTangle` | -1.0 | TNT の水平のランダムな角度を固定（0〜2π、-1で既定） | 向きを毎回同じにする | 【一次】[S5] |
| `tntRandomRange` | -1 | 爆発の乱数範囲を固定。`optimizedTNT` が有効でないと設定できない | 威力のばらつきを消す | 【一次】[S5] |
| `optimizedTNT` | false | 同じ場所・液体中での爆発を軽くする | 大量 TNT の負荷 | 【一次】[S5] |
| `mergeTNT` | false | 止まっている着火 TNT をまとめる | 大量 TNT の負荷 | 【一次】[S5] |
| `explosionNoBlockDamage` | false | 爆発でブロックが壊れない | 装置を壊さずに繰り返す | 【一次】[S5] |
| `tntDoNotUpdate` | false | 動力源の隣に置いても TNT が着火しない | 装置作り | 【一次】[S5] |
| `fastRedstoneDust` | false | レッドストーンの軽量化。位置に依存するバニラの挙動は保証しない | T10 では使わない | 【一次】[S5] |
| `sculkSensorRange` | 8 | スカルクセンサーの範囲を変える（1〜1024） | T09 では既定のまま | 【一次】[S5] |
| `pushLimit` | バニラの値 | ピストンの押せる数（1〜1024） | 装置作り | 【一次】[S5] |
| `simulationDistance` / `viewDistance` | 0 | サーバの設定を上書き（0〜32、0は上書きしない） | 遠くの装置を動かす | 【一次】[S5] |
| `antiCheatDisabled` | false | 速く動くプレイヤーが引き戻されない・飛行で蹴られない | 高速の撮影移動 | 【一次】[S5] |
| `creativeNoClip`・`creativeFlySpeed`・`creativeFlyDrag` | false・1.0・0.09 | クリエイティブ飛行の壁抜け・速さ・空気抵抗。壁抜けはサーバではクライアントとサーバの両方での設定が必要、速さ・空気抵抗はクライアントだけの設定 | 撮影の移動 | 【一次】[S5] |

> 「so behaviour of locational vanilla contraptions is not guaranteed」[S5]
> 「With 1.0 drag, using speed of 11 seems to matching vanilla speeds.」[S5]

### Scarpet（スクリプト）
> 「Carpet contains Scarpet, a powerful in-game programming language that allows you to easily interact with the game or make powerful apps to further enhance your game.」[S1]

**アプリの置き場所と読み込み**【一次】[S14]
- `.sc` のファイルをワールドの `scripts` フォルダに置き、`/script load [app_name]` で読み込む。ワールドと一緒に読み込まれるもの（`scriptsAutoload` 既定 true）もある。【一次】[S14][S5]
- 名前が `foo` のアプリなら、スクリプトは `world/scripts/foo.sc`、アプリ専用のデータは `world/scripts/foo.data/...`、共有データは `world/scripts/shared/...`。【一次】[S14]

**位置・速度の取得**【一次】[S14]
- `query(e, 'pos')` は位置の3つ組、`query(e, 'motion')` は motion ベクトル、`query(e, 'on_ground')` は接地。【一次】[S14]
> 「Motion represents the velocity from all the forces that exert on the given entity.」[S14]
> 「Things that are not 'forces' like voluntary movement, or reaction from the ground are not part of said forces.」[S14]

**毎 tick の処理**【一次】[S14]
> 「Event triggers at the beginning of each tick, located in the overworld.」[S14]
- 上は `__on_tick()` の説明。エンティティ単位では `entity_event(e, 'on_tick', ...)`（そのエンティティの tick の直前）と `'on_move'`（位置が変わった直後。引数は `entity, velocity, pos1, pos2`）がある。`entity_load_handler` で、ある種類のエンティティが読み込まれるたびに処理を付けられる。【一次】[S14]
> 「executes every tick right before the entity is ticked in the game」[S14]
- `game_tick(mstime?)` はゲームを1tick進める関数。tick の中で呼ぶと処理の途中に別の tick が挟まるので、ドキュメントは「generally a bad idea」としている。【一次】[S14]

**ファイルへの書き出し**（`write_file(resource, type, data, ...)`）【一次】[S14]
- 種類は `nbt`、`json`、`text`（行ごとに改行を足す）、`raw`（改行を足さない）と、それぞれの `shared_` 版。拡張子は種類から決まる（`.nbt`、`.json`、`.txt`）。【一次】[S14]
> 「The default no-name app, via `/script run` command can only save/load/read files from the shared space.」[S14]
> 「Since files are closed after each write, sending multiple lines of data to write is beneficial for writing speed.」[S14]

**ワールドに図形を描く**（`draw_shape`）【一次】[S14]
- 図形は `'line'`、`'box'`、`'sphere'`、`'cylinder'`、`'polygon'`、`'label'`（文字）など。`duration` tick で消える。【一次】[S14]
- 共通の属性: `color`（`0xRRGGBBAA`）、`fill`、`follow`（エンティティに追従）、`seethrough`（ブロック越しに見える）、`debug`（F3+B のときだけ見える）、`player`（見せる相手）。【一次】[S14]
> 「Shapes will draw properly on all carpet clients.」[S14]
> 「Other connected players that don't have carpet installed will still be able to see the required shapes in the form of dust particles.」[S14]
- Carpet の無いクライアント向けのパーティクルでは `duration` は守られない。【一次】[S14]
- `create_marker(text, pos, ...)` は文字やブロックを表示する防具立ての目印を出す。アプリを外すと読み込まれている範囲の目印は消える。【一次】[S14]

**権限**: `commandScriptACE`（既定 ops）未満の権限のユーザーはアプリの読み込みや `/script run` ができない。【一次】[S5]

### 拡張 mod
- README は、自動クラフトなどを足す carpet-extra、Scarpet アプリの置き場（gnembon/scarpet）、スナップショット向けの最小版 quick-carpet を紹介している。quick-carpet では拡張や Scarpet アプリは使えない。【一次】[S2]
> 「You will not be able to add any extensions or use scarpet apps on this one though.」[S2]
- Carpet TIS Addition は Carpet の拡張で、ライセンス LGPL-3.0-only、Modrinth の互換性欄は 1.14.4〜26.4-snapshot-8（2026-11-19 取得、5日前に更新の表示）。同じ MC バージョンの Carpet と一緒に使う。ドキュメントは carpet.tis.world（このセッションでは読めないホスト）。【一次】[S15][S16]
> 「Under the default configuration conditions, this mod will not change any vanilla behavior at all」[S16]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。

- **計測の正本は今の方式（バニラの /tick step ＋ RCON で `data get`）のまま**にする。Carpet の Scarpet で `__on_tick` か `on_move` から位置と motion を `write_file`（json / text）に書く方式を「速い記録方式」の候補にし、E001 で同じ値になるかを比べる。行はまとめて書く。（根拠: [S14]）
- 実験の下見（装置の調整）には `/log projectiles full` を使う。**購読してから発射する**。チャットの出力なので、正式な計測には使わない。（根拠: [S11][S6]）
- 爆発の回（T07・T15）では `/log explosions full` の `dV` で、爆発ごとのエンティティの速度変化を数値で出せるか試す。（根拠: [S13]）
- TNT の乱数を消すルール（`tntPrimerMomentumRemoved`、`hardcodeTNTangle`、`tntRandomRange`）はバニラと違う条件になるので、使う回は `experiment.yaml` と動画内の両方に明記する。乱数を含めた本来の挙動は、今の方針どおり N 回繰り返して分布で示す。（根拠: [S5]、[../../docs/MC実行基盤.md](../../docs/MC実行基盤.md) §5）
- 投げる・撃つ・走るの再現は `/player` で行う。弓は `use continuous` → N tick 後に `stop` で引き時間を変えられるか、`/tick freeze` と `step` を組み合わせて実測で確かめる。（根拠: [S8][S9]）
- 軌跡をワールドに描く場合は `draw_shape` を使い、**撮影用クライアントにも Carpet を入れる**。Flashback / Replay Mod の録画に映るかは最初に試す。（根拠: [S14]）
- レッドストーン（T10）とスカルク（T09）の回では `fastRedstoneDust`・`sculkSensorRange` を既定のままにし、`/carpet` の一覧で既定と違うルールがないことを撮影前に確かめる。（根拠: [S5][S6]）
- `mc/mods.yaml` には Carpet の版に加えて、変えたルールと `carpet.conf` の中身を書く。（根拠: [S6]）

## わかっていないこと・要確認
- 26.3 向けの最新リリースの版番号・公開日（Modrinth のバージョン一覧は JS で読めず、CurseForge は 403 だった）。→ 2026-11-20 に、[バージョン対応表.md](バージョン対応表.md) が読んだ Modrinth の版のページで確かめた: Carpet 26.3、2026-09-18、release【一次】[S17]。それが 26.3 向けの最新であることは、バージョン対応表.md の調べ（プロジェクトページに埋め込まれた版の一覧）による。
- `commandTick` ルールが現在何を制御しているか。Carpet がバニラの /tick に何かを足しているか（Modrinth の説明文には `/tick warp` が残る）。
- `/log projectiles` が対象にするエンティティの種類（矢・トライデント・雪玉・エンダーパール・花火など、どれが含まれるか）と、軌跡ログのヘルパーが作られるタイミング（エンティティの生成時か）。ソースのミックスインは未読。
- `/player use continuous` → N tick 後に `stop` で、弓の引き時間を tick 単位で決められるか（`releaseUsingItem` が呼ばれることだけはソースで確認。弓の挙動は未実測）。
- Scarpet の `__on_tick`／`on_move` と `write_file` を組み合わせて、RCON の往復なしに毎 tick の値をファイルに残せるか（個々の機能はドキュメントで確認、組み合わせは未実測）。
- full 出力の数値の桁数（Messenger.dblt の書式）。
- RCON（プレイヤーでない実行者）や偽プレイヤーが /log を購読できるか。
- Scarpet の `__on_tick` がバニラの `/tick freeze` 中に動くか、`/tick step` と1対1で同期するか。
- `draw_shape` の図形が Flashback / Replay Mod の録画に入るか。
- Carpet を入れただけ（ルールは既定値）で、計測する物理の値がバニラと変わらないか（実測で比べる）。
- `/player look <rotation>` の引数の順序（Wiki は pitch yaw と書くが、ソースはバニラの回転の引数を使っている）。

## 参照先
- [S1] Carpet - Minecraft Mod — Modrinth — https://modrinth.com/mod/carpet — 更新: 「2か月前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] Fabric Carpet README.md — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] gradle.properties（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/gradle.properties — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] CarpetServer.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/CarpetServer.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] CarpetSettings.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/CarpetSettings.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Commands（GitHub Wiki） — gnembon/fabric-carpet Wiki — https://raw.githubusercontent.com/wiki/gnembon/fabric-carpet/Commands.md — 不明（古いバージョンの記述を含む） — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Current Available Settings（GitHub Wiki） — gnembon/fabric-carpet Wiki — https://raw.githubusercontent.com/wiki/gnembon/fabric-carpet/Current-Available-Settings.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] PlayerCommand.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/commands/PlayerCommand.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] EntityPlayerActionPack.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/helpers/EntityPlayerActionPack.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] LoggerRegistry.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/logging/LoggerRegistry.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] TrajectoryLogHelper.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/logging/logHelpers/TrajectoryLogHelper.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S12] TNTLogHelper.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/logging/logHelpers/TNTLogHelper.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S13] ExplosionLogHelper.java（master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/src/main/java/carpet/logging/logHelpers/ExplosionLogHelper.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S14] Scarpet のドキュメント（docs/scarpet/Full.md、master） — gnembon/fabric-carpet — https://raw.githubusercontent.com/gnembon/fabric-carpet/master/docs/scarpet/Full.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S15] Carpet TIS Addition README.md — TISUnion — https://raw.githubusercontent.com/TISUnion/Carpet-TIS-Addition/HEAD/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S16] Carpet TIS Addition - Minecraft Mod — Modrinth — https://modrinth.com/mod/carpet-tis-addition — 更新: 「5日前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S17] Carpet 26.3（Modrinth の版のページ） — Modrinth（gnembon） — https://modrinth.com/mod/carpet/version/yt9oDFOj — 2026-09-18（ページに埋め込まれた公開日。表示は「2 か月前」） — 取得: 2026-11-19 — 原文: 読んだ
