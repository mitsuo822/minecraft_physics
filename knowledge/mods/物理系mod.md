# 物理系mod（物理を扱う・変える mod と、modなしで物理を変えるバニラの属性）

> 対象: Minecraft の物理を扱う・変える mod（Create、Create Aeronautics と Sable、Valkyrien Skies 2、Physics Mod、重力を変える mod、惑星の重力がある mod、大きさを変える mod、Immersive Portals、流体の mod）の中身・ローダー・対応バージョン・ライセンス。あわせて、mod なしで重力・大きさ・摩擦・空気抵抗・反発を変えられるバニラの「属性（attribute）」。
> 使う場面: テーマ選定（T06・T11・T12・T14・T17・T18 など mod を使う回の実現性の判断）、`mc/mods.yaml` の別構成（`profiles.create` 等）を決めるとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition。各 mod の対応は 2026-11-19 時点の Modrinth の表示。バニラの属性は Java Edition 1.20.5〜26.3。最新の Java Edition は 26.3（[バージョン対応表.md](バージョン対応表.md)）。
> 関連: [バージョン対応表.md](バージョン対応表.md), [Carpet.md](Carpet.md), [計測と可視化のmod.md](計測と可視化のmod.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../filming/Flashback.md](../filming/Flashback.md), [../filming/ReplayMod.md](../filming/ReplayMod.md), [../mechanics/重力と空気抵抗.md](../mechanics/重力と空気抵抗.md), [../mechanics/摩擦と滑りやすさ.md](../mechanics/摩擦と滑りやすさ.md), [../mechanics/流体.md](../mechanics/流体.md)

## 要点

- **物理系の大型 mod は、どれも最新の 26.3 に対応していない。** Create は 1.21.1（NeoForge）まで、Create の Fabric 版は 1.20.1 まで、Valkyrien Skies 2 は 1.20.1 まで、Create Aeronautics と Sable は 1.21.1 だけ（2026-11-19 の Modrinth の表示）。【一次】[S1][S4][S7][S9][S11]
- **Create の本流は Forge／NeoForge 用。** Fabric 版（Create Fabric）は別チームの移植で、最新は 1.20.1 向けの 6.0.8.1（2025-12-02）。【一次】[S1][S4]
- **Create Aeronautics（飛行機・車・気球などの物理の乗り物）は NeoForge 1.21.1 専用**で、ライブラリ mod の Sable と Create が必須。Sable の物理の処理は Rust 製の物理エンジン Rapier に基づく。Iris（シェーダー）とは表示に問題があると公式ページに書かれている。【一次】[S7][S9][S10]
- **Sable は動くブロックの塊（sub-level）を追加するライブラリで、`/sable` コマンドで組み立て・変更・問い合わせができ、Fabric 版もある**（1.21.1）。ただしサバイバルで遊べる内容や、サバイバルで sub-level を作る手段は追加しない、と書かれている。【一次】[S9]
- **Valkyrien Skies 2 は「ライブラリ」で、遊ぶにはアドオン（Eureka! など）が要る。** 浮力・衝突・Create 連携がある。公式は自らを BETA と書いている。公式リポジトリには 1.21.1 用のブランチがあるが、Modrinth での公式の配布は 1.20.1 まで。【一次】[S11][S12][S13]
- **Physics Mod（Haubna）は「クライアント側」だけで動く mod**（Modrinth の対応環境の表示）。ラグドール、ブロックの破砕、アイテムの物理、重力の変更がある。26.3 に対応（3.2.5）。ライセンスは ARR（All Rights Reserved）。【一次】[S15][S16]
- **mod を入れなくても、生物の重力は変えられる。** Java Edition 1.20.5 で `gravity` 属性（既定 0.08 ブロック/tick²）、`scale` 属性（大きさ）、`safe_fall_distance`・`fall_damage_multiplier` が入った。【一次】[S17][S18]【二次】[S20]
- **26.2（2026-06-16）で `bounciness`（反発）、`friction_modifier`（地面の摩擦）、`air_drag_modifier`（空気抵抗）の属性が入った。** 公式の開発者ノートには、属性で空気抵抗を取り除くとスライムブロックが生物を際限なく跳ねさせるようになった（訳）、という記述がある（原文「when air drag is removed via the entity attribute, Slime Blocks will now correctly bounce Mobs indefinitely」）。【一次】[S19]
- **惑星の重力がある Ad Astra は、惑星の重力の値を地球の値 9.807 で割った比を、バニラの 0.08 に掛ける。** 月は 1.622 なので、MC 内の重力は 0.08×1.622/9.807 ≈ 0.0132 ブロック/tick²（ソースコードの値からの計算）。【一次】[S26]
- **大きさを変える Pehkui は 2024-06-19 以降更新がなく、対応は 1.21.1 まで。** 生物の大きさは 1.20.5 以降バニラの `scale` 属性でも変えられる（0.0625〜16 倍）。【一次】[S29][S18]【二次】[S20]
- **Immersive Portals は、開発元のリポジトリの README の冒頭に「this repo is not being maintained now」とある**（メンテナンスの終了）。Modrinth の対応は 1.16.5〜1.21.1。【一次】[S30][S31]
- **水を有限にする Flowing Fluids は 26.3 対応で、サーバー側だけでも動く**（クライアントにも入れるのが推奨）。作者は「early development」と書いている。【一次】[S32]

## 詳細

### 調べ方

- Modrinth の各 mod のプロジェクトページ（本文、互換性、ライセンス）を読み、ページに埋め込まれたデータ（公開日・更新日・対応 MC バージョン・ローダー・ダウンロード数）と、最新の版のページ（版番号・公開日・対応 MC・ローダー・依存関係・変更履歴）を読んだ。取得はすべて 2026-11-19。
- ライセンス・仕組みは、GitHub のリポジトリのファイルを raw.githubusercontent.com で読んだ（README、LICENSE、gradle.properties、ソースコード）。
- 「最新」は、Modrinth のプロジェクトに登録された版のうち、末尾の数件を開いて確認したもの。古い MC バージョン向けにそれより新しい版がある可能性は残る。

### 一覧（2026-11-19 時点、Modrinth の表示）

| mod | 何をする | ローダー | 対応 MC（Modrinth） | 最新の版（公開日） | ライセンス（Modrinth の表示） | 確度・出典 |
|---|---|---|---|---|---|---|
| Create | 歯車・回転動力の機械、動く装置（contraption） | Forge, NeoForge | 1.18.2, 1.19.2, 1.20.1, 1.21.1 | 6.0.10（1.21.1・NeoForge、2026-04-21）／1.20.1 は 6.0.8（2025-11-02） | Create Mod License（コード MIT、素材 ARR） | 【一次】[S1][S2] |
| Create Fabric | Create の Fabric 移植 | Fabric, Quilt | 1.18.2, 1.19.2, 1.20.1 | 6.0.8.1（1.20.1、2025-12-02） | MIT | 【一次】[S4] |
| Create Fly | Create の非公式の Fabric フォーク | Fabric, Quilt | 1.21.8〜26.3 の一部 | 更新 2026-11-07 | CC0-1.0 | 【一次】[S6] |
| Create Aeronautics | Create を拡張して、乗り物・物理の装置を作る | NeoForge | 1.21.1 | 1.3.2（2026-08-29） | Simulated Project License（コード MIT、素材 ARR） | 【一次】[S7][S8] |
| Sable | 動くブロックの塊（sub-level）と物理（Rapier） | Fabric, NeoForge | 1.21.1 | 2.0.6（2026-10-03） | PolyForm Shield 1.0.0 | 【一次】[S9][S10] |
| Valkyrien Skies 2 | ブロックの船・乗り物に物理（ライブラリ） | Fabric, Forge | 1.12.2〜1.20.1 | 2.4.11（1.20.1、2026-04-10） | LGPL-3.0-only | 【一次】[S11] |
| Eureka! Ships | Valkyrien Skies のアドオン（船） | Fabric, Forge | 1.16.5〜1.20.1 | 1.6.4（1.20.1、2026-11-01） | Apache-2.0 | 【一次】[S13] |
| Physics Mod | ラグドール、ブロックの破砕、アイテムの物理（クライアント側） | Fabric, Forge, NeoForge, Quilt | 1.16.5〜26.3（26.4 スナップショットはベータ） | 3.2.5（26.3・Fabric、2026-09-17）／1.21.1 は 3.0.35（2026-11-04） | ARR | 【一次】[S15] |
| Ad Astra | 宇宙・惑星（月・火星など）、惑星ごとの重力 | Fabric, Forge, NeoForge | 1.18.2〜1.21.1 | 1.16.26（1.21.1、2026-09-13） | Terrarium Licence（コード MIT、それ以外 ARR） | 【一次】[S25][S27] |
| Galacticraft-Legacy | 宇宙 mod（旧版） | Forge | 1.12.2 | 更新 2023-12-09 | MIT | 【一次】[S28] |
| Gravity API（Fusion Flux） | プレイヤーの重力の向きを変える | Fabric, Quilt（本文は Quilt mod と説明） | 1.18.2〜1.20.1 | 更新 2023-08-24 | MIT | 【一次】[S21] |
| Gravity Changer（Gaider10） | 重力の向きを変える（元祖） | Fabric | 1.17.1, 1.18.1 | 更新 2021-12-19 | MIT | 【一次】[S22] |
| Amethyst Gravity | 重力の向きを変えるブロック等 | Fabric, Quilt | 1.19, 1.19.2 | 更新 2022-10-05 | CC0-1.0 | 【一次】[S24] |
| Pehkui | エンティティの大きさを変える | Fabric, Forge, NeoForge, Quilt | 1.14.4〜1.21.1 | 3.8.3（2024-06） | MIT | 【一次】[S29] |
| Immersive Portals | 覗けるポータル、非ユークリッド空間 | Fabric | 1.16.5〜1.21.1 | 5.2.0（1.20.1、2025-11-21）／v6.0.6（1.21.1、2024-11-29） | Apache-2.0 | 【一次】[S30] |
| Flowing Fluids | 有限の水・溶岩、流れの物理 | Fabric, Forge, NeoForge, Quilt | 〜26.3 | 1.0.8（26.3、2026-11-06） | LGPL-3.0-only | 【一次】[S32] |
| Create Big Cannons | Create の大砲 | Fabric, Forge, NeoForge, Quilt | 1.18.2〜1.21.1 | 更新 2026-06-22 | Create Big Cannons License（本文は未読） | 【一次】[S33] |

- 動画で使うときのライセンス上の条件（クレジットの要否など）は [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md) で扱う。この表はライセンスの名前だけ。
- 各 mod の MC バージョンごとの対応の一覧は [バージョン対応表.md](バージョン対応表.md)。

### Create

- Modrinth の Create は Forge と NeoForge 用で、対応は 1.18.2・1.19.2・1.20.1・1.21.1。ダウンロード数は 28,280,190（2026-11-19）。【一次】[S1]
  > 「This version of Create runs on Forge and NeoForge. Install one of these loaders before adding Create to your game.」[S1]
  > 「Alternatively, you can find a ported project compatible with the Fabric ecosystem here.」[S1]
- 最新は版の名前が `Create 6.0.10 for mc1.21.1` の版（版番号 `6.0.10+mc1.21.1`、NeoForge、2026-04-21）。1.20.1 向けの最新は `Create 6.0.8 for mc1.20.1`（版番号 `mc1.20.1-6.0.8`、Forge・NeoForge、2025-11-02）。【一次】[S1]
- GitHub の Create の既定ブランチの `gradle.properties` は `mod_version = 6.0.11`、`minecraft_version = 1.21.1`（2026-11-19 に読んだ時点。Modrinth には 6.0.11 はまだない）。26.x 用のブランチ名（`mc26.1/dev` など）を試したが見つからなかった。【一次】[S3]
- ライセンス（Modrinth の表示は「Create Mod License」）の中身は、`./src/main/resources/assets/` 以下が All Rights Reserved、それ以外のファイルが MIT。【一次】[S1][S2]
  > 「This license applies to any files under the following directories: - ./src/main/resources/assets/」[S2]
- Modrinth の説明は、対応バージョンと開発中の内容を専用の wiki ページで案内している（原文「Find out about supported versions and what's currently in the works in this dedicated wiki page.」）。GitHub の wiki の該当ページには、wiki.createmod.net に移った旨の一文だけがある。移転先のページは読めなかった。【一次】[S1][S3]
  > 「This section can now be found at https://wiki.createmod.net/users/development-status」[S3]

#### Create の Fabric 版

- Create Fabric（Fabricators of Create）は Fabric と Quilt 専用で、対応は 1.18.2・1.19.2・1.20.1。最新は版の名前が `6.0.8.1 for 1.20.1` の版（版番号 `6.0.8.1+build.1744-mc1.20.1`、2025-12-02）。この版の依存関係で Fabric API が必須。【一次】[S4]
  > 「This version of Create runs on Fabric and Quilt only.」[S4]
- Fabricators of Create のリポジトリには `mc1.21.1/fabric/dev` というブランチがある（中身の進み具合は未確認）。【一次】[S5]
- 非公式の Fabric フォーク『Create Fly』の Modrinth の対応は 1.21.8、1.21.10〜1.21.11、26.1.2、26.2、26.3。【一次】[S6]
- そのページには公式の Fabric 版について次のように書かれている（第三者の説明）。Fabric API をインストールしなくても Create の全機能を実装している、と作者が書いている（原文「This project implements the full Create feature independently, without the need to install the Fabric API.」）。【二次】[S6]
  > 「The official Create Fabric fork has not released a version 1.21.1 or higher. it has been a year since then.」[S6]
  > 「Please do not report issues with this mod to simibubi and NeoForge Create.」[S6]

### Create Aeronautics と Sable

- Create Aeronautics は Create を拡張して、飛行機・ドローン・熱気球・車などの乗り物と物理の装置を作れるようにする mod。NeoForge・1.21.1 専用。【一次】[S7]
  > 「Create Aeronautics expands on the systems of Create to enable players to build all types of vehicles and physics contraptions using Sable.」[S7]
  > 「You must have both Sable and Create installed to play Create Aeronautics.」[S7]
- 3つの部分からなる: Simulated（組み立て・レッドストーン部品・道具）、Aeronautics（熱気球・プロペラ・浮く岩）、Offroad（車輪で陸の乗り物）。【一次】[S7]
- 既知の非互換として Iris が挙げられている。【一次】[S7]
  > 「Aeronautics currently has visual issues when used with Iris Shaders.」[S7]
- Modrinth 上の最も古い版は 1.0.2（2026-04-17）、最新は 1.3.2（2026-08-29）。プロジェクトの作成日は 2026-02-07。ダウンロード数は 9,543,534（2026-11-19）。【一次】[S7]
- Modrinth のページに「Official nominee」「The Game Awards 2026」「Best User Creation」「Create Aeronautics is one of five nominees.」と表示されている（2026-11-19 に取得したページの表示。The Game Awards 側の発表は読んでいない）。【一次】[S7]
- ライセンス（Simulated Project License）は、3つの部分の `assets` 以下が All Rights Reserved、それ以外が MIT。【一次】[S8]
- Sable は「sub-level」（動くブロック・ブロックエンティティ・エンティティの塊）を追加するライブラリで、物理は Rust 製の Rapier を使う。Fabric と NeoForge の両方があり、1.21.1 のみ。【一次】[S9][S10]
  > 「Sable contains a physics pipeline (based on the Rapier physics engine written in Rust) that allows sub-levels to move with physics and react to changes in the world.」[S9]
  > 「Sable does not add any content to the survival game, or any manner of constructing sub-levels in survival.」[S9]
  > 「Use /sable to assemble, modify, and query sub-levels.」[S9]
  > 「Sable is an incredibly intrusive mod. It makes extensive use of mixins, and is prone to many compatibility issues with other mods.」[S9]

### Valkyrien Skies 2（と Eureka!）

- ブロックの塊を動かし、物理を与えるライブラリ mod。単体では遊べず、アドオン（Eureka! など）が要る。【一次】[S11]
  > 「Notice: Valkyrien Skies is a library mod, you need to download an add-on to use it in ordinary gameplay.」[S11]
  > 「If your ship is light enough, it floats!」[S11]
  > 「Ship to ship. Ship to world. Ship to player. Ship to entities.」[S11]
  > 「Oh, right. It also supports Create」[S11]
- 公式は BETA と書いている（原文のつづりのまま）。【一次】[S11]
  > 「Valkryien Skies 2 is in BETA.」[S11]
- Modrinth での対応は 1.12.2・1.16.5・1.18.2・1.19.2・1.20.1。最新は 2.4.11（Forge・Fabric とも 1.20.1、2026-04-10）。2.4.11 の変更履歴には「Atmospheric max has been changed from 1000 to 2000.」とあり、雲より上でプロペラ機が急に失速しにくくなる、と説明されている。【一次】[S11]
- 公式リポジトリには `1.21.1/main` ブランチがあり、`minecraft_version=1.21.1`、`enabled_platforms=fabric,neoforge`、`mod_version=2.4.12`。既定ブランチは `minecraft_version=1.20.1`。リリースされたかどうかは Modrinth では確認できない（Modrinth の公式プロジェクトに 1.21.1 の版はない）。【一次】[S11][S12]
- 第三者による非公式の移植「Valkyrien Skies [UNOFFICIAL] Port」（1.21.1・1.21.11・26.2）が Modrinth にあるが、プロジェクトの状態は archived。公式に不具合を報告しないよう書かれている。【一次】[S14]
  > 「Do NOT report any bugs or issues found in this version to the official Valkyrien Skies developers.」[S14]

### Physics Mod（Haubna）

- 生物のラグドール、ブロックの崩壊、アイテムの物理などを追加する mod。【一次】[S15]
  > 「Each Vanilla Minecraft mob supports ragdolls, fracturing and a blocky version!」[S15]
  > 「Gravity? Moon? Mars? Pluto? Earth? Change it to whatever you want!」[S15]
- Modrinth の「対応している環境」は「クライアント側」のみ（サーバー側は非対応）。【一次】[S15]
- 26.3 には 3.2.5 が出ている（Fabric/Quilt 2026-09-17、NeoForge 2026-09-17、Forge 2026-09-20）。26.4 のスナップショット向けはベータ。1.21.1 向けは 3.0.35（2026-11-04）。ライセンスは ARR。ダウンロード数は 24,763,263（2026-11-19）。【一次】[S15]
- GitHub の README の Credits に、PhysX の Java ラッパー（fabmax の physx-jni）を作った fabmax への謝辞がある。物理の計算にそれをどう使っているかは README には書かれていない。【一次】[S16]
  > 「Special thanks to **fabmax** for creating the PhysX JNI wrapper:」[S16]
- README には「Physics Mod Pro v170」「Physics Mod Pro v188」という版の名前が出てくる（シェーダー開発者向けの海の描画の説明）。Pro が有料かどうか・入手方法・無料版との違いは README には書かれていない（下の『わかっていないこと・要確認』の節へ）。【一次】[S16]

### 重力を変える: バニラの属性（mod なし）

属性（attribute）は、プレイヤー・生物・防具立ての数値の性質を決める仕組み。コマンド `/attribute` で変えられる。【二次】[S20]
> 「Attributes control certain numeric properties of players, mobs, and armor stands.」[S20]（wikitext のリンク記法を外した）

| 属性 | 追加された版（Java） | 範囲・既定値 | 中身 | 確度・出典 |
|---|---|---|---|---|
| `gravity` | 1.20.5（スナップショット 24w06a） | 既定 0.08、-1〜1 | 下向きの加速度（ブロック/tick²） | 【一次】[S17]【二次】[S20] |
| `safe_fall_distance` / `fall_damage_multiplier` | 1.20.5（24w06a） | — | 落下ダメージが始まる距離／落下ダメージの倍率 | 【一次】[S17] |
| `jump_strength`（全エンティティへ） | 1.20.5（24w06a） | — | 馬専用だったものを改名して全エンティティに | 【一次】[S17] |
| `scale` | 1.20.5（23w51a） | 既定 1、0.0625〜16 | 大きさと当たり判定を掛ける | 【一次】[S18]【二次】[S20] |
| `bounciness` | 26.2 | 既定 0、0〜1 | ブロック等にぶつかったあとに戻る速度の割合 | 【一次】[S19] |
| `friction_modifier` | 26.2 | 既定 1、0〜2048 | 乗っているブロックから受ける地面の摩擦の倍率 | 【一次】[S19] |
| `air_drag_modifier` | 26.2 | 既定 1、0〜2048 | 空中で受ける抵抗の倍率 | 【一次】[S19] |

> 「Added generic.gravity attribute that controls blocks/tick^2 acceleration downward」[S17]
> 「Added generic.scale attribute that can be used to rescale any living entity」[S18]
> 「Determines what portion of the velocity is restituted after the entity collides with blocks and collidable entities」[S19]（bounciness）
> 「Default value: 0.0 - no velocity is restituted」「Maximum value: 1.0 - full velocity is restituted, collisions with blocks and collidable entities will have no effect on lowering the velocity」[S19]
> 「Determines how much ground friction is applied to the entity in regard to the block it is on」[S19]（friction_modifier）
> 「Determines how much drag is applied to an entity while in the air」「Minimum value: 0.0 - no drag is applied to the entity」[S19]（air_drag_modifier）
> 「Developer's Note: We have tweaked how Beds and Slime Blocks restitute entity velocity after collisions. For instance, when air drag is removed via the entity attribute, Slime Blocks will now correctly bounce Mobs indefinitely.」[S19]

- 1.21.2 で属性名の接頭辞（`generic.` など）がなくなった（例: `generic.gravity` → `gravity`）。【二次】[S20]
- minecraft.wiki の説明では、`air_drag_modifier` を掛けたあとの空気抵抗は 1 −（1 − friction）×（属性値）で計算され、0〜1 に収められる（原文「clamped to 0 to 1」）。表の基準の値（Base value）は、オウム・ハチ・ブロックを持ったスルファーキューブが 0.91、ほかの生物が 0.98。【二次】[S20]
- 26.2 では同時に、ベッドが少し跳ねやすくなり（統合版に合わせた）、エンティティがブロック等で跳ね返ると周波数 2 の振動を出すようになった。【一次】[S19]
- 重力と空気抵抗の物理そのもの（式と値）は [../mechanics/重力と空気抵抗.md](../mechanics/重力と空気抵抗.md)、摩擦は [../mechanics/摩擦と滑りやすさ.md](../mechanics/摩擦と滑りやすさ.md) で扱う。

### 重力の向きを変える mod

- 系譜: Gaider10 の Gravity Changer → Fusion Flux の Gravity API（そのフォーク）→ qouteall のフォーク（Gravity API のフォーク）。qouteall は Immersive Portals のためにフォークを保守していると書いている。【一次】[S23]
  > 「Maintaining the fork because Immersive Portals mod depends on the Gravity changing mod, and Fabric mod cannot depend on a Quilt mod.」[S23]
  > 「By default, all living entities, projectiles and minecarts can change gravity.」[S23]
- qouteall のフォークのコマンドには、重力の向き（`/gravity set_base_direction`）と強さ（`/gravity set_base_strength`）、ディメンション単位の強さ（`/gravity set_dimension_gravity_strength`）がある。リポジトリの既定ブランチの `gradle.properties` は `mod_version = 1.3.0`、`minecraft_version=1.20.4`。配布先は確認できていない。【一次】[S23]
- Fusion Flux の Gravity API は、プレイヤーの重力を6方向に変える Quilt mod（QSL が必須）。Modrinth の対応は 1.20.1 まで、最終更新 2023-08-24。【一次】[S21]
  > 「This is a quilt mod and api that lets you change player gravity direction.」[S21]
- Gaider10 の Gravity Changer は 1.17.1・1.18.1 のみ（最終更新 2021-12-19）。Amethyst Gravity は 1.19・1.19.2 のみ（最終更新 2022-10-05）。【一次】[S22][S24]

### 惑星の重力がある mod

- Ad Astra は月・火星・金星・水星・Glacio の5つの天体、ロケット、宇宙服などを追加する。【一次】[S25]
- 惑星の重力の値は、定数のファイル（`PlanetConstants.java`）で地球 9.807、月 1.622、火星 3.72076、金星 8.87、水星 3.7、Glacio 3.721、宇宙（`SPACE_GRAVITY`）0.0。月のデータファイル（`planets/moon.json`）にも `"gravity": 1.622` とある。単位はコードに書かれていない（定数のファイルのコメントに、出典として windows2universe.org の惑星の表の URL がある）。【一次】[S26]
- 重力の計算は、惑星の値を地球の値（`EARTH_GRAVITY` = 9.807）で割った比を求め（`GravityApiImpl.java`）、生物の移動処理（`travel`）の最初で、縦の速度に `0.08 − 0.08×比` を足す形（`LivingEntityMixin.java`）。つまりバニラの重力 0.08 に比を掛けたものになる。比が `ZERO_GRAVITY_THRESHOLD`（0.05）以下だと無重力の処理に切り替わる。水中・溶岩中・エリトラ・低速落下のときは手を加えない。飛行中のプレイヤーも対象外。落下ダメージも比で変わる。比の計算は 1.20.x ブランチと既定ブランチ（`version=1.16.26`、`minecraftVersion=1.21.1`）で同じ式。`travel` の処理は既定ブランチのものだけ読んだ。【一次】[S26]
  > `return Optionull.mapOrDefault(PlanetApi.API.getPlanet(level), Planet::gravity, PlanetConstants.EARTH_GRAVITY) / PlanetConstants.EARTH_GRAVITY;` [S26]
  > `float newGravity = 0.08f * gravity;` [S26]
- 上の値からの計算（1ブロック=1 m、1秒=20 tick とし、Ad Astra の値を m/s² とみなす）: 月の比は 1.622/9.807 ≈ 0.165、MC 内の重力は ≈ 0.0132 ブロック/tick² ≈ 5.3 m/s²。Ad Astra 自身の月の値（1.622）の約3.3倍で、MC の地上（0.08 ブロック/tick² = 32 m/s²）と地球の値 9.807 の比（約3.3倍）と同じ。（計算。出典の値: [S26]）
- Ad Astra のライセンス（Terrarium License v1）は、ソースコード・`resources/data` 以下などの「Code」が MIT、それ以外が All Rights Reserved（読んだのは 1.19 ブランチの LICENSE）。【一次】[S27]
- Galacticraft は、Modrinth で見つかったのは Forge 1.12.2 用の「Galacticraft-Legacy」だけ（最終更新 2023-12-09）。新しい版の Galacticraft の状況は調べきれていない。【一次】[S28]

### 大きさを変える mod（Pehkui）とバニラの `scale`

- Pehkui はほとんどのエンティティの大きさを変える mod と API。`/scale` コマンドで、幅・高さ・当たり判定・目の高さなどを別々に変えられる。【一次】[S29]
  > 「This mod allows for most entities to have their size changed, either enlarging or shrinking them.」[S29]
  > 「The Quilt/Fabric version is the actively supported version and will receive features, updates, and fixes first.」[S29]
- 最新は 3.8.3（2024-06）。Fabric/Quilt 版は 1.14.4〜1.21 で使える1つの jar。プロジェクトの最終更新は 2024-06-19。【一次】[S29]
- バニラの `scale` 属性（1.20.5〜）は生物に対して、大きさと当たり判定を 0.0625〜16 倍にする。【一次】[S18]【二次】[S20] Pehkui のように幅と高さを別々に変える機能はバニラの属性の説明には書かれていない。

### Immersive Portals

- 覗き込めるポータルと、ロード画面なしの移動。回転・拡大縮小で非ユークリッドな空間を作れる（原文「Portals can "fold" space and create uneuclidian geometry with rotation and scale transformations.」）。鏡、ディメンションの積み重ね、世界の折り返しもある。【一次】[S30]
- README（既定ブランチ）の冒頭に、メンテナンスを止めた旨がある。ポータルはプレイヤーの大きさと重力の向きを変えられる、とも書かれている。【一次】[S31]
  > 「Update: this repo is not being maintained now. Forks are welcomed.」[S31]
  > 「The portal can transform player scale and gravity direction.」[S31]
- Modrinth の対応は 1.16.5〜1.21.1。最新の登録は 5.2.0（1.20.1、2025-11-21）、1.21.1 向けは v6.0.6（2024-11-29）。Fabric 専用。【一次】[S30]

### 流体の mod（Flowing Fluids）

- 水・溶岩をほぼ有限（原文「mostly finite」）にし、坂を流れ下って溜まるようにする。海・川・沼は無限の水源として振る舞うが、補充の速さに上限がある。ピストンでポンプにできる。シェーダーと両立するように通常の流体の描画を使う。【一次】[S32]
  > 「Flowing fluids is a mod adding more realistic fluid physics to the game, making fluids mostly finite, and adding an element of fluid management to the game.」[S32]
  > 「This mod works best when on both server and client side. However, it is only required on the server side」[S32]
  > 「⚠ The mod is currently in early development ⚠」[S32]
- 設定は `/flowing_fluids settings` で変えられ、`/flowing_fluids settings enable_mod on|off` で無効にもできる。Create の水車・パイプとの連携設定がある。【一次】[S32]
- 26.3 向けの 1.0.8 が Fabric/Quilt と NeoForge で出ている（2026-11-06）。【一次】[S32]
- バニラの流体の仕様は [../mechanics/流体.md](../mechanics/流体.md) で扱う。

## このチャンネルでの使い方（提案）

> ※この節は上の事実から導いた提案で、事実ではない。

- **T17『もしMCの重力が現実と同じだったら（自作mod）』は、mod を作らずにバニラの属性で撮れる可能性が高い。** 1ブロック=1 m、1秒=20 tick なら、現実の 9.8 m/s² は 9.807/400 ≈ 0.0245 ブロック/tick²。`/attribute <target> <attribute> base set <value>` の書式（minecraft.wiki）で `/attribute @e[type=minecraft:pig] minecraft:gravity base set 0.0245` のように設定して落とせば比べられる。ただし属性は生物などにしか効かないので、アイテムや金床（落下するブロック）は対象外になるはず。空気抵抗（0.98）は残るので、26.2 以降なら `air_drag_modifier` も合わせて調整する。実際の効き方は E001 と同じ方法で【実測】してから動画にする。（根拠: [S17][S19][S20][S36]）
- **T14『Createで永久機関は作れるか（エネルギー保存則）』の前に、バニラだけで、跳ね続けるスライムブロックを検証する回が作れる。** 公式の開発者ノートが、属性で空気抵抗を取り除くとスライムブロックが生物を際限なく跳ねさせる、と書いている（26.2〜、原文は詳細の節の引用）。エネルギー保存則（反発係数1・抵抗0）の説明にそのまま使える題材。`bounciness` を0〜1で変えて跳ね返りの高さを測れば、反発係数の実験にもなる。（根拠: [S19]）
- **T04（摩擦）と T03（終端速度）に、26.2 の `friction_modifier` と `air_drag_modifier` を、条件を変える実験として足せる。** 氷の上で摩擦の属性を0にする、空気抵抗を0にして終端速度がなくなるのを見せる、など。（根拠: [S19][S20]）
- **仮題『月面で落とすとどうなる？』は、Ad Astra を使っても現実の月の重力にはならない点がネタになる。** Ad Astra の月の重力は MC の地上の 0.165 倍で、1ブロック=1 m として現実の単位に直すと約 5.3 m/s²（Ad Astra 自身の月の値 1.622 の約3.3倍）。T01『MCの重力は地球の何倍？』の続編として、MC の月も月の値の3倍以上になる、と言える可能性がある。数値は必ず【実測】で確かめる。（根拠: [S26]）
- **mod を使う回の別インスタンスは、どの mod を使うかで MC バージョンとローダーが決まる。** Create＋Valkyrien Skies なら 1.20.1（Fabric でも Forge でも可）、Create Aeronautics なら 1.21.1 の NeoForge。基盤（26.3・Fabric）とは別に立てる。詳しい組み合わせは [バージョン対応表.md](バージョン対応表.md) の提案の節。（根拠: [S1][S4][S7][S11]）
- **Physics Mod は「見た目の物理」として扱い、計測には使わない。** Modrinth の表示ではクライアント側だけの mod なので、サーバーで計測する値（`data get entity` の Pos・Motion）にその物理が反映されるとは考えにくい。使うならオチや演出の映像に限る。反映されるかどうかは確かめていないので、使う前に【実測】する。（根拠: [S15]）
- **T11（ニュートンのゆりかご）・T12（フーコーの振り子）は、Sable（1.21.1・Fabric 版あり）の `/sable` でブロックの塊を作れるかを先に試す。** Create なしで済めば、Fabric の 1.21.1 で Flashback（録画）と同じインスタンスにできる。Sable の物理（Rapier）がどこまで現実的かは未確認なので、試作で確かめる。（根拠: [S9][S10]、Flashback の対応は [バージョン対応表.md](バージョン対応表.md)）
- **T06・T18（水）は、バニラの流体と Flowing Fluids の「有限の水」を比べる構成にできる。** Flowing Fluids は 26.3 対応で、基盤と同じバージョンで使える。ただし作者が「early development」と書いているので、計測用の基盤には入れず、その回だけのインスタンスにする。（根拠: [S32]）
- **非公式の移植（Create Fly、Valkyrien Skies の非公式移植）は、公式の不具合報告先がないので、計測の結果を動画で断言する回には使わない。** 使う場合は、非公式の移植を使っていることを概要欄に書く。（根拠: [S6][S14]）

## わかっていないこと・要確認

- 新しい版の Galacticraft（Fabric 版など）があるか、あれば対応バージョン・惑星の重力の値。今回は Modrinth で `galacticraft` のプロジェクトが見つからず、検索の回数の上限に達したため調べきれていない。
- Create の公式の開発状況ページ（wiki.createmod.net/users/development-status）の中身。26.x への対応予定。読めなかった。
- Valkyrien Skies の 1.21.1 版の公式リリースの予定（リポジトリにブランチはあるが、公式サイト valkyrienskies.org は読めなかった）。
- Valkyrien Skies 2.4.11（1.20.1）が Create Fabric 6.0.8.1 と一緒に動くか。
- Physics Mod の重力の設定が、バニラのエンティティ（サーバー側で計算される動き）に影響するか。
- Physics Mod Pro が有料かどうか、入手方法（Patreon など）と無料版との機能の違い。検索の要約（検索要約のみ・原文未読）にはそれらしい記述があったが、要約同士が食い違い、minecraftphysicsmod.com は読めなかった。【未確認】[S34]
- Valkyrien Skies の、ほかの非公式の 1.21.1 移植（NeoForge 版・Fabric 版）。検索の要約（検索要約のみ・原文未読）では複数あるとされるが、CurseForge のページは読めなかった。【未確認】[S35]
- Ad Astra の重力がアイテム・落下するブロック・投射物にも効くか（生物の処理しか読んでいない）。
- バニラの `gravity` 属性がアイテム・落下するブロック・TNT・投射物に効かないことの直接の確認（minecraft.wiki の「players, mobs, and armor stands」という説明からの推定にとどまる）。→ 【実測】で確認する。
- `friction_modifier` の正確な計算式（minecraft.wiki でも「info needed」）。
- qouteall の GravityChanger の配布先と最新の対応バージョン。
- Create Fly の品質（検索結果の題名に「[AI slop] Create Fly」という CurseForge のページがあったが、Cloudflare で読めず中身は不明）。
- Sable 単体（Create なし）で、どこまで物理の実験装置を作れるか。Flashback で sub-level を録画できるか。

## 参照先

- [S1] Create - Minecraft Mod（プロジェクトページと版のページ /version/UjX6dr61, /version/8amzvn9x） — Modrinth（simibubi ほか Creators of Create） — https://modrinth.com/mod/create — 更新 2026-04-21 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] LICENSE.md（Create） — Creators of Create — https://raw.githubusercontent.com/Creators-of-Create/Create/HEAD/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Create の gradle.properties（既定ブランチ）と GitHub wiki の dev.status の移転の一文 — Creators of Create — https://raw.githubusercontent.com/Creators-of-Create/Create/HEAD/gradle.properties ／ https://raw.githubusercontent.com/wiki/Creators-of-Create/Create/dev.status.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Create Fabric（プロジェクトページと /version/HAqwA6X1） — Modrinth（Fabricators of Create） — https://modrinth.com/mod/create-fabric — 更新 2025-12-02 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Fabricators-of-Create/Create のブランチ mc1.21.1/fabric/dev の gradle.properties — Fabricators of Create — https://raw.githubusercontent.com/Fabricators-of-Create/Create/mc1.21.1/fabric/dev/gradle.properties — 不明 — 取得: 2026-11-19 — 原文: 読んだ（ファイルが存在することのみ確認。版の記載はなかった）
- [S6] Create Fly — Modrinth（ZurrTum） — https://modrinth.com/mod/create-fly — 公開 2025-09-13、更新 2026-11-07 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Create Aeronautics（プロジェクトページと /version/44pLdPGg, /version/HY8u0JqC） — Modrinth（Creators of Aeronautics） — https://modrinth.com/mod/create-aeronautics — 作成 2026-02-07、更新 2026-08-29 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] LICENSE.md（Simulated Project） — Creators of Aeronautics — https://raw.githubusercontent.com/Creators-of-Aeronautics/Simulated-Project/main/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Sable（プロジェクトページと /version/OLG7vDD6） — Modrinth（RyanHCode） — https://modrinth.com/mod/sable — 公開 2025-07-23、更新 2026-10-03 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] Sable README.md と開発者 wiki（Home） — RyanHCode — https://raw.githubusercontent.com/ryanhcode/sable/main/README.md ／ https://raw.githubusercontent.com/wiki/ryanhcode/sable/Home.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Valkyrien Skies（プロジェクトページと /version/qJr3y5vI, /version/pOkdwuUh） — Modrinth（Valkyrien Skies） — https://modrinth.com/mod/valkyrien-skies ／ https://modrinth.com/mod/valkyrien-skies/version/qJr3y5vI — 更新 2026-04-10 — 取得: 2026-11-19 — 原文: 読んだ
- [S12] Valkyrien-Skies-2 の gradle.properties（既定ブランチと 1.21.1/main）と README — Valkyrien Skies — https://raw.githubusercontent.com/ValkyrienSkies/Valkyrien-Skies-2/1.21.1/main/gradle.properties ／ https://raw.githubusercontent.com/ValkyrienSkies/Valkyrien-Skies-2/HEAD/gradle.properties — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S13] Eureka! Ships! for Valkyrien Skies — Modrinth（Valkyrien Skies） — https://modrinth.com/mod/eureka — 更新 2026-11-01 — 取得: 2026-11-19 — 原文: 読んだ
- [S14] Valkyrien Skies [UNOFFICIAL] Port — Modrinth（第三者） — https://modrinth.com/mod/GE25t0ct — 公開 2026-05-27、更新 2026-08-24 — 取得: 2026-11-19 — 原文: 読んだ
- [S15] Physics Mod（プロジェクトページと /version/6losOHhe, /version/iVnZdLtE ほか） — Modrinth（Haubna） — https://modrinth.com/mod/physicsmod — 更新 2026-11-18 — 取得: 2026-11-19 — 原文: 読んだ
- [S16] PhysicsMod README.md — Haubna — https://raw.githubusercontent.com/haubna/PhysicsMod/main/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S17] Minecraft Snapshot 24w06a — Mojang（Java Team） — https://www.minecraft.net/en-us/article/minecraft-snapshot-24w06a — 2024-02-07 — 取得: 2026-11-19 — 原文: 読んだ
- [S18] Minecraft Snapshot 23w51b（URL は 23w51a） — Mojang（Java Team） — https://www.minecraft.net/en-us/article/minecraft-snapshot-23w51a — 2023-12-18 — 取得: 2026-11-19 — 原文: 読んだ
- [S19] Minecraft Java Edition 26.2 — Mojang（Java Team） — https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2 — 2026-06-16 — 取得: 2026-11-19 — 原文: 読んだ
- [S20] Attribute — Minecraft Wiki — https://minecraft.wiki/w/Attribute（`?action=raw` で読んだ） — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S21] Gravity API — Modrinth（Fusion Flux） — https://modrinth.com/mod/gravity-api — 更新 2023-08-24 — 取得: 2026-11-19 — 原文: 読んだ
- [S22] Gravity Changer — Modrinth（Gaider10） — https://modrinth.com/mod/gravitychanger — 更新 2021-12-19 — 取得: 2026-11-19 — 原文: 読んだ（プロジェクトのデータのみ）
- [S23] GravityChanger README.md・gradle.properties・LICENSE — qouteall — https://raw.githubusercontent.com/qouteall/GravityChanger/master/README.md ／ https://raw.githubusercontent.com/qouteall/GravityChanger/master/gradle.properties — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S24] Amethyst Gravity — Modrinth（CyborgCabbage） — https://modrinth.com/mod/amethyst-gravity — 更新 2022-10-05 — 取得: 2026-11-19 — 原文: 読んだ（プロジェクトのデータのみ）
- [S25] Ad Astra（プロジェクトページと /version/R1Zh2VaO, /version/18wLDrwY） — Modrinth（Terrarium） — https://modrinth.com/mod/ad-astra — 更新 2026-09-13 — 取得: 2026-11-19 — 原文: 読んだ
- [S26] Ad Astra のソースコードとデータ（既定ブランチの LivingEntityMixin.java・PlanetConstants.java・GravityApiImpl.java・gradle.properties・planets/moon.json、1.20.x ブランチの GravityApiImpl.java） — Terrarium — https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/HEAD/src/main/java/earth/terrarium/adastra/mixins/common/LivingEntityMixin.java ／ https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/HEAD/src/main/java/earth/terrarium/adastra/common/constants/PlanetConstants.java ／ https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/HEAD/src/main/java/earth/terrarium/adastra/common/systems/GravityApiImpl.java ／ https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/HEAD/gradle.properties ／ https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/HEAD/src/main/generated/resources/data/ad_astra/planets/moon.json ／ https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/1.20.x/common/src/main/java/earth/terrarium/adastra/common/systems/GravityApiImpl.java — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S27] Terrarium License v1（Ad Astra の LICENSE） — Terrarium — https://raw.githubusercontent.com/terrarium-earth/Ad-Astra/1.19/LICENSE — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S28] Galacticraft-Legacy — Modrinth（Team Galacticraft） — https://modrinth.com/mod/galacticraft-legacy — 更新 2023-12-09 — 取得: 2026-11-19 — 原文: 読んだ（プロジェクトのデータのみ）
- [S29] Pehkui（プロジェクトページと版のページ） — Modrinth（Virtuoel） — https://modrinth.com/mod/pehkui — 更新 2024-06-19 — 取得: 2026-11-19 — 原文: 読んだ
- [S30] Immersive Portals（プロジェクトページと版のページ） — Modrinth（qouteall） — https://modrinth.com/mod/immersiveportals — 更新 2025-11-21 — 取得: 2026-11-19 — 原文: 読んだ
- [S31] ImmersivePortalsMod README.md（既定ブランチ） — qouteall — https://raw.githubusercontent.com/qouteall/ImmersivePortalsMod/HEAD/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S32] Flowing Fluids（プロジェクトページと /version/C8nuLuR3） — Modrinth（Traben） — https://modrinth.com/mod/flowing-fluids — 更新 2026-11-06 — 取得: 2026-11-19 — 原文: 読んだ
- [S33] Create Big Cannons — Modrinth（Cannoneers of Create） — https://modrinth.com/mod/create-big-cannons — 更新 2026-06-22 — 取得: 2026-11-19 — 原文: 読んだ（プロジェクトのデータのみ。ライセンス本文は未読）
- [S34] Web 検索「Physics Mod Haubna Pro vs free features ragdoll block physics Patreon client side only」の結果の要約（minecraftphysicsmod.com/pro、texture-packs.com、sportskeeda.com、feed-the-mods.com などの要約） — 各サイト — https://minecraftphysicsmod.com/pro ほか — 不明 — 取得: 2026-11-19 — 原文: 検索要約のみ
- [S35] Web 検索「Valkyrien Skies 2 1.21.1 port release」の結果の要約（CurseForge の VS Unofficial Neoforge Port ほか） — 各サイト — https://www.curseforge.com/minecraft/mc-mods/vs-unofficial-neoforge-port ほか — 不明 — 取得: 2026-11-19 — 原文: 検索要約のみ
- [S36] Commands/attribute — Minecraft Wiki — https://minecraft.wiki/w/Commands/attribute（`?action=raw` で読んだ） — 不明 — 取得: 2026-11-19 — 原文: 読んだ
