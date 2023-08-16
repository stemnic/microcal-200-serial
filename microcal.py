# Microcal Serial Interface
from typing import Type
import serial
import time

class _commands:
    GET_ELECTRICAL_INPUT = 0x01
    GET_BATTERY_VOLTAGE = 0x0E
    GET_DATE = 0x15

    SET_ACTUAL_OUTPUT = 0x80
    SET_OUTPUT_VALUE = 0x81

class Microcal:
    _device_path = ""
    _serial_interface = None
    _id_number = 0
    _baud = 9600
    _debug = False
    def __init__(self, serial_device: str, id_number: int, baud: int, debug: bool = False):
        self._device_path = serial_device
        self._id_number = id_number
        self._baud = baud
        self._serial_interface = serial.Serial(self._device_path, bytesize=8, baudrate=baud, timeout=0.25)  # open serial port
        self._debug = debug

    def _do_command(self, command: int, parameters: list) -> list:
        self._serial_interface.flush()
        self._serial_interface.flushInput()
        self._serial_interface.flushOutput()
        if self._debug:
            print(f"TX:{self._id_number}")
        self._serial_interface.write(self._id_number.to_bytes(1, byteorder='big'))
        Rx_IDNAME = self._serial_interface.read(1)
        if self._debug:
            print(f"RX:{Rx_IDNAME}")
        if self._debug:
            print(f"TX:{command}")
        self._serial_interface.write(command.to_bytes(1, byteorder='big'))
        Rx_Instruction = self._serial_interface.read(1)
        if self._debug:
            print(f"RX:{Rx_Instruction}")
        if self._debug:
            print(f"TX:{parameters[0]}")
        self._serial_interface.write(parameters[0].to_bytes(1, byteorder='big'))
        Data1 = int.from_bytes(self._serial_interface.read(1), 'big')
        if self._debug:
            print(f"RX:{Data1}")
        if self._debug:
            print(f"TX:{parameters[1]}")
        self._serial_interface.write(parameters[1].to_bytes(1, byteorder='big'))
        Data2 = int.from_bytes(self._serial_interface.read(1), 'big')
        if self._debug:
            print(f"RX:{Data2}")
        if self._debug:
            print(f"TX:{parameters[2]}")
        self._serial_interface.write(parameters[2].to_bytes(1, byteorder='big'))
        Data3 = int.from_bytes(self._serial_interface.read(1), 'big')
        if self._debug:
            print(f"RX:{Data3}")
        if self._debug:
            print(f"TX:{parameters[3]}")
        self._serial_interface.write(parameters[3].to_bytes(1, byteorder='big'))
        Data4 = int.from_bytes(self._serial_interface.read(1), 'big')
        if self._debug:
            print(f"RX:{Data4}")
        Tx_Checksum = (parameters[0] + parameters[1] + parameters[2] + parameters[3]) & (0x7F)
        if self._debug:
            print(f"TX_Checksum:{Tx_Checksum}")
            print(f"TX:{Tx_Checksum}")
        self._serial_interface.write(Tx_Checksum.to_bytes(1, byteorder='big'))
        Rx_Checksum = int.from_bytes(self._serial_interface.read(1), 'big')
        if self._debug:
            print(f"RX:{Rx_Checksum}")
        Rx_Checksum_expected = (Data1 + Data2 + Data3 + Data4) & (0xFF)
        if((Rx_Checksum != Tx_Checksum) and self._debug):
            print("Checksum error!")
            print(f"Rx_Checksum: {Rx_Checksum}")
            print(f"Tx_Checksum: {Tx_Checksum}")
        return [Data1, Data2, Data3, Data4]

    
    def get_battery_voltage(self) -> int:
        data = self._do_command(_commands.GET_BATTERY_VOLTAGE, [0x0,0x0,0x0,0x0])
        VBATT_H = data[2]
        VBATT_L = data[3]
        VBATT = (VBATT_H << 8 ) | VBATT_L
        return VBATT
    
    def get_date(self) -> str:
        data = self._do_command(_commands.GET_DATE, [0x0,0x0,0x0,0x0])
        DAY = data[0]
        MONTH = data[1]
        YEAR = data[2]
        return f"{YEAR}-{MONTH}-{DAY}"

    def get_electrical_input(self) -> int:
        data = self._do_command(_commands.GET_ELECTRICAL_INPUT, [0x0,0x0,0x0,0x0])
        INPUT_HH = data[0]
        INPUT_H  = data[1]
        INPUT_L  = data[2]
        INPUT_LL = data[3]
        INPUT = (INPUT_HH << 24 ) | (INPUT_H << 16 ) | (INPUT_L << 8 ) | INPUT_LL
        return INPUT
    
    def set_output(self, inp : int):
        INPUTHH = (inp >> 24 ) & 0xFF
        INPUTH  = (inp >> 16 ) & 0xFF
        INPUTL  = (inp >> 8 )  & 0xFF
        INPUTLL = inp & 0xFF
        self._do_command(_commands.SET_OUTPUT_VALUE, [INPUTHH,INPUTH,INPUTL,INPUTLL])

    def set_output_type(self, inp : int):
        IO_TYPE = (inp >> 24 ) & 0xFF
        IO_SUBTYPE  = (inp >> 16 ) & 0xFF
        IO_FLAG_IO_H  = (inp >> 8 )  & 0xFF
        IO_FLAG_IO_L = inp & 0xFF
        self._do_command(_commands.SET_ACTUAL_OUTPUT, [IO_TYPE,IO_SUBTYPE,IO_FLAG_IO_H,IO_FLAG_IO_L])
    



cal = Microcal("/dev/tty.usbserial-140", 1, 9600, debug=False)
print(cal.get_battery_voltage())
print(cal.get_date())
i = 0
#cal.set_output(150000)
while True:
    cal.set_output(i)
    i = i + 100
    print(cal.get_electrical_input())

