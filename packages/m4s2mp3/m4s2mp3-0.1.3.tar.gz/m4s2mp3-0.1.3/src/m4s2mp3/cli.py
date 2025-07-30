"""
Command line interface for m4s2mp3 converter
"""
import argparse
import sys
import os
from pathlib import Path
from m4s2mp3.converter import convert_m4s_to_mp3, convert_multiple_m4s_to_mp3, merge_m4s_files_to_mp3


def main():
    parser = argparse.ArgumentParser(
        description="Convert M4S files to MP3 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  m4s2mp3 input.m4s                           # Convert single file
  m4s2mp3 input.m4s -o output.mp3             # Convert single file with custom output name
  m4s2mp3 /path/to/m4s/files/                 # Convert all m4s files in directory
  m4s2mp3 /path/to/m4s/files/ -o /path/to/output/  # Convert all m4s files to custom output directory
  m4s2mp3 /path/to/m4s/files/ --merge -o output.mp3  # Merge all m4s files into single mp3
        """
    )
    
    parser.add_argument(
        "input",
        help="Input m4s file or directory containing m4s files"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file or directory path"
    )
    
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge all m4s files into a single mp3 file (requires directory input)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    try:
        # Check if input exists
        if not os.path.exists(args.input):
            print(f"Error: Input path does not exist: {args.input}")
            return 1
        
        # Handle single file conversion
        if os.path.isfile(args.input) and args.input.lower().endswith('.m4s'):
            if args.merge:
                print("Error: --merge option requires directory input, not a single file")
                return 1
                
            output_path = convert_m4s_to_mp3(args.input, args.output)
            if args.verbose:
                print(f"Converted: {args.input} -> {output_path}")
            else:
                print(f"Converted to {output_path}")
        
        # Handle directory operations
        elif os.path.isdir(args.input):
            if args.merge:
                if not args.output:
                    print("Error: --merge option requires an output file path")
                    return 1
                output_path = merge_m4s_files_to_mp3(args.input, args.output)
                if args.verbose:
                    print(f"Merged all m4s files in {args.input} to {output_path}")
                else:
                    print(f"Merged to {output_path}")
            else:
                converted_files = convert_multiple_m4s_to_mp3(args.input, args.output)
                if args.verbose:
                    print(f"Converted {len(converted_files)} files:")
                    for f in converted_files:
                        print(f"  {f}")
                else:
                    print(f"Converted {len(converted_files)} files")
        else:
            print(f"Error: Invalid input. Must be a .m4s file or directory: {args.input}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())