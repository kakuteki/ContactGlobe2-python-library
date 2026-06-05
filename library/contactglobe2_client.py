# ----------------------------------------------------
# ContactGlove 2 に OSC で接続するためのクライアントライブラリ
# 参考文献: https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1
# ----------------------------------------------------
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import threading

# HandQuat で送られてくる指関節の順序（各関節はクォータニオン 4 成分）
JOINT_NAMES = [
    "thumb_cmc", "thumb_mcp", "thumb_ip",
    "index_mcp", "index_pip", "index_dip",
    "middle_mcp", "middle_pip", "middle_dip",
    "ring_mcp", "ring_pip", "ring_dip",
    "little_mcp", "little_pip", "little_dip",
]

# HandQuat の引数構成: version, id, is_left + 15 関節 * 4 成分
_HAND_QUAT_HEADER = 3
_HAND_QUAT_LENGTH = _HAND_QUAT_HEADER + len(JOINT_NAMES) * 4


class ContactGlobe2Client:
    """ContactGlove 2 / DivingStation と OSC で通信するクライアント。

    DivingStation へ接続要求を送り、別スレッドの OSC サーバーで手の姿勢データ
    （HandQuat）やデバイス情報（Device）を受信する。手データは ``hand_callback``
    に渡すか、``get_hand_data()`` で最後の値を取得できる。
    """

    def __init__(self, server_ip="127.0.0.1", client_port=25788,
                 divingstation_port=25790, hand_callback=None):
        self.server_ip = server_ip
        self.client_port = client_port
        self.divingstation_port = divingstation_port
        self.divingstation_client = SimpleUDPClient(server_ip, divingstation_port)
        self.dispatcher = Dispatcher()
        self.server = None
        self.server_thread = None
        self.device_info = None
        self.hand_data = None
        self._hand_callback = hand_callback

        # OSC アドレスとハンドラの対応付け
        self.dispatcher.map("/DS/HC/Device", self._handle_device_info)
        self.dispatcher.map("/DS/HC/HandQuat", self._handle_hand_quat)

    def set_hand_callback(self, callback):
        """手データ受信時に呼ばれるコールバックを登録する。"""
        self._hand_callback = callback

    def _handle_device_info(self, address, *args):
        self.device_info = args

    def _handle_hand_quat(self, address, *args):
        """HandQuat を解析し、辞書に整形してコールバックへ渡す。"""
        if len(args) < _HAND_QUAT_LENGTH:
            print(f"[警告] HandQuat の引数が不足しています "
                  f"(受信 {len(args)} / 期待 {_HAND_QUAT_LENGTH})")
            return
        try:
            data = {
                "version": int(args[0]),
                "id": str(args[1]),
                "is_left": int(args[2]) != 0,
                "joints": {},
            }
            for i, name in enumerate(JOINT_NAMES):
                base = _HAND_QUAT_HEADER + i * 4
                data["joints"][name] = tuple(float(v) for v in args[base:base + 4])
        except (ValueError, TypeError) as e:
            print(f"[警告] HandQuat の解析に失敗しました: {e}")
            return

        self.hand_data = data
        if self._hand_callback:
            self._hand_callback(data)

    def connect_divingstation(self):
        """DivingStation へ接続要求を送信する。成功で True を返す。"""
        try:
            self.divingstation_client.send_message("/DS/HC/Connect", self.client_port)
        except OSError as e:
            print(f"[エラー] DivingStation への接続要求に失敗しました: {e}")
            return False
        print("DivingStation へ接続要求を送信しました。")
        return True

    def start_osc_server(self):
        """データ受信用の OSC サーバーを別スレッドで起動する。成功で True を返す。"""
        if self.server is not None:
            print("OSC サーバーは既に実行中です。")
            return False
        try:
            self.server = BlockingOSCUDPServer(
                (self.server_ip, self.client_port), self.dispatcher)
        except OSError as e:
            print(f"[エラー] OSC サーバーを起動できませんでした "
                  f"(ポート {self.client_port}): {e}")
            self.server = None
            return False

        self.server_thread = threading.Thread(
            target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        print(f"OSC サーバーを起動しました: {self.server_ip}:{self.client_port}")
        return True

    def stop_osc_server(self):
        """OSC サーバーを停止する。"""
        if not self.server:
            return
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join()
        self.server = None
        self.server_thread = None
        print("OSC サーバーを停止しました。")

    def get_device_info(self):
        """最後に受信したデバイス情報を返す。"""
        return self.device_info

    def get_hand_data(self):
        """最後に受信した手データ（辞書）を返す。未受信なら None。"""
        return self.hand_data


if __name__ == "__main__":
    import time

    def on_hand_data(data):
        side = "左" if data["is_left"] else "右"
        print(f"[{side}手] index_mcp={data['joints']['index_mcp']}")

    client = ContactGlobe2Client(hand_callback=on_hand_data)
    client.connect_divingstation()
    if not client.start_osc_server():
        raise SystemExit(1)

    print("手データを待機中... (Ctrl+C で終了)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop_osc_server()
