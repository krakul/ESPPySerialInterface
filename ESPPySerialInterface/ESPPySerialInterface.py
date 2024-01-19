"""
ESP32 serial communication interface
"""

from PySerialInterface.SerialInterface import SerialInterface
from PySerialInterface.SerialRequest import SerialRequest, Event, EmptyMessage, CLIResponseMessage, InvalidMessage
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class DebugEventMessage(Event):
    content: str = ""


@dataclass_json
@dataclass
class InfoEventMessage(Event):
    content: str = ""


@dataclass_json
@dataclass
class WarningEventMessage(Event):
    content: str = ""


@dataclass_json
@dataclass
class ErrorEventMessage(Event):
    content: str = ""


# Define your custom parser
def my_custom_parse_message(line) -> Event:
    if line is None or len(line) == 0:
        return EmptyMessage(error="Empty line")
    line = SerialRequest.cut_line_end_characters(line)
    if isinstance(line, InvalidMessage):
        return line

    if SerialRequest.check_valid_ascii(line) is False:
        msg = InvalidMessage(content=line, error="Illegal character(s)")
        return msg

    # Try to decode line as ASCII
    try:
        line = line.decode('ascii')
    except UnicodeDecodeError as e:
        msg = InvalidMessage(content=line.hex('-'), error=f"Not ASCII: {e}")
        return msg

    # Strip trailing whitespaces
    line = line.rstrip()

    # Make sure text is not empty
    if not line:
        return EmptyMessage(error="Empty line")

    # Get content behind prefix
    if len(line) > 1:
        content = line.lstrip()
    else:
        content = ''

    # Judge by prefix what is it
    if line.startswith("D "):
        return DebugEventMessage(content=content)
    elif line.startswith("I "):
        return InfoEventMessage(content=content)
    elif line.startswith("W "):
        return WarningEventMessage(content=content)
    elif line.startswith("E "):
        return ErrorEventMessage(content=content)
    else:
        # there is no logging prefix, so it is a CLI response
        return CLIResponseMessage(content=content)


SerialRequest.parse_message = staticmethod(my_custom_parse_message)


class ESPPySerialInterface(SerialInterface):
    pass
