#https://huggingface.co/pyannote/speaker-diarization-3.0
# from . import configLogOutput

import traceback
from vtnLibs.common_utils.abstract_classes.TimeMonitoring import TimeMonitoring as TMON
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU
from vtnLibs.common_utils.DateTimeUtils import DateUtils as dtU
from vtnLibs.common_utils.DateTimeUtils import DateUtils as logU
from vtnLibs.common_utils.LogUtils import configLogOutput
from vtnLibs.AudioFileUtils import AudioFileUtils as AudFU
from faster_whisper import WhisperModel
import logging
import time


logging.basicConfig(level=logging.DEBUG)
#logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

class WhisperModelTranscription(TMON):
    MODEL_SIZE_LARGEV2 = "large-v2"
    # "cuda" or "cpu"
    MODEL_DEVICE_CPU = "cpu"
    MODEL_DEVICE_CUDA = "cuda"
    MODEL_DEVICE_MPS = "mps" #for M1 chipset: Metal Performance Shaders
    # "int8" | "int8_float16" | "float16"
    MODEL_COMPUTE_TYPE_INT8 = "int8"
    MODEL_COMPUTE_TYPE_INT8FLOAT16 = "int8_float16"
    MODEL_COMPUTE_TYPE_FLOAT16 = "float16"
    def __init__(self,output_root_folder,vadFlag = True, min_silence_duration_ms=500, model_size = MODEL_SIZE_LARGEV2, modelDevice = MODEL_DEVICE_CPU, modelComputeType = MODEL_COMPUTE_TYPE_INT8,num_workers=1, cpu_threads=0):
        self.model = None
        self.vadFlag = vadFlag
        self.min_silence_duration_ms=min_silence_duration_ms

        self.model_size = model_size
        self.modelDevice = modelDevice
        self.modelComputeType = modelComputeType
        self.num_workers=num_workers
        self.cpu_threads=cpu_threads


        self.audio_base_file_name = None
        self.audio_base_file_ext = None

        self.audio_input_filename = None
        self.audio_input_folder = None
        self.output_root_folder = output_root_folder
        self.current_out_folder = None
        self.full_input_filename = None
        self.transcription_file = None

        self.inializeModel()
        self.set_timer_parameters()


    def setup_file_path_variables(self) -> None:
        self.audio_base_file_name, self.audio_base_file_ext = ffU.splitBaseFilenameExtension(self.audio_input_filename)
        # self.current_out_folder = self.output_root_folder + "/" + self.audio_base_file_name
        self.current_out_folder = self.output_root_folder

        tmpFolder = ffU.createFolder(self.current_out_folder)

        # self.rttm_file_path = self.current_out_folder + f"/spk_diarization_{self.audio_base_file_name}.rttm"
        # self.debug(f"Speech transcription save to file: {self.rttm_file_path}")

    def process_files_in_folder(self, main_folder, include_subdirs=False, allowed_extensions=None):
        errNbr=0
        fileList = ffU.parse_folder_with_subfolders(folder_to_parse=main_folder, include_subdirs=include_subdirs, allowed_extensions=allowed_extensions)
        self.startTimer()
        self.debug("================================================================================")
        self.debug(f"|          looking for file in folder: {main_folder}")
        self.debug("================================================================================")
        idx=0
        for full_path, relative_path in fileList:
            directory, base_filename, extension = ffU.split_file_path(full_path)
            abs_file_path = ffU.get_file_absolute_path_after_check(full_path)
            audioFilename=base_filename+extension
            filesize = ffU.get_file_size(abs_file_path)
            audio_length = AudFU.get_audio_length_ffmpeg(full_path)
            self.debug(f" ### {idx:5}   ### processing audio file:{audioFilename} [size={filesize['mb']:.2f}MB/duration={audio_length}] in folder {directory}")
            try:
                self.process_audio_file(audio_input_folder=directory, audio_input_filename=audioFilename)
            except Exception as e:
                errNbr+=1
                self.error(f"An error occured on file {full_path}",exception=e)

            idx += 1
        self.stopTimer()
        self.show_total_processing_time()
        return errNbr

    def __get_audio_file_size_length__(self):
        audio_length = AudFU.get_audio_length_ffmpeg(self.audio_file_path)
        filesize = ffU.get_file_size(self.audio_file_path)
        return filesize, audio_length

    def process_audio_file(self, audio_input_folder: str, audio_input_filename: str, output_file_ext: str="txt"):
        errNbr = 0
        self.audio_input_folder = audio_input_folder
        self.audio_input_filename = audio_input_filename
        self.setup_file_path_variables()

        self.full_input_filename = self.audio_input_folder + "/" + self.audio_input_filename
        self.transcription_file = self.current_out_folder + f"/transcript_{self.audio_base_file_name}.{output_file_ext}"
        self.info(f"  ### processing audio file:{self.full_input_filename} => {self.transcription_file}")

        self.start_intermediate_timer()
        try:

            abs_path_input_file = ffU.get_file_absolute_path_after_check(self.full_input_filename)

            segments = None
            info = None
            if self.vadFlag:
                segments, info = self.segmentation_and_transcription_method2(self.full_input_filename)
            else:
                segments, info = self.segmentation_and_transcription_method1(self.full_input_filename)

            with open(self.transcription_file, 'w') as file:
                file.write(
                    "| ==================================================================================================================================\n")
                file.write("NFO:")
                file.write("\t - audio file = '%s' \n" % (abs_path_input_file))
                filesize, audio_length = self.__get_audio_file_size_length__()
                file.write(f"\t Audio length: \t {audio_length}\n")
                file.write(f"\t Audio size: \t {filesize}\n")
                file.write(f"\t transcription model: \t WhisperModel(model_size={self.model_size}, device={self.modelDevice}, compute_type={self.modelComputeType})\n")
                file.write(
                    "\t - Detected language '%s' with probability %f \n" % (info.language, info.language_probability))
                file.write(
                    "| ==================================================================================================================================\n")

            idx = 0
            # processing each segments
            for segment in segments:
                startSegmentTimer=dtU.get_time_for_perf_counter()
                segment_transcription = self.process_audio_segment(segment, self.transcription_file)
                endSegmentTimer=dtU.get_time_for_perf_counter()
                elapsed_segment_time = dtU.get_elapsed_time(startSegmentTimer, endSegmentTimer)
                print(f"Segment {idx}: tokenize completed => {elapsed_segment_time:.2f}s: {segment_transcription}")
                idx += 1
        except Exception as e:

            errNbr += 1
            self.error("an error occured", exception=e)
            print(e)
            traceback.print_exc()

        self.show_elapsed_time_since_intermediate_timer()
        return errNbr

    def process_audio_segment(self, segment, transcription_file):
        start_time = time.time()  # Start timer
        segment_transcription = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
        with open(self.transcription_file, 'a') as file:
            # print(transcription)
            # Append the transcription to the output file
            file.write(segment_transcription + '\n')
        return segment_transcription

    def inializeModel(self):
        # Run on GPU with FP16
        #model = WhisperModel(model_size, device="cuda", compute_type="float16")
        # or run on GPU with INT8
        #model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
        # or run on CPU with INT8
        #model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.model = WhisperModel(self.model_size, device=self.modelDevice, compute_type=self.modelComputeType, num_workers=self.num_workers)

        #to forces the model to predict in English under the task of speech recognition:
        #model.config.forced_decoder_ids = WhisperProcessor.get_decoder_prompt_ids(language="english", task="transcribe")

    def segmentation_and_transcription_method1(self, audio_file_path):
        segments, info = self.model.transcribe(audio_file_path, beam_size=5)
        return segments, info

    def segmentation_and_transcription_method2(self, audio_file_path, min_silence_duration_ms=500):
        segments, info = self.model.transcribe(
            audio_file_path,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=min_silence_duration_ms),
        )
        return segments, info

if __name__ == "__main__":
    #audio_file_path = 'resampled_audio.wav'
    """
    audio_in_path = '../../../resources/audio/'
    audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a"
    audioFN = "2023_08_04_16_01_48_us622545Dierick.m4a"
    
    audio_in_path = '../out/audio/2023_08_18_15_03_17_datasourceForBfEData2MyConnect.trailingFrom00:18:38/'
    audioFN = "2023_08_18_15_03_17_datasourceForBfEData2MyConnect.trailingFrom00:18:38.speedup1.5..m4a"

    audio_in_path = "../out/audio/2023_08_04_16_01_48_us622545Dierick/"
    audioFN = "2023_08_04_16_01_48_us622545Dierick.speedup2.0..m4a"

    audio_file_path = audio_in_path + '/' + audioFN
    modelFrom = "LocalGoogleWhisper{model_size}"
    #audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"

    outputFolder = "../out/audio/"
    """

    # # audioFile = "../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"
    # audio_filename = "2023_08_29_14_34_14_povertySASSolutionGabPietOlivier.m4a"
    # audio_files_folder = "../../../resources/audio"
    #
    # # audio_files_folder = "../../../out/audio/convertedAudio"
    # output_folder = "../../../out/audio/transcription"
    #
    #
    # configLogOutput()
    #
    # module = WhisperModelTranscription(output_root_folder=output_folder)
    # #module.process_files_in_folder(main_folder=audio_files_folder, include_subdirs=False)
    # module.process_audio_file(audio_input_folder=audio_files_folder, audio_input_filename=audio_filename)

    relative_file_path = '../../../../resources/audio/2023_08_29_14_34_14_povertySASSolutionGabPietOlivier.m4a'
    abs_path_input_file = ffU.get_file_absolute_path_after_check(relative_file_path)
    print(abs_path_input_file)
