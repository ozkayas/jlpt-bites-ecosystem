# Audio Slicer Pipeline

A Python CLI tool that downloads YouTube videos and slices them into audio clips based on specified time ranges.

## Features

- **Automated YouTube Download**: Multiple fallback strategies for reliable downloads
- **Audio Slicing**: Precise FFmpeg-based audio extraction
- **Checkpoint System**: Resume processing from where you left off
- **Python 3.13 Virtual Environment**: Isolated, reproducible setup

## System Requirements

- **Python**: 3.13 (recommended)
- **FFmpeg**: Required for audio processing
  - macOS: `brew install ffmpeg`
  - Linux: `apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

### Quick Setup (Recommended)

The project includes a virtual environment with Python 3.13 for optimal performance.

```bash
cd "/Users/suatozkaya/Flutter Projects/jlpt-bites/listening audio workflow"

# Create virtual environment (already done)
# python3.13 -m venv venv

# Activate and install dependencies (already done)
# source venv/bin/activate
# pip install -r requirements.txt
```

### Manual Setup

If you need to reinstall:

```bash
# Create virtual environment with Python 3.13
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Setup

Create `input.json` in the project root:

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=XXXXXX",
  "ranges": [
    {"start": 80, "end": 105},
    {"start": 120, "end": 145}
  ]
}
```

- `youtube_url`: YouTube video URL
- `ranges`: Array of time ranges in seconds (start and end times)

## Usage

### Quick Start

Simply run the pipeline script:

```bash
./run.sh
```

This will automatically activate the virtual environment and run the pipeline.

### Manual Run

If you prefer to run manually:

```bash
source venv/bin/activate
python pipeline.py
```

The pipeline will:
1. Download the YouTube video as audio
2. Slice it into clips based on your time ranges

## Output Structure

```
project/
├── source_audio/
│   └── full_audio.mp3              # Downloaded audio
├── clips/
│   ├── clip_01_01m20s_01m45s/
│   │   ├── audio.mp3               # Sliced audio clip
│   │   └── .done_slice             # Checkpoint file
│   └── clip_02_02m00s_02m25s/
│       ├── audio.mp3
│       └── .done_slice
└── logs/
    └── pipeline_YYYYMMDD_HHMMSS.log
```

### Output Files

**audio.mp3**
- High-quality MP3 audio clip
- Extracted from the specified time range
- Ready to use in your application

**.done_slice**
- Checkpoint file
- Indicates this clip has been processed
- Enables resume functionality

## Resume Functionality

The pipeline creates checkpoint files (`.done_slice`) for each clip. If the pipeline is interrupted, simply run it again:

```bash
./run.sh
```

It will skip already-processed clips and continue from where it left off.

## Error Handling

The pipeline uses an MVP approach to error handling:
- Errors are logged to `logs/pipeline_*.log`
- Failed clips are skipped
- Processing continues with remaining clips
- You can manually fix issues and re-run

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg using your system's package manager (see System Requirements).

### "403 Forbidden"
YouTube blocked the download attempt. See [YOUTUBE_TROUBLESHOOTING.md](YOUTUBE_TROUBLESHOOTING.md) for solutions.

## Limitations (MVP)

- Download success depends on YouTube's anti-bot measures
- Slicing precision depends on keyframes (FFmpeg -ss placement)
- No complex retry logic for failed operations

## License

MIT
