import speech_recognition as sr
import pyaudio
from langdetect import detect
import langid

import webrtcvad
import sounddevice as sd
import numpy as np
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC, configLogOutput
from vtnLibs.AudioDeviceUtils import AudioUtils as AudU
from vtnLibs.UserInteractionUtils import UserInputUtils

class RTAudioTranscription(LEC):

    def __int__(self):
        self.mic_index = None
        self.micElements = None
        self.speakerElements = None
        self.input_device_index
    def list_device(self):
        p = pyaudio.PyAudio()

        # Get available microphones
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            device_info = p.get_device_info_by_index(index)
            print(f"{index}: {name} [{device_info['maxInputChannels']}, model': {device_info.get('model_info', '')}]")
            #print(f"{index}: {name} [{device_info}]")

    def choose_device(self):
        self.list_device()
        mic_index = int(input("Choose a microphone (enter the corresponding index): "))
        return mic_index

    def recognize_speech(self):
        # Initialize the recognizer
        recognizer = sr.Recognizer()

        # Ask the user to choose a microphone
        self.mic_index=self.choose_device()

        # Initialize the selected microphone
        self.mic = sr.Microphone(device_index=self.mic_index)

        print("Listening...")

        language=None

        with self.mic as source:
            print("Listening... Press 'q' to exit.")
            while True:
                try:
                    audio = recognizer.listen(source)

                    recognized_text = None
                    if language:
                        print(f"declared language:{language}")
                        recognized_text = recognizer.recognize_google(audio, language=language)
                    else:
                        print(f"recognition with language auto detection:{language}")
                        recognized_text = recognizer.recognize_google(audio)

                    # Detect the language of the transcribed text
                    detected_language1 = detect(recognized_text)
                    # Detect the language of the transcribed text
                    detected_language2, confidence = langid.classify(recognized_text)

                    print("You said:", recognized_text)
                    print(f"in {detected_language1} with {confidence}:")
                    print(f"in {detected_language2} with {confidence}:")
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                inputStr=input("Enter the language, Enter for autodetection or press 'q' to exit: ")
                if inputStr.strip().lower() == 'q':
                    print("Exiting...")
                    break
                elif inputStr.strip().lower() == '':
                    language = None
                else:
                    language = inputStr
                print("Listening...")

class RTAudioProcessing(LEC):
    def __init__(self, duration=10, fs=16000):
        super().__init__()
        print(f"initalization subclass {self.__class__.__name__}")
        self.input_device_index=None
        # Initialize VAD
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(2)  # Aggressive mode
        self.input_device_index = None
        self.speaker_device_index = None
        # Parameters for audio processing
        self.duration = duration  # Duration in seconds
        self.fs = fs  # Sample rate in Hz
        self.speakerElements = []
        self.micElements = []


    # Callback function to process audio chunks
    def detectSilencecallback(self, indata, frames, time, status):
        if status:
            print('Error:', status)

        # Print some information about the audio data
        print('Audio data shape:', indata.shape)
        print('Audio data min:', np.min(indata))
        print('Audio data max:', np.max(indata))
        print('Audio data mean:', np.mean(indata))

        # Convert audio data to a byte string
        # audio_bytes = b''.join(indata)
        #audio_bytes = indata.tobytes()
        #audio_bytes = (indata * 32767.0).astype(np.int16).tobytes()   # to be compatible with SD
        audio_bytes = (indata.flatten() * 32767.0).astype(np.int16).tobytes()   # to be compatible with SD

        # Check the length of the byte string (should match the frames)
        print('Length of audio_bytes:', len(audio_bytes), 'frames:', frames)

        # Check if speech is detected
        try:
            if self.vad.is_speech(audio_bytes, self.fs):
                print('Speech detected')
            else:
                print('No speech detected')
        except Exception as e:
            print('Error from webrtcvad:', str(e))

    def find_input_devices(self):
        self.find_audio_devices()
        # print(self.micElements)

    def display_microphone_menu(self):
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


    def microphoneSelectionCOntrol(self, userInput):
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
        self.find_input_devices()
        # print(self.micElements)
        userInput = UserInputUtils.getUserInput("Please select a microphone device:", displayMenuCallback=self.display_microphone_menu, userInputControlCallback=self.microphoneSelectionCOntrol, refreshManu=False)

    def find_speaker_devices(self):
        self.find_audio_devices()
        #print(self.speakerElements)

    def find_audio_devices(self):
        self.speakerElements, self.micElements = AudU.findSpeakerMicroDeviceElements()

    def display_speaker_menu(self):
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

    def speakerSelectionCOntrol(self, userInput):

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
        self.find_speaker_devices()
        # print(self.speakerElements)
        userInput = UserInputUtils.getUserInput("Please select a speaker device:", displayMenuCallback=self.display_speaker_menu, userInputControlCallback=self.speakerSelectionCOntrol, refreshManu=False)

    def processRTAudio(self):
        self.choose_speaker_device()
        self.choose_input_device()
        # Start audio recording and process in real-time

        print(f'Listening for speech...{self.duration} - {self.fs}')
        deviceName = AudU.getDeviceElementByDeviceIdxFromList(self.micElements, self.input_device_index).get("device").get("name")
        print(f"deviceName={deviceName}")
        # with sd.InputStream(device=self.input_device_index, callback=self.detectSilencecallback, channels=1, samplerate=self.fs):
        # with sd.InputStream(device=self.input_device_index, callback=self.detectSilencecallback, channels=1, samplerate=self.fs):
        with sd.InputStream(device=deviceName, callback=self.detectSilencecallback, channels=1, samplerate=self.fs):
            sd.sleep(int(self.duration * 1000))

        print('Done')
if __name__ == "__main__":
    FEAT_TRANSCRIPTION= "trasncription"
    FEAT_RT_PROCESSING= "RTProcessing"

    configLogOutput()

    method=FEAT_RT_PROCESSING

    if method == FEAT_TRANSCRIPTION:
        audTrans = RTAudioTranscription()
        audTrans.recognize_speech()
    elif method == FEAT_RT_PROCESSING:
        pRTAudio=RTAudioProcessing()
        pRTAudio.processRTAudio()
    else:
         print("please choose a method")

