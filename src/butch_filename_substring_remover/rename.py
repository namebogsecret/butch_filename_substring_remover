
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

    Uses bottom-up traversal (topdown=False) to ensure that when we rename
    a directory, all its contents have already been processed. This allows
    renaming the entire tree in a single pass.

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

    # Use topdown=False to traverse from deepest directories to root.
    # This ensures that when we rename a directory, all its contents
    # have already been renamed, so paths remain valid throughout.
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        line = f'Processing: {dirpath}'
        current_length = len(line)
        max_length = max(max_length, current_length)
        print(f'\r{line}{" " * (max_length - current_length)}', end='', flush=True)

        # Get current items in this directory for conflict detection
        try:
            existing_items = set(os.listdir(dirpath))
        except OSError as e:
            error_msg = f"\nError: Cannot list directory '{dirpath}': {e}"
            print(error_msg, file=sys.stderr)
            all_errors.append(error_msg)
            continue

        # Process files in this directory
        for filename in filenames:
            all_files += 1
            new_name = remove_substrings(filename, to_remove)

            if new_name != filename:
                # Validate new filename
                if not is_valid_filename(new_name):
                    error_msg = f"\nError: Invalid filename result when renaming '{filename}' to '{new_name}': Empty or invalid name"
                    print(error_msg, file=sys.stderr)
                    all_errors.append(error_msg)
                    continue

                # Check for name conflicts
                if new_name in existing_items and new_name != filename:
                    error_msg = f"\nError: Name conflict when renaming '{filename}' to '{new_name}': File already exists"
                    print(error_msg, file=sys.stderr)
                    all_errors.append(error_msg)
                    continue

                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_name)

                if rename_item(old_path, new_path, "file", all_errors):
                    file_count += 1
                    # Update tracking set for subsequent conflict checks
                    existing_items.discard(filename)
                    existing_items.add(new_name)

        # Process subdirectories in this directory
        # Since we're using topdown=False, contents of subdirs are already processed
        for dirname in dirnames:
            all_dirs += 1
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

                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, new_name)

                if rename_item(old_path, new_path, "directory", all_errors):
                    dir_count += 1
                    # Update tracking set for subsequent conflict checks
                    existing_items.discard(dirname)
                    existing_items.add(new_name)

    print()  # New line after processing

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
