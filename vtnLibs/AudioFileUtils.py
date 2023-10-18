import subprocess
from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec
from pydub import AudioSegment
import subprocess
import ffmpeg
import re

class AudioFileUtils(lec):
    FFMPEG_FORMAT_WAV = ".wav"
    FFMPEG_FORMAT_MP3 = ".mp3"
    FFMPEG_FORMAT_AAC = ".aac"
    FFMPEG_FORMAT_FLAC = ".flac"
    FFMPEG_FORMAT_OGG = ".ogg"
    FFMPEG_FORMAT_M4A = ".m4a"
    FFMPEG_FORMAT_WMA = ".wma"
    FFMPEG_FORMAT_AIFF = ".aiff"
    FFMPEG_ALL_FORMAT = [
        FFMPEG_FORMAT_WAV,
        FFMPEG_FORMAT_MP3,
        FFMPEG_FORMAT_AAC,
        FFMPEG_FORMAT_FLAC,
        FFMPEG_FORMAT_OGG,
        FFMPEG_FORMAT_M4A,
        FFMPEG_FORMAT_WMA,
        FFMPEG_FORMAT_AIFF,
    ]

    def __init__(self):
        None


    @staticmethod
    def speedUpAudioWithFFMPEG(input_file, output_file, speed_multiplier):
        # Run FFmpeg command to speed up the audio
        command = [
            "ffmpeg",
            "-i", input_file,
            "-filter:a", f"atempo={speed_multiplier}",
            output_file
        ]
        subprocess.run(command)

    @staticmethod
    def speedUpAudioWithPyDub(audio_path, output_path, speed_multiplier):
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)

        # Speed up the audio
        sped_up_audio = audio.speedup(playback_speed=speed_multiplier)

        # Export the sped up audio
        sped_up_audio.export(output_path, format="wav")

        return output_path

    @staticmethod
    def copyRemainingAudioWithFFMPEG(input_file, output_file, start_time = None, end_time = None):
        # Run FFmpeg command to copy the remaining part of the audio
        command = None
        if (end_time is None):
            command = [
                "ffmpeg",
                "-ss", str(start_time),  # Start time in HH:MM:SS format or seconds
                "-i", input_file,
                "-c", "copy",
                output_file
            ]
        elif (start_time is None):
            command = [
                "ffmpeg",
                "-ss", str(start_time),  # Start time in HH:MM:SS format or seconds
                "-to", str(end_time),  # End time in HH:MM:SS format or seconds
                "-i", input_file,
                "-c", "copy",
                output_file
            ]
        else:
            command = [
                "ffmpeg",
                "-ss", str(start_time),  # Start time in HH:MM:SS format or seconds
                "-to", str(end_time),  # End time in HH:MM:SS format or seconds
                "-i", input_file,
                "-c", "copy",
                output_file
            ]
        subprocess.run(command)

    @staticmethod
    def mp3_to_wav(cls,audio_file_path):
        sound = AudioSegment.from_mp3(audio_file_path)
        audio_file_path = audio_file_path.split('.')[0] + '.wav'
        sound.export(audio_file_path, format="wav")
        return audio_file_path

    @staticmethod
    def convert_audio(input_file, output_file, output_format=FFMPEG_FORMAT_WAV, quiet_mode = False):
        try:
            if quiet_mode:
                command = ['ffmpeg', '-y', '-v', 'quiet', '-i', input_file, '-f', output_format, output_file]
            else:
                command = ['ffmpeg', '-i', input_file, '-f', output_format, output_file]
            # subprocess.run(['ffmpeg', '-i', input_file, '-f', output_format, output_file])
            subprocess.run(command, check=True)
            print('Conversion successful!')
        except subprocess.CalledProcessError as e:
            print(f'Error during conversion: {e}')

    @staticmethod
    def get_audio_length_ffmpeg(audio_file):
        try:
            info = ffmpeg.probe(audio_file, show_entries="format")
            duration = float(info['format']['duration'])
            return duration
        except ffmpeg.Error as e:
            print(f"An error occurred: {e.stderr}")

    @staticmethod
    def get_audio_length_subprocess(audio_file):
        try:
            result = subprocess.run(['ffmpeg', '-i', audio_file], capture_output=True, text=True)
            output = result.stderr
            duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", output)
            if duration_match:
                duration = duration_match.group(1)
                return duration
            else:
                print("Duration not found in ffmpeg output.")
                return None
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr}")
