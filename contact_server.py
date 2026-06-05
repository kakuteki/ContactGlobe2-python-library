# ----------------------------------------------------
# 作成者:加賀日向太
# 作成日:2025/04/26
# ContactGlove 2 のデバイス情報を受信して表示するサンプル
# 参考文献:https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1
# ----------------------------------------------------
import time

from library import ContactGlobe2Client


def main():
    client = ContactGlobe2Client()
    client.connect_divingstation()
    if not client.start_osc_server():
        return

    print("デバイス情報を待機中... (Ctrl+C で終了)")
    try:
        while True:
            info = client.get_device_info()
            if info:
                print(f"デバイス情報: {info}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop_osc_server()


if __name__ == "__main__":
    main()
