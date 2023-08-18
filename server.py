from klein import run, route
from microcal import Microcal
from MKS_901P_Pressure_Transducer_Driver.Pressure_901P import Pressure_901P
import logging
import time
import board
import adafruit_dht
import psutil

cal = Microcal("/dev/ttyUSB0", 1, 9600, debug=False)
pres = Pressure_901P("/dev/ttyUSB1", 253, 9600, debug=False)

for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
sensor = adafruit_dht.DHT11(board.D4)

import threading

def logger_thread(cal_device):
    while True:
        input_val = cal_device.get_electrical_input()
        humidity = 0
        try:
            humidity = sensor.humidity
        except RuntimeError as error:
            continue
        with open("readings.txt", "a") as myfile:
            myfile.write(str(time.time_ns())+","+str(input_val)+","+str(humidity)+","+str(pres.read_PR2()) + "\n")
        #logging.info("%i", input_val)

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,datefmt="%H:%M:%S")

x = threading.Thread(target=logger_thread, args=(cal,))
x.start()

import os

@route('/')
def home(request):
    with open('readings.txt', 'rb') as f:
        try:  # catch OSError in case of a one line file 
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
        return str(last_line)

@route('/history')
def history(request):
    with open('readings.txt', 'rb') as f:
        ret_str = ""
        for x in f.readlines():
            ret_str = ret_str + str(x.decode()) + "\n"
        return ret_str

run("0.0.0.0", 8080)
