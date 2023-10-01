import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import wave
import os
import tempfile

# Constants for audio processing
SAMPLE_RATE = 44100  # Sample rate (in Hz)
WINDOW_SIZE = 1024   # Size of each FFT window
RECORDING_DURATION = 20  # Duration to save audio (in seconds)

# Global variables for audio processing and playback
audio_buffer = []
playback_device_id = None

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
# Function to plot the spectrum
def plot_spectrum(indata, frames, time, status):
    global spec_data, fig, ax

    print("Received audio data:")
    print(indata)

    if status:
        print("Error in callback:", status)
        return

    # Calculate the spectrogram
    spec_data = np.abs(np.fft.fft(indata.flatten(), n=WINDOW_SIZE))
    freqs = np.fft.fftfreq(len(spec_data), d=1.0/SAMPLE_RATE)

    # Update the plot
    ax.clear()
    ax.plot(freqs, 20 * np.log10(spec_data))  # Convert to dB
    ax.set_xlim(0, SAMPLE_RATE / 2)
    ax.set_ylim(bottom=-100, top=10)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Spectrum')
    fig.canvas.draw()  # Update the plot
    fig.canvas.flush_events()  # Ensure the GUI event loop is updated

# Function to save the audio to a WAV file
def save_audio():
    global audio_buffer
    if len(audio_buffer) == 0:
        print("No audio to save.")
        return

    # Create a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
        wav_filename = tmpfile.name

    # Write the audio data to the WAV file
    with wave.open(wav_filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(np.array(audio_buffer).astype(np.int16).tobytes())

    print("Audio saved to:", wav_filename)

# Function to play the saved audio
def play_audio():
    global playback_device_id

    if playback_device_id is None:
        print("Please select a playback device.")
        return

    # Load the saved audio file
    wav_filename = "audio.wav"  # Change this to the actual file name
    if not os.path.isfile(wav_filename):
        print("No saved audio found.")
        return

    # Load and play the audio using sounddevice
    audio_data, fs = sd.read(wav_filename, dtype='int16')
    sd.play(audio_data, samplerate=fs, device=playback_device_id)
    sd.wait()

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

# Function to handle saving audio
def save_audio_button():
    save_audio()

# Function to handle playing saved audio
def play_audio_button():
    play_audio()

def get_speaker_devices():
    speaker_devices = []
    i = 0
    for dev in sd.query_devices():
        if dev['max_output_channels'] > 0:
            try:
                sd.check_output_settings(device=dev["name"])
                speaker_devices.append((i, dev['name']))
            except sd.PortAudioError as e:
                log_to_debug(f"Error checking device '{dev['name']}': {str(e)}")
            except Exception as e:
                log_to_debug(f"An unexpected error occurred: {str(e)}")
        i += 1
    return speaker_devices

# Function to handle dropdown selection for speakers
def on_select_speakers(event):
    selected_device_id = getSelectedSpeakerIndex()
    print(f"Selected speaker device ID: {selected_device_id}")

# Function to get the selected speaker device index
def getSelectedSpeakerIndex():
    str_device = speaker_dropdown.get()
    str_device = str_device.split(',')[0]
    str_device = str_device.split(':')[1]
    str_device = str_device.strip()
    selected_index = int(str_device)
    return selected_index

# Get a list of available speaker devices
speaker_devices = get_speaker_devices()

# Dropdown for speaker selection
speaker_var = tk.IntVar(root)
speaker_dropdown = ttk.Combobox(root, textvariable=speaker_var, width=50, state="readonly")
speaker_dropdown.bind("<<ComboboxSelected>>", on_select_speakers)

# Populate the dropdown with speaker device names
speaker_dropdown['values'] = [f"ID: {i}, Name: {device}" for i, device in speaker_devices]
speaker_dropdown.pack(pady=10)

# Button to start listening
listen_button = tk.Button(root, text="Start Listening", command=start_listening)
listen_button.pack(pady=10)

# Button to save audio
save_button = tk.Button(root, text="Save Audio", command=save_audio_button)
save_button.pack(pady=10)

# Button to play saved audio
play_button = tk.Button(root, text="Play Saved Audio", command=play_audio_button)
play_button.pack(pady=10)

root.mainloop()
