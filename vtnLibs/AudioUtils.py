from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import numpy as np

class AudioUtils(LEC):
    @staticmethod
    def extract_audio_segment(audio_file, start_time, end_time):
        """
        Play an audio segment using pydub's playback functionality.
        """
        # Load the original audio file
        audio = AudioSegment.from_file(audio_file)

        # Extract the specified segment
        segment = audio[start_time * 1000:end_time * 1000]
        return segment

    # Play the audio segment
    def play_audio_segment(segment, device_id=None):
        if device_id:
            # play(segment, device=device)
            raw_audio_data = segment.raw_data
            # sd.play(raw_audio_data, samplerate=segment.frame_rate, device=device_id)

            # Convert segment to raw PCM data
            samples = np.array(segment.get_array_of_samples())

            # Play the audio segment using sounddevice
            sd.play(samples, samplerate=segment.frame_rate, device=device_id)
            sd.wait()  # Wait for playback to finish
