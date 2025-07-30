#!/usr/bin/env python3
"""
CLI tool to generate Final Cut Pro compatible subtitle files from MP3/MP4 files using Whisper.
"""

import argparse
import os
import sys
from pathlib import Path
import whisper
from moviepy import VideoFileClip
import tempfile


def extract_audio_from_video(video_path, output_path):
    """Extract audio from MP4 file and save as temporary WAV file."""
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path, verbose=False, logger=None)
        audio.close()
        video.close()
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False


def transcribe_audio(audio_path, model_size="base", language=None):
    """Transcribe audio file using Whisper and return segments with timestamps."""
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, word_timestamps=True, language=language)
        return result
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


def format_time_fcpxml(seconds):
    """Convert seconds to Final Cut Pro FCPXML time format on frame boundaries."""
    # Round to nearest frame boundary for 30fps (1001/30000s per frame)
    frame_duration = 1001/30000
    frames = round(seconds / frame_duration)
    return f"{frames * 1001}/30000s"


def generate_fcpxml_subtitle(transcription_result, output_path):
    """Generate Final Cut Pro compatible FCPXML subtitle file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # FCPXML header
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE fcpxml>\n')
            f.write('<fcpxml version="1.11">\n')
            f.write('  <resources>\n')
            f.write('    <format id="r1" name="FFVideoFormat1080p30" frameDuration="1001/30000s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>\n')
            f.write('    <effect id="r2" name="Basic Title" uid=".../Titles.localized/Bumper:Opener.localized/Basic Title.localized/Basic Title.moti"/>\n')
            f.write('  </resources>\n')
            f.write('  <library location="">\n')
            f.write('    <event name="Subtitles">\n')
            f.write('      <project name="Generated Subtitles">\n')
            f.write('        <sequence format="r1" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">\n')
            f.write('          <spine>\n')
            
            # Generate title clips according to DTD
            for i, segment in enumerate(transcription_result['segments']):
                start_time = format_time_fcpxml(segment['start'])
                duration = format_time_fcpxml(segment['end'] - segment['start'])
                text = segment['text'].strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
                
                f.write(f'            <title ref="r2" name="Basic Title" offset="{start_time}" duration="{duration}" start="3600s">\n')
                f.write(f'              <text>{text}</text>\n')
                f.write(f'            </title>\n')
            
            # FCPXML footer
            f.write('          </spine>\n')
            f.write('        </sequence>\n')
            f.write('      </project>\n')
            f.write('    </event>\n')
            f.write('  </library>\n')
            f.write('</fcpxml>\n')
        
        return True
    except Exception as e:
        print(f"Error generating FCPXML file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate Final Cut Pro compatible subtitles from MP3/MP4 files using Whisper"
    )
    parser.add_argument(
        "input_file",
        help="Input MP3 or MP4 file path"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output subtitle file path (default: input_filename.fcpxml)"
    )
    parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "-l", "--language",
        help="Language code for transcription (e.g., 'en', 'es', 'fr', 'ko', 'ja'). Auto-detect if not specified."
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Check file extension
    file_ext = input_path.suffix.lower()
    if file_ext not in ['.mp3', '.mp4', '.wav', '.m4a']:
        print(f"Error: Unsupported file format '{file_ext}'. Supported: .mp3, .mp4, .wav, .m4a")
        sys.exit(1)
    
    # Set output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.fcpxml')
    
    print(f"Processing: {input_path}")
    print(f"Model: {args.model}")
    if args.language:
        print(f"Language: {args.language}")
    else:
        print("Language: Auto-detect")
    print(f"Output: {output_path}")
    
    # Handle different file types
    audio_path = str(input_path)
    temp_audio_file = None
    
    if file_ext == '.mp4':
        print("Extracting audio from video...")
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_file.close()
        
        if not extract_audio_from_video(str(input_path), temp_audio_file.name):
            print("Failed to extract audio from video.")
            sys.exit(1)
        
        audio_path = temp_audio_file.name
    
    # Transcribe audio
    print("Transcribing audio...")
    transcription = transcribe_audio(audio_path, args.model, args.language)
    
    if transcription is None:
        print("Transcription failed.")
        if temp_audio_file:
            os.unlink(temp_audio_file.name)
        sys.exit(1)
    
    # Generate subtitle file
    print("Generating FCPXML subtitle file...")
    if generate_fcpxml_subtitle(transcription, output_path):
        print(f"Subtitle file created: {output_path}")
    else:
        print("Failed to generate subtitle file.")
        if temp_audio_file:
            os.unlink(temp_audio_file.name)
        sys.exit(1)
    
    # Clean up temporary file
    if temp_audio_file:
        os.unlink(temp_audio_file.name)
    
    print("Done!")


if __name__ == "__main__":
    main()