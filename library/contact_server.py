# ----------------------------------------------------
# 作成者:加賀日向太
# 作成日:2025/04/26
# ContactGlobe2にOSCで接続するためのサンプルコード
# 参考文献:https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1
# ----------------------------------------------------
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

ip = "127.0.0.1"

def print_message(address, *args):
    print(f"{address}: {args}")

def DivingStation_connect():
    port = 25790
    client = SimpleUDPClient(ip, port)
    client.send_message("/DS/HC/Connect", 25788)
    print("🔌DivingStation接続要求を送信しました。")

# def DivingStation_disconnect():

def Get_device_info():
    print("📡デバイス情報を取得します。")

    dispatcher = Dispatcher()
    dispatcher.map("/DS/HC/Device", print_message)

    port = 25788       # Port to listen on
    server = BlockingOSCUDPServer((ip, port), dispatcher)

    print("⚙️デバイス情報を取得しました。")

    print(f"IP:{ip}  ポート:{port}に送信しました。")
    server.handle_request()

# def Get_Hand_data():
# def Get_HandQuat_data():
# def Get_Wrist_data():
# def Get_Controller_data():

# def Send_Haptics_data():

if __name__ == "__main__":
    DivingStation_connect()
    Get_device_info()


