from vtnLibs.common_utils.FileFolderOperationsUtils import FileFOlderOpsUtils as ffoU
from vtnLibs.AudioFileUtils import AudioFileUtils as afU

if __name__ == "__main__":
    # Replace with the desired start time in HH:MM:SS format or seconds
    start_time = "00:18:38"

    audio_in_path = '../../../../resources/audio/'
    audioFN = '2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a'

    outputFolder = "../../out/audio/"


    audio_file_path = audio_in_path + '/' + audioFN
    baseAudioFilename, ext = ffoU.splitBaseFilenameExtension(audio_file_path)
    print(baseAudioFilename)
    print(ext)
    workingOutFolder = outputFolder + '/' + baseAudioFilename
    print(workingOutFolder)

    ffoU.createFolder(workingOutFolder)
    output_file = workingOutFolder + f"/{baseAudioFilename}.trailingFrom{start_time}{ext}"

    afU.copyRemainingAudioWithFFMPEG(audio_file_path, output_file, start_time=start_time)
