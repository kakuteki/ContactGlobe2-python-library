from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import threading
import time

class ContactGlobe2Client:
    def __init__(self, server_ip="127.0.0.1", client_port=25788, divingstation_port=25790):
        self.server_ip = server_ip
        self.client_port = client_port
        self.divingstation_port = divingstation_port
        self.divingstation_client = SimpleUDPClient(server_ip, divingstation_port)
        self.osc_client = SimpleUDPClient(server_ip, client_port)
        self.dispatcher = Dispatcher()
        self.server = None
        self.server_thread = None
        self.device_info = None
        self.hand_data = {} # Placeholder for hand data

        # Map OSC addresses to handler functions
        self.dispatcher.map("/DS/HC/Device", self._handle_device_info)
        # Add more mappings as needed, e.g., for hand data
        # self.dispatcher.map("/DS/HC/Hand", self._handle_hand_data)

    def _handle_device_info(self, address, *args):
        print(f"Received device info from {address}: {args}")
        self.device_info = args

    # def _handle_hand_data(self, address, *args):
    #     print(f"Received hand data from {address}: {args}")
    #     # Process and store hand data

    def connect_divingstation(self):
        """DivingStationへの接続要求を送信します。"""
        self.divingstation_client.send_message("/DS/HC/Connect", self.client_port)
        print("🔌 DivingStation接続要求を送信しました。")

    def start_osc_server(self):
        """ContactGlobe2からのデータを受信するためのOSCサーバーを開始します。"""
        if self.server is None:
            self.server = BlockingOSCUDPServer((self.server_ip, self.client_port), self.dispatcher)
            print(f"Serving OSC on {self.server_ip}:{self.client_port}")
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True # Allow the main program to exit even if the thread is running
            self.server_thread.start()
        else:
            print("OSCサーバーは既に実行中です。")

    def stop_osc_server(self):
        """OSCサーバーを停止します。"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
            self.server = None
            self.server_thread = None
            print("OSCサーバーを停止しました。")
        else:
            print("OSCサーバーは実行されていません。")

    def get_device_info(self):
        """最後に受信したデバイス情報を返します。"""
        # You might want to send a message to request device info if it's not automatically sent
        # For now, it just returns the last received info
        return self.device_info

    # Placeholder for other data acquisition methods
    # def get_hand_data(self):
    #     return self.hand_data

if __name__ == "__main__":
    client = ContactGlobe2Client()
    client.connect_divingstation()
    client.start_osc_server()

    # Example usage: wait for some time to receive data
    print("Waiting for device info... (Press Ctrl+C to exit)")
    try:
        while True:
            device_info = client.get_device_info()
            if device_info:
                print(f"Current Device Info: {device_info}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        client.stop_osc_server()
