import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

# Constants for audio processing
SAMPLE_RATE = 44100  # Sample rate (in Hz)
WINDOW_SIZE = 1024   # Size of each FFT window

# Function to get a list of microphone devices
def get_microphone_devices_fail():
    info = sd.query_devices()
    mic_devices = []
    for i, device in enumerate(info):
        if 'input' in device['name'].lower():
            try:
                # Test opening the device as input (microphone)
                with sd.InputStream(device=i, channels=1, samplerate=SAMPLE_RATE, blocksize=WINDOW_SIZE):
                    mic_devices.append((i, device['name']))
            except sd.PortAudioError:
                pass  # Skip devices that cause errors when opened as input
    return mic_devices

def get_microphone_devices():
    working_devices = []
    i=0
    for dev in sd.query_devices():
        try:
            sd.check_input_settings(device=dev["name"])
            #working_devices.append(dev)
            working_devices.append((i, dev['name']))
        except sd.PortAudioError as e:
            log_to_debug(f"Error checking device '{dev['name']}': {str(e)}")
        except Exception as e:
            log_to_debug(f"An unexpected error occurred: {str(e)}")
        i+=1
    return working_devices

def log_to_debug(message):
    print(message + "\n")

# Function to handle dropdown selection
def on_select(event):
    selected_device_id = getSelectedDeviceIndex()
    print(f"Selected device ID: {selected_device_id}")

# Get a list of available microphone devices
mic_devices = get_microphone_devices()

# Initialize Tkinter
root = tk.Tk()
root.title("Microphone Selector")

# Dropdown for microphone selection
device_var = tk.IntVar(root)
device_dropdown = ttk.Combobox(root, textvariable=device_var, width=50, state="readonly")
device_dropdown.bind("<<ComboboxSelected>>", on_select)

# Populate the dropdown with microphone device names
device_dropdown['values'] = [f"ID: {i}, Name: {device}" for i, device in mic_devices]
device_dropdown.pack(pady=10)

# Configure the audio input using the selected microphone
def plot_spectrum(indata, frames, time, status):
    if status:
        print("Error in callback:", status)
        return

    # Calculate the spectrogram
    spec_data = np.abs(np.fft.fft(indata.flatten(), n=WINDOW_SIZE))
    freqs = np.fft.fftfreq(len(spec_data), d=1.0/SAMPLE_RATE)

    # Update the plot
    ax.cla()
    ax.plot(freqs, 20 * np.log10(spec_data))  # Convert to dB
    ax.set_xlim(0, SAMPLE_RATE / 2)
    ax.set_ylim(bottom=-100, top=10)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Spectrum')
    plt.pause(0.001)


def getSelectedDeviceIndex():
    print(device_dropdown.get())
    str=device_dropdown.get().split(',')[0]
    str=str.split(':')[1]
    str=str.strip()
    selected_index = int(str)
    #selected_index = device_dropdown.current()
    return selected_index

def start_listening():
    global fig, ax
    #selected_device_id = device_var.get()
    selected_device_id = getSelectedDeviceIndex()
    if selected_device_id == -1:
        print("Please select a microphone device.")
        return

    fig, ax = plt.subplots()
    with sd.InputStream(device=selected_device_id, callback=plot_spectrum, channels=1, samplerate=SAMPLE_RATE):
        plt.ion()  # Turn on interactive mode for plotting
        plt.show()

# Button to start listening
listen_button = tk.Button(root, text="Start Listening", command=start_listening)
listen_button.pack(pady=10)

root.mainloop()
