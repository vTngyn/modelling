import torch
from pydub import AudioSegment
from pydub.playback import play
from pyannote.audio.features import RawAudio
from pyannote.audio.features.pretrained import SincNet

import librosa
import numpy as np
# Load the pre-trained SincNet model
sincnet = SincNet.from_h5("sincnet_musan.h5")

# Constants for audio preprocessing
SAMPLE_RATE = 16000  # SincNet requires 16kHz sample rate
NUM_CHANNELS = 1  # Mono

def extract_mfcc(audio_file, num_mfcc=13):
    # Load the audio file
    y, sr = librosa.load(audio_file, sr=None)

    # Extract MFCC features
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=num_mfcc)

    # Transpose the matrix to have time along the x-axis (frames) and features along the y-axis
    mfccs = mfccs.T

    return mfccs

# Function to preprocess audio
def preprocess_audio(audio_file):
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_frame_rate(SAMPLE_RATE)
    audio = audio.set_channels(NUM_CHANNELS)
    return audio.raw_data

# Function to extract embeddings for a speaker
def extract_embeddings(speaker_name, audio_data):
    # Extract features
    raw_audio = RawAudio(sample_rate=SAMPLE_RATE)
    features = raw_audio({"waveform": torch.Tensor(audio_data).unsqueeze(0)})

    # Extract embeddings
    embeddings = sincnet({'raw_audio': features})
    return embeddings, speaker_name

# Example usage
audio_file = "path/to/audio/file.wav"
speaker_name = "John Doe"

# Preprocess audio
audio_data = preprocess_audio(audio_file)

# Extract embeddings for the speaker
embeddings, speaker_name = extract_embeddings(speaker_name, audio_data)

# Print or store the embeddings and associated speaker name
print("Speaker:", speaker_name)
print("Embeddings shape:", embeddings.shape)
