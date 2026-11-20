# mod・シェーダーの利用条件

> 対象: 撮影・計測に使う予定の mod・シェーダーパックについて、ライセンスの種類と、動画・配信での利用、再配布（配布ワールド・modpack）、クレジットに関する条件を、各 mod の公式ページ（Modrinth）と LICENSE の本文から整理する。
> 使う場面: 使う mod・シェーダーを決めるとき（`mc/mods.yaml` に記録するとき）、説明欄のクレジットを書くとき、視聴者向けにワールドや modpack を配るとき、自作の撮影用 mod を作るとき。
> 調査日: 2026-11-19 ／ mc_version: Java Edition。各 mod の対応版は Modrinth の表示（2026-11-19 取得）で、範囲は 1.7.10〜26.4-snapshot-10。ライセンス本文は取得時点の、参照先の URL に書いたブランチ（develop / master / main / HEAD）のもの（過去の版のライセンスは未確認）。
> 関連: [Mojang利用ガイドライン.md](Mojang利用ガイドライン.md)（ゲーム画面そのものの扱い）, [../mods/バージョン対応表.md](../mods/バージョン対応表.md), [../filming/シェーダーと画質mod.md](../filming/シェーダーと画質mod.md), [../filming/ReplayMod.md](../filming/ReplayMod.md), [../filming/Flashback.md](../filming/Flashback.md), [../mods/物理系mod.md](../mods/物理系mod.md), [../mods/Carpet.md](../mods/Carpet.md), [../mods/計測と可視化のmod.md](../mods/計測と可視化のmod.md), [AI生成・改変コンテンツの開示.md（movie）](https://github.com/mitsuo822/movie/blob/main/knowledge/youtube/AI生成・改変コンテンツの開示.md)（YouTube の『第三者の企業によるトレーニング』設定）

## 要点
- 動画での利用を**ライセンスの文面で明示的に許可**しているのは、読んだ範囲では Complementary（License Agreement 1.8）、BSL（Modrinth 本文の AGREEMENT）、Photon（LICENSE）の3つのシェーダーだけ。【一次】[S13][S14][S16]
- Complementary のライセンスは、Complementary を使って撮ったゲーム映像を**AIモデルの学習に使うことを明示的に禁止**している（2.1）。【一次】[S13]
- Photon は、商業的に公開するスクリーンショットと動画での利用を明示的に許可している。制作者に直接・間接の金銭的な見返りを与えるプラットフォーム（例として Modrinth・CurseForge）での再配布は、作者の明示の書面の許可が要る。【一次】[S16]
- BSL は動画・スクリーンショットでの利用を許可し、許可のない再配布と、収益型のURL短縮サービスで作者のサイトやファイルにリンクすることを禁止している。【一次】[S14]
- 録画 mod の Flashback は Modrinth で ARR と表示され、LICENSE.md は再配布を禁止し全権利を留保している。動画利用についての記述は LICENSE.md にない。【一次】[S3][S4]
- Replay Mod は GPL-3.0-or-later。GPL v3 の本文は、プログラムを実行した出力は、その内容自体がプログラム（の派生物）でない限りライセンスの対象にならないと書いている。【一次】[S1][S2]
- Sodium の Modrinth のライセンス表示は Polyform Shield 1.0.0（2026-11-19 取得）。競合する製品を提供する目的以外なら、どの目的でも使える条件。【一次】[S8][S9]
- Iris、Distant Horizons、MiniHUD 系（Tweakeroo、Litematica、Servux、malilib）、Valkyrien Skies は LGPL-3.0-only、Carpet は MIT と Modrinth に表示されている。【一次】[S6][S10][S19][S20][S21][S22][S23][S27][S18]
- Create（Forge/NeoForge 版）は、`./src/main/resources/assets/` 以下のファイルが All Rights Reserved、それ以外（コード）が MIT の2本立て。Create Fabric は Modrinth で MIT と表示。【一次】[S24][S25][S26]
- Physics Mod は Modrinth で ARR と表示。動画での利用条件は、公式ページ・README からは確認できなかった。【一次】[S28][S29]
- 読んだライセンスの文面のうち、**動画の中や説明欄でのクレジット表記を義務付けているものはなかった**（クレジットや表示を求める条項は、modpack・改変版・ソフトウェアの複製の配布に対するもの）。【一次】[S13][S14][S16][S25][S9]

## 詳細

### ライセンスの本文が何を縛っているか
ここでは条文の文言だけを示す。動画が配布に当たるかどうかといった法的な判断は、この調査では行っていない（下の、わかっていないこと・要確認の節を参照）。

- **GPL v3**（Replay Mod、WorldEdit）: 第2条は、改変していないプログラムを実行する権利を無制限に認め、実行の出力は内容がプログラム（の派生物）を構成する場合だけ対象になると書いている。【一次】[S2]
  > 「This License explicitly affirms your unlimited permission to run the unmodified Program. The output from running a covered work is covered by this License only if the output, given its content, constitutes a covered work.」[S2]
- **LGPL v3**（Iris、Distant Horizons、MiniHUD 系、Valkyrien Skies）: LGPL v3 は GPL v3 の条件を取り込み、追加の許可を加えたものだと本文の冒頭に書かれている。【一次】[S7]
  > 「This version of the GNU Lesser General Public License incorporates the terms and conditions of version 3 of the GNU General Public License」[S7]
- **MIT**（Carpet、Create のコード、Create Fabric）: 条件は、著作権表示と許諾表示をソフトウェアの複製に含めること。【一次】[S25]
  > 「The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.」[S25]
- **Polyform Shield 1.0.0**（Sodium、Sable）: 競合する製品の提供以外はどの目的でも使える。無料でも競合になると明記されている。【一次】[S9]
  > 「Any purpose is a permitted purpose, except for providing any product that competes with the software or any product the licensor or any of its affiliates provides using the software.」[S9]
  > 「Goods and services compete even when provided free of charge.」[S9]
- **ARR（All Rights Reserved）**: Flashback、BSL、Bliss、Physics Mod の Modrinth 表示。Flashback の LICENSE.md の本文は `Do not redistribute.` と `All rights reserved.` だけで、利用（動画を含む）についての許可の条項はない。【一次】[S3][S4][S14][S17][S28]

### 一覧（2026-11-19 取得）

| 名前 | 用途 | ライセンス（Modrinth の表示） | 動画での利用についての本文の記述 | 再配布 | 対応版（Modrinth 表示の最新／最古）・ローダー | 確度・出典 |
|---|---|---|---|---|---|---|
| Replay Mod | 録画・レンダリング | GPL-3.0-or-later | 記述なし（GPL 第2条の出力の扱いは上記） | GPL の条件で可 | 26.3／1.8・Fabric, Forge | 【一次】[S1][S2] |
| Flashback | 録画・編集 | ARR | 記述なし | 禁止（`Do not redistribute.`） | 26.3／1.21・Fabric | 【一次】[S3][S4][S5] |
| Sodium | 描画の最適化 | Polyform Shield 1.0.0 | 記述なし | 条件つきで可（Notices の条項） | 26.3／1.16.3・Fabric, NeoForge, Quilt | 【一次】[S8][S9] |
| Iris | シェーダーの読み込み | LGPL-3.0-only | 記述なし | LGPL の条件で可 | 26.3／1.16.5・Fabric, NeoForge, Quilt | 【一次】[S6][S7] |
| Distant Horizons | 遠景（LOD） | LGPL-3.0-only | 記述なし（Modrinth 本文） | LGPL の条件で可 | 26.3／1.12.2・Fabric, Forge, NeoForge | 【一次】[S10] |
| Complementary（Reimagined / Unbound） | シェーダー | Custom（Complementary License Agreement 1.8） | **明示的に許可**。AI 学習への映像の利用は禁止 | modpack への追加・改変版の配布は条件つき | 26.3／1.7.10（Reimagined）・1.7.x（Unbound）・Iris, OptiFine | 【一次】[S11][S12][S13] |
| BSL Shaders | シェーダー | ARR（Modrinth 本文に AGREEMENT あり） | **明示的に許可** | 許可なしは禁止 | 26.3／1.7.10・Iris, OptiFine | 【一次】[S14] |
| Photon | シェーダー | 取得したテキストでは欄が空。LICENSE は独自の Photon Shaders License Agreement | **明示的に許可**（商業的な公開も） | 条件つきで可。modpack への同梱は可 | 26.3／1.16.5・Iris, OptiFine | 【一次】[S15][S16] |
| Bliss | シェーダー | ARR | 記述なし（Modrinth 本文） | 記述なし | 26.3／1.17・Iris, OptiFine | 【一次】[S17] |
| Carpet | 計測（偽プレイヤー・ログ） | MIT | 記述なし | MIT の条件で可 | 26.3／1.14.4・Fabric | 【一次】[S18] |
| MiniHUD | 表示（座標・速度など） | LGPL-3.0-only | 記述なし | LGPL の条件で可 | 26.3／1.8・Fabric ほか | 【一次】[S19] |
| Tweakeroo / Litematica / Servux / malilib | 補助・設計図・サーバ連携・前提ライブラリ | いずれも LGPL-3.0-only | 記述なし | LGPL の条件で可 | — | 【一次】[S20][S21][S22][S23] |
| WorldEdit | 装置作り | GPL-3.0-only | 記述なし | GPL の条件で可。modpack への同梱は明示の許可なしで可（Modrinth 本文の FAQ） | — | 【一次】[S35] |
| Fabric API | 前提ライブラリ | Apache-2.0 | 記述なし | — | 26.4-snapshot-10／1.14・Fabric | 【一次】[S34] |
| Create | 物理系の題材 | Create Mod License（コード MIT・assets は ARR） | 記述なし | assets は ARR | 1.21.1／1.18.2・Forge, NeoForge | 【一次】[S24][S25] |
| Create Fabric | 同上（Fabric 移植） | MIT | 記述なし | MIT の条件で可 | 1.20.1／1.18.2・Fabric, Quilt | 【一次】[S26] |
| Valkyrien Skies | 物理系の題材 | LGPL-3.0-only | 記述なし | LGPL の条件で可 | 1.20.1／1.12.2・Fabric, Forge | 【一次】[S27] |
| Physics Mod | 物理系の題材 | ARR | 記述なし（Modrinth 本文・README） | 記述なし | 26.4-snapshot-10／1.16.5・Fabric, Forge, NeoForge, Quilt | 【一次】[S28][S29] |
| Create: Aeronautics | 物理系の題材 | Simulated Project License（コード MIT・assets は ARR） | 記述なし | assets は ARR | 1.21.1・NeoForge | 【一次】[S31][S32] |
| Sable | 物理系の題材 | PolyForm Shield License 1.0.0 | 記述なし | 条件つきで可 | 1.21.1・Fabric, NeoForge | 【一次】[S33] |

- 表の記述なしは、読んだページ（Modrinth の本文・README・LICENSE）に動画・配信・スクリーンショットについての記述が見当たらなかったという意味で、禁止という意味ではない。
- 対応版の詳細（間の抜けている版など）は [../mods/バージョン対応表.md](../mods/バージョン対応表.md) で扱う。

### 録画: Replay Mod と Flashback
- Replay Mod は、記録したカメラパスを、画面録画ソフトを使わずに動画へレンダリングできると公式ドキュメントに書いている。【一次】[S37]
  > 「With the Replay Mod, you can render Camera Paths to videos without using a screen recording tool like Fraps.」[S37]
- Replay Mod のライセンスは GPL-3.0-or-later（Modrinth 表示）。リポジトリの LICENSE.md は GPL v3（29 June 2007）の全文。【一次】[S1][S2]
- Flashback の README は冒頭で再アップロードと再配布を禁止している。【一次】[S5]
  > 「Copyright 2024 Moulberry. Do not reupload or redistribute.」[S5]
- Flashback は外部からのコードの貢献を受け付けていない。【一次】[S5]
  > 「Flashback currently does not accept outside contributions」[S5]
- Flashback の翻訳ファイルだけは CC BY 4.0（日本語は hqnkuh・stabery）。【一次】[S4]
- Flashback の Modrinth の説明は、ゲームの記録・再生と映画的なショットの作成を目的としている。【一次】[S3]
  > 「Record your Minecraft gameplay, play it back and create stunning cinematic shots」[S3]

### 描画: Sodium、Iris、Distant Horizons
- Sodium の LICENSE.md は PolyForm Shield License 1.0.0 の全文で、Modrinth の表示も Polyform Shield 1.0.0（2026-11-19 取得）。【一次】[S8][S9]
- Polyform Shield は、ソフトウェアを受け取った人にライセンスの条件（または URL）と `Required Notice:` で始まる行を渡すことを求めている（配布するとき）。【一次】[S9]
- Polyform Shield は、法律上のフェアユースの権利を制限しないと書いている。【一次】[S9]
- Iris と Distant Horizons の組み合わせ（互換性）は [../filming/シェーダーと画質mod.md](../filming/シェーダーと画質mod.md) で扱う。

### シェーダー: Complementary
- リポジトリの License.txt は『Complementary License Agreement 1.8』（2026-11-19 取得）。Modrinth のライセンス表示は Reimagined・Unbound とも Custom。【一次】[S11][S12][S13]
- 1.1 は、通常の利用（Normal Usage）としてゲームプレイ、映像を使った動画制作、ライブ配信を挙げている。【一次】[S13]
  > 「Using gameplay footage recorded while using The Pack to create other video content」[S13]
  > 「Streaming live gameplay footage while using The Pack」[S13]
- 通常の利用に当たらないものとして、パックの（一部の）再配布とコードの改変が明記されている（0.2）。【一次】[S13]
- 2.1 は、このパックを使って作ったコード・素材・**ゲーム映像**を AI モデル・機械学習・ニューラルネットワークの学習に使うことを禁止している。【一次】[S13]
  > 「It is explicitly disallowed to use any code, material, or gameplay footage that was made with the aid of This Pack for the purpose of training artificial intelligence models」[S13]
- modpack に入れる条件（1.2）: 新規ユーザーに既定で有効なら modpack の説明ページでクレジットする、内容を一切変更しない、Modrinth か CurseForge の既存の仕組みで追加する（ファイルの直接アップロードでの再配布は不可）。【一次】[S13]
  > 「This Pack must be visibly credited in the Modpack's description page(s) if This Pack is enabled by default for new users of the Modpack.」[S13]
  > 「It is not allowed to redistribute This Pack using a direct file upload.」[S13]
- 改変版の配布（1.3）は、名前に Complementary を含めない、昼の地上の見た目が目に見えて違う、人が書いたコードの追加がかなりある、などの条件つき。【一次】[S13]
- 許可（Grants）に明記されていない利用は All Rights Reserved として扱い、避けるよう書かれている（2.2）。【一次】[S13]
- ライセンスは、その License.txt が入っている版にだけ適用され、同じ文面を含まない過去・将来の版には適用されない（3.3）。【一次】[S13]
  > 「This agreement only applies to the version of This Pack that this exact file can be found in.」[S13]

### シェーダー: BSL、Photon、Bliss
- BSL の Modrinth の AGREEMENT は、スクリーンショットと動画での利用、個人利用での改変を許可している。【一次】[S14]
  > 「Use this shaderpack for taking screenshots and videos.」[S14]
- BSL の禁止事項: 許可のない再配布、自作だと主張する（名前を変える）こと、収益型のURL短縮サービスで作者のサイトやファイルにリンクすること。【一次】[S14]
  > 「Redistribute the shaderpack without my permission.」[S14]
  > 「Use monetized URL shorteners to my site or files.」[S14]
- BSL の公式サイトは capttatsu.com と Modrinth に書かれている（このサイトは今回の取得対象外で未読）。【一次】[S14]
- Photon の LICENSE（Copyright © 2021-2025 Benjamin Stott）は、商業的に公開するスクリーンショット・動画を含む利用を許可している。【一次】[S16]
  > 「Use Photon Shaders, including for commercially published screenshots and videos.」[S16]
- Photon は、改変・未改変の（部分の）再配布を認める一方、制作者に直接・間接の金銭的な見返りを与えるプラットフォーム（例: Modrinth、CurseForge）での再配布と、複製と引き換えにお金を求めることは、書面の許可なしには禁止している。【一次】[S16]
  > 「You may not redistribute Photon Shaders or derivative works on platforms that provide direct or indirect monetary compensation to creators (e.g. Modrinth, CurseForge) without my explicit written permission.」[S16]
- Photon は、（商業的な）modpack の一部としての再配布を許可している。【一次】[S16]
  > 「Redistribute Photon Shaders as part of a (commercial) Modpack.」[S16]
- Bliss は Modrinth で ARR。動画での利用についての記述は Modrinth の本文になかった。【一次】[S17]

### 物理系の mod
- Create の LICENSE.md は、`./src/main/resources/assets/` 以下を All Rights Reserved、それ以外を MIT としている。【一次】[S25]
  > 「All other files are licensed under the MIT License:」[S25]
- Create（本流）は Forge と NeoForge 用で、Fabric 向けには移植版（Create Fabric）がある。Create Fabric の Modrinth 表示は MIT、対応は 1.18.2〜1.20.1。【一次】[S24][S26]
- Create: Aeronautics のリポジトリ（Simulated-Project）の LICENSE.md も、assets 以下を All Rights Reserved、それ以外を MIT とする同じ形。【一次】[S32]
- Physics Mod は Modrinth で ARR、クライアント側の mod。GitHub の README は開発者向けの情報（シェーダー連携・Ragdoll API）だけで、利用条件の記述はない。【一次】[S28][S29]
- Physics Mod の GitHub の README は、シェーダー連携の説明の中で『Physics Mod Pro』のバージョン番号に触れている（Pro 版が有料かどうか、入手方法は README には書かれていない）。【一次】[S29]
  > 「Physics Mod Pro v170」[S29]

### 装置作り: WorldEdit
- WorldEdit の Modrinth の表示は GPL-3.0-only。本文の FAQ は、明示の許可を求めずに modpack に入れてよいと答え、このページか GitHub Sponsors へのリンクがあればありがたい（appreciated）と書いている。【一次】[S35]
  > 「You are free to include WorldEdit, without having to asking for explicit permission.」[S35]
  > 「A link back to this page or our GitHub Sponsors would be appreciated, however.」[S35]

### YouTube の『第三者の企業によるトレーニング』設定との関係
- YouTube には、AI モデルを作る第三者の企業にチャンネルの動画を学習に使わせる設定があり、既定はオフで、オンにすると（YouTube Studio を使うクリエイターの場合）チャンネルの対象の動画がすべて含まれる（設定の詳細は movie の [AI生成・改変コンテンツの開示.md](https://github.com/mitsuo822/movie/blob/main/knowledge/youtube/AI生成・改変コンテンツの開示.md) の §10）。Complementary の 2.1（映像の AI 学習への利用の禁止）との関係は下の提案の節に書く。【一次】[S36]

## このチャンネルでの使い方（提案）
> ※この節は上の事実から導いた提案で、事実ではない。法的な助言でもない。

- **シェーダーは、動画での利用を明文で許可している Complementary・BSL・Photon から選ぶ。** Bliss のように明文が見当たらないものは、作者に確認できるまで本編の撮影には使わない。（根拠: [S13][S14][S16][S17]）
- **Complementary を使うなら、YouTube の『第三者の企業によるトレーニング』は既定のオフのままにする。** この設定はチャンネル単位で全動画が対象になるため、1本でも Complementary の映像があれば 2.1 と衝突するおそれがある。自分たちで映像を機械学習に使う計画（例: 映像から物体を自動追跡するモデルの学習）も、Complementary の映像では行わない。（根拠: [S13][S36]）
- **説明欄に、使った mod・シェーダーの名前と公式ページ（Modrinth）へのリンクを書く。** 義務ではないが、視聴者が再現する手がかりになる。BSL へのリンクには収益型の短縮URLを使わない。（根拠: [S13][S14][S16]）
- **視聴者に配るワールドや modpack に、Flashback・BSL の本体を同梱しない。** Complementary を入れるなら Modrinth/CurseForge の仕組みで追加し、説明ページにクレジットを書き、中身を変えない。Photon は modpack への同梱を許可しているが、Modrinth・CurseForge での再配布には許可が要るので、どちらに当たるかを作者に確認してから入れる。（根拠: [S4][S5][S13][S14][S16]）
- **`mc/mods.yaml` には、ライセンス名だけでなく、動画利用の明文の有無・再配布の可否・確認日・出典URLも書く。** Complementary はライセンスが版ごとに適用されると明記しており、版を上げたら License.txt を読み直す。（根拠: [S13][S8]）
- **自作の撮影用クライアント mod（`docs/MC実行基盤.md` §4 の全自動の段階）を作るときは、Flashback のコードを流用しない。** Flashback は全権利留保で再配布も禁止している。Replay Mod のコードを参考にして公開するなら GPL の条件を確認する。Sodium の上に作る場合は、Sodium と競合する製品にならないことを確認する。（根拠: [S2][S4][S5][S9]）
- **物理系の題材で Create・Create: Aeronautics・Physics Mod を使う回は、動画での利用について作者の公式の案内（Discord・公式サイト）を確認してから撮る。** assets が ARR、または ARR で、読んだ範囲に動画利用の明文がないため。（根拠: [S25][S28][S32]）

## わかっていないこと・要確認
- **ARR の mod（Flashback、Physics Mod、Bliss）や ARR の assets（Create、Create: Aeronautics）が映った動画を収益化してよいか**、本文に明文がない。作者の Discord や FAQ で公式の案内を探す。
- **GPL・LGPL・MIT・Polyform Shield の mod で撮った動画が、ライセンス上の配布や出力（GPL の output）に当たるかどうか**の法的判断（日本法での扱いを含む）。弁護士や公的機関の解説は今回読んでいない。
- Physics Mod の公式サイト（minecraftphysicsmod.com）と Pro 版の利用条件・入手方法。検索要約では、Pro 版は有料で、公式サイトに PRO VERSION のページがあるとされるが、原文は読めていない【未確認】（検索要約のみ・原文未読）[S30]。公式サイトはこの環境から読めず（プロキシが 403）、CurseForge のページも 403 で読めなかった。Modrinth のページには Patreon と Ko-fi の寄付リンクがあるが、Pro 版との関係は書かれていない。[S28]
- BSL の公式サイト（capttatsu.com）と Complementary の公式サイトにある FAQ・利用条件の詳細（未読）。
- Sodium の過去の版のライセンスが今と同じか（今回は最新の LICENSE.md と Modrinth の現在の表示だけを読んだ）。
- Photon の、制作者に金銭的な見返りがあるプラットフォームでの再配布には許可が要るという条項と、modpack の一部としての再配布は可という条項が、Modrinth 上の modpack にどう適用されるか。
- Complementary Unbound の配布ファイルに入っている License.txt の本文（今回読んだのは ComplementaryReimagined リポジトリの License.txt だけ。ライセンスは同じ文面を含む版にしか適用されないと 3.3 に書かれているため、Unbound も同じ 1.8 かは未確認）。
- Distant Horizons・MiniHUD 系・Valkyrien Skies・Carpet・Create Fabric・WorldEdit・Fabric API・Sable・Bliss の LICENSE ファイルの本文は未読（Modrinth の表示だけ）。
- リソースパック（テクスチャ）の利用条件は今回調べていない。バニラ以外のリソースパックを使う場合は個別に調べる。
- ゲーム画面そのもの（Minecraft の映像）の収益化の条件は Mojang 側の規約の範囲で、[Mojang利用ガイドライン.md](Mojang利用ガイドライン.md) を参照。

## 参照先
- [S1] ReplayMod - Minecraft Mod — Modrinth（ReplayMod） — https://modrinth.com/mod/replaymod — Modrinth 表示「先月 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S2] ReplayMod LICENSE.md（GNU General Public License v3） — ReplayMod（GitHub） — https://raw.githubusercontent.com/ReplayMod/ReplayMod/develop/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S3] Flashback - Minecraft Mod — Modrinth（Moulberry） — https://modrinth.com/mod/flashback — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S4] Flashback LICENSE.md — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S5] Flashback README.md — Moulberry（GitHub） — https://raw.githubusercontent.com/Moulberry/Flashback/master/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S6] Iris Shaders - Minecraft Mod — Modrinth（IrisShaders） — https://modrinth.com/mod/iris — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S7] Iris LICENSE（GNU Lesser General Public License v3） — IrisShaders（GitHub） — https://raw.githubusercontent.com/IrisShaders/Iris/HEAD/LICENSE — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S8] Sodium - Minecraft Mod — Modrinth（CaffeineMC） — https://modrinth.com/mod/sodium — Modrinth 表示「先週 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S9] Sodium LICENSE.md（PolyForm Shield License 1.0.0） — CaffeineMC（GitHub） — https://raw.githubusercontent.com/CaffeineMC/sodium/HEAD/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S10] Distant Horizons - Minecraft Mod — Modrinth — https://modrinth.com/mod/distanthorizons — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S11] Complementary Shaders - Reimagined — Modrinth（Complementary Development） — https://modrinth.com/shader/complementary-reimagined — Modrinth 表示「17 時間前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S12] Complementary Shaders - Unbound — Modrinth（Complementary Development） — https://modrinth.com/shader/complementary-unbound — Modrinth 表示「17 時間前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S13] Complementary License Agreement 1.8（License.txt） — ComplementaryDevelopment（GitHub） — https://raw.githubusercontent.com/ComplementaryDevelopment/ComplementaryReimagined/main/License.txt — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S14] BSL Shaders - Minecraft Shader — Modrinth（capttatsu） — https://modrinth.com/shader/bsl-shaders — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S15] Photon Shaders - Minecraft Shader — Modrinth（sixthsurge） — https://modrinth.com/shader/photon-shader — Modrinth 表示「先月 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S16] Photon Shaders License Agreement（LICENSE） — sixthsurge（GitHub） — https://raw.githubusercontent.com/sixthsurge/photon/HEAD/LICENSE — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S17] Bliss Shaders - Minecraft Shader — Modrinth — https://modrinth.com/shader/bliss-shader — Modrinth 表示「昨年 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S18] Carpet - Minecraft Mod — Modrinth（gnembon） — https://modrinth.com/mod/carpet — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S19] MiniHUD - Minecraft Mod — Modrinth（masa） — https://modrinth.com/mod/minihud — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S20] Tweakeroo - Minecraft Mod — Modrinth（masa） — https://modrinth.com/mod/tweakeroo — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S21] Litematica - Minecraft Mod — Modrinth（masa） — https://modrinth.com/mod/litematica — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S22] Servux - Minecraft Mod — Modrinth（masa） — https://modrinth.com/mod/servux — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S23] MaLiLib - Minecraft Mod — Modrinth（masa） — https://modrinth.com/mod/malilib — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S24] Create - Minecraft Mod — Modrinth（Creators of Create） — https://modrinth.com/mod/create — Modrinth 表示「7 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S25] Create LICENSE.md（License Overview） — Creators-of-Create（GitHub） — https://raw.githubusercontent.com/Creators-of-Create/Create/HEAD/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S26] Create Fabric - Minecraft Mod — Modrinth（Fabricators of Create） — https://modrinth.com/mod/create-fabric — Modrinth 表示「昨年 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S27] Valkyrien Skies - Minecraft Mod — Modrinth — https://modrinth.com/mod/valkyrien-skies — Modrinth 表示「7 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S28] Physics Mod - Minecraft Mod — Modrinth（Haubna） — https://modrinth.com/mod/physicsmod — Modrinth 表示「昨日 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S29] Physics Mod README.md — haubna（GitHub） — https://raw.githubusercontent.com/haubna/PhysicsMod/main/README.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S30] PRO VERSION — Physics Mod 公式サイト — https://minecraftphysicsmod.com/pro — 不明 — 取得: 2026-11-19（取得を試みたがプロキシが 403） — 原文: 検索要約のみ
- [S31] Create Aeronautics - Minecraft Mod — Modrinth — https://modrinth.com/mod/create-aeronautics — Modrinth 表示「3 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S32] Simulated-Project LICENSE.md（License Overview） — Creators-of-Aeronautics（GitHub） — https://raw.githubusercontent.com/Creators-of-Aeronautics/Simulated-Project/main/LICENSE.md — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S33] Sable - Minecraft Mod — Modrinth — https://modrinth.com/mod/sable — Modrinth 表示「2 か月前 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S34] Fabric API - Minecraft Mod — Modrinth — https://modrinth.com/mod/fabric-api — Modrinth 表示「一昨日 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S35] WorldEdit - Minecraft Plugin — Modrinth — https://modrinth.com/plugin/worldedit — Modrinth 表示「先月 に更新」 — 取得: 2026-11-19 — 原文: 読んだ
- [S36] コンテンツと第三者の企業によるトレーニング - YouTube ヘルプ — Google — https://support.google.com/youtube/answer/15509945?hl=ja — 不明 — 取得: 2026-11-19 — 原文: 読んだ
- [S37] Replay Mod Documentation — Replay Mod — https://www.replaymod.com/docs/ — 不明 — 取得: 2026-11-19 — 原文: 読んだ
