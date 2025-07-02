# ContactGlobe2 Python Library

A Python library for interfacing with ContactGlobe2 using OSC (Open Sound Control) protocol. This library provides tools to receive and process hand tracking data from ContactGlobe2 devices.

## Features

- Receive hand tracking data via OSC protocol
- Support for quaternion-based hand pose data
- Example scripts for both client and server implementations
- Easy integration with Python applications

## Prerequisites

- Python 3.6 or higher
- python-osc library
- ContactGlobe2 device and DivingStation software

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/OSC-contactglobe2.git
   cd OSC-contactglobe2
   ```

2. Install the required dependencies:
   ```bash
   pip install python-osc
   ```

## Project Structure

- `hand.py` - Example script demonstrating how to receive hand tracking data
- `contact_client.py` - Basic client implementation
- `contact_server.py` - Basic server implementation
- `osc_client.py` - OSC client implementation
- `osc_server.py` - OSC server implementation
- `library/` - Contains library modules
  - `contact_server.py` - Server library implementation
  - `contactglobe2_client.py` - Client library implementation

## Usage

### Basic Example

See `hand.py` for a complete example of receiving and processing hand tracking data:

```python
# Example of processing hand data
def print_message(address, *args):
    version = int(args[0])
    device_id = str(args[1])
    is_left = bool(args[2])
    # Process quaternion data for each finger joint...
    
# Set up OSC server
server = BlockingOSCUDPServer((ip, port), dispatcher)
print(f"Listening on {ip}:{port}")
server.serve_forever()
```

## Configuration

Update the following parameters in the scripts as needed:
- IP address and port for OSC communication
- Data processing callbacks
- Logging preferences

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- [ContactGlove 2 Developer Documentation](https://docs.diver-x.jp/contact-glove-2-dev/cg2_protocolv1)
- [python-osc Documentation](https://python-osc.readthedocs.io/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
