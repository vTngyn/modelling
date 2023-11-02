from vtnLibs.AudioDeviceUtils import EmbeddedAudioSelector, DeviceLabelModel
from typing import List

class AudioSelectionModel:
    def __init__(self, audio_selector: EmbeddedAudioSelector):
        self.audio_selector = audio_selector
        self.input_audio_device_labels: List[DeviceLabelModel] = []
        self.output_audio_device_labels: List[DeviceLabelModel] = []

        self.initialize_models()


    def initialize_models(self):
        self.output_audio_device_labels=self.audio_selector.get_speaker_model_labels()
        self.input_audio_device_labels=self.audio_selector.get_mic_model_labels()

    def refresh_audio_device_labels(self):
        # self.audio_segment = None
        self.audio_selector.__
        self.initialize_models()
        # output_idx=self.audio_selector.get_label_list_index_of_selected_speaker_device() or 0
        if not self.audio_selector.output_device_index and not self.audio_selector.get_speaker_model_list() and len(self.audio_selector.get_speaker_model_list())>0:
            self.audio_selector.set_selected_speaker_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())

        # input_idx=self.audio_selector.get_label_list_index_of_selected_mic_device() or 0
        if not self.audio_selector.input_device_index and not self.audio_selector.get_mic_model_list() and len(self.audio_selector.get_mic_model_list())>0:
            self.audio_selector.set_selected_mic_device_by_user(self.audio_selector.get_speaker_model_list()[0].get_device_idx())

