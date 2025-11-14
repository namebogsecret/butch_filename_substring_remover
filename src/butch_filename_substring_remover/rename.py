
import os
import sys
from .utils import remove_substrings, color_text


def is_valid_filename(name: str) -> bool:
    """Check if the filename is valid (not empty, not just whitespace or dots).

    Args:
        name: The filename to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not name or name.strip() == "":
        return False
    if name in (".", ".."):
        return False
    # Check for names that are only whitespace or dots
    if name.replace(".", "").replace(" ", "") == "":
        return False
    return True


def rename_item(old_path: str, new_path: str, item_type: str, all_errors: list) -> bool:
    """Rename a file or directory and handle errors.

    Args:
        old_path: The current path of the item.
        new_path: The new path for the item.
        item_type: Type of item ('file' or 'directory').
        all_errors: List to append errors to.

    Returns:
        True if rename was successful, False otherwise.
    """
    old_name = os.path.basename(old_path)
    new_name = os.path.basename(new_path)

    try:
        os.rename(old_path, new_path)
        return True
    except OSError as e:
        error_msg = f"\nError renaming {item_type} '{old_name}' to '{new_name}': {e}"
        print(error_msg, file=sys.stderr)
        all_errors.append(error_msg)
        return False
    except Exception as e:
        error_msg = f"\nUnexpected error renaming {item_type} '{old_name}' to '{new_name}': {type(e).__name__}: {e}"
        print(error_msg, file=sys.stderr)
        all_errors.append(error_msg)
        return False


def rename_files_and_dirs(root_dir: str, to_remove: set[str]) -> None:
    """Renames files and folders in the specified directory.

    Args:
        root_dir: The root directory to rename files and folders in.
        to_remove: A set of substrings to remove from the names of files and folders.
    """
    max_length = 80
    all_errors = []
    dir_count = 0
    file_count = 0
    all_dirs = 0
    all_files = 0

    # Collect all directories first (to avoid issues with renaming during traversal)
    all_directories = []
    all_files_list = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        line = f'Scanning: {dirpath}'
        current_length = len(line)
        max_length = max(max_length, current_length)
        print(f'\r{line}{" " * (max_length - current_length)}', end='', flush=True)

        # Collect directories with their full paths
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            all_directories.append(full_path)
            all_dirs += 1

        # Collect files with their full paths
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            all_files_list.append(full_path)
            all_files += 1

    print()  # New line after scanning

    # Process files first
    existing_files = set()
    for file_path in all_files_list:
        dirpath = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Track existing files in this directory
        if dirpath not in existing_files:
            existing_files = set(os.listdir(dirpath))

        new_name = remove_substrings(filename, to_remove)

        if new_name != filename:
            # Validate new filename
            if not is_valid_filename(new_name):
                error_msg = f"\nError: Invalid filename result when renaming '{filename}' to '{new_name}': Empty or invalid name"
                print(error_msg, file=sys.stderr)
                all_errors.append(error_msg)
                continue

            # Check for name conflicts
            if new_name in existing_files and new_name != filename:
                error_msg = f"\nError: Name conflict when renaming '{filename}' to '{new_name}': File already exists"
                print(error_msg, file=sys.stderr)
                all_errors.append(error_msg)
                continue

            old_path = file_path
            new_path = os.path.join(dirpath, new_name)

            if rename_item(old_path, new_path, "file", all_errors):
                file_count += 1
                # Update tracking set
                existing_files.discard(filename)
                existing_files.add(new_name)

    # Sort directories by depth (deepest first) to avoid renaming parent before children
    all_directories.sort(key=lambda x: x.count(os.sep), reverse=True)

    # Process directories from deepest to shallowest
    for dir_path in all_directories:
        if not os.path.exists(dir_path):
            # Directory might have been renamed as part of parent rename
            continue

        dirpath = os.path.dirname(dir_path)
        dirname = os.path.basename(dir_path)

        # Get existing items in parent directory
        existing_items = set(os.listdir(dirpath))

        new_name = remove_substrings(dirname, to_remove)

        if new_name != dirname:
            # Validate new directory name
            if not is_valid_filename(new_name):
                error_msg = f"\nError: Invalid directory name result when renaming '{dirname}' to '{new_name}': Empty or invalid name"
                print(error_msg, file=sys.stderr)
                all_errors.append(error_msg)
                continue

            # Check for name conflicts
            if new_name in existing_items and new_name != dirname:
                error_msg = f"\nError: Name conflict when renaming directory '{dirname}' to '{new_name}': Directory already exists"
                print(error_msg, file=sys.stderr)
                all_errors.append(error_msg)
                continue

            old_path = dir_path
            new_path = os.path.join(dirpath, new_name)

            if rename_item(old_path, new_path, "directory", all_errors):
                dir_count += 1

    # Print all errors
    for error in all_errors:
        print(color_text(error, "31"), file=sys.stderr)

    # Print summary
    print(f"\n{color_text('Summary:', '1;4;34')}")
    print(f"Directories renamed: {color_text(dir_count, '32')}/{all_dirs}")
    print(f"Files renamed: {color_text(file_count, '32')}/{all_files}")
    print(f"Errors: {color_text(len(all_errors), '31')}")
    if all_errors:
        print(color_text("Please check the errors above.", "31"))
