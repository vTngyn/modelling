import pyaudio
import sounddevice as sd
import speech_recognition as sr
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC, configLogOutput
from vtnLibs.AudioDeviceUtils import AudioUtils as AudU
from vtnLibs.UserInteractionUtils import UserInputUtils

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
    def __getDevicesWithSD__():
        return sd.query_devices()
    @staticmethod
    def choose_device(messagePrompt="Choose a microphone (enter the corresponding index): "):
        AudioUtils.list_device()
        mic_index = int(input(messagePrompt))
        return mic_index

    @staticmethod
    def findSpeakerMicroDeviceElements():
        devices = AudioUtils.__getDevicesWithSD__()
        deviceElements=[]

        # print(devices)
        sound_devices = []
        microphone_devices = []

        for idx, device in enumerate(devices):
            deviceElement = AudioUtils.convertToDeviceElement(device, idx)
            # device_info = f"{idx}: {device['name']} (USB Port: {device.get('usb_port', 'N/A')})"
            # if device['max_output_channels'] > 0:
            if AudioUtils.is_speaker(deviceElement):
                # working_devices.append({"index":idx, "name": name, "device":dev)
                # sound_devices.append(device_info)
                # AudioUtils.__addDeviceElementToList__(sound_devices, device, idx)
                sound_devices.append(deviceElement)
            # if device['max_input_channels'] > 0:
            if AudioUtils.is_microphone(deviceElement):
                if AudioUtils.is_microphone(deviceElement):
                    # AudioUtils.__addDeviceElementToList__(microphone_devices, device, idx)
                    #microphone_devices.append(device_info)
                    microphone_devices.append(deviceElement)

        return sound_devices, microphone_devices

    @staticmethod
    def addDeviceElementToList(resultList, device, idx):
        deviceElement = AudioUtils.convertToDeviceElement(device, idx)
        resultList.append(deviceElement)
        return resultList

    @staticmethod
    def convertToDeviceElement(device, idx):
        device_info = f"{idx}: {device['name']} (USB Port: {device.get('usb_port', 'N/A')})"
        name = device["name"]
        deviceElement = {"index": idx, "label":device_info, "name": name, "device": device}
        return deviceElement

    @staticmethod
    def extractDeviceFromDeviceDictElement(deviceDictElement):
        # print(deviceDictElement)
        if deviceDictElement:
            return deviceDictElement.get("index"), deviceDictElement.get("label"), deviceDictElement.get("name"), deviceDictElement.get("device")
        return None, None, None, None
    @staticmethod
    def getDeviceElementByDeviceIdxFromList(deviceList, idx):
        # print(deviceList)
        for i, deviceDictElement in enumerate(deviceList):
            # keys = deviceDictElement.keys()
            deviceIndex = deviceDictElement.get("index")
            if deviceIndex == idx:
                return deviceDictElement
        return None
    @staticmethod
    def get_working_audio_deviceElements():
        working_devices = []
        # for dev in sd.query_devices():
        idx=0
        for dev in AudioUtils.__getDevicesWithSD__():
            # print(dev)
            try:
                name=dev["name"]
                sd.check_input_settings(device=name)
                AudioUtils.addDeviceElementToList(working_devices, dev, idx)
            except sd.PortAudioError as e:
                AudioUtils.debug(f"is_audio_devices_working check: device '{dev['name']}': {str(e)}")
                #print(e)
            except Exception as e:
                AudioUtils.debug(f"is_audio_devices_working check2: device '{dev['name']}' : An unexpected error occurred: {str(e)}")
                #print(e)
        return working_devices

    @staticmethod
    def is_microphone_withRefresh(deviceIndex):
        deviceList = sd.query_devices()
        AudioUtils.is_microphone_working(deviceList, deviceIndex)

    @staticmethod
    def is_speaker(deviceElement):
        idx, label, name, device = AudioUtils.extractDeviceFromDeviceDictElement(deviceElement)
        result = False
        if device:
            if device['max_output_channels'] > 0:
                return True
        return result

    @staticmethod
    def is_microphone(deviceElement):
        result = False
        try:
            # dev=deviceList[deviceIndex]
            idx, label, name, device = AudioUtils.extractDeviceFromDeviceDictElement(deviceElement)
            # print("name")
            if device:
            ###
            #### sd.check_input_settings(device=name)
            # sd.check_input_settings(device=dev["name"])

                if device['max_input_channels'] > 0:
                    # print("check micro3")
                    return True
        except sd.PortAudioError as e:
            AudioUtils.debug(f"is_audio_devices_working check: device '{device['name']}': {str(e)}")
        except Exception as e:
            AudioUtils.debug(f"is_audio_devices_working check: : An unexpected error occurred: {str(e)}")

        return result


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

    def __find_input_devices__(self):
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
                if (deviceElement and AudU.is_microphone(deviceElement)):
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
        self.speakerElements, self.micElements = AudU.findSpeakerMicroDeviceElements()

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
                if (deviceElement and AudU.is_speaker(deviceElement)):
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


