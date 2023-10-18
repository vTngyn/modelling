import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioRecorderApp:
    def __init__(self, root, samplePerSec=44100, bufferSIze=20, plotLength=30, bitSize=1024):
        self.root = root
        self.root.title("Audio Recorder App")
        self.recording = False
        self.paused = False
        self.bufferSIze=bufferSIze
        self.samplePerSec=samplePerSec
        self.plotLength=plotLength
        self.bitSize=bitSize
        self.audio_data = deque(maxlen=bufferSIze*samplePerSec)  # Max 20 seconds at 44100 samples/sec
        self.spectrogram_data = np.zeros((self.samplePerSec, self.plotLength * self.samplePerSec // self.bitSize))  # Initialize spectrogram data
        # self.spectrogram_times = np.linspace(0, 30, self.spectrogram_data.shape[1])

        self.selected_microphone_device_idx = None
        self.init_gui()

    def addGUIComponentToGrid(self, componentList, currentIndex):
        rowIdx = currentIndex

        for compArray in componentList:
            colIdx=0
            print(f"[{rowIdx},{colIdx}] length:{len(compArray)}")
            for comp in compArray:
                print(type(comp['obj']))
                print((comp['type']))
                comp['obj'].grid(row=rowIdx, column=colIdx, **comp['type'])
                print(f'component [{rowIdx},{colIdx}] initialized')
                colIdx+=1
            rowIdx+=1
        return rowIdx

    def init_gui(self):
        currentRowIndex=0


        self.device_label = ttk.Label(self.root, text="Select Sound Device:")
        #self.device_label.grid(row=currentRowIndex, column=0, padx=10, pady=5, sticky=tk.W)
        self.device_var = tk.StringVar()
        self.device_dropdown = ttk.Combobox(self.root, textvariable=self.device_var, state="readonly")
        #self.device_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)



        self.microphone_label = ttk.Label(self.root, text="Select Microphone Device:")
        #self.microphone_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.microphone_var = tk.StringVar()
        self.microphone_dropdown = ttk.Combobox(self.root, textvariable=self.microphone_var, state="readonly")
        #self.microphone_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Label to display the size of the recorded sound
        self.info_label = ttk.Label(self.root, text="Recorded Sound Size: 0 KB")
        #self.info_label.grid(row=6, column=0, columnspan=2)

        self.start_button = ttk.Button(self.root, text="Start/Resume Recording", command=self.start_recording)
        #self.start_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.record_button = ttk.Button(self.root, text="Start Listening", command=self.toggle_recording)
        #self.record_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.playback_button = ttk.Button(self.root, text="Playback", command=self.playback)
        #self.playback_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Added a playback buffer and index
        self.playback_buffer = np.array([], dtype=np.float32)
        self.playback_buffer_index = 0

        self.alert_label = ttk.Label(self.root, text="Recording Status:", font=("Arial", 12))
        #self.alert_label.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)

        self.alert_light = ttk.Label(self.root, text="pause", background="grey", width=3)
        #self.alert_light.grid(row=5, column=1, pady=5, sticky=tk.W)

        # Added a spectrogram plot
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Frequency (Hz)')
        self.ax.set_title('Spectrogram')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        #self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, pady=10)

        type0={'padx':10, 'pady':5, 'sticky':tk.W}
        type1={'columnspan':2}
        type2={'columnspan':2, 'pady':20}
        type3={'columnspan':2, 'pady':5}
        type4={'pady':5, 'sticky':tk.W}
        type5={'columnspan':2, 'pady':10}

        compList=[
            [{'obj':self.device_label, 'type':type0},{'obj':self.device_dropdown, 'type':type0}],
            [{'obj':self.microphone_label, 'type':type0}, {'obj':self.microphone_dropdown, 'type':type0}],
            [{'obj':self.start_button, 'type':type0}],
            [{'obj':self.record_button, 'type':type2}],
            [{'obj':self.playback_button, 'type':type3}],
            [{'obj':self.alert_label, 'type':type0}, {'obj':self.alert_light, 'type':type4}],
            [{'obj':self.info_label, 'type':type1}],
            [{'obj':self.canvas.get_tk_widget(), 'type':type5}]
        ]
        currentRowIndex=self.addGUIComponentToGrid(compList,currentRowIndex)

        self.populate_device_dropdowns()

    def update_recorded_sound_info(self):
        size_kb = len(self.audio_data) * 2 / self.bitSize  # Assume 16-bit audio, hence 2 bytes per sample
        length_seconds = len(self.audio_data) / self.samplePerSec
        self.info_label.config(text=f"Recorded Sound Info: Size - {size_kb:.2f} KB, Length - {length_seconds:.2f} seconds")

    def populate_device_dropdowns(self):
        devices = sd.query_devices()
        sound_devices = []
        microphone_devices = []

        for idx, device in enumerate(devices):
            device_info = f"{idx}: {device['name']} (USB Port: {device.get('usb_port', 'N/A')})"
            if device['max_output_channels'] > 0:
                sound_devices.append(device_info)
            if device['max_input_channels'] > 0:
                microphone_devices.append(device_info)

        self.device_dropdown['values'] = sound_devices
        self.microphone_dropdown['values'] = microphone_devices


    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
            self.record_button.configure(text="Start Listening")
            if self.paused:
                self.record_button.configure(text="Listening Paused")
            else:
                self.record_button.configure(text="Start Listening")
        else:
            self.start_recording()
            self.record_button.configure(text="Listening")
        self.paused = not self.paused

    def plot_spectrogram(self):
        self.ax.cla()
        extent = [0, len(self.audio_data) / self.samplePerSec, 0, round(self.samplePerSec/2)]  # Adjust the y-axis limit according to your needs
        extent = [0, 1, 0, round(self.samplePerSec/2)]  # Adjust the y-axis limit according to your needs

        self.ax.imshow(self.spectrogram_data, aspect='auto', origin='lower', cmap='viridis', extent=extent)
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Frequency (Hz)')
        self.ax.set_title('Spectrogram')
        self.ax.axvline(x=len(self.audio_data) / self.samplePerSec, color='red', linestyle='--')  # Add a marker for the recorded section
        self.canvas.draw()

    def start_recording(self):
        #selected_microphone_device = self.microphone_var.get()
        selected_microphone_device_idx = self.getSelectedMicrophoneDevice()
        self.recording = True
        self.showRecordingStatus()

        def callback(indata, frames, time, status):
            if status:
                print("Error:", status)
            if self.recording and not self.paused:
                self.showRecordingStatus()
                try:
                    self.audio_data.extend(indata.flatten())

                    # Update the spectrogram data
                    # self.spectrogram_data = np.roll(self.spectrogram_data, -indata.shape[0], axis=1)
                    # self.spectrogram_data[:, -indata.shape[0]:] = np.abs(np.fft.fft(indata, axis=0))[ :self.spectrogram_data.shape[0], :]
                    spec_data = np.abs(np.fft.fft(indata.flatten(), n=self.bitSize))
                    self.spectrogram_data = np.roll(self.spectrogram_data, -1, axis=1)
                    self.spectrogram_data[:, -1] = spec_data

                    # Update the spectrogram plot
                    self.plot_spectrogram()


                    # Update the recorded sound size display
                    self.update_recorded_sound_info()

                except Exception as e:
                    print("Exception in callback:", str(e))

        self.recording = True
        try:
            with sd.InputStream(device=self.getSelectedMicrophoneDevice(), channels=1, callback=callback):
                self.root.mainloop()
        except Exception as e:
            print("Exception in start_recording:", str(e))

    def getSelectedMicrophoneDevice(self):
        self.selected_microphone_device_idx = int(self.microphone_var.get().split(':')[0])

    def showRecordingStatus(self):
        if self.recording:
            if self.paused:
                self.alert_light.configure(background="grey")
            else:
                self.alert_light.configure(background="green")
        else:
            self.alert_light.configure(background="grey")




    def stop_recording(self):
        self.recording = False
        self.showRecordingStatus()

    # def toggle_recording(self):
    #     if self.recording:
    #         self.stop_recording()
    #         self.record_button.configure(text="Start Recording")
    #         self.alert_light.configure(background="grey")
    #     else:
    #         self.start_recording()
    #         self.record_button.configure(text="Stop Recording")
    #         self.alert_light.configure(background="green")
    #

    def playback(self):
        if self.recording:
            self.stop_recording()
            self.paused = True
            self.showRecordingStatus()

        if len(self.audio_data) == 0:
            print("No recorded audio for playback.")
            return

        # Convert deque to numpy array
        audio_array = np.array(self.audio_data)

        # Play the last 20 seconds of recorded audio
        playback_duration = 20  # seconds
        playback_samples = int(playback_duration * self.samplePerSec)
        if len(audio_array) > playback_samples:
            audio_to_play = audio_array[-playback_samples:]
            sd.play(audio_to_play, samplerate=self.samplePerSec)

        self.paused = False  # Resume recording after playback

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root, samplePerSec=44100, bufferSIze=20, plotLength=30, bitSize=1024)
    root.mainloop()
