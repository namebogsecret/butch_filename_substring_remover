
import os
import sys
import argparse

from .rename_directory import rename_directory


def main() -> None:
    parser = argparse.ArgumentParser(
        description='🔄 Batch rename files and folders by removing substrings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  butch-rename /path/to/folder _old _backup
      Remove "_old" and "_backup" from all filenames

  butch-rename --dry-run /path/to/folder _test
      Preview changes without actually renaming

  butch-rename -y /path/to/folder _temp
      Skip confirmation prompt

  butch-rename --ext .txt .pdf /path/to/folder _draft
      Only process .txt and .pdf files

  butch-rename --undo-file restore.sh /path/to/folder _old
      Save undo script to restore.sh
"""
    )

    parser.add_argument(
        'root_directory',
        type=str,
        help='Root directory to rename files and folders in'
    )
    parser.add_argument(
        'substrings_to_remove',
        nargs='+',
        help='Substrings to remove from filenames'
    )
    parser.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='Preview changes without actually renaming files'
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser.add_argument(
        '--ext',
        nargs='+',
        metavar='EXT',
        help='Only process files with these extensions (e.g., --ext .txt .pdf)'
    )
    parser.add_argument(
        '--undo-file',
        type=str,
        metavar='PATH',
        help='Path for the undo script (default: auto-generated)'
    )
    parser.add_argument(
        '--no-undo',
        action='store_true',
        help='Do not generate an undo script'
    )

    args = parser.parse_args()

    try:
        rename_directory(
            root_directory=args.root_directory,
            substrings_to_remove=args.substrings_to_remove,
            dry_run=args.dry_run,
            skip_confirm=args.yes,
            extensions=args.ext,
            undo_file=args.undo_file,
            no_undo=args.no_undo
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
