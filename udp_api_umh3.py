import argparse
import time
import math
from typing import Union
from fastapi import FastAPI
import socketserver, threading, time
from threading import Thread

app = FastAPI()

x = 0
y = 0
z = 0
w = 0

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        #print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))

        data_string = list(data.decode()[1:-1].split(','))
        data_int = [int(round(float(i),1)*10) for i in data_string]
        data_float = [round(float(i),1) for i in data_string]

        corrected_x = data_int[0] + 225 
        corrected_y = -data_int[1] + 79

        scaling_factor = 0.521
        scaled_y = round(corrected_y * scaling_factor)          
        scaled_x = round(corrected_x * scaling_factor)

        global x, y, z, w
        y = scaled_y + 120
        x = scaled_x 
        z = data_int[2]      
        w = data_float[3]  
        #w = 360 - math.degrees(data_float[3]+math.pi)

        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):    
    pass

@app.get("/pose")
async def read_position():
    return [x,y,z,w]

@app.get("/position/{id}")
async def read_position(id: int):
    return [x,y,z,w][id]

# UDP Server parameters 
server = ThreadedUDPServer(('10.205.3.4', 10881), ThreadedUDPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
