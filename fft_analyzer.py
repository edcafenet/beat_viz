from src.stream_analyzer import Stream_Analyzer
import time
import pyautogui
import random

class fft_analyzer:
    raw_fftx = None
    raw_fft = None
    binned_fftx = None
    binned_fft = None

    def convert_window_ratio(self, window_ratio):
        if '/' in window_ratio:
            dividend, divisor = window_ratio.split('/')
            try:
                float_ratio = float(dividend) / float(divisor)
            except:
                raise ValueError('window_ratio should be in the format: float/float')
            return float_ratio
        raise ValueError('window_ratio should be in the format: float/float')

    def beat_present(self):
        if self.binned_fft[1] > 10.0:
            return True
        else:
            return False

    def run(self):
        window_ratio = self.convert_window_ratio("24/9")

        ear = Stream_Analyzer(
                        device = 0,                  # Pyaudio (portaudio) device index, defaults to first mic input
                        rate   = None,               # Audio samplerate, None uses the default source settings
                        FFT_window_size_ms  = 60,    # Window size used for the FFT transform
                        updates_per_second  = 500,   # How often to read the audio stream for new data
                        smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
                        n_frequency_bins = 8,        # The FFT features are grouped in bins
                        visualize = 0,               # Visualize the FFT features with PyGame
                        verbose   = 0,    # Print running statistics (latency, fps, ...)
                        height    = 450,     # Height, in pixels, of the visualizer window,
                        window_ratio = 24/9  # Float ratio of the visualizer window. e.g. 24/9
                        )

        fps = 60  #How often to update the FFT features + display
        last_update = time.time()
        print("All ready, starting audio measurements now...")
        fft_samples = 0
        while True:
            if (time.time() - last_update) > (1./fps):
                last_update = time.time()
                self.raw_fftx, self.raw_fft, self.binned_fftx, self.binned_fft = ear.get_audio_features()
                fft_samples += 1

                if self.binned_fft[0] > 10.0:
                    jump = round(self.binned_fft[1])
                    pyautogui.mouseDown()
                    pyautogui.moveRel(random.randrange(-jump,jump),random.randrange(-jump,jump))
                    pyautogui.mouseUp()

                #    print(f"Got fft_features #{fft_samples} of shape {raw_fft.shape}")
            # elif args.sleep_between_frames:
            #     time.sleep(((1./fps)-(time.time()-last_update)) * 0.99)



