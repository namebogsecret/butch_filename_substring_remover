
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
    # Note: "/" is checked separately (only exact match, not as parent)
    unix_system_dirs = [
        "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64",
        "/proc", "/root", "/sbin", "/sys", "/usr", "/var",
        "/opt", "/srv", "/tmp", "/run", "/mnt", "/media"
    ]

    # Check for root directory (exact match only)
    if path_obj == Path("/"):
        return True

    # Check if path is or is within any Unix system directory
    for sys_dir in unix_system_dirs:
        try:
            sys_path = Path(sys_dir)
            if path_obj == sys_path or sys_path in path_obj.parents:
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


def rename_directory(
    root_directory: str,
    substrings_to_remove: list,
    dry_run: bool = False,
    skip_confirm: bool = False,
    extensions: list[str] | None = None,
    undo_file: str | None = None,
    no_undo: bool = False
) -> None:
    """Rename files and directories by removing specified substrings.

    Args:
        root_directory: The root directory to process.
        substrings_to_remove: List of substrings to remove from filenames.
        dry_run: If True, only show what would be renamed without making changes.
        skip_confirm: If True, skip the confirmation prompt.
        extensions: If provided, only process files with these extensions.
        undo_file: Path for the undo script. If None, auto-generated.
        no_undo: If True, don't generate an undo script.

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

    # Check if the directory is writable (only if not dry-run)
    if not dry_run and not os.access(root_directory, os.W_OK):
        raise PermissionError(f"The directory {root_directory} is not writable.")

    # Check for system directories
    if is_system_directory(root_directory):
        raise ValueError(
            f"It is not safe to run this script in system directories. "
            f"The directory '{root_directory}' is a protected system directory."
        )

    # Perform renaming of files and directories
    rename_files_and_dirs(
        root_dir=root_directory,
        to_remove=set(substrings_to_remove),
        dry_run=dry_run,
        skip_confirm=skip_confirm,
        extensions=extensions,
        undo_file=undo_file,
        no_undo=no_undo
    )
