from vtnLibs.AudioFileUtils import AudioFileUtils as afU
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU
from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC

class AudioPlayBackSpeedModifier(LEC):
    def __init__(self, output_root_folder: str,speed_multiplier = 1):
        self.speed_multiplier = speed_multiplier

        self.output_root_folder = output_root_folder

        self.audio_base_file_name = None
        self.audio_base_file_ext = None

        self.audio_input_filename = None
        self.audio_input_folder = None
        self.current_out_folder = None

    def setup_file_path_variables(self) -> None:
        self.audio_base_file_name, self.audio_base_file_ext = ffU.splitBaseFilenameExtension(self.audio_input_filename)
        # self.current_out_folder = self.output_root_folder + "/" + self.audio_base_file_name
        self.current_out_folder = self.output_root_folder

        tmpFolder = ffU.createFolder(self.current_out_folder)



    """
    audio_in_path = '../../resources/audio/'
    audioFN = '2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a'
    audioFN = "2023_08_04_16_01_48_us622545Dierick.m4a"

    audio_in_path = '../../out/audio/2023_08_18_15_03_17_datasourceForBfEData2MyConnect/'
    audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.trailingFrom00:18:38.m4a"
    """
    def speedup_audio_file(self, audio_input_folder, audio_input_filename):
        self.audio_input_filename = audio_input_filename
        self.audio_input_folder = audio_input_folder
        self.setup_file_path_variables()
        ext = "wav"

        output_file = self.current_out_folder + f"/{self.audio_base_file_name}.speedup_{self.speed_multiplier}.{ext}"

        afU.speedUpAudioWithFFMPEG(self.audio_input_folder + "/" + self.audio_input_filename, output_file, self.speed_multiplier)
        # not working when using PyDub !!
        # afU.speedUpAudioWithPyDub(audio_file_path, output_file, speed_multiplier)

    def apply_for_files_in_folder(self, main_folder, include_subdirs=False):
        fileList = ffU.parse_folder_with_subfolders(folder_to_parse=main_folder, include_subdirs=include_subdirs)
        self.debug("================================================================================")
        self.debug(f"|          looking for file in folder: {main_folder}")
        self.debug("================================================================================")
        idx=0
        for full_path, relative_path in fileList:
            directory, base_filename, extension = ffU.split_file_path(full_path)
            audioFilename=base_filename+extension
            self.debug(f" ### {idx:5}   ### processing audio file:{audioFilename} in folder {relative_path}")
            self.speedup_audio_file(audio_input_folder=directory, audio_input_filename=audioFilename)

if __name__ == "__main__":
    None
    audio_filename = "2023_06_22_13_40_25.m4a"
    audio_files_folder = "../../../../resources/audio"
    output_folder = "../../../../out/audio/speedup"

    module = AudioPlayBackSpeedModifier(output_root_folder=output_folder, speed_multiplier=1)
    module.speedup_audio_file(audio_input_folder=audio_files_folder, audio_input_filename=audio_filename)