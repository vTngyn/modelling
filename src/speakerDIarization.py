from pyAudioAnalysis import audioSegmentation as aS

# Load the audio
# Assumes 'audio_file.wav' is the path to the audio file
audio_file = 'audio_file.wav'

# Perform speaker diarization
[flagsInd, classesAll, acc, CM] = aS.mtFileClassification(audio_file, 'svm', 'data/svmSM', True, 'data/scaler')

# Print the segments and their associated classes
print("Speaker Diarization Segments:")
for i in range(len(classesAll)):
    print(f"Segment {i+1}: Speaker {classesAll[i]}")

# You can use flagsInd and classesAll to get information about speaker segments
