import pyaudio
import sounddevice as sd
import speech_recognition as sr
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC, configLogOutput
from vtnLibs.AudioUtils import AudioUtils as AudU
from vtnLibs.UserInteractionUtils import UserInputUtils
from enum import Enum
from typing import Tuple
from vtnLibs.DecoratorAndAnnotation import deprecated_class, deprecated_function


class AudioUtils(LEC):

    @staticmethod
    def list_device(messageList="Available microphones:"):
        p = pyaudio.PyAudio()
        devices = AudioUtils.__getDevicesWithSR__()

        # Get available microphones
        # print(messageList)
        for index, name in enumerate(devices):
            device_info = p.get_device_info_by_index(index)
            print(f"{index}: {name} [{device_info['maxInputChannels']}, model': {device_info.get('model_info', '')}]")
            # print(f"{index}: {name} [{device_info}]")

    @staticmethod
    def __getDevicesWithSR__():
        return sr.Microphone.list_microphone_names()
    @staticmethod
    def __refreshSDDevices__():
        sd._terminate()
        sd._initialize()

    @staticmethod
    def __getDevicesWithSD__():
        if sd._initialized != 0:
            AudioUtils.__refreshSDDevices__()
        devices = sd.query_devices()
        print(f"#device={devices}")
        return devices
    @staticmethod
    def choose_device(messagePrompt="Choose a microphone (enter the corresponding index): "):
        AudioUtils.list_device()
        mic_index = int(input(messagePrompt))
        return mic_index

    @staticmethod
    def findSpeakerMicDevices():
        devices = AudioUtils.__getDevicesWithSD__()

        sound_devices = []
        microphone_devices = []

        for idx, device in enumerate(devices):
            if AudioUtils.is_speaker_device_element(device):
                # working_devices.append({"index":idx, "name": name, "device":dev)
                # sound_devices.append(device_info)
                # AudioUtils.__addDeviceElementToList__(sound_devices, device, idx)
                sound_devices.append(device)
            # if device['max_input_channels'] > 0:
            if AudioUtils.is_device_model_microphone(device):
                if AudioUtils.is_device_model_microphone(device):
                    # AudioUtils.__addDeviceElementToList__(microphone_devices, device, idx)
                    #microphone_devices.append(device_info)
                    microphone_devices.append(device)

        return sound_devices, microphone_devices

    @staticmethod
    def find_speaker_mic_devices():
        devices = AudioUtils.__getDevicesWithSD__()
        deviceElements=[]

        # print(devices)
        sound_devices = []
        microphone_devices = []

        for idx, device in enumerate(devices):
            if AudioUtils.is_speaker_device(device):
                sound_devices.append(device)
            # if device['max_input_channels'] > 0:
            if AudioUtils.is_mic_device(device):
                # if AudioUtils.is_device_model_microphone(device):
                microphone_devices.append(device)
        return sound_devices, microphone_devices

    # @staticmethod
    # @deprecated_function
    # def addDeviceElementToList(resultList, device, idx):
    #     deviceElement = AudioUtils.convertToDeviceElement(device, idx)
    #     resultList.append(deviceElement)
    #     return resultList
    #
    # @staticmethod
    # @deprecated_function
    # def convertToDeviceElement(device, idx):
    #     device_info = f"{idx}: {device['name']} (USB Port: {device.get('usb_port', 'N/A')})"
    #     name = device["name"]
    #     deviceElement = {"index": idx, "label":device_info, "name": name, "device": device}
    #     return deviceElement
    #
    # @staticmethod
    # @deprecated_function
    # def extractDeviceFromDeviceDictElement(deviceDictElement):
    #     # print(deviceDictElement)
    #     if deviceDictElement:
    #         return deviceDictElement.get("index"), deviceDictElement.get("label"), deviceDictElement.get("name"), deviceDictElement.get("device")
    #     return None, None, None, None
    # @staticmethod
    # @deprecated_function
    # def getDeviceElementByDeviceIdxFromList(deviceList, idx):
    #     # print(deviceList)
    #     for i, deviceDictElement in enumerate(deviceList):
    #         # keys = deviceDictElement.keys()
    #         deviceIndex = deviceDictElement.get("index")
    #         if deviceIndex == idx:
    #             return deviceDictElement
    #     return None
    # @staticmethod
    # @deprecated_function
    # def get_working_audio_deviceElements():
    #     working_devices = []
    #     # for dev in sd.query_devices():
    #     idx=0
    #     for dev in AudioUtils.__getDevicesWithSD__():
    #         # print(dev)
    #         try:
    #             name=dev["name"]
    #             sd.check_input_settings(device=name)
    #             AudioUtils.addDeviceElementToList(working_devices, dev, idx)
    #         except sd.PortAudioError as e:
    #             AudioUtils.debug(f"is_audio_devices_working check: device '{dev['name']}': {str(e)}")
    #             #print(e)
    #         except Exception as e:
    #             AudioUtils.debug(f"is_audio_devices_working check2: device '{dev['name']}' : An unexpected error occurred: {str(e)}")
    #             #print(e)
    #     return working_devices
    #
    # @staticmethod
    # @deprecated_function
    # def is_microphone_withRefresh(deviceIndex):
    #     deviceList = sd.query_devices()
    #     AudioUtils.is_microphone_working(deviceList, deviceIndex)
    #
    # @staticmethod
    # @deprecated_function
    # def is_speaker_device_element(deviceElement):
    #     idx, label, name, device = AudioUtils.extractDeviceFromDeviceDictElement(deviceElement)
    #     result = False
    #     if device:
    #         if device['max_output_channels'] > 0:
    #             return True
    #     return result
    #
    # @staticmethod
    # @deprecated_function
    # def is_device_model_microphone(deviceElement):
    #     result = False
    #     try:
    #         # dev=deviceList[deviceIndex]
    #         idx, label, name, device = AudioUtils.extractDeviceFromDeviceDictElement(deviceElement)
    #         # print("name")
    #         if device:
    #         ###
    #         #### sd.check_input_settings(device=name)
    #         # sd.check_input_settings(device=dev["name"])
    #
    #             if device['max_input_channels'] > 0:
    #                 # print("check micro3")
    #                 return True
    #     except sd.PortAudioError as e:
    #         AudioUtils.debug(f"is_audio_devices_working check: device '{device['name']}': {str(e)}")
    #     except Exception as e:
    #         AudioUtils.debug(f"is_audio_devices_working check: : An unexpected error occurred: {str(e)}")
    #
    #     return result

    @staticmethod
    def is_mic_device(device):
        result = False
        try:
            if device:
                if device['max_input_channels'] > 0:
                    return True
        except sd.PortAudioError as e:
            AudioUtils.debug(f"is_audio_devices_working check: device '{device['name']}': {str(e)}")
        except Exception as e:
            AudioUtils.debug(f"is_audio_devices_working check: : An unexpected error occurred: {str(e)}")
        return result
    @staticmethod
    def is_speaker_device(device):
        result = False
        try:
            if device:
                if device['max_output_channels'] > 0:
                    return True
        except sd.PortAudioError as e:
            AudioUtils.debug(f"is_audio_devices_working check: device '{device['name']}': {str(e)}")
        except Exception as e:
            AudioUtils.debug(f"is_audio_devices_working check: : An unexpected error occurred: {str(e)}")
        return result

class DeviceType(Enum):
    DEVICE_TYPE_IN = 0
    DEVICE_TYPE_OUT = 1

class DeviceLabelModel():

    DEVICE_LABEL_SEPARATOR="-"
    DEVICE_DISPLAY_SEPARATOR=". "
    def __init__(self,device: dict, type:DeviceType):
        self.device=device
        self.type=type
        self.label=None

    def get_device_idx(self):
        if self.device:
            return self.device["index"]
        return None
    def get_device_name(self):
        if self.device:
            return self.device["name"]
        return None
    def get_device_label(self):
        if self.device:
            return f"{self.get_device_idx()} {DeviceLabelModel.DEVICE_LABEL_SEPARATOR} {self.get_device_name()}"
        return None

    def display_device_for_printing(self):
        if self.device:
            return f"[ {self.get_device_idx()}] => {self.get_device_name()}"
        return None

    def get_device_info(self,key: str):
        if self.device:
            return self.device[key]

    def is_device_type(self, device_type):
        if (self.type == device_type):
            return True
        return False
    @staticmethod
    def get_device_idx_name_from_label(label: str) -> Tuple[int, str]:
        idx=None
        name=None
        try:
            if label:
                elements = label.split(DeviceLabelModel.DEVICE_LABEL_SEPARATOR)
                n=len(elements)
                if n == 2:
                    idx = int(elements[0])
                    name = elements[1]
                elif n > 2:
                    idx = int(elements[0])
                    name = ''.join(elements[1:])
        except Exception as e:
            DeviceLabelModel.error(f"{e}", exception=e)
        return idx, name

class EmbeddedAudioSelector(LEC):
    def __init__(self, configLog=False):
        super().__init__()
        #print(f"initalization subclass {self.__class__.__name__}")
        self.input_device_index=None
        self.speaker_device_index = None
        self.mic_device_models: list[DeviceLabelModel] = []
        self.speaker_device_models: list[DeviceLabelModel] = []
        self.output_device_index = None
        self.input_device_index = None

        self.__initialize_audio_devices__()

        if (configLog):
            configLogOutput()

    def __initialize_audio_devices__(self):
        speaker_models, mic_models = AudioUtils.find_speaker_mic_devices()
        print(f"#speaker{len(speaker_models)}")
        print(f"#mic{len(mic_models)}")
        for e in speaker_models:
            self.speaker_device_models.append(DeviceLabelModel(e, DeviceType.DEVICE_TYPE_OUT))
        for e in mic_models:
            self.mic_device_models.append(DeviceLabelModel(e, DeviceType.DEVICE_TYPE_OUT))

    def reinitialize_module(self):
        self.input_device_index=None
        self.speaker_device_index = None
        self.mic_device_models: list[DeviceLabelModel] = []
        self.speaker_device_models: list[DeviceLabelModel] = []
        self.output_device_index = None
        self.input_device_index = None
        self.__initialize_audio_devices__()

    def find_device_model_from_idx(self, idx: int, device_type:DeviceType):
        model_list=None
        if (device_type==DeviceType.DEVICE_TYPE_IN):
            model_list = self.mic_device_models
        else:
            model_list = self.speaker_device_models
        for device_model in self.speaker_device_models:
            if device_model.get_device_idx() == idx:
                return device_model
        return None
    def __display_microphones_menu__(self):
        device_model_list = self.mic_device_models
        self.__display_device_menu__(self, device_model_list=device_model_list)
    def __display_speaker_menu__(self):
        device_model_list = self.speaker_device_models
        self.__display_device_menu__(self, device_model_list=device_model_list)
    def __display_device_menu__(self, device_model_list):
        print("Available input devices:")
        for i, deviceModel in enumerate(self.mic_device_models):
            print(f"- {deviceModel.display_device_for_printing()}")

    def __microphonePostSelectionControl__(self, userInput):
        self.__devicePostSelectionControl__(userInput, DeviceType.DEVICE_TYPE_IN)
    def __speakerPostSelectionControl__(self, userInput):
        self.__devicePostSelectionControl__(userInput, DeviceType.DEVICE_TYPE_OUT)

    def __check__device_of_type__(self, device_model, device_type):
        if (device_type==DeviceType.DEVICE_TYPE_IN and device_model.is_device_type(device_type) and AudU.is_mic_device(device_model)):
            return True
        elif (device_type==DeviceType.DEVICE_TYPE_OUT and device_model.is_device_type(device_type) and AudU.is_speaker_device(device_model)):
            return True
        return False
    def __devicePostSelectionControl__(self, userInput, device_type):
        try:
            if (userInput.strip().lower()=="q"):
                return UserInputUtils.QUIT_LOOP
            else:
                device_model = self.find_device_model_from_idx(idx=int(userInput), device_type=device_type)
                if (device_type==DeviceType.DEVICE_TYPE_OUT):
                    if device_model.is_device_type(device_type) and AudU.is_mic_device(device_model.device):
                        self.input_device_index = int(userInput)
                        return UserInputUtils.VALID_INPUT
                elif (device_type == DeviceType.DEVICE_TYPE_OUT):
                    if device_model.is_device_type(device_type) and AudU.is_speaker_device(device_model.device):
                        self.output_device_index = int(userInput)
                        return UserInputUtils.VALID_INPUT
            print("Invalid option!")
            return UserInputUtils.INVALID_INPUT
        except Exception as e:
            self.debug("An error occured!", exception=e,appendTrace=False)
        return UserInputUtils.INVALID_INPUT

    def get_unique_label_from_audio_device(self, device) -> str:
        return f"{device['index']}{DeviceLabelModel.DEVICE_LABEL_SEPARATOR}{device['name']}"
    def get_unique_label_from_audio_device_model(self, device_model) -> str:
        return self.get_unique_label_from_audio_device(device_model.device)

    def choose_mic_device(self):
        userInput = UserInputUtils.getUserInput("Please select a speaker device:", displayMenuCallback=self.__display_microphones_menu__, userInputControlCallback=self.__microphonePostSelectionControl__, refreshManu=False)

    def __display_speakers_menu__(self):
        print("Available output devices:")
        for i, deviceModel in enumerate(self.speaker_device_models):
            print(f"- {deviceModel.display_device_for_printing()}")

    def choose_speaker_device(self):
        # print(self.speakerElements)
        userInput = UserInputUtils.getUserInput("Please select a speaker device:", displayMenuCallback=self.__display_speaker_menu__, userInputControlCallback=self.__speakerSelectionCOntrol__, refreshManu=False)

    def get_speaker_model_list(self):
        return self.speaker_device_models

    def get_speaker_model_labels(self):
        return [self.get_unique_label_from_audio_device_model(model) for model in self.speaker_device_models]

    def get_mic_model_labels(self):
        return [self.get_unique_label_from_audio_device_model(model) for model in self.mic_device_models]

    def get_mic_model_from_list_by_idx(self, idx):
        return self.find_device_model_from_idx(idx, DeviceType.DEVICE_TYPE_IN)

    def get_speaker_model_from_list_by_idx(self, idx):
        return self.find_device_model_from_idx(idx, DeviceType.DEVICE_TYPE_OUT)

    def get_mic_model_list(self):
        return self.mic_device_models

    def set_selected_mic_device_by_user(self, idx: int):
        self.input_device_index=idx

    def get_selected_mic_device_model_by_user(self):
        if self.input_device_index:
            return self.find_device_model_from_idx(self.input_device_index, DeviceType.DEVICE_TYPE_IN)
        return None

    def set_selected_speaker_device_by_user(self, idx: int):
        self.output_device_index=idx

    def get_selected_speaker_device_model_by_user(self):
        if self.output_device_index:
            return self.find_device_model_from_idx(self.output_device_index, DeviceType.DEVICE_TYPE_OUT)
        return None

    def get_label_list_index_of_selected_mic_device(self):
        if self.input_device_index:
            for i, device_model in enumerate(self.get_mic_model_list()):
                if device_model.get_device_idx() == self.input_device_index:
                    return i
        return None

    def get_label_list_index_of_selected_speaker_device(self):
        if self.output_device_index:
            for i, device_model in enumerate(self.get_speaker_model_list()):
                if device_model.get_device_idx() == self.output_device_index:
                    return i
        return None


@deprecated_class
class AudioSelector(LEC):
    def __init__(self, duration=10, fs=16000, configLog=False):
        super().__init__()
        print(f"initalization subclass {self.__class__.__name__}")
        self.input_device_index=None
        self.speaker_device_index = None
        self.speakerElements = []
        self.micElements = []
        if (configLog):
            configLogOutput()

        self.__find_audio_devices__()
        # print(self.micElements)

    def __display_microphone_menu__(self):
        print("Available input devices:")
        #devices = sd.query_devices()
        # for i, device in enumerate(self.mics):
        #     if device['max_input_channels'] > 0:
        #         print(f"Device {i}: {device['name']}, Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")
        for i, deviceElement in enumerate(self.micElements):
            # print(i)
            # print(deviceElement)
            idx, label, name, device = AudU.extractDeviceFromDeviceDictElement(deviceElement)
            # print(f"- {label}")
            print(f"- {label} [{idx}]")


    def __microphoneSelectionCOntrol__(self, userInput):
        try:
            if (userInput.strip().lower()=="q"):
                return UserInputUtils.QUIT_LOOP
            else:
                deviceElement = AudU.getDeviceElementByDeviceIdxFromList(self.micElements, int(userInput))
                if (deviceElement and AudU.is_device_model_microphone(deviceElement)):
                    self.input_device_index = int(userInput)
                    return UserInputUtils.VALID_INPUT
            print("Invalid option!")
            return UserInputUtils.INVALID_INPUT
        except Exception as e:
            self.debug("An error occured!", exception=e,appendTrace=False)
        return UserInputUtils.INVALID_INPUT

    def choose_input_device(self):
        self.__find_input_devices__()
        # print(self.micElements)
        userInput = UserInputUtils.getUserInput("Please select a microphone device:", displayMenuCallback=self.__display_microphone_menu__, userInputControlCallback=self.__microphoneSelectionCOntrol__, refreshManu=False)

    def __find_speaker_devices__(self):
        self.__find_audio_devices__()
        #print(self.speakerElements)

    def __find_audio_devices__(self):
        self.speakerElements, self.micElements = AudU.find_speaker_mic_devices()

    def __display_speaker_menu__(self):
        print("Available speaker devices:")
        #devices = sd.query_devices()
        # for i, device in enumerate(self.mics):
        #     if device['max_input_channels'] > 0:
        #         print(f"Device {i}: {device['name']}, Channels: {device['max_input_channels']}, Sample Rate: {device['default_samplerate']}")
        for i, deviceElement in enumerate(self.speakerElements):
            # print(i)
            # print(deviceElement)
            idx, label, name, device = AudU.extractDeviceFromDeviceDictElement(deviceElement)
            print(f"- {label} [{idx}]")
            # print(f"- {label}")

    def __speakerSelectionCOntrol__(self, userInput):

        try:
            if (userInput.strip().lower() == "q"):
                return UserInputUtils.QUIT_LOOP
            else:
                deviceElement = AudU.getDeviceElementByDeviceIdxFromList(self.speakerElements, int(userInput))
                if (deviceElement and AudU.is_speaker_device_element(deviceElement)):
                    self.speaker_device_index = int(userInput)
                    return UserInputUtils.VALID_INPUT
            print("Invalid option!")
            return UserInputUtils.INVALID_INPUT
        except Exception as e:
            self.debug("An error occured!", exception=e,appendTrace=False)
        return UserInputUtils.INVALID_INPUT

    def choose_speaker_device(self):
        self.__find_speaker_devices__()
        # print(self.speakerElements)
        userInput = UserInputUtils.getUserInput("Please select a speaker device:", displayMenuCallback=self.__display_speaker_menu__, userInputControlCallback=self.__speakerSelectionCOntrol__, refreshManu=False)

    def __getSelectedSpeakerDeviceName__(self):
        deviceName = AudU.getDeviceElementByDeviceIdxFromList(self.speakerElements, self.speaker_device_index).get(
            "device").get("name")
        return deviceName

    def __getSelectedMicroDeviceName__(self):
        deviceName = AudU.getDeviceElementByDeviceIdxFromList(self.micElements, self.input_device_index).get(
            "device").get("name")
        return deviceName


