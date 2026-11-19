# Replay Mod

> 対象: Replay Mod（ReplayMod）の録画・再生・カメラパス・レンダリングの機能、対応バージョン、Iris/Sodium との互換、ファイル、既知の制限、自動化に使える仕組み。
> 使う場面: 撮影方式を決めるとき（Flashback との比較）、Replay Mod で撮る回の撮影前の確認、書き出し設定を決めるとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition。Replay Mod 2.6.28 時点（2.6.28 は 1.8.9〜26.3 の各版に配布）。統合版（Bedrock）には無い。
> 関連: [Flashback.md](Flashback.md), [時間制御とスロー.md](時間制御とスロー.md), [カメラワーク技法.md](カメラワーク技法.md), [縦型撮影.md](縦型撮影.md), [シェーダーと画質mod.md](シェーダーと画質mod.md), [録画設定.md](録画設定.md), [../mods/バージョン対応表.md](../mods/バージョン対応表.md), [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md)

## 要点
- Replay Mod は完全にクライアント側の mod で、サーバには入れられない。MC 1.14 以上は Fabric、1.12.2 以下は Forge が必要。【一次】[S1][S2]
- 2026-11-19 時点の最新は v2.6.28 で、MC 26.3・26.2・26.1・1.21.11 から古い版まで、同じ 2.6.28 が各MCバージョン向けに配布されている。【一次】[S2][S3]
- 開発方針として、MCバージョンごとに1つの版を保ち、全バージョンで機能をそろえている。【一次】[S5]
- ライセンスは GPL-3.0-or-later。【一次】[S4][S5]
- 録画はワールド／サーバに入った時点から始める必要がある（設定で自動録画）。記録されるのは描画距離（サーバでは view-distance）内の読み込み済みチャンク。【一次】[S1]
- カメラパスは位置キーフレーム（x, y, z, yaw, pitch, roll）と時間キーフレームで作る。補間は3次スプライン（既定）と直線の2種類。キーフレームのタイムラインは最長10分。【一次】[S1]
- 時間キーフレームで再生速度を制御でき、同じ時刻の時間キーフレームを2つ置くとその区間は時間が止まる。カメラパスの中で時間を逆行させることはできない。【一次】[S1]
- レンダリングは外部の FFmpeg を使う（2.6 以降、PNG 連番は FFmpeg 不要）。方式は通常・立体視（左右）・キューブ・正距円筒（360°）。MP4/WEBM/MKV（可逆）/PNG連番/OpenEXR連番を選べ、クロマキー（空の色の固定）と深度マップの書き出しがある。【一次】[S1][S3]
- ドキュメントのエンコードのプリセット一覧は古い。変更履歴では「MP4 - High Quality」が 2.4.0 で、「MP4 - Default Quality」が 2.6 で削除されている。【一次】[S1][S3]
- 公式ドキュメントの互換性の節には、Sodium では描画できないという趣旨の古い記述が残るが、ダウンロードページには Sodium 0.4.3 以降の公式版が対応したと書かれている。Iris は 1.16.5 以上で対応とされる。【一次】[S1][S2]
- 2.6.27 で、録画したプレイヤーの位置が真の位置からわずかにずれる不具合（1tick あたり 1/4096 未満、最大 0.03 ブロック）が直された。【一次】[S3]
- 自動化に使える仕組み: FFmpeg のコマンドと引数を差し替えられる、レンダーキューがリプレイファイルに保存される、複数リプレイのキューをまとめて描画できる、カメラパスを .glb で書き出せる。README は、Replay Mod は外部向けの API を提供しないとしている。カメラパスを外部から読み込む公式の手段は、読んだ資料には見当たらなかった。【一次】[S1][S3][S5]

## 詳細

### 基本情報

| 項目 | 内容 | 確度 | 出典 |
|---|---|---|---|
| 動作環境 | クライアント側のみ | 【一次】 | [S1][S4] |
| ローダー | MC 1.14 以上は Fabric、1.12.2 以下は Forge | 【一次】 | [S1][S2] |
| ライセンス | GPL-3.0-or-later（Modrinth の表示と README） | 【一次】 | [S4][S5] |
| Modrinth の数値 | 1950万（19.5M）ダウンロード、4.6K フォロワー、「4 年前に作成」「先月 に更新」と表示（2026-11-19 取得） | 【一次】 | [S4] |
| 先行配布 | ダウンロードページに、VIP の Patreon 支援者は新しい版を先に使えるとある | 【一次】 | [S2] |

> 「Note: The Replay Mod is entirely client side and can not be installed on the servers you play on.」[S1]

README の開発方針（訳）: MCバージョンごとに Replay Mod を1つずつ保ち、それらはすべて同じ機能（とほとんどのバグ）を共有する。【一次】[S5]
> 「we maintain one version of the ReplayMod for each version of Minecraft and all these versions share the same feature set (and most bugs)」[S5]

### 対応バージョン（2026-11-19 時点）

ダウンロードページの先頭に「Replay Mod v2.6.28」とあり、2.6.28 の Fabric 版は MC 26.3、26.2、26.1、1.21.11、1.21.10（1.21.9 兼用）、1.21.7（1.21.8・1.21.6 兼用）、1.21.5、1.21.4、1.21.2（1.21.3 兼用）、1.21（1.21.1 兼用）、1.20.6、1.20.4（1.20.3 兼用）、1.20.2、1.20.1（1.20 兼用）、1.19.x、1.18.x、1.17.1、1.16.x、1.15.2、1.14.4 に、Forge 版は 1.12.2 以下に配布されている。【一次】[S2]

Modrinth の互換表示は Java Edition の 26.3、26.2、26.1.x、1.21.x、1.20.6、1.20–1.20.4、1.19.x … 1.8。プラットフォームは Fabric と Forge。【一次】[S4]

変更履歴の主な対応の追加（日付は変更履歴に書かれていない）【一次】[S3]:

| 版 | MC の対応 | 主な変更（抜粋） |
|---|---|---|
| 2.6.28 | 26.3 | 26.2 以上のチームに関するネットワークエラーの修正 |
| 2.6.27 | 26.2 | 26.1 以上でレンダリング中に光が更新されない不具合の修正、録画プレイヤーの位置のずれの修正 |
| 2.6.26 | 26.1 | 1.21.11 でテクスチャのアニメーションが出ない不具合の修正 |
| 2.6.23 | 1.21.7 | 1.21.5 以上の深度の書き出しの修正、Iris 1.7 以上で一人称の手が消える不具合の修正 |

最新のMC本体のバージョンや、他の mod と揃うバージョンは [../mods/バージョン対応表.md](../mods/バージョン対応表.md) を見る。

### 録画

- 設定で有効にすると、すべてのプレイ中のセッションを自動で録画する。録画の開始はチャットで知らされ、左上に録画中の表示が出る（どちらも設定で消せる）。【一次】[S1]
- 録画はサーバ／ワールドに入るときに始める必要がある。途中からでは、リプレイファイルに必要なデータが欠ける。【一次】[S1]
> 「Due to the way the Replay Mod works, you need to start recording when joining a Server or World」[S1]
- 2.2.0-b1 で、ゲーム中に録画の一時停止・再開・停止・開始ができるようになった。実際には常に録画していて、あとで Replay Editor を自動でかける方式と書かれている。【一次】[S3]
> 「Add option to pause/resume/stop/start replay while ingame (actually always records but automagically applies Replay Editor afterwards)」[S3]
- 記録されるチャンク: シングルプレイでは描画距離内の読み込み済みチャンクすべて。サーバでは server.properties の view-distance に依存（既定は11チャンクと書かれている）。背後のチャンクも記録される。【一次】[S1]
- 録画中に M キーでイベントマーカーを置ける。再生中にもマーカーを足せ、名前を付けられ、タイムライン上で右クリックするとその位置・時刻へ飛べる。【一次】[S1]
- 公式の説明では、録画は通常フレームレートに影響せず、サーバのラグも起こさない。【一次】[S1]

### ファイル

- 録画ファイルの拡張子は .mcpr。大きさは含まれるワールドのデータ量で大きく変わり、虚無のワールドで録った場合は小さい。【一次】[S1]
- ファイルの大きさについて、公式の記述どうしで数値が違う: ドキュメントは10分で2〜10MBが普通、Modrinth の紹介文は1時間で10MB未満としている。【一次】[S1][S4]
> 「An average Replay File of 10 Minutes duration usually is between 2MB and 10MB large.」[S1]
> 「an average recording over 1 hour is less than 10 Megabytes large」[S4]
- レンダリング中の FFmpeg の情報は .minecraft フォルダの export.log に出る。【一次】[S1]

### 再生と時間の操作

- リプレイ中は WASD・スペース・Shift でスペクテイターのように自由に飛べ、ブロックを通り抜けられる。マウスホイールで飛ぶ速さを変える。【一次】[S1]
- J／L キーでカメラを傾け（ロール）、K で戻す。【一次】[S1]
- 生き物（プレイヤーを含む）を右クリックすると、その視点で観戦できる。【一次】[S1]
- P キーで一時停止すると、エンティティ・パーティクル・ブロック更新が止まり、その間も飛び回れる。速度スライダーの範囲は通常の 0.1倍〜8倍。【一次】[S1]
> 「The minimum Speed value is 0.1 times the normal Minecraft Tick Speed, and the maximum Speed is 8 times as fast.」[S1]
- リプレイのタイムラインをクリックするとその時刻へ移動する。大きく飛ぶときや後ろへ戻るときは時間がかかる。Quick Mode（既定は Q キー）を使うと移動が速くなるが、プレビューでパーティクルやスキンの第2層が描かれなくなる。【一次】[S1]

### カメラパス（キーフレーム）

- キーフレームのタイムラインは10分の長さで、カメラパスは最長10分。タイムラインの時刻はリプレイ内の時刻ではなく実時間（映像の時間）を表す。【一次】[S1]
> 「The Keyframe Timeline is 10 Minutes long, meaning a Camera Path can take up to 10 Minutes.」[S1]
- 位置キーフレームはカメラの位置と向き（x, y, z, yaw, pitch, roll）を持つ。【一次】[S1]
- 補間は既定で3次スプライン補間による滑らかな曲線。設定で直線に変えられ、O キーで3次と直線を切り替える。H キーで経路を赤い線でワールド内に表示する。【一次】[S1]
> 「This curve is generated using Cubic Spline Interpolation.」[S1]
- 時間キーフレームはリプレイ内の時刻を持ち、カメラパスの再生中はリプレイの時刻がキーフレームの間で補間される。【一次】[S1]
> 「Two Time Keyframes with the same Timestamp will freeze the Replay time for the duration of their interval.」[S1]
> 「Note: Travelling backwards in time is not supported during Camera Paths.」[S1]
- V キーで、速度スライダーの現在値の速さになる位置へタイムラインのカーソルを合わせる（Shift を押すと速度 1.0 として合わせる）。【一次】[S1]
- 観戦中は位置キーフレームの代わりにスペクテイターキーフレームになる。観戦を続けるには同じエンティティで2つ以上必要で、普通の位置キーフレームを置くと観戦から抜ける。【一次】[S1]
- キーフレームをダブルクリックすると編集画面が開き、位置やタイムライン上の時刻を数値で設定できる。Ctrl+Z／Ctrl+Y で取り消し・やり直し（2.5.0 で追加）。【一次】[S1][S3]
- X キーの Keyframe Repository に、リプレイファイルごとにキーフレームのプリセットを保存・読み込みできる。【一次】[S1]
- 2.2.0-b1 から、現在のカメラパスが自動で保存・読み込みされる。【一次】[S3]

### レンダリング

**方式**【一次】[S1]

| 方式 | 内容 |
|---|---|
| Default Rendering | 指定の解像度で描画。最も速い |
| Stereoscopic Rendering | 左右に並べた立体視。入力する幅は最終の幅（フルHDなら 3840×1080） |
| Cubic Rendering | キューブ投影の360°。YouTube の360°動画には使えない |
| Equirectangular Rendering | 正距円筒の360°。YouTube の360°に使える（メタデータの注入が必要）。縦横比は常に 2:1、4320×2160 を推奨 |

- 2.2.0-b1 で球面系の書き出しに FOV のスライダーが付いた（VR180 などのため）。変更履歴には、VR 動画を作るための描画方式として ODS を追加した項目と、ODS の修正が複数ある（ドキュメントの方式の一覧には ODS は無い）。【一次】[S1][S3]
> 「Added ODS Rendering Method to create VR videos」[S3]
- 解像度は任意の値を入力できる（例として 1280×720、1920×1080、3840×2160 が挙げられている）。【一次】[S1]
- ドキュメントの「Video Framerate」の節は見出しだけで本文が無い（2026-11-19 取得時）。【一次】[S1]

**エンコードのプリセット**（ドキュメントの記載）【一次】[S1]

| プリセット | 内容 |
|---|---|
| MP4 - Default Quality | x264。※2.6 で削除（下記） |
| MP4 - High Quality | x264、ほぼ可逆、ファイルは大きい。※2.4.0 で削除（下記） |
| MP4 - Potato Quality | x264、試し描き用の低画質 |
| MP4 - Custom Bitrate | x264、ビットレートを指定 |
| WEBM - Custom Bitrate | vp8、ビットレートを指定 |
| MKV - Lossless | x264 の可逆。多くの編集ソフトで開けないので普段は MP4 High を勧めている（その MP4 High は 2.4.0 で削除済み） |
| PNG Sequence | PNG 連番。深度は BGRA の8bit成分に32bit浮動小数で詰めてある |
| OpenEXR Sequence | 深度などの追加の層を持てる |

- ドキュメントは「MP4 - Default Quality」を既定としているが、変更履歴では 2.6 でこのプリセットを削除し、既定のビットレートを 10 から 20mbps に変えている。ドキュメントのこの部分は古い。【一次】[S1][S3]
> 「Remove the MP4 Default Quality preset because it was too unreliable, changed default bitrate from 10 to 20mbps (#475)」[S3]
- ドキュメントにある「MP4 - High Quality」も、変更履歴の 2.4.0 で、ビットレートが極端に大きくなるという理由で削除されている。変更履歴には、このプリセットを戻したという記述は無い。【一次】[S1][S3]
> 「Remove High Quality MP4 preset because it resulted in ludicrous bit rates (#254)」[S3]
- 2.6 で PNG 書き出しは FFmpeg が不要になり、深度も書き出せるようになった。2.6.6 で OpenEXR と PNG の書き出しが複数の CPU コアを使うようになり、OpenEXR は全MCバージョンで使えるようになった。【一次】[S3]

**高度な設定**【一次】[S1]
- 名札の描画を切れる（防具立てやモブの名札も消える）。
- 360°系ではカメラの pitch と roll を固定（安定化）できる。
- クロマキー: 空の色を固定色にする実験的な機能。雲は半透明なので切っておくのがよいとされる。
- 深度マップ: 深度の情報を書き出し、Blender などで後から物体を合成して前後関係を保てる。半透明ブロックは深度で正確に表せない。深度の書き出しではアンチエイリアスが効かないので、高解像度で描いて最後に縮小するよう勧めている。

**コマンドラインの設定**【一次】[S1]
- Replay Mod は FFmpeg をコマンドラインで実行して動画にする。実行するコマンドと引数を書き換えられる。
- 引数の中で %WIDTH%、%HEIGHT%、%FPS%、%FILENAME%、%BITRATE% が画面の設定値に置き換えられる。FFmpeg は書き出し先のフォルダで実行される。
- FFmpeg は Windows では ffmpeg.exe を .minecraft フォルダ内のどこかに置けばよい。見つからないときはコマンド欄にフルパスを入れる。

**速さ**【一次】[S1]
- 描画ボタンを Ctrl を押しながらクリックすると High Performance Rendering になり、進み具合の表示の更新を1秒分ごとに減らして少し速くなる。

**レンダーキューとカメラパスの書き出し**【一次】[S3]
- 2.5.0: カメラパスの書き出しを追加。2.5.1 の修正の記述で、カメラパスの書き出しのファイルが .glb と書かれている。
> 「Add camera path export (#391)」[S3]
> 「Fix surplus video file extension in .glb (camera path export) file name (#422)」[S3]
- 2.5.0: レンダーキューをリプレイファイルに保存するようになり、複数のリプレイを Ctrl で選んで「Render X videos」でまとめて描画できるようになった。Keyframe Repository に「Add to Queue」が付いた。
- 2.6.11: キューに入れたあとでキーフレームを変えると、キュー内のパスまで変わる不具合が直された。

### Iris・Sodium・他の mod との互換

- ドキュメント: MC 1.16.5 以上では Iris を使え、完全に対応しているとする。ただし同じ段落に、当面は Replay Mod のダウンロードページの改造版 Sodium と使うようにとある。【一次】[S1]
> 「On Minecraft 1.16.5 and up you can use Iris, which is fully supported.」[S1]
- ドキュメントの Sodium の節: Sodium がある状態で録画はできるが、描画に必要な FREX Flawless Frames API が無いので、改造版 Sodium を使うようにとある。【一次】[S1]
> 「ReplayMod can record when Sodium is installed, but currently lacks the FREX Flawless Frames API to render.」[S1]
- ダウンロードページ: 互換 Sodium の一覧の 1.19.1 の位置に、公式の Sodium（0.4.3 以降）が対応したとある。改造版 Sodium は 1.16.5〜1.19 向けまでしか並んでいない。ドキュメントの上の2つの記述は、これより前の状態のままと読める。【一次】[S2]
> 「Official Sodium (as of 0.4.3) is now compatible」[S2]
- 変更履歴 2.6: Sodium での描画（FREX Flawless Frames API による）と Iris での描画（空、影の更新、葉などのアニメーション）に対応。アニメーションを映像の時間とリプレイの時間のどちらに合わせるかの設定がある。【一次】[S3]
> 「Add support for rendering with Iris (fixes sky, updating of shadows, animations (e.g. foliage), and likely more), there is also a config option for changing between video-time and replay-time for animations」[S3]
- 変更履歴の Iris 関連の修正: 2.6.4（Iris 1.1.3 以上で手が消える・ODS）、2.6.16（Iris 1.7.x の ODS）、2.6.23（Iris 1.7 以上で一人称の手が消える）。【一次】[S3]
- 対応しない起動環境: Future Client（Mixin が合わない）、Lunar Client（非対応）、Badlion Client（別物の Replay Mod を提供）。【一次】[S1]
- 問題が報告されている mod（ドキュメントの記載）: Tickrate Changer（Replay Viewer で固まる）、Baritone（リプレイ読み込みでクラッシュ）ほか。【一次】[S1]

シェーダーの選び方と負荷は [シェーダーと画質mod.md](シェーダーと画質mod.md) を見る。

### 既知の制限・注意

- ドキュメントのクラッシュ対処に、カメラを Y=0 より下や Y=255 より上へ動かさないようにとある。この記述が今の高さの範囲のMCでも当てはまるかは書かれていない。【一次】[S1]
> 「Make sure the camera doesn't move below Y=0 or above Y=255」[S1]
- 変更履歴の 2.4.0 に、読み込まれたチャンクの外（例として Y > 256）で描画すると固まる不具合の修正がある。【一次】[S3]
> 「Fix lockup when rendering outside of loaded chunks (e.g. Y > 256) (#197)」[S3]
- カメラパスでは時間を逆行できず、パスは最長10分（上記）。【一次】[S1]
- 2.6.27 より前の版で録ったリプレイでは、録画したプレイヤー自身の位置が最大 0.03 ブロックずれていた（2.6.27 で修正。古いリプレイが直るかは書かれていない）。【一次】[S3]
> 「Fix recording player entity position slightly drifting from true position (less than 1/4096 per tick, at most 0.03 blocks)」[S3]
- 変更履歴では、録画時の不具合は既存のリプレイを直せないと何度も注記されている（例: 2.3.2、2.4.0）。【一次】[S3]

### 自動化の手がかり

- 事実として使えるもの: FFmpeg のコマンドと引数の差し替え（プレースホルダつき）、レンダーキューのリプレイファイルへの保存、複数リプレイの一括描画、カメラパスの .glb 書き出し、リプレイごとのキーフレームのプリセット。【一次】[S1][S3]
- README のバージョンの付け方の説明に、Replay Mod は外部向けの API を提供しないとある。【一次】[S5]
> 「the ReplayMod does not provide any external API」[S5]
- カメラパスを外部のファイルから読み込む手段や、描画を外部から起動する公式の手段は、今回読んだドキュメント・変更履歴・README には書かれていなかった。【一次】[S1][S3][S5]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。

- **計測値はリプレイから読まない。** 位置の記録にずれの不具合があった前例があるので、数値の正本は RCON で取る CSV（`docs/MC実行基盤.md` §3）にし、リプレイは見せるためだけに使う。（根拠: [S3]）
- **録画はワールドに入る前から有効にしておく。** 途中から録れないので、実験の手順の中で、録画を有効にしてから接続することを決まりにする。（根拠: [S1]）
- **スローは時間キーフレームで作る。** 2つの時間キーフレームの間の、リプレイ内の時間と映像の時間の比が速さになる。同じ時刻を2つ置けば静止画のような止めが作れる。ただしパスの中で巻き戻しはできないので、同じ瞬間をもう一度見せるときはパスを分けて編集でつなぐ。（根拠: [S1]）
- **書き出しは PNG 連番か MP4 - Custom Bitrate。** Remotion で組むので、まずは PNG 連番（FFmpeg 不要、多コア）で書き出して試し、容量が重ければ MP4 - Custom Bitrate でビットレートを高めに指定する。ドキュメントにある「MP4 - Default Quality」「MP4 - High Quality」は無くなっている前提で手順を書き、使う版の画面で実際に並ぶプリセットを確かめる。（根拠: [S1][S3]）
- **計測線の合成に深度マップを試す価値がある。** OpenEXR の深度を使えば、軌跡の線や目盛りをブロックの後ろに隠れるように合成できる可能性がある。半透明ブロックの前では崩れる点に注意。（根拠: [S1]）
- **空の色を固定して合成する**場合はクロマキーを使い、雲を切る。（根拠: [S1]）
- **Sodium・Iris と一緒に使う場合**、ドキュメントの改造版 Sodium の案内は古いと見て、Sodium 公式版を使う。採用する前に、使うMCバージョンで実際に描画できるかを短いパスで確かめる。（根拠: [S1][S2]）
- **NVENC で書き出したい場合**、コマンドライン引数を差し替える余地があるが、同梱でない FFmpeg を使うので、使う FFmpeg が NVENC に対応しているかを先に確かめる。（根拠: [S1]）
- 基盤のMCバージョンで Flashback が使えるなら Flashback を主にし、Replay Mod は Flashback が対応しない版（例: 1.21.2〜1.21.3、1.20.x 以下）や Forge を使う回の予備にする（比較と Flashback の対応版は [Flashback.md](Flashback.md)）。（根拠: [S2][S4]、Flashback.md の [S1]）

## わかっていないこと・要確認
- 書き出せるフレームレートの範囲（ドキュメントの節が空）。
- Y=0〜255 の制限が今の版でも残っているか。
- 26.x 系で必要な Iris・Sodium の版（ダウンロードページと変更履歴には書かれていない）。
- システムプロパティ（例: `-Dreplaymod.render.height`）で描画の設定を渡す方法が Replay Mod のフォーラムに書かれていたという検索結果がある。そのページは取得時に HTTP 404 で原文を読めず、どの版の話か、今の版で使えるかもわからない（検索要約のみ・原文未読）。【未確認】[S6]
- 2.6 以降の版で、画面に実際に並ぶエンコードのプリセットの一覧（ドキュメントは古く、変更履歴からは削除の記録しかわからない）。
- カメラパス（.glb またはキーフレームのプリセット）を外部で作って読み込めるか。リプレイファイル内での保存形式。
- サーバ側で `/tick freeze`・`/tick rate` を使った場面を録ったとき、リプレイの時間がどう記録されるか（実測が要る。[時間制御とスロー.md](時間制御とスロー.md) とすり合わせる）。

## 参照先
- [S1] Minecraft Replay Mod - Documentation — ReplayMod — https://www.replaymod.com/docs — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] Minecraft Replay Mod - Download Page — ReplayMod — https://www.replaymod.com/download — 更新日 不明（最新 v2.6.28 を掲載） — 取得: 2026-11-19 — 原文: 読んだ
- [S3] changelog.txt — ReplayMod — https://www.replaymod.com/changelog.txt — 更新日 不明（先頭が 2.6.28） — 取得: 2026-11-19 — 原文: 読んだ
- [S4] ReplayMod - Minecraft Mod — Modrinth — https://modrinth.com/mod/replaymod — 「先月 に更新」と表示 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] ReplayMod README.md（develop ブランチ） — ReplayMod（GitHub） — https://raw.githubusercontent.com/ReplayMod/ReplayMod/develop/README.md — 更新日 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Replay Mod Forums thread 921 — ReplayMod — https://www.replaymod.com/forum/thread/921 — 不明 — 取得: 2026-11-19（HTTP 404） — 原文: 検索要約のみ
