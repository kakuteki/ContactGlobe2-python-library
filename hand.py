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
    # HandQuaternionDataの各要素を変数へ格納
    version = int(args[0])
    id = str(args[1])
    is_left = bool(args[2])
    thumb_cmc_quat = list(map(float, args[3:7]))
    thumb_mcp_quat = list(map(float, args[7:11]))
    thumb_ip_quat = list(map(float, args[11:15]))
    index_mcp_quat = list(map(float, args[15:19]))
    index_pip_quat = list(map(float, args[19:23]))
    index_dip_quat = list(map(float, args[23:27]))
    middle_mcp_quat = list(map(float, args[27:31]))
    middle_pip_quat = list(map(float, args[31:35]))
    middle_dip_quat = list(map(float, args[35:39]))
    ring_mcp_quat = list(map(float, args[39:43]))
    ring_pip_quat = list(map(float, args[43:47]))
    ring_dip_quat = list(map(float, args[47:51]))
    little_mcp_quat = list(map(float, args[51:55]))
    little_pip_quat = list(map(float, args[55:59]))
    little_dip_quat = list(map(float, args[59:63]))

    # デバッグ用出力（必要に応じて後続処理に渡す）
    print(f"version: {version}, id: {id}, is_left: {is_left}")
    print(f"thumb_cmc_quat: {thumb_cmc_quat}")
    print(f"thumb_mcp_quat: {thumb_mcp_quat}")
    print(f"thumb_ip_quat: {thumb_ip_quat}")
    print(f"index_mcp_quat: {index_mcp_quat}")
    print(f"index_pip_quat: {index_pip_quat}")
    print(f"index_dip_quat: {index_dip_quat}")
    print(f"middle_mcp_quat: {middle_mcp_quat}")
    print(f"middle_pip_quat: {middle_pip_quat}")
    print(f"middle_dip_quat: {middle_dip_quat}")
    print(f"ring_mcp_quat: {ring_mcp_quat}")
    print(f"ring_pip_quat: {ring_pip_quat}")
    print(f"ring_dip_quat: {ring_dip_quat}")
    print(f"little_mcp_quat: {little_mcp_quat}")
    print(f"little_pip_quat: {little_pip_quat}")
    print(f"little_dip_quat: {little_dip_quat}")

    import csv
    import os
    import time
    
    csv_filename = "hand_data_log.csv"
    fieldnames = [
        "timestamp", "version", "id", "is_left",
        "thumb_cmc_quat_0", "thumb_cmc_quat_1", "thumb_cmc_quat_2", "thumb_cmc_quat_3",
        "thumb_mcp_quat_0", "thumb_mcp_quat_1", "thumb_mcp_quat_2", "thumb_mcp_quat_3",
        "thumb_ip_quat_0", "thumb_ip_quat_1", "thumb_ip_quat_2", "thumb_ip_quat_3",
        "index_mcp_quat_0", "index_mcp_quat_1", "index_mcp_quat_2", "index_mcp_quat_3",
        "index_pip_quat_0", "index_pip_quat_1", "index_pip_quat_2", "index_pip_quat_3",
        "index_dip_quat_0", "index_dip_quat_1", "index_dip_quat_2", "index_dip_quat_3",
        "middle_mcp_quat_0", "middle_mcp_quat_1", "middle_mcp_quat_2", "middle_mcp_quat_3",
        "middle_pip_quat_0", "middle_pip_quat_1", "middle_pip_quat_2", "middle_pip_quat_3",
        "middle_dip_quat_0", "middle_dip_quat_1", "middle_dip_quat_2", "middle_dip_quat_3",
        "ring_mcp_quat_0", "ring_mcp_quat_1", "ring_mcp_quat_2", "ring_mcp_quat_3",
        "ring_pip_quat_0", "ring_pip_quat_1", "ring_pip_quat_2", "ring_pip_quat_3",
        "ring_dip_quat_0", "ring_dip_quat_1", "ring_dip_quat_2", "ring_dip_quat_3",
        "little_mcp_quat_0", "little_mcp_quat_1", "little_mcp_quat_2", "little_mcp_quat_3",
        "little_pip_quat_0", "little_pip_quat_1", "little_pip_quat_2", "little_pip_quat_3",
        "little_dip_quat_0", "little_dip_quat_1", "little_dip_quat_2", "little_dip_quat_3"
    ]
    row = {
        "timestamp": time.time(),  # Unix timestamp with microsecond precision
        "version": version,
        "id": id,
        "is_left": is_left,
    }
    # 各クォータニオンを展開してrowに追加
    quat_lists = [
        thumb_cmc_quat, thumb_mcp_quat, thumb_ip_quat,
        index_mcp_quat, index_pip_quat, index_dip_quat,
        middle_mcp_quat, middle_pip_quat, middle_dip_quat,
        ring_mcp_quat, ring_pip_quat, ring_dip_quat,
        little_mcp_quat, little_pip_quat, little_dip_quat
    ]
    for label, quat in zip(fieldnames[4:], sum(quat_lists, [])):
        row[label] = quat
    # ファイルがなければヘッダー出力
    write_header = not os.path.isfile(csv_filename)
    with open(csv_filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    # --- 追加ここまで ---


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
    dispatcher.map("/DS/HC/HandQuat", print_message)  # Map the "/test" address to the print_message function
    

    # Create and start the server
    ip = "127.0.0.1"  # Localhost
    port = 25788       # Port to listen on
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    print(f"Serving on {ip}:{port}")
    server.serve_forever()

