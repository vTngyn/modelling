import tkinter as tk
# from tkinter import filedialog
# from tkinter import ttk
import sounddevice as sd  # Import sounddevice for audio device management
from vtnLibs.AudioUtils import AudioUtils as AudioU
import pprint
import time
from common_classes import SegmentData
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from vtnLibs.AudioDeviceUtils import EmbeddedAudioSelector
from vtnLibs.AudioDeviceUtils import DeviceLabelModel
import numpy as np
import threading

class RT_VAD_DetectionGUI(LEC):


    def __init__(self, root, on_gui_close, audio_selector: EmbeddedAudioSelector):
        self.audio_segment = None
        self.on_gui_close = on_gui_close
        self.playback_position = None

        self.audio_selector=audio_selector

        self.root = root
        self.root.title("Audio Player")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Bind the resizing event to the on_resize callback
        self.root.bind("<Configure>", self.on_resize)
        self.root.geometry("300x250")

        self.play_button = tk.Button(self.root, text="Play", command=self.play_audio)
        self.play_button.pack()

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_audio)
        self.pause_button.pack()

        idx=None
        if (self.audio_selector):
            idx = self.audio_selector.speaker_device_index
        self.device_label = tk.Label(self.root, text=f"Select Audio Device: {idx}")
        self.device_label.pack()

        # Create a label to display the window size
        self.window_size_label = tk.Label(self.root, text="Window size: ")
        self.window_size_label.pack()

        # Get a list of available audio output devices
        # self.output_audio_devices = sd.query_devices(kind='output')
        # self.output_audio_devices = [device['name'] for device in self.audio_devices if device['max_output_channels'] > 0]
        # Filter out non-output audio devices
        # self.audio_devices = self.audio_selector.speaker_device_models

        self.output_audio_device_labels = self.audio_selector.get_speaker_model_labels()
        self.input_audio_device_labels = self.audio_selector.get_mic_model_labels()

        output_idx = self.audio_selector.get_label_list_index_of_selected_speaker_device() or 0

        input_idx = self.audio_selector.get_label_list_index_of_selected_mic_device() or 0

        self.selected_audio_output_device = tk.StringVar(
            value=self.output_audio_device_labels[output_idx])  # Default to the first device

        self.audio_output_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_output_device,
                                                          *self.output_audio_device_labels)
        self.audio_output_device_dropdown.bind('<<ComboboxSelected>>', self.speaker_selected_by_user)
        self.audio_output_device_dropdown.pack()

        self.mic_device_label = tk.Label(self.root, text="Select Mic. Device:")
        self.mic_device_label.pack()

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.on_close)
        self.quit_button.pack(pady=10)

        self.extract_audio_sgement()

    def speaker_selected_by_user(self, event):
        selected_device = self.audio_output_device_dropdown.get()
        if selected_device:
            device_idx = DeviceLabelModel.get_device_idx_name_from_label(selected_device)
            self.audio_selector.set_selected_speaker_device_by_user(device_idx)
            self.selected_audio_output_device = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: out={self.selected_audio_output_device.get_device_name()}")

    def mic_selected_by_user(self, event):
        selected_device = self.audio_input_device_dropdown.get()
        if selected_device:
            device_idx = DeviceLabelModel.get_device_idx_name_from_label(selected_device)
            self.audio_selector.set_selected_mic_device_by_user(device_idx)
            self.selected_audio_input_device = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: out={self.selected_audio_input_device.get_device_name()}")


    def get_unique_label_from_audio_device(self, device) -> str:
        return f"{device['index']}{DeviceLabelModel.DEVICE_LABEL_SEPARATOR}{device['name']}"
    def get_audio_device_idx_from_unique_label(self, device_unique_label:str):
        return device_unique_label.split(DeviceLabelModel.DEVICE_LABEL_SEPARATOR)[0]
    def get_audio_device_name_from_unique_label(self, device_unique_label:str):
        return device_unique_label.split(DeviceLabelModel.DEVICE_LABEL_SEPARATOR)[1]
    def on_resize(self, event):
        #self.window_size_label.config(text=f"Window size: {event.width}x{event.height}")
        None

    def extract_audio_sgement(self):
        self.audio_segment = AudioU.extract_audio_segment(self.selected_segment_info.audio_file, self.selected_segment_info.start_timestamp, self.selected_segment_info.end_timestamp)

    def play_audio(self):
        print(self.selected_audio_output_device.get())
        tmp0=self.selected_audio_output_device.get()
        tmpIdx = self.get_audio_device_idx_from_unique_label(tmp0)
        tmpName = self.get_audio_device_name_from_unique_label(tmp0)
        # selected_device_index = self.output_audio_device_names.index(int(tmp))
        # tomp1=self.output_audio_devices[selected_device_index]
        # selected_device_id = tmp1['id']

        selected_device_id = int(tmpIdx)
        self.audio_selector.set_selected_speaker_device_by_user(selected_device_id)

        AudioU.play_audio_segment(self.audio_segment, device_id=selected_device_id)
        # Replace this with the logic to play the audio segment
        # You'll need to use appropriate audio playback libraries for your specific use case
        # Example: Play audio using a library like PyAudio or other suitable audio playback library
        time.sleep(5)  # Simulating audio playback

    def pause_audio(self):
        print("Pausing audio...")
        # Replace this with the logic to pause the audio segment
        # self.playback_position = sd.get_stream().time_done
        sd.stop()
        pass

    def on_close(self):
        # Call the provided callback function when the GUI is closed
        if self.on_gui_close:
            self.on_gui_close(audio_selector = self.audio_selector)
        self.root.destroy()

    def update_audio_gui(self):
        print(f"update_audio_gui : {time.ctime()}")
        # self.root.after(1000, self.update_audio_gui)
        while True:
            time.sleep(1)
        # self.run()

    def run(self):
        # self.root.mainloop()
        # while True:
        #     time.sleep(1)
        self.update_audio_gui()
        # self.root.after(1000, self.update_audio_gui)

