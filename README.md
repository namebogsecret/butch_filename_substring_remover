```markdown
# Butch Filename Substring Remover

This is a batch renaming script to remove substrings from filenames and directories.

## Installation

You can install this package using pip:

```bash
pip install butch_filename_substring_remover
```

## Usage

### Command Line

```bash
butch-rename /path/to/directory substring1 substring2
```

### As a Module

```python
from butch_filename_substring_remover import rename_directory

root_directory = '/path/to/directory'
substrings_to_remove = ['substring1', 'substring2']

try:
    rename_directory(root_directory, substrings_to_remove)
    print("Renaming completed successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Example

Assume you have a directory with the following files:

```
/example_dir
    file1_test.txt
    file2_sample.txt
    subdir1_test
```

Running the following command:

```bash
butch-rename /example_dir test sample
```

will rename the files to:

```
/example_dir
    file1_.txt
    file2_.txt
    subdir1_
```

## License

MIT License

```
