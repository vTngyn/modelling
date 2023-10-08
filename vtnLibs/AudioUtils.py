from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from pydub import AudioSegment
from pydub.playback import play

class AudioUtils(LEC):
    @staticmethod
    def play_audio_segment(self, audio_file, start_time, end_time):
        """
        Play an audio segment using pydub's playback functionality.
        """
        # Load the original audio file
        audio = AudioSegment.from_file(audio_file)

        # Extract the specified segment
        segment = audio[start_time * 1000:end_time * 1000]

        # Play the audio segment
        play(segment)
