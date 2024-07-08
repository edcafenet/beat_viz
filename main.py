import socket
import pyautogui
import struct
import numpy as np
import keyboard
import random
from audiohandler import audiohandler

UDP_IP = "10.205.3.229"
UDP_PORT = 9876

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, UDP_PORT))

audio = audiohandler()
audio.start()     # open the the stream

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        data_string = list(data.decode()[1:-1].split(','))
        data_int = [int(round(float(i)*10)) for i in data_string]
        data_int[1] += 1500
        data_int[0] += 600
  
        # if audio.beat_present():
        #     pyautogui.drag(random.randint(0, 10), random.randint(0, 10), 1, button='left') 
        if audio.beat_present():
            pyautogui.moveTo(data_int[1], data_int[0])
            pyautogui.click()
            pyautogui.mouseDown()

        print(data_int[1], data_int[0])

    except KeyboardInterrupt:
        audio.stop()
        pass