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

        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):    
    pass

@app.get("/position")
def read_position():
    return [x, y, z]

# This function assumes you have a Live session with one track and the AUGraphicEQ
@app.get("/eq")
def change_eq():
    set = live.Set(scan=True)
    track = set.tracks[0]
    device = track.devices[0]

    # Turn on the EQ
    device.parameters[0].value = 1

    for i in range(1,32):
        device.parameters[i].value = fsmooth(i*4)/500


# UDP Server parameters 
server = ThreadedUDPServer(('192.168.1.131', 9876), ThreadedUDPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

spline_array_x = list(range(124))
spline_array_y = [174,175,176,177,178,179,180,182,183,185,188,191,195,199,204,206,211,216,222,228,234,239,245,248,254,260,265,270,278,287,295,300,303,305,305,303,300,295,290,283,276,267,261,252,243,235,227,218,210,208,199,195,192,186,183,180,180,182,184,187,189,192,195,197,200,204,208,212,216,221,225,228,233,237,242,247,251,254,259,263,267,271,275,277,280,284,286,288,290,291,292,292,292,292,291,290,289,287,285,283,280,277,274,271,266,262,258,255,247,245,239,233,227,221,212,199,187,178,166,156,148,143,139,136]
fsmooth = spi.InterpolatedUnivariateSpline(spline_array_x, spline_array_y)
