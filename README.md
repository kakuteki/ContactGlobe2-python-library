# ContactGlove 2 Python Library

Diver-X 社の触覚グローブ **ContactGlove 2** から、手の姿勢データ（各指関節のクォータニオン）を **OSC（Open Sound Control）** 経由で受信・記録するための Python サンプルコード集です。

母艦ソフト **DivingStation** とローカル UDP で通信し、手のトラッキング結果をリアルタイムに取得します。プロトコルは ContactGlove 2 の公式開発者ドキュメント（プロトコル v1）に準拠しています。

- 参考: [ContactGlove 2 開発者向けドキュメント（プロトコル v1）](https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1)

---

## できること

- DivingStation への接続要求の送信と、手データ受信用 OSC サーバーの起動
- `/DS/HC/HandQuat` で送られてくる手の姿勢データ（5 指 × 各関節のクォータニオン）の受信とパース
- 受信した手データの CSV ファイルへのタイムスタンプ付きロギング
- デバイス情報（`/DS/HC/Device`）の受信
- 関数版・クラス版それぞれのサンプル実装

> 注意: 現時点で完成しているのは「接続 → 手のクォータニオン受信 → CSV 記録」までです。手首・コントローラ情報の取得や触覚フィードバック（Haptics）の送信は未実装です。詳しくは後述の「実装状況」を参照してください。

---

## 動作要件

- Python 3.6 以上
- [python-osc](https://python-osc.readthedocs.io/) ライブラリ
- ContactGlove 2 本体
- DivingStation（ContactGlove 2 の母艦ソフト）。本ライブラリを動かす PC 上で起動しておく必要があります

---

## インストール

1. リポジトリをクローンします。

   ```bash
   git clone https://github.com/kakuteki/ContactGlobe2-python-library.git
   cd ContactGlobe2-python-library
   ```

2. 依存ライブラリをインストールします。

   ```bash
   pip install -r requirements.txt
   ```

---

## 通信の仕組み

本ライブラリと DivingStation は、同一 PC（`127.0.0.1`）上で 2 つの UDP ポートを使って双方向にやり取りします。

```
  [ 本ライブラリ ]                       [ DivingStation ]
        |                                       |
        |  (1) 接続要求 "/DS/HC/Connect"        |
        |  送信先ポート 25790  ----------------> |
        |     ※引数で「受信ポート 25788」を通知 |
        |                                       |
        |  (2) 手データ "/DS/HC/HandQuat" など  |
        | <----------------  送信先ポート 25788 |
        |                                       |
   ポート 25788 で                              |
   OSC サーバーを起動して受信                   |
```

| 用途 | ポート | 向き |
| --- | --- | --- |
| DivingStation への接続要求・各種コマンド送信 | `25790` | 本ライブラリ → DivingStation |
| ContactGlove 2 のデータ受信 | `25788` | DivingStation → 本ライブラリ |

主な OSC アドレス:

| アドレス | 内容 |
| --- | --- |
| `/DS/HC/Connect` | DivingStation への接続要求（引数に受信ポート番号を指定） |
| `/DS/HC/Device` | デバイス情報の受信 |
| `/DS/HC/HandQuat` | 手の姿勢データ（各指関節のクォータニオン）の受信 |

---

## ディレクトリ構成

| ファイル | 説明 |
| --- | --- |
| `hand.py` | メインのサンプル。手のクォータニオンを受信し、`hand_data_log.csv` にタイムスタンプ付きで記録します |
| `contact_server.py` | 接続要求を送り、`/DS/HC/Device` を受信して表示する最小サーバー |
| `contact_client.py` | `/DS/HC/Device` を送る送信テスト用クライアント |
| `osc_server.py` | Diver-X に依存しない、素の OSC 受信ひな形（`/test` を受信） |
| `osc_client.py` | Diver-X に依存しない、素の OSC 送信ひな形（`/test` を送信） |
| `library/contactglobe2_client.py` | 中核となる `ContactGlobe2Client` クラス。接続・サーバー起動/停止・手データ/デバイス情報の受信をメソッド化 |
| `library/__init__.py` | `library` パッケージのエントリ。`ContactGlobe2Client` と `JOINT_NAMES` を公開 |

OSC の疎通だけを確認したい場合は `osc_server.py` / `osc_client.py` から、ContactGlove 2 の実機データを扱いたい場合は `hand.py` から始めると分かりやすい構成です。

---

## 使い方

### 1. 手データを受信して CSV に記録する（`hand.py`）

最も完成度の高いサンプルです。DivingStation を起動した状態で実行してください。

```bash
python hand.py
```

実行すると、

1. DivingStation へ接続要求（`/DS/HC/Connect`）を送信し、
2. ポート `25788` で OSC サーバーを起動して `/DS/HC/HandQuat` の受信を待ち受け、
3. 受信した手の姿勢データをコンソールに表示しつつ、
4. 同じフォルダの `hand_data_log.csv` に 1 フレームずつ追記します（ファイルが無ければヘッダーを自動生成）。

CSV にはタイムスタンプ（Unix 時間）、バージョン、デバイス ID、左右フラグに加え、各指関節のクォータニオンが 1 成分ずつ列として保存されます。

### 2. クラスとして使う（`library/contactglobe2_client.py`）

接続やサーバー管理をまとめて扱いたい場合は `ContactGlobe2Client` を利用します。

```python
from library import ContactGlobe2Client
import time

def on_hand_data(data):
    # data = {"version", "id", "is_left", "joints": {関節名: (x, y, z, w), ...}}
    side = "左" if data["is_left"] else "右"
    print(f"[{side}手] index_mcp =", data["joints"]["index_mcp"])

client = ContactGlobe2Client(
    server_ip="127.0.0.1",
    client_port=25788,         # データ受信ポート
    divingstation_port=25790,  # DivingStation への送信ポート
    hand_callback=on_hand_data,
)

client.connect_divingstation()      # 接続要求を送信
if client.start_osc_server():       # 別スレッドで受信サーバーを起動
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop_osc_server()    # サーバーを停止
```

`hand_callback` を渡すと、手データを受信するたびに整形済みの辞書が渡されます。コールバックを使わず `client.get_hand_data()` で最後に受信した値を取得することもできます。OSC サーバーはデーモンスレッドで動くため、メインプログラムの処理を止めずにバックグラウンドで受信を続けられます。

---

## 受信データの構造（`/DS/HC/HandQuat`）

`/DS/HC/HandQuat` の引数は次の順番で届きます。各指の関節姿勢は、それぞれクォータニオン 4 成分（x, y, z, w）で表現されます。

| 位置 | 内容 |
| --- | --- |
| `args[0]` | バージョン（整数） |
| `args[1]` | デバイス ID（文字列） |
| `args[2]` | 左手かどうか（真偽値） |
| `args[3:7]` | 親指 CMC 関節のクォータニオン |
| `args[7:11]` | 親指 MCP 関節 |
| `args[11:15]` | 親指 IP 関節 |
| `args[15:27]` | 人差し指（MCP / PIP / DIP の順に各 4 成分） |
| `args[27:39]` | 中指（MCP / PIP / DIP） |
| `args[39:51]` | 薬指（MCP / PIP / DIP） |
| `args[51:63]` | 小指（MCP / PIP / DIP） |

合計で 5 指分・15 関節のクォータニオンが 1 フレームとして送られてきます。

---

## 設定

スクリプト内で、用途に応じて次の項目を書き換えてください。

- OSC 通信の IP アドレスとポート番号（既定はローカル `127.0.0.1`、受信 `25788` / 送信 `25790`）
- 受信時に呼ばれるコールバック処理（`dispatcher.map(...)` で割り当て）
- CSV の出力先ファイル名やヘッダー（`hand.py` 内）

---

## 実装状況

| 機能 | 状態 |
| --- | --- |
| DivingStation への接続要求 | 実装済み |
| 手の姿勢データ（HandQuat）の受信・パース | 実装済み（クラス版・`hand.py` の両方） |
| 受信データの CSV ロギング | 実装済み（`hand.py`） |
| デバイス情報（Device）の受信 | 実装済み |
| 手首・コントローラ情報の取得 | 未実装 |
| 触覚フィードバック（Haptics）の送信 | 未実装 |

手データの受信は `ContactGlobe2Client` に集約済みで、クラスを import するだけで取得できます。手首・コントローラ情報や送信系（Haptics）はこれから拡張していく構成です。

---

## 参考リンク

- [ContactGlove 2 開発者向けドキュメント（プロトコル v1）](https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1)
- [python-osc ドキュメント](https://python-osc.readthedocs.io/)
