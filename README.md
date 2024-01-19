# Python ESP32  Serial Interface

Python script to communicate with ESP32 devices over serial interface.

Handles reconnection and data parsing. Logs received data to whatever logging is supplied or to stdout.

Function queue_request_wait_response can be used to send a request and wait for a certain response.
Only start of response is matched.
