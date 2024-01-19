"""
STM32 serial communication interface
"""
import threading
import time
from parse import parse
from asyncio import QueueEmpty
from dataclasses import dataclass
from enum import Enum
from queue import Queue, Empty
from threading import Thread, RLock
from dataclasses_json import dataclass_json
from serial import Serial
import serial.serialutil


@dataclass_json
@dataclass
class Event:
    timestamp: float = 0.0


@dataclass_json
@dataclass
class RequestMessage(Event):
    request: str = ""


@dataclass_json
@dataclass
class SuccessResponseMessage(Event):
    content: str = ""


@dataclass_json
@dataclass
class FailResponseMessage(Event):
    content: str = ""


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


@dataclass_json
@dataclass
class UnknownMessage(Event):
    content: str = ""


@dataclass_json
@dataclass
class InvalidMessage(Event):
    content: str = ""
    error: str = None


@dataclass_json
@dataclass
class InvalidSuccessResponseMessage(Event):
    message: SuccessResponseMessage = None
    error: str = None


@dataclass_json
@dataclass
class ResponseTimeout(Event):
    request: str = ""


@dataclass_json
@dataclass
class RequestHandlerTimeout(Event):
    request: str = ""


@dataclass_json
@dataclass
class SerialConnected(Event):
    port: str = ""


@dataclass_json
@dataclass
class SerialConnectionLost(Event):
    reason: str = ""


@dataclass_json
@dataclass
class SerialNotConnected(Event):
    pass


# ----------------------------------------------------------------------------------------------------------------------


# Serial communication interface
class SerialInterface(Thread):
    # Fields
    serial: Serial = None
    serial_list: list[str]
    request_queue: Queue = Queue()
    response_queue: Queue = Queue()

    # Constructor
    def __init__(self, port_list):
        super().__init__()
        super().setDaemon(True)

        # Construct fields
        self.serial_list = port_list
        self.is_not_stopped = True

    # Connect to first available serial interface
    def __connect(self):
        # Reset previous serial interface
        self.serial = None

        # Try connecting
        for port in self.serial_list:
            try:
                # Try to open port
                self.serial = Serial(port=port, baudrate=115200, timeout=0.1)
                print(f"UART connection opened on port {self.serial.port} with " +
                      f"baudrate {self.serial.baudrate} and timeout {self.serial.timeout}")

                # Create event
                conn = SerialConnected(timestamp=time.time(), port=port)
                self.__append_to_log(conn)
                return True
            except serial.SerialException as e:
                print(e)
        return False

    # Append event to log
    def __append_to_log(self, event: Event):
        # Show it in console
        print(str(event))

    # Parse message
    @staticmethod
    def __parse_message(text) -> Event:

        # Strip trailing whitespaces
        text = text.rstrip()

        # Make sure text is not empty
        if not text:
            return InvalidMessage(timestamp=time.time(), content=text, error="Empty line")

        # Get content behind prefix
        if len(text) > 1:
            content = text.lstrip()
        else:
            content = ''

        # Judge by prefix what is it
        if text[0] == 'D' and text[1] == " ":
            return DebugEventMessage(timestamp=time.time(), content=content)
        elif text[0] == 'I' and text[1] == " ":
            return InfoEventMessage(timestamp=time.time(), content=content)
        elif text[0] == 'W' and text[1] == " ":
            return WarningEventMessage(timestamp=time.time(), content=content)
        elif text[0] == 'E' and text[1] == " ":
            return ErrorEventMessage(timestamp=time.time(), content=content)
        else:
            return SuccessResponseMessage(timestamp=time.time(), content=content)

    # Read message
    # Return None if timeout
    def __read_message(self) -> Event:

        # Read line bytes - note that it can time out
        line = self.serial.readline()

        # Got line ?
        if line:
            # Cut the new line character
            if line[-1] == 0x0a:
                line = line[:-1]
                if len(line) == 0:
                    msg = InvalidMessage(timestamp=time.time(), content=line.hex('-'), error="Msg only 0x0a")
                    return msg

            if line[-1] == 0x0d:
                line = line[:-1]
                if len(line) == 0:
                    msg = InvalidMessage(timestamp=time.time(), content=line.hex('-'), error="Msg only 0x0d")
                    return msg
                if line[-1] == 0x0d:
                    line = line[:-1]
                if len(line) == 0:
                    msg = InvalidMessage(timestamp=time.time(), content=line.hex('-'), error="Msg only 0x0d")
                    return msg

            # Check that bytes are valid ASCII characters
            for b in line:
                if b < 0x20 or b > 0x7E:
                    msg = InvalidMessage(timestamp=time.time(), content=line.hex('-'), error="Illegal character(s)")
                    print(line)
                    self.__append_to_log(msg)
                    return msg

            # Try to decode line as ASCII
            try:
                text = line.decode('ascii')
            except UnicodeDecodeError as e:
                msg = InvalidMessage(timestamp=time.time(), content=line.hex('-'), error="Not ASCII")
                self.__append_to_log(msg)
                return msg

            # Parse and log the message
            msg = self.__parse_message(text)
            self.__append_to_log(msg)
            return msg

        return None

    def __wait_for_response(self, required_resp_start, resp_type, timeout):
        timeout_time = time.time() + timeout
        while True:
            msg = self.__read_message()

            # Got something ?
            if isinstance(msg, resp_type):
                print("MSG: ", msg.content)
                print("REQUIRES RESP: ", required_resp_start)
                if type(required_resp_start) == list:
                    for i in required_resp_start:
                        if i in msg.content:
                            return msg
                else:
                    if required_resp_start in msg.content:
                        return msg

            # Timeout ?
            if time.time() > timeout_time:
                break

        # We have timeout
        msg = ResponseTimeout(timestamp=time.time())
        self.__append_to_log(msg)
        return msg

    # Handle serial request
    def __handle_serial_request(self, req, required_resp_start, resp_type, timeout):
        if req is None:
            return self.__wait_for_response(required_resp_start, resp_type, timeout)

        # Try to send request up to 3 times
        for trial in range(3):

            # Send the request
            self.serial.write(bytes(req + '\n', 'ascii'))

            # Make sure message goes out
            self.serial.flush()

            timeout_time = time.time() + timeout

            # Wait for response, but collect all other messages also
            while True:
                msg = self.__read_message()

                # Got something ?
                if isinstance(msg, resp_type):
                    print("MSG: ", msg.content)
                    print("REQUIRES RESP: ", required_resp_start)
                    if type(required_resp_start) == list:
                        for i in required_resp_start:
                            if i in msg.content:
                                return msg
                    else:
                        if required_resp_start in msg.content:
                            return msg

                # Timeout ?
                if time.time() > timeout_time:
                    break

        # We have timeout
        msg = ResponseTimeout(timestamp=time.time(), request=req)
        self.__append_to_log(msg)
        return msg

    # Main loop
    def __main_loop(self):
        while self.is_not_stopped:
            try:
                # Read messages and just log them
                self.__read_message()

                # Any request in queue ?
                if not self.request_queue.empty():
                    try:
                        queue_item = self.request_queue.get(block=False, timeout=None)
                    except QueueEmpty:
                        # It shouldn't happen actually because this thread is only one reading the queue
                        continue

                    req = queue_item[0]
                    required_resp_start = queue_item[1]
                    resp_type = queue_item[2]
                    timeout = queue_item[3]
                    # Process request
                    resp = self.__handle_serial_request(req, required_resp_start, resp_type, timeout)
                    if resp:
                        self.response_queue.put(resp)
            except serial.SerialException as e:
                # Serial port error is critical, abort and try reconnecting
                conn = SerialConnectionLost(timestamp=time.time(), reason=str(e))
                self.__append_to_log(conn)
                self.serial.close()
                break

    # Thread entry function
    def run(self):
        while self.is_not_stopped:

            # If connection succeeds, go to main loop
            if self.__connect():
                self.__main_loop()

            # Idle for 10 seconds before reconnecting.
            # But handle pending requests also meanwhile, otherwise they queue up...
            for loop in range(10):
                time.sleep(1)

                # Process queued requests and respond with not-connected
                while not self.request_queue.empty():
                    try:
                        self.request_queue.get(block=False, timeout=None)
                        conn = SerialNotConnected(timestamp=time.time())
                        self.__append_to_log(conn)
                        self.response_queue.put(conn)
                    except QueueEmpty:
                        pass

    # Queue request and wait for response (up to 10 seconds)
    def queue_request_wait_response(self, req, required_resp_start, resp_type=SuccessResponseMessage, timeout=1.5):
        self.request_queue.put((req, required_resp_start, resp_type, timeout))
        try:
            # Timeout has to 3 x each request timeout + some more
            return self.response_queue.get(block=True, timeout=timeout + 10.0)
        except Empty:
            # It should not happen, but don't crash.
            err = RequestHandlerTimeout(timestamp=time.time(), request=req)
            self.__append_to_log(err)
            return err
