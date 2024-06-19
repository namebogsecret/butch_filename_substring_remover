
import os
import sys
import argparse

from butch_filename_substring_remover import rename_files_and_dirs

def main() -> None:
    parser = argparse.ArgumentParser(description='Batch renamer script')
    parser.add_argument('root_directory', type=str, help='Root directory to rename files and folders in')
    parser.add_argument('substrings_to_remove', nargs='+', help='List of substrings to remove')
    args = parser.parse_args()

    # Check if the directory exists
    if not os.path.isdir(args.root_directory):
        print(f"Error: The directory {args.root_directory} does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    # Check if the directory is writable
    if not os.access(args.root_directory, os.W_OK):
        print(f"Error: The directory {args.root_directory} is not writable.", file=sys.stderr)
        sys.exit(1)

    # Warning about potential dangers of running the script in system directories
    system_dirs = ["/", "/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc", "/root", "/sbin", "/sys", "/usr", "/var"]
    if os.path.abspath(args.root_directory) in system_dirs:
        print("Error: It is not safe to run this script in system directories.", file=sys.stderr)
        sys.exit(1)

    # Perform renaming of files and directories
    rename_files_and_dirs(args.root_directory, set(args.substrings_to_remove))

if __name__ == '__main__':
    main()
