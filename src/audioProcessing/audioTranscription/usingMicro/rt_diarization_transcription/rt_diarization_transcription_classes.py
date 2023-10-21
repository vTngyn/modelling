import os
import sys
import numpy as np
import whisper_timestamped as whisper
from pyannote.core import Segment
from contextlib import contextmanager


@contextmanager
def suppress_stdout():
    # Auxiliary function to suppress Whisper logs (it is quite verbose)
    # All credit goes to: https://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

class WhisperTranscriber:
    def __init__(self, model="small", device=None):
        self.model = whisper.load_model(model, device=device)
        self._buffer = ""

    def transcribe(self, waveform):
        """Transcribe audio using Whisper"""
        # Pad/trim audio to fit 30 seconds as required by Whisper
        audio = waveform.data.astype("float32").reshape(-1)
        audio = whisper.pad_or_trim(audio)

        # Transcribe the given audio while suppressing logs
        with suppress_stdout():
            transcription = whisper.transcribe(
                self.model,
                audio,
                # We use past transcriptions to condition the model
                initial_prompt=self._buffer,
                verbose=True  # to avoid progress bar
            )

        return transcription

    def identify_speakers(self, transcription, diarization, time_shift):
        """Iterate over transcription segments to assign speakers"""
        speaker_captions = []
        for segment in transcription["segments"]:

            # Crop diarization to the segment timestamps
            start = time_shift + segment["words"][0]["start"]
            end = time_shift + segment["words"][-1]["end"]
            dia = diarization.crop(Segment(start, end))

            # Assign a speaker to the segment based on diarization
            speakers = dia.labels()
            num_speakers = len(speakers)
            if num_speakers == 0:
                # No speakers were detected
                caption = (-1, segment["text"])
            elif num_speakers == 1:
                # Only one speaker is active in this segment
                spk_id = int(speakers[0].split("speaker")[1])
                caption = (spk_id, segment["text"])
            else:
                # Multiple speakers, select the one that speaks the most
                max_speaker = int(np.argmax([
                    dia.label_duration(spk) for spk in speakers
                ]))
                caption = (max_speaker, segment["text"])
            speaker_captions.append(caption)

        return speaker_captions

    def __call__(self, diarization, waveform):
        # Step 1: Transcribe
        transcription = self.transcribe(waveform)
        # Update transcription buffer
        self._buffer += transcription["text"]
        # The audio may not be the beginning of the conversation
        time_shift = waveform.sliding_window.start
        # Step 2: Assign speakers
        speaker_transcriptions = self.identify_speakers(transcription, diarization, time_shift)
        return speaker_transcriptions