import os

outputFolder = "../out/audio/"
audio_file_path = '../resources/audio/2023_08_18_15_03_17_datasourceForBfEData2MyConnect.m4a'

model = None

def create_folder_if_not_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    else:
        print(f"Folder '{folder_name}' already exists.")


def get_base_filename_without_extension(full_path):
    # Get the base filename from the full path
    base_filename = os.path.basename(full_path)

    # Split the base filename into filename and extension
    filename, extension = os.path.splitext(base_filename)

    return filename

baseTransFilename = get_base_filename_without_extension(audio_file_path)
print(baseTransFilename)
workingOutFolder = outputFolder+baseTransFilename
print(workingOutFolder)
transOutputFolder = create_folder_if_not_exists(workingOutFolder)

transcription_file_path = workingOutFolder + f"/transcription_{baseTransFilename}.txt"
print(transcription_file_path)

with open(transcription_file_path, "w") as file:
    file.write("ca marched ?")

with open(transcription_file_path, "r") as file:
    print("file content:")
    print(file.readline())

