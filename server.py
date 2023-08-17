from klein import run, route
from microcal import Microcal
import logging
import time

cal = Microcal("/dev/ttyUSB0", 1, 9600, debug=False)

import threading

def logger_thread(cal_device):
    while True:
        input_val = cal_device.get_electrical_input()
        with open("readings.txt", "a") as myfile:
            myfile.write(str(time.time_ns())+","+str(input_val) + "\n")
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
