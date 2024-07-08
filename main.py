import pyautogui
import socketserver, threading, time
from threading import Thread
from fft_analyzer import fft_analyzer
import random

fft = fft_analyzer()

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))

        data_string = list(data.decode()[1:-1].split(','))
        data_int = [int(round(float(i),1)*10) for i in data_string]

        corrected_x = data_int[0] + 338
        corrected_y = -data_int[1] + 124

        scaling_x = 0.70
        scaling_y = 0.41

        scaled_x = corrected_x * scaling_x
        scaled_y = corrected_y * scaling_y        

        #pyautogui.dragTo(scaled_x, scaled_y, button='left')
        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

def run_fft():
    fft.run()

if __name__ == "__main__":
    UDP_IP = "172.16.13.200"
    UDP_PORT = 9876

    server = ThreadedUDPServer((UDP_IP, UDP_PORT), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    fft_thread = threading.Thread(target=run_fft)

    try:
        server_thread.start()
        print("Server started at {} port {}".format(UDP_IP, UDP_PORT))
        fft_thread.start()
        print("FFT started")

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()