from pyAudioAnalysis import audioSegmentation as aS
import matplotlib.pyplot as plt
from pydub import AudioSegment

# Load an audio file
audio_file = "path/to/audio.wav"  # Replace with your audio file
audio = AudioSegment.from_wav(audio_file)
fs = audio.frame_rate  # Sample rate

# Perform speech activity detection
flags, classes = aS.silenceRemoval(audio_file)

# Plot the audio waveform and SAD results
plt.subplot(2, 1, 1)
plt.plot(audio.get_array_of_samples())
plt.title('Audio Waveform')
plt.xlabel('Time (s)')

plt.subplot(2, 1, 2)
plt.plot(classes, color='r')
plt.title('Speech Activity Detection (SAD)')
plt.xlabel('Time (s)')

plt.tight_layout()
plt.show()
