from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
from threading import Thread, Event
import time
import uuid
import csv
import numpy as np


class LSLSender:

    def __init__(self, *args):
        info = StreamInfo(*args)
        self.outlet = StreamOutlet(info)
        self.event = Event()

    def _send_sample(self, frequency):
        while True:
            if self.event.is_set():
                break
            self.outlet.push_sample(self.sample)
            time.sleep(1/frequency)

    def start_sending_thread(self, sample, frequency=250):
        self.event.clear()
        self.sample = sample
        Thread(target=self._send_sample, args=[frequency]).start()

    def update_sample(self, sample):
        self.sample = sample

    def stop_sending_thread(self):
        self.event.set()


class LSLReceiver:

    def __init__(self):

        stream = resolve_stream('type', 'EEG')
        self.inlet = StreamInlet(stream[0])

        stream = resolve_stream('type', 'Markers')
        self.marker_inlet = StreamInlet(stream[0])

        self.event = Event()
    
    def _recieve_sample(self, filename):
        data = []
        while True:
            if self.event.is_set():
                break
            sample, timestamp = self.inlet.pull_sample()
            marker, _ = self.marker_inlet.pull_sample()
            data.append([timestamp] + sample + [marker])

        print("test")
        with open(f'{filename}_{uuid.uuid4()}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp'] + [f'Ch{i+1}' for i in range(len(sample))] + ['marker'])
            writer.writerows(data)
    
    def start_recieving_thread(self, filename):
        self.event.clear()
        Thread(target=self._recieve_sample, args=[filename]).start()

    def stop_recieving_thread(self):
        self.event.set()
        print(f'Event is set:{self.event.is_set()}')


def main():
    frequency = 250

    eeg_sender = LSLSender('eeg', 'EEG', 8, 250, 'float32', 'myuid34234')
    eeg_sender.start_sending_thread(np.random.rand(8), frequency)


if __name__ == '__main__':
    main()