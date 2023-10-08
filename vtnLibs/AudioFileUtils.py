import subprocess
from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec
from pydub import AudioSegment
import subprocess

class AudioFileUtils(lec):
    FFMPEG_FORMAT_WAV = "wav"
    FFMPEG_FORMAT_MP3 = "mp3"
    FFMPEG_FORMAT_AAC = "aac"
    FFMPEG_FORMAT_FLAC = "flac"
    FFMPEG_FORMAT_OGG = "ogg"
    FFMPEG_FORMAT_M4A = "m4a"
    FFMPEG_FORMAT_WMA = "wma"
    FFMPEG_FORMAT_AIFF = "aiff"

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
