import subprocess

import vtnLibs.common_utils.LogUtils
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU
from vtnLibs.AudioFileUtils import AudioFileUtils

"""
    FFMPEG supported format:
        WAV (Waveform Audio File Format)
        MP3 (MPEG Audio Layer III)
        AAC (Advanced Audio Codec)
        FLAC (Free Lossless Audio Codec)
        OGG (Ogg Vorbis)
        M4A (MPEG-4 Audio Layer)
        WMA (Windows Media Audio)
        AIFF (Audio Interchange File Format)
"""
class AudioFormatConverter(LEC):
    FFMPEG_FORMAT_WAV = "wav"
    FFMPEG_FORMAT_MP3 = "mp3"
    FFMPEG_FORMAT_AAC = "aac"
    FFMPEG_FORMAT_FLAC = "flac"
    FFMPEG_FORMAT_OGG = "ogg"
    FFMPEG_FORMAT_M4A = "m4a"
    FFMPEG_FORMAT_WMA = "wma"
    FFMPEG_FORMAT_AIFF = "aiff"
    def __init__(self, output_root_folder):
        self.output_root_folder = output_root_folder

        self.audio_base_file_name = None
        self.audio_base_file_ext = None

        self.audio_input_filename = None
        self.audio_input_folder = None
        self.current_out_folder = None



    def convert_audio_file(self, audio_input_folder, audio_input_filename, output_format=FFMPEG_FORMAT_WAV, quiet_mode=True):
        self.audio_input_folder = audio_input_folder
        self.audio_input_filename = audio_input_filename
        self.setup_file_path_variables()

        full_input_filename = self.audio_input_folder + "/" + self.audio_input_filename
        output_file = self.current_out_folder + f"/{self.audio_base_file_name}.{output_format}"
        self.info(f"  ### processing audio file:{full_input_filename} => {output_file}")

        AudioFileUtils.convert_audio(input_file=full_input_filename, output_file=output_file, output_format=output_format, quiet_mode=quiet_mode)
        # try:
        #     subprocess.run(['ffmpeg', '-i', full_input_filename, '-f', output_format, output_file])
        #     print('Conversion successful!')
        # except subprocess.CalledProcessError as e:
        #     print(f'Error during conversion: {e}')

    def setup_file_path_variables(self) -> None:
        self.audio_base_file_name, self.audio_base_file_ext = ffU.splitBaseFilenameExtension(self.audio_input_filename)
        # self.current_out_folder = self.output_root_folder + "/" + self.audio_base_file_name
        self.current_out_folder = self.output_root_folder

        tmpFolder = ffU.createFolder(self.current_out_folder)

        self.rttm_file_path = self.current_out_folder + f"/spk_diarization_{self.audio_base_file_name}.rttm"
        self.debug(f"converted audio file saved ! {self.rttm_file_path}")

    def convert_files_in_folder(self, main_folder, include_subdirs=False):
        fileList = ffU.parse_folder_with_subfolders(folder_to_parse=main_folder, include_subdirs=include_subdirs)
        self.debug("================================================================================")
        self.debug(f"|          looking for file in folder: {main_folder}")
        self.debug("================================================================================")
        idx=0
        for full_path, relative_path in fileList:
            directory, base_filename, extension = ffU.split_file_path(full_path)
            audioFilename=base_filename+extension
            self.info(f" ### {idx:5}   ### processing audio file:{audioFilename} in folder {relative_path}")
            self.convert_audio_file(audio_input_folder=directory, audio_input_filename=audioFilename)

if __name__ == "__main__":

    vtnLibs.common_utils.LogUtils.configLogOutput()

    output_format = AudioFormatConverter.FFMPEG_FORMAT_WAV

    audio_filename = "2023_06_22_13_40_25.m4a"
    audio_files_folder = "../../../../resources/audio"
    output_folder = "../../../../out/audio/convertedAudio"


    # Convert 'm4a' to 'wav'
    module = AudioFormatConverter(output_folder)
    module.convert_audio_file(audio_files_folder, audio_filename, output_format, quiet_mode=False)
    #module.convert_files_in_folder(main_folder=audio_files_folder)