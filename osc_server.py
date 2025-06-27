# OSCサーバー (受信側)
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def print_message(address, *args):
    print(f"Received message from {address}: {args}")

if __name__ == "__main__":
    # Dispatcher to handle incoming messages
    dispatcher = Dispatcher()
    dispatcher.map("/test", print_message)  # Map the "/test" address to the print_message function

    # Create and start the server
    ip = "127.0.0.1"  # Localhost
    port = 5005       # Port to listen on
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    print(f"Serving on {ip}:{port}")
    server.serve_forever()
