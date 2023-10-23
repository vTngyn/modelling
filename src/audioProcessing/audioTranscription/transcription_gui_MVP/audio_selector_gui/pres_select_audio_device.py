from typing import Protocol, List, Callable
from src.audioProcessing.audioTranscription.transcription_gui_MVP.audio_selector_gui.model_select_audio_device import AudioSelectionModel
from vtnLibs.AudioDeviceUtils import DeviceLabelModel


class AudioSelectionView(Protocol):
    def update_audio_out_dropdown_elements(self, output_audio_device_labels: List[str], selected_audio_output_device_dropdown_value:str):
        ...

    def update_audio_in_dropdown_elements(self, input_audio_device_labels: List[str], selected_audio_input_device_dropdown_value:str):
        ...

    def event_on_close(self):
        ...

    def event_refresh_audio_devices(self):
        ...
    @property
    def user_selected_audio_out_device(self):
        ...

    @property
    def user_selected_audio_in_device(self):
        ...

class AudioSelectionPresenter():
    def __init__(self,model: AudioSelectionModel, view:AudioSelectionView, on_gui_close_callback: Callable):
        self.model:AudioSelectionModel = model
        self.view: AudioSelectionView=view
        self.on_gui_close_callback = on_gui_close_callback


    def get_selected_audio_out_device_label(self):
        # return self.model.output_audio_device_labels[self.get_selected_audio_out_device_label_idx()]
        idx = self.get_selected_audio_out_device_label_idx()
        if idx:
            dev_label = self.model.output_audio_device_labels[idx]
            if dev_label:
                return dev_label
        return None

    def get_selected_audio_out_device_label_idx(self):
        output_idx = self.model.audio_selector.get_label_list_index_of_selected_speaker_device()
        # output_idx = self.model.audio_selector.get_label_list_index_of_selected_speaker_device() or 0
        return output_idx

    def get_selected_audio_in_device_label(self):
        idx=self.get_selected_audio_in_device_label_idx()
        if idx:
            dev_label = self.model.input_audio_device_labels[idx]
            if dev_label:
                return dev_label
        return None
    def get_selected_audio_in_device_label_idx(self):
        # output_idx = self.model.audio_selector.get_label_list_index_of_selected_mic_device() or 0
        output_idx = self.model.audio_selector.get_label_list_index_of_selected_mic_device()
        return output_idx

    def get_audio_out_device_labels(self):
        return self.model.output_audio_device_labels

    def get_audio_in_device_labels(self):
        return self.model.input_audio_device_labels

    def  refresh_audio_device_labels(self):
        return self.model.refresh_audio_device_labels()

    # def handle_selected_in_device_by_user(self, in_device_label: str, refresh_options_widget: bool =False):
    def handle_selected_in_device_by_user(self, *args, **kwargs):
        print("handle_selected_in_device_by_user")
        in_device_label = self.view.user_selected_audio_in_device
        refresh_options_widget: bool = False

        if in_device_label:
            device_idx, device_name = DeviceLabelModel.get_device_idx_name_from_label(in_device_label)
            print(f"device_idx={device_idx}")
            self.model.audio_selector.set_selected_mic_device_by_user(device_idx)
            # self.selected_audio_input_device = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: in={in_device_label}")
        if refresh_options_widget:
            self.view.update_audio_in_dropdown_elements(audio_device_labels=self.get_audio_in_device_labels(), selected_audio_device_dropdown_value=self.get_selected_audio_in_device_label())

    def handle_selected_out_device_by_user(self, *args, **kwargs):
    # def handle_selected_out_device_by_user(self, out_device_label:str, refresh_options_widget: bool =False):
        print("handle_selected_out_device_by_user")
        out_device_label = self.view.user_selected_audio_out_device
        refresh_options_widget: bool = False
        if out_device_label:
            device_idx, device_name = DeviceLabelModel.get_device_idx_name_from_label(out_device_label)
            print(f"device_idx={device_idx}")
            self.model.audio_selector.set_selected_speaker_device_by_user(device_idx)
            # self.selected_audio_output_device_model = self.audio_selector.get_selected_speaker_device_model_by_user()
        print(f"selected devices: out={out_device_label}")
        if refresh_options_widget:
            self.view.update_audio_in_dropdown_elements(audio_device_labels=self.get_audio_out_device_labels(), selected_audio_evice_dropdown_value=self.get_selected_audio_out_device_label())

    def update_audio_out_dropdown_elements(self, *args):
        print("update_audio_out_dropdown_elements")
        print("update_audio_in_dropdown_elements")
        label = self.get_selected_audio_out_device_label()
        print(label)
        if not label:
            label=""
        labels = self.get_audio_out_device_labels()
        print(labels)
        if len(labels)==0:
            labels=None
        self.view.update_audio_out_dropdown_elements(selected_audio_device_dropdown_value=label,
                                                audio_device_labels=labels)

    def update_audio_in_dropdown_elements(self, *args):
        print("update_audio_in_dropdown_elements")
        label = self.get_selected_audio_in_device_label()
        print(label)
        if not label:
            label=""
        labels = self.get_audio_in_device_labels()
        print(labels)
        if len(labels)==0:
            labels=None
        self.view.update_audio_in_dropdown_elements(selected_audio_device_dropdown_value=label,
                                               audio_device_labels=labels)

    def handle_event_on_close(self):
        # Call the provided callback function when the GUI is closed
        if self.on_gui_close_callback:
            print(f'output_device={self.view.user_selected_audio_out_device}, input_device={self.view.user_selected_audio_in_device}')
            self.on_gui_close_callback(output_device=self.view.user_selected_audio_out_device, input_device=self.view.user_selected_audio_in_device)
        self.view.event_on_close()

    def reinitialize_audio_selector_module(self):
        self.model.audio_selector.reinitialize_module()

    def handle_event_refresh_audio_devices(self):
        self.reinitialize_audio_selector_module()
        self.view.event_refresh_audio_devices()

    def run(self):
        self.view.run(self)
