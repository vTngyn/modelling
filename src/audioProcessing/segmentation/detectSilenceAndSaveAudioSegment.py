import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import threading
from pydub import AudioSegment
import datetime
import time

import numpy as np
import sounddevice as sd
from pydub import AudioSegment
import tensorflow as tf
import tensorflow_hub as hub
import datetime
import threading
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

class RealTimeAudioAnalyzer:
    def __init__(self):
        self.model_url = "https://tfhub.dev/google/vggish/1"
        self.vggish_model = hub.load(self.model_url)
        self.current_segment = None
        self.segment_count = 0
        self.running = False
        self.segmentFilesOutputPath= "../../../out/audio/segmentAudioFiles"
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        self.model_name = "facebook/wav2vec2-base-960h"
        self.model_processorWav2Vec2 = None
        self.model_Wav2Vec2 = None

    def preprocess_audio(self, audio):
        # Normalize audio data
        audio /= np.max(np.abs(audio))

        # Pad or truncate the audio to match the model's input shape
        target_length = 96000  # Adjust according to the model's expected length
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        elif len(audio) > target_length:
            audio = audio[:target_length]

        # Reshape audio to match the expected input shape of the model
        audio = audio.reshape((1, -1))

        return audio

    # Voice Activity Detection (VAD) using Root Mean Square (RMS)
    def vad_rms(self, audio_frame):
        # Constants for VAD
        SPEECH_THRESHOLD = 0.01  # Adjust this threshold based on your audio characteristics

        rms_value = np.sqrt(np.mean(audio_frame ** 2))
        return rms_value > SPEECH_THRESHOLD

    def detect_speech(self, embeddings):
        # Perform your own logic here to determine speech activity based on embeddings
        # For demonstration, we'll consider embeddings with any non-zero value as speech
        is_speech = np.any(embeddings != 0)
        return is_speech

    def save_segment_with_timestamp(self, segment):


        # Save the segment as both FLAC and MP3 with the timestamp in the filename
        segment.export(f'{self.segmentFilesOutputPath}/segment_{self.timestamp}_{self.segment_count}.flac', format='flac')
        segment.export(f'{self.segmentFilesOutputPath}/segment_{self.timestamp}_{self.segment_count}.mp3', format='mp3')
        print(f'Segment {self.segment_count} saved with timestamp {self.timestamp}.')

        self.segment_count += 1

    # def preprocess_audio(self, audio):
    #     # Normalize audio data
    #     audio /= np.max(np.abs(audio))
    #
    #     # Pad or truncate the audio to match the model's input shape
    #     target_length = 96000  # Adjust according to the model's expected length
    #     if len(audio) < target_length:
    #         audio = np.pad(audio, (0, target_length - len(audio)))
    #     elif len(audio) > target_length:
    #         audio = audio[:target_length]
    #
    #     # Reshape audio to match the expected input shape of the model
    #     audio = audio.reshape((1, -1)).astype(np.float32)
    #
    #     return {'waveform': tf.convert_to_tensor(audio)}
    # def preprocess_audio(self, audio):
    #     # Normalize audio data
    #     audio /= np.max(np.abs(audio))
    #
    #     # Pad or truncate the audio to match the model's input shape
    #     target_length = 96000  # Adjust according to the model's expected length
    #     if len(audio) < target_length:
    #         audio = np.pad(audio, (0, target_length - len(audio)))
    #     elif len(audio) > target_length:
    #         audio = audio[:target_length]
    #
    #     # Reshape audio to match the expected input shape of the model
    #     audio = audio.reshape((1, -1)).astype(np.float32)
    #
    #     return tf.convert_to_tensor(audio)
    def preprocess_audio(self, audio):
        # Normalize audio data
        audio /= np.max(np.abs(audio))

        # Pad or truncate the audio to match the model's input shape
        target_length = 96000  # Adjust according to the model's expected length
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        elif len(audio) > target_length:
            audio = audio[:target_length]

        # Reshape audio to match the expected input shape of the model
        audio = audio.reshape((1, -1)).astype(np.float32)

        return tf.convert_to_tensor(audio)

    # Define a function to preprocess the audio data
    def preprocess_audio(self, audio_data):
        # Preprocess audio (assuming mono audio)
        inputs = self.model_processorWav2Vec2(audio_data, sampling_rate=16000, return_tensors="pt", padding=True)
        return inputs

    def load_model_transformers(self):
        # Load the pre-trained Wav2Vec2 model and processor
        self.model_name = "facebook/wav2vec2-base-960h"
        self.model_processorWav2Vec2 = Wav2Vec2Processor.from_pretrained(self.model_name)
        self.model_Wav2Vec2 = Wav2Vec2ForCTC.from_pretrained(self.model_name)

    def audio_callback_torch(self, indata, frames, time, status):
        if status:
            print("Error:", status)
            return

        # Assuming indata is mono audio
        audio_mono = torch.from_numpy(indata[:, 0]).float()
        inputs = self.preprocess_audio(audio_mono)

        # Perform inference with the pre-trained model
        with torch.no_grad():
            outputs = self.model_Wav2Vec2(**inputs)

        # Process the model outputs as needed based on your use case
        # For example, obtain the predicted transcriptions
        transcriptions = self.model_processorWav2Vec2.batch_decode(outputs["logits"])
        print("Predicted transcriptions:", transcriptions)

    def transcribe_speech_segments(self, speech_segments):
        # Iterate through speech segments
        for segment in speech_segments:
            # Transcribe the segment using Wav2Vec2
            transcription = self.model_processorWav2Vec2.transcribe(segment)
            print("Transcription:", transcription)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print('Error:', status)
            return

        sample_rate = sd.query_devices(None, 'input')['default_samplerate']

        audio_frame_mono = np.mean(indata, axis=1)
        audio_flat = audio_frame_mono.flatten()
        """
        audio_flat_reshaped = audio_flat.reshape(-1)  # Reshape to (None,)

        # Convert the audio_flat to a TensorFlow Tensor
        audio_tensor = tf.constant(audio_flat_reshaped, dtype=tf.float32)

        embeddings = self.vggish_model({'waveform': audio_tensor})['embedding']

        is_speech = self.detect_speech(embeddings)
        """
        preprocessed_frame = self.preprocess_audio_for_vggish(audio_frame_mono)

        speech_segments = self.apply_vggish_for_vad(preprocessed_frame)

        # embeddings = self.vggish_model(self.preprocess_audio(audio_flat))
        # embeddings = self.vggish_model(self.preprocess_audio(audio_flat))['embedding']
        # embeddings = self.vggish_model({'waveform': self.preprocess_audio(audio_flat)})['embedding']
        # embeddings = self.vggish_model(self.preprocess_audio(audio_flat))['embedding']

        is_speech = self.vad_rms(audio_frame_mono)

        if is_speech:
            print('+', end='', flush=True)  # Speech detected
            if self.current_segment is None:
                self.current_segment = AudioSegment.silent()
            self.current_segment += AudioSegment(
                audio_flat.tobytes(),
                frame_rate=44100,
                sample_width=audio_flat.dtype.itemsize,
                channels=1
            )
        elif np.any(embeddings != 0):
            print('*', end='', flush=True)  # Ambiguous prediction
        else:
            print('.', end='', flush=True)  # Silence

        if self.current_segment is not None:
            self.save_segment_with_timestamp(self.current_segment)
            self.current_segment = None

    def preprocess_audio_for_vggish(self, audio_frame):
        # Assuming audio_frame is mono audio and you need to convert to mel spectrogram
        # You may need to modify this preprocessing based on your specific requirements
        mel_spectrogram = self.compute_mel_spectrogram(audio_frame)

        # Convert to PyTorch tensor and add batch dimension
        mel_spectrogram_tensor = torch.unsqueeze(torch.tensor(mel_spectrogram), 0)

        return mel_spectrogram_tensor

    # Example function to compute mel spectrogram (you may need to adjust this)
    def compute_mel_spectrogram(self, audio_frame):
        # Use torchaudio or any other library to compute mel spectrogram
        mel_transform = torchaudio.transforms.MelSpectrogram()
        mel_spectrogram = mel_transform(torch.tensor(audio_frame))
        return mel_spectrogram.numpy()  # Convert to NumPy array for VGGish

    def apply_vggish_for_vad(self, preprocessed_audio):
        # Assuming your VGGish model processes the mel spectrogram directly
        # Adjust this based on how your VGGish model expects the input
        vggish_embeddings = self.vggish_model(preprocessed_audio)

        # Perform VAD based on embeddings or other criteria
        # For simplicity, let's assume speech if embeddings are above a threshold
        threshold = 0.5
        vad_results = vggish_embeddings > threshold

        # Convert to a list of speech segments (start, end) based on VAD results
        speech_segments = self.extract_speech_segments(vad_results)

        return speech_segments

    # Example function to extract speech segments based on VAD results
    def extract_speech_segments(self, vad_results):
        segments = []
        start = None

        for i, is_speech in enumerate(vad_results):
            if is_speech and start is None:
                start = i
            elif not is_speech and start is not None:
                segments.append((start, i - 1))
                start = None

        if start is not None:
            segments.append((start, len(vad_results) - 1))

        return segments
    def listen_and_detect(self):
        with sd.InputStream(callback=self.audio_callback, channels=1):
            print("Listening in real-time. Press 'q' to stop.")
            while self.running:
                sd.sleep(100)

    def start_listening(self):
        self.running = True
        listen_thread = threading.Thread(target=self.listen_and_detect)
        listen_thread.start()

        while True:
            user_input = input()
            if user_input.lower() == 'q':
                self.running = False
                break

if __name__ == "__main__":
    analyzer = RealTimeAudioAnalyzer()
    analyzer.start_listening()

# # Load the pre-trained VGGish model
# model_url = "https://tfhub.dev/google/vggish/1"
# vggish_model = hub.load(model_url)
#
# segmentFilesOutputPath= "../../../out/audio/segmentAudioFiles"
# # Variable to indicate if the program should keep running
# running = True
#
# # Silence parameters
# SILENCE_THRESHOLD = -30  # Adjust according to your environment and noise level
# SILENCE_DURATION = 5000  # milliseconds (5 seconds)
#
# # Variables to manage audio segments
# current_segment = None
# segment_count = 0
#
# # Function to preprocess the audio data and get embeddings
# # (Same as in the previous code)
#
# # Function to detect speech activity
# # (Same as in the previous code)
# # Function to save the current segment with a timestamp in the filename
# def save_segment_with_timestamp(segment):
#     global segment_count
#
#     # Generate a timestamp for the file name (format: YYYYMMDD_HHMMSS)
#     timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
#
#     # Save the segment as both FLAC and MP3 with the timestamp in the filename
#     segment.export(f'segment_{timestamp}_{segment_count}.flac', format='flac')
#     segment.export(f'segment_{timestamp}_{segment_count}.mp3', format='mp3')
#     print(f'Segment {segment_count} saved with timestamp {timestamp}.')
#
#     segment_count += 1
#
# # Function to continuously listen to audio and detect speech
# def listen_and_detect():
#     global current_segment, segment_count
#     with sd.InputStream(callback=audio_callback, channels=1):
#         while running:
#             sd.sleep(100)
#
# # Callback function to process audio chunks and detect speech activity
# # def audio_callback(indata, frames, time, status):
# #     global current_segment
# #     if status:
# #         print('Error:', status)
# #         return
# #
# #     # Convert audio data to mono and flatten
# #     audio_mono = np.mean(indata, axis=1)
# #     audio_flat = audio_mono.flatten()
# #
# #     # Detect speech activity
# #     is_speech = detect_speech(audio_flat)
# #
# #     # Print speech activity
# #     if is_speech:
# #         print('Speech detected')
# #         if current_segment is None:
# #             current_segment = AudioSegment.silent()
# #         current_segment += AudioSegment(
# #             audio_flat.tobytes(),
# #             frame_rate=44100,
# #             sample_width=audio_flat.dtype.itemsize,
# #             channels=1
# #         )
# #     else:
# #         print('No speech detected')
# #         if current_segment is not None:
# #             # Save the current segment with a timestamp in the filename
# #             save_segment_with_timestamp(current_segment)
# #             current_segment = None
# def audio_callback(indata, frames, time, status):
#     global current_segment
#     if status:
#         print('Error:', status)
#         return
#
#     # Convert audio data to mono and flatten
#     audio_mono = np.mean(indata, axis=1)
#     audio_flat = audio_mono.flatten()
#
#     # Get the embeddings using the VGGish model
#     embeddings = vggish_model(preprocess_audio(audio_flat))
#
#     # Detect speech activity
#     is_speech = detect_speech(embeddings)
#
#     # Print speech activity
#     if is_speech:
#         print('+', end='', flush=True)  # Speech detected
#         if current_segment is None:
#             current_segment = AudioSegment.silent()
#         current_segment += AudioSegment(
#             audio_flat.tobytes(),
#             frame_rate=44100,
#             sample_width=audio_flat.dtype.itemsize,
#             channels=1
#         )
#     elif np.any(embeddings != 0):
#         print('*', end='', flush=True)  # Ambiguous prediction
#     else:
#         print('.', end='', flush=True)  # Silence
#
#     if current_segment is not None:
#         # Save the current segment with a timestamp in the filename
#         save_segment_with_timestamp(current_segment)
#         current_segment = None
#
# # Function to preprocess the audio data and get embeddings
# def preprocess_audio(audio):
#     # Normalize audio data
#     audio /= np.max(np.abs(audio))
#
#     # Pad or truncate the audio to match the model's input shape
#     target_length = 96000  # Adjust according to the model's expected length
#     if len(audio) < target_length:
#         audio = np.pad(audio, (0, target_length - len(audio)))
#     elif len(audio) > target_length:
#         audio = audio[:target_length]
#
#     # Reshape audio to match the expected input shape of the model
#     audio = audio.reshape((1, -1))
#
#     return audio
#
# # Function to detect speech activity
# # def detect_speech(audio):
# #     # Preprocess the audio
# #     preprocessed_audio = preprocess_audio(audio)
# #
# #     # Get the embeddings using the VGGish model
# #     embeddings = vggish_model(preprocessed_audio)
# #
# #     # Predict speech activity
# #     prediction = model.predict(embeddings)
# #     is_speech = prediction > 0.5  # Adjust threshold if needed
# #
# #     return is_speech
# def detect_speech(embeddings):
#     # Perform your own logic here to determine speech activity based on embeddings
#     # For demonstration, we'll consider embeddings with any non-zero value as speech
#     is_speech = np.any(embeddings != 0)
#     return is_speech
#
#
# # Function to continuously listen to audio and detect speech
# def listen_and_detect():
#     with sd.InputStream(callback=audio_callback, channels=1):
#         while running:
#             sd.sleep(100)
#
# # Function to stop the program when 'q' is pressed
# def stop_program():
#     global running
#     while True:
#         user_input = input()
#         if user_input.lower() == 'q':
#             running = False
#             break
#
# # Function to stop the program when 'q' is pressed
# # (Same as in the previous code)
#
# # Start the listening and speech detection in separate threads
# listen_thread = threading.Thread(target=listen_and_detect)
# listen_thread.start()
#
# # Start a thread to listen for user input to stop the program
# input_thread = threading.Thread(target=stop_program)
# input_thread.start()
#
# # Wait for the listening thread to finish
# listen_thread.join()
#
# # Wait for the input thread to finish
# input_thread.join()
