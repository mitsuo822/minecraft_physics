# Flashback

> 対象: Flashback（作者 Moulberry）の録画・エディタ・キーフレームの種類・書き出しの機能、シェーダーと Sodium への対応、対応バージョン、ライセンス、Replay Mod との違い（出典のあるものだけ）。
> 使う場面: 撮影方式を決めるとき、Flashback で撮る回の撮影前の確認、書き出し設定を決めるとき、mod の構成（`mc/mods.yaml`）を決めるとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition。Modrinth の互換表示は 1.21〜26.3。ソースの master ブランチは mod 0.43.6・MC 26.3 向け（2026-11-19 取得）。統合版（Bedrock）には無い。
> 関連: [ReplayMod.md](ReplayMod.md), [時間制御とスロー.md](時間制御とスロー.md), [カメラワーク技法.md](カメラワーク技法.md), [縦型撮影.md](縦型撮影.md), [シェーダーと画質mod.md](シェーダーと画質mod.md), [録画設定.md](録画設定.md), [../mods/バージョン対応表.md](../mods/バージョン対応表.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md)

**この文書の根拠の読み方**: Flashback の公式の説明文は短く、機能の多くはソースの英語・日本語の UI 文字列（`lang/en_us.json`、`lang/ja_jp.json`、master ブランチ、2026-11-19 取得）から拾った。UI 文字列があることは「その機能がソースにある」ことの根拠で、配布中の各版に入っているかは版ごとに確かめる必要がある。

## 要点
- Flashback はゲームを録画し、再生し、映像用のショットを書き出す mod。Fabric のみ、クライアント側のみ。【一次】[S1][S2]
- 2026-11-19 時点の Modrinth の互換表示は Java Edition の 26.3、26.2、26.1.x、1.21.4–1.21.11、1.21–1.21.1。1.20 以前と 1.21.2〜1.21.3 は表示に無い。【一次】[S1]
- ライセンスは独自（Modrinth の表示は ARR）。再配布・再アップロードは禁止。翻訳ファイルだけ CC BY 4.0。外部からの貢献は受け付けていない。【一次】[S1][S2][S3]
- master ブランチの fabric.mod.json は Java 21 以上、Fabric API 0.107.0 以上を要求し、Iris 1.10.9 未満とは共存しない（breaks）。FREX Flawless Frames の連携の入口がある。【一次】[S5]
- キーフレームの種類は、カメラ、カメラ軌道（オービット）、FOV、速度、フリーズ、タイムラプス、時刻、手ブレ、エンティティ追跡、ブロック上書き、オーディオトラック。【一次】[S6]
- 補間の種類は Smooth、Linear、Ease In、Ease Out、Ease In/Out、Hold、Hermite の7つ。キーフレームごとに右クリックで変える。【一次】[S6]
- 0.40.0（MC 26.1.x 向け）で投影に「Orthographic」（平行投影）、「Cube Map」、「Equirectangular」が追加された。【一次】[S8][S6]
- 書き出しの画面に、コンテナ・エンコーダ・コーデック・ビットレート・フレームレート・解像度・SSAA・GUIなし・透明な空・深度マップ・開始／終了 tick・「Reset RNG」・音声の設定がある。書き出しのキュー（ジョブ）もある。【一次】[S6]
- 縦横比（Aspect）の選択肢の表示名に「9:16 (Shorts)」がある。構図のガイドとして重ねて表示するものか、書き出しの解像度も縦にするものかは、言語ファイルからは読み取れない。【一次】[S6]
- tick と乱数に関わる機能: 再生ヘッドを矢印キーで1tickずつ動かせる、同じ場面を何度書き出しても揃いやすくする「Reset RNG」、シングルプレイでクライアントと内蔵サーバを同じ歩調で進める「Synchronize Ticking」（20 TPS 未満で録るとき向け、デッドロックの恐れあり）。【一次】[S6]
- 日本語の UI では、補間の「Smooth」が「ベジェ」、「Reset RNG」の説明が「全く同じ出力を得やすくします」と訳されている。英語の原文の「Reset RNG」の説明は「Attempts to」（試みる）で始まり、完全な一致は約束していない。【一次】[S6][S7]
- 拡張する別の mod が Modrinth にある（書き出しのプリセット、全シーンの一括キュー、カメラパスの書き出し、出来事をきっかけにした自動録画など）。【一次】[S12][S13][S14][S15][S16]

## 詳細

### 基本情報

| 項目 | 内容 | 確度 | 出典 |
|---|---|---|---|
| 作者 | Moulberry | 【一次】 | [S2][S5] |
| 説明 | ゲームを録画し、再生し、映像用のショットを作る | 【一次】 | [S1][S2] |
| ローダー | Fabric のみ（Modrinth の表示、README の導入手順） | 【一次】 | [S1][S2] |
| 動作環境 | クライアント側（fabric.mod.json の environment は client） | 【一次】 | [S1][S5] |
| ライセンス | Modrinth の表示は ARR。LICENSE.md は再配布禁止・全権利留保。翻訳ファイルは CC BY 4.0 | 【一次】 | [S1][S3] |
| 外部貢献 | 受け付けていない | 【一次】 | [S2] |
| サポート | Discord の #support | 【一次】 | [S2] |
| ホームページ | fabric.mod.json に https://flashback.moulberry.com/ とある（今回は未読） | 【一次】 | [S5] |
| Modrinth の数値 | 1310万（13.1M）ダウンロード、3.9K フォロワー、「2 年前 に公開」「2 か月前 に更新」と表示（2026-11-19 取得） | 【一次】 | [S1] |

> 「Copyright 2024 Moulberry. Do not reupload or redistribute.」[S2]
> 「Flashback currently does not accept outside contributions」[S2]

- 動画で使うときの条件（クレジット等）は [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md) で扱う。

### 対応バージョンと依存（2026-11-19 時点）

- Modrinth の互換表示: 26.3、26.2、26.1.x、1.21.4–1.21.11、1.21–1.21.1。プラットフォームは Fabric。【一次】[S1]
- master ブランチの gradle.properties: `minecraft_version=26.3`、`loader_version=0.19.5`、`mod_version=0.43.6`、`fabric_version=0.161.0+26.3`。これは開発中のソースの値で、Modrinth で配布中の 26.3 向けの版の番号とは一致しない可能性がある。【一次】[S4]
- master ブランチの fabric.mod.json の depends: fabricloader `>=0.15.10`、minecraft `>26.2 <26.4`、java `>=21`、fabric-api `>=0.107.0`。breaks: iris `<1.10.9`、voicechat_api `<2.6.24`。【一次】[S5]
- 0.40.0 は「リリース」（正式版）で MC 26.1.x 向け。公開は Modrinth の表示で「7 か月前」（2026-11-19 から見て）、ダウンロードは「83.9万」と表示（2026-11-19 取得）。【一次】[S8]

### 録画

UI 文字列から読める録画の機能【一次】[S6]:
- ワールド／サーバに入ると自動で録画を始める設定、出ると自動で終える設定。
- 録画の開始・一時停止・再開・取り消し・終了のボタン（ポーズメニューに出る）。
- マーカーを4種類（キー割り当てつき）。ディメンションを移ったときに自動でマーカーを付ける設定もある。
- 一人称の位置・向きの更新頻度の設定。自分の一人称視点を書き出すなら、書き出すフレームレートまで上げるよう説明にある。
- 異常終了した録画の復旧。最後の最大5分が失われることがある。
> 「Unfortunately, up to 5 minutes of gameplay from the end of the recording may be lost」[S6]
- 録画・再生・書き出しのそれぞれで、問題が知られている mod が入っていると警告を出す画面がある（対象の mod の一覧は今回読んだファイルには無い）。
- MCバージョンやプロトコル・データのバージョンが違うリプレイは開けないか、開けない恐れがあると警告する。mod を足し引きしたあとはリプレイが動かないことがある。

### エディタ（再生と編集）

UI 文字列から読めるもの【一次】[S6]:
- 書き出しはメインメニューバーの「File」→「Export Video」。I／O キーで書き出す区間（In/Out）を決める。
- 左右の矢印キーで再生ヘッドを1tick進める・戻す。上下の矢印キーで次・前のキーフレームへ飛ぶ。
> 「Use the left/right arrow keys to move the playhead forwards/backwards 1 tick.」[S6]
- 飛ぶ速さはマウスホイールで変える。X・Y・Z・Yaw・Pitch を固定して動ける。
- シーン（複数のキーフレームの組）を作り、名前を付けて切り替えられる。書き出しのファイル名に `%scene%` を使える。
- ワールド内のエンティティを右クリックすると、観戦、表示・非表示、発光などのメニューが出る。
- `/hide [entity]` と `/show [entity]` のコマンドで、書き出し時に隠すエンティティを指定できる。
- 「Render Filter」でエンティティやパーティクルの種類ごとに描画を切れる。パーティクルは新しく出るものを止めるだけで、出ているものは消えない。
- 「Visuals」: GUI の各部やワールドの各部（ブロック、エンティティ、パーティクル、空、名札など）の表示の切り替えと、空の色、霧、FOV、時刻、暗視、天気の上書き。
- 構図のガイド: 三分割（Rule of Thirds Guide）、中央（Center Guide）。
- 縦横比（Aspect）の選択肢: 16:9、9:16 (Shorts)、2.40:1、1:1、4:3、3:2。ほかに『Sizing』の選択肢（Keep Aspect Ratio、Change Aspect Ratio、Fill、Underlay）がある。これらがどの画面の項目か、構図のガイドなのか書き出しの設定なのかは、言語ファイルからは読み取れない（[縦型撮影.md](縦型撮影.md) と同じ扱い）。なお、別 mod の Flashback Extras は、縦の枠を画面に重ねて表示する Export Preview Overlay を追加するとしている（下の『拡張する別の mod』の表）。【一次】[S6][S12]
- 実時間のキーフレーム補間: 有効だと実時間の差で、無効だと tick の差でキーフレームの間を補間する。
> 「Interpolate between keyframes based on the realtime difference. Disable to use the tick difference for interpolation」[S6]

### キーフレームの種類

| 内部名 | 英語の表示 | 日本語の表示 | 確度 | 出典 |
|---|---|---|---|---|
| camera | Camera | カメラ | 【一次】 | [S6][S7] |
| camera_orbit | Camera Orbit | カメラ軌道 | 【一次】 | [S6][S7] |
| fov | FOV | 視野 | 【一次】 | [S6][S7] |
| speed | Speed | 速度 | 【一次】 | [S6][S7] |
| freeze | Freeze | フリーズ | 【一次】 | [S6][S7] |
| timelapse | Timelapse | タイムラプス | 【一次】 | [S6][S7] |
| time_of_day | Time of day | 時刻 | 【一次】 | [S6][S7] |
| camera_shake | Camera Shake | 手ブレ | 【一次】 | [S6][S7] |
| track_entity | Track Entity | エンティティ追跡 | 【一次】 | [S6][S7] |
| block_override | Block Override | ブロック上書き | 【一次】 | [S6][S7] |
| audio_track | Audio Track | オーディオトラック | 【一次】 | [S6][S7] |

- フリーズには、滑らかに止めるための遅れ（tick 単位）の設定があり、設定すると指定の時間をかけて徐々に遅くなって止まる。【一次】[S6]
> 「Setting this will make the game gradually slow down over the specified delay until it comes to a freeze」[S6]
- タイムラプスにはキーフレームが2つ要り、右のキーフレームの時刻は左より大きくなければならない。【一次】[S6]
- エンティティ追跡は頭・胴・根元（Root）のどこを追うかと、位置・向き・視点のオフセットを持つ。プレイヤーを観戦するだけならカメラのキーフレームは要らないと表示される。【一次】[S6]
- キーフレームは Ctrl+C／Ctrl+V でコピー・貼り付けでき、取り消し・やり直しのキーがある。位置・Yaw・Pitch を基準にした相対コピー（Copy Relative）もある。Shift を押すとキーフレームに吸着する。【一次】[S6]

### 補間の種類

| 内部名 | 英語の表示 | 日本語の表示 | 確度 | 出典 |
|---|---|---|---|---|
| smooth | Smooth | ベジェ | 【一次】 | [S6][S7] |
| linear | Linear | リニア | 【一次】 | [S6][S7] |
| ease_in | Ease In (Linear Out) | イーズイン(リニアアウト) | 【一次】 | [S6][S7] |
| ease_out | Ease Out (Linear In) | イーズアウト(リニアイン) | 【一次】 | [S6][S7] |
| ease_in_out | Ease In/Out | イージーイーズ | 【一次】 | [S6][S7] |
| hold | Hold | ホールド | 【一次】 | [S6][S7] |
| hermite | Hermite | ハーマイト | 【一次】 | [S6][S7] |

- 新しく作るキーフレームの既定の補間を設定で選べる。【一次】[S6]
- 「Smooth」がどの曲線かは読んだ資料に無い（訳の「ベジェ」が正しいかも未確認）。

### 書き出し

UI 文字列から読める書き出しの項目【一次】[S6]:

| 区分 | 項目 |
|---|---|
| 取り込み（Capture Options） | 開始／終了 tick、フレームレート、Reset RNG |
| 映像（Video Options） | コンテナ、エンコーダ、コーデック、ビットレート（最大ビットレートを使う設定あり）、解像度、SSAA、No GUI、透明な空、深度マップ |
| 音声（Audio Options） | 音声の記録、ステレオ（2ch）、音声コーデック、音の聞き手（カメラ／エンティティ） |
| ジョブ | 書き出しのキュー、ジョブ名、すべて開始・すべて削除 |
| その他 | スクリーンショットの書き出し、ファイル名の変数（`%replay%`、`%scene%`、`%seq%` など） |

- SSAA は2倍の解像度で描いて縮小し、ギザギザを消す。【一次】[S6]
- 深度マップはグレースケールで書き出す。【一次】[S6]
- 透明な空: Visuals で「Render Sky」を切り、書き出し画面で「Transparent Sky」を入れる。【一次】[S6]
> 「Export with a transparent sky by first unticking 'Render Sky' in the Visuals window and then ticking 'Transparent Sky' in the export window」[S6]
- Reset RNG: 同じ場面を何度も書き出すときに出力を揃えるため、リプレイから乱数性を取り除こうとする（「試みる」と書かれている）。【一次】[S6]
> 「Attempts to remove randomness from the replay in order to produce more consistent outputs when recording the same scene multiple times」[S6]
- 日本語訳は「全く同じ出力」としているが、英語の原文は「more consistent」（より揃った）で、完全な一致は約束していない。【一次】[S6][S7]
> 「リプレイからランダム性を除去し、同じシーンを複数回再生しても全く同じ出力を得やすくします」[S7]
- GIF は非常に大きくなるので WebP を勧める警告がある。【一次】[S6]
- フルスクリーンでは書き出しに問題が出るので、切ってから書き出すよう警告が出る。【一次】[S6]
> 「Fullscreen causes various issues when exporting. Please disable fullscreen before exporting」[S6]
- 「Use System FFmpeg」: システムの FFmpeg のライブラリを使う設定で、libx264 や AMD AMF などのエンコーダが使えるようになるかもしれないとある（再起動が必要）。Replay Mod のように FFmpeg を別に入れる手順は README の導入手順に無い。【一次】[S6][S2]
> 「Try to use the FFmpeg libraries from your system, may allow for additional encoders like libx264 or AMD AMF. (Requires restart!)」[S6]
- 「Dummy Render Frames」: 1コマ保存する前に空のコマを余分に描く。書き出しは大幅に遅くなるが、時間方向に蓄積するシェーダーや、FREX Flawless Frames に対応しない mod では必要なことがある。【一次】[S6]
> 「This will DRASTICALLY increase the time it takes to export, but may be necessary when using shaders that rely on temporal accumulation or mods which lack support for FREX Flawless Frames」[S6]

### 投影（Projection）

- UI 文字列に投影の選択肢として Perspective、Orthographic、Cube Map、Equirectangular がある。【一次】[S6]
- 0.40.0 の変更点に、この3つの投影の追加が書かれている。同じ版で、キー割り当ての変更、In/Out の解除キー（Ctrl+I／Ctrl+O）、ズームのキー（=／-）、ロールのキー（既定は未割り当て）なども追加された。【一次】[S8]
> 「Added "Orthographic" projection」[S8]
- ja_jp.json には投影（projection）の項目の訳が見当たらなかった（2026-11-19 取得時）。日本語の UI でも英語のまま出る可能性がある。【一次】[S7]
- 平行投影が書き出しの映像にそのまま反映されるか、どの画面で選ぶかは、読んだ資料からはわからない。

### シェーダー（Iris）・Sodium

- master の fabric.mod.json は Iris 1.10.9 未満を breaks にしている。つまり Iris を入れるなら 1.10.9 以上が必要。【一次】[S5]
- fabric.mod.json に `frex_flawless_frames` の入口（`com.moulberry.flashback.exporting.FrexFlawlessFramesIntegration`、書き出し（exporting）のパッケージ）がある。【一次】[S5]
- 時間方向に蓄積するシェーダーでは Dummy Render Frames が必要なことがある（上記）。【一次】[S6]
- Flashback の空の色の上書きを Iris のシェーダーで効かせる別 mod『Flashback-Iris-SkyColorOverrideCompat』がある。Modrinth の互換表示は 1.21.11、1.21.4–1.21.5、1.21–1.21.1 で、26.x は無い。ライセンスは CC-BY-NC-SA-4.0。2.0.0 では雲をシェーダーの設定で手で切る必要があると書かれている（2026-11-19 取得）。【一次】[S13]
> 「Make Flashback's sky override option work with iris shaders.」[S13]
> 「However, you must manually disable clouds in your shader settings.」[S13]
- Sodium との組み合わせについての公式の説明は、今回読んだ資料には無かった。シェーダーパックの選び方は [シェーダーと画質mod.md](シェーダーと画質mod.md)。

### 時間と tick に関わる設定

- 「Synchronize Ticking」（詳細設定）: クライアントと内蔵サーバを同じ歩調で tick させる。シングルプレイのみ。20 TPS 未満で録るときに有用。デッドロックの恐れがある。【一次】[S6]
> 「Tick client and integrated server in lockstep. Only works in singleplayer. Useful if recording below 20 TPS. May result in deadlocks」[S6]
- サーバの `/tick` との関係は [時間制御とスロー.md](時間制御とスロー.md) で扱う。

### Replay Mod との違い（出典のあるものだけ）

| 項目 | Flashback | Replay Mod | 確度 | 出典 |
|---|---|---|---|---|
| ライセンス | 独自（ARR、再配布禁止） | GPL-3.0-or-later | 【一次】 | [S1][S3][S10] |
| ローダー | Fabric のみ | Fabric（ドキュメントは 1.14 以上と記載。ダウンロードページの現行版の最古は 1.14.4）、Forge（1.12.2 以下） | 【一次】 | [S1][S9][S18] |
| MC の範囲（Modrinth の表示） | 1.21〜26.3 | 1.8〜26.3 | 【一次】 | [S1][S10] |
| 補間 | 7種類（上の表） | 3次スプラインと直線 | 【一次】 | [S6][S9] |
| キーフレームの種類 | 11種類（上の表） | 位置、時間、スペクテイター | 【一次】 | [S6][S9] |
| 投影 | 透視、平行、キューブ、正距円筒 | 通常、立体視、キューブ、正距円筒 | 【一次】 | [S6][S9] |
| 空の処理 | 透明な空 | クロマキー（空を固定色） | 【一次】 | [S6][S9] |
| 深度 | グレースケールの深度マップ | OpenEXR・PNG に深度 | 【一次】 | [S6][S9] |
| 縦横比 | 縦横比の選択肢に 9:16 (Shorts) など（ガイドか書き出しの設定かは未確認） | 解像度を任意に入力 | 【一次】 | [S6][S9] |
| tick 単位の移動 | 矢印キーで1tick | 速度スライダー 0.1〜8倍、タイムラインをクリック | 【一次】 | [S6][S9] |
| FFmpeg | システムの FFmpeg を使う設定がある（既定の仕組みは未確認） | 動画にするには FFmpeg を別に入れる（2.6 以降の PNG 連番と OpenEXR 連番は不要） | 【一次】 | [S6][S9][S17] |

### 拡張する別の mod（各 mod の Modrinth のページ、2026-11-19 取得）

| mod | ページに書かれている内容 | MC の互換表示 | ライセンス | 確度 | 出典 |
|---|---|---|---|---|---|
| Flashback Extras | 書き出しのプリセット（YouTube 1440p などの組み込みと自作）、TikTok や YouTube Shorts 向けに縦型の枠を重ねて表示する Export Preview Overlay、タイムラインの横スクロール。タイムラプスなどの速度変更で音がおかしくなる問題の修正 | 26.3、26.2、26.1.x、1.21.6–1.21.11 | ARR | 【一次】 | [S12] |
| Flashbatch | 同じリプレイの全シーンを一度に書き出しのキューに入れる。ファイル名の変数、書き出しの設定、時間の範囲（In/Out、最初と最後のキーフレーム、全体）を選べる。自分では描画せず、Flashback のキューに入れるだけ | 26.2、26.1.x | MIT | 【一次】 | [S14] |
| FlashPlus | VFX 向けのアドオン。エンティティ追跡、カメラパスの書き出し（FOV キーフレームを含む）、パノラマの書き出し（HDRI 用）。Blender に読み込むには別のアドオンが要る。入れているときは Flashback の作者に不具合を報告しないようにとある | 26.1.x、1.21.11 | ARR | 【一次】 | [S15] |
| Flashback Instant Record | 録画の開始・停止のキー割り当て（3つ）と、30種類以上のゲーム内の出来事（落下、被ダメージ、ディメンションの移動など）をきっかけに録画を自動で始める・止める仕組み。YACL が必要 | 26.3、26.2、26.1.x、1.21.11、1.21.4 | ARR | 【一次】 | [S16] |

> 「Nothing renders automatically: FlashBatch only queues the jobs into Flashback's own render queue」[S14]
> 「Camera Path Exporting (Including FOV Keyframes)」[S15]
> 「It also adds 30+ Different triggers to start / stop flashback automatically without you touching anything.」[S16]

- Flashbatch のページは、Flashbatch の書き出しの設定として投影（projection）を挙げ、それを Flashback 自身の書き出し画面と同じ設定だと説明している。Flashback の平行投影を書き出し画面で選ぶことの間接的な根拠になる（Flashback 本体の資料ではない）。【二次】[S14]
> 「resolution, framerate, projection, container/codec/encoder, bitrate, transparency, SSAA, audio settings... the same options Flashback's own export window offers」[S14]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。

- **第一候補は Flashback。** キーフレームの種類と補間が多く、1tick 単位で再生ヘッドを動かせ、平行投影と 9:16 (Shorts) の縦横比の選択肢がある。基盤のMCバージョンは 1.21 以降で、他の mod と揃う版を [../mods/バージョン対応表.md](../mods/バージョン対応表.md) で決める。（根拠: [S1][S6][S8]）
- **平行投影で「計測映像」を撮る。** 横から平行投影で撮れば、放物線や落下距離を画面上の長さで比べられる。採用前に、0.40.0 以降で平行投影が書き出しに反映されるか、1ブロックが何ピクセルになるかを短い試し撮りで確かめる。（根拠: [S6][S8]）
- **着地 tick の確認に1tick送りを使う。** 矢印キーで1tickずつ動かして、RCON の CSV（`docs/MC実行基盤.md` §3）の着地 tick と映像が一致するかを見る。数値の正本は CSV のまま。（根拠: [S6]）
- **乱数の絡む実験（TNT 等）の撮り直しに Reset RNG を試す。** ただし原文は「試みる」なので、同じ場面を2回書き出して一致するかを実測で確かめてから頼る。（根拠: [S6][S7]）
- **`/tick rate` で遅くした世界を録るなら Synchronize Ticking を試す。** シングルプレイ限定でデッドロックの恐れがあるので、本番前に試す。サーバを分けて RCON で動かす今の構成（専用サーバ）では使えない可能性が高い。（根拠: [S6]）
- **録画は自動開始にする。** 実験の再実行と録画をつなぐため、ワールドに入ると自動で録画が始まる設定を使う。ゲーム内の出来事で録画を制御したいなら Flashback Instant Record を試す（ARR の別 mod で、使うMCバージョンの版があるかを先に見る）。（根拠: [S6][S16]）
- **シーンを分けて撮る回は Flashbatch でまとめてキューに入れることを検討する。** MIT ライセンスで、26.2・26.1.x 向けしか無い点に注意。（根拠: [S14]）
- **ショートは縦横比の『9:16 (Shorts)』を選んで構図を決めることを試す。** それが表示の枠だけなのか、書き出しも縦になるのかを最初の試し撮りで確かめる。縦の枠を重ねて見たいだけなら Flashback Extras の Export Preview Overlay も候補。細かい撮り方は [縦型撮影.md](縦型撮影.md)。（根拠: [S6][S12]）
- **合成用に透明な空と深度マップを使う**（背景の差し替え、目盛りの重ね合わせ）。（根拠: [S6]）
- **シェーダーを使う回は Iris 1.10.9 以上にし、ちらつく場合は Dummy Render Frames を入れる。**（根拠: [S5][S6]）
- **jar をリポジトリや共有フォルダに置かない。** 再配布禁止なので、`mc/mods.yaml` には入手元（Modrinth）の URL と版だけを書く。（根拠: [S2][S3]）
- **手順書には英語の UI 名を併記する。**（根拠: [S6][S7]）

## わかっていないこと・要確認
- リプレイファイルの形式と保存場所、キーフレーム（シーン）を外部のプログラムで作って読み込めるか（自動化の可否）。
- 平行投影が書き出しに反映されるか、どの画面で選ぶか（Flashbatch のページの説明からは書き出し画面と読めるが、Flashback 本体の資料では未確認）。平行投影での表示範囲（ズーム）の決め方。
- 速度キーフレームで指定できる速さの範囲。タイムラインの最大の長さ。
- 書き出しで選べるコンテナ・コーデックの一覧（既定で使える FFmpeg の中身）と、NVENC が使えるか。
- 「Smooth」補間の数式。
- 縦横比（Aspect）の選択肢と『Sizing』がどの画面の項目か。『9:16 (Shorts)』を選んだとき、書き出しの解像度も縦になるのか、表示の枠だけなのか（[縦型撮影.md](縦型撮影.md) にも同じ項目）。
- 26.3 向けに Modrinth で配布中の版の番号（master は 0.43.6）。
- 問題が知られている mod の一覧（警告画面に出るもの）。
- サーバ側で `/tick freeze`・`/tick step` を使った場面を録ったとき、リプレイの tick がどう記録されるか（実測が要る）。
- Replay Mod と同時に入れたときの挙動。Flashback の変更履歴に、Replay Mod が Flashback のリプレイを録画しないようにしたという項目がある、という検索結果がある（検索要約のみ・原文未読。Modrinth の変更履歴のページは本文が JS で出ず読めなかった）。【未確認】[S11]
- Flashback と Replay Mod のどちらが優れているかを示す公式の比較や第三者の検証は、今回の調査では見つからなかった。
- ホームページ（flashback.moulberry.com）の内容（未読）。

## 参照先
- [S1] Flashback - Minecraft Mod — Modrinth — https://modrinth.com/mod/flashback — 「2 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] Flashback README.md（master） — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/README.md — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Flashback LICENSE.md（master） — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/LICENSE.md — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Flashback gradle.properties（master） — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/gradle.properties — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Flashback fabric.mod.json（master） — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/src/main/resources/fabric.mod.json — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Flashback lang/en_us.json（master） — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/src/main/resources/assets/flashback/lang/en_us.json — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Flashback lang/ja_jp.json（master） — 翻訳 hqnkuh、stabery（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/src/main/resources/assets/flashback/lang/ja_jp.json — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] 0.40.0 - Flashback — Modrinth — https://modrinth.com/project/4das1Fjq/version/XRtfepgi — 「7 か月前」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Minecraft Replay Mod - Documentation — ReplayMod — https://www.replaymod.com/docs — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] ReplayMod - Minecraft Mod — Modrinth — https://modrinth.com/mod/replaymod — 「先月 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Flashback - Changelog — Modrinth — https://modrinth.com/mod/flashback/changelog — 不明 — 取得: 2026-11-19 — 原文: 検索要約のみ（ページは本文がJSで出ず読めなかった）
- [S12] Flashback Extras — Modrinth — https://modrinth.com/mod/flashback-extras — 「3 日前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S13] Flashback-Iris-SkyColorOverrideCompat — Modrinth — https://modrinth.com/mod/flashback-iris-skycoloroverridecompat — 「3 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S14] Flashbatch - A Flashback Addon — Modrinth — https://modrinth.com/mod/flashbatch — 「4 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ（当初の出典 modpackindex.com は読めないホストのため差し替え）
- [S15] FlashPlus — Modrinth — https://modrinth.com/mod/flashplus — 「7 か月前 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S16] Flashbackinstantrecord — Modrinth — https://modrinth.com/mod/flashbackinstantrecord — 「先月 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S17] changelog.txt — ReplayMod — https://www.replaymod.com/changelog.txt — 更新日 不明（先頭が 2.6.28） — 取得: 2026-11-19 — 原文: 読んだ
- [S18] Minecraft Replay Mod - Download Page — ReplayMod — https://www.replaymod.com/download — 更新日 不明（最新 v2.6.28 を掲載） — 取得: 2026-11-19 — 原文: 読んだ
