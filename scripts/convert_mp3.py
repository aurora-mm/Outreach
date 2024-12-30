# Script for converting MP3 file according to Outreach requirements

import os
import subprocess

def convert_to_mp3(input_file, output_file):
    metadata = {
        "artist": "LR Friberg",
        "album": "Cities Visited",
        "title": "",  # Placeholder; title tag should simply be present
        "date": "",  # Placeholder; title tag should simply be present
        "genre": "Field Recordings",
    }

    metadata_args = []
    for key, value in metadata.items():
        metadata_args.extend(["-metadata", f"{key}={value}"])

    # Build the FFmpeg command
    command = [
        "ffmpeg",
        "-i", input_file,  # Input audio file
        "-codec:a", "libmp3lame",
         "-b:a", "320k",  # Constant bitrate of 320 kbps
        "-ar", "44100",  # Sampling rate
        *metadata_args,
        "-id3v2_version", "3",  # Use ID3v2.3 for better compatibility
        output_file
    ]

    # Run the command
    subprocess.run(command, check=True)

def main():
    # Input audio file
    input_file = input("Enter the input audio file path: ").strip()
    if not os.path.isfile(input_file):
        print("Input file does not exist.")
        return

    # Output MP3 file
    output_file = "output.mp3"

    # Convert to MP3 with metadata
    try:
        convert_to_mp3(input_file, output_file)
        print(f"Conversion complete. File saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    main()