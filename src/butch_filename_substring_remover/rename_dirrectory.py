
import os
from butch_filename_substring_remover import rename_files_and_dirs

def rename_directory(root_directory: str, substrings_to_remove: list) -> None:
    # Check if the directory exists
    if not os.path.isdir(root_directory):
        raise FileNotFoundError(f"The directory {root_directory} does not exist or is not a directory.")

    # Check if the directory is writable
    if not os.access(root_directory, os.W_OK):
        raise PermissionError(f"The directory {root_directory} is not writable.")

    # Warning about potential dangers of running the script in system directories
    system_dirs = ["/", "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc", "/root", "/sbin", "/sys", "/usr", "/var"]
    if os.path.abspath(root_directory) in system_dirs:
        raise ValueError("It is not safe to run this script in system directories.")

    # Perform renaming of files and directories
    rename_files_and_dirs(root_directory, set(substrings_to_remove))
