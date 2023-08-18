# Microcal Serial Interface
from typing import Type
import serial
import time

class _commands:
    GET_ELECTRICAL_INPUT = 0x01

class Pressure_901P:
    _device_path = ""
    _serial_interface = None
    _id_number = 0
    _baud = 9600
    _debug = False
    def __init__(self, serial_device: str, id_number: int, baud: int, debug: bool = False):
        self._device_path = serial_device
        self._id_number = id_number
        self._baud = baud
        self._serial_interface = serial.Serial(self._device_path, bytesize=8, baudrate=baud, timeout=0.1)  # open serial port
        self._debug = debug

    def _do_command(self, command_str : str) -> str:
        self._serial_interface.flush()
        self._serial_interface.flushInput()
        self._serial_interface.flushOutput()
        command = f"@{self._id_number:03d}{command_str}?;FF"
        if self._debug:
            print(f"TX:{command}")
        self._serial_interface.write(command.encode())
        Data = bytes.decode(self._serial_interface.read(20), 'utf-8')
        if self._debug:
            print(f"RX:{Data}")
        value = Data.split("ACK")
        if(len(value) > 1):
            return value[1].split(";")[0]
        return "Err"
    def read_PR2(self):
        return self._do_command("PR2")

    
#cal = Pressure_901P("/dev/ttyUSB1", 253, 9600, debug=True)
#data = cal.read_PR2()
#print(data)