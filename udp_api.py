import argparse
import time
from typing import Union
from fastapi import FastAPI
import socketserver, threading, time
from threading import Thread

import scipy.interpolate as spi
import numpy as np
import live

app = FastAPI()

x = 0
y = 0
z = 0

counter = 0
spline_array_x = []
spline_array_y = []
fsmooth = None

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        #print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))

        data_string = list(data.decode()[1:-1].split(','))
        data_int = [int(round(float(i),1)*10) for i in data_string]

        corrected_x = data_int[0] + 225 
        corrected_y = -data_int[1] + 79

        scaling_factor = 0.521
        
        scaled_y = round(corrected_y * scaling_factor)          
        scaled_x = round(corrected_x * scaling_factor)

        global x, y, z
        y = scaled_y + 120
        x = scaled_x 
        z = data_int[2]        

        global spline_array_x, spline_array_y, fsmooth, counter
        spline_array_x.append(counter)
        spline_array_y.append(y) 

        counter = counter + 1

        if(counter > 62):
            fsmooth = spi.InterpolatedUnivariateSpline(spline_array_x, spline_array_y)
            spline_array_x = []
            spline_array_y = []
            counter = 0

        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):    
    pass

@app.get("/position")
def read_position():
    return [x, y, z]

# UDP Server parameters 
server = ThreadedUDPServer(('10.205.3.4', 10876), ThreadedUDPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

#Pylive code for interfacing with the track
set = live.Set(scan=True)
track = set.tracks[0]
device = track.devices[0]

# Turn on the EQ
device.parameters[0].value = 1

# This loop assumes you have a Live session with one track and the AUGraphicEQ
while (True):
    for i in range(1,32):
        if fsmooth == None:
            device.parameters[i].value = 0.5
        else:
            device.parameters[i].value = fsmooth(i*2)/500
    
    time.sleep(1)
