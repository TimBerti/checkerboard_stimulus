from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
import time
from threading import Thread, Event


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
            time.sleep(frequency)

    def start_sending_thread(self, sample, frequency=1/250):
        self.sample = sample
        Thread(target=self._send_sample, args=[frequency]).start()

    def update_sample(self, sample):
        self.sample = sample

    def stop_sending_thread(self):
        self.event.set()


class LSLReceiver:

    def __init__(self):
        stream = resolve_stream('type', 'Marker')
        self.marker_inlet = StreamInlet(stream[0])

        stream = resolve_stream('type', 'EEG')
        self.eeg_inlet = StreamInlet(stream[0])

        self.event = Event()
    
    def _recieve_sample(self, frequency):
        while True:
            if self.event.is_set():
                break
            marker, _ = self.marker_inlet.pull_sample()
            eeg_data, timestamp = self.eeg_inlet.pull_sample()
            print(timestamp, eeg_data, marker[0])
            time.sleep(frequency)
    
    def start_recieving_thread(self, frequency=1/250):
        Thread(target=self._recieve_sample, args=[frequency]).start()

    def stop_recieving_thread(self):
        self.event.set()


def main():
    frequency = 1

    marker_sender = LSLSender('test', 'Marker', 1, 0, 'string', 'myuidw43536')
    marker_sender.start_sending_thread(['green'], frequency)

    eeg_sender = LSLSender('eeg', 'EEG', 8, 250, 'float32', 'myuid34234')
    eeg_sender.start_sending_thread([1, 2, 3, 4, 5, 6, 7, 8], frequency)

    receiver = LSLReceiver()
    receiver.start_recieving_thread(frequency)

    time.sleep(5)
    marker_sender.update_sample(['red'])

    time.sleep(5)
    receiver.stop_recieving_thread()
    marker_sender.stop_sending_thread()
    eeg_sender.stop_sending_thread()


if __name__ == '__main__':
    main()