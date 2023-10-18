import deepspeech
import wave
import time
import numpy

job_start_time = time.time()  # Start timer
audio_path = 'resampled_audio.wav'
transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_path}_transcriptionDeepSpeech.txt"

# Load the pre-trained DeepSpeech model
model_path = r'C:\repo\dev\pythonProjects\testVSCode\audio2text\models\deepSpeech\deepspeech-0.9.3-models.pbmm'
ds = deepspeech.Model(model_path)

# Load the scorer file for improved accuracy (optional, but recommended)
scorer_path = r'C:\repo\dev\pythonProjects\testVSCode\audio2text\models\deepSpeech\deepspeech-0.9.3-models.scorer'
ds.enableExternalScorer(scorer_path)

# Load the audio file
audio = None
sample_rate = None
try:
    #with wave.open(audio_path, 'rb') as audio_file:
    #    print('Number of Channels:', audio_file.getnchannels())
    #    print('Sample Width (bytes):', audio_file.getsampwidth())
    #    print('Frame Rate:', audio_file.getframerate())
    #    print('Number of Frames:', audio_file.getnframes())

    audio_file = wave.open(audio_path, 'rb')
    audio = audio_file.readframes(-1)
    sample_rate = audio_file.getframerate()
    audio_file.close()

        #audio = audio_file.readframes(audio_file.getnframes())
    #    audio = audio_file.readframes(-1)
        #audio = audio_file.read()
        #sample_rate = audio_file.getframerate()

except wave.Error as e:
    print('Failed to read the audio file:', str(e))
# Perform speech-to-text

if audio is not None and sample_rate is not None:
    #text = ds.stt(audio)
    text = ds.stt(numpy.frombuffer(audio, numpy.int16))
    #text = ds.stt(audio, sample_rate)
    print('Transcription:', text)

    # Save the transcription to a text file
    with open(transcription_file_path, "w") as file:
        file.write(transcription)
else:
    print('Failed to read the audio file.')
    sample_rate = audio_file.getframerate()



# Print the transcribed text
#print('Transcription:', text)

job_end_time = time.time()  # Start timer
job_elapsed_time = job_end_time - job_start_time
print(f"Transcription JOB completed in {job_elapsed_time:.2f} seconds")