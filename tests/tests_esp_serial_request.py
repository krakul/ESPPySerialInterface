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
        self.assertEqual(event.content, "E ESP32 ERROR")
        self.assertIsInstance(event, ErrorEventMessage)

    def test_parse_message_esp_warning(self):
        event = SerialRequest.parse_message(b"W ESP32 WARNING\r\n")
        self.assertEqual(event.content, "W ESP32 WARNING")
        self.assertIsInstance(event, WarningEventMessage)

    def test_parse_message_esp_info(self):
        event = SerialRequest.parse_message(b"I ESP32 INFO\r\n")
        self.assertEqual(event.content, "I ESP32 INFO")
        self.assertIsInstance(event, InfoEventMessage)

    def test_parse_message_esp_debug(self):
        event = SerialRequest.parse_message(b"D ESP32 DEBUG\r\n")
        self.assertEqual(event.content, "D ESP32 DEBUG")
        self.assertIsInstance(event, DebugEventMessage)


if __name__ == '__main__':
    unittest.main()
