import tkinter as tk
# from tkinter import filedialog
# from tkinter import ttk
import sounddevice as sd  # Import sounddevice for audio device management
from vtnLibs.AudioUtils import AudioUtils as AudioU
import pprint
import time
from common_classes import SegmentData
from vtnLibs.AudioDeviceUtils import EmbeddedAudioSelector
from vtnLibs.AudioDeviceUtils import DeviceLabelModel
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC

class AudioSelectionGUI(LEC):

    IDX_LABEL_SPLIT_CHARS="#"
    def __init__(self, root, on_gui_close, audio_selector: EmbeddedAudioSelector):
        self.on_gui_close = on_gui_close
        self.root = root
        self.audio_selector = audio_selector
        self.__initialize_module__()

    def __initialize_module__(self):
        # self.audio_segment = None

        self.mic_device_models: [DeviceLabelModel]  = None
        self.speaker_device_models: [DeviceLabelModel] = None
        self.input_audio_device_labels = None
        self.output_audio_device_labels = None

        self.root.geometry("300x250")
        self.root.title("Select Audio Player/Recorder")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.device_label = tk.Label(self.root, text="Select Audio Device:")
        self.device_label.pack()




        # Get a list of available audio output devices
        # self.output_audio_devices = sd.query_devices(kind='output')
        # self.output_audio_devices = [device['name'] for device in self.audio_devices if device['max_output_channels'] > 0]
        # Filter out non-output audio devices

        self.output_audio_device_labels=self.audio_selector.get_speaker_model_labels()
        self.input_audio_device_labels=self.audio_selector.get_mic_model_labels()

        output_idx=self.audio_selector.get_label_list_index_of_selected_speaker_device() or 0
        if not self.audio_selector.output_device_index and not self.audio_selector.get_speaker_model_list() and len(self.audio_selector.get_speaker_model_list())>0:
            self.audio_selector.set_selected_speaker_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())

        input_idx=self.audio_selector.get_label_list_index_of_selected_mic_device() or 0
        if not self.audio_selector.input_device_index and not self.audio_selector.get_mic_model_list() and len(self.audio_selector.get_mic_model_list())>0:
            self.audio_selector.set_selected_mic_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())


        self.selected_audio_output_device = tk.StringVar(value=self.output_audio_device_labels[output_idx])

        self.audio_output_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_output_device, *self.output_audio_device_labels)
        self.audio_output_device_dropdown.bind('<<ComboboxSelected>>', self.speaker_selected_by_user)
        self.audio_output_device_dropdown.pack()
        self.selected_audio_output_device.trace('w', self.speaker_selected_by_user)

        self.mic_device_label = tk.Label(self.root, text="Select Mic. Device:")
        self.mic_device_label.pack()
        if not self.input_audio_device_labels and len(self.input_audio_device_labels)>0:
            self.selected_audio_input_device = tk.StringVar(value=self.input_audio_device_labels[input_idx])
            self.audio_input_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_input_device,
                                                             *self.input_audio_device_labels)
            self.audio_input_device_dropdown.bind('<<ComboboxSelected>>', self.mic_selected_by_user)
            self.audio_input_device_dropdown.pack()
            self.selected_audio_input_device.trace('w', self.speaker_selected_by_user)
        else:
            self.selected_audio_input_device = tk.StringVar(value="")
            self.audio_input_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_input_device,
                                                             [])


        # Quit button
        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_audio_devices)
        self.refresh_button.pack(pady=10)
        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.on_close)
        self.quit_button.pack(pady=10)

        # Create a label to display the window size
        #self.window_size_label = tk.Label(self.root, text=f"Window size: {self.get_window_size()}")
        # self.window_size_label.pack()

        # self.extract_audio_sgement()

    def reinitialize_audio_selection(self):
        self.__initialize_module__()

    def speaker_selected_by_user(self, *args):
        print("speaker_selected_by_user")
        selected_device = self.selected_audio_output_device.get()
        if selected_device:
            device_idx, device_name = DeviceLabelModel.get_device_idx_name_from_label(selected_device)
            print(f"device_idx={device_idx}")
            self.audio_selector.set_selected_speaker_device_by_user(device_idx)
            # self.selected_audio_output_device_model = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: out={selected_device}")

    def mic_selected_by_user(self, *args):
        print("mic_selected_by_user")
        selected_device = self.selected_audio_input_device.get()
        if selected_device:
            device_idx, device_name = DeviceLabelModel.get_device_idx_name_from_label(selected_device)
            print(f"device_idx={device_idx}")
            self.audio_selector.set_selected_mic_device_by_user(device_idx)
            # self.selected_audio_input_device = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: out={selected_device}")

    def get_window_size(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        return f"{width:5f} x {height:5f}"

    def __preparation_for_speaker_dropdown__(self):

        # self.audio_devices = sd.query_devices()
        self.speaker_device_models = self.audio_selector.get_speaker_model_list()

        pprint.pprint(self.speaker_device_models, width=20, indent=4)
        self.output_audio_device_labels=[]
        for i, device_model in enumerate(self.speaker_device_models):
            device_label = device_model.get_device_label()
            print(f"i={i} : {device_label}")
            self.output_audio_device_labels.append(device_label)
        pprint.pprint(self.output_audio_device_labels)

    def __preparation_for_mic_dropdown__(self):

        self.mic_device_models = self.audio_selector.get_mic_model_list()

        pprint.pprint(self.mic_device_models, width=20, indent=4)
        self.input_audio_device_labels=[]
        for i, device_model in enumerate(self.mic_device_models):
            device_label = device_model.get_device_label()
            print(f"i={i} : {device_label}")
            self.input_audio_device_labels.append(device_label)
        pprint.pprint(self.input_audio_device_labels)

    def on_resize(self, event):
        self.window_size_label.config(text=f"Window size: {event.width}x{event.height}")

    # def extract_audio_sgement(self):
    #     self.audio_segment = AudioU.extract_audio_segment(self.segment_data.audio_file, self.segment_data.start_timestamp, self.segment_data.end_timestamp)

    # def play_audio(self):
    #     print(self.selected_audio_output_device.get())
    #     device_model_label=self.selected_audio_output_device.get()
    #     tmpIdx, tmpName = DeviceLabelModel.get_device_idx_name_from_label(device_model_label)
    #     # selected_device_index = self.output_audio_device_names.index(int(tmp))
    #     # tomp1=self.output_audio_devices[selected_device_index]
    #     # selected_device_id = tmp1['id']
    #
    #     selected_device_id = int(tmpIdx)
    #
    #     AudioU.play_audio_segment(self.audio_segment, device_id=selected_device_id)
    #     # Replace this with the logic to play the audio segment
    #     # You'll need to use appropriate audio playback libraries for your specific use case
    #     # Example: Play audio using a library like PyAudio or other suitable audio playback library
    #     time.sleep(5)  # Simulating audio playback
    #
    # def pause_audio(self):
    #     print("Pausing audio...")
    #     # Replace this with the logic to pause the audio segment
    #     pass

    def destroy_widget_from_myroot(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def refresh_audio_devices(self):
        self.audio_selector.reinitialize_module()
        self.destroy_widget_from_myroot()
        self.__initialize_module__()

    def on_close(self):
        # Call the provided callback function when the GUI is closed
        print(f"selected devices: out={self.selected_audio_output_device}, in={self.selected_audio_input_device}")
        if self.on_gui_close:
            self.on_gui_close(output_device=self.selected_audio_output_device, input_device=self.selected_audio_input_device)
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

