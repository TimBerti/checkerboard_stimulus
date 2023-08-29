from pylsl import StreamInlet, resolve_stream
import csv
from datetime import datetime

print("Loading the library...")

print("Resolving an EEG stream...")
eeg_stream = []
while not eeg_stream:
    eeg_stream = resolve_stream('type', 'EEG')

print("Resolving a Marker stream...")
marker_stream = []
while not marker_stream:
    marker_stream = resolve_stream('type', 'Markers')

print("Opening an EEG inlet...")
eeg_inlet = StreamInlet(eeg_stream[0])

print("Opening a Marker inlet...")
marker_inlet = StreamInlet(marker_stream[0])

print("Waiting for the first marker to start data collection...")
start_collection = False
current_marker = None
data = []

try:
    while True:
        if not start_collection:
            marker_sample, marker_timestamp = marker_inlet.pull_sample()
            if marker_sample is not None:
                current_marker = marker_sample[0]
                start_collection = True
                print("First marker received, starting data collection...")
        else:
            sample, timestamp = eeg_inlet.pull_sample()
            sample.append(timestamp)

            # Check for new marker samples
            marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)
            if marker_sample is not None:
                current_marker = marker_sample[0]

            # Check if the current marker is '6'
            if current_marker == 8:
                print("Marker '8' received, stopping data collection...")
                break

            # Append the current marker to the sample
            sample.append(current_marker)

            #print(sample)
            #print(len(sample))
            #print(timestamp)
            data.append(sample)

except KeyboardInterrupt:
    print("Interrupted!")

print("finally")
# Save the data to a CSV file after the loop ends
current_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = fr"C:\Users\MetisVidere\Desktop\Experiments\tim_14_channel_cca{current_date_time}.csv"
with open(outfile, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['EEG'+str(i+1) for i in range(20)] + ['Timestamp', 'MarkerID'])
    writer.writerows(data)

print(f"Data written to {outfile}")