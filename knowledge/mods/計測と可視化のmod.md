# 計測と可視化の mod（MiniHUD・Tweakeroo・Litematica・Servux・WorldEdit・F3）

> 対象: 画面に座標・速度・明るさなどを出す道具（MiniHUD、バニラの F3 デバッグ画面とデバッグレンダラー）と、実験装置を作る・置き直す道具（Litematica、WorldEdit）、その補助（Tweakeroo、Servux）。Carpet は [Carpet.md](Carpet.md) に分ける。
> 使う場面: 実験の設計、計測値を画面に出して撮るかどうかの判断、装置の作成と再配置、`mc/mods.yaml` を書くとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition。mod の互換性は Modrinth の表示（2026-11-19 取得、各 mod とも最新は 26.3）。F3 の項目は minecraft.wiki の記事（取得時点の版。1.21.9〜26.3 と、開発中の 26.4 の記述を含む）。MiniHUD の表示項目は sakura-ryoko/minihud の既定ブランチの言語ファイル（対応する MC バージョンは未確認）。
> 関連: [Carpet.md](Carpet.md), [バージョン対応表.md](バージョン対応表.md), [../filming/カメラワーク技法.md](../filming/カメラワーク技法.md), [../filming/ワールド内の演出.md](../filming/ワールド内の演出.md), [../filming/シェーダーと画質mod.md](../filming/シェーダーと画質mod.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../mechanics/光.md](../mechanics/光.md), [../mechanics/流体.md](../mechanics/流体.md)

## 要点
- MiniHUD はクライアント専用で、MaLiLib が必要。「mini F3」の情報行と、明るさ・スライムチャンク・構造物の範囲などのオーバーレイを描く。ライセンス LGPL-3.0-only。【一次】[S1]
- MiniHUD の速度の行は3種類（合計、軸ごと、水平と垂直）で、単位を m/s・km/h・mph・fps・mach・c から選べる。3つとも説明はプレイヤー自身の速度。ほかに乗っている馬の速さ（m/s）を出す `infoHorseSpeed` があるが、言語ファイルにはそれ以外のエンティティ（矢・TNT など）の速度を出す行は見当たらない。【一次】[S2]
- MiniHUD のサーバ TPS の行は、Carpet のサーバで TPS 表示の Carpet ルールが有効なときだけ正確で、それ以外はクライアント側の推定（20 未満しか検出できない）。TPS の行には Frozen・Sprinting の表示もある。【一次】[S2]
- バニラの F3 デバッグ画面は 28 の要素に分かれ、F3+F6 のデバッグオプションで要素ごとに OFF / In Overlay / Always を選べる（1.21.9 で導入。Always は F3 を開かなくても常に表示）。【二次】[S7]
- **Java 26.3 でバニラの F3 に `player_speed`（プレイヤーの速さ、単位は blocks/tick）が追加された**。【二次】[S7]
- デバッグレンダラーは15種類。当たり判定（F3+B）、チャンク境界（F3+G）に加えて、1.21.11 から衝突箱・水位・ブロックの光・空の光・足場ブロックなどの表示もデバッグオプションから切り替えられる。【二次】[S8]
- F3+B の当たり判定の表示は見た目のモデルに対する箱で、実際の当たり判定とずれることがある（Java Edition、記事の取得時点）。【二次】[S8]
- Tweakeroo はクライアント側の小さな機能の集まりで、人気の機能にフリーカメラ・ガンマの上書きなどが挙がり、1.13.2〜1.20.4 版の機能一覧にはズームもある。サーバによっては不正とみなされる。ライセンス LGPL-3.0-only。【一次】[S3]
- Litematica は設計図（schematic）の mod。1.21.3 以降はシェーダーと一緒だと描画が正しく動かないので、使うときはシェーダーを切る。【一次】[S4]
- Servux はサーバ側の mod で、MiniHUD に構造物の範囲などを送る。シングルプレイやクライアントには不要。【一次】[S5]
- WorldEdit は Java 版専用のワールド編集ツールで、説明文では NeoForge・Fabric・Bukkit 系（Spigot・Paper）に対応（Modrinth のプラットフォーム欄には Forge・Folia・Quilt も載る）。ライセンス GPL-3.0-only。【一次】[S6]

## 詳細

### MiniHUD
> 「MiniHUD is a client-side mod that has various "mini F3" info lines that you can choose from.」[S1]
> 「You should never put MiniHUD on the server. It doesn't do anything there. Only put Servux on the server.」[S1]

| 項目 | 内容（2026-11-19 取得） | 確度・出典 |
|---|---|---|
| 依存 | MaLiLib（設定画面・ホットキーの仕組みを使う） | 【一次】[S1] |
| 操作 | 表示全体の切り替えは H、設定画面は H + C（既定） | 【一次】[S1] |
| 環境 | クライアント側 | 【一次】[S1] |
| ローダー | Fabric、Forge、LiteLoader、Ornithe、Rift | 【一次】[S1] |
| 互換性欄 | 1.8〜26.3（26.3、26.2、26.1.x、1.21.x、1.20.1–1.20.6 …） | 【一次】[S1] |
| ライセンス | LGPL-3.0-only | 【一次】[S1] |

**計測に関係する情報行**（言語ファイルの説明文）。【一次】[S2]

| 情報行 | 説明 | 確度・出典 |
|---|---|---|
| `infoCoordinates` | 「Show the player's coordinates」。言語ファイルの書式は `XYZ: %.2f / %.4f / %.2f`（y だけ小数4桁）。`useCustomizedCoordinateFormat` を使うと `coordinateFormat`（説明上の既定は `x: %.1f y: %.1f z: %.1f`）に変わる | 【一次】[S2] |
| `infoBlockPosition`、`infoChunkPosition` | プレイヤーのブロック座標、チャンク | 【一次】[S2] |
| `infoSpeed` | 「Show the player's current moving speed」 | 【一次】[S2] |
| `infoSpeedAxis` | 「Show the player's current moving speed per axis」 | 【一次】[S2] |
| `infoSpeedHV` | 水平（xz）と垂直（y）に分けた速さ | 【一次】[S2] |
| `infoHorseSpeed` | 乗っている馬の速さ（m/s）。書式は `%s Speed: §b%.3f§r m/s` | 【一次】[S2] |
| `infoDistance` | 基準点からの距離。基準点はホットキー `setDistanceReferencePoint` でプレイヤーの今の位置を記録する | 【一次】[S2] |
| `infoRotationYaw`、`infoRotationPitch`、`infoFacing` | 向き | 【一次】[S2] |
| `infoLightLevel` | 「Show the current light level」 | 【一次】[S2] |
| `infoTimeWorld` | 「Show the current world time in ticks」 | 【一次】[S2] |
| `infoServerTPS` | サーバの TPS と MSPT（下の注を参照） | 【一次】[S2] |
| `infoLookingAtEntity`、`infoLookingAtEffects` | 見ているエンティティの名前・体力、効果。Servux があると情報が増える | 【一次】[S2] |

- 速度の表示の書式は、単位ごとに `Speed: %.3f m/s`、`Speed: x: %.3f y: %.3f z: %.3f m/s`、`Speed: xz: %.3f y: %.3f m/s` などで、小数3桁。単位は `speedUnits` の設定で m/s、km/h、mph、fps、mach、c から選ぶ。【一次】[S2]
- サーバ TPS の行の説明。【一次】[S2]
> 「Note: This is only accurate when running a Carpet server」[S2]
> 「Otherwise it is estimated on the client side」[S2]
- TPS の行の表示文字列に「[§b§lFrozen§r]」「[§d§lSprinting§r]」がある。どの条件で表示されるかは、ソースを読んでいないため未確認。【一次】[S2]

**オーバーレイ（ワールドに描く表示）**。【一次】[S1][S2]
- 明るさ（Light Level）、ブロックの格子（Block Grid）、スライムチャンク、リージョンファイルの境界、構造物の範囲などのオーバーレイがある。【一次】[S2]
- 形の表示（shapes）として、箱、円・円柱、球（ブロック単位）、ブロックの線、角錐、円錐などがある。【一次】[S2]
- 構造物の範囲の表示は、シングルプレイと、Servux を入れたサーバで動く。【一次】[S1]
- 球の形は MC 1.18 向けの更新以降、少し歪んでいると作者が注記している。【一次】[S1]
> 「The sphere shape is currently slightly broken since the mod update for MC 1.18」[S1]

### バニラの F3 デバッグ画面（Java Edition）
> 「The debug screen consists of 28 elements」[S7]
- 各要素は F3+F6 のデバッグオプションで OFF / In Overlay / Always を選べる。組み込みの設定に Default Profile と Performance Profile がある。【二次】[S7]
> 「"Always" causes the element to display on-screen even when the debug overlay is not open.」[S7]
- ゲームルール `reduced_debug_info` を true にすると、一部の要素は設定に関係なく表示されない。【二次】[S7]
- 計測に関係する要素。【二次】[S7]

| 要素 | 表示 | 確度・出典 |
|---|---|---|
| `player_position` | `XYZ:`（足の座標）、`Block:`、`Chunk:`、`Facing:`（方角・yaw・pitch）、ディメンション、強制読み込みチャンク数 | 【二次】[S7] |
| `player_speed` | `Speed: #.### blocks/tick`。プレイヤーの速さ（既定は OFF） | 【二次】[S7] |
| `light_levels` | `Client Light:` 合計（空の光とブロックの光の大きい方）と内訳。クライアント側の値 | 【二次】[S7] |
| `tps` | サーバの種類、1tick の処理時間（シングルプレイのみ）、パケット数 | 【二次】[S7] |
| `fps` | フレームレート、上限、表示モード、画面のリフレッシュレート | 【二次】[S7] |
| `looking_at_entity` ほか | 見ているブロック・流体・エンティティの ID・状態・タグ | 【二次】[S7] |

> 「Displays the player's speed in blocks per tick.」[S7]

**変更の履歴**（記事の History 節）。【二次】[S7]

| バージョン | 変更 | 確度・出典 |
|---|---|---|
| 1.21.9（25w31a） | 既定の F3 を簡素化。項目ごとに切り替える設定画面を追加（当初は F3+F5） | 【二次】[S7] |
| 1.21.9（Pre-Release 4） | 設定画面のキーが F3+F6 に変わる | 【二次】[S7] |
| 26.1（snap1） | `looking_at_block` などを `_state` と `_tags` に分ける。光のグラフ（lightmap graph）を追加 | 【二次】[S7] |
| 26.3（snap4） | `player_speed` を追加。`fps` にリフレッシュレート。設定画面に GUI Scale | 【二次】[S7] |
| 26.4（開発中、snap2） | F3 の見た目を読みやすく作り直す | 【二次】[S7] |

### デバッグレンダラー（ワールドに重ねて描く F3 の表示）
> 「There are 15 debug renderers that can be enabled.」[S8]
- F3+F6 の「Debug Renderers」で切り替える。既定のプロファイルで有効なのは `3d_crosshair` だけ。【二次】[S8]

| レンダラー | 内容 | 使える版（記事の履歴） | 確度・出典 |
|---|---|---|---|
| `entity_hitboxes` | 当たり判定（白い箱）、向き（青。1.21.11 から矢印）、目の高さ（赤） | F3+B は 1.4.4 から | 【二次】[S8] |
| `chunk_borders` | チャンクの境界 | F3+G は 1.10 から | 【二次】[S8] |
| `3d_crosshair` | 照準を xyz 軸（赤・緑・青）の線に置き換える | 1.8 から | 【二次】[S8] |
| `visualize_collision_boxes` | 周囲のブロックの衝突箱（選択枠と違う） | 1.21.11 から設定画面で切替 | 【二次】[S8] |
| `visualize_entity_supporting_block` | エンティティが乗っているとみなされるブロック（プレイヤーは赤） | 1.21.11 から設定画面で切替 | 【二次】[S8] |
| `visualize_water_levels` | 水の高さ（水源 8 〜 流れの端 1） | 1.21.11 から設定画面で切替 | 【二次】[S8] |
| `visualize_block_light_levels` | ブロックの光（黄の 15 〜 赤の 1、0 は非表示） | 1.21.11 から設定画面で切替 | 【二次】[S8] |
| `visualize_sky_light_levels` | 空の光（シアンの 14 〜 青の 0、15 は非表示） | 1.21.11 から設定画面で切替 | 【二次】[S8] |
| `visualize_heightmap`、`visualize_solid_faces`、`visualize_chunks_on_server` ほか | 高さマップ、頑丈な面、チャンクの読み込み状態など | 1.21.11 から設定画面で切替 | 【二次】[S8] |

- 1.21.9 の開発版 25w37a では一部をデバッグプロパティで有効にする形だったが、1.21.11（25w41a）でプロパティが消え、設定画面から切り替えられるようになった。【二次】[S8]
> 「Note that the shown hitbox is just a visual box relative to the visual model, rather than the actual hitbox」[S8]

### Tweakeroo
> 「Tweakeroo is a client-side mod that adds a whole bunch of miscellaneous "tweaks" to the game.」[S3]
- 人気の機能として、手持ちの補充、ブロックの置き方の拡張、高速クリック、ガンマの上書き、フリーカメラが挙がっている。設定画面は X + C（既定）。【一次】[S3]
- 1.13.2〜1.20.4 版の機能一覧に `tweakFreeCamera`、`tweakZoom`、`tweakFlySpeed`、`tweakGammaOverride` などがある（それ以降の版の一覧はページに無い）。【一次】[S3]
- サーバのアンチチートに引っかかる機能があるので、サーバの管理者に確認するよう注意書きがある。【一次】[S3]
> 「Note: Features marked with an asterisk only work in single player.」[S3]
- 互換性欄は 1.12.x〜26.3、ライセンス LGPL-3.0-only、クライアント側。【一次】[S3]
- フリーカメラを撮影に使う話は [../filming/カメラワーク技法.md](../filming/カメラワーク技法.md) に任せる。

### Litematica（装置の保存と再配置）
> 「A client-side schematic mod with extra features for creative mode work」[S4]
- 1.14 以降は Fabric が主。Forge 版は 1.12.2 だけ。【一次】[S4]
- メインメニューは M、設定は M + C、配置の一覧は M + P、設計図との照合（Schematic Verifier）は M + V（既定）。【一次】[S4]
> 「Litematica's rendering doesn't currently work properly with shaders (even with Iris) in 1.21.3+.」[S4]
- 簡単設置（Easy Place）は空気ブロックをクリックするため、サーバによっては不正とみなされる。【一次】[S4]
- 互換性欄は 1.12.x〜26.3、ライセンス LGPL-3.0-only。【一次】[S4]

### Servux
> 「Servux itself is never needed on the clients or in single player. It's only needed/useful on the server side in multiplayer.」[S5]
- LAN で開くホストのクライアントに入れると、接続した他のプレイヤーにも効く。【一次】[S5]
- ページの説明（0.1.x 時点）では、機能は MiniHUD への構造物の範囲の送信だけとされる。【一次】[S5]　一方、MiniHUD の言語ファイルには Servux の「Entity Data Sync」「HUD Data Sync」の通信を使う設定があり、Servux と組み合わせると見ているエンティティの情報が増えるとある。【一次】[S2]
- 互換性欄は 1.14.4〜26.3、Fabric、環境は「専用サーバーのみ」の表示、ライセンス LGPL-3.0-only。【一次】[S5]

### WorldEdit（装置作り）
> 「A Minecraft Map Editor... that runs in-game!」[S6]
> 「Compatible with NeoForge, Fabric, and Bukkit-based platforms (Spigot and Paper).」[S6]
- mod 版（NeoForge / Fabric）は `mods` フォルダ、プラグイン版（Spigot / Paper）は `plugins` フォルダに入れる。【一次】[S6]
> 「WorldEdit does not support Bedrock!」[S6]
- 互換性欄は 1.2.3〜26.3、環境はサーバー側・シングルプレイ、ライセンス GPL-3.0-only（2026-11-19 取得、「先月 に更新」の表示）。【一次】[S6]

### ワールド内に計測値や軌跡を描くほかの方法
- Carpet の Scarpet の `draw_shape`（線・箱・球・文字）と `/log` の軌跡ログは [Carpet.md](Carpet.md) に書いた。
- 表示エンティティ・パーティクル・ボスバーなどのバニラの演出は [../filming/ワールド内の演出.md](../filming/ワールド内の演出.md) に任せる。

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。

- **基盤のバージョンが 26.3 以降なら、プレイヤーの座標と速さはバニラの F3 だけで出せる**。必要な要素だけを Always にして、ほかは OFF にした表示を撮影用に作る。速さの単位は blocks/tick なので、字幕で換算を添える。（根拠: [S7]）
- 視聴者に m/s や km/h で速さを見せたいときは MiniHUD の `infoSpeedAxis` / `infoSpeedHV` を使う。ただし**プレイヤー自身（と乗っている馬）の速さしか出ない**ので、矢や TNT などの速さは Carpet の `/log` か Scarpet で取る。（根拠: [S2]、[Carpet.md](Carpet.md)）
- 画面に出す値は計測値ではなく見せるための表示として扱い、計測の正本は `experiment.yaml` の手順で取った CSV にする（MiniHUD の座標は小数1〜4桁で表示され、F3+B の箱は見た目のモデル基準でずれうるため）。（根拠: [S2][S8]）
- 光（T08）は `visualize_block_light_levels` / `visualize_sky_light_levels`、水（T06・T18）は `visualize_water_levels`、摩擦（T04）は `visualize_entity_supporting_block` で、数値をワールドに重ねた画が撮れるか試す（1.21.11 以降）。（根拠: [S8]）
- 実験装置は Litematica か WorldEdit で保存して置き直す。Litematica は**シェーダーを切って配置し、置き終えてからシェーダーを入れて撮る**。（根拠: [S4][S6]）
- ローカルの専用サーバを使う構成（[../../docs/MC実行基盤.md](../../docs/MC実行基盤.md)）なので、MiniHUD の構造物表示やエンティティ情報が要る回だけ、サーバ側に Servux を入れる。（根拠: [S1][S5]）
- サーバの TPS を画面に出すなら、MiniHUD の値は Carpet のサーバで TPS 表示のルールが有効なときだけ正確なので、Carpet を入れた構成で使い、どのルールかを先に確かめる。（根拠: [S2]）

## わかっていないこと・要確認
- MiniHUD の速度の行が、何から速度を計算しているか（位置の差か、motion か）と、/tick freeze 中にどう表示されるか。ソースは未読。
- MiniHUD の言語ファイルを読んだ sakura-ryoko/minihud の既定ブランチが、どの MC バージョン向けか。Modrinth の MiniHUD がどのリポジトリから配布されているか。
- MiniHUD の TPS の行の注にある「TPS display carpet rule」[S2] がどの Carpet ルールを指すか（master の CarpetSettings に該当する名前は見当たらなかった）。
- MiniHUD の TPS の行の Frozen・Sprinting が、バニラの /tick freeze・/tick sprint の状態を示すのか（表示条件のソースは未読）。
- バニラ F3 の `player_speed` が、プレイヤー以外（乗り物に乗っているとき等）でどの速さを出すか。座標の小数の桁数。
- デバッグレンダラーの表示や F3 の Always の表示が、Flashback / Replay Mod の録画に入るか（クライアントの画面表示なので入らない可能性があるが未確認）。
- Servux の現在の機能一覧（Modrinth の説明は 0.1.x 時点のまま）。
- Tweakeroo の 1.20.5 以降の機能一覧（Modrinth のページは 1.20.4 までの一覧）。
- 26.4 で F3 の作り直しがどこまで項目に影響するか（開発中）。

## 参照先
- [S1] MiniHUD - Minecraft Mod — Modrinth — https://modrinth.com/mod/minihud — 更新: 「2か月前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] MiniHUD 言語ファイル en_us.json（既定ブランチ） — sakura-ryoko/minihud — https://raw.githubusercontent.com/sakura-ryoko/minihud/HEAD/src/main/resources/assets/minihud/lang/en_us.json — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Tweakeroo - Minecraft Mod — Modrinth — https://modrinth.com/mod/tweakeroo — 更新: 「2か月前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Litematica - Minecraft Mod — Modrinth — https://modrinth.com/mod/litematica — 更新: 「2か月前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Servux - Minecraft Mod — Modrinth — https://modrinth.com/mod/servux — 更新: 「2か月前」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] WorldEdit - Minecraft Plugin — Modrinth — https://modrinth.com/plugin/worldedit — 更新: 「先月」の表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Debug screen — Minecraft Wiki — https://minecraft.wiki/w/Debug_screen?action=raw — 不明（取得時点の版） — 取得: 2026-11-19 — 原文: 読んだ
- [S8] Debug renderer — Minecraft Wiki — https://minecraft.wiki/w/Debug_renderer?action=raw — 不明（取得時点の版） — 取得: 2026-11-19 — 原文: 読んだ
