from faster_whisper import WhisperModel
import logging
import time

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

model_size = "large-v2"
# "cuda" or "cpu"
modelDevice = "cpu"  
# "int8" | "int8_float16" | "float16"
modelComputeType = "int8" 

audio_file_path = 'resampled_audio.wav'
modelFrom = "LocalGoogleWhisper{model_size}"
#audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"
transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_file_path}_transcription{modelFrom}.txt"

model = None


def getModel(device, compute_type):
    # Run on GPU with FP16
    #model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    #model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    # or run on CPU with INT8
    #model = WhisperModel(model_size, device="cpu", compute_type="int8")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    return model

job_start_time = time.time()  # Start timer

model = getModel(modelDevice, modelComputeType)

def getSegmentsMethod1(audio_file_path):
    segments, info = model.transcribe(audio_file_path, beam_size=5)
    return segments, info

def getSegmentsMethod2(audio_file_path):
    segments, info = model.transcribe(
        "audio.mp3",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    return segments, info

segments, info = getSegmentsMethod1(audio_file_path)
with open(output_file, 'a') as file:
    file.write("| ==================================================================================================================================\n")
    file.write("NFO:")
    file.write("\t - audio file = '%s' with probability %f \n" % (audio_file_path))
    file.write("\t - Detected language '%s' with probability %f \n" % (info.language, info.language_probability))
    file.write("| ==================================================================================================================================\n")
    for segment in segments:
        start_time = time.time()  # Start timer
        transcription = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
        print(transcription)
        # Append the transcription to the output file
        file.write(transcription + '\n')
        end_time = time.time()  # End timer
        elapsed_time = end_time - start_time
        print(f"Chunk {idx+1}: takenize completed => {elapsed_time:.2f} seconds")

job_end_time = time.time()  # Start timer
job_elapsed_time = job_end_time - job_start_time
print(f"Transcription JOB completed in {job_elapsed_time:.2f} seconds")


