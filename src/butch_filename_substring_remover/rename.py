
import os
import sys
from .utils import remove_substrings, color_text

def rename_files_and_dirs(root_dir: str, to_remove: set[str]) -> None:
    """Renames files and folders in the specified directory.
    root_dir: The root directory to rename files and folders in.
    to_remove: A set of substrings to remove from the names of files and folders."""
    max_length = 80  # To store the maximum length of the string
    all_errors = []  # To store all errors that occur during renaming
    dir_count = 0  # To store the number of directories processed
    file_count = 0  # To store the number of files processed
    all_dirs = 0  # To store the number of directories
    all_files = 0  # To store the number of files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        line = f'Processing: {dirpath}'
        current_length = len(line)
        max_length = max(max_length, current_length)  # Update the maximum length of the string
        print(f'\r{line}{" " * (max_length - current_length)}', end='\n')

        # Renaming files
        for filename in filenames:
            all_files += 1
            new_name = remove_substrings(filename, to_remove)
            if new_name != filename:
                if new_name == "":
                    print(f"\nError renaming file '{filename}' to '{new_name}': Empty filename", file=sys.stderr)
                    all_errors.append(f"\nError renaming file '{filename}' to '{new_name}': Empty filename")
                    continue
                try:
                    os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, new_name))
                    file_count += 1
                except OSError as e:
                    print(f"\nError renaming file '{filename}' to '{new_name}': {e}", file=sys.stderr)
                    all_errors.append(f"\nError renaming file '{filename}' to '{new_name}': {e}")
                except Exception as e:
                    print(f"Error type: {type(e)}")
                    print(f"\nError renaming file '{filename}' to '{new_name}': {e}", file=sys.stderr)
                    all_errors.append(f"\nError renaming file '{filename}' to '{new_name}': {e}")

        # Renaming directories
        for dirname in dirnames:
            all_dirs += 1
            new_name = remove_substrings(dirname, to_remove)
            if new_name != dirname:
                if new_name == "":
                    print(f"\nError renaming directory '{dirname}' to '{new_name}': Empty directory name", file=sys.stderr)
                    all_errors.append(f"\nError renaming directory '{dirname}' to '{new_name}': Empty directory name")
                    continue
                try:
                    os.rename(os.path.join(dirpath, dirname), os.path.join(dirpath, new_name))
                    dir_count += 1
                except OSError as e:
                    print(f"\nError renaming directory '{dirname}' to '{new_name}': {e}", file=sys.stderr)
                    all_errors.append(f"\nError renaming directory '{dirname}' to '{new_name}': {e}")
                except Exception as e:
                    print(f"Error type: {type(e)}")
                    print(f"\nError renaming directory '{dirname}' to '{new_name}': {e}", file=sys.stderr)
                    all_errors.append(f"\nError renaming directory '{dirname}' to '{new_name}': {e}")
    for error in all_errors:
        print(color_text(error, "31"), file=sys.stderr)

    print(f"\n{color_text('Summary:', '1;4;34')}")
    print(f"Directories renamed: {color_text(dir_count, '32')}/{all_dirs}")
    print(f"Files renamed: {color_text(file_count, '32')}/{all_files}")
    print(f"Errors: {color_text(len(all_errors), '31')}")
    if all_errors:
        print(color_text("Please check the errors above.", "31"))