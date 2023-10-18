import librosa
import numpy as np
import requests
import json

from keras.models import load_model
from transformers import AutoFeatureExtractor, WhisperModel



audio_file_path = 'resampled_audio.wav'
modelFrom = "LocalGoogleWhisper"
modelFilePath = r'C:\repo\dev\pythonProjects\testVSCode\audio2text\models\googleWhisper\tf_model.h5'
modelFilePath = r'C:\repo\dev\pythonProjects\testVSCode\audio2text\models\googleWhisper\tf_model(2).h5'
#audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"
transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_file_path}_transcription{modelFrom}.txt"

# Define the chunk size (e.g., 10 seconds per chunk)
chunk_size_seconds = 30
# Define the overlap factor
overlap_factor = 0.5  # 50% overlap

# Load the TensorFlow model
model = WhisperModel.from_pretrained("openai/whisper-large-v2")

#model = load_model(modelFilePath)

# Load audio file
audio, sample_rate = librosa.load(audio_file_path, sr=16000)  # Resampling to 16kHz if needed

chunk_size = int(chunk_size_seconds * sample_rate)

# Function to preprocess audio and transcribe using Google Whisper model
def process_and_append_transcription(audio_chunk, output_file):
    # Preprocessing steps
    mfccs = librosa.feature.mfcc(y=audio_chunk, sr=sample_rate, n_mfcc=13)
    mfccs = (mfccs - np.mean(mfccs)) / np.std(mfccs)
    mfccs = np.expand_dims(mfccs, axis=0)

    # Call the function to transcribe the audio chunk
    transcription = transcribe_audio(mfccs)

    # Append the transcription to the output file
    with open(output_file, 'a') as file:
        file.write(transcription + '\n')

# Function to send MFCCs to Google Whisper model (local h5 file)
def transcribe_audio(mfccs):
    # Load the model (replace with your actual model loading code)
    model = load_google_whisper_model()  # Implement this function

    # Assuming your model takes MFCCs as input and returns transcriptions
    transcription = model.predict(mfccs)

    return transcription

# Load Google Whisper model (replace with your actual model loading code)
def load_google_whisper_model():
    # Load your model from the h5 file
    # Replace the following with your actual model loading code
    model = None  # Load your model using appropriate functions
    return model

# Split audio into chunks, preprocess, and transcribe each chunk
start = 0
transcription_output_file = transcription_file_path

total_samples = len(audio)
overlap_samples = int(chunk_size * overlap_factor)
step_size = chunk_size - overlap_samples

chunks = []
while start < total_samples:
    end = min(start + chunk_size, total_samples)
    chunk = audio[start:end]

    # Process and append the transcription of the chunk to the output file
    process_and_append_transcription(chunk, transcription_output_file)

    #chunks.append(chunk)
    start += step_size

print('Transcriptions saved to', transcription_output_file)
