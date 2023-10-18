from pyAudioAnalysis import audioSegmentation
import numpy as np
from pydub import AudioSegment


def speaker_diarization(audio_file):
    # Load audio file and perform segmentation
    #[flagsInd, classesAll, acc, CM] = audioSegmentation.mtFileClassification(audio_file, "data/models/svm_rbf_sm", "svm_rbf", True, "data/models/svm_rbf_sm")

    [flagsInd, classesAll, acc, CM] = audioSegmentation.silenceRemoval(audio_file, "data/svmSM", "svm", True)

    # Convert the flags to segments
    segments = []
    current_segment = []
    for i in range(len(flagsInd)):
        if i == 0:
            current_segment.append(i)
        elif flagsInd[i] != flagsInd[i - 1]:
            current_segment.append(i - 1)
            segments.append(tuple(current_segment))
            current_segment = [i]

    # Add the last segment
    if len(current_segment) > 0:
        current_segment.append(len(flagsInd) - 1)
        segments.append(tuple(current_segment))

    return segments

if __name__ == "__main__":
    audio_file = "path/to/your/audio.wav"  # Replace with the path to your audio file

    audio_in_path = '../../resources/audio/'
    #    audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a"
    audioFN = "2023_08_04_16_01_48_us622545Dierick.m4a"

    audio_file = audio_in_path + '/' + audioFN
    segments = speaker_diarization(audio_file)

    # Print the segments
    for i, segment in enumerate(segments):
        start_time = segment[0] * 0.1  # Each frame is 0.1 seconds
        end_time = segment[1] * 0.1  # Each frame is 0.1 seconds
        print(f"Segment {i+1}: Start Time: {start_time} s, End Time: {end_time} s")


"""
    pyAudioAnalysis: The main library that provides audio analysis functionalities.
        Installation: pip install pyAudioAnalysis

    scipy: Library for scientific and technical computing.
        Installation: pip install scipy

    numpy: Fundamental package for numerical computing with Python.
        Installation: pip install numpy

    matplotlib: Library for creating static, animated, and interactive visualizations in Python.
        Installation: pip install matplotlib

    sklearn (scikit-learn): Library for machine learning and data analysis.
        Installation: pip install scikit-learn
        
    pip install hmmlearn eyed3 imblearn plotly
    
    
"""