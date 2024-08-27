import pyautogui
import socketserver, threading, time
from threading import Thread
from fft_analyzer import fft_analyzer
import random
import math
import argparse
from astar import astar
import numpy as np

# Position variables 
x = 0
y = 0
z = 0

color = None

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

class beat_viz():
    def __init__(self, device_id):
        self.fft = fft_analyzer(device_id)
        self.fft.run()
                
        self.time_start = time.time()
        self.current_mouse_position = [0,650]
        self.new_mouse_position = [0,0]
        self.random_increment = [0,0]
    
        self.current_beat = 0
        self.previous_beat = 0
        self.threshold = 20

        # A star variables
        self.path_counter = 0

        # Direction of the movement
        self.direction_forward = None

        global color

    def get_kick(self):
        # Run the FFT and retrieve a value for the first bin
        self.fft.run()
        self.current_beat = self.fft.binned_fft[0]

    def move_mouse(self, jump):
        # Remove the previous random movement
        self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment[0]
        self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment[1]

        # Calculate the next random movement
        self.random_increment = [random.randrange(-jump,jump), random.randrange(-jump,jump)]

        # Caculate new position
        self.new_mouse_position = [self.current_mouse_position[0] + self.random_increment[0], self.current_mouse_position[1] + self.random_increment[1]]

        # Move the mouse and click (it seems it is better than drag)
        pyautogui.mouseDown()
        pyautogui.moveTo(self.new_mouse_position[0], self.new_mouse_position[1])
        pyautogui.mouseUp()

        # Update position
        self.current_mouse_position = self.new_mouse_position

    def move_mouse_hand(self, jump):
        # Remove the previous random movement
        self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment[0]
        self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment[1]

        # Calculate the next random movement
        self.random_increment = [random.randrange(-jump,jump), random.randrange(-jump,jump)]

        # Caculate new position
        self.new_mouse_position = [self.current_mouse_position[0] + self.random_increment[0], self.current_mouse_position[1] + self.random_increment[1]]

        # Drag behavior
        pyautogui.dragTo(self.new_mouse_position[0], self.new_mouse_position[1], button='left')

        # Update position
        self.current_mouse_position = self.new_mouse_position

    def drop_splash(self):
        # If there is a drop press 'space'
        if round(self.current_beat - self.previous_beat) > (self.threshold+5):
            pyautogui.press('space') 
        
        # Calculate the time window for calculate the drop above
        if  (time.time() - self.time_start) > (1./5):
            self.time_start = time.time()
            self.previous_beat = self.current_beat

    def autonomous_line(self):        
        self.get_kick()

        if self.fft.beat_present(0, self.threshold):
            if self.current_mouse_position[0] <= 25:
                self.direction_forward = True
            elif self.current_mouse_position[0] > (pyautogui.size()[0] - 25):
                self.direction_forward = False

            jump = round(self.current_beat/3)

            if self.direction_forward:
                self.current_mouse_position[0] += jump
            if not self.direction_forward:
                self.current_mouse_position[0] -= jump 
            
            # Update the mouse position according to the jump
            self.move_mouse(jump)
        
        # Splash effect for the drop
        # self.drop_splash()

    def autonomous_path(self, path):        
        self.get_kick()

        if self.fft.beat_present(0, self.threshold):
            jump = round(self.current_beat/3)
          
            if self.path_counter < len(path):
                self.current_mouse_position[0] = path[self.path_counter][0]
                self.current_mouse_position[1] = path[self.path_counter][1]
            else:
                self.path_counter = 0

            # Update the mouse position according to the jump
            self.move_mouse(jump)
        
            # Update counter
            self.path_counter += 1

        # Splash effect for the drop
        self.drop_splash()

    def hand_control_trigger(self):
        if z > 1800:
            return True
        else:
            return False

    def hand_control(self):        
        self.get_kick()

        if self.fft.beat_present(0, self.threshold):
            jump = round(self.current_beat/3)
        
            self.current_mouse_position[0] = x
            self.current_mouse_position[1] = y
            
            self.move_mouse_hand(jump)
        
        # Splash effect for the drop
        # self.drop_splash()
    
    def run(self):
        grid = np.ones((pyautogui.size()[0], pyautogui.size()[1]))

        # Forbidden space
        for row in range(0, 450):
            for column in range(750, 1150):
                grid[column][row] = 0

        # A star algorithm with the path desired
        a = astar(grid)
        astar_thread = threading.Thread()
        astar_thread.daemon = True
        astar_thread.start()
        
        path = a.search([75,200], [75, 650])
        path = path + a.search([75, 650], [1400, 650])
        path = path + a.search([1400, 650], [1400, 200])
        path = path + a.search([1400, 200], [75, 200])
        path = path[::3]

        # Path that will be used later
        circle_path = path

        go_to_hand = False
        first_time = True
        hand_control = False

        while True:
            if self.hand_control_trigger() and first_time:
                first_time = False
                path = a.search([self.current_mouse_position[0], self.current_mouse_position[1]], [x,y])
                path = path[::4]
                go_to_hand = True        
                self.path_counter = 0

            if go_to_hand:
                if math.dist([self.current_mouse_position[0], self.current_mouse_position[1]], [x,y]) < 75:
                    hand_control = True
         
            if hand_control:
                self.hand_control()

                if self.hand_control_trigger():
                    go_to_hand = False
                    hand_control = False
                    
                    path = a.search([x,y], [75, 200])
                    path = path + circle_path
                    path = path[::3]

                    self.path_counter = 0

            else:
                self.autonomous_path(path)
                first_time = True
        

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
    # Parsing the arguments from command line
    args = parse_args()
    
    # UDP Server parameters 
    server = ThreadedUDPServer((args.ip, args.port), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    # Viz object that contains all the different modes
    viz = beat_viz(args.device)

    try:
        server_thread.start()
        print("Server started at {} port {}".format(args.ip, args.port))
        viz.run()

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()