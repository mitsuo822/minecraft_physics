# Fabricのmod開発（26.x）

> 対象: Minecraft 26.x 向けの Fabric mod 開発の前提（難読化のない本体、Fabric Loom、Java 25、Mixin）、クライアント側の描画のフックとカメラ、/tick freeze 中の描画、録画との連携、既存 mod のコードを流用するときの注意。
> 使う場面: [MC実行基盤.md](../../docs/MC実行基盤.md) §4 の全自動撮影（自作のクライアント mod）を作り始める前と、P2 の半自動・全自動の比較の前。
> 調査日: 2026-11-20 ／ mc_version: Java Edition 26.1〜26.3（Fabric Docs の移植ガイドは取得時点で 26.2→26.3 を扱っている）。統合版（Bedrock）は対象外。
> 関連: [バージョン対応表.md](バージョン対応表.md), [Carpet.md](Carpet.md), [../filming/Flashback.md](../filming/Flashback.md), [../filming/ReplayMod.md](../filming/ReplayMod.md), [../filming/時間制御とスロー.md](../filming/時間制御とスロー.md), [../filming/カメラワーク技法.md](../filming/カメラワーク技法.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md)

## 要点
- Java Edition 26.1（2026-03-24 リリース）は、難読化された版を併せて出さない最初のリリースで、Java 25 を必要とする最初の版でもある 【二次】[S11]。Mojang は 2025-10-29 に難読化の廃止を告知した 【一次】[S10]。
- Fabric の告知では、1.21.11 以前の mod は少なくとも再コンパイルしないと 26.1 では動かず、Yarn マッピングは Fabric の公式サポートから外れた 【一次】[S1]。
- 26.x の mod は新しい Gradle プラグイン `net.fabricmc.fabric-loom` を使う。このプラグインは本体も mod もリマップしない。`modImplementation` は `implementation`、`remapJar` は `jar` に置き換える 【一次】[S1]。
- Gradle を動かす JVM は Java 25 以上が必要。IntelliJ IDEA で Mixin を正しく扱うには 2025.3 以上が必要 【一次】[S1]。公式のテンプレート（26.3 ブランチ）は `options.release = 25` と Java 25 互換を指定している 【一次】[S5]。
- 推奨の版は時期で変わる。26.3 の告知（2026-09-15）は Loom 1.17・Gradle 9.6.0・Loader 0.19.5 を挙げたが、2026-11-20 取得時のテンプレートは Loader 0.20.1・Loom 1.19-SNAPSHOT・Fabric API 0.166.2+26.3 を指定していた 【一次】[S3][S6]。
- 26.x の描画は、データを集める extraction と描画する drawing の2段階に分かれる方向で作り直されている。Fabric API のイベントは `LevelExtractionEvents` と `LevelRenderEvents`（パッケージ `...rendering.v1.level`）で、drawing の段階では不変の render state しか触れない 【一次】[S7][S8]。
- Fabric API がすべての描画フックを用意しているわけではない。26.3 の公式ドキュメントの例でも、描画パスを得るために `LevelRenderer` への Mixin（MixinExtras の `@WrapOperation`）を使っている 【一次】[S7][S9]。
- 26.1 は OpenGL だけに対応する最後の版になる見込みとされ、26.2 で Vulkan の実験的なバックエンドに切り替えられるようになった。生の OpenGL 呼び出しを使う mod は Blaze3D の API に移行する必要がある 【一次】[S1][S2]。
- 26.3 ではウィンドウとキー入力のライブラリが GLFW から SDL に替わり、マウスボタンなどの定数も変わった。入力は `InputConstants` を通す 【一次】[S3]。
- `/tick freeze` はプレイヤーと、プレイヤーが乗っているエンティティ以外のゲーム要素を止める。止めたままプレイヤーは自由に動いて世界を見られる 【一次】[S13]【二次】[S12]。ただし、止めている間のクライアント側の描画（補間）がどう動くかを書いた資料は見つからなかった。
- カメラを動かす既存の mod は、ライセンスがばらばら。Flashback は ARR、Replay Mod は GPL-3.0-or-later、CMDCam は LGPL-2.1-only、Free Camera は MIT（いずれも Modrinth の表示、2026-11-20 取得）【一次】[S14][S15][S16][S17]。
- CMDCam はサーバのコマンドでプレイヤーにカメラパスをたどらせられるが、Modrinth の表示では Forge と NeoForge だけで Fabric 版はない 【一次】[S16]。

## 詳細

### 1. 難読化のない本体（26.1 から）
- Mojang の告知（2025-10-29）は、Mounts of Mayhem の後の最初のスナップショットから Java Edition を難読化しないこと、クライアントとサーバの .jar を難読化しないこと、各 .jar に LICENSE ファイルを入れることを予告した 【一次】[S10]。
  > 「This means that this build (and all future builds) will have all of our original names」[S10]
  （訳）その版（と以後のすべての版）には、こちらの元の名前がすべて入る。
- 同じ告知は、移行の準備のために、難読化した版と並べて難読化しない実験版を出すとした 【一次】[S10]。
- 難読化をやめても EULA と利用ガイドラインは変わらず、mod にも適用されると書かれている 【一次】[S10]。
  > 「these changes don’t affect our Minecraft End User License Agreement and Minecraft Usage Guidelines. Both still apply to Minecraft: Java Edition and any mods」[S10]
  （訳）この変更は EULA と利用ガイドラインには影響しない。どちらも Java Edition とあらゆる mod に引き続き適用される。動画での扱いは [../rights/](../rights/) の各ファイルを参照。
- minecraft.wiki によると、26.1 は年.ドロップ.修正 の新しい版番号を使う最初のリリースで、2026-03-24 に出た 【二次】[S11]。
  > 「to be fully unobfuscated without an accompanying obfuscated variant」[S11]
- 同じページの技術的な変更の欄に「The game now requires Java 25.」とある 【二次】[S11]。
- Fabric の 26.1 告知（2026-03-14）は、26.1 を難読化されない最初の版とし、旧版の mod はそのままでは動かないと書いた 【一次】[S1]。
  > 「no mods from 1.21.11 or before will work without, at a minimum, recompilation.」[S1]
  > 「as Yarn is no longer officially supported by Fabric」[S1]
- Fabric API の名前も Yarn 由来から公式名に合わせて変わった。例として `ItemGroupEvents` は `CreativeModeTabEvents` になった。後方互換はない 【一次】[S1]。
- Fabric は逆コンパイルしたソースをブラウザで読む『mcsrc.dev』を作った。Mojang のサーバから本体の jar を落とし、WASM にした Vineflower で逆コンパイルする仕組みで、Mixin と AccessWidener/ClassTweaker を書く補助もある 【一次】[S1]。
  > 「mcsrc.dev also provides tools to aid with creating mixins and AccessWideners/ClassTweakers」[S1]

### 2. ビルドの道具: Fabric Loom・Gradle・Java 25
- 26.1 告知の推奨は Loom 1.15・Gradle 9.4.0・Loader 0.18.4（告知時点）【一次】[S1]。26.2 告知（2026-06-15）は Loom 1.17・Gradle 9.5.1・Loader 0.19.3 【一次】[S2]。26.3 告知（2026-09-15）は Loom 1.17・Gradle 9.6.0・Loader 0.19.5 【一次】[S3]。
- 26.x では旧プラグイン（`net.fabricmc.fabric-loom-remap` または `fabric-loom`）から新プラグイン `net.fabricmc.fabric-loom` に切り替える 【一次】[S1]。
  > 「which does not remap Minecraft or mods」[S1]
  > 「Any use of `modImplementation`, `modCompileOnly`, or similar should be switched out for the standard `implementation` or `compileOnly`」[S1]
- Java の要件と IDE の要件 【一次】[S1]。
  > 「Minecraft 26.1 requires Java 25 minimum for the Gradle JVM」[S1]
  > 「if you are using IntelliJ IDEA, version 2025.3 or above is required for mixins to work correctly」[S1]
- 公式テンプレート（fabric-example-mod の 26.3 ブランチ、2026-11-20 取得）の build.gradle の要点 【一次】[S5]。
  - プラグインは `id 'net.fabricmc.fabric-loom' version "${loom_version}"`。
  - `loom { splitEnvironmentSourceSets() }` で、共通（main）とクライアント（client）のソースセットを分けている。
  - Fabric Loader と Fabric API は `implementation` で依存に入れる。Fabric API には「This is technically optional, but you probably want it anyway.」と注記がある。
  - `it.options.release = 25`、`sourceCompatibility = JavaVersion.VERSION_25`。
- 同じテンプレートの gradle.properties（2026-11-20 取得）の値 【一次】[S6]。

| 項目 | 値 | 確度・出典 |
|---|---|---|
| minecraft_version | 26.3 | 【一次】[S6] |
| loader_version | 0.20.1 | 【一次】[S6] |
| loom_version | 1.19-SNAPSHOT | 【一次】[S6] |
| fabric_api_version | 0.166.2+26.3 | 【一次】[S6] |

- 26.3 告知の推奨（Loom 1.17・Loader 0.19.5）とテンプレートの値（Loom 1.19-SNAPSHOT・Loader 0.20.1）は違う。告知の値は「at the time of writing」と断ってあり、取得日の差によるもの 【一次】[S3][S6]。
- Fabric Docs の移植ガイド（取得時点で 26.2→26.3 を扱う）は、`./gradlew wrapper --gradle-version latest` で Gradle を上げ、推奨の版は Fabric Develop のサイトで確かめ、迷ったらテンプレートを参照するよう書いている 【一次】[S4]。
- 26.1 の初期リリースでは Fabric Model Loading API と Renderer/Indigo のモジュールが使えないかもしれないと告知された 【一次】[S1]。現在の状態は未確認（下の要確認の節）。
- Fabric API は `fabric` という mod ID を提供しなくなった。`fabric.mod.json` の依存は `fabric-api` と書く 【一次】[S1]。

### 3. 描画のフック（26.3 時点）
- Fabric Docs『Rendering in the World』によると、最近の版は描画を extraction（準備）と drawing（描画）の2段階に分けようとしている。描画に要るデータは extraction で集め、drawing ではバッファを画面に描く 【一次】[S7]。
  > 「allow for drawing the previous frame in parallel to extracting the next frame」[S7]
  （訳）前のフレームの描画と次のフレームの extraction を並行して行えるようにする（性能のため）。
- 同ページの例のコードでは、`LevelExtractionEvents.END_EXTRACTION` で描くものを用意し、`LevelRenderEvents.BEFORE_RENDER_PASS` と `LevelRenderEvents.END_MAIN` で描画の準備と後始末をしている。パッケージは `net.fabricmc.fabric.api.client.rendering.v1.level` 【一次】[S8]。
  > 「You can only access the (immutable and thread safe) render state in the drawing phase.」[S8]
- 例のコードはカメラの位置を `context.levelState().cameraRenderState.pos` から読み、その分だけ座標をずらして箱を描いている。描画の座標はカメラ基準になる 【一次】[S8]。
- 26.3 では描画パスを Fabric API が渡してくれないため、ドキュメントの例は `LevelRenderer` に Mixin を当てて `draw` を呼んでいる。後始末にも `GameRenderer#close` への Mixin が要る 【一次】[S7]。
  > 「In 26.3, we use a mixin to call `draw`, since Fabric API does not provide the render pass.」[S7]
- その Mixin は MixinExtras の `@WrapOperation` で `LevelRenderer` の `executeClassicTransparency` 内の呼び出しを包み、元の処理の後に自分の描画を足している 【一次】[S9]。
- 26.3 の例のコードは、描画パスやパイプラインのクラスを `com.mojang.renderpearl.api` から import している 【一次】[S8][S9]。
- 画面に重ねる HUD は、26.1 で非推奨の `HudRenderCallback` が削除され `HudElementRegistry` に置き換わった 【一次】[S1]。
  > 「the deprecated `HudRenderCallback` event has been removed in favour of `HudElementRegistry`」[S1]
- 26.1 以前の名前（`WorldRenderEvents` など）から `LevelRenderEvents` への改名は、Fabric Docs の 26.1 向け Fabric API 移植ガイドに対応表がある（独語版・中国語版の検索要約のみ・原文未読）【未確認】[S18]。
- Vulkan への移行: 26.1 告知は、26.1 が OpenGL だけに対応する最後の版になる見込みとし、26.2 告知は OpenGL（既定）と実験的な Vulkan を切り替えられるようになったと書く。OpenGL は Vulkan が安定したら外す予定 【一次】[S1][S2]。
  > 「Developers making use of raw OpenGL calls rather than going through the Blaze3D API will need to migrate for their mods to work.」[S1][S2]
- 26.3 の告知は、技術的な変更が主に描画に集中していると書く 【一次】[S3]。版を上げるたびに描画まわりのコードは直す前提になる。

### 4. 入力（キー操作）
- 26.3 でウィンドウとキー割り当ての管理に使っていた GLFW が外れ、SDL に替わった 【一次】[S3]。
  > 「The GLFW library used for window and keybind management has been removed in favour of SDL.」[S3]
- `GLFW` の定数を直接使っていた mod が主に影響を受け、マウスボタンを含む一部の定数の値が変わった 【一次】[S3]。
  > 「do not attempt to hardcode your inputs to avoid using `InputConstants`」[S3]

### 5. /tick freeze 中の動き（mod から見て）
- `/tick` は 23w43a（2023-10-25 公開のスナップショット、Java Edition 1.20.3 の開発版）で追加された管理・デバッグ用のコマンドで、既定ではコマンドブロックやデータパックからは使えない権限レベル 【一次】[S13]。
- freeze はプレイヤーと、プレイヤーが乗っているエンティティ以外を止める 【一次】[S13]【二次】[S12]。
  > 「allowing the player to move around freely and inspect the world」[S13]
  > 「Freezes ticking. All gameplay elements are not ticked, except players and any」[S12]
- tick の速さを 20 より上げると、プレイヤーは 20 tick/秒のまま動き、エンティティの補間に乱れが出ることがあるとされた 【一次】[S13]。
  > 「but can cause artifacts in entities interpolation」[S13]
- 26.3 の開発版（snap1）で、`/tick step`・`/tick step stop`・`/tick sprint stop` が失敗時にメッセージを出すだけでなくエラーを返すように変わった 【二次】[S12]。
  > 「will now signal an error instead of just printing an error message」[S12]
  `lab/runner.py` が戻り値で成否を見ているなら、26.3 で挙動が変わる。
- freeze 中にクライアントがエンティティをどう描くか（補間を止めるか、最後の位置で止まるか）を書いた一次資料・Wiki は見つからなかった。/tick の詳しい仕様は [../filming/時間制御とスロー.md](../filming/時間制御とスロー.md)。

### 6. 録画との連携と、カメラを動かす既存の mod
Modrinth の各ページの表示（2026-11-20 取得）。対応版・ライセンスは更新で変わる。

| mod | 対応する Java Edition | ローダー | 動く側 | ライセンス | 確度・出典 |
|---|---|---|---|---|---|
| Flashback | 26.3, 26.2, 26.1.x, 1.21.4–1.21.11, 1.21–1.21.1 | Fabric | クライアント | ARR | 【一次】[S14] |
| ReplayMod | 26.3, 26.2, 26.1.x, 1.21.x 〜 1.8 | Fabric, Forge | クライアント | GPL-3.0-or-later | 【一次】[S15] |
| CMDCam | 26.3, 26.2, 26.1.2, 26.1, 1.21.8–1.21.11 ほか | Forge, NeoForge | クライアント／クライアントとサーバ | LGPL-2.1-only | 【一次】[S16] |
| Free Camera | 26.2, 26.1.x, 1.21.4, 1.21.1, 1.20.1–1.20.4 | Fabric, Forge, NeoForge | クライアント | MIT | 【一次】[S17] |

- Flashback は Modrinth でソースへのリンクを出しているが、ライセンス欄は「ライセンス ARR」と表示される 【一次】[S14]。ダウンロード数は 13.1M（2026-11-20 取得）【一次】[S14]。
- Replay Mod は動画を書き出す機能を内蔵し、カメラパスを GUI で作る 【一次】[S15]。
  > 「Coming with a built-in video creator, the Replay Mod allows everyone to make perfect clips without any external software.」[S15]
- CMDCam は滑らかなカメラパス（ズーム・ロール・対象の追尾・補間の種類の切り替え）を作る mod で、録画は別の道具で行う 【一次】[S16]。
  > 「Just keep in mind that you need an external tool to record it.」[S16]
- CMDCam はサーバにも入れられ、パスをサーバに保存し、コマンドでプレイヤーにパスをたどらせられる。`/cam-server start <path> <players>` で指定したプレイヤーのアニメーションを始める 【一次】[S16]。
  > 「Make a player follow a path by using a command.」[S16]
  > 「starts the animation for the given players」[S16]
- CMDCam の補間は linear・cosine・cubic・hermite・circular から選べ、既定は hermite。距離に応じたタイミング（一定速度）の設定もある。前提 mod として CreativeCore が要る 【一次】[S16]。
- Free Camera 3.0.0 は完全にクライアント側で動き、実際のプレイヤーを動かさずにカメラを動かす。キーフレームのパスと、線形・Catmull-Rom の補間、カメラの動きの記録と再生がある 【一次】[S17]。
  > 「Linear and smooth Catmull-Rom interpolation」[S17]
  > 「Does not move your real player」[S17]
- Free Camera の記録とパスはローカルのファイル（`config/free-camera/recordings/` と `config/free-camera/paths/`）に保存される 【一次】[S17]。26.2 用は Fabric Loader 0.19.3+ と Fabric API 0.154.2+26.2 が必要で、Java 25 が要る 【一次】[S17]。取得時点で 26.3 は対応版に入っていない 【一次】[S17]。
- Flashback と Replay Mod のカメラパスや書き出しの詳細は [../filming/Flashback.md](../filming/Flashback.md) と [../filming/ReplayMod.md](../filming/ReplayMod.md)。

### 7. 既存 mod のコードを流用するとき
- 上の表のとおり、カメラ系の mod でもライセンスは ARR・GPL・LGPL・MIT と分かれている 【一次】[S14][S15][S16][S17]。ソースが公開されていることと、流用してよいことは別。各ライセンスの条件と動画での扱いは [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md) を参照。
- 自作 mod にも Minecraft の EULA と利用ガイドラインが適用される 【一次】[S10]。

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- 自作 mod は fabric-example-mod の基盤の版のブランチ（26.3 なら 26.3 ブランチ）を複製して始める。JDK 25 と IntelliJ IDEA 2025.3 以上を入れる。旧版向けの解説記事（Yarn 名、`modImplementation`、`remapJar` を使うもの）は 26.x では使えないので参考にしない。（根拠: [S1][S5][S6]）
- `gradle.properties` の4つの版（Minecraft・Loader・Loom・Fabric API）は、決めたら `mc/mods.yaml` に記録して固定する。推奨値は数か月で変わる。（根拠: [S1][S2][S3][S6]）
- 撮影用 mod はクライアント専用にし、テンプレートの client ソースセットに置く。サーバ側（計測）は Carpet と RCON のまま分ける。（根拠: [S5]、[Carpet.md](Carpet.md)）
- 作る前に P2 で既存の mod と比べる。Free Camera（MIT・キーフレームのパスをファイルに保存）が 26.3 に対応したら、`experiment.yaml` の `shots` からパスのファイルを生成できるかを最初に試す。できれば自作の量が大きく減る。CMDCam はサーバのコマンドでパスを再生できるので RCON から操作しやすいが、Fabric 版がないため基盤には入らない。（根拠: [S16][S17]）
- カメラの位置はフレームごとに補間して決め、tick（20/秒）ごとにしない。描画のコードは extraction と drawing の分け方に合わせ、生の OpenGL を呼ばない。軌跡の線などワールド内の描き足しは `LevelExtractionEvents`/`LevelRenderEvents`、計測値の表示は `HudElementRegistry` を使う。（根拠: [S1][S2][S7][S8]）
- カメラを動かすフック（どのクラスのどのメソッドに Mixin を当てるか）は、基盤の版の本体のソースを『mcsrc.dev』で読んで決め、版を上げたら必ず見直す。描画まわりは毎版変わる前提で、Mixin は MixinExtras の `@WrapOperation` のように元の処理を残す形を優先する。（根拠: [S1][S3][S9]）
- キー割り当ては `InputConstants` を通し、GLFW の定数を直書きしない。（根拠: [S3]）
- コマ撮り（全自動・発展）は、/tick freeze 中もプレイヤーは動けるので、原理的にはカメラだけ動かして撮れる見込みがある。ただし止まっている物体の描画（補間）の挙動が資料で確かめられないので、P2 で、freeze 中に動く物体が静止して描かれるかを最初に実測する。（根拠: [S12][S13]）
- 26.3 では `/tick step` の失敗がエラーとして返るので、`lab/runner.py` の成否判定を基盤の版で確かめる。（根拠: [S12]）
- 他の mod のコードは、ライセンスを確かめるまで写さない。特に Flashback は ARR 表示なので、コードを参考にするのは読むだけにとどめる。（根拠: [S14]、[../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md)）

## わかっていないこと・要確認
- 26.3 でカメラ（視点の位置・向き・FOV）を動かすのに Mixin を当てるべきクラスとメソッド。今回読めた資料には書かれていない。『mcsrc.dev』で本体のソースを読んで確かめる。
- `/tick freeze` 中のクライアント側の描画: 止まったエンティティが補間なしで描かれるか、frame の部分 tick がどう扱われるか。一次資料・Wiki とも記述なし。P2 で実測する。
- 自作 mod から1コマずつ画面を書き出す方法（スクリーンショットの API の使い方、描画の同期）。今回の資料にはない。
- Free Camera のパスのファイル形式と、26.3 への対応時期。CMDCam の Fabric 版（Modrinth の検索結果に `cmdcam-fabric` という別のプロジェクトがあるが未読）が 26.x に対応しているか。
- Flashback と Replay Mod に、外部からカメラパスを読み込ませる手段や API があるか（C5 の各ファイルと照らし合わせる）。
- 26.1 の初期リリースで使えないかもしれないとされた Fabric Model Loading API と Renderer/Indigo の、26.3 時点の状態。
- `WorldRenderEvents` から `LevelRenderEvents` への改名の詳細（英語の移植ガイドは未読。[S18] は検索要約のみ）。
- 26.3 ブランチのテンプレートが指定する Gradle の版（`gradle-wrapper.properties` は未読）。
- Vulkan のバックエンドを選んだときに、自作の描画やシェーダー mod（Iris）がどうなるか。画質の側は [../filming/](../filming/) の各ファイルで扱う。
- GPL・LGPL のコードを、配布しない自分用の mod に取り込む場合の条件。[../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md) で確かめる。

## 参照先
- [S1] Fabric for Minecraft 26.1 — FabricMC（fabricmc.net のブログの原稿） — https://raw.githubusercontent.com/FabricMC/fabricmc.net/main/_posts/2026-03-14-261.md （公開ページ: https://fabricmc.net/2026/03/14/261.html ） — 2026-03-14 — 取得: 2026-11-20 — 原文: 読んだ
- [S2] Fabric for Minecraft 26.2 — FabricMC — https://raw.githubusercontent.com/FabricMC/fabricmc.net/main/_posts/2026-06-15-262.md — 2026-06-15 — 取得: 2026-11-20 — 原文: 読んだ
- [S3] Fabric for Minecraft 26.3 — FabricMC — https://raw.githubusercontent.com/FabricMC/fabricmc.net/main/_posts/2026-09-15-263.md — 2026-09-15 — 取得: 2026-11-20 — 原文: 読んだ
- [S4] Porting to 26.3 — Fabric Docs（FabricMC/fabric-docs） — https://raw.githubusercontent.com/FabricMC/fabric-docs/main/develop/porting/index.md — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S5] fabric-example-mod build.gradle（26.3 ブランチ） — FabricMC — https://raw.githubusercontent.com/FabricMC/fabric-example-mod/26.3/build.gradle — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S6] fabric-example-mod gradle.properties（26.3 ブランチ） — FabricMC — https://raw.githubusercontent.com/FabricMC/fabric-example-mod/26.3/gradle.properties — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S7] Rendering in the World — Fabric Docs — https://raw.githubusercontent.com/FabricMC/fabric-docs/main/develop/rendering/world.md — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S8] CustomRenderPipeline.java（Fabric Docs の参照コード） — FabricMC — https://raw.githubusercontent.com/FabricMC/fabric-docs/main/reference/latest/src/client/java/com/example/docs/rendering/CustomRenderPipeline.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S9] LevelRendererMixin.java（Fabric Docs の参照コード） — FabricMC — https://raw.githubusercontent.com/FabricMC/fabric-docs/main/reference/latest/src/client/java/com/example/docs/mixin/client/LevelRendererMixin.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S10] Removing obfuscation in Java Edition — Mojang（minecraft.net） — https://www.minecraft.net/en-us/article/removing-obfuscation-in-java-edition — 2025-10-29 — 取得: 2026-11-20 — 原文: 読んだ
- [S11] Java Edition 26.1 — minecraft.wiki — https://minecraft.wiki/w/Java_Edition_26.1?action=raw — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S12] Commands/tick — minecraft.wiki — https://minecraft.wiki/w/Commands/tick?action=raw — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S13] Minecraft Snapshot 23w43a — Mojang（minecraft.net、Java Team） — https://www.minecraft.net/en-us/article/minecraft-snapshot-23w43a — 2023-10-25 — 取得: 2026-11-20 — 原文: 読んだ
- [S14] Flashback — Modrinth — https://modrinth.com/mod/flashback — 取得時の表示「2 か月前 に更新」 — 取得: 2026-11-20 — 原文: 読んだ
- [S15] ReplayMod — Modrinth — https://modrinth.com/mod/replaymod — 取得時の表示「先月 に更新」 — 取得: 2026-11-20 — 原文: 読んだ
- [S16] CMDCam — Modrinth — https://modrinth.com/mod/cmdcam — 取得時の表示「先月 に更新」 — 取得: 2026-11-20 — 原文: 読んだ
- [S17] Free Camera — Modrinth — https://modrinth.com/mod/free-camera — 取得時の表示「4 か月前 に更新」 — 取得: 2026-11-20 — 原文: 読んだ
- [S18] Fabric API 26.1 移植指南（Fabric Docs 中国語版。独語版も同様） — Fabric Docs — https://docs.fabricmc.net/zh_cn/develop/porting/26.1/fabric-api — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ
