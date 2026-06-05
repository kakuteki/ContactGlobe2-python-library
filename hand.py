# ----------------------------------------------------
# 作成者:加賀日向太
# 作成日:2025/04/26
# ContactGlove 2 から手の姿勢データを受信し CSV に記録するサンプル
# 参考文献:https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1
# ----------------------------------------------------
import csv
import os
import time

from library import ContactGlobe2Client, JOINT_NAMES

CSV_FILENAME = "hand_data_log.csv"

# CSV のヘッダー。各関節クォータニオンを 4 成分（0-3）ずつ列に展開する
FIELDNAMES = ["timestamp", "version", "id", "is_left"] + [
    f"{name}_{axis}" for name in JOINT_NAMES for axis in range(4)
]


def build_row(data):
    """受信した手データ辞書を CSV の 1 行（辞書）へ整形する。"""
    row = {
        "timestamp": time.time(),  # Unix 時間（マイクロ秒精度）
        "version": data["version"],
        "id": data["id"],
        "is_left": data["is_left"],
    }
    for name, quat in data["joints"].items():
        for axis, value in enumerate(quat):
            row[f"{name}_{axis}"] = value
    return row


def main():
    # ファイルが無い／空のときだけヘッダーを書く
    write_header = (not os.path.isfile(CSV_FILENAME)
                    or os.path.getsize(CSV_FILENAME) == 0)
    csv_file = open(CSV_FILENAME, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
    if write_header:
        writer.writeheader()

    def on_hand_data(data):
        writer.writerow(build_row(data))
        csv_file.flush()  # 異常終了時も直近のデータを残す

    client = ContactGlobe2Client(hand_callback=on_hand_data)
    client.connect_divingstation()
    if not client.start_osc_server():
        csv_file.close()
        return

    print(f"手データを {CSV_FILENAME} に記録中... (Ctrl+C で終了)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop_osc_server()
        csv_file.close()
        print("記録を終了しました。")


if __name__ == "__main__":
    main()
