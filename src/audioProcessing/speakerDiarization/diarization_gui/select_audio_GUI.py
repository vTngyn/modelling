import tkinter as tk
# from tkinter import filedialog
# from tkinter import ttk
import sounddevice as sd  # Import sounddevice for audio device management
from vtnLibs.AudioUtils import AudioUtils as AudioU
import pprint
import time
from common_classes import SegmentData
from vtnLibs.AudioDeviceUtils import EmbeddedAudioSelector
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC

class AudioSegmentPlayerGUI(LEC):

    IDX_LABEL_SPLIT_CHARS="#"
    def __init__(self, root, on_gui_close):
        self.on_gui_close = on_gui_close
        self.audio_selector = EmbeddedAudioSelector()
        self.audio_selector.__initialize_audio_devices__()

        self.root = root
        self.initialize_gui_layout()

        selected_device_idx_of_list = 0
        self.output_audio_devices=[]
        if (self.audio_selector):
            print("device list")
            for i, device_model in enumerate(self.audio_selector.speaker_device_models):
                print(f"i={i}")
                print(device_model)
                device=device_model.device
                # if device_model.device['max_output_channels'] > 0:
                self.output_audio_devices.append(device)
                if (self.audio_selector.speaker_device_index==device_model.get_device_idx()):
                    selected_device_idx_of_list=i

            pprint.pprint(self.output_audio_devices)
            print(f"selected_device_idx_of_list={selected_device_idx_of_list}")

        self.output_audio_device_names = [self.get_unique_label_from_audio_device(device) for device in self.output_audio_devices]
        self.selected_audio_output_device = tk.StringVar(value=self.output_audio_device_names[selected_device_idx_of_list])

        self.audio_output_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_output_device, *self.output_audio_device_names)
        self.audio_output_device_dropdown.pack()

        self.extract_audio_sgement()

    def initialize_gui_layout(self):
        self.root.title("Select Audio Device")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)
        # Bind the resizing event to the on_resize callback
        self.root.bind("<Configure>", self.on_resize)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.on_close)
        self.quit_button.pack(pady=10)

        self.select_speaker_button = tk.Button(self.root, text="Select speaker", command=self.select_speaker)
        self.select_speaker_button.pack()

        self.select_mic_button = tk.Button(self.root, text="Select microphone", command=self.select_mic)
        self.select_mic_button.pack()

        self.device_label = tk.Label(self.root, text="Select Audio Device:")
        self.device_label.pack()

        # Create a label to display the window size
        self.window_size_label = tk.Label(self.root, text="Window size: ")
        self.window_size_label.pack()


    def get_unique_label_from_audio_device(self, device) -> str:
        return f"{device['index']}{AudioSegmentPlayerGUI.IDX_LABEL_SPLIT_CHARS}{device['name']}"
    def get_audio_device_idx_from_unique_label(self, device_unique_label:str):
        return device_unique_label.split(AudioSegmentPlayerGUI.IDX_LABEL_SPLIT_CHARS)[0]
    def get_audio_device_name_from_unique_label(self, device_unique_label:str):
        return device_unique_label.split(AudioSegmentPlayerGUI.IDX_LABEL_SPLIT_CHARS)[1]
    def on_resize(self, event):
        self.window_size_label.config(text=f"Window size: {event.width}x{event.height}")

    def extract_audio_sgement(self):
        self.audio_segment = AudioU.extract_audio_segment(self.segment_data.audio_file, self.segment_data.start_timestamp, self.segment_data.end_timestamp)

    def on_close_window(self):
        self.__on_close__()
    def on_close_window(self, event):
        self.__on_close__()
    def on_close(self, **kwargs):
        self.__on_close__()

    def __on_close__(self, **kwargs):
        print("Audio selectio GUI is closing")
        # Call the provided callback function when the GUI is closed
        if self.on_gui_close:
            self.on_gui_close(output_device=self.selected_output_device,input_device=self.selected_input_device,audio_selector=self.audio_selector)
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

