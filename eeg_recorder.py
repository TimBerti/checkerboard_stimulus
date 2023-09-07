from pylsl import StreamInlet, resolve_stream
import uuid
import csv

subject = 'Test'
color_vision_deficiency = 'None'
severity = 0.5
series = 'Protanomaly-red'

filename = f'{subject}_{color_vision_deficiency}_{severity}_{series}_{uuid.uuid4()}'

stream = resolve_stream('type', 'EEG')
eeg_inlet = StreamInlet(stream[0])

stream = resolve_stream('type', 'Markers')
marker_inlet = StreamInlet(stream[0])

data = []
current_marker = [None]
while True:
    sample, timestamp = eeg_inlet.pull_sample()
    marker, _ = marker_inlet.pull_sample(timeout=0.0)
    if marker is not None:
        current_marker = marker
    print(current_marker)
    if current_marker[0] == 'black-and-white-slow':
        break
    if current_marker[0] is not None:
        data.append([timestamp] + sample + current_marker)
with open(f'{filename}.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['timestamp'] + [f'Ch{i+1}' for i in range(len(sample))] + ['marker'])
    writer.writerows(data)