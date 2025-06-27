# ----------------------------------------------------
# 作成者:加賀日向太
# 作成日:2025/04/26
# ContactGlobe2にOSCで接続するためのサンプルコード
# 参考文献:https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1
# ----------------------------------------------------
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher


def print_message(address, *args):
    print(f"Received message from {address}: {args}")

if __name__ == "__main__":
    # DivingStation接続設定

    # OSC server client setup
    ip = "127.0.0.1"  # Server IP
    DivingStation_port = 25790       # Server port
    DivingStation_client = SimpleUDPClient(ip, DivingStation_port)

    # Send a test message
    DivingStation_client.send_message("/DS/HC/Connect",25788)  # Address and arguments

    port = 25788
    client = SimpleUDPClient(ip, port)

    client.send_message("/DS/HC/Connect",25788)  # Address and arguments

    print("DivingStation接続要求を送信しました。")

    dispatcher = Dispatcher()
    dispatcher.map("/DS/HC/Device", print_message)  # Map the "/test" address to the print_message function

    # Create and start the server
    ip = "127.0.0.1"  # Localhost
    port = 25788       # Port to listen on
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    print(f"Serving on {ip}:{port}")
    server.serve_forever()
