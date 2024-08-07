from src.stream_analyzer import Stream_Analyzer
import time

class fft_analyzer:
    raw_fftx = None
    raw_fft = None
    binned_fftx = None
    binned_fft = None
    sound_device_index = None
    visualizer = None
    
    def __init__(self, sound_device_index, nbins=8):
        self.sound_device_index = sound_device_index
        self.visualizer = False
        self.nbins = nbins

        self.ear = Stream_Analyzer(
                        device = self.sound_device_index, # Pyaudio (portaudio) device index, defaults to first mic input
                        rate   = None,                    # Audio samplerate, None uses the default source settings
                        FFT_window_size_ms  = 60,         # Window size used for the FFT transform
                        updates_per_second  = 500,        # How often to read the audio stream for new data
                        smoothing_length_ms = 50,         # Apply some temporal smoothing to reduce noisy features
                        n_frequency_bins = self.nbins,    # The FFT features are grouped in bins
                        visualize = self.visualizer,      # Visualize the FFT features with PyGame
                        verbose   = 0,                    # Print running statistics (latency, fps, ...)
                        height    = 450,                  # Height, in pixels, of the visualizer window,
                        window_ratio = 24/9               # Float ratio of the visualizer window. e.g. 24/9
                        )

        self.fps = 60                                     #How often to update the FFT features + display
        self.last_update = time.time()
        print("All ready, starting audio measurements now...")

    def beat_present(self, bin_id, threshold):
        if self.binned_fft[bin_id] > threshold:
            return True
        else:
            return False

    def run(self):
        if (time.time() - self.last_update) > (1./self.fps):
            self.last_update = time.time()
            self.raw_fftx, self.raw_fft, self.binned_fftx, self.binned_fft = self.ear.get_audio_features()                
