"""
M4S to MP3 converter package
"""
from .converter import convert_m4s_to_mp3, convert_multiple_m4s_to_mp3, merge_m4s_files_to_mp3

__all__ = [
    "convert_m4s_to_mp3",
    "convert_multiple_m4s_to_mp3", 
    "merge_m4s_files_to_mp3"
]