
import os
import sys
from .utils import (
    remove_substrings,
    color_text,
    format_preview_line,
    generate_undo_script,
    create_progress_bar,
    should_process_file
)


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
        error_msg = f"Error renaming {item_type} '{old_name}' to '{new_name}': {e}"
        all_errors.append(error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error renaming {item_type} '{old_name}' to '{new_name}': {type(e).__name__}: {e}"
        all_errors.append(error_msg)
        return False


def count_items(root_dir: str, extensions: list[str] | None = None) -> tuple[int, int]:
    """Count total files and directories that will be scanned.

    Args:
        root_dir: The root directory to count items in.
        extensions: If provided, only count files with these extensions.

    Returns:
        Tuple of (total_files, total_dirs)
    """
    total_files = 0
    total_dirs = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        total_dirs += len(dirnames)
        for filename in filenames:
            if should_process_file(filename, extensions):
                total_files += 1

    return total_files, total_dirs


def collect_rename_operations(
    root_dir: str,
    to_remove: set[str],
    extensions: list[str] | None = None
) -> tuple[list[tuple[str, str, str, str]], list[str]]:
    """Collect all rename operations without executing them.

    Args:
        root_dir: The root directory to process.
        to_remove: Set of substrings to remove.
        extensions: If provided, only process files with these extensions.

    Returns:
        Tuple of (operations, errors) where operations is a list of
        (old_path, new_path, old_name, new_name) tuples and errors is a list of error messages.
    """
    operations = []
    errors = []

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        try:
            existing_items = set(os.listdir(dirpath))
        except OSError as e:
            errors.append(f"Cannot list directory '{dirpath}': {e}")
            continue

        # Process files
        for filename in filenames:
            if not should_process_file(filename, extensions):
                continue

            new_name = remove_substrings(filename, to_remove)

            if new_name != filename:
                if not is_valid_filename(new_name):
                    errors.append(f"Invalid filename result: '{filename}' → '{new_name}'")
                    continue

                if new_name in existing_items and new_name != filename:
                    errors.append(f"Name conflict: '{filename}' → '{new_name}' (already exists)")
                    continue

                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_name)
                operations.append((old_path, new_path, filename, new_name))
                existing_items.discard(filename)
                existing_items.add(new_name)

        # Process directories
        for dirname in dirnames:
            new_name = remove_substrings(dirname, to_remove)

            if new_name != dirname:
                if not is_valid_filename(new_name):
                    errors.append(f"Invalid directory name: '{dirname}' → '{new_name}'")
                    continue

                if new_name in existing_items and new_name != dirname:
                    errors.append(f"Name conflict: '{dirname}' → '{new_name}' (already exists)")
                    continue

                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, new_name)
                operations.append((old_path, new_path, dirname, new_name))
                existing_items.discard(dirname)
                existing_items.add(new_name)

    return operations, errors


def print_preview(operations: list[tuple[str, str, str, str]], to_remove: set[str]) -> None:
    """Print a colored preview of all rename operations.

    Args:
        operations: List of (old_path, new_path, old_name, new_name) tuples.
        to_remove: Set of substrings being removed (for highlighting).
    """
    if not operations:
        print("\n📋 " + color_text("No files or directories would be renamed.", "33"))
        return

    print("\n" + color_text("📋 Preview of changes:", "1;36"))
    print(color_text("   (removed parts shown in ", "90") + color_text("strikethrough red", "9;31") + color_text(")", "90"))
    print()

    # Group by directory for cleaner output
    by_dir: dict[str, list] = {}
    for old_path, new_path, old_name, new_name in operations:
        dir_path = os.path.dirname(old_path)
        if dir_path not in by_dir:
            by_dir[dir_path] = []
        by_dir[dir_path].append((old_name, new_name, os.path.isdir(old_path)))

    for dir_path, items in by_dir.items():
        # Show directory header
        print(f"  📂 {color_text(dir_path, '34')}")

        for old_name, new_name, is_dir in items:
            item_type = "directory" if is_dir else "file"
            line = format_preview_line(old_name, new_name, to_remove, item_type)
            print(line)
        print()


def ask_confirmation(operations: list, root_dir: str) -> bool:
    """Ask user for confirmation before proceeding.

    Args:
        operations: List of operations to perform.
        root_dir: The root directory being processed.

    Returns:
        True if user confirms, False otherwise.
    """
    file_count = sum(1 for op in operations if os.path.isfile(op[0]))
    dir_count = len(operations) - file_count

    print(color_text("─" * 50, "90"))
    print(f"\n📊 " + color_text("Summary:", "1"))
    print(f"   📁 Directories to rename: {color_text(dir_count, '33')}")
    print(f"   📄 Files to rename: {color_text(file_count, '33')}")
    print(f"   📂 Location: {color_text(root_dir, '34')}")
    print()

    try:
        response = input(color_text("Proceed with renaming? [y/N]: ", "1;33")).strip().lower()
        return response in ('y', 'yes')
    except EOFError:
        return False


def rename_files_and_dirs(
    root_dir: str,
    to_remove: set[str],
    dry_run: bool = False,
    skip_confirm: bool = False,
    extensions: list[str] | None = None,
    undo_file: str | None = None,
    no_undo: bool = False
) -> None:
    """Renames files and folders in the specified directory.

    Args:
        root_dir: The root directory to rename files and folders in.
        to_remove: A set of substrings to remove from the names.
        dry_run: If True, only preview changes without renaming.
        skip_confirm: If True, skip the confirmation prompt.
        extensions: If provided, only process files with these extensions.
        undo_file: Path for the undo script.
        no_undo: If True, don't generate an undo script.
    """
    # Print header
    print()
    print(color_text("🔄 Butch Filename Substring Remover", "1;36"))
    print(color_text("─" * 50, "90"))

    # Show what we're looking for
    substrings_str = ", ".join(f"'{color_text(s, '33')}'" for s in to_remove)
    print(f"📂 Directory: {color_text(root_dir, '34')}")
    print(f"🔍 Removing: {substrings_str}")
    if extensions:
        ext_str = ", ".join(color_text(e, '35') for e in extensions)
        print(f"📎 Extensions: {ext_str}")
    if dry_run:
        print(f"👁️  Mode: {color_text('DRY RUN (preview only)', '33')}")
    print()

    # Collect all operations first
    print(f"🔍 Scanning files...", end="", flush=True)
    operations, errors = collect_rename_operations(root_dir, to_remove, extensions)
    print(f" {color_text('Done!', '32')}")

    # Show preview
    print_preview(operations, to_remove)

    # Show errors found during scan
    if errors:
        print(color_text("⚠️  Issues found during scan:", "33"))
        for error in errors:
            print(f"   {color_text('•', '31')} {error}")
        print()

    # If dry run, stop here
    if dry_run:
        file_count = sum(1 for op in operations if os.path.isfile(op[0]))
        dir_count = len(operations) - file_count
        print(color_text("─" * 50, "90"))
        print(f"\n💡 {color_text('DRY RUN COMPLETE', '1;33')}")
        print(f"   Would rename {color_text(file_count, '32')} files and {color_text(dir_count, '32')} directories")
        print(f"   Run without {color_text('--dry-run', '36')} to apply changes\n")
        return

    # If no operations, exit early
    if not operations:
        print(color_text("✨ Nothing to rename!", "32"))
        return

    # Ask for confirmation
    if not skip_confirm:
        if not ask_confirmation(operations, root_dir):
            print(f"\n{color_text('❌ Operation cancelled.', '31')}\n")
            return
        print()

    # Execute operations
    print(color_text("🚀 Renaming files...", "1"))
    print()

    successful_ops = []
    rename_errors = []
    total = len(operations)

    for i, (old_path, new_path, old_name, new_name) in enumerate(operations, 1):
        # Show progress
        progress = create_progress_bar(i, total, 25)
        item_type = "📁" if os.path.isdir(old_path) else "📄"
        status_line = f"\r   {progress} {item_type} {old_name[:30]}"
        print(f"{status_line:<80}", end="", flush=True)

        if rename_item(old_path, new_path, "item", rename_errors):
            successful_ops.append((old_path, new_path))

    print(f"\r   {create_progress_bar(total, total, 25)} {color_text('Complete!', '32'):<50}")
    print()

    # Generate undo script
    if successful_ops and not no_undo:
        try:
            script_path = generate_undo_script(successful_ops, undo_file)
            print(f"💾 Undo script saved: {color_text(script_path, '36')}")
        except Exception as e:
            print(f"⚠️  Could not save undo script: {e}", file=sys.stderr)

    # Print errors
    if rename_errors:
        print()
        print(color_text("❌ Errors during renaming:", "31"))
        for error in rename_errors:
            print(f"   {color_text('•', '31')} {error}")

    # Print summary
    file_count = sum(1 for op in successful_ops if os.path.isfile(op[1]))
    dir_count = len(successful_ops) - file_count
    total_errors = len(errors) + len(rename_errors)

    print()
    print(color_text("─" * 50, "90"))
    print(f"\n{color_text('✨ Summary:', '1;32')}")
    print(f"   📁 Directories renamed: {color_text(dir_count, '32')}")
    print(f"   📄 Files renamed: {color_text(file_count, '32')}")
    if total_errors > 0:
        print(f"   ⚠️  Errors: {color_text(total_errors, '31')}")
    print()

    if successful_ops and not no_undo:
        print(f"💡 To undo, run: {color_text(f'bash {script_path}' if script_path.endswith('.sh') else script_path, '36')}")
        print()
