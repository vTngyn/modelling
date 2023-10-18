import subprocess

def run_lium_diarization(input_wav, output_rttm):
    # Path to the LIUM SpkDiarization JAR file
    lium_jar_path = "../../../resources/javaLibs/LIUMSpkDiarization/lium_spkdiarization-8.4.1.jar"  # Replace with your path

    # Run LIUM SpkDiarization
    subprocess.run([
        "java", "-Xmx2024m", "-jar", lium_jar_path,
        "--fInputMask=" + input_wav,
        "--sOutputMask=" + output_rttm,
        "--doCEClustering", "false",  # Change parameters as needed
        "--uem=ignore",
        "--trace=false", "--sTop=2", "--tInputMask=null",
        "--saveAllStep", "false", "--doCEClustering",
        "--fInputDesc=null", "--sOutputDesc=null"
    ])

if __name__ == "__main__":
    input_wav = "/path/to/your/input.wav"  # Replace with your input audio file
    output_rttm = "/path/to/your/output.rttm"  # Replace with the desired output RTTM file

    run_lium_diarization(input_wav, output_rttm)
