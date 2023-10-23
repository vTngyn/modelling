import tkinter as tk
import pprint
import time
from vtnLibs.AudioDeviceUtils import EmbeddedAudioSelector
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from typing import Protocol, List, Callable


EVENT_COMBOBOX_SELECTED = r'<<ComboboxSelected>>'
EVENT_LISTBOX_SELECTED = r'<<ListboxSelect>>'

EVENT_DELETE_WINDOW = "WM_DELETE_WINDOW"

BTN_LABEL_QUIT = "Quit"
BTN_LABEL_REFRESH = "Refresh"
BTN_LABEL_SELECT_AUDIO_OUT_DEVICE = "Select Speaker Device:"
FIELD_LABEL_SELECT_AUDIO_IN_DEVICE = "Select Mic. Device:"
MSG_TEXT_WINDOWS_SIZE = "Windows size:"


IDX_LABEL_SPLIT_CHARS = "#"
WINDOW_TITLE = "Select Audio Player/Recorder"
WINDOW_HEIGHT = 300
WINDOW_WIDTH = 250
WINDOW_GEOMETRY = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"


class AudioSelectionPresenter(Protocol):
    def refresh_audio_device_labels(self):
        ...

    def get_selected_audio_out_device_label(self):
        ...
    def get_audio_out_device_labels(self):
        ...
    def handle_selected_out_device_by_user(self, *args, **kwargs):
        ...

    def get_selected_audio_in_device_label(self):
        ...

    def get_audio_in_device_labels(self):
        ...

    def handle_selected_in_device_by_user(self, *args, **kwargs):
        ...

    def reinitialize_audio_selector_module(self):
        ...
    def event_on_GUI_close(self):
        ...
    def update_audio_out_dropdown_elements(self, *args):
        ...
    def update_audio_in_dropdown_elements(self, *args):
        ...
    def handle_event_on_close(self):
        ...
    def handle_event_refresh_audio_devices(self):
        ...

class AudioSelectionView(LEC):


    def __init__(self, root, audio_selector: EmbeddedAudioSelector):
        self.root = root
        self.presenter = None
        # self.audio_selector = audio_selector

    def checkOutValue(self, *values):
        print(f"onselection:")
        print(values)
        """ resultat:
        onselection:
        ('PY_VAR0', '', 'w')
        """
    def on_select(self, val):
        print(f"onselection:{val}")
    def on_select2(self, event):
        selected_item = event.widget.get(event.widget.curselection())
        print(f"onselection:{selected_item}")
    def __initialize_module__(self):

        self.root.geometry(WINDOW_GEOMETRY)
        self.root.title(WINDOW_TITLE)
        self.root.protocol(EVENT_DELETE_WINDOW, self.event_on_close)

        # Refresh button
        self.refresh_button = tk.Button(self.root, text=BTN_LABEL_REFRESH, command=self.presenter.handle_event_refresh_audio_devices)
        self.refresh_button.pack(pady=10)
        # Quit button
        self.quit_button = tk.Button(self.root, text=BTN_LABEL_QUIT, command=self.presenter.handle_event_on_close)
        self.quit_button.pack(pady=10)


        self.speaker_device_label = tk.Label(self.root, text=BTN_LABEL_SELECT_AUDIO_OUT_DEVICE)
        self.speaker_device_label.pack()

        self.selected_audio_output_device_dropdown_label = tk.StringVar(value=None)
        # self.selected_audio_output_device_dropdown_label.trace('w', self.checkOutValue)   #it works!
        self.selected_audio_output_device_dropdown_label.trace('w', self.presenter.handle_selected_out_device_by_user)

        empty_dropdown_label = tk.StringVar(value=None)
        empty_audio_device_labels: List[str] = []
        # self.audio_output_device_dropdown = tk.OptionMenu(self.root, variable=self.selected_audio_output_device_dropdown_label, value=empty_dropdown_label, *empty_audio_device_labels)
        self.audio_output_device_dropdown = tk.OptionMenu(self.root, variable=self.selected_audio_output_device_dropdown_label, value=empty_dropdown_label, *empty_audio_device_labels, command=lambda event: self.presenter.handle_selected_out_device_by_user(selected=self.selected_audio_output_device_dropdown_label.get()))
        # self.audio_output_device_dropdown = tk.OptionMenu(self.root, variable=self.selected_audio_output_device_dropdown_label, value=empty_dropdown_label, *empty_audio_device_labels, command=lambda event: self.on_select("value"))
        # self.audio_output_device_dropdown.bind(EVENT_LISTBOX_SELECTED, self.on_select2)
        self.audio_output_device_dropdown.bind(EVENT_COMBOBOX_SELECTED, self.presenter.handle_selected_out_device_by_user)
        self.audio_output_device_dropdown.bind(EVENT_LISTBOX_SELECTED, self.presenter.handle_selected_out_device_by_user)
        self.audio_output_device_dropdown.pack()
        # self.selected_audio_output_device_dropdown_label.trace('w', self.event_speaker_selected_by_user)

        self.presenter.update_audio_out_dropdown_elements()

        # Get a list of available audio output devices
        # self.output_audio_devices = sd.query_devices(kind='output')
        # self.output_audio_devices = [device['name'] for device in self.audio_devices if device['max_output_channels'] > 0]
        # Filter out non-output audio devices

        # self.output_audio_device_labels=self.audio_selector.get_speaker_model_labels()
        # self.input_audio_device_labels=self.audio_selector.get_mic_model_labels()
        #
        # output_idx=self.audio_selector.get_label_list_index_of_selected_speaker_device() or 0
        # if not self.audio_selector.output_device_index and not self.audio_selector.get_speaker_model_list() and len(self.audio_selector.get_speaker_model_list())>0:
        #     self.audio_selector.set_selected_speaker_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())
        #
        # input_idx=self.audio_selector.get_label_list_index_of_selected_mic_device() or 0
        # if not self.audio_selector.input_device_index and not self.audio_selector.get_mic_model_list() and len(self.audio_selector.get_mic_model_list())>0:
        #     self.audio_selector.set_selected_mic_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())



        # self.selected_audio_output_device = tk.StringVar(value=self.output_audio_device_labels[output_idx])
        # self.selected_audio_output_device_dropdown_label = tk.StringVar(value=self.presenter.get_selected_audio_out_device_label())
        #
        # self.audio_output_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_output_device_dropdown_label, *self.presenter.get_audio_out_device_labels())
        # self.audio_output_device_dropdown.bind(EVENT_COMBOBOX_SELECTED, self.event_speaker_selected_by_user)
        # self.audio_output_device_dropdown.pack()
        # self.selected_audio_output_device_dropdown_label.trace('w', self.event_speaker_selected_by_user)

        self.mic_device_label = tk.Label(self.root, text=FIELD_LABEL_SELECT_AUDIO_IN_DEVICE)
        self.mic_device_label.pack()

        self.selected_audio_input_device_dropdown_label = tk.StringVar(value=None)


        # self.audio_input_device_dropdown = tk.OptionMenu(self.root, variable=self.selected_audio_input_device_dropdown_label, value=empty_dropdown_label, *empty_audio_device_labels)
        self.audio_input_device_dropdown = tk.OptionMenu(self.root, variable=self.selected_audio_input_device_dropdown_label, value=empty_dropdown_label, *empty_audio_device_labels, command=lambda event: self.presenter.handle_selected_in_device_by_user(selected=self.selected_audio_input_device_dropdown_label.get()))

        # self.audio_input_device_dropdown.bind(EVENT_COMBOBOX_SELECTED, self.event_speaker_selected_by_user)
        self.audio_input_device_dropdown.bind(EVENT_COMBOBOX_SELECTED, self.presenter.handle_selected_in_device_by_user)
        self.audio_input_device_dropdown.bind(EVENT_LISTBOX_SELECTED, self.presenter.handle_selected_in_device_by_user)
        self.audio_input_device_dropdown.pack()

        self.presenter.update_audio_in_dropdown_elements()


        # input_audio_device_labels = self.presenter.get_audio_out_device_labels()
        # self.selected_audio_input_device_dropdown_label = None
        # if not input_audio_device_labels and len(input_audio_device_labels)>0:
        #     # self.selected_audio_input_device_dropdown_value = tk.StringVar(value=self.input_audio_device_labels[input_idx])
        #     self.selected_audio_input_device_dropdown_label = tk.StringVar(value=self.presenter.get_selected_audio_in_device_label())
        #     # self.audio_input_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_input_device_dropdown_value, *self.input_audio_device_labels)
        #     self.audio_input_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_input_device_dropdown_label, *self.presenter.get_selected_audio_in_device_label())
        #     self.audio_input_device_dropdown.bind(EVENT_COMBOBOX_SELECTED, self.event_mic_selected_by_user)
        #     self.audio_input_device_dropdown.pack()
        #     self.selected_audio_input_device_dropdown_label.trace('w', self.event_speaker_selected_by_user)
        # else:
        #     self.selected_audio_input_device_dropdown_label = tk.StringVar(value="")
        #     self.audio_input_device_dropdown = tk.OptionMenu(self.root, self.selected_audio_input_device_dropdown_label,
        #                                                      [])



        # Create a label to display the window size
        #self.window_size_label = tk.Label(self.root, text=f"Window size: {self.get_window_size()}")
        # self.window_size_label.pack()

        # self.extract_audio_sgement()

    def __update_option_menu__(self, selected_option_widget, dropdown_option_widget, new_selected_value, new_options, callback: Callable):
        # Clear the existing options
        dropdown_option_widget['menu'].delete(0, 'end')

        # Add the new options
        if new_options:
            for item in new_options:
                # dropdown_option_widget['menu'].add_command(label=option, command=tk._setit(selected_option_widget, option))
                dropdown_option_widget['menu'].add_command(label=item, command=lambda option=item: selected_option_widget.set(option))

            # Set the new selected value
        if new_selected_value:
            selected_option_widget.set(new_selected_value)
        dropdown_option_widget.bind(EVENT_COMBOBOX_SELECTED, callback)
        dropdown_option_widget.bind(EVENT_LISTBOX_SELECTED, callback)
        dropdown_option_widget.pack()

    def update_audio_out_dropdown_elements(self, audio_device_labels: List[str], selected_audio_device_dropdown_value:str):
        print("update_audio_out_dropdown_elements")
        # input_audio_device_labels = self.presenter.get_audio_out_device_labels()

        self.__update_option_menu__(self.selected_audio_output_device_dropdown_label, self.audio_output_device_dropdown, selected_audio_device_dropdown_value, audio_device_labels, callback=self.presenter.handle_selected_out_device_by_user)

    def update_audio_in_dropdown_elements(self, audio_device_labels: List[str], selected_audio_device_dropdown_value:str):
        print("update_audio_in_dropdown_elements")
        # input_audio_device_labels = self.presenter.get_audio_out_device_labels()
        self.__update_option_menu__(self.selected_audio_input_device_dropdown_label, self.audio_input_device_dropdown, selected_audio_device_dropdown_value, audio_device_labels, callback=self.presenter.handle_selected_in_device_by_user)


    def reinitialize_audio_selection(self):
        self.__initialize_module__()

    def event_speaker_selected_by_user(self, *args):
        print("speaker_selected_by_user")
        selected_output_device = self.selected_audio_output_device_dropdown_label.get()
        self.presenter.handle_selected_out_device_by_user(selected_output_device)

    def event_mic_selected_by_user(self, *args):
        print("mic_selected_by_user")
        selected_input_device = self.selected_audio_input_device_dropdown_label.get()
        self.presenter.handle_selected_in_device_by_user(selected_input_device)

    def get_window_size(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        return f"{width:5f} x {height:5f}"

    def event_on_resize(self, event):
        self.window_size_label.config(text=f"{MSG_TEXT_WINDOWS_SIZE}: {event.width}x{event.height}")


    def event_destroy_widget_from_myroot(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def event_refresh_audio_devices(self):
        self.event_destroy_widget_from_myroot()
        self.__initialize_module__()

    def event_on_close(self):
        # Call the provided callback function when the GUI is closed
        self.root.destroy()


    @property
    def user_selected_audio_out_device(self):
        return self.selected_audio_output_device_dropdown_label.get()
    @property
    def user_selected_audio_in_device(self):
        return self.selected_audio_input_device_dropdown_label.get()


    def update_audio_gui(self):
        print(f"update_audio_gui : {time.ctime()}")
        # self.root.after(1000, self.update_audio_gui)
        while True:
            time.sleep(1)
        # self.run()

    def run(self, presenter:AudioSelectionPresenter):
        # self.root.mainloop()
        # while True:
        #     time.sleep(1)
        self.presenter = presenter
        self.__initialize_module__()

