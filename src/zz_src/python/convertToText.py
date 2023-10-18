from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf
import torch

import ffmpeg
import os

import subprocess
import librosa

import traceback
import wave
import time


# C:\repo\dev\pythonProjects\testVSCode\audio2text\.venv\lib\site-packages\transformers\models\wav2vec2\tokenization_wav2vec2.py:792: FutureWarning: The class `Wav2Vec2Tokenizer` is deprecated and will be removed in version 5 of Transformers. Please use `Wav2Vec2Processor` or `Wav2Vec2CTCTokenizer` instead.

convertAudioToWav = False
resampledAudio = False
language_code = 'en'


def is_ffmpeg_installed():
    try:
        # Run the ffmpeg command to get the version
        result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False  # ffmpeg executable not found


def convert_m4a_to_wav(input_path, output_path):
    # Run ffmpeg to convert M4A to WAV
    ffmpeg.input(input_path).output(output_path).run()

def transcribe_audio(audio_path, convertAudioToWav, resampledAudio, output_transcription_file):
    job_start_time = time.time()  # Start timer
    # Load pre-trained ASR model and tokenizer
    
    model_name = "facebook/wav2vec2-base"
    model_name = "facebook/wav2vec2-base-960h"
    #model_name = f"facebook/wav2vec2-{language_code}"

    #tokenizer = Wav2Vec2Tokenizer.from_pretrained(model_name)
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name)


    
    target_sample_rate = 16000

    # Resample the audio
    resampled_audio_path = "resampled_audio.wav"
    wav_audio_path = "converted_audio.wav"

    if resampledAudio:
        if (convertAudioToWav):
            print("Converting audio to WAV...")
            convert_m4a_to_wav(audio_path, wav_audio_path)
        else:
            print("Reading existing audio wav file [converted_audio.wav]...")
        # Load audio file and convert to mono if needed
        audio, original_sample_rate = sf.read(wav_audio_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        print("Audio Shape:", audio.shape)
        print("orig Sample Rate:", original_sample_rate)


        audio_resampled = librosa.core.resample(y=audio, orig_sr=original_sample_rate, target_sr=target_sample_rate)
        # Save the resampled audio
        sf.write(resampled_audio_path, audio_resampled, target_sample_rate)
        print("Resampled Audio Shape:", audio_resampled.shape)
        print("Resampled Audio saved at:", resampled_audio_path)
        print("target Sample Rate:", target_sample_rate)
    else:
        audio_resampled, target_sample_rate = sf.read(resampled_audio_path)
        #audio_resampled = wave.open(resampled_audio_path, 'r')
        #frame_rate = audio_resampled.getframerate()
        #print("save target Sample Rate:", frame_rate)
        print("Resampled Audio Shape:", audio_resampled.shape)
        print("target Sample Rate:", target_sample_rate)

    print("Resampled Audio Values (first 10):", audio_resampled[:10])


    try:
        # Tokenize the audio and transcribe
        #inputs = tokenizer(audio, return_tensors="pt", padding="longest", truncation=True)



        # Tokenize the audio and transcribe

        # Tokenize the audio and transcribe
        #inputs = processor(audio, return_tensors="pt", padding=True)
        #inputs = processor(audio, sampling_rate=original_sample_rate, return_tensors="pt", padding=True, verbose=True)
        #inputs = processor(audio_resampled, sampling_rate=target_sample_rate, return_tensors="pt", padding=True, verbose=True)
        #print("Input Shape:", inputs.input_values.shape)
        #print("Input Values:", inputs.input_values)
        #print("Tokens Shape:", inputs['input_values'].shape)
        #print("Tokens Length:", inputs['input_values'].shape[1])
        #print("inputs['input_values'].shape[1]:", inputs['input_values'].shape[1])
        #print("Input Values:", inputs.input_values)


        # Truncate if the sequence is too long for the model
        #max_length = 512  # You can adjust this based on the model's maximum length
        #if inputs['input_values'].shape[1] > max_length:
        #    inputs['input_values'] = inputs['input_values'][:, :max_length]

        # Split the audio into chunks of 30 seconds (you can modify the duration)
        chunk_size = 30 * target_sample_rate  # 30 seconds
        #chunks = [audio_resampled[i:i + chunk_size] for i in range(0, len(audio_resampled), chunk_size)]
        chunks = [audio_resampled[i:i + chunk_size] for i in range(0, len(audio_resampled), chunk_size)]

        print(f"total #chunks:{len(chunks)}")

        transcriptions = []

        with open(output_transcription_file, 'w') as transcript_file:
            for idx, chunk in enumerate(chunks):
            #for chunk in chunks:
                # Tokenize the audio chunk and transcribe
                inputs = processor(chunk, sampling_rate=target_sample_rate, return_tensors="pt", padding=True, verbose=True)
                start_time = time.time()  # Start timer

                with torch.no_grad():
                    logits = model(input_values=inputs.input_values).logits
                #print("idx:", idx)
                #print("Logits Shape:", logits.shape)
                #print("Logits Values:", logits)

                end_time = time.time()  # End timer
                elapsed_time = end_time - start_time
                print(f"Chunk {idx+1}: takenize completed => {elapsed_time:.2f} seconds")

                # Decode the logits to obtain the transcriptions
                predicted_ids = torch.argmax(logits, dim=-1)

                #transcription = tokenizer.batch_decode(predicted_ids)[0]
                transcription = processor.batch_decode(predicted_ids)[0]

                end_time = time.time()  # End timer
                elapsed_time = end_time - start_time
                print(f"Chunk {idx+1}: trasncription completed => {elapsed_time:.2f} seconds")

                # Append the transcription to the text file
                transcript_file.write(f"Chunk {idx+1}:\n")
                transcript_file.write(transcription + "\n\n")


                end_time = time.time()  # End timer
                elapsed_time = end_time - start_time
                print(f"Chunk {idx+1}: saving completed => {elapsed_time:.2f} seconds")
                #transcriptions.append(transcription)

        # return ' '.join(transcriptions)


        #return transcription
    except Exception as e:
        traceback.print_exc()  # Print the detailed error traceback
        print("Error during transcription:", e)
    
    job_end_time = time.time()  # Start timer
    job_elapsed_time = job_end_time - job_start_time
    print(f"Transcription JOB completed in {job_elapsed_time:.2f} seconds")
    #return transcription

if __name__ == "__main__":
    # Check if ffmpeg is installed
    if is_ffmpeg_installed():
        print("ffmpeg is installed.")
    else:
        print("ffmpeg is not installed or not in the system's PATH.")

    if convertAudioToWav:
        print("to wav audio conversion will occurs")
    else:
        print("reuse existing to wav audio converted file")


    # Replace with the path to your audio file
    audio_file_path = "../resources/2023_08_04_16_01_48_us622545Dierick.m4a"
    audio_file_name = os.path.split(audio_file_path)[1]
    audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resources\2023_08_04_16_01_48_us622545Dierick.m4a"

    transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_file_name}_transcription.txt"

    # Transcribe the audio file
    transcription = transcribe_audio(audio_file_path, convertAudioToWav, resampledAudio, transcription_file_path)
   # if transcription:
   #     print("Transcription:", transcription)
   # else:
   #     print("Transcription failed.")

    #print("Transcription:", transcription)

    # Save the transcription to a text file
    #with open(transcription_file_path, "w") as file:
    #    file.write(transcription)

    print("Transcription saved to:", transcription_file_path)
   