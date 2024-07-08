import numpy as np
import pyaudio
import time
import librosa

class audiohandler(object):
    def __init__(self):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2
        self.p = None
        self.stream = None
        self.test = None
        self.beats  = np.zeros(shape=(1, 1))

    def start(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK,
                                  input_device_index=3)
        
        self.stream.start_stream()

    def stop(self):
        self.stream.close()
        self.p.terminate()

    def callback(self, in_data, frame_count, time_info, flag):
        numpy_array = np.frombuffer(in_data, dtype=np.float32)
        onset_env = librosa.onset.onset_strength(y=numpy_array)
        pulse = librosa.beat.plp(onset_envelope=onset_env)
        #self.beats = np.flatnonzero(librosa.util.localmax(pulse))
        self.beats = librosa.effects.percussive(y=numpy_array)
        print(self.beats)
        return None, pyaudio.paContinue
    
    def beat_present(self):
        if self.beats[0] == 4:
                return True
        else:
                return False

    # def mainloop(self):
    #     while (self.stream.is_active()): # if using button you can set self.stream to 0 (self.stream = 0), otherwise you can use a stop condition
    #         time.sleep(2.0)

