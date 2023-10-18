import wave
import numpy as np
from faster_whisper import WhisperModel

model_size = "large-v2"
# "cuda" or "cpu"
modelDevice = "cpu"
# "int8" | "int8_float16" | "float16"
modelComputeType = "int8"

# Load the RTTM file and extract segment information
def load_rttm(rttm_file):
    segments = []
    with open(rttm_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            start_time = float(parts[3])
            end_time = start_time + float(parts[4])
            speaker_label = parts[7]
            segments.append((start_time, end_time, speaker_label))
    return segments

# Segment the audio based on RTTM information
def segment_audio(audio_file, segments):
    audio = wave.open(audio_file, 'rb')
    sample_width = audio.getsampwidth()
    frame_rate = audio.getframerate()
    num_frames = audio.getnframes()
    total_duration = num_frames / frame_rate

    segmented_audio = {}
    for start_time, end_time, speaker_label in segments:
        start_frame = int(start_time * frame_rate)
        end_frame = int(end_time * frame_rate)
        audio.setpos(start_frame)
        segment_data = audio.readframes(end_frame - start_frame)
        segment_np = np.frombuffer(segment_data, dtype=np.int16)
        segmented_audio.setdefault(speaker_label, []).append((segment_np, frame_rate, start_time, end_time))

    return segmented_audio

def getModel(model_size, device, compute_type):
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

# Load the ASR model
def load_asr_model(model_path, model_size, device, compute_type):
    # Load your ASR model (replace with actual loading code)
    return getModel(model_size, device, compute_type)

# Transcribe a segment using the ASR model
def transcribe_segment(asr_model, segment_data):
    # Assuming your ASR model expects the segment data as input
    # Replace this with your actual ASR model inference
    transcription = asr_model.predict(np.array([segment_data]))  # Replace with your ASR model prediction
    return transcription

# Process each segment using the ASR model (dummy example)
def process_segments(segmented_audio):
    for speaker_label, segments in segmented_audio.items():
        #for segment, frame_rate in segments:  ## ??
        for segment_np, frame_rate, start_time, end_time in segments:
            # Here you would use your ASR model to transcribe each segment
            # Replace this with actual ASR model inference
            # Transcribe the segment using the ASR model
            transcription = transcribe_segment(asr_model, segment_np)
            #transcription = f"Transcription of {speaker_label} segment using ASR model."

            #print(transcription)
            print("Transcription for speaker [%.2fs -> %.2fs] %s: %s" % ( start_time, end_time, speaker_label,transcription))

if __name__ == "__main__":
    rttm_file = "../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.run2.NbrSpeakerGiven.rttm"
    audio_file = "../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"
    asr_model_path = "path/to/your/asr_model.h5"

    # Load the ASR model
    asr_model = load_asr_model(asr_model_path, model_size, modelDevice, modelComputeType)

    segments = load_rttm(rttm_file)
    segmented_audio = segment_audio(audio_file, segments)
    process_segments(segmented_audio)
