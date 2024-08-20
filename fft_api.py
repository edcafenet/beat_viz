import argparse
import time
from typing import Union
from fastapi import FastAPI
from fft_analyzer import fft_analyzer

app = FastAPI()
# Parsing the arguments from command line
# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--device', type=int, default=2, dest='device',
#                         help='pyaudio (portaudio) device index')
#     parser.add_argument('--nbins', type=int, default=9, dest='nbins',
#                         help='pyaudio (portaudio) device index')

#     return parser.parse_args()

# args = parse_args()
fft = fft_analyzer(2, 9)

@app.get("/color")
async def read_color():
    return db_to_color(fft)

def db_to_color(fft):
    fft.run()

    low = fft.binned_fft[0] + fft.binned_fft[1] + fft.binned_fft[2]
    mid = fft.binned_fft[3] + fft.binned_fft[4] + fft.binned_fft[5]
    high = fft.binned_fft[6] + fft.binned_fft[7] + fft.binned_fft[8] 
    
    red = int(low*2)
    green = int(mid*6)
    blue = int(high*8)

    if red > 255:
        red = 255
    if green > 255:
        green = 255
    if blue > 255:
        blue = 255

    return [red, green, blue]
