# 計測用サーバの立て方（Windows）

E001（P1）はバニラのサーバだけで動く。mod（Fabric）が必要になるのは撮影の段階（P2）から。

## 1. 準備

1. Java 21 以上を入れる（`java -version` で確認）。必要なJavaのバージョンはMCのバージョンで違う【未確認】。
2. このフォルダ（`mc/server/`）に、公式サイトからサーバの jar を置く（例: `server.jar`）。jar とワールドは git に入らない。
3. 初回起動:
   ```powershell
   cd mc\server
   java -Xmx4G -jar server.jar nogui
   ```
   止まったら `eula.txt` を `eula=true` に書き換える。
4. `server.properties` を `server.properties.example` のとおりに書き換える。
   **ワールドを平らにするため、書き換えたあとに `world` フォルダを消してから**もう一度起動する。

## 2. Python の準備（リポジトリの一番上で）

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest            # 模擬サーバでの試験。5件通ればよい
```

## 3. 計測

```powershell
$env:MC_RCON_PASSWORD = "server.properties に書いたパスワード"
python -m lab run experiments\E001_free_fall\experiment.yaml --dry-run      # 送るコマンドの確認
python -m lab run experiments\E001_free_fall\experiment.yaml --mc-version 1.21.x
```

結果は `experiments/E001_free_fall/results/run_日時/` に出る（CSV、results.json、summary.md、グラフ）。
クライアントでサーバに入って見ていてもよい（その場合も計測には影響しないはず【未確認】）。

## 4. うまくいかないとき

| 症状 | 見るところ |
|---|---|
| RCON に接続できない | サーバの起動ログに `RCON running on 0.0.0.0:25575` が出ているか。パスワード |
| 「ゲーム時刻が進みません」 | `pause-when-empty-seconds=0` になっているか。`tick step` が使えるバージョンか（1.20.3以降） |
| 召喚に失敗する（応答が summary.md でなく実行ログに出る） | NBTの書式がバージョンに合っているか（`experiment.yaml` の `entities`） |
| エンティティが動かない | `forceload` が効いているか。豚に NoAI を付けていないか |
| 値の読み取りでエラー | 応答の書式が違う。`lab/parse.py` を直す（応答の文字列を控えておく） |
