from pyannote.audio import Pipeline
# from pyannote.audio import Diarization
from pyannote.audio.pipelines.utils.hook import ProgressHook
from vtnLibs.AudioFileUtils import AudioFileUtils as AudFU
from . import ffU
from . import LEC
from . import dtU
from . import TMON
import torchaudio
import torch
import re

# Pre-loading audio files in memory may result in faster processing:
#waveform, sample_rate = torchaudio.load(audioFile)
#diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})

class SpeakerDiarization(TMON):
    default_reprocess_file = False
    default_diarization_model_name = "pyannote/speaker-diarization-3.0"

    def __init__(self, output_root_folder: str, saveToFile: bool = True, load_audio_in_memory: bool = False, sad_model=None, overlap_function = True, diarization_model_name = default_diarization_model_name):

        self.pipeline = None
        self.diarization = None
        self.pipeline = None
        self.overlap_function = overlap_function
        self.sad_model = sad_model

        self.diarization_model_name = diarization_model_name

        self.load_audio_in_memory = load_audio_in_memory

        self.output_root_folder = output_root_folder
        self.saveToFile = saveToFile

        self.audio_base_file_name = None
        self.audio_base_file_ext = None

        self.audio_input_filename = None
        self.audio_input_folder = None
        self.current_out_folder = None
        self.rttm_file_path = None

        self.initializePipeline()


        self.set_timer_parameters()


    def setup_file_path_variables(self) -> None:
        self.audio_base_file_name, self.audio_base_file_ext = ffU.splitBaseFilenameExtension(self.audio_input_filename)
        # self.current_out_folder = self.output_root_folder + "/" + self.audio_base_file_name
        self.current_out_folder = self.output_root_folder

        tmpFolder = ffU.createFolder(self.current_out_folder)

        self.rttm_file_path = self.current_out_folder + f"/spk_diarization_{self.audio_base_file_name}.rttm"
        self.debug(f"Spk Diarization save to file: {self.rttm_file_path}")

    def initializePipeline(self) -> None:
        self.pipeline = Pipeline.from_pretrained(self.diarization_model_name, use_auth_token="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")

        #Processing on GPU
        #pipeline.to(torch.device("cuda"))
        self.pipeline.to(torch.device("mps"))

        # run the pipeline on an audio file
        #diarization = pipeline(audioFile)

        # Activate OSD and SAD (if available in the pipeline's configuration)
        #self.pipeline.model.params['overlap'] = self.overlap_function
        #self.pipeline.model.params['sad'] = 'my_sad_model'  # Replace with an actual SAD model if available

        # Deactivate OSD and SAD
        # self.pipeline.model.params['overlap'] = False
        # self.pipeline.model.params['sad'] = None  # Deactivate SAD

    def diarize_audio_file(self, audio_input_folder, audio_input_filename, specifyNrSpeakers = True, reprocess_file=default_reprocess_file, isExactNbrSPeakerKnown = False, numberOfSpeakers = 2, min_speakers = 2, max_speakers = 6, log_to_cosole=True):
        self.audio_input_filename = audio_input_filename
        self.audio_input_folder = audio_input_folder
        self.setup_file_path_variables()

        self.start_intermediate_timer()

        full_file_path = self.audio_input_folder+"/"+self.audio_input_filename

        if not reprocess_file:
            if ffU.is_existing_file(filepath=self.rttm_file_path):
                self.debug(f"  ### diarization file exists [{self.rttm_file_path}] for audio file:{audio_input_filename} in folder {audio_input_folder}")
                return None

        if log_to_cosole:
            self.debug(f"  ### processing audio file:{audio_input_filename} in folder {audio_input_folder}")

        #Hooks are available to monitor the progress of the pipeline:
        with ProgressHook() as hook:
            pipeline_kwargs_dict = {"hook": hook}
            if specifyNrSpeakers:
                if isExactNbrSPeakerKnown:
                    self.debug(f"parametrizing for Exact Nbr Of SPeakerKnown w/ #speaker = {numberOfSpeakers}")
                    # self.diarization = self.pipeline(self.audio_input_filename, hook=hook, num_speakers=numberOfSpeakers)
                    pipeline_kwargs_dict.update({"num_speakers": numberOfSpeakers})
                else:
                    self.debug(f"parametrizing for guessing #Speakers between  {min_speakers} and {max_speakers}")
                    # self.diarization = self.pipeline(self.audio_input_filename, hook=hook, min_speakers=min_speakers, max_speakers=max_speakers)
                    pipeline_kwargs_dict.update({"min_speakers": min_speakers, "max_speakers": max_speakers})
                    # self.diarization = self.pipeline(self.audio_input_folder+"/"+self.audio_input_filename)
            else:
                # self.diarization = self.pipeline(self.audio_input_filename, hook=hook)
                self.debug(f"parametrizing for guessing without knwon #Speaker")
                None


            if self.load_audio_in_memory:
                self.debug(f"Diarization using audio in memory preload")
                waveform, sample_rate = torchaudio.load(full_file_path)
                self.diarization = self.pipeline({"waveform": waveform, "sample_rate": sample_rate}, **pipeline_kwargs_dict)
            else:
                self.debug(f"Diarization using audio file")
                self.diarization = self.pipeline(self.audio_input_folder+"/"+self.audio_input_filename, **pipeline_kwargs_dict)

        # dump the diarization output to disk using RTTM format
        if self.saveToFile:
            self.saveRTTMFile()

        self.show_elapsed_time_since_intermediate_timer()

        return self.diarization

    def __get_audio_file_size_length__(self):
        audio_length = AudFU.get_audio_length_ffmpeg(self.audio_file_path)
        filesize = ffU.get_file_size(self.audio_file_path)
        return filesize, audio_length

    def saveRTTMFile(self):
        # with open("../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.rttm", "w") as rttm:
        with open(self.rttm_file_path, "w") as rttm:
            self.diarization.write_rttm(rttm)
            rttm.write(
                "| ==================================================================================================================================\n")
            rttm.write("NFO:")
            rttm.write(f"\t Audio file: \t {self.audio_input_filename}")
            filesize, audio_length = self.__get_audio_file_size_length__()
            rttm.write(f"\t Audio length: \t {audio_length}")
            rttm.write(f"\t Audio size: \t {filesize}")
            rttm.write(f"\t RTTM file: \t {self.rttm_file_path}")
            rttm.write(f"\t RTTM model: \t {self.diarization_model_name}")
            rttm.write(
                "| ==================================================================================================================================\n")


    @staticmethod
    def extract_parameters_for_number_of_speakers_from_filename(base_file_name: str) -> dict:
        #default parameters:
        specifyNrSpeakers = False
        isExactNbrSPeakerKnown = False
        numberOfSpeakers = 2
        min_speakers = 2
        max_speakers = 6
        #, specifyNrSpeakers = True, isExactNbrSPeakerKnown = False, numberOfSpeakers = 2, min_speakers = 2, max_speakers = 6
        # Define regex patterns to match the desired patterns
        pattern_interval = r'_(\d+)[pP]-(\d+)[pP]_'  # Pattern for interval: {lower}-{upper}p
        pattern_single = r'_(\d+)[pP]_'  # Pattern for single number

        # Use findall to extract all matching substrings for interval
        matches_interval = re.findall(pattern_interval, base_file_name)
        if matches_interval and len(matches_interval) > 0:
            try:
                min_speakers, max_speakers = int(matches_interval[0][0]), int(matches_interval[0][1])
                specifyNrSpeakers = True
            except Exception as e:
                SpeakerDiarization.error("an error occured", exception=e, appendTrace=True)
        else:
            # If no interval numbers found, try to extract single numbers
            matches_single = re.findall(pattern_single, base_file_name)
            if matches_single and len(matches_single) > 0:
                try:
                    numberOfSpeakers = int(matches_single[0])
                    specifyNrSpeakers = True
                    isExactNbrSPeakerKnown = True
                except Exception as e:
                    SpeakerDiarization.error("an error occured", exception=e, appendTrace=True)
        result = {'specifyNrSpeakers': specifyNrSpeakers, 'isExactNbrSPeakerKnown': isExactNbrSPeakerKnown,
                  'numberOfSpeakers': numberOfSpeakers, 'min_speakers': min_speakers, 'max_speakers': max_speakers}
        SpeakerDiarization.debug("extracted speaker parameters:")
        print(result)
        return result

    def diarize_files_in_folder(self, main_folder, include_subdirs=False, allowed_audio_formats =  None, reprocess_file=default_reprocess_file):
        fileList = ffU.parse_folder_with_subfolders(folder_to_parse=main_folder, include_subdirs=include_subdirs, allowed_extensions=allowed_audio_formats)
        self.debug("================================================================================")
        self.debug(f"|          looking for file in folder: {main_folder}")
        self.debug("================================================================================")
        idx=0

        self.startTimer()

        for full_path, relative_path in fileList:
            directory, base_filename, extension = ffU.split_file_path(full_path)
            audioFilename=base_filename+extension
            filesize = ffU.get_file_size(full_path)
            self.debug(f" ### {idx:5}   ### processing audio file:{audioFilename} [size={filesize['mb']:.2f}MB] in folder {full_path}")
            try:
                speaker_params_kwargs=SpeakerDiarization.extract_parameters_for_number_of_speakers_from_filename(base_filename)
                self.diarize_audio_file(audio_input_folder=directory, audio_input_filename=audioFilename, log_to_cosole=False, reprocess_file=reprocess_file, **speaker_params_kwargs)
            except Exception as e:
                self.error("an exception has occured!", exception=e)
                print(e)
            idx += 1

        self.stopTimer()
        self.show_total_processing_time()

if __name__ == "__main__":
    None
    SpeakerDiarization.extract_parameters_for_number_of_speakers_from_filename("djksfhksj_45p_ferfe.txt")