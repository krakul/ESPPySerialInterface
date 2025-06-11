# SPDX-License-Identifier: MIT

import unittest
from ESPPySerialInterface.ESPPySerialInterface import SerialRequest, CLIResponseMessage, DebugEventMessage, \
    InfoEventMessage, WarningEventMessage, ErrorEventMessage


class TestESPSerialRequest(unittest.TestCase):

    def test_parse_message_cli_response(self):
        event = SerialRequest.parse_message(b"OK\r\n")
        self.assertIsInstance(event, CLIResponseMessage)
        self.assertEqual(event.content, "OK")

    def test_parse_message_esp_error(self):
        event = SerialRequest.parse_message(b"E ESP32 ERROR\r\n")
        self.assertIsInstance(event, ErrorEventMessage)
        self.assertEqual(event.content, "E ESP32 ERROR")

    def test_parse_message_esp_warning(self):
        event = SerialRequest.parse_message(b"W ESP32 WARNING\r\n")
        self.assertIsInstance(event, WarningEventMessage)
        self.assertEqual(event.content, "W ESP32 WARNING")

    def test_parse_message_esp_info(self):
        event = SerialRequest.parse_message(b"I ESP32 INFO\r\n")
        self.assertIsInstance(event, InfoEventMessage)
        self.assertEqual(event.content, "I ESP32 INFO")

    def test_parse_message_esp_debug(self):
        event = SerialRequest.parse_message(b"D ESP32 DEBUG\r\n")
        self.assertIsInstance(event, DebugEventMessage)
        self.assertEqual(event.content, "D ESP32 DEBUG")


if __name__ == '__main__':
    unittest.main()
