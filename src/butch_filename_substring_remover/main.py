
import os
import sys
import argparse

# import sys
# sys.path.append('/Volumes/Untitled/python/butch_filename_substring_remover/src')

from .rename_directory import rename_directory

def main() -> None:
    parser = argparse.ArgumentParser(description='Batch renamer script')
    parser.add_argument('root_directory', type=str, help='Root directory to rename files and folders in')
    parser.add_argument('substrings_to_remove', nargs='+', help='List of substrings to remove')
    args = parser.parse_args()

    try:
        rename_directory(args.root_directory, args.substrings_to_remove)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
