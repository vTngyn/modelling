#https://betterprogramming.pub/color-your-captions-streamlining-live-transcriptions-with-diart-and-openais-whisper-6203350234ef
#whisper-timestamped: https://github.com/linto-ai/whisper-timestamped#first-installation
# diart: https://github.com/juanmc2005/StreamingSpeakerDiarization#installation
# reactive programming: https://rxpy.readthedocs.io/en/latest/get_started.html
# optuna: https://optuna.readthedocs.io/en/stable/index.html
# pyannote: http://pyannote.github.io/pyannote-core/structure.html
#source code: https://gist.github.com/juanmc2005/ed6413e697e176cb36a149d8c40a3a5b
# https://github.com/openai/whisper#available-models-and-languages


import logging
import traceback
import diart.operators as dops
import rich
import rx.operators as ops
from diart import OnlineSpeakerDiarization, PipelineConfig
from diart.sources import MicrophoneAudioSource
from rt_diarization_transcription_classes import WhisperTranscriber

import whisper_timestamped as whisper

# audio = whisper.load_audio("AUDIO.wav")
#
# model = whisper.load_model("tiny", device="cpu")
# model = whisper.load_model("NbAiLab/whisper-large-v2-nob", device="cpu")

#
# result = whisper.transcribe(model, audio, language="fr", plot_word_alignment=True)
# results = whisper_timestamped.transcribe(model, audio, beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), detect_disfluencies=True)
# import json
# print(json.dumps(result, indent = 2, ensure_ascii = False))

# Suppress whisper-timestamped warnings for a clean output
logging.getLogger("whisper_timestamped").setLevel(logging.ERROR)

# If you have a GPU, you can also set device=torch.device("cuda")
config = PipelineConfig(
    duration=5,
    step=0.5,
    latency="min",
    tau_active=0.5,
    rho_update=0.1,
    delta_new=0.57
)
dia = OnlineSpeakerDiarization(config)
source = MicrophoneAudioSource(config.sample_rate)

asr = WhisperTranscriber(model="small")

import numpy as np
from pyannote.core import Annotation, SlidingWindowFeature, SlidingWindow

def concat(chunks, collar=0.05):
    """
    Concatenate predictions and audio
    given a list of `(diarization, waveform)` pairs
    and merge contiguous single-speaker regions
    with pauses shorter than `collar` seconds.
    """
    first_annotation = chunks[0][0]
    first_waveform = chunks[0][1]
    annotation = Annotation(uri=first_annotation.uri)
    data = []
    for ann, wav in chunks:
        annotation.update(ann)
        data.append(wav.data)
    annotation = annotation.support(collar)
    window = SlidingWindow(
        first_waveform.sliding_window.duration,
        first_waveform.sliding_window.step,
        first_waveform.sliding_window.start,
    )
    data = np.concatenate(data, axis=0)
    return annotation, SlidingWindowFeature(data, window)

def colorize_transcription(transcription):
    """
    Unify a speaker-aware transcription represented as
    a list of `(speaker: int, text: str)` pairs
    into a single text colored by speakers.
    """
    colors = 2 * [
        "bright_red", "bright_blue", "bright_green", "orange3", "deep_pink1",
        "yellow2", "magenta", "cyan", "bright_magenta", "dodger_blue2"
    ]
    result = []
    for speaker, text in transcription:
        if speaker == -1:
            # No speakerfound for this text, use default terminal color
            result.append(text)
        else:
            result.append(f"[{colors[speaker]}]{text}")
    return "\n".join(result)

transcription_duration = 2
batch_size = int(transcription_duration // config.step)
source.stream.pipe(
    dops.rearrange_audio_stream(
        config.duration, config.step, config.sample_rate
    ),
    ops.buffer_with_count(count=batch_size),
    ops.map(dia),
    ops.map(concat),
    ops.filter(lambda ann_wav: ann_wav[0].get_timeline().duration() > 0),
    ops.starmap(asr),
    ops.map(colorize_transcription),
).subscribe(on_next=rich.print, on_error=lambda _: traceback.print_exc())


import traceback
import rich
import rx.operators as ops
import diart.operators as dops

# Split the stream into 2s chunks for transcription
transcription_duration = 2
# Apply models in batches for better efficiency
batch_size = int(transcription_duration // config.step)

# Chain of operations to apply on the stream of microphone audio
source.stream.pipe(
    # Format audio stream to sliding windows of 5s with a step of 500ms
    dops.rearrange_audio_stream(
        config.duration, config.step, config.sample_rate
    ),
    # Wait until a batch is full
    # The output is a list of audio chunks
    ops.buffer_with_count(count=batch_size),
    # Obtain diarization prediction
    # The output is a list of pairs `(diarization, audio chunk)`
    ops.map(dia),
    # Concatenate 500ms predictions/chunks to form a single 2s chunk
    ops.map(concat),
    # Ignore this chunk if it does not contain speech
    ops.filter(lambda ann_wav: ann_wav[0].get_timeline().duration() > 0),
    # Obtain speaker-aware transcriptions
    # The output is a list of pairs `(speaker: int, caption: str)`
    ops.starmap(asr),
    # Color transcriptions according to the speaker
    # The output is plain text with color references for rich
    ops.map(colorize_transcription),
).subscribe(
    on_next=rich.print,  # print colored text
    on_error=lambda _: traceback.print_exc()  # print stacktrace if error
)

import numpy as np
from pyannote.core import Annotation, SlidingWindowFeature, SlidingWindow

def concat(chunks, collar=0.05):
    """
    Concatenate predictions and audio
    given a list of `(diarization, waveform)` pairs
    and merge contiguous single-speaker regions
    with pauses shorter than `collar` seconds.
    """
    first_annotation = chunks[0][0]
    first_waveform = chunks[0][1]
    annotation = Annotation(uri=first_annotation.uri)
    data = []
    for ann, wav in chunks:
        annotation.update(ann)
        data.append(wav.data)
    annotation = annotation.support(collar)
    window = SlidingWindow(
        first_waveform.sliding_window.duration,
        first_waveform.sliding_window.step,
        first_waveform.sliding_window.start,
    )
    data = np.concatenate(data, axis=0)
    return annotation, SlidingWindowFeature(data, window)

def colorize_transcription(transcription):
    """
    Unify a speaker-aware transcription represented as
    a list of `(speaker: int, text: str)` pairs
    into a single text colored by speakers.
    """
    colors = 2 * [
        "bright_red", "bright_blue", "bright_green", "orange3", "deep_pink1",
        "yellow2", "magenta", "cyan", "bright_magenta", "dodger_blue2"
    ]
    result = []
    for speaker, text in transcription:
        if speaker == -1:
            # No speakerfound for this text, use default terminal color
            result.append(text)
        else:
            result.append(f"[{colors[speaker]}]{text}")
    return "\n".join(result)


print("Listening...")
source.read()
