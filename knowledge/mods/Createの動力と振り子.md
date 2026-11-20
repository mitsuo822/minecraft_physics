# Createの動力と振り子

> 対象: Create の回転動力（応力＝SU）の計算の仕組みと、動力源ごとに何を消費しているか。あわせて、MC で物理的に揺れる振り子を作る手段（Sable／Create Aeronautics とそのアドオン、Valkyrien Skies 2）。
> 使う場面: T14（Createで永久機関は作れるか）と T12（フーコーの振り子）の企画判断・台本の下調べ・実験設計。
> 調査日: 2026-11-20 ／ mc_version: Java Edition 1.21.1（Create は GitHub の `mc1.21.1/dev` ブランチ＝NeoForge 版のソースを読んだ。Sable・Create Aeronautics とそのアドオンも 1.21.1）。Valkyrien Skies 2 と『Create: NUE』は 1.20.1 まで（Modrinth の表示）。統合版は対象外。
> 関連: [物理系mod.md](物理系mod.md)（ローダー・対応版・ライセンスの一覧）, [バージョン対応表.md](バージョン対応表.md), [../mechanics/流体.md](../mechanics/流体.md)（バニラの水流）, [../rights/mod・シェーダーの利用条件.md](../rights/mod・シェーダーの利用条件.md), [../filming/シェーダーと画質mod.md](../filming/シェーダーと画質mod.md)

## 要点
- Create の動力網（`KineticNetwork`）では、発電側の容量（capacity）は登録値×発電側の回転数の絶対値、機械側の消費（stress）は登録値×その機械の回転数の絶対値で計算し、それぞれの合計を網の各ブロックに渡している（両者を比べて過負荷にする処理そのものは、読んだファイルにはない）。【一次】[S1]
- そのため歯車で回転数を上げても網の容量は増えず、速く回した機械の消費だけが増える。設定ファイルの説明にも、速度を上げるたびにコストが倍になると書いてある。【一次】[S1][S2][S4]
- 過負荷（overstressed）になった装置について、ゲーム内の案内は、動力源を増やすか負荷の大きい機械を遅くするよう促す。【一次】[S4]
- 水車のコードは周囲の流体の流れの向きを読むだけで、読んだ範囲に水を減らす処理はない。泡の柱や溶岩の流れも回転の元として扱われる。【一次】[S5]
- 風車ベアリングの回転数は帆ブロックの数だけで決まり（既定で帆8枚ごとに1 RPM、1〜16 RPM）、高さや天候を見る処理は読んだメソッドにない。【一次】[S6][S7]
- 蒸気機関のボイラーは、炎・マグマブロック・溶岩・焚き火など（タグ `create:passive_boiler_heaters`）をパッシブ熱（passive heat）として受け付ける。API の説明は、パッシブ熱を無料の熱源（訳。原文「free sources of heat」）に使うものと書いている。【一次】[S9][S10][S11]
- ボイラーに入れた水は貯まらず消えていく（排出の要求には常に空を返す）。水の供給量・ボイラーの大きさ・熱の3つの最小値で出力レベル（最大18）が決まる。【一次】[S9]
- ハンドクランクはプレイヤーが回す。回す速さからプレイヤーの消耗（exhaustion）を計算する係数の設定（既定 0.01）があり、疲れ切る（fully exhausted）まで使う隠し進捗もある。【一次】[S4][S7]
- 応力の値（各ブロックの容量・消費）は設定ファイル（`stressValues.v2`）の項目で、既定値から変えられる。【一次】[S2]
- Create 本体のベアリング類の説明は、回転入力どおりに構造物を回すというもの（時計ベアリングは時刻に合わせて回る）。重力で揺れるという説明はない。【一次】[S4]
- 物理で動く構造物（サブレベル）を扱う mod として、Sable（Rust 製の物理エンジン Rapier を使うライブラリ、1.21.1）と、その上で動く Create Aeronautics（1.21.1・NeoForge のみ）がある。【一次】[S12][S14]
- 関節（ユニバーサルジョイント等）は Aeronautics のアドオン『Transmission & Linkage』にあり、物理構造物の回転を Create の動力に戻す変換ベアリング（kinetic conversion bearing）もある。【一次】[S15]
- 別のアドオン『Gadgets & Gizmos』1.2.0 の Coupler は、サブレベル同士をつなぐ減衰ばね付きのヒンジで、±10度を超えると減衰と復元の力がかかり、最大角は±30度と説明されている。【一次】[S18]
- Valkyrien Skies 2 は 1.20.1 までで、1.21.1 の Sable とは同じ版で並べられない（2026-11-20 取得の Modrinth 表示）。【一次】[S12][S16]

## 詳細

### 1. 読んだソースの版
- Create は GitHub リポジトリ Creators-of-Create/Create の `mc1.21.1/dev` ブランチを raw.githubusercontent.com で読んだ（2026-11-20 取得）。ボイラーのコードは `net.neoforged` のクラスを import しており、NeoForge 版のコードである。このブランチに対応する Create のリリース番号は確認していない。【一次】[S9]
- Fabric 版が同じ数値・同じ計算かは読んでいない（『わかっていないこと・要確認』を参照）。

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
- 各ブロックの既定値は `AllBlocks.java` で登録され、`CStress` がそれを設定項目（設定の名前は `stressValues.v2`）として定義する。つまり表の値は既定値で、設定で変更できる。【一次】[S2][S3]
- `KineticNetwork` は容量と消費の合計を網の各ブロックに `updateFromNetwork` で渡す。両者を比べて過負荷にする処理は `KineticBlockEntity` 側と考えられるが、読んでいない。【一次】[S1]

### 3. 動力源ごとの仕組み（既定値）

| 動力源 | 登録容量（SU、回転数を掛ける前） | 回転数の決まり方 | 何を消費するか | 確度・出典 |
|---|---|---|---|---|
| 水車 | 32 | 流れがあれば 8 ÷ 大きさ RPM（`Mth.clamp(flowScore, -1, 1) * 8 / getSize()`。通常の水車の `getSize()` は 1） | 読んだコードは流れの向きを読むだけ | 【一次】[S3][S5] |
| 大型水車 | 128 | 通常の水車の半分の速さ（ポンダーの説明） | 同上 | 【一次】[S3][S4] |
| 風車ベアリング | 512 | 帆の数 ÷ 8（設定）を 1〜16 に制限 | 読んだメソッドは帆の数だけを見る | 【一次】[S3][S6][S7] |
| 蒸気機関 | 1024 | ボイラーのレベルで効率が決まる | ボイラーへの水と熱源 | 【一次】[S3][S9] |
| ハンドクランク | 8 | プレイヤーが右クリックを押し続けて回す | プレイヤーの消耗（exhaustion）の設定がある | 【一次】[S3][S4][S7] |
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
- 設定 `crankHungerMultiplier`（既定 0.01）の説明は次のとおり。回す速さからプレイヤーの消耗（exhaustion）を計算する係数である。消耗を実際に加える処理（ハンドクランクのブロックのコード）は読んでいない。【一次】[S7]
> 「multiplier used for calculating exhaustion from speed when a crank is turned.」[S7]
- 隠し進捗『Workout Session』の条件は、ハンドクランクを疲れ切る（fully exhausted）まで使うこと。【一次】[S4]
> 「Use a Hand Crank until fully exhausted」[S4]

#### 蒸気機関とボイラー
> 「The minimal setup requires 4 Fluid Tanks」[S4]
> 「With each added power level, an additional Engine can output at full capacity」[S4]
- 大きさで決まる上限はボイラーの大きさ（`getTotalTankSize()` の値）÷ 4（最大18）、水で決まる上限は水の供給量 ÷ 10（最大18）。実際のレベルは熱・水・大きさの最小値。【一次】[S9]
> 「return (int) Math.min(18, boilerSize / 4);」[S9]
> 「private static final int waterSupplyPerLevel = 10;」[S9]
- ボイラーの流体の入口は水だけを受け付け、入ってきた量を供給量として数えるだけで、中身の問い合わせと排出の要求には常に空を返す。入れた水はボイラーに貯まらない。【一次】[S9]
> 「return FluidStack.EMPTY;」[S9]
- 供給量は、5回の処理ごとに、その間に入った量を 5 で割った値を記録し、直近10回分の最大値をとる。水が足りないときのゴーグル表示は、供給量を mB で、レベル1つ分の必要量を 10 mB の「per Tick」として出す。【一次】[S4][S9]
> 「static final int SAMPLE_RATE = 5;」[S9]
> 「%1$s per Tick」[S4]
- 熱源はタンクの真下の1段を調べる。熱が0の熱源（パッシブ熱）しかないときはパッシブ扱いになり、機関の効率は合計で 1/8 になる。【一次】[S9]
> 「private static final float passiveEngineEfficiency = 1 / 8f;」[S9]
- ゴーグルに出す総出力の式は、効率 × 16 × max(レベル, 機関の数) × 蒸気機関の登録容量。【一次】[S9]
> 「double totalSU = getEngineEfficiency(boilerSize) * 16 * Math.max(boilerLevel, attachedEngines)」[S9]
- 蒸気機関はボイラーから効率（0〜1に丸めた値）を受け取り、出力軸に渡す。【一次】[S8]
> 「float efficiency = Mth.clamp(tank.boiler.getEngineEfficiency(tank.getTotalTankSize()), 0, 1);」[S8]
- この式に既定値を入れると、パッシブ熱だけのボイラーは機関の数によらず 2048 SU、レベル18で機関18台なら 294,912 SU になる（自分たちの計算）。【未確認】[S3][S9]

### 4. パッシブ熱＝無料の熱源
- API の説明（`BoilerHeater.java`）は、パッシブ熱を少量で制限の強い熱とし、炎やマグマブロックのような無料の熱源に使うと書いている。【一次】[S10]
> 「passive heat can be used to provide a small amount of heat, highly limiting」[S10]
> 「This is usually used for free sources of heat, such as fire or magma blocks.」[S10]
- パッシブ熱源のタグ `create:passive_boiler_heaters` の中身: `create:blaze_burner`、`create:lit_blaze_burner`、マグマブロック、溶岩、焚き火（タグ `#minecraft:campfires`）、炎（タグ `#minecraft:fire`）。【一次】[S11]
> 「minecraft:magma_block」[S11]
- ポンダーの説明では、ブレイズバーナーがバスンの処理に熱を出すには燃える物を食べさせる必要があり、ブレイズが入っていないバーナーは工業用の加熱に使えない。【一次】[S4]
> 「For this, the Blaze has to be fed with flammable items」[S4]
> 「However, without a blaze they are not suitable for industrial heating」[S4]

### 5. 歯車・変速と過負荷
> 「Shifting from large to small cogs, the conveyed speed will be doubled」[S4]
> 「Shifting the opposite way, the conveyed speed will be halved」[S4]
> 「It appears that this contraption is _overstressed_. Add more sources or _slow_ _down_ the components with a high _stress_ _impact_.」[S4]
- 回転数の上限は設定 `maxRotationSpeed`（既定 256 RPM）。【一次】[S7]
> 「Maximum allowed rotation speed for any Kinetic Block.」[S7]
- フライホイールは、読んだ版のツールチップでは機械を飾るブロックとして説明されている。【一次】[S4]
> 「_Embellish_ your _Machines_ with this imposing Wheel of Brass.」[S4]

### 6. 流体を無限に扱う仕組み（ポンプと組み合わせる場合）
- 十分に大きな海にホース滑車を下ろすと、元の水を減らさずに流体を出し入れできる。【一次】[S4]
> 「It will provide/dispose fluids without affecting the source」[S4]
- パイプの開いた端は、目の前の水源ブロックを吸い上げられ、空いた場所へこぼすと水源を作れる。【一次】[S4]
> 「Source blocks right in front of an open end can be picked up」[S4]
> 「while spilling into empty spaces can create fluid sources」[S4]
- 第三者のアドオン『Create: No Unlimited Energy（NUE）』（Modrinth の表示: 1.20.1・Fabric、Create（Fabric）6.x と Flowing Fluids が必須、MIT、「486ダウンロード」、2026-11-20 取得）は、発電の取水口で少し水を消費させ、閉じたポンプ→水車のループを干上がらせると説明している。【一次】[S19]
> 「No perpetual motion. Generating consumes a little water at the intake, so closed pump→wheel loops run dry; only genuine rain / river / ocean sources sustain.」[S19]
- NUE の作者は、止まった水たまりの水車や閉じたポンプのループが拠点の動力になることを問題と書いている（既定の Create でそれが成立するかの検証ではなく、作者の見方）。【二次】[S19]
> 「Free, easy energy is the bug. A wheel in a still pool — or a sealed pump loop — should not power a base.」[S19]
- 第三者の mod『Flowing Fluids』（Modrinth の表示: 26.3・26.2・26.1.x・1.21.x・1.20–1.20.1、Fabric・Forge・NeoForge・Quilt、LGPL-3.0-only、2026-11-20 取得）は、水源2つで無限の水が作れないようにし、Create の水車とパイプの動作を変える互換設定を持つ。【一次】[S20]
> 「can't just place 2 water source blocks and have infinite water」[S20]
> 「Flowing Fluids has special compatibility settings for use with the Create mod, to modify the behaviour of water wheels and pipes.」[S20]

### 7. 永久機関について、事実から言えること
- 歯車だけで出力を増やすことは計算式の上でできない。容量は発電側の回転数で決まり、変速して速く回した機械は消費が比例して増えるから。【一次】[S1][S2]
- 一方で、読んだコードの範囲では、水車は流れの向きを読むだけ、風車は帆の数だけを見ており、燃料や水を減らす処理はない。ボイラーのコード（`BoilerData`）にも熱源のブロックを減らす処理はなく、API はパッシブ熱を無料の熱源（free sources of heat）向けと書いている。【一次】[S5][S6][S9][S10]
- ただし蒸気機関のボイラーは入れた水を貯めずに消費し続け、ハンドクランクには回す速さからプレイヤーの消耗を計算する設定がある。【一次】[S7][S9]

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
- Modrinth のページからリンクされている Wiki（GitHub の ryanhcode/sable）のトップ（『Depending on Sable』の説明）には、『Working with Sable』として『Block Physics Properties』『Dimension Physics Data』が並んでいる（両ページは raw.githubusercontent.com で 404、中身は未読）。【一次】[S12][S13]

#### 8.3 Create Aeronautics とアドオン
> 「You must have both Sable and Create installed to play Create Aeronautics.」[S14]
> 「Aeronautics currently has visual issues when used with Iris Shaders.」[S14]
- Modrinth の表示（2026-11-20 取得）: 1.21.1、NeoForge のみ、ライセンス Simulated Project License、「9.5Mダウンロード」、公開は「7 か月前」。【一次】[S14]
- 同じページに、The Game Awards 2026 の Best User Creation の候補である旨のバナーが出ている（TGA 側の資料は未読）。【二次】[S14]
> 「Create Aeronautics is one of five nominees.」[S14]
- アドオン『Create Aeronautics: Transmission & Linkage』（1.21.1・NeoForge、CC-BY-NC-4.0、「464.4Kダウンロード」、2026-11-20 取得）: ユニバーサルジョイント、油圧ロッド、ヒンジヘッド、空気圧レギュレーター、変換ベアリングを追加する。【一次】[S15]
> 「Universal joints and joint rods allow separate physics structures to stay connected while still permitting controlled movement.」[S15]
> 「Kinetic conversion bearings convert the rotation of an attached Aeronautics physics structure into Create kinetic output」[S15]
- アドオン『Absolute Kinematics』は、Aeronautics のスイベルベアリングを補う物理ジョイントとしてボールジョイントとヒンジを追加する（CurseForge は 403 で読めず、検索要約のみ。Modrinth の `mod/absolute-kinematics` は「Project not found」、2026-11-20）。【未確認】[S17]
- アドオン『Create Aeronautics: Gadgets & Gizmos』のバージョン 1.2.0（Modrinth の表示: 1.21.1・NeoForge、ライセンス ARR、変更履歴の日付 2026-09-11、2026-11-20 取得）は、Coupler を追加した。サブレベル同士をつなぐ減衰ばね付きのヒンジで、±10度までは減衰の力がなく、それを超えると減衰と復元の力が働き、最大角の±30度に近づくほど強くなる。【一次】[S18]
> 「Dampened spring back hinge for connecting sub-levels.」[S18]
> 「-10 - 10 degrees has no damping force. after that damping and spring back kick in and scale as the angle approaches the maximum angle of -30 - 30 degrees.」[S18]

#### 8.4 Valkyrien Skies 2
> 「Valkryien Skies 2 is in BETA.」[S16]
> 「Notice: Valkyrien Skies is a library mod, you need to download an add-on to use it in ordinary gameplay.」[S16]
- Modrinth の表示（2026-11-20 取得）: 対応は 1.20.1・1.19.2・1.18.2・1.16.5・1.12.2、Fabric と Forge、ライセンス LGPL-3.0-only、「6.3Mダウンロード」、更新は「7 か月前」。原文の BETA の文は綴りが Valkryien になっている。【一次】[S16]
- 船どうし・船と地形・船とプレイヤー・船とエンティティが衝突すると説明され、Create への対応も書かれている。【一次】[S16]
> 「Ship to ship. Ship to world. Ship to player. Ship to entities.」[S16]
> 「Your favorite Create machines just got mobile!」[S16]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。
- **T14 の結論の立て方**: 歯車で増やす永久機関は式の上で無理（根拠: [S1][S2]）。一方で燃料なしで回り続ける機械は、水車・風車で最初から作れ、パッシブ熱のボイラーも燃料は要らない（水の供給は要る）（根拠: [S5][S6][S9][S10]）。ゲームの世界が無料の動力源を用意している、という見せ方ができる。動画の山場は、この2つの違い（閉じた系か、外から無料のエネルギーが入っているか）を見せることにできる。
- **入口探しの実験**: 各動力源について、何がなくなると止まるかを1つずつ消して見せる（水源を壊す、帆を減らす、火を消す、ボイラーへの水を止める、クランクで空腹ゲージを撮る）。蒸気機関の水とハンドクランクの空腹は、エネルギーの入口がゲーム内に見える例として使える（根拠: [S4][S7][S9]）。
- **数値はゴーグルで実測してから言う**: 表の計算例（256 SU、8192 SU、2048 SU など）は式から出した値なので、【実測】にしてから台本に入れる。設定ファイルの値も撮影ワールドで記録する（根拠: [S2][S3][S9]）。
- **ポンプ→水車のループ**: 海のホース滑車やパイプの開口で水を作れるので、水車がポンプを回してその水で回る系が作れるかを実機で確かめる。成立するなら、MCの水は無限であり外部からの入力だ、という説明になる。対照として、水を有限にする『Flowing Fluids』や、取水で水を消費させる『NUE』を入れた場合と比べられる（ただし NUE は 1.20.1・Fabric）（根拠: [S4][S5][S19][S20]。成立は未確認）。
- **T12 の振り子**: 揺れる面が自由でないと面の回転（歳差）は見えないので、1軸のヒンジではなくボールジョイントやユニバーサルジョイントで吊る構成を探す（根拠: [S15][S17]）。『Gadgets & Gizmos』の Coupler は±10度を超えると減衰と復元の力がかかり最大±30度なので、自由な振り子には向かない（根拠: [S18]）。Create 本体のベアリングで作る振り子は、動きを決めて動かしているだけの比較用にできる（根拠: [S4]）。
- **環境は別インスタンス**: Sable と Aeronautics は 1.21.1 なので、計測の基盤（別の版）とは別のインスタンスを立てる。Aeronautics は NeoForge のみ、Iris で表示の問題があるので、撮影は Flashback／Replay Mod とシェーダーの組み合わせを事前に試す（根拠: [S12][S14]。録画 mod の対応は [../filming/Flashback.md](../filming/Flashback.md) を参照）。
- **自動化**: Sable はコマンド `/sable` でサブレベルを組み立てられるので、`experiment.yaml` から RCON で振り子を組む案がある（根拠: [S12]）。

## わかっていないこと・要確認
- `calculateAddedStressCapacity` が登録値をそのまま返すか（容量の計算例の前提）。実機のゴーグル表示で確かめる。
- 読んだブランチに対応する Create のリリース番号。Fabric 版で同じ値・同じ式か。
- ボイラーの水の表示は mB／tick だが、`BoilerData` の処理が毎 tick 呼ばれるか（呼び出し元の `FluidTankBlockEntity` は未読）。`getTotalTankSize()` がタンクのブロック数か。
- ポンプ→水車の閉ループが既定の Create で成立するか（『NUE』の作者は閉じたポンプのループを問題として挙げているが、既定の Create で試した記録ではない）。
- Sable 単体に関節（拘束）を作るコマンドや API があるか。『Block Physics Properties』『Dimension Physics Data』の中身（重力や空気抵抗を設定できるか）。
- Sable の物理（Rapier）が回転座標系を扱うか。数値誤差で振り子の揺れの面がずれるか（T12 で、揺れの面が回らないことを示すための対照実験が要る）。
- スイベルベアリング（Aeronautics 本体）の自由度、『Absolute Kinematics』のボールジョイントの実在と対応版（CurseForge が読めず、Modrinth には同じ名前のページがない）。
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
- [S12] Sable - Minecraft Mod — Modrinth（ソース・Wiki は GitHub の ryanhcode/sable） — https://modrinth.com/mod/sable — 公開「7 か月前」・更新「2 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S13] Sable Wiki: Home — GitHub の ryanhcode/sable の Wiki — https://raw.githubusercontent.com/wiki/ryanhcode/sable/Home.md — 不明 — 取得: 2026-11-20 — 原文: 読んだ
- [S14] Create Aeronautics - Minecraft Mod — Modrinth（Create Aeronautics チーム） — https://modrinth.com/mod/create-aeronautics — 公開「7 か月前」・更新「3 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S15] Create Aeronautics: Transmission & Linkage - Minecraft Mod — Modrinth — https://modrinth.com/mod/create-aeronautics-transmission-linkage — 公開「6 か月前」・更新「3 週間前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S16] Valkyrien Skies - Minecraft Mod — Modrinth — https://modrinth.com/mod/valkyrien-skies — 公開「6 年前」・更新「7 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S17] Absolute Kinematics — CurseForge — https://www.curseforge.com/minecraft/mc-mods/absolute-kinematics — 不明 — 取得: 2026-11-20 — 原文: 検索要約のみ（403。Modrinth の https://modrinth.com/mod/absolute-kinematics は「Project not found」）
- [S18] 1.2.0 - Create Aeronautics: Gadgets & Gizmos — Modrinth — https://modrinth.com/mod/create-aeronautics-gadgets-and-gizmos/version/1.2.0 — 変更履歴「2026-09-11 Version 1.2.0 Release」 — 取得: 2026-11-20 — 原文: 読んだ
- [S19] Create: No Unlimited Energy - Minecraft Mod — Modrinth — https://modrinth.com/mod/create-nue — 公開「5 か月前」・更新「5 か月前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ
- [S20] Flowing Fluids - Minecraft Mod — Modrinth — https://modrinth.com/mod/flowing-fluids — 公開「2 年前」・更新「2 週間前」（取得時の表示） — 取得: 2026-11-20 — 原文: 読んだ（当初の CurseForge のページは読めず、同じ mod の Modrinth のページに差し替えた）
