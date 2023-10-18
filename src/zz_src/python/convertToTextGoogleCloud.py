import wave
from google.cloud import speech_v1p1beta1 as speech

audio_file_path = 'resampled_audio.wav'
moldeFrom = "GoogleCloud"
#audio_file_path = r"C:\repo\dev\pythonProjects\testVSCode\audio2text\resampled_audio.wav"
transcription_file_path = f"C:\\repo\\dev\\pythonProjects\\testVSCode\\audio2text\\out\\transciptions\\{audio_file_path}_transcription{moldeFrom}.txt"

def transcribe_audio_streaming(audio_file_path, output_path, chunk_size=8192):
    client = speech.SpeechClient()

    with wave.open(audio_file_path, 'rb') as audio:
        sample_rate = audio.getframerate()

        # Initialize streaming request
        streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=sample_rate,
                language_code="en-US",
            ),
            single_utterance=True,
        )

        def generator():
            try:
                while True:
                    chunk = audio.readframes(chunk_size)
                    if not chunk:
                        return
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
            except GeneratorExit:
                return

        streaming_request = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in generator())

        # Perform streaming transcription
        responses = client.streaming_recognize(config=streaming_config, requests=streaming_request)

        # Save transcriptions to a text file
        with open(output_path, "w") as transcript_file:
            for response in responses:
                for result in response.results:
                    transcript_file.write("Transcript: {}\n".format(result.alternatives[0].transcript))

        print("Transcription saved to:", output_path)

# Replace with your actual paths
audio_file_path = "path/to/your/audio_file.wav"
output_path = "transcription.txt"

transcribe_audio_streaming(audio_file_path, transcription_file_path)
