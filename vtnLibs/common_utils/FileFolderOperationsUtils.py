import os
from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec

class FileFOlderOpsUtils(lec):
    FOLDER_EXIST = "exists"
    FOLDER_CREATED = "fdCreated"

    @staticmethod
    def createFolder(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            FileFOlderOpsUtils.info(f"Folder '{folder_name}' created successfully.")
            return FileFOlderOpsUtils.FOLDER_CREATED
        else:
            FileFOlderOpsUtils.info(f"Folder '{folder_name}' already exists.")
            return FileFOlderOpsUtils.FOLDER_EXIST

    @staticmethod
    def splitBaseFilenameExtension(full_path):
        # Get the base filename from the full path
        base_filename = os.path.basename(full_path)

        # Split the base filename into filename and extension
        filename, extension = os.path.splitext(base_filename)
        return filename, extension

    @staticmethod
    def split_file_path(file_path):
        # Split the file path into directory, base filename, and extension
        directory, full_filename = os.path.split(file_path)
        base_filename, extension = os.path.splitext(full_filename)
        return directory, base_filename, extension

    @staticmethod
    def parse_folder_with_subfolders(folder_to_parse, allowed_extensions=None, include_subdirs=True):
        result = []
        if not include_subdirs:
            contents = [item for item in os.listdir(folder_to_parse) if os.path.isfile(os.path.join(folder_to_parse, item))]
            for file in contents:
                full_path = os.path.join(folder_to_parse, file)
                relative_path = os.path.relpath(full_path, folder_to_parse)
                result.append((full_path, relative_path))

        else:
            for root, dirs, files in os.walk(folder_to_parse):
                for file in files:
                    pathBaseFilename, extension = os.path.splitext(file)
                    if extension.lower() in allowed_extensions:
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, folder_to_parse)
                        result.append((full_path, relative_path))

        return result


if __name__ == "__main__":
    None