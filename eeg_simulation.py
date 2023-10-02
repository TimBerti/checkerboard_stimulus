from pylsl import StreamInfo, StreamOutlet
import time
import numpy as np

frequency = 250
info = StreamInfo('eeg', 'EEG', 8, 250, 'float32', 'myuid34234')
outlet = StreamOutlet(info)
while True:
    outlet.push_sample(np.random.rand(8))
    time.sleep(1/frequency)
