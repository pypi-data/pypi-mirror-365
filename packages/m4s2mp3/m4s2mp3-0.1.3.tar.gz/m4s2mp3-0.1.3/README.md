# m4s2mp3

A Python package for converting M4S audio files to MP3 format.

## Features

-   Convert single M4S files to MP3
-   Convert all M4S files in a directory to MP3
-   Merge multiple M4S files into a single MP3 file
-   Command-line interface for easy usage

## Installation

```bash
pip install m4s2mp3
```

Note: This package depends on `pydub` which requires `ffmpeg` to be installed on your system. Please follow the
[pydub installation guide](https://github.com/jiaaro/pydub#installation) to install ffmpeg.

## Usage

### As a command-line tool

```bash
# Convert a single file
m4s2mp3 input.m4s

# Convert a single file with custom output name
m4s2mp3 input.m4s -o output.mp3

# Convert all m4s files in a directory
m4s2mp3 /path/to/m4s/files/

# Convert all m4s files to a custom output directory
m4s2mp3 /path/to/m4s/files/ -o /path/to/output/

# Merge all m4s files into a single mp3 file
m4s2mp3 /path/to/m4s/files/ --merge -o output.mp3
```

### As a Python library

```python
from m4s2mp3 import convert_m4s_to_mp3, convert_multiple_m4s_to_mp3, merge_m4s_files_to_mp3

# Convert a single file
convert_m4s_to_mp3("input.m4s", "output.mp3")

# Convert all m4s files in a directory
convert_multiple_m4s_to_mp3("/path/to/m4s/files/", "/path/to/output/")

# Merge all m4s files into a single mp3 file
merge_m4s_files_to_mp3("/path/to/m4s/files/", "merged_output.mp3")
```

## API

### convert_m4s_to_mp3(input_path: str, output_path: str = None) -> str

Convert a single M4S file to MP3 format.

-   `input_path`: Path to the input M4S file
-   `output_path`: Path for the output MP3 file. If not provided, uses the same name as input with .mp3 extension.
-   Returns: Path to the converted MP3 file

### convert_multiple_m4s_to_mp3(input_dir: str, output_dir: str = None) -> list

Convert all M4S files in a directory to MP3 format.

-   `input_dir`: Directory containing M4S files
-   `output_dir`: Directory for output MP3 files. If not provided, uses the same directory as input files.
-   Returns: List of paths to converted MP3 files

### merge_m4s_files_to_mp3(input_dir: str, output_path: str) -> str

Merge all M4S files in a directory into a single MP3 file.

-   `input_dir`: Directory containing M4S files
-   `output_path`: Path for the output MP3 file
-   Returns: Path to the merged MP3 file

## License

MIT
