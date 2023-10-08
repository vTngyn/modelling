#https://huggingface.co/pyannote/speaker-diarization-3.0

from faster_whisper import WhisperModel
import logging
import time
import os

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

vadFlag = True
min_silence_duration_ms=500

model_size = "large-v2"
# "cuda" or "cpu"
modelDevice = "cpu"  
# "int8" | "int8_float16" | "float16"
modelComputeType = "int8" 

#audio_file_path = 'resampled_audio.wav'
"""
audio_in_path = '../resources/audio/'
audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a"
audioFN = "2023_08_04_16_01_48_us622545Dierick.m4a"

audio_in_path = '../out/audio/2023_08_18_15_03_17_datasourceForBfEData2MyConnect.trailingFrom00:18:38/'
audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.trailingFrom00:18:38.speedup1.5..m4a"
"""
audio_in_path = "../out/audio/2023_08_04_16_01_48_us622545Dierick/"
audioFN = "2023_08_04_16_01_48_us622545Dierick.speedup2.0..m4a"

audio_file_path = audio_in_path + '/' + audioFN
modelFrom = "LocalGoogleWhisper{model_size}"
#audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"

outputFolder = "../out/audio/"

model = None

def create_folder_if_not_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    else:
        print(f"Folder '{folder_name}' already exists.")


def get_base_filename_without_extension(full_path):
    # Get the base filename from the full path
    base_filename = os.path.basename(full_path)

    # Split the base filename into filename and extension
    filename, extension = os.path.splitext(base_filename)

    return filename

baseTransFilename = get_base_filename_without_extension(audio_file_path)
print(baseTransFilename)
workingOutFolder = outputFolder+baseTransFilename
print(workingOutFolder)
transOutputFolder = create_folder_if_not_exists(workingOutFolder)

transcription_file_path = workingOutFolder + f"/transcription_{baseTransFilename}.txt"
print(f"transcription save to file: {transcription_file_path}")
def getModel(device, compute_type):
    # Run on GPU with FP16
    #model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    #model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    #model = WhisperModel(model_size, device="cpu", compute_type="int8")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    #to forces the model to predict in English under the task of speech recognition:
    #model.config.forced_decoder_ids = WhisperProcessor.get_decoder_prompt_ids(language="english", task="transcribe")

    return model

job_start_time = time.time()  # Start timer

model = getModel(modelDevice, modelComputeType)

def getSegmentsMethod1(audio_file_path):
    segments, info = model.transcribe(audio_file_path, beam_size=5)
    return segments, info

def getSegmentsMethod2(audio_file_path,min_silence_duration_ms=500):
    segments, info = model.transcribe(
        audio_file_path,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms),
    )
    return segments, info

segments = None
info = None
if vadFlag:
    segments, info = getSegmentsMethod2(audio_file_path)
else:
    segments, info = getSegmentsMethod1(audio_file_path)

with open(transcription_file_path, 'w') as file:
    file.write("| ==================================================================================================================================\n")
    file.write("NFO:")
    file.write("\t - audio file = '%s' \n" % (audio_file_path))
    file.write("\t - Detected language '%s' with probability %f \n" % (info.language, info.language_probability))
    file.write("| ==================================================================================================================================\n")

idx=0
for segment in segments:
    start_time = time.time()  # Start timer
    transcription = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
    with open(transcription_file_path, 'a') as file:
        #print(transcription)
        # Append the transcription to the output file
        file.write(transcription + '\n')
    end_time = time.time()  # End timer
    elapsed_time = end_time - start_time
    print(f"Segment {idx}: tokenize completed => {elapsed_time:.2f}s: {transcription}")
    idx+=1

job_end_time = time.time()  # Start timer
job_elapsed_time = job_end_time - job_start_time
print(f"Transcription JOB completed in {job_elapsed_time:.2f} seconds")


