from src.stream_analyzer import Stream_Analyzer
import time
import pyautogui
import random

class fft_analyzer:
    raw_fftx = None
    raw_fft = None
    binned_fftx = None
    binned_fft = None
    sound_device_index = None
    visualizer = None

    random_increment_x = 0
    random_increment_y = 0
    current_mouse_position = [0,0]

    def __init__(self, sound_device_index, visualizer):
        self.sound_device_index = sound_device_index
        self.visualizer = visualizer

    def beat_present(self, bin_id, threshold):
        if self.binned_fft[bin_id] > threshold:
            return True
        else:
            return False

    def run(self):
        ear = Stream_Analyzer(
                        device = self.sound_device_index, # Pyaudio (portaudio) device index, defaults to first mic input
                        rate   = None,               # Audio samplerate, None uses the default source settings
                        FFT_window_size_ms  = 60,    # Window size used for the FFT transform
                        updates_per_second  = 500,   # How often to read the audio stream for new data
                        smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
                        n_frequency_bins = 8,        # The FFT features are grouped in bins
                        visualize = self.visualizer, # Visualize the FFT features with PyGame
                        verbose   = 0,    # Print running statistics (latency, fps, ...)
                        height    = 450,     # Height, in pixels, of the visualizer window,
                        window_ratio = 24/9  # Float ratio of the visualizer window. e.g. 24/9
                        )

        fps = 60  #How often to update the FFT features + display
        last_update = time.time()
        print("All ready, starting audio measurements now...")
        while True:
            if (time.time() - last_update) > (1./fps):
                last_update = time.time()
                self.raw_fftx, self.raw_fft, self.binned_fftx, self.binned_fft = ear.get_audio_features()
                
                if self.beat_present(0, 20):
                    self.current_mouse_position[0] = pyautogui.position()[0]
                    self.current_mouse_position[1] = pyautogui.position()[1]

                    self.current_mouse_position[0] = self.current_mouse_position[0] - self.random_increment_x
                    self.current_mouse_position[1] = self.current_mouse_position[1] - self.random_increment_y
                    
                    jump = round(self.binned_fft[0]/4)
                    self.random_increment_x = random.randrange(-jump,jump)
                    self.random_increment_y = random.randrange(-jump,jump)

                    pyautogui.mouseDown()
                    pyautogui.moveTo(self.current_mouse_position[0] + self.random_increment_x, self.current_mouse_position[1] + self.random_increment_y)
                    pyautogui.mouseUp()