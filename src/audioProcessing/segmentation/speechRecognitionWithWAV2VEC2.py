import torch
import torchaudio
import IPython
import matplotlib.pyplot as plt
from torchaudio.utils import download_asset
import pprint


from vtnLibs.common_utils.LogUtils import LogEnabledClass as LEC, configLogOutput,get_printable_from_tuple

class wav2vec2SpeechRocgnition(LEC):
    def __init__(self, audio_file):
        self.device = None
        self.model = None
        self.bundle = None
        self.waveform = None
        self.waveform_orig = None
        self.sample_rate = None
        self.sample_rate_orig = None
        self.emission = None
        self.features = None

        self.audio_file = audio_file
        # SPEECH_FILE = download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")

        self.__initialize_model__()
        self.__initialize_pipeline__()


    def __initialize_model__(self):
        self.debug(f"torch version={torch.__version__}")
        self.debug(f"torchaudio version={torchaudio.__version__}")

        torch.random.manual_seed(0)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        #self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.debug(f"device={self.device}")
        self.device = "cpu"

        SPEECH_FILE = download_asset("tutorial-assets/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav")

    def __initialize_pipeline__(self):
        self.bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
        self.debug(f"Sample Rate:{str(self.bundle.sample_rate)}")
        self.debug(f"Labels:{(''.join(self.bundle.get_labels()))}")

        self.model = self.bundle.get_model().to(self.device)


    def resample_audio(self):
        self.waveform_orig, self.sample_rate_orig = torchaudio.load(self.audio_file)
        self.waveform = self.waveform_orig.to(self.device)

        if self.sample_rate_orig != self.bundle.sample_rate:
            self.waveform = torchaudio.functional.resample(self.waveform_orig, self.sample_rate_orig, self.bundle.sample_rate)
            self.sample_rate = self.bundle.sample_rate
            # When performing resampling multiple times on the same set of sample rates, using torchaudio.transforms.Resample might improve the performace.
        else:
            self.waveform = self.waveform_orig
            self.sample_rate = self.sample_rate_orig
    def display_audio_file(self):
        IPython.display.Audio(self.audio_file)

    def extract_accoustic_feature(self):

        with torch.inference_mode():
            self.features, _ = self.model.extract_features(self.waveform)

        fig, ax = plt.subplots(len(self.features), 1, figsize=(16, 4.3 * len(self.features)))
        for i, feats in enumerate(self.features):
            ax[i].imshow(feats[0].cpu(), interpolation="nearest")
            ax[i].set_title(f"Feature from transformer layer {i+1}")
            ax[i].set_xlabel("Feature dimension")
            ax[i].set_ylabel("Frame (time-axis)")
        fig.tight_layout()

    def feature_classification(self):
        with torch.inference_mode():
            self.emission, _ = self.model(self.waveform)
            # Let’s visualize this:
            plt.imshow(self.emission[0].cpu().T, interpolation="nearest")
            plt.title("Classification result")
            plt.xlabel("Frame (time-axis)")
            plt.ylabel("Class")
            plt.tight_layout()
            print("Class labels:", self.bundle.get_labels())

#class for generating trasncriptions
class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, blank=0):
        super().__init__()
        self.labels = labels
        self.blank = blank

    def forward(self, emission: torch.Tensor) -> str:
        """Given a sequence emission over labels, get the best path string
        Args:
          emission (Tensor): Logit tensors. Shape `[num_seq, num_label]`.

        Returns:
          str: The resulting transcript
        """
        indices = torch.argmax(emission, dim=-1)  # [num_seq,]
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i != self.blank]
        return "".join([self.labels[i] for i in indices])

if __name__ == "__main__":
    audio_file = "/Users/vtn/pythonProjects/audioVIdeo/testTensorFlowM1/out/audio/convertedAudio/2023_10_12_11_29_52_2p_intro_audit_reco_gabriel.wav"

    configLogOutput()
    module = wav2vec2SpeechRocgnition(audio_file = audio_file)
    module.resample_audio()
    # module.display_audio_file()
    module.extract_accoustic_feature()
    module.feature_classification()

    decoder = GreedyCTCDecoder(labels=module.bundle.get_labels())
    transcript = decoder(module.emission[0])
