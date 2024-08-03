import pyautogui
import socketserver, threading, time
from threading import Thread
from fft_analyzer import fft_analyzer
import random
import argparse
from astar import astar
import numpy as np

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
        
        scaled_y = (corrected_y * scaling_factor)          
        scaled_x = (corrected_x * scaling_factor)

        global x, y, z
        y = scaled_y + 120
        x = scaled_x 
        z = data_int[2]
 
        socket.sendto(data.upper(), self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):    
    pass

class beat_viz():
    def __init__(self, device_id):
        self.fft = fft_analyzer(device_id)
        
        for i in range(10):
            self.fft.run()
            time.sleep(0.1)
        
        self.time_start = time.time()
        self.current_mouse_position = [0,650]
        self.new_mouse_position = [0,0]
        self.random_increment = [0,0]
    
        self.current_beat = 0
        self.previous_beat = 0

        self.threshold = 20

        self.path_counter = 0

        # Direction of the movement
        self.direction_forward = None

    def autonomous_line(self):        
        # Run the FFT and retrieve a value for the first bin
        self.fft.run()
        self.current_beat = self.fft.binned_fft[0]

        if self.fft.beat_present(0, self.threshold):
            if self.current_mouse_position[0] <= 25:
                self.direction_forward = True
            elif self.current_mouse_position[0] > (pyautogui.size()[0] - 25):
                self.direction_forward = False

            jump = round(self.current_beat/2)

            if self.direction_forward:
                self.current_mouse_position[0] += jump
            if not self.direction_forward:
                self.current_mouse_position[0] -= jump 

            # Remove the previous random movement
            self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment[0]
            self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment[1]
            
            # Calculate the next random movement
            self.random_increment = [random.randrange(-jump,jump), random.randrange(-jump,jump)]

            # Caculate new position
            self.new_mouse_position = [self.current_mouse_position[0] + self.random_increment[0], self.current_mouse_position[1] + self.random_increment[1]]

            # Move the mouse
            pyautogui.mouseDown()
            pyautogui.moveTo(self.new_mouse_position[0], self.new_mouse_position[1])
            pyautogui.mouseUp()

            # Update position
            self.current_mouse_position = self.new_mouse_position

        # If there is a drop press 'space'
        if round(self.current_beat - self.previous_beat) > self.threshold:
            pyautogui.press('space') 
        
        # Calculate the time window for calculate the drop above
        if  (time.time() - self.time_start) > (1./5):
            self.time_start = time.time()
            self.previous_beat = self.current_beat

    def autonomous_path(self, path):        
        self.fft.run()
        self.current_beat = self.fft.binned_fft[0]

        if self.fft.beat_present(0, self.threshold):
            jump = round(self.current_beat/2)
          
            if self.path_counter < len(path):
                self.current_mouse_position[0] = path[self.path_counter][0]
                self.current_mouse_position[1] = path[self.path_counter][1]
            else:
                self.path_counter = 0

            # Remove the previous random movement
            self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment[0]
            self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment[1]
            
            # Calculate the next random movement
            self.random_increment = [random.randrange(-jump,jump), random.randrange(-jump,jump)]

            # Caculate new position
            self.new_mouse_position = [self.current_mouse_position[0] + self.random_increment[0], self.current_mouse_position[1] + self.random_increment[1]]

            # Drag the mouse
            pyautogui.dragTo(self.new_mouse_position[0], self.new_mouse_position[1], button='left')

            # Update position
            self.current_mouse_position = self.new_mouse_position

            # Update counter
            self.path_counter += 1

        # If there is a drop press 'space'
        if round(self.current_beat - self.previous_beat) > self.threshold:
            pyautogui.press('space') 
        
        # Calculate the time window for calculate the drop above
        if  (time.time() - self.time_start) > (1./10):
            self.time_start = time.time()
            self.previous_beat = self.current_beat
        
    def run(self):
        grid = np.ones((pyautogui.size()[0], pyautogui.size()[1]))

        for row in range(0, 500):
            for column in range(500, 1000):
                grid[column][row] = 0

        a = astar(grid)
        path = a.search([75,200], [75, 650])
        path = path + a.search([75, 650], [1400, 650])
        path = path + a.search([1400, 650], [1400, 200])
        path = path + a.search([1400, 200], [75, 200])

        while True:
            self.autonomous_path(path)

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

    viz = beat_viz(args.device)

    try:
        server_thread.start()
        print("Server started at {} port {}".format(args.ip, args.port))
        viz.run()

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()