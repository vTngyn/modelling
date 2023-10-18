import webrtcvad
import sounddevice as sd
import numpy as np

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(2)  # Aggressive mode

# Parameters for audio processing
duration = 10  # Duration in seconds
fs = 16000  # Sample rate in Hz

# Callback function to process audio chunks
def callback(indata, frames, time, status):
    if status:
        print('Error:', status)
    if vad.is_speech(b''.join(indata), fs):
        print('Speech detected')
    else:
        print('No speech detected')

# Start audio recording and process in real-time
print('Listening for speech...')
with sd.InputStream(callback=callback, channels=1, samplerate=fs):
    sd.sleep(int(duration * 1000))

print('Done')
