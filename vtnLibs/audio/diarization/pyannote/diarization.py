from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from . import ffU
from . import LEC
from . import dtU
from . import TMON
import torchaudio


# Pre-loading audio files in memory may result in faster processing:
#waveform, sample_rate = torchaudio.load(audioFile)
#diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate})

class SpeakerDiarization(TMON):
    def __init__(self, output_root_folder: str, saveToFile: bool = True, load_audio_in_memory: bool = False):
        self.pipeline = None
        self.diarization = None
        self.pipeline = None

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


    def setup_file_path_variables(self) -> None:
        self.audio_base_file_name, self.audio_base_file_ext = ffU.splitBaseFilenameExtension(self.audio_input_filename)
        # self.current_out_folder = self.output_root_folder + "/" + self.audio_base_file_name
        self.current_out_folder = self.output_root_folder

        tmpFolder = ffU.createFolder(self.current_out_folder)

        self.rttm_file_path = self.current_out_folder + f"/spk_diarization_{self.audio_base_file_name}.rttm"
        self.debug(f"Spk Diarization save to file: {self.rttm_file_path}")

    def initializePipeline(self) -> None:
        self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.0", use_auth_token="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")

        import torch

        #Processing on GPU
        #pipeline.to(torch.device("cuda"))

        # run the pipeline on an audio file
        #diarization = pipeline(audioFile)

    def diarize_audio_file(self, audio_input_folder, audio_input_filename, specifyNrSpeakers = True, isExactNbrSPeakerKnown = False, numberOfSpeakers = 2, min_speakers = 2, max_speakers = 6):
        self.audio_input_filename = audio_input_filename
        self.audio_input_folder = audio_input_folder
        self.setup_file_path_variables()

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
                waveform, sample_rate = torchaudio.load(self.audio_input_folder+"/"+self.audio_input_filename)
                diarization = self.pipeline({"waveform": waveform, "sample_rate": sample_rate}, **pipeline_kwargs_dict)
            else:
                self.debug(f"Diarization using audio file")
                self.diarization = self.pipeline(self.audio_input_folder+"/"+self.audio_input_filename, **pipeline_kwargs_dict)

        # dump the diarization output to disk using RTTM format
        if self.saveToFile:
            self.saveRTTMFile()
        return self.diarization
    def saveRTTMFile(self):
        # with open("../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.rttm", "w") as rttm:
        with open(self.rttm_file_path, "w") as rttm:
            self.diarization.write_rttm(rttm)

    def diarize_files_in_folder(self, main_folder, include_subdirs=False):
        fileList = ffU.parse_folder_with_subfolders(folder_to_parse=main_folder, include_subdirs=include_subdirs)
        self.debug("================================================================================")
        self.debug(f"|          looking for file in folder: {main_folder}")
        self.debug("================================================================================")
        idx=0
        for full_path, relative_path in fileList:
            directory, base_filename, extension = ffU.split_file_path(full_path)
            audioFilename=base_filename+extension
            self.debug(f" ### {idx:5}   ### processing audio file:{audioFilename} in folder {relative_path}")
            self.diarize_audio_file(audio_input_folder=directory, audio_input_filename=audioFilename)

if __name__ == "__main__":
    None
