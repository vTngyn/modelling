import tkinter as tk
# from tkinter import filedialog
# from tkinter import ttk
import sounddevice as sd  # Import sounddevice for audio device management
from vtnLibs.AudioUtils import AudioUtils as AudioU
import pprint
import time
from common_classes import SegmentData


class AudioSegmentPlayerGUI:

    IDX_LABEL_SPLIT_CHARS="#"
    def __init__(self, root, segment_data: SegmentData, on_gui_close):
        self.segment_data = segment_data
        self.audio_segment = None
        self.on_gui_close = on_gui_close

        self.root = root
        self.root.title("Audio Player")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Bind the resizing event to the on_resize callback
        self.root.bind("<Configure>", self.on_resize)

        self.play_button = tk.Button(self.root, text="Play", command=self.play_audio)
        self.play_button.pack()

        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_audio)
        self.pause_button.pack()

        self.device_label = tk.Label(self.root, text="Select Audio Device:")
        self.device_label.pack()

        # Create a label to display the window size
        self.window_size_label = tk.Label(root, text="Window size: ")
        self.window_size_label.pack()

        # Get a list of available audio output devices
        # self.output_audio_devices = sd.query_devices(kind='output')
        # self.output_audio_devices = [device['name'] for device in self.audio_devices if device['max_output_channels'] > 0]
        # Filter out non-output audio devices
        self.audio_devices = sd.query_devices()
        print("device from query_devices()")
        pprint.pprint(self.audio_devices, width=20, indent=4)

        print("device list")
        self.output_audio_devices=[]
        for i, device in enumerate(self.audio_devices):
            print(f"i={i}")
            print(device)
            if device['max_output_channels'] > 0:
                self.output_audio_devices.append(device)
        pprint.pprint(self.output_audio_devices)

        self.output_audio_device_names = [self.get_unique_label_from_audio_device(device) for device in self.output_audio_devices]
        self.selected_audio_output_device = tk.StringVar(value=self.output_audio_device_names[0])  # Default to the first device

        self.audio_output_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_output_device, *self.output_audio_device_names)
        self.audio_output_device_dropdown.pack()

        self.extract_audio_sgement()


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

    def play_audio(self):
        print(self.selected_audio_output_device.get())
        tmp0=self.selected_audio_output_device.get()
        tmpIdx = self.get_audio_device_idx_from_unique_label(tmp0)
        tmpName = self.get_audio_device_name_from_unique_label(tmp0)
        # selected_device_index = self.output_audio_device_names.index(int(tmp))
        # tomp1=self.output_audio_devices[selected_device_index]
        # selected_device_id = tmp1['id']

        selected_device_id = int(tmpIdx)

        AudioU.play_audio_segment(self.audio_segment, device_id=selected_device_id)
        # Replace this with the logic to play the audio segment
        # You'll need to use appropriate audio playback libraries for your specific use case
        # Example: Play audio using a library like PyAudio or other suitable audio playback library
        time.sleep(5)  # Simulating audio playback

    def pause_audio(self):
        print("Pausing audio...")
        # Replace this with the logic to pause the audio segment
        pass

    def on_close(self):
        # Call the provided callback function when the GUI is closed
        if self.on_gui_close:
            self.on_gui_close()
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

