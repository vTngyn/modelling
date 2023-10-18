import os
import wave
import math
import speech_recognition as sr

audio_file_path = 'resampled_audio.wav'
#audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"
transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_file_path}_transcriptionGoogleWebAPI.txt"


def split_audio_into_chunks(audio_file_path, chunk_duration=10):
    audio = wave.open(audio_file_path, "rb")

    chunk_size = int(chunk_duration * audio.getframerate())
    total_frames = audio.getnframes()
    num_chunks = math.ceil(total_frames / chunk_size)

    chunks = []
    for i in range(num_chunks):
        start_frame = i * chunk_size
        end_frame = min(start_frame + chunk_size, total_frames)
        audio.setpos(start_frame)
        chunk_data = audio.readframes(end_frame - start_frame)
        chunks.append(chunk_data)

    audio.close()
    return chunks

def transcribe_audio_streaming(audio_file_path, output_path, chunk_duration=10):
    recognizer = sr.Recognizer()

    # Split the audio into chunks
    audio_chunks = split_audio_into_chunks(audio_file_path, chunk_duration)

    # Perform transcription for each chunk
    with open(output_path, "w") as transcription_file:
        for i, chunk in enumerate(audio_chunks):
            with sr.AudioFile(chunk) as source:
                try:
                    audio_data = recognizer.record(source)
                    transcription = recognizer.recognize_google(audio_data)
                    transcription_file.write(f"Chunk {i+1}:\n{transcription}\n\n")
                except sr.RequestError as e:
                    print(f"Could not request results for chunk {i+1}; {str(e)}")
                except sr.UnknownValueError:
                    print(f"Google Web Speech API could not understand chunk {i+1}")

    print("Transcription saved to:", output_path)

# Replace with your actual paths

transcribe_audio_streaming(audio_file_path, transcription_file_path)
