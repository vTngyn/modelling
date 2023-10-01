import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
import wave
import os
import tempfile
import threading
import queue

class SpectrumAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.audio_thread = None
        self.isRecording = False
        self.isListening = False

        # Variables for audio processing
        self.audio_buffer = []
        self.recording_audio_buffer = []
        self.spec_data = None
        self.audioInputStream = None

        self.selected_speaker_device_id = None
        self.selected_mic_device_id = None

        # Constants for audio processing
        self.SAMPLE_RATE = 44100
        self.WINDOW_SIZE = 1024
        self.RECORDING_DURATION = 20
        self.WAVE_DISPLAY_DURATION = 5
        self.WAVE_DISPLAY_AMPLITUDE_MIN = 0.5
        self.SPECTRUM_DISPLAY_AMPLIFIER = 20

        master.title("Microphone Spectrum Analyzer")
        self.init_gui()


        #self.fig, self.ax = plt.subplots()
        self.fig1, self.ax_spectrum = plt.subplots()
        self.fig2, self.ax_waveform = plt.subplots()
        #self.fig, (self.ax_spectrum, self.ax_waveform) = plt.subplots(2, 1)
        self.fig1.subplots_adjust(bottom=0.2)
        self.fig2.subplots_adjust(bottom=0.2)
        # self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        # self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # self.canvas.draw()
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.master)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas1.draw()
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.master)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas2.draw()

    def init_gui(self):
        self.create_widgets()

    def create_widgets(self):
        # Dropdown for microphone selection
        self.microphone_devices = self.get_microphone_devices()
        self.device_var = tk.IntVar()
        self.device_dropdown = ttk.Combobox(self.master, textvariable=self.device_var, width=50, state="readonly")
        self.device_dropdown.bind("<<ComboboxSelected>>", self.on_select_microphones)
        self.device_dropdown['values'] = [f"ID: {i}, Name: {device}" for i, device in self.microphone_devices]
        self.device_dropdown.pack(pady=10)

        # Dropdown for speaker selection
        self.speaker_devices = self.get_speaker_devices()
        self.speaker_var = tk.IntVar()
        self.speaker_dropdown = ttk.Combobox(self.master, textvariable=self.speaker_var, width=50, state="readonly")
        self.speaker_dropdown.bind("<<ComboboxSelected>>", self.on_select_speakers)
        self.speaker_dropdown['values'] = [f"ID: {i}, Name: {device}" for i, device in self.speaker_devices]
        self.speaker_dropdown.pack(pady=10)

        # Button to start/stop listening
        self.toggle_button = tk.Button(self.master, text="Start Listening", command=self.toggle_listening)
        self.toggle_button.pack(pady=10)

        # Button to start/stop listening
        self.toggle_recording_button = tk.Button(self.master, text="Start Recording", command=self.toggle_recording)
        self.toggle_recording_button.pack(pady=10)

        # Button to save audio
        self.clear_recording_buffer_button = tk.Button(self.master, text="Clear recorded audio ", command=self.flush_recording_buffer)
        self.clear_recording_buffer_button.pack(pady=10)

        # Button to save audio
        self.save_button = tk.Button(self.master, text="Save Recorded Audio", command=self.save_audio_button)
        self.save_button.pack(pady=10)

        # Button to play saved audio
        self.play_button = tk.Button(self.master, text="Play from Recorded Audio", command=self.play_audio_from_RecordedBuffer)
        self.play_button.pack(pady=10)

        # Button to play saved audio
        self.play_button = tk.Button(self.master, text="Play from life Audio buffer", command=self.play_audio_from_LifeBuffer)
        self.play_button.pack(pady=10)

        self.adjust_listeningButtonLabel()
        self.adjust_recordingButtonLabel()


    def log_to_debug(self, message):
        print(message + "\n")

    def get_microphone_devices(self):
        working_devices = []
        i = 0
        for dev in sd.query_devices():
            try:
                sd.check_input_settings(device=dev["name"])
                # working_devices.append(dev)
                working_devices.append((i, dev['name']))
            except sd.PortAudioError as e:
                self.log_to_debug(f"Error checking device '{dev['name']}': {str(e)}")
            except Exception as e:
                self.log_to_debug(f"An unexpected error occurred: {str(e)}")
            i += 1
        return working_devices

    def get_speaker_devices(self):
        speaker_devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_output_channels'] > 0:
                speaker_devices.append((i, dev['name']))
        return speaker_devices

    def on_select_microphones(self, event):
        self.selected_mic_device_id = self.get_selected_microphone_index()
        print(f"Selected microphone device ID: {self.selected_mic_device_id}")

    def on_select_speakers(self, event):
        self.selected_speaker_device_id = self.get_selected_speaker_index()
        print(f"Selected speaker device ID: {self.selected_speaker_device_id}")

    def get_selected_microphone_index(self):
        try:
            str_device = self.device_dropdown.get()
            str_device = str_device.split(',')[0]
            str_device = str_device.split(':')[1]
            str_device = str_device.strip()
            selected_index = int(str_device)
        except Exception as e:
            print(e)
            selected_index=-1
        return selected_index

    def get_selected_speaker_index(self):
        try:
            str_device = self.speaker_dropdown.get()
            str_device = str_device.split(',')[0]
            str_device = str_device.split(':')[1]
            str_device = str_device.strip()
            selected_index = int(str_device)
        except Exception as e:
            print(e)
            selected_index=-1
        return selected_index


    def setupAx(self,ax, title, xlabel, ylabel, xlimLow, xlimhigh,ylimLow, ylimhigh):
        ax.clear()
        ax.set_xlim(xlimLow, xlimhigh)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if ylimLow:
            ax.set_ylim(bottom=ylimLow, top=ylimhigh)

    def plot_spectrum(self, indata, frames, time, status):
        #print('method: plot_spectrum')

        if status:
            print("Error in callback:", status)
            return

        self.spec_data = np.abs(np.fft.fft(indata.flatten(), n=self.WINDOW_SIZE))


        # Redraw the plot
        # self.canvas.draw()
        self.canvas1.draw()
        self.canvas2.draw()

        # Append the audio data to the buffer
        self.audio_buffer.extend(indata.tolist())
        if self.isRecording:
            self.recording_audio_buffer.extend(indata.tolist())

        # Keep only the last 20 seconds of audio data
        max_buffer_size = int(self.SAMPLE_RATE * self.RECORDING_DURATION)
        if len(self.audio_buffer) > max_buffer_size:
            self.audio_buffer = self.audio_buffer[-max_buffer_size:]

        # Create a time vector
        time_vector = np.arange(len(self.audio_buffer)) / self.SAMPLE_RATE

        # ax.clear()
        # ax.plot(time_vector, audio_buffer)
        # ax.set_xlim(0, RECORDING_DURATION)
        # ax.set_xlabel('Time (s)')
        # ax.set_ylabel('Amplitude')
        # ax.set_title('Waveform')
        if self.isListening:
            # Update the spectrum plot
            if self.ax_spectrum:
                self.setupAx(ax=self.ax_spectrum, title='Spectrum', xlabel='Frequency (Hz)', ylabel='Magnitude (dB)', xlimLow=0, xlimhigh=(self.WINDOW_SIZE // 2),ylimLow=-100, ylimhigh=10)

                self.ax_spectrum.plot(self.SPECTRUM_DISPLAY_AMPLIFIER * np.log10(self.spec_data))
                self.ax_spectrum.set_ylim(bottom=-100, top=10)

            # Update the waveform plot
            if self.ax_waveform:
                time_vector = np.arange(len(self.audio_buffer)) / self.SAMPLE_RATE
                self.setupAx(ax=self.ax_waveform, title='Waveform', ylabel='Amplitude', xlabel='Time (s)', xlimLow=0, xlimhigh=self.WAVE_DISPLAY_DURATION,ylimLow=None, ylimhigh=None)
                self.ax_waveform.plot(time_vector, self.audio_buffer)

            # Redraw the plot
            self.fig1.canvas.draw()
            self.fig1.canvas.flush_events()
            self.fig2.canvas.draw()
            self.fig2.canvas.flush_events()
            # self.fig.canvas.draw()
            # self.fig.canvas.flush_events()

    def adjust_listeningButtonLabel(self):
        #print('method: adjust_listeningButtonLabel')
        if not self.isListening:
            self.toggle_button.config(text="Start Listening")
        else:
            self.toggle_button.config(text="Stop Listening")

    def adjust_recordingButtonLabel(self):
        #print('method: adjust_recordingButtonLabel')
        if not self.isRecording:
            self.toggle_recording_button.config(text="Start Recording")
        else:
            self.toggle_recording_button.config(text="Stop Recording")


    def toggle_listening(self):
        print('method: toggle_listening')
        if self.toggle_button.cget("text") == "Start Listening":
            self.start_listening()
            self.adjust_listeningButtonLabel()
        else:
            self.stop_listening()
            self.adjust_listeningButtonLabel()


    def toggle_recording(self):
        print('method: toggle_recording')
        if self.toggle_recording_button.cget("text") == "Start Recording":
            self.start_recording()
            # self.toggle_recording_button.config(text="Stop Recording")
            self.adjust_recordingButtonLabel()
        else:
            self.stop_recording()
            #self.toggle_recording_button.config(text="Start Recording")
            self.adjust_recordingButtonLabel()

    def start_listening(self):
        print('method: start_listening')
        if not self.isListening:

            selected_device_id = self.get_selected_microphone_index()
            if selected_device_id == -1:
                print("Please select a microphone device.")
                return

            recording_device_info = sd.query_devices(device=selected_device_id, kind='input')
            print(recording_device_info)

            self.start_audio_stream(selected_device_id)
            self.adjust_listeningButtonLabel()

        # # Set up the audio stream with the selected microphone and callback function
        # self.stream = sd.InputStream(device=selected_device_id, channels=1, samplerate=self.SAMPLE_RATE,
        #                         callback=self.plot_spectrum)
        #
        # # Start the audio stream
        # with self.stream:
        #     plt.ion()
        #     plt.show()

    def stop_listening(self):
        print('method: stop_listening')
        if hasattr(self, 'audioInputStream') and self.audioInputStream.active:
            print('going to stop the stream')
            self.isListening = False
            #self.audioInputStream.stop_stream()
            self.audioInputStream.stop()
            # self.audioInputStream.close()
            # self.listeningstreamCLoseThread(())
            self.audioInputStream=None
        self.adjust_listeningButtonLabel()

    # Function to close the stream
    def listeningstreamCLoseThread(self, stream):
        print('method: listeningstreamCLoseThread')
        close_thread = threading.Thread(target=self.close_listeningstream, args=(self.audioInputStream,))
        close_thread.start()

    def close_listeningstream(self, stream):
        print('method: close_listeningstream')
        stream.stop()
        stream.close()
    def start_recording(self):
        print('method: start_recording')
        if hasattr(self, 'audioInputStream') and self.audioInputStream.active:
            print('starting to  recording =============================================')
            self.isRecording = True

    def stop_recording(self):
        print('method: stop_recording')
        self.isRecording = False
        # if hasattr(self, 'stream') and self.stream.active:
        #     self.stream.stop_stream()
        #     self.stream.close()
    def flush_recording_buffer(self):
        print('method: flush_recording_buffer')
        self.stop_recording()
        self.recording_audio_buffer = []
        # if hasattr(self, 'stream') and self.stream.active:
        #     self.stream.stop_stream()
        #     self.stream.close()

    def save_audio_button(self):
        self.save_audio()

    def play_audio_button(self):
        self.play_audio()

    def save_audio(self):
        print('method: save_audio')
        if len(self.recording_audio_buffer) == 0:
            print("No audio to save.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
            wav_filename = tmpfile.name

        with wave.open(wav_filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(np.array(self.recording_audio_buffer).astype(np.int16).tobytes())

        print("Audio saved to:", wav_filename)

    def play_audio(self):
        print('method: play_audio')
        self.play_audio_from_RecordedBuffer()

    def play_audio_from_RecordedBuffer(self):
        print('method: play_audio_from_RecordedBuffer')
        self.play_audio_from_buffer(self.recording_audio_buffer)
    def play_audio_from_LifeBuffer(self):
        print('method: play_audio_from_LifeBuffer')
        self.play_audio_from_buffer(self.audio_buffer)

    def play_audio_from_buffer(self, buffer):
        print('method: play_audio_from_buffer')
        playback_device_id = self.get_selected_speaker_index()

        if playback_device_id is None:
            print("Please select a playback device.")
            return

        if not buffer:
            print("No audio to play.")
            return

        audio_data = np.array(buffer).flatten()

        playback_device_info = sd.query_devices(device=playback_device_id, kind='output')
        print(playback_device_info)

        num_output_channels = playback_device_info.get('max_output_channels', 1)
        if num_output_channels > 0:
            audio_data = audio_data.reshape(-1, num_output_channels)

            sd.play(audio_data, samplerate=self.SAMPLE_RATE, device=playback_device_id)
            sd.wait()
        else:
            print("num_output_channels for selected audio output device is 0")

    def start_audio_thread(self):
        print('method: start_audio_thread')
        self.audio_thread = threading.Thread(target=self.start_audio_stream)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def start_audio_stream(self, selectedDeviceId=None):
        print('method: start_audio_stream')
        istream = self.getSDInputStream()
        if istream:
            istream.start()
        else:
            if not selectedDeviceId:
                self.audioInputStream = sd.InputStream(callback=self.plot_spectrum, channels=1, samplerate=self.SAMPLE_RATE)
            else:
                self.audioInputStream = sd.InputStream(device=selectedDeviceId, callback=self.plot_spectrum, channels=1, samplerate=self.SAMPLE_RATE)
            with self.audioInputStream:
                self.isListening = True
                # while True:
                while self.isListening:
                    self.adjust_listeningButtonLabel()
                    sd.sleep(100)

    def getSDInputStream(self):
        print('method: getSDInputStream')
        if hasattr(self, 'audioInputStream'):
            if self.audioInputStream:
                if self.audioInputStream.active:
                    return self.audioInputStream
                else:
                    return self.audioInputStream
        return None

def run_gui():
    root = tk.Tk()
    app = SpectrumAnalyzerApp(root)
    app.start_audio_thread()
    root.mainloop()

if __name__ == "__main__":
    run_gui()
