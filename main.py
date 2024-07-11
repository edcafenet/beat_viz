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

        scaling_x = 0.52
        scaling_y = 0.52

        scaled_y = (corrected_y * scaling_y)          
        scaled_x = (corrected_x * scaling_x)

        scaled_y = scaled_y + 120
        scaled_x = scaled_x 

        pyautogui.moveTo(scaled_x, scaled_y)
        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class beat_viz:
    random_increment_x = 0
    random_increment_y = 0
    current_mouse_position = [0,0]
    fft = None

    def __init__(self, fft):
        self.fft = fft

    def sync_glow(self, bin_id, threshold):
        if self.fft.beat_present(bin_id, threshold):
            self.current_mouse_position[0] = pyautogui.position()[0]
            self.current_mouse_position[1] = pyautogui.position()[1]

            self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment_x
            self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment_y
            
            jump = round(self.fft.get_binned_fft(bin_id)/4)
            self.random_increment_x = random.randrange(-jump,jump)
            self.random_increment_y = random.randrange(-jump,jump)

            pyautogui.mouseDown()
            pyautogui.moveTo(self.current_mouse_position[0] + self.random_increment_x, self.current_mouse_position[1] + self.random_increment_y)
            pyautogui.mouseUp()
    
    def run(self):
        # Give time to the FFT to load the first samples
        time.sleep(1)

        # Loop for the viz function
        while True:
            self.sync_glow(0,20)
            time.sleep(0.001)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=2, dest='device',
                        help='pyaudio (portaudio) device index')
    parser.add_argument('--ip', type=str, default="localhost", dest='ip',
                        help='UDP Server IP')
    parser.add_argument('--port', type=int, default=9876, dest='port',
                        help='UDP Serverr Port')
    parser.add_argument('--visualizer', action='store_true')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # UDP SERVER
    server = ThreadedUDPServer((args.ip, args.port), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    
    # FFT 
    fft = fft_analyzer(args.device, args.visualizer)
    fft_thread = threading.Thread(target=fft.run)
    fft_thread.daemon = True

    # VIZ OBJECT
    beat = beat_viz(fft)

    try:
        server_thread.start()
        print("Server started at {} port {}".format(args.ip, args.port))
        fft_thread.start()
        print("FFT started")
        
        # Run the main loop
        beat.run()

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()