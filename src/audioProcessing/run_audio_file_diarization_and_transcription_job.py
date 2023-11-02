from audioFileOperations.audioFormatConversion.AudioFormatConverter import run_audio_conversion_job
from audioTranscription.speech_transcription_from_audio_file import run_audio_file_transcription_job
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU
from vtnLibs.common_utils.LogUtils import configLogOutput
from src.audioProcessing.speakerDiarization.extractSpeakerDiarization import run_audio_file_diarization_job
import logging, traceback

# starting audio conversion
audio_filename = "2023_06_22_13_40_25.m4a"
audio_filename = None
project_folder_name="testTensorFlowM1"

configLogOutput()

try:

    this_script_file_path_elements = ffU.get_caller_location_elements()
    # print(this_script_file_path_elements)
    abs_path = this_script_file_path_elements[0]
    # print(abs_path)

    last_char_index = abs_path.rfind(project_folder_name) + len(project_folder_name) +1
    project_abs_base_path = abs_path[:last_char_index]
    print(f"project_abs_base_path0={project_abs_base_path}")

    # split_abs_path_elem = abs_path.split('/')
    # found_idx = None
    # project_abs_base_path = None
    # for i, e in enumerate(split_abs_path_elem):
    #     if e == project_folder_name:
    #         found_idx = i
    #         break
    #
    # if found_idx:
    #     project_abs_base_path = "/".join(split_abs_path_elem[:found_idx+1])
    # print(f"project_abs_base_path={project_abs_base_path}")
    # print(this_script_file_path_elements)

    try:
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        logging.debug("Starting transcription ")
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        ret=run_audio_file_transcription_job(project_base_folder_path=project_abs_base_path)
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        logging.debug("Starting audio convertion ")
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        ret1=run_audio_conversion_job(project_base_folder_path=project_abs_base_path, audio_filename=audio_filename)
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        logging.debug("Starting diarization ")
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
        run_audio_file_diarization_job(project_base_folder_path=project_abs_base_path)
        logging.debug(" #############################################################################################################################################################################################################################################################################################################################")
    except Exception as e:
        logging.error(e)
except Exception as e:
    # Log the exception along with the full stack trace
    logging.error("An error occurred: %s", str(e))
    logging.error("Stack trace:\n%s", traceback.format_exc())

