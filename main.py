import pyautogui
import socketserver, threading, time
from threading import Thread
from fft_analyzer import fft_analyzer
import random
import argparse

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))

        data_string = list(data.decode()[1:-1].split(','))
        data_int = [int(round(float(i),1)*10) for i in data_string]

        corrected_x = data_int[0] + 225 
        corrected_y = -data_int[1] + 79

        scaling_x = 0.521
        scaling_y = 0.521

        scaled_y = (corrected_y * scaling_y)          
        scaled_x = (corrected_x * scaling_x)

        scaled_y = scaled_y + 120
        scaled_x = scaled_x 

        pyautogui.moveTo(scaled_x, scaled_y)
        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=2, dest='device',
                        help='pyaudio (portaudio) device index')
    parser.add_argument('--ip', type=str, default="localhost", dest='ip',
                        help='UDP Server IP')
    parser.add_argument('--port', type=int, default=9876, dest='port',
                        help='UDP Server Port')
    parser.add_argument('--visualizer', action='store_true')

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_args()
    server = ThreadedUDPServer((args.ip, args.port), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    fft = fft_analyzer(args.device, args.visualizer)

    try:
        server_thread.start()
        print("Server started at {} port {}".format(args.ip, args.port))
        fft.run()

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()