import inspect
import os
from vtnLibs.common_utils.LogUtils import LogEnabledClass as lec
from typing import List
import pprint

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
    def splitBaseFilenameExtension(full_path, remove_leading_dot=False):
        # Get the base filename from the full path
        base_filename = os.path.basename(full_path)

        # Split the base filename into filename and extension
        filename, extension = os.path.splitext(base_filename)
        if remove_leading_dot:
            return filename, FileFOlderOpsUtils.get_extension_without_leading_dot(extension)
        return filename, extension

    @staticmethod
    def split_file_path(file_path, remove_leading_dot=False):
        # Split the file path into directory, base filename, and extension
        directory, full_filename = os.path.split(file_path)
        base_filename, extension = os.path.splitext(full_filename)
        if remove_leading_dot:
            return directory, base_filename, FileFOlderOpsUtils.get_extension_without_leading_dot(extension)
        return directory, base_filename, extension

    @staticmethod
    def get_extension_with_leading_dot(extension: str) -> str:
        result = extension
        if extension and not extension.startswith("."):
            result = "." + extension
        return result

    @staticmethod
    def is_existing_file(filepath):
        """Check if the given path is an existing regular file."""
        return os.path.isfile(filepath)

    @staticmethod
    def is_existing_dir(dirpath):
        """Check if the given path is an existing regular file."""
        return os.path.isdir(dirpath)

    @staticmethod
    def get_extension_without_leading_dot(extension: str) -> str:
        result = extension
        if extension and extension.startswith("."):
            result = extension[1:]
        return result

    @staticmethod
    def is_file_extension_in_extensions_list(file_ext, ext_list: List):
        if ext_list:
            for i, e in enumerate(ext_list):
                r = FileFOlderOpsUtils.is_file_extension_equality(file_ext, e)
                if r:
                    return r
    @staticmethod
    def __check_file_extension__(file_ext: str, ext_admitted: str, both_none_equals=True):
        return FileFOlderOpsUtils.is_file_extension_equality(file_ext, ext2=ext_admitted, both_none_equals=both_none_equals)

    @staticmethod
    def check_file_extension(file_path: str, ext_admitted: str, both_none_equals=True):
        directory, base_filename, extension = FileFOlderOpsUtils.split_file_path(file_path=file_path, remove_leading_dot=True)
        ext_admit = FileFOlderOpsUtils.get_extension_without_leading_dot(ext_admitted)
        return FileFOlderOpsUtils.__check_file_extension__(file_ext=extension, ext_admitted=ext_admit, both_none_equals=both_none_equals)
    @staticmethod
    def check_file_extension_in_list(file_path: str, ext_list: List, both_none_equals=True, null_list_return_true=True):
        directory, base_filename, extension = FileFOlderOpsUtils.split_file_path(file_path=file_path, remove_leading_dot=True)
        if ext_list :
            if len(ext_list)==0:
                if null_list_return_true:
                    return True
                return False
            else:
                for i, e in enumerate(ext_list):
                    ext_admit = FileFOlderOpsUtils.get_extension_without_leading_dot(e)
                    r = FileFOlderOpsUtils.__check_file_extension__(file_ext=extension, ext_admitted=ext_admit, both_none_equals=both_none_equals)
                    if r:
                        return r
        else:
            if null_list_return_true:
                return True
            return False

    @staticmethod
    def is_file_extension_equality(ext1, ext2, both_none_equals=True):
        if ext1:
            tmp1=FileFOlderOpsUtils.get_extension_without_leading_dot(ext1)
            if ext2:
                tmp2=FileFOlderOpsUtils.get_extension_without_leading_dot(ext2)
                return tmp1 == tmp2
            return False
        else:
            if ext2:
                return False
            if both_none_equals:
                return True
            return False
    @staticmethod
    def parse_folder_with_subfolders(folder_to_parse, allowed_extensions=None, include_subdirs=True):
        result = []
        if not include_subdirs:
            contents = [item for item in os.listdir(folder_to_parse) if os.path.isfile(os.path.join(folder_to_parse, item))]
            for file in contents:
                pathBaseFilename, extension = os.path.splitext(file)

                if allowed_extensions is None or FileFOlderOpsUtils.is_fileext_in_allowed_file_format(extension, allowed_extensions):
                    full_path = os.path.join(folder_to_parse, file)
                    relative_path = os.path.relpath(full_path, folder_to_parse)
                    result.append((full_path, relative_path))

        else:
            for root, dirs, files in os.walk(folder_to_parse):
                for file in files:
                    pathBaseFilename, extension = os.path.splitext(file)
                    ext = FileFOlderOpsUtils.get_extension_without_leading_dot(extension=extension)
                    if allowed_extensions is None or FileFOlderOpsUtils.is_fileext_in_allowed_file_format(ext, allowed_extensions):
                        full_path = os.path.join(root, file)
                        relative_path = os.path.relpath(full_path, folder_to_parse)
                        result.append((full_path, relative_path))
        return result

    @staticmethod
    def is_fileext_in_allowed_file_format(file_extension,  allowed_extensions):
        result=True
        if allowed_extensions and len(allowed_extensions) > 0:
            if file_extension.lower() not in allowed_extensions:
                result=False
        FileFOlderOpsUtils.debug(f"is allowed file in list({allowed_extensions}) ? {result}")
        return result

    @staticmethod
    def get_file_size(file_path):
        try:
            # Get file size in bytes
            file_size = os.path.getsize(file_path)

            # Convert bytes to kilobytes (KB)
            file_size_kb = file_size / 1024

            # Convert bytes to megabytes (MB)
            file_size_mb = file_size / (1024 * 1024)

            # Convert bytes to gigabytes (GB)
            file_size_gb = file_size / (1024 * 1024 * 1024)

            return {
                'b': file_size,
                'kb': file_size_kb,
                'mb': file_size_mb,
                'gb': file_size_gb
            }
        except Exception as e:
            FileFOlderOpsUtils.error("An error occured!", exception=e)

    @staticmethod
    def get_file_absolute_path_after_check(relative_path):
        """
        Get the absolute path of a file given its relative path.

        Parameters:
        relative_path (str): The relative path of the file.

        Returns:
        str: The absolute path of the file if it exists, None otherwise.
        """
        # Get the absolute path of the file
        abs_path = os.path.abspath(relative_path)

        # Check if the file exists
        if os.path.exists(abs_path):
            return abs_path
        else:
            return None

    @staticmethod
    def get_relative_file_path_from_script_folder(file_path_from_root: str, script_folder_deep: int) -> str:
        p = str()
        for i in range(script_folder_deep):
            p += "../"
        return p + file_path_from_root

    @staticmethod
    def get_current_location_path():
        # Get the frame object for the current function
        current_frame = inspect.currentframe()

        # Get the filename (path) of the current frame
        current_file = inspect.getframeinfo(current_frame).filename

        # Convert to an absolute path
        absolute_path = os.path.abspath(current_file)

        return absolute_path

    @staticmethod
    def get_caller_file_location(base_fct_name=None, level=1):
        # Get the frame of the calling function
        stack = inspect.stack()
        if base_fct_name:
            # print(f"looking into stack levels from 0 to {len(stack)}")
            next_is_correct = False
            for level in range(len(stack)):
                # print(f"\tlevel={level}")
                caller_frame = inspect.stack()[level]
                # doc:  j=3 => function name
                #       j=1 => file in which the function is located

                # for j in range(len(caller_frame)):
                #     print(f"\tj={j}")
                #     print (caller_frame[j])

                if caller_frame[3] == base_fct_name:
                    next_is_correct = True
                    base_caller_frame = inspect.stack()[level + 1]
                    return (base_caller_frame[1], base_caller_frame[3])

        else:
            idx_caller_frame = inspect.stack()[level]
            return (idx_caller_frame[1], idx_caller_frame[3])

    @staticmethod
    def get_caller_location_elements():
        cur_fct_frame =  inspect.currentframe()
        cur_fct_name = cur_fct_frame.f_code.co_name
        # print(cur_fct_name.f_back)
        # print(cur_fct_name.f_back.f_code)
        # print(cur_fct_name.f_back.f_code.co_name)
        #path = FileFOlderOpsUtils.get_caller_file_location(level=2)
        path, fct_name = FileFOlderOpsUtils.get_caller_file_location(base_fct_name=cur_fct_name)
        return FileFOlderOpsUtils.split_file_path(file_path=path, remove_leading_dot=True)

    @staticmethod
    def get_this_location_path_elements():
        path = FileFOlderOpsUtils.get_current_location_path()
        print(path)
        return FileFOlderOpsUtils.split_file_path(file_path=path, remove_leading_dot=True)


if __name__ == "__main__":
    None
    # Call the function to get the absolute path of the current file
    current_file_path = FileFOlderOpsUtils.get_current_location_path()
    print("Absolute path of the current file:", current_file_path)
    p, bn, ext = FileFOlderOpsUtils.get_this_location_path_elements()
    print(f'path={p}')
    print(f'base name={bn}')
    print(f'ext={ext}')
