from faster_whisper import WhisperModel
import time
from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec

class SpeechRecognitionGoogleWhisper(lec):
    def __int__(self, audio_file_path, transcription_file_path):
        self.job_start_time = None
        self.job_end_time = None
        self.job_elapsed_time = None
        self.audio_file_path = audio_file_path
        self.transcription_file_path = transcription_file_path

        self.model_size = None
        # "cuda" or "cpu"
        self.modelDevice = None
        # "int8" | "int8_float16" | "float16"
        self.modelComputeType = None
        self.model = None
        self.modelInitialized = False

        self.beam_size

        self.__segments__ = None
        self.__info__ = None

    def __run__(self):
        print(f"transcription save to file: {self.transcription_file_path}")
        print(f"Trasncription job is starting...")
        self.job_start_time = time.time()  # Start timer

    def __finished__(self):
        print(f"Trasncription job has ended...")
        self.job_end_time = time.time()  # end timer
        self.job_elapsed_time = self.job_end_time - self.job_start_time
        print(f"Transcription JOB completed in {self.job_elapsed_time:.2f} seconds")

    def setModelParams(self, model_size = "large-v2", modelDevice = "cpu", modelComputeType = "int8", beam_size=5, vad_filter=True, min_silence_duration_ms=500):
        self.model_size = model_size
        self.modelDevice = modelDevice

        self.modelComputeType = modelComputeType
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.vad_parameters = dict(min_silence_duration_ms=min_silence_duration_ms)

        self.__getModel__()

    def __getModel__(self):
        # Run on GPU with FP16
        #model = WhisperModel(model_size, device="cuda", compute_type="float16")
        # or run on GPU with INT8
        #model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
        # or run on CPU with INT8
        #model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        self.modelInitialized = True


    def transcribeAudio(self):
        if (self.modelInitialized):
            self.__run__()
            self.__getModel__()

            self.__getSegmentsMethod1__()
            #self.__getSegmentsMethod2__()
            self.__initializeOUtput__()

            self.__execJob__()

            self.__finished__()
        else:
            print("Error: Model Not initialized!!")

    def __getSegmentsMethod1__(self):
        self.__segments__, self.__info__ = self.model.transcribe(self.audio_file_path, beam_size=self.beam_size)
        #return segments, info

    def __getSegmentsMethod2__(self):
        self.__segments__, self.__info__ = self.model.transcribe(
            self.audio_file_path,
            vad_filter=self.vad_filter,
            vad_parameters=self.vad_parameters
        )
        #return segments, info

    def __initializeOUtput__(self):
        with open(self.transcription_file_path, 'w') as file:
            file.write("| ==================================================================================================================================\n")
            file.write("NFO:")
            file.write("\t - audio file = '%s' \n" % (self.audio_file_path))
            file.write("\t - Detected language '%s' with probability %f \n" % (self.info.language, self.info.language_probability))
            file.write("| ==================================================================================================================================\n")

    def __execJob__(self):
        idx=0
        for segment in self.segments:
            start_time = time.time()  # Start timer
            transcription = "[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)
            with open(self.transcription_file_path, 'a') as file:
                #print(transcription)
                # Append the transcription to the output file
                file.write(transcription + '\n')
            end_time = time.time()  # End timer
            elapsed_time = end_time - start_time
            print(f"Segment {idx}: tokenize completed => {elapsed_time:.2f}s: {transcription}")
            idx+=1



if __name__ == "__main__":
    None