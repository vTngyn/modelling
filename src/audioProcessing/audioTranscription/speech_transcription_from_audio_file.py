"""
    prerequisite:
        those activities below are not required per say but it's good to have them
        -- execute : src/audioProcessing/audioFileOperations/audioFormatConversion/AudioFormatConverter.py
        -- execute: src/audioProcessing/speakerDiarization/extractSpeakerDiarization.py
"""

from vtnLibs.common_utils.LogUtils import configLogOutput
from vtnLibs.audio.speech_transcription.whisper_molde.whisper_model_transcription import WhisperModelTranscription
from vtnLibs.common_utils.CodingUtils import get_relative_file_path_from_script_folder
from vtnLibs.AudioFileUtils import AudioFileUtils

# audioFile = "../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"

pathLevelFromParentProjectFolder = get_relative_file_path_from_script_folder("",script_folder_deep=3)

audio_filename = "2023_08_29_14_34_14_povertySASSolutionGabPietOlivier.m4a"
audio_filename = "2023_08_23_15_14_38_courtierAlainVanderschr.AssurancePension.m4a"
audio_filename = "2023_08_25_10_16_48_emirRefitReghub_gabriel.m4a"
audio_files_folder = pathLevelFromParentProjectFolder + "resources/audio"

# audio_files_folder = "../../../out/audio/convertedAudio"
# output_folder = "../../../../out/audio/transcription"
output_folder = pathLevelFromParentProjectFolder+"out/audio/transcription"
allowed_extensions=[AudioFileUtils.FFMPEG_FORMAT_M4A]

configLogOutput()

module = WhisperModelTranscription(output_root_folder=output_folder, modelDevice=WhisperModelTranscription.MODEL_DEVICE_CPU)
module.process_files_in_folder(main_folder=audio_files_folder, include_subdirs=False, allowed_extensions=allowed_extensions)
# module.process_audio_file(audio_input_folder=audio_files_folder, audio_input_filename=audio_filename)
