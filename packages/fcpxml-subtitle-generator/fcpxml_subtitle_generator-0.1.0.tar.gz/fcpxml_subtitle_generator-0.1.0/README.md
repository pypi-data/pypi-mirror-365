# Subtitle Automation

A CLI tool to generate Final Cut Pro compatible subtitle files from audio/video files using OpenAI's Whisper.

## Features

- **Multiple file format support**: MP3, MP4, WAV, M4A
- **Automatic audio extraction**: Extracts audio from MP4 video files
- **AI transcription**: Uses OpenAI Whisper for accurate speech-to-text
- **Final Cut Pro integration**: Generates FCPXML subtitle files compatible with Final Cut Pro
- **Multiple model sizes**: Choose from tiny, base, small, medium, or large Whisper models
- **Language support**: Auto-detect or specify language for better accuracy
- **Frame-accurate timing**: Generates subtitles with precise frame boundaries (30fps)

## Installation

This project uses `uv` for dependency management. Make sure you have Python 3.13+ installed.

```bash
# Clone the repository
git clone <repository-url>
cd subtitle_automation

# Install dependencies using uv
uv sync
```

## Usage

### Basic Usage

```bash
# Generate subtitles from an MP3 file
python subtitle_generator.py input.mp3

# Generate subtitles from an MP4 file (audio will be extracted)
python subtitle_generator.py input.mp4
```

### Advanced Options

```bash
# Specify output file
python subtitle_generator.py input.mp3 -o custom_subtitles.fcpxml

# Use a different Whisper model (higher quality but slower)
python subtitle_generator.py input.mp3 -m large

# Specify language for better accuracy
python subtitle_generator.py input.mp3 -l en

# Combine all options
python subtitle_generator.py input.mp4 -o subtitles.fcpxml -m medium -l ko
```

### Command Line Arguments

- `input_file`: Path to the input audio/video file (MP3, MP4, WAV, M4A)
- `-o, --output`: Output FCPXML file path (default: `input_filename.fcpxml`)
- `-m, --model`: Whisper model size - `tiny`, `base`, `small`, `medium`, `large` (default: `base`)
- `-l, --language`: Language code (e.g., 'en', 'es', 'fr', 'ko', 'ja'). Auto-detect if not specified

## Dependencies

- **openai-whisper**: AI transcription engine
- **moviepy**: Video/audio processing for MP4 files
- **Python 3.13+**: Required Python version

## Output Format

The tool generates FCPXML files that can be directly imported into Final Cut Pro as subtitle tracks. The generated subtitles include:

- Precise timing synchronized to 30fps frame boundaries
- XML-escaped text content
- Standard FCPXML 1.11 format structure
- Basic Title effect references for Final Cut Pro compatibility

## Technical Details

- **Frame Rate**: 30fps (1001/30000s per frame)
- **Audio Processing**: Temporary WAV files for MP4 audio extraction
- **Text Encoding**: UTF-8 with XML escaping
- **Timing Precision**: Frame-accurate subtitle positioning

## Examples

```bash
# Process a podcast MP3 file
python subtitle_generator.py podcast.mp3

# Process a video interview with Korean language
python subtitle_generator.py interview.mp4 -l ko -m medium

# Generate subtitles with high accuracy model
python subtitle_generator.py presentation.mp4 -m large -o presentation_subs.fcpxml
```

## License

This project is open source. Please check the license file for details.