"""
M4S to MP3 converter module
"""
import os
from pydub import AudioSegment
from pathlib import Path
from typing import Optional, List


def convert_m4s_to_mp3(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Convert a single m4s file to mp3 format.
    
    Args:
        input_path (str): Path to the input m4s file
        output_path (str, optional): Path for the output mp3 file. 
                                    If not provided, uses the same name as input with .mp3 extension.
    
    Returns:
        str: Path to the converted mp3 file
    """
    # Check if input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Validate input file extension
    if not input_path.lower().endswith('.m4s'):
        raise ValueError("Input file must have .m4s extension")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.rsplit('.', 1)[0] + '.mp3'
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Load m4s file and convert to mp3
    audio = AudioSegment.from_file(input_path, format="mp4")
    audio.export(output_path, format="mp3")
    
    return output_path


def convert_multiple_m4s_to_mp3(input_dir: str, output_dir: Optional[str] = None) -> List[str]:
    """
    Convert all m4s files in a directory to mp3 format.
    
    Args:
        input_dir (str): Directory containing m4s files
        output_dir (str, optional): Directory for output mp3 files.
                                   If not provided, uses the same directory as input files.
    
    Returns:
        list: List of paths to converted mp3 files
    """
    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input path is not a directory: {input_dir}")
    
    # Generate output directory if not provided
    if output_dir is None:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    converted_files = []
    
    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.m4s'):
            input_path = os.path.join(input_dir, filename)
            output_filename = filename.rsplit('.', 1)[0] + '.mp3'
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert the file
            convert_m4s_to_mp3(input_path, output_path)
            converted_files.append(output_path)
    
    return converted_files


def merge_m4s_files_to_mp3(input_dir: str, output_path: str) -> str:
    """
    Merge all m4s files in a directory into a single mp3 file.
    
    Args:
        input_dir (str): Directory containing m4s files
        output_path (str): Path for the output mp3 file
    
    Returns:
        str: Path to the merged mp3 file
    """
    # Check if input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input path is not a directory: {input_dir}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Get all m4s files and sort them
    m4s_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.m4s')]
    m4s_files.sort()
    
    if not m4s_files:
        raise ValueError(f"No m4s files found in directory: {input_dir}")
    
    # Load and concatenate all audio segments
    combined = AudioSegment.empty()
    for filename in m4s_files:
        input_path = os.path.join(input_dir, filename)
        audio = AudioSegment.from_file(input_path, format="mp4")
        combined += audio
    
    # Export the combined audio
    combined.export(output_path, format="mp3")
    
    return output_path