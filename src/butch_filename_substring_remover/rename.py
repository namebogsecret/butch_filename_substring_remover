
import os
import sys
from .utils import remove_substrings

def rename_files_and_dirs(root_dir: str, to_remove: set[str]) -> None:
    """Renames files and folders in the specified directory.
    root_dir: The root directory to rename files and folders in.
    to_remove: A set of substrings to remove from the names of files and folders."""
    max_length = 80  # To store the maximum length of the string
    for dirpath, dirnames, filenames in os.walk(root_dir):
        line = f'Processing: {dirpath}'
        current_length = len(line)
        max_length = max(max_length, current_length)  # Update the maximum length of the string
        print(f'\r{line}{" " * (max_length - current_length)}', end='\n')

        # Renaming files
        for filename in filenames:
            new_name = remove_substrings(filename, to_remove)
            if new_name != filename:
                try:
                    os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, new_name))
                except OSError as e:
                    print(f"\nError renaming file {filename} to {new_name}: {e}", file=sys.stderr)

        # Renaming directories
        for dirname in dirnames:
            new_name = remove_substrings(dirname, to_remove)
            if new_name != dirname:
                try:
                    os.rename(os.path.join(dirpath, dirname), os.path.join(dirpath, new_name))
                except OSError as e:
                    print(f"\nError renaming directory {dirname} to {new_name}: {e}", file=sys.stderr)
