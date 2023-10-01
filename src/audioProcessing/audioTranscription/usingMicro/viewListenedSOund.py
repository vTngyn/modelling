import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import wave
import os
import tempfile
import threading
import queue

# Constants for audio processing
SAMPLE_RATE = 44100  # Sample rate (in Hz)
WINDOW_SIZE = 1024   # Size of each FFT window
RECORDING_DURATION = 20  # Duration to save audio (in seconds)

# Global variables for audio processing and playback
audio_buffer = []
playback_device_id = None

fig = None
ax = None
wav_filename=None

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
# Function to plot the spectrum and save audio data
def plot_spectrum(indata, frames, time, status):
    global spec_data, fig, audio_buffer, ax

    if status:
        print("Error in callback:", status)
        return

    # Calculate the spectrogram
    spec_data = np.abs(np.fft.fft(indata.flatten(), n=WINDOW_SIZE))

    # Append the audio data to the buffer
    audio_buffer.extend(indata.tolist())

    # Keep only the last 20 seconds of audio data
    max_buffer_size = int(SAMPLE_RATE * RECORDING_DURATION)
    if len(audio_buffer) > max_buffer_size:
        audio_buffer = audio_buffer[-max_buffer_size:]

    setupAx(ax, fig)

def setupAx(ax, fig):
    # Update the plot
    if (ax):
        ax.clear()
        ax.plot(20 * np.log10(spec_data))
        plt.xlim(0, WINDOW_SIZE // 2)
        plt.ylim(bottom=-100, top=10)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.title('Spectrum')

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

# Function to update the plot periodically
def update_plot():
    global fig, ax
    # Update the plot
    # setupAx(ax, fig)
    root.after(100, update_plot)  # Update the plot every 100 milliseconds

# Function to handle the audio stream and updating the plot
def audio_stream(q):
    with sd.InputStream(callback=plot_spectrum, channels=1, samplerate=SAMPLE_RATE):
        while True:
            # Put a message in the queue to update the plot
            q.put("update_plot")
            # Sleep for a short duration to control plot update rate
            sd.sleep(100)

# Function to start the audio stream thread
def start_audio_thread(q):
    audio_thread = threading.Thread(target=audio_stream, args=(q,))
    audio_thread.daemon = True
    audio_thread.start()

# Function to save the audio to a WAV file
def save_audio():
    global audio_buffer, wav_filename
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

CHUNK_SIZE = 1024    # Size of each chunk to read from the file

# Function to read audio from file and stream it
def stream_audioFromFile(file_path):
    global audio_buffer

    wf = wave.open(file_path, 'rb')

    while True:
        data = wf.readframes(CHUNK_SIZE)
        if not data:
            break

        # Convert the audio data to a numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_buffer.extend(audio_data)

    # Close the audio file
    wf.close()

# Function to play the audio from the buffer
def play_audioThread():
    global audio_buffer

    if not audio_buffer:
        print("No audio to play.")
        return

    # Convert the audio buffer to a numpy array
    audio_data = np.array(audio_buffer)

    # Play the audio
    sd.play(audio_data, samplerate=SAMPLE_RATE)
    sd.wait()

# Function to play the saved audio
def play_audio_fromFile():
    global wav_filename
    playback_device_id = getSelectedDeviceIndex()

    if playback_device_id is None:
        print("Please select a playback device.")
        return

    if not audio_buffer:
        print("No audio to play.")
        return

    # Load the saved audio file
    if not os.path.isfile(wav_filename):
        print("No saved audio found.")
        return

    # Start streaming audio from a file (modify the file path accordingly)
    file_path = 'path/to/your/audio/file.wav'
    audio_thread = threading.Thread(target=stream_audioFromFile, args=(file_path,))
    audio_thread.start()

    # Play the audio (modify the timing accordingly)
    play_thread = threading.Thread(target=play_audioThread)
    play_thread.start()

def play_audio():
    play_audioFromBuffer()
def play_audioFromBuffer():
    global wav_filename, audio_buffer
    playback_device_id = getSelectedSpeakerIndex()

    if playback_device_id is None:
        print("Please select a playback device.")
        return

    if not audio_buffer:
        print("No audio to play.")
        return

    # Load the saved audio file
    if not os.path.isfile(wav_filename):
        print("No saved audio found.")
        return

    # Load and play the audio using sounddevice
    #audio_data, fs = sd.read(wav_filename, dtype='int16')
    #sd.play(audio_data, samplerate=fs, device=playback_device_id)

    audio_data = np.array(audio_buffer).flatten()

    # Get the info of the selected playback device
    playback_device_info = sd.query_devices(device=playback_device_id, kind='output')
    print(playback_device_info)

    # Ensure the audio data has the correct number of channels for the playback device
    num_output_channels = playback_device_info.get('max_output_channels', 1)
    if (num_output_channels) > 0:
        audio_data = audio_data.reshape(-1, num_output_channels)

        sd.play(audio_data, samplerate=SAMPLE_RATE, device=playback_device_id)
        sd.wait()
    else:
        print("num_output_channels for selected audio output device is 0")

def getSelectedDeviceIndex():
    global device_dropdown
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

    # Get the info of the selected playback device
    recording_device_info = sd.query_devices(device=selected_device_id, kind='input')
    print(recording_device_info)


    # Set up the audio stream with the selected microphone and callback function
    stream = sd.InputStream(device=selected_device_id, channels=1, samplerate=SAMPLE_RATE, callback=plot_spectrum)
    #stream = sd.InputStream(device=selected_device_id, channels=1, samplerate=SAMPLE_RATE, callback=lambda indata, frames, time, status: plot_spectrum(indata, frames, time, status,ax))

    # Start the audio stream
    with stream:
        plt.ion()  # Turn on interactive mode for plotting
        if not ax:
            fig, ax = plt.subplots()
        plt.show()
        root.mainloop()
        # Start updating the plot periodically
        #update_plot()

        # Run the main loop for the GUI
        #root.mainloop()

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
    print(str_device)
    str_device = str_device.split(',')[0]
    str_device = str_device.split(':')[1]
    str_device = str_device.strip()
    selected_index = int(str_device)
    #print(f"selected speaker={selected_index}")
    return selected_index

# Function to stop the audio stream
def stop_listening():
    plt.close(fig)
    root.quit()


# Function to handle starting and stopping listening
listening = False

def toggle_listening():
    global listening, toggle_button, ax, fig
    if listening:
        toggle_button.config(text="Stop Listening")
        stop_listening()
        ax=None
        fx=None
    else:
        toggle_button.config(text="Start Listening")
        start_listening()

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
#listen_button = tk.Button(root, text="Start Listening", command=start_listening)
#listen_button.pack(pady=10)
# Button to stop listening
# stop_button = tk.Button(root, text="Stop Listening", command=stop_listening)
# stop_button.pack(pady=10)

# Button to start/stop listening
toggle_button = tk.Button(root, text="Start Listening", command=toggle_listening)
toggle_button.pack(pady=10)

# Button to save audio
save_button = tk.Button(root, text="Save Audio", command=save_audio_button)
save_button.pack(pady=10)

# Button to play saved audio
play_button = tk.Button(root, text="Play Saved Audio", command=play_audio_button)
play_button.pack(pady=10)


# Update the plot periodically
root.after(100, update_plot)

# Start the audio stream thread
q = queue.Queue()
start_audio_thread(q)

root.mainloop()
