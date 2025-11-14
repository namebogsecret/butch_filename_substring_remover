
import os
import sys
import platform
from pathlib import Path
from .rename import rename_files_and_dirs


def is_system_directory(path: str) -> bool:
    """Check if the path is a system directory that should not be modified.

    Args:
        path: The directory path to check.

    Returns:
        True if the path is a system directory, False otherwise.
    """
    abs_path = os.path.abspath(path)
    path_obj = Path(abs_path)

    # Unix/Linux system directories
    unix_system_dirs = [
        "/", "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64",
        "/proc", "/root", "/sbin", "/sys", "/usr", "/var",
        "/opt", "/srv", "/tmp", "/run", "/mnt", "/media"
    ]

    # Check if path is or is within any Unix system directory
    for sys_dir in unix_system_dirs:
        try:
            if path_obj == Path(sys_dir) or Path(sys_dir) in path_obj.parents:
                return True
        except (ValueError, OSError):
            continue

    # Windows system directories
    if platform.system() == "Windows":
        windows_system_dirs = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
            "C:\\System Volume Information"
        ]
        for sys_dir in windows_system_dirs:
            try:
                if path_obj == Path(sys_dir) or Path(sys_dir) in path_obj.parents:
                    return True
            except (ValueError, OSError):
                continue

    # Check if it's the user's home directory root (allow subdirectories)
    home = Path.home()
    if path_obj == home:
        return True

    return False


def rename_directory(root_directory: str, substrings_to_remove: list) -> None:
    """Rename files and directories by removing specified substrings.

    Args:
        root_directory: The root directory to process.
        substrings_to_remove: List of substrings to remove from filenames.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If the directory is not writable.
        ValueError: If the directory is a system directory.
    """
    # Check if the directory exists
    if not os.path.isdir(root_directory):
        raise FileNotFoundError(
            f"The directory {root_directory} does not exist or is not a directory."
        )

    # Check if the directory is writable
    if not os.access(root_directory, os.W_OK):
        raise PermissionError(f"The directory {root_directory} is not writable.")

    # Check for system directories
    if is_system_directory(root_directory):
        raise ValueError(
            f"It is not safe to run this script in system directories. "
            f"The directory '{root_directory}' is a protected system directory."
        )

    # Perform renaming of files and directories
    rename_files_and_dirs(root_directory, set(substrings_to_remove))
