# OSCクライアント (送信側)
from pythonosc.udp_client import SimpleUDPClient

if __name__ == "__main__":
    # OSC client setup
    ip = "127.0.0.1"  # Server IP
    port = 5005       # Server port
    client = SimpleUDPClient(ip, port)

    # Send a test message
    client.send_message("/test", [42, "Hello, OSC!"])  # Address and arguments
    print("Message sent!")