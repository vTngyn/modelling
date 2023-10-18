"""
    prerequisite:
        -- execute : src/audioProcessing/audioFileOperations/audioFormatConversion/AudioFormatConverter.py
"""
#speaker diarization demo: https://youtu.be/SY6rHaD-eEc

# instantiate the pipeline
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import matplotlib.pyplot as plt
from vtnLibs.audio.diarization.pyannote.diarization import SpeakerDiarization as sd
from vtnLibs.common_utils.LogUtils import configLogOutput
from vtnLibs.AudioFileUtils import AudioFileUtils
from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffU

# audioFile = "../../out/audio/2023_08_04_16_01_48_us622545Dierick/resampled_audio.wav"
# audio_filename = "2023_06_22_13_40_25.m4a"
src_audio_files_folder = "../../../resources/audio"
audio_filename = "2023_06_22_13_40_25.wav"
prep_audio_files_folder = "../../../out/audio/convertedAudio"
output_folder = "../../../out/audio/diarization"

audio_files_folder = prep_audio_files_folder


configLogOutput()

include_subdirs=False
allowed_audio_formats=[AudioFileUtils.FFMPEG_FORMAT_WAV]
fileList = ffU.parse_folder_with_subfolders(folder_to_parse=src_audio_files_folder, include_subdirs=include_subdirs,
                                            allowed_extensions=allowed_audio_formats)


sdModule = sd(output_root_folder=output_folder, load_audio_in_memory=True)
sdModule.diarize_files_in_folder(main_folder=audio_files_folder, allowed_audio_formats=allowed_audio_formats, reprocess_file=True)
# sdModule.diarize_audio_file(audio_input_folder=audio_files_folder, audio_input_filename=audio_filename, reprocess_file=True)




"""
#https://github.com/FrenchKrab/IS2023-powerset-diarization/

# An example notebook is available, you can see how to load a powerset model (for example, one available in models/ [https://github.com/FrenchKrab/IS2023-powerset-diarization/blob/master/models]),
# how to train it further on a toy dataset, and finally how to get its local segmentation output and final diarization output.
# Using checkpoints in a pipeline

from pyannote.audio.models.segmentation import PyanNet
from pyannote.audio.pipelines import SpeakerDiarization as SpeakerDiarizationPipeline

# constants (params from the pyannote/speaker-diarization huggingface pipeline)
WAV_FILE="../pyannote-audio/tutorials/assets/sample.wav"
MODEL_PATH="models/powerset/powerset_pretrained.ckpt"
PIPELINE_PARAMS = {
    "clustering": {
        "method": "centroid",
        "min_cluster_size": 15,
        "threshold": 0.7153814381597874,
    },
    "segmentation": {
        "min_duration_off": 0.5817029604921046,
        # "threshold": 0.4442333667381752,  # does not apply to powerset
    },
}

# create, instantiate and apply the pipeline
pipeline = SpeakerDiarizationPipeline(
    segmentation=MODEL_PATH,
    embedding="speechbrain/spkrec-ecapa-voxceleb",
    embedding_exclude_overlap=True,
    clustering="AgglomerativeClustering",
)
pipeline.instantiate(PIPELINE_PARAMS)
pipeline(WAV_FILE)

"""