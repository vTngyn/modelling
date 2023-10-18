
def get_relative_file_path_from_script_folder(file_path_from_root: str, script_folder_deep: int) -> str:
    p = str()
    for i in range(script_folder_deep):
        p += "../"
    return p + file_path_from_root