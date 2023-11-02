# from diart import OnlineSpeakerDiarization, PipelineConfig
#https://github.com/juanmc2005/diart#installation

# from diart.sources import MicrophoneAudioSource
# from diart.inference import RealTimeInference
# from diart.sinks import RTTMWriter
# from diart.models import EmbeddingModel, SegmentationModel

#
# def model_loader():
#     return load_pretrained_model("my_model.ckpt")
#
#
# class MySegmentationModel(SegmentationModel):
#     def __init__(self):
#         super().__init__(model_loader)
#
#     @property
#     def sample_rate(self) -> int:
#         return 16000
#
#     @property
#     def duration(self) -> float:
#         return 2  # seconds
#
#     def forward(self, waveform):
#         # self.model is created lazily
#         return self.model(waveform)
#
#
# class MyEmbeddingModel(EmbeddingModel):
#     def __init__(self):
#         super().__init__(model_loader)
#
#     def forward(self, waveform, weights):
#         # self.model is created lazily
#         return self.model(waveform, weights)
#
#
# config = PipelineConfig(
#     segmentation=MySegmentationModel(),
#     embedding=MyEmbeddingModel()
# )

# pipeline = OnlineSpeakerDiarization()
# #Third-party models can be integrated seamlessly by subclassing SegmentationModel and EmbeddingModel (which are PyTorch Module subclasses):
# # pipeline = OnlineSpeakerDiarization(config)
# sample_rate = pipeline.config.sample_rate
# mic = MicrophoneAudioSource(sample_rate)
# inference = RealTimeInference(pipeline, mic, do_plot=True)
# inference.attach_observers(RTTMWriter(mic.uri, "/output/file.rttm"))
# prediction = inference()

#Tune hyper-parameters
from diart.optim import Optimizer

optimizer = Optimizer("/wav/dir", "/rttm/dir", "/output/dir")
optimizer(num_iter=100)
#This will write results to an sqlite database in /output/dir.

#Distributed optimization
# #For bigger datasets, it is sometimes more convenient to run multiple optimization processes in parallel. To do this, create a study on a recommended DBMS (e.g. MySQL or PostgreSQL) making sure that the study and database names match:
#
# mysql -u root -e "CREATE DATABASE IF NOT EXISTS example"
# optuna create-study --study-name "example" --storage "mysql://root@localhost/example"
#
# #You can now run multiple identical optimizers pointing to this database:
#
# from diart.optim import Optimizer
# from optuna.samplers import TPESampler
# import optuna
#
# db = "mysql://root@localhost/example"
# study = optuna.load_study("example", db, TPESampler())
# optimizer = Optimizer("/wav/dir", "/rttm/dir", study)
# optimizer(num_iter=100)

#Build pipelines
import rx.operators as ops
import diart.operators as dops
from diart.sources import MicrophoneAudioSource
from diart.blocks import SpeakerSegmentation, OverlapAwareSpeakerEmbedding

segmentation = SpeakerSegmentation.from_pyannote("pyannote/segmentation")
embedding = OverlapAwareSpeakerEmbedding.from_pyannote("pyannote/embedding")
sample_rate = segmentation.model.sample_rate
mic = MicrophoneAudioSource(sample_rate)

stream = mic.stream.pipe(
    # Reformat stream to 5s duration and 500ms shift
    dops.rearrange_audio_stream(sample_rate=sample_rate),
    ops.map(lambda wav: (wav, segmentation(wav))),
    ops.starmap(embedding)
).subscribe(on_next=lambda emb: print(emb.shape))

mic.read()

