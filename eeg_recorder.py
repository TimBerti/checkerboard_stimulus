from pylsl import StreamInlet, resolve_stream
import uuid
import csv
import json

subject = 'Test'

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
        print(marker)
        current_marker = marker
    if current_marker[0] == 'stop':
        break
    if current_marker[0] is not None:
        data.append([timestamp] + sample + current_marker)


meta_data = json.loads(data[0][-1])
filename = f'{subject}_{meta_data["deficiency"]}_{meta_data["severity"]}_{meta_data["series"]}_{uuid.uuid4()}'

with open(f'../Data/{filename}.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([f'Subject: {subject}'])
    writer.writerow([f'Series: {meta_data["series"]}'])
    writer.writerow([f'Screen Width: {meta_data["screen_width"]}'])
    writer.writerow([f'Screen Height: {meta_data["screen_height"]}'])
    writer.writerow([f'Frequency: {meta_data["frequency"]}'])
    writer.writerow([f'Tile Size: {meta_data["tile_size"]}'])
    writer.writerow([f'Color Vision Deficiency: {meta_data["deficiency"]}'])
    writer.writerow([f'Severity: {meta_data["severity"]}'])
    writer.writerow([])
    writer.writerow(['timestamp'] + [f'Ch{i+1}' for i in range(len(sample))] + ['marker'])
    writer.writerows(data[1:])
    print(f'{filename}.csv')
