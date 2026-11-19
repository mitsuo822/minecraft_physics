# シェーダーと画質mod

> 対象: Java版の画質を上げる mod（Sodium、Iris、Distant Horizons）と、動画でよく使われるシェーダーパック（Complementary Reimagined / Unbound、BSL、Photon、Bliss、SEUS PTGI）の機能・対応バージョン・互換性・負荷。ライセンスの詳細と録画 mod 本体の機能は別ファイル。
> 使う場面: 撮影用インスタンスの mod 構成を決めるとき。回ごとにシェーダーを選ぶとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition のみ（統合版は対象外）。Modrinth の互換性表示は 2026-11-19 取得時点のもので、最新は 26.3（2026年からの新しい番号体系。26.1.x → 26.2 → 26.3）。数値（ダウンロード数など）もすべて 2026-11-19 取得時点。
> 関連: [録画設定.md](録画設定.md), [ReplayMod.md](ReplayMod.md), [Flashback.md](Flashback.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../mods/バージョン対応表.md](../mods/バージョン対応表.md)

## 要点
- Sodium は描画エンジンを置き換える最適化 mod。Fabric / NeoForge / Quilt 向けで、対応環境の表示はクライアント側。Modrinth の表示で 1.16.3〜26.3 に対応、ライセンスは Polyform Shield 1.0.0。【一次】[S1]
- Iris は OptiFine 用のシェーダーパックと互換を目指すシェーダーローダー。公式サイトは Sodium を同梱すると説明し、Fabric は 1.16.5 以上、NeoForge は 1.21.1 以上に対応、Forge は非対応。ライセンスは LGPL-3.0-only。【一次】[S2][S3]
- Iris 公式 FAQ は、OptiFine・Canvas・Vulkan 系 mod とは非互換でクラッシュすると明記している。Distant Horizons と Voxy は、それらへの対応を明示したシェーダーパックとだけ併用できる。【一次】[S3]
- MC 本体の描画 API: 26.2 で OpenGL と Vulkan を選べるようになり、開発中の 26.4 では設定 Default が Prefer Vulkan と同じ動作になる（minecraft.wiki の記述）。Iris が本体の Vulkan 描画で動くかは確認できていない（末尾の節（わかっていないこと・要確認）を参照）。【二次】[S10]
- Distant Horizons（DH）は、256 チャンク以上（ページの表記は「extreme (256+)」）の描画距離を低い負荷で出すとうたう mod。Iris でシェーダーと併用できるのは DH 2.1.0 以上・Iris 1.7 以上・DH 対応を組み込んだシェーダーの3つがそろう組み合わせだけで、DH 2.0 以前は Iris と動かない。OptiFine では forward rendering のシェーダーで一部だけ動く。【一次】[S4]
- Complementary には Reimagined（バニラの見た目を活かす）と Unbound（よりリアル寄り）の2スタイルがあり、違いは既定の設定だけ。Potato〜Ultra のプロファイルがある。ライセンス表示は Custom。【一次】[S5][S6]
- BSL は明るくカラフルな作風を掲げ（原文「It's bright, colorful, and distinct.」）、被写界深度・モーションブラー・セルシェーディング・地平線の湾曲などの効果を持つ。ページの AGREEMENT でスクリーンショットと動画への使用を許可している。ライセンス表示は ARR。【一次】[S7]
- Photon は半リアル調。ブルーム・被写界深度・モーションブラーのカメラ効果と TAA / FXAA / CAS を持ち、対応 mod として Voxy と Distant Horizons を挙げる。Apple GPU（Metal）には非対応。【一次】[S8]
- Bliss は Chocapic13 の V9 系を大きく改変したファンタジー調のパック。Iris が必要（OptiFine でも動くかもしれない、と作者）、1.17 以上向け。ライセンス表示は ARR。【一次】[S9]
- Replay Mod の公式 docs は、1.16.5 以上で Iris を fully supported とする一方、Sodium 入りでレンダリングするには Replay Mod 側が配布する改造版 Sodium が要ると書いている（docs の更新日は不明）。【一次】[S11]
- バニラの Fabulous! はノートPC と 4K 画面で性能に大きく響く可能性がある、と wiki は記す。RTX 4070 Ti SUPER でのシェーダー別・プロファイル別の fps の資料は見つからなかった。【二次】[S10]

## 詳細

### Sodium（描画の最適化）
- 説明文は「A high-performance rendering engine replacement for Minecraft, which greatly improves frame rates and reduces micro-stutter.」（訳: フレームレートを大きく上げ、細かいカクつきを減らす描画エンジンの置き換え）。【一次】[S1]
- 互換性の表示（2026-11-19）: 26.3、26.2、26.1.x、1.21.x、1.20.x、1.19.x、1.18.x、1.17.x、1.16.3–1.16.5。プラットフォームは Fabric / NeoForge / Quilt、対応している環境はクライアント側。【一次】[S1]
- ダウンロード 254.2M、フォロワー 42.9K、「6 年前 に公開」「先週 に更新」と表示（2026-11-19 取得）。ライセンス Polyform Shield 1.0.0。【一次】[S1]
- 作者は Fabric を勧めている: 「we recommend using Fabric Loader for the most simple and lightweight experience」【一次】[S1]
- 設定は基本的に変えなくてよい、と説明している: 「By default, Sodium will enable all optimizations which are supported on your system」（訳: 既定で、そのシステムで使えるすべての最適化が有効になる）。【一次】[S1]
- Sodium が最適化するのは描画だけ: 「By design, Sodium only optimizes the rendering code of Minecraft.」。それ以外は Lithium（MC 1.15 以上）などの別 mod を勧めている。【一次】[S1]
- 公式サポートは OpenGL 4.5 以上に対応したドライバのデスクトップ GPU: 「We only provide official support for desktop graphics cards which have up-to-date drivers compatible with OpenGL 4.5 or newer.」。NVIDIA は GeForce 400 Series（Fermi）以降が例に挙がっている。【一次】[S1]
- 不具合の多くは古いドライバが原因だとしている: 「Out-of-date graphics drivers are often the reason for most crashes, rendering bugs, and performance issues.」【一次】[S1]

### Iris（シェーダーローダー）
- 説明文は「A modern shader pack loader for Minecraft intended to be compatible with existing OptiFine shader packs」。【一次】[S2]
- 互換性の表示（2026-11-19）: 26.3、26.2、26.1.x、1.21.x、1.20.x、1.19.x、1.18.x、1.17.x、1.16.5。Modrinth 上のプラットフォーム表示は Fabric / NeoForge / Quilt、クライアント側。ダウンロード 196.1M、「2 か月前 に更新」。ライセンス LGPL-3.0-only。【一次】[S2]
- 公式サイトの説明: 「Compatible with OptiFine shader packs, as well as Iris-enhanced packs.」「Iris ships with Sodium for optimized rendering out of the box.」（訳: Iris は Sodium と一緒に配布され、最初から最適化された描画になる）。【一次】[S3]
- 対応ローダー: 「Iris supports Fabric on 1.16.5 and higher, and NeoForge on 1.21.1 and higher. Forge is not supported.」【一次】[S3]
- 他の描画系 mod との相性（公式 FAQ）:
  - 「Optifine, Canvas, or Vulkan mods: Incompatible, and will crash the game.」【一次】[S3]
  - 「Voxy and Distant Horizons: Compatible with *some* shader packs. Shader packs must explicitly support them.」【一次】[S3]
  - 「Nvidium: Will disable itself with shaders enabled, but can be installed with Iris.」【一次】[S3]
- リソースパックとの相性: 「Resource packs that use "core shaders" (shaders that do not require mods) will not work with a shader pack enabled.」（訳: mod 不要の「コアシェーダー」を使うリソースパックは、シェーダーパック有効時には動かない）。【一次】[S3]
- Modrinth のページは、非対応のシェーダーパックの一覧と、直せない制限の一覧を別ページで公開していると案内している（その一覧は未読）。【一次】[S2]

### 本体の Vulkan 化と Iris
- minecraft.wiki の Options の履歴: 26.2（snap1）で「Added the ability to choose between OpenGL and Vulkan in the video settings.」。【二次】[S10]
- 設定「Graphics API」の選択肢は Default / Prefer OpenGL / Prefer Vulkan (experimental)。wiki の注記では、Default は 26.4 より前は OpenGL、26.4（開発中）からは Vulkan を使う。【二次】[S10]
- 26.4 の開発版の履歴: snap1 で Default が Prefer Vulkan と同じ動作になり、snap7 で Default が起動ごとに OpenGL と Vulkan のどちらかをランダムに選ぶ挙動になり、snap9 で「"Graphics API" Video Setting: "Default" now behaves the same as "Prefer Vulkan" again.」。【二次】[S10]
- Iris の公式資料（[S2][S3]）には、本体の Vulkan 描画への対応についての記述は見当たらなかった。Iris の FAQ が非互換とする「Vulkan mods」が本体の Vulkan 描画を含むかは書かれていない。検索要約の内容は末尾の節（わかっていないこと・要確認）に置いた。【一次】[S2][S3]

### Distant Horizons（遠景の LOD）
- 説明文は「Massively increase render distance without harming performance.」、本文は「Distant Horizons allows you to achieve extreme (256+) chunk render distances at a low performance cost.」。【一次】[S4]
- 掲載写真の条件: 「This photo was taken with a Minecraft render distance of 8 and a mod distance of 512.」（訳: MC の描画距離 8、mod の描画距離 512 で撮影）。【一次】[S4]
- 互換性の表示（2026-11-19）: 26.3、26.2、26.1.x、1.21.3–1.21.11、1.21–1.21.1、1.20.6、1.20.4、1.20–1.20.2、1.19.x、1.18.x、1.17.x、1.16.3–1.16.5、1.12.2。表示上、1.21.2、1.20.5、1.20.3 は入っていない。プラットフォームは Fabric / Forge / NeoForge、クライアント・サーバーどちらにも入る。【一次】[S4]
- 1 つの jar の中身: 1.20.6 以降は NeoForge と Fabric、1.20.4 以前は Forge と Fabric が同じ jar に入っている。【一次】[S4]
- シェーダーとの互換（FAQ）: 「Optifine: DH partially works with forward rendered shaders.」「Iris (and equivalent ports): DH 2.1.0+ only works with Iris 1.7+ and only with shaders built with DH support in mind.」「DH 2.0 and older don't work with Iris.」【一次】[S4]
- 描画の API: 「Distant Horizons uses OpenGL or Vulkan for graphics rendering.」【一次】[S4]
- プレイヤーが建てた構造物も LOD に出る（FAQ の答えは Yes）。クライアントだけに入れた場合も LOD はセッションをまたいで保存されるが、一度その場所を探索する必要がある。サーバーにも入れると、Distant Generation を有効にした接続者へ LOD が自動で送られる。【一次】[S4]
- カクつくときの対処（FAQ）: Java 21 以上なら ZGC などの並行 GC を使う、割り当て RAM を増やす（4〜8 コアの CPU は 6〜8 GB、10 コア以上は 12〜16 GB）、DH の CPU 負荷を下げる、Distant Generation を切る、DH の Graphics Preset を下げる。【一次】[S4]
- ダウンロード 38.2M、ライセンス LGPL-3.0-only。【一次】[S4]

### シェーダーパックの比較表
表の値はすべて各パックの Modrinth ページ（2026-11-19 取得）。「表示タグ」は Modrinth のページに出ているタグのうち負荷・用途に関わるものをそのまま写した（タグの意味の定義は未確認）。

| パック | 作風（ページの説明） | ローダー | 対応版の表示 | ライセンス表示 | DL数 | 表示タグ（負荷関連） | 確度・出典 |
|---|---|---|---|---|---|---|---|
| Complementary Reimagined | 「Preserving the elements of Minecraft with exceptional quality, detail, and performance.」 | Iris / OptiFine | 1.7.10〜26.3 | Custom | 73.3M | 高負荷・軽量・標準・低負荷 | 【一次】[S5] |
| Complementary Unbound | 「Transforming the visuals of Minecraft with exceptional quality, detail, and performance.」 | Iris / OptiFine | 1.7.x〜26.3 | Custom | 47.8M | 高負荷・軽量・標準・低負荷 | 【一次】[S6] |
| BSL | 「It's bright, colorful, and distinct.」 | Iris / OptiFine | 1.7.10〜26.3 | ARR | 32.1M | 軽量 | 【一次】[S7] |
| Photon | 「A gameplay-focused shader pack with a semi-realistic style」 | Iris / OptiFine | 1.16.5〜26.3 | 空欄 | 29.5M | 高負荷・軽量・標準 | 【一次】[S8] |
| Bliss | 「A well performing fantasy styled shaderpack with emphasis on scene variation and customization.」 | Iris / OptiFine | 1.17.x〜26.3 | ARR | 15.9M | 標準・高負荷・軽量・スクリーンショット | 【一次】[S9] |

### Complementary（Reimagined / Unbound）
- 全体の説明: 「It offers a ton of high quality effects, two default visual style choices, custom effects for almost every block in the game, profiles ranging from Potato to Ultra and it's designed to never be obstructive during gameplay.」【一次】[S5]
- 来歴: 「It started as an edit of BSL Shaders in 2018」【一次】[S5]
- 2スタイルの違い: 「The only difference between these two styles is the default settings.」「The Unbound style is designed for people looking for a more realistic experience, while the Reimagined style is made to reimagine Minecraft while preserving its unique visual elements.」。Unbound でブロック状の雲にする、Reimagined でリアルな水にする、といった変更は Shader Options でできる。【一次】[S5][S6]
- 導入: Iris を入れ、ゲーム内の Shaderpacks メニューから shaderpacks フォルダを開き、zip のまま置く（「Please don't unzip the file」）。自動で入れる Complementary Installer もある。【一次】[S5]
- 更新: 両ページとも「17 時間前 に更新」と表示（2026-11-19 取得）。【一次】[S5][S6]

### BSL
- 効果: 「This shader includes realtime shadows, volumetric light, ambient occlusion, bloom, customizable clouds and water, and built in anti-aliasing.」「Additional effects are available, such as depth of field, motion blur, specular and normal mapping, celshading, world curvature, and more.」【一次】[S7]
- 利用条件（ページの AGREEMENT）: 許可として「Use this shaderpack for taking screenshots and videos.」、禁止として「Redistribute the shaderpack without my permission.」などを挙げる。詳しい扱いは [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md)。【一次】[S7]
- 導入は OptiFine か Iris を入れて .minecraft\shaderpacks に置く。【一次】[S7]

### Photon
- 機能（ページの Features から抜粋）: 「Camera effects: bloom, depth of field, motion blur」「Much improved image quality with TAA, FXAA and CAS」「Voxel-based colored lighting (enabled with Ultra profile, requires Iris)」「Advanced temporal upscaling (disabled by default) for low end devices」。ほかに雲の層、天候、スクリーンスペース反射、ボリュメトリックフォグ、GTAO。【一次】[S8]
- ローダー: Iris を推奨し、色つきの光は Iris でだけ動く。OptiFine も可。【一次】[S8]
- GPU: Nvidia / AMD / Intel に対応、「NOT compatible with Apple GPUs (Metal)」。【一次】[S8]
- 対応 mod として Voxy と Distant Horizons を挙げる。【一次】[S8]
- MC のバージョンへの依存について作者は「Shader packs are generally not very dependent on MC versions; as long as Iris is available, Photon should just work.」と書いている。【一次】[S8]
- ライセンス欄はページ上で空欄だった。【一次】[S8]

### Bliss
- 来歴: 「Bliss is a big edit of Chocapic13's V9.0 - V9.1」【一次】[S9]
- 要件: 「The mod "Iris". The mod "Optifine" might work as well.」「Designed for Minecraft versions 1.17.0+」。AMD / Intel / NVidia に対応し、Apple 製品は OpenGL の版の制約で対応が限られる。【一次】[S9]
- 「昨年 に更新」と表示（2026-11-19 取得）。【一次】[S9]

### SEUS PTGI
- Modrinth・CurseForge の公式ページは今回見つけられず、読めた資料は検索要約だけ。確認できた事実はない。検索要約の内容は末尾の節（わかっていないこと・要確認）に置いた。

### 負荷について出典で言えること
- バニラの Fabulous!（1.16 で追加、1.21.11 からはグラフィックのプリセットの1つ。wiki の履歴）: 「This may severely impact performance for portable devices (e.g. laptops) and 4K displays.」【二次】[S10]
- 描画距離: 「The fewer chunks that are included, the faster each frame can be rendered」【二次】[S10]
- Complementary は Potato〜Ultra のプロファイル、Photon は低性能機向けの時間方向のアップスケーリング（既定は無効）を用意している。【一次】[S5][S8]
- DH は「low performance cost」をうたうが、カクつき対策として RAM・GC・CPU 負荷の設定を FAQ に挙げている（上記）。【一次】[S4]
- Sodium のページの性能比較は内蔵 GPU（Intel Xe Graphics）の PC で測ったものと明記している。RTX 4070 Ti SUPER のような GPU での数値は、今回読めた資料にはない。【一次】[S1]

### 録画 mod との組み合わせ（概要だけ。詳細は録画 mod のファイル）
- Replay Mod の docs: 「On Minecraft 1.16.5 and up you can use Iris, which is fully supported. For the time being, you will have to use it with the custom Sodium provided on our download page.」【一次】[S11]
- 同じく: 「ReplayMod can record when Sodium is installed, but currently lacks the FREX Flawless Frames API to render.」（訳: Sodium 入りでも録画はできるが、レンダリングに要る FREX Flawless Frames API がない）。改造版 Sodium は Replay Mod のダウンロードページから入手する、としている。【一次】[S11]
- Flashback との互換は [Flashback.md](Flashback.md)、Replay Mod の詳細は [ReplayMod.md](ReplayMod.md) を見る。

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- 撮影用クライアントは Fabric + Sodium + Iris を基本にする。Sodium と Iris はクライアント側の mod なので、計測用のサーバには入れない。（根拠: [S1][S2][S3]）
- MC 26.2 以降を使うなら、Graphics API を「Prefer OpenGL」に固定してから Iris の動作を確かめる。Vulkan での Iris の動作は未確認なので、MC のバージョンを上げる前に毎回確認する。（根拠: [S3][S10][S12]）
- 物理の計測を見せるショットは、シェーダーなし、または効果を減らしたプロファイルで撮る。モーションブラー・被写界深度・TAA があると、動いている物体の位置が画面上で読みにくくなるおそれがあるので、効果のオン・オフを同じショットで撮り比べて決める（撮り比べた結果は【実測】として残す）。（根拠: [S7][S8]）
- 遠景が要る回（大規模な爆発、長距離の投射物など）だけ Distant Horizons を入れる。シェーダーと併用するなら、DH への対応を明記している Photon を第一候補にする。（根拠: [S3][S4][S8]）
- シェーダーの選択は、作風（Reimagined＝バニラ寄り、Unbound / Photon＝リアル寄り、BSL＝明るくカラフル）とライセンスの両方で決める。動画での使用の許可が明文で読めるのは今回 BSL だけなので、他は利用条件のファイルで確認してから使う。（根拠: [S5][S6][S7][S8][S9]）
- Replay Mod でシェーダー付きの書き出しをするなら、Replay Mod 配布の改造版 Sodium が今も必要かを、使う MC バージョンで最初に確かめる。（根拠: [S11]）
- 自宅 PC（RTX 4070 Ti SUPER）で、シェーダー×プロファイル×描画距離ごとの fps を一度測り、`knowledge/` に【実測】として残す。（根拠: [S1][S10]）

## わかっていないこと・要確認
- Iris が MC 本体の Vulkan 描画（26.2 で選択可、26.4 で既定化の予定）で動くか、対応の予定と時期。検索要約（原文未読）では、26.2 の Iris の公式ビルドは OpenGL でだけ動き Vulkan を有効にするとシェーダーが切れる、後継の Aperture という mod が開発中、とされていた。出典は非公式のモッドパックのページで、Iris 公式の発表は読めていない。【未確認】[S12]
- Complementary と Bliss の Distant Horizons 対応（Modrinth のページには書かれていなかった）。
- SEUS PTGI の現在の配布先、対応バージョン、Iris での動作、ライセンス。検索要約（原文未読）では、OptiFine 上で動くソフトウェアのパストレーシングとして作られ RTX カードは不要だが高性能な GPU が要る、ビルドごとに必要な OptiFine の版が違う、Iris で動くとする配布サイトもあるが出典同士で食い違う、配布は作者の Patreon の投稿、とされていた。【未確認】[S13]
- Modrinth のタグ「軽量」「低負荷」「標準」「高負荷」「スクリーンショット」の定義と、誰が付けるか。
- Photon のライセンス（Modrinth のライセンス欄が空欄）。
- Replay Mod の docs の更新日。改造版 Sodium が 2026-11 時点でも必要か。
- 各シェーダーの録画時の負荷（RTX 4070 Ti SUPER、1080p / 4K、OBS の NVENC 同時使用時）。
- Iris の非対応シェーダー一覧・制限一覧の中身（未読）。

## 参照先
- [S1] Sodium - Minecraft Mod — Modrinth — https://modrinth.com/mod/sodium — 更新: 「先週 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] Iris Shaders - Minecraft Mod — Modrinth — https://modrinth.com/mod/iris — 更新: 「2 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Iris Shaders（公式サイト、FAQ） — IrisShaders — https://irisshaders.dev/ — 更新日不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Distant Horizons - Minecraft Mod — Modrinth — https://modrinth.com/mod/distanthorizons — 更新: 「2 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Complementary Shaders - Reimagined - Minecraft Shader — Modrinth — https://modrinth.com/shader/complementary-reimagined — 更新: 「17 時間前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Complementary Shaders - Unbound - Minecraft Shader — Modrinth — https://modrinth.com/shader/complementary-unbound — 更新: 「17 時間前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] BSL Shaders - Minecraft Shader — Modrinth — https://modrinth.com/shader/bsl-shaders — 更新: 「2 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] Photon Shaders - Minecraft Shader — Modrinth — https://modrinth.com/shader/photon-shader — 更新: 「先月 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Bliss Shaders - Minecraft Shader — Modrinth — https://modrinth.com/shader/bliss-shader — 更新: 「昨年 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] Options（wikitext） — Minecraft Wiki — https://minecraft.wiki/w/Options?action=raw — 更新日不明（26.4 開発版 snap9 までの履歴を含む） — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Replay Mod Documentation — Replay Mod — https://www.replaymod.com/docs — 更新日不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S12] 検索「Iris shaders Vulkan Minecraft 26.2 support」の要約（主な結果: Distant Horizons & Iris Shaders モッドパックのファイルページ） — CurseForge ほか — https://www.curseforge.com/minecraft/modpacks/distant-horizons-iris-shaders/files/8299382 — 不明 — 取得: 2026-11-19 — 原文: 検索要約のみ
- [S13] 検索「SEUS PTGI path tracing shader requirements Iris OptiFine」の要約（主な結果: texture-packs.com の SEUS PTGI ページ、作者の Patreon 投稿） — https://texture-packs.com/shaders/seus-ptgi ／ https://www.patreon.com/posts/seus-ptgi-e6-25937144 — 不明 — 取得: 2026-11-19 — 原文: 検索要約のみ
