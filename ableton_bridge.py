import live
import time
import requests
import scipy.interpolate as spi
import numpy as np

spline_array_x = []
spline_array_y = []
spline_array_z = []

spline_complete = False

umh0_x = 0
umh0_y = 0
umh0_z = 0

umh1_x = 0
umh1_y = 0
umh1_z = 0

def get_positions():
    global umh0_x, umh0_y, umh0_z, umh1_x, umh1_y, umh1_z
    response = requests.get("http://127.0.0.1:8001/position/0")
    umh0_x = int(response.content.decode('UTF-8'))

    response = requests.get("http://127.0.0.1:8001/position/1")
    umh0_y = int(response.content.decode('UTF-8'))

    response = requests.get("http://127.0.0.1:8001/position/2")
    umh0_z = int(response.content.decode('UTF-8'))

    response = requests.get("http://127.0.0.1:8002/position/0")
    umh1_x = int(response.content.decode('UTF-8'))

    response = requests.get("http://127.0.0.1:8002/position/1")
    umh1_y = int(response.content.decode('UTF-8'))

    response = requests.get("http://127.0.0.1:8002/position/2")
    umh1_z = int(response.content.decode('UTF-8'))

def trigger_eq():
    if umh1_z > 750 and umh1_z < 850:
        if umh1_x > 450 and umh1_x < 600:
            if umh1_y > 160 and umh1_y < 300:
                return True
    return False

def trigger_disconnect_eq():
    if umh0_x > umh1_x:
        if umh0_z > 1000 and umh1_z > 1000:
            return True
    return False

def reset_spline():
    global spline_array_x, spline_array_y
    spline_array_x = []
    spline_array_y = []

def reset_eq():
    for i in range(1,32):
        device.parameters[i].value = 0.5

#Pylive code for interfacing with the track
set = live.Set(scan=True)
track = set.tracks[0]
device = track.devices[0]

# Turn on the EQ
device.parameters[0].value = 1
    
# This loop assumes you have a Live session with one track and the AUGraphicEQ
while (True):
    try:
        get_positions()
    
    except KeyboardInterrupt:
        break    
    
    except:
        pass

    if trigger_eq():
        if not spline_complete:
            spline_array_x.append(len(spline_array_x))
            spline_array_y.append(umh0_y)
            time.sleep(0.005) 
        
    else:
        if spline_array_x and len(spline_array_x) < 93:
            spline_array_x.append(len(spline_array_x))
            spline_array_y.append(250)
        
    if len(spline_array_x) == 93:
        spline_complete = True
        fsmooth = spi.InterpolatedUnivariateSpline(spline_array_x, spline_array_y)
        fsmooth.set_smoothing_factor(0.5)
        
        for i in range(1,32):
            device.parameters[i].value = fsmooth(i*3)/500
    
    if trigger_disconnect_eq():
        reset_eq()
        reset_spline()
        spline_complete = False

    if spline_complete:
        time.sleep(5)
        reset_spline()
        spline_complete = False
    