#! /usr/bin/env python

import serial
import time
import sys
import re
import requests
import datetime



def connect_serial():
    return serial.Serial(
        port='/dev/ttyUSB0', \
        baudrate=9600, \
        parity=serial.PARITY_NONE, \
        stopbits=serial.STOPBITS_ONE, \
        bytesize=serial.EIGHTBITS, \
        timeout=0)

def parse_reading(line):
    if line.startswith("$"):
        return None
    return re.match("C(\\d+)ppm", line).group(1)

count=1
line = ""
while True:
    # Reconnect for every set of readings in order to get updated information.
    # There's probably something important I'm not doing to make this work correctly with
    # a persistent connection.
    ser = connect_serial()
    print("connected to: " + ser.portstr)
    got_reading = False
    while not got_reading:
        c = ser.read()
        if re.match("\\n", c):
            print(line)
            reading = parse_reading(line)
            if reading is not None:
                got_reading = True
                print("Posting " + reading + " at " + str(datetime.datetime.now()))
                try:
                    res = requests.post("http://192.168.1.105:1337/log", json={"type": "office-co2", "value": reading})
                    print(res.status_code)
                except Exception as e:
                    print(e)
            line = ""
            sys.stdout.flush()
            if reading:
                time.sleep(60)
        else:
            line += c

    ser.close()


