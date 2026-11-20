# Createの動力と振り子

> 対象: Create の回転動力（応力＝SU）の計算の仕組みと、動力源ごとに「何を消費しているか」。あわせて、MC で物理的に揺れる振り子を作る手段（Sable／Create Aeronautics とそのアドオン、Valkyrien Skies 2）。
> 使う場面: T14（Createで永久機関は作れるか）と T12（フーコーの振り子）の企画判断・台本の下調べ・実験設計。
> 調査日: 2026-11-20 ／ mc_version: Java Edition 1.21.1（Create は GitHub の `mc1.21.1/dev` ブランチ＝NeoForge 版のソースを読んだ。Sable・Create Aeronautics も 1.21.1）。Valkyrien Skies 2 は 1.20.1 まで。統合版は対象外。
> 関連: [物理系mod.md](物理系mod.md)（ローダー・対応版・ライセンスの一覧）, [バージョン対応表.md](バージョン対応表.md), [../mechanics/流体.md](../mechanics/流体.md)（バニラの水流）, [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../filming/シェーダーと画質mod.md](../filming/シェーダーと画質mod.md)

## 要点
- Create の動力網では、発電側の「容量」は登録値×発電側の回転数の絶対値、機械側の「消費」は登録値×その機械の回転数の絶対値で計算され、両方の合計を比べている。【一次】[S1]
- そのため歯車で回転数を上げても網の容量は増えず、速く回した機械の消費だけが増える。設定ファイルの説明にも、速度を上げるたびにコストが倍になると書いてある。【一次】[S1][S2][S4]
- 消費が容量を超えると網全体が過負荷（overstressed）になり、ゲーム内の案内は、動力源を増やすか負荷の大きい機械を遅くするよう促す。【一次】[S4]
- 水車のコードは周囲の流体の「流れの向き」を読むだけで、読んだ範囲に水を減らす処理はない。泡の柱や溶岩の流れも回転の元として扱われる。【一次】[S5]
- 風車ベアリングの回転数は帆ブロックの数だけで決まり（既定で帆8枚ごとに1 RPM、1〜16 RPM）、高さや天候を見る処理は読んだメソッドにない。【一次】[S6][S7]
- 蒸気機関のボイラーは、炎・マグマブロック・溶岩・焚き火などを「パッシブ熱」として受け付ける。API の説明は、これを「タダの熱源」と書いている。【一次】[S9][S10][S11]
- ボイラーに入れた水は貯まらず消えていく（排出の要求には常に空を返す）。水の供給量・ボイラーの大きさ・熱の3つの最小値で出力レベル（最大18）が決まる。【一次】[S9]
- ハンドクランクはプレイヤーが回し、回す速さに応じてプレイヤーの空腹（exhaustion）が減る設定がある。【一次】[S4][S7]
- 応力の値（各ブロックの容量・消費）はサーバー設定で変えられる。動画で数値を言うときは設定値を確認する必要がある。【一次】[S2]
- Create 本体のベアリング類の説明は、回転入力どおりに構造物を回すというもの（時計ベアリングは時刻に合わせて回る）。重力で揺れるという説明はない。【一次】[S4]
- 物理で揺れる構造物を作るなら、Sable（Rust 製の物理エンジン Rapier を使うライブラリ、1.21.1）と、その上の Create Aeronautics（NeoForge のみ）が候補。【一次】[S12][S14]
- 関節（ユニバーサルジョイント等）は Aeronautics のアドオン『Transmission & Linkage』にあり、物理構造物の回転を Create の動力に戻す「変換ベアリング」もある。【一次】[S15]
- Valkyrien Skies 2 は 1.20.1 までで、1.21.1 の Sable とは同じ版で並べられない（2026-11-20 取得の Modrinth 表示）。【一次】[S12][S16]

## 詳細

### 1. 読んだソースの版
- Create は GitHub リポジトリ Creators-of-Create/Create の `mc1.21.1/dev` ブランチを raw.githubusercontent.com で読んだ（2026-11-20 取得）。ボイラーのコードは `net.neoforged` のクラスを import しており、NeoForge 版のコードである。このブランチに対応する Create のリリース番号は確認していない。【一次】[S9]
- Fabric 版が同じ数値・同じ計算かは読んでいない（「わかっていないこと・要確認」を参照）。

### 2. 応力（SU）の計算式
単位は Stress Units（SU）で、設定の説明に「[in Stress Units]」とある。【一次】[S2]

`KineticNetwork.java` の該当部分【一次】[S1]:
> 「sources.get(be) * getStressMultiplierForSpeed(be.getGeneratedSpeed())」[S1]
> 「members.get(be) * getStressMultiplierForSpeed(be.getTheoreticalSpeed())」[S1]
> 「return Math.abs(speed);」[S1]

- 容量（capacity）は、動力源に登録された値に発電側が生み出す回転数の絶対値を掛けて合計する。消費（stress）は、機械に登録された値にその機械の理論上の回転数の絶対値を掛けて合計する。【一次】[S1]
- 設定ファイルの説明文（`CStress.java`）【一次】[S2]:
> 「Configure the individual stress impact of mechanical blocks. Note that this cost is doubled for every speed increase it receives.」[S2]
> 「Configure how much stress a source can accommodate for.」[S2]
- 各ブロックの既定値は `AllBlocks.java` で登録され、`CStress` がそれを設定項目として定義する（つまり既定値であり、サーバー設定で変更できる）。【一次】[S2][S3]

### 3. 動力源ごとの仕組み（既定値）

| 動力源 | 登録容量（SU、回転数を掛ける前） | 回転数の決まり方 | 何を消費するか | 確度・出典 |
|---|---|---|---|---|
| 水車 | 32 | 流れがあれば 8 ÷ 大きさ RPM（`Mth.clamp(flowScore, -1, 1) * 8 / getSize()`） | 読んだコードは流れの向きを読むだけ | 【一次】[S3][S5] |
| 大型水車 | 128 | 通常の水車の半分の速さ（ポンダーの説明） | 同上 | 【一次】[S3][S4] |
| 風車ベアリング | 512 | 帆の数 ÷ 8（設定）を 1〜16 に制限 | 読んだメソッドは帆の数だけを見る | 【一次】[S3][S6][S7] |
| 蒸気機関 | 1024 | ボイラーのレベルで効率が決まる | ボイラーへの水と熱（燃料） | 【一次】[S3][S9] |
| ハンドクランク | 8 | プレイヤーが右クリックを押し続けて回す | プレイヤーの空腹 | 【一次】[S3][S4][S7] |
| 銅のバルブハンドル | 8 | 設定した角度だけ回す | （未調査） | 【一次】[S3][S4] |
| クリエイティブモーター | 16384 | 入力パネルで設定 | なし（クリエイティブ用） | 【一次】[S3][S4] |

機械側の登録消費（SU、回転数を掛ける前）の例: 扇風機（encased fan）2、ターンテーブル 4、石臼 4、粉砕ホイール 8、メカニカルプレス 8、メカニカルミキサー 4、メカニカルポンプ 4、メカニカルベアリング 4、時計ベアリング 4、ロープ滑車 4、ドリル 4、のこぎり 4、デプロイヤー 4、メカニカルクラフター 2、メカニカルアーム 2。【一次】[S3]

計算例（式に既定値を代入したもの。`calculateAddedStressCapacity` が登録値をそのまま返すことは読んでいないので、実機のゴーグル表示で確かめる）:
- 水車1台: 32 × 8 RPM = 256 SU。大型水車: 128 × 4 RPM = 512 SU。【未確認】[S1][S3][S5]
- 風車（帆128枚以上で16 RPM）: 512 × 16 = 8192 SU。【未確認】[S1][S3][S6]

#### 水車
> 「Water Wheels draw force from adjacent Water Currents」[S4]
> 「Covering additional sides will not improve its kinetic output further」[S4]
- `determineAndApplyFlowScore` は周囲の位置ごとに流体の流れのベクトルを読み、回転方向と揃った流れを数えて正負の点数にする。点数は −1〜1 に丸められるので、流れに触れる面を増やしても速くならない。【一次】[S5]
- 泡の柱（bubble column）は上向きまたは下向きの流れとして扱われる。【一次】[S5]
> 「if (blockState.getBlock() == Blocks.BUBBLE_COLUMN)」[S5]
- 溶岩の流れでも回り、そのときは別の進捗（LAVA_WHEEL）が付く。【一次】[S5]
> 「award(lava ? AllAdvancements.LAVA_WHEEL : AllAdvancements.WATER_WHEEL);」[S5]

#### 風車
> 「The Amount of Sail Blocks determine its Rotation Speed」[S4]
> 「Any Structure can count as a valid Windmill, as long as it contains at least 8 sail-like Blocks.」[S4]
> 「return Mth.clamp(sails, 1, 16) * getAngleSpeedDirection();」[S6]
- 設定 `windmillSailsPerRPM` の既定は 8、`minimumWindmillSails` の既定は 8。【一次】[S7]
> 「Number of sail-type blocks required to increase windmill speed by 1RPM.」[S7]

#### ハンドクランク
> 「Hand Cranks can be used by players to apply rotational force manually」[S4]
- 設定 `crankHungerMultiplier`（既定 0.01）の説明は次のとおり。回す速さからプレイヤーの消耗（exhaustion）を計算する係数である。【一次】[S7]
> 「multiplier used for calculating exhaustion from speed when a crank is turned.」[S7]

#### 蒸気機関とボイラー
> 「The minimal setup requires 4 Fluid Tanks」[S4]
> 「With each added power level, an additional Engine can output at full capacity」[S4]
- 大きさで決まる上限はタンク数 ÷ 4（最大18）、水で決まる上限は水の供給量 ÷ 10（最大18）。実際のレベルは熱・水・大きさの最小値。【一次】[S9]
> 「return (int) Math.min(18, boilerSize / 4);」[S9]
> 「private static final int waterSupplyPerLevel = 10;」[S9]
- ボイラーの流体の入口は、入ってきた量を供給量として数えるだけで、排出の要求には常に空を返す。入れた水はボイラーに貯まらない。【一次】[S9]
> 「return FluidStack.EMPTY;」[S9]
- 熱源はタンクの真下の1段を調べる。熱が0の熱源（パッシブ熱）しかないときはパッシブ扱いになり、機関の効率は合計で 1/8 になる。【一次】[S9]
> 「private static final float passiveEngineEfficiency = 1 / 8f;」[S9]
- ゴーグルに出す総出力の式は、効率 × 16 × max(レベル, 機関の数) × 蒸気機関の登録容量。【一次】[S9]
> 「double totalSU = getEngineEfficiency(boilerSize) * 16 * Math.max(boilerLevel, attachedEngines)」[S9]
- 蒸気機関はボイラーから効率（0〜1に丸めた値）を受け取り、出力軸に渡す。【一次】[S8]
> 「float efficiency = Mth.clamp(tank.boiler.getEngineEfficiency(tank.getTotalTankSize()), 0, 1);」[S8]
- この式に既定値を入れると、パッシブ熱だけのボイラーは機関の数によらず 2048 SU、レベル18で機関18台なら 294,912 SU になる（自分たちの計算）。【未確認】[S3][S9]

### 4. パッシブ熱＝「タダの熱源」
- API の説明（`BoilerHeater.java`）は、パッシブ熱を少量で制限の強い熱とし、炎やマグマブロックのような無料の熱源に使うと書いている。【一次】[S10]
> 「passive heat can be used to provide a small amount of heat, highly limiting」[S10]
> 「This is usually used for free sources of heat, such as fire or magma blocks.」[S10]
- パッシブ熱源のタグ `create:passive_boiler_heaters` の中身: `create:blaze_burner`、`create:lit_blaze_burner`、マグマブロック、溶岩、焚き火（タグ `#minecraft:campfires`）、炎（タグ `#minecraft:fire`）。【一次】[S11]
> 「minecraft:magma_block」[S11]
- ブレイズバーナーで強い熱を出すには、燃える物を食べさせる必要がある。ブレイズが入っていないバーナーは工業用の加熱に使えない。【一次】[S4]
> 「For this, the Blaze has to be fed with flammable items」[S4]
> 「However, without a blaze they are not suitable for industrial heating」[S4]

### 5. 歯車・変速と過負荷
> 「Shifting from large to small cogs, the conveyed speed will be doubled」[S4]
> 「Shifting the opposite way, the conveyed speed will be halved」[S4]
> 「It appears that this contraption is _overstressed_. Add more sources or _slow_ _down_ the components with a high _stress_ _impact_.」[S4]
- 回転数の上限は設定 `maxRotationSpeed`（既定 256 RPM）。【一次】[S7]
> 「Maximum allowed rotation speed for any Kinetic Block.」[S7]
- フライホイールは、現在の版では「機械を飾る」ブロックとして説明されている。【一次】[S4]
> 「_Embellish_ your _Machines_ with this imposing Wheel of Brass.」[S4]

### 6. 流体を「無限に」扱う仕組み（ポンプと組み合わせる場合）
- 十分に大きな海にホース滑車を下ろすと、元の水を減らさずに流体を出し入れできる。【一次】[S4]
> 「It will provide/dispose fluids without affecting the source」[S4]
- パイプの開いた端は、目の前の水源ブロックを吸い上げられ、空いた場所へこぼすと水源を作れる。【一次】[S4]
> 「Source blocks right in front of an open end can be picked up」[S4]
> 「while spilling into empty spaces can create fluid sources」[S4]
- 第三者のアドオン『Create: NUE』は、発電の取水口で少し水を消費させ、閉じたポンプ→水車のループを干上がらせる、と説明している（検索要約のみ・原文未読）。【未確認】[S19]
- 第三者の mod『Flowing Fluids』は、水源2つで無限の水が作れないようにし、Create の水車との互換設定を持つ（検索要約のみ・原文未読）。【未確認】[S20]

### 7. 永久機関について、事実から言えること
- 歯車だけで出力を増やすことは計算式の上でできない。容量は発電側の回転数で決まり、変速して速く回した機械は消費が比例して増えるから。【一次】[S1][S2]
- 一方で、水車・風車・パッシブ熱のボイラーは、読んだコードの範囲では燃料を減らさない（水車は流れを読むだけ、風車は帆の数だけ、パッシブ熱はAPIが「タダ」と呼ぶ）。ゲームの世界自体が無限の動力源を用意している、と言える。【一次】[S5][S6][S10]
- 例外として、蒸気機関は水を消費し続け、ハンドクランクはプレイヤーの空腹を消費する。ここではエネルギーの「入口」がゲーム内に表れている。【一次】[S7][S9]

### 8. 振り子を作る手段
#### 8.1 Create 本体（決まった動きをさせるだけ）
> 「Upon receiving Rotational Force, the structure will be rotated according to the hour of the day」[S4]
> 「Seq. Gearshifts relay rotation by following a timed list of instructions」[S4]
- メカニカルベアリングは回転入力どおりに構造物を回し、時計ベアリングは時刻に合わせて回し、シーケンス変速機は時間付きの命令列どおりに回転を伝える。読んだ説明はどれも、動きが回転入力・時刻・命令列で決まるというもので、重力で揺れるという説明はない。【一次】[S4]

#### 8.2 Sable（物理エンジンのライブラリ）
> 「Sable contains a physics pipeline (based on the Rapier physics engine written in Rust) that allows sub-levels to move with physics and react to changes in the world.」[S12]
> 「Use /sable to assemble, modify, and query sub-levels.」[S12]
> 「Sable does not add any content to the survival game, or any manner of constructing sub-levels in survival.」[S12]
> 「Sable is an incredibly intrusive mod. It makes extensive use of mixins, and is prone to many compatibility issues with other mods.」[S12]
- Modrinth の表示（2026-11-20 取得）: Java Edition 1.21.1、Fabric と NeoForge、ライセンス PolyForm Shield License 1.0.0、「6.7Mダウンロード」、公開は「7 か月前」、更新は「2 か月前」。【一次】[S12]
- 公式 Wiki のトップには、開発者向けのページとして『Block Physics Properties』『Dimension Physics Data』が並んでいる（中身は取得できず未読）。【一次】[S13]

#### 8.3 Create Aeronautics とアドオン
> 「You must have both Sable and Create installed to play Create Aeronautics.」[S14]
> 「Aeronautics currently has visual issues when used with Iris Shaders.」[S14]
- Modrinth の表示（2026-11-20 取得）: 1.21.1、NeoForge のみ、ライセンス Simulated Project License、ダウンロード数の表示は 9.6M（同じ日の再取得では 9.5M）、公開は「7 か月前」。【一次】[S14]
- 同じページに、The Game Awards 2026 の Best User Creation の候補である旨のバナーが出ている。【二次】[S14]
- アドオン『Create Aeronautics: Transmission & Linkage』（1.21.1・NeoForge、CC-BY-NC-4.0、「464.4Kダウンロード」、2026-11-20 取得）: ユニバーサルジョイント、油圧ロッド、ヒンジヘッド、空気圧レギュレーター、変換ベアリングを追加する。【一次】[S15]
> 「Universal joints and joint rods allow separate physics structures to stay connected while still permitting controlled movement.」[S15]
> 「Kinetic conversion bearings convert the rotation of an attached Aeronautics physics structure into Create kinetic output」[S15]
- アドオン『Absolute Kinematics』は、Aeronautics のスイベルベアリングを補う物理ジョイントとしてボールジョイントとヒンジを追加する（CurseForge は 403 で読めず、検索要約のみ）。【未確認】[S17]
- アドオン『Create Aeronautics: Gadgets & Gizmos』1.2.0 は、サブレベル同士をつなぐ減衰ばね付きヒンジ（coupler）を追加する（検索要約のみ）。【未確認】[S18]

#### 8.4 Valkyrien Skies 2
> 「Valkryien Skies 2 is in BETA.」[S16]
> 「Notice: Valkyrien Skies is a library mod, you need to download an add-on to use it in ordinary gameplay.」[S16]
- Modrinth の表示（2026-11-20 取得）: 対応は 1.20.1・1.19.2・1.18.2・1.16.5・1.12.2、Fabric と Forge、ライセンス LGPL-3.0-only、「6.3Mダウンロード」、更新は「7 か月前」。原文の BETA の文は綴りが Valkryien になっている。【一次】[S16]
- 船どうし・船と地形・船とプレイヤー・船とエンティティが衝突し、Create の機械を船に載せられる、と説明されている。【一次】[S16]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- **T14 の結論の立て方**: 歯車で増やす永久機関は式の上で無理（根拠: [S1][S2]）。一方で燃料ゼロで回り続ける機械は、水車・風車・パッシブ熱で最初から作れる（根拠: [S5][S6][S10]）。動画の山場は、この2つの違い（閉じた系か、外から無料のエネルギーが入っているか）を見せることにできる。
- **入口探しの実験**: 各動力源について、何がなくなると止まるかを1つずつ消して見せる（水源を壊す、帆を減らす、火を消す、クランクで空腹ゲージを撮る）。ハンドクランクの空腹は、エネルギー保存を一番わかりやすく見せられる（根拠: [S7]）。
- **数値はゴーグルで実測してから言う**: 表の計算例（256 SU、8192 SU、2048 SU など）は式から出した値なので、【実測】にしてから台本に入れる。設定ファイルの値も撮影ワールドで記録する（根拠: [S2][S3][S9]）。
- **ポンプ→水車のループ**: 海のホース滑車やパイプの開口で水を作れるので、水車がポンプを回してその水で回る系が作れるかを実機で確かめる。成立するなら、MCの水は無限であり外部からの入力だ、という説明になる（根拠: [S4][S5]。成立は未確認）。
- **T12 の振り子**: 揺れる面が自由でないと面の回転（歳差）は見えないので、1軸のヒンジではなくボールジョイントやユニバーサルジョイントで吊る構成を探す（根拠: [S15][S17]）。Create 本体のベアリングで作る振り子は、動きを決めて動かしているだけの比較用にできる（根拠: [S4]）。
- **環境は別インスタンス**: Sable と Aeronautics は 1.21.1 なので、計測の基盤（別の版）とは別のインスタンスを立てる。Aeronautics は NeoForge のみ、Iris で表示の問題があるので、撮影は Flashback／Replay Mod とシェーダーの組み合わせを事前に試す（根拠: [S12][S14]。録画 mod の対応は [../filming/Flashback.md](../filming/Flashback.md) を参照）。
- **自動化**: Sable はコマンド `/sable` でサブレベルを組み立てられるので、`experiment.yaml` から RCON で振り子を組む案がある（根拠: [S12]）。

## わかっていないこと・要確認
- `calculateAddedStressCapacity` が登録値をそのまま返すか（容量の計算例の前提）。実機のゴーグル表示で確かめる。
- 読んだブランチに対応する Create のリリース番号。Fabric 版で同じ値・同じ式か。
- ボイラーの水の単位（10 が mB／tick か）。
- ポンプ→水車の閉ループが既定の Create で成立するか（『Create: NUE』の説明からは成立しそうだが原文未読）。
- Sable 単体に関節（拘束）を作るコマンドや API があるか。『Block Physics Properties』『Dimension Physics Data』の中身（重力や空気抵抗を設定できるか）。
- Sable の物理（Rapier）が回転座標系を扱うか。数値誤差で振り子の揺れの面がずれるか（T12 で「回っていない」と言うための対照実験が要る）。
- スイベルベアリング（Aeronautics 本体）の自由度、『Absolute Kinematics』のボールジョイントの実在と対応版（CurseForge が読めず）。
- 『Transmission & Linkage』の変換ベアリングで、物理構造物→Create 動力の変換にエネルギー保存が成り立つか（T14 の続編の題材になりうる）。
- Sable・Aeronautics と Carpet・Flashback・Iris などの同時使用の可否（Sable は mixin が多く互換性の問題が出やすいと自ら書いている）。

## 参照先
- [S1] KineticNetwork.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/content/kinetics/KineticNetwork.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S2] CStress.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/infrastructure/config/CStress.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S3] AllBlocks.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/AllBlocks.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S4] en_us.json（Create の英語の言語ファイル。ポンダー・ツールチップ・GUIの文言） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/generated/resources/assets/create/lang/en_us.json — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S5] WaterWheelBlockEntity.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/content/kinetics/waterwheel/WaterWheelBlockEntity.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S6] WindmillBearingBlockEntity.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/content/contraptions/bearing/WindmillBearingBlockEntity.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S7] CKinetics.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/infrastructure/config/CKinetics.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S8] SteamEngineBlockEntity.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/content/kinetics/steamEngine/SteamEngineBlockEntity.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S9] BoilerData.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/content/fluids/tank/BoilerData.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S10] BoilerHeater.java（Create, mc1.21.1/dev） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/main/java/com/simibubi/create/api/boiler/BoilerHeater.java — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S11] passive_boiler_heaters.json（Create のブロックタグ） — Creators-of-Create — https://raw.githubusercontent.com/Creators-of-Create/Create/mc1.21.1/dev/src/generated/resources/data/create/tags/block/passive_boiler_heaters.json — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S12] Sable - Minecraft Mod — Modrinth（作者 ryanhcode ほか） — https://modrinth.com/mod/sable — 公開「7 か月前」・更新「2 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S13] Sable Wiki: Home — ryanhcode — https://raw.githubusercontent.com/wiki/ryanhcode/sable/Home.md — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S14] Create Aeronautics - Minecraft Mod — Modrinth（Create Aeronautics チーム） — https://modrinth.com/mod/create-aeronautics — 公開「7 か月前」・更新「3 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S15] Create Aeronautics: Transmission & Linkage - Minecraft Mod — Modrinth — https://modrinth.com/mod/create-aeronautics-transmission-linkage — 公開「6 か月前」・更新「3 週間前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S16] Valkyrien Skies - Minecraft Mod — Modrinth（Valkyrien Skies チーム） — https://modrinth.com/mod/valkyrien-skies — 公開「6 年前」・更新「7 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S17] Absolute Kinematics — CurseForge — https://www.curseforge.com/minecraft/mc-mods/absolute-kinematics — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ（403）
- [S18] Create Aeronautics: Gadgets & Gizmos 1.2.0 — Modrinth — https://modrinth.com/mod/create-aeronautics-gadgets-and-gizmos/version/1.2.0 — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ
- [S19] Create: NUE — Modrinth — https://modrinth.com/mod/create-nue — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ
- [S20] Flowing Fluids — CurseForge — https://www.curseforge.com/minecraft/mc-mods/flowing-fluids — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ
