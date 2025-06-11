# Python ESP32 Serial Interface

Based on the original SerialInterface for all devices [PySerialInterface](https://github.com/krakul/PySerialInterface)

Python script to specficly communicate with ESP32 devices over serial interface, handles ESP32 Error, Info, Warning and Debug level messages.

Handles reconnection and data parsing. Logs received data to whatever logging is supplied or to stdout.

Function queue_request_wait_response can be used to send a request and wait for a certain response.
Only start of response is matched.


## Example usage

```python
from ESPPySerialInterface.ESPPySerialInterface import ESPPySerialInterface, CLIResponseMessage

# Create a SerialInterface instance
interface = ESPPySerialInterface("/dev/ttyUSB0", baudrate=115200)
interface.start()

# Send a request and wait for a response
response = interface.queue_request_wait_response(req="AT", required_resp_start="OK")
if isinstance(response, CLIResponseMessage):
    print(f"Received response: {response.content}")
else:
    # Handle unexpected response
    print(f"Unexpected response received: {response}")

interface.stop()
```


## License

This project is licensed under the [MIT License](./LICENSE) – © 2025 Krakul
