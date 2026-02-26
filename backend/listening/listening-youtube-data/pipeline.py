#!/usr/bin/env python3
"""
Audio Slicer Pipeline

A simple CLI tool that downloads YouTube videos and slices them into audio clips.
Processes videos through 2 nodes: Download → Slice
"""

import json
import os
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Third-party imports
import yt_dlp


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Initialize logging to both file and console."""
    os.makedirs('logs', exist_ok=True)
    log_file = f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_time(seconds):
    """Convert seconds to XXmYYs format.
    
    Args:
        seconds: Integer seconds
        
    Returns:
        String in format "XXmYYs" (e.g., "01m25s")
    """
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}m{secs:02d}s"


def parse_time(time_val):
    """Convert time value (int seconds or str "m:s") to integer seconds.
    
    Args:
        time_val: Integer seconds or String in "m:s" or "h:m:s" format.
        
    Returns:
        Total seconds as integer.
    """
    if isinstance(time_val, int):
        return time_val
    if isinstance(time_val, str):
        if ':' in time_val:
            parts = time_val.split(':')
            if len(parts) == 2:  # m:s
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # h:m:s
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        try:
            return int(time_val)
        except ValueError:
            logger.error(f"Invalid time format: {time_val}")
            raise
    return time_val


def get_video_id(youtube_url):
    """Extract unique video ID from YouTube URL.
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Video ID string
    """
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info.get('id')


# ============================================================================
# NODE 1: YOUTUBE DOWNLOAD
# ============================================================================

def node_1_download(youtube_url):
    """Download YouTube video as audio only with automated fallback strategies.
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Path to downloaded audio file
        
    Raises:
        Exception: If all download strategies fail
    """
    video_id = get_video_id(youtube_url)
    if not video_id:
        raise Exception("Could not extract video ID from URL")
        
    output_path = f"source_audio/{video_id}.mp3"
    
    if os.path.exists(output_path):
        logger.info(f"Audio for {video_id} already exists, skipping download")
        return output_path
    
    os.makedirs("source_audio", exist_ok=True)
    
    # Template for output filename
    # yt-dlp might use different extensions before conversion, 
    # but we want to know where the final mp3 ends up.
    out_tmpl = f"source_audio/{video_id}.%(ext)s"
    
    # Multiple download strategies for reliability
    strategies = [
        {
            'name': 'Standard with modern user-agent',
            'opts': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': out_tmpl,
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            }
        },
        {
            'name': 'With extractor args',
            'opts': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': out_tmpl,
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            }
        },
        {
            'name': 'iOS client',
            'opts': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': out_tmpl,
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'youtube': {'player_client': ['ios']}},
            }
        },
        {
            'name': 'With cookies (if available)',
            'opts': {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': out_tmpl,
                'quiet': True,
                'no_warnings': True,
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            }
        },
    ]
    
    last_error = None
    
    for i, strategy in enumerate(strategies, 1):
        # Skip cookie strategy if no cookies file
        if strategy['opts'].get('cookiefile') is None and 'cookies' in strategy['name']:
            continue
            
        logger.info(f"Attempting download strategy {i}/{len(strategies)}: {strategy['name']}")
        
        try:
            with yt_dlp.YoutubeDL(strategy['opts']) as ydl:
                ydl.download([youtube_url])
            logger.info(f"✓ Downloaded successfully using: {strategy['name']}")
            logger.info(f"Saved to: {output_path}")
            return output_path
        except Exception as e:
            last_error = e
            logger.warning(f"✗ Strategy '{strategy['name']}' failed: {str(e)[:100]}")
            continue
    
    # All strategies failed
    logger.error("")
    logger.error("=" * 60)
    logger.error("All automated download strategies failed!")
    logger.error("=" * 60)
    logger.error(f"Last error: {last_error}")
    logger.error("")
    logger.error("This is likely due to YouTube's anti-bot protection.")
    logger.error("The video may have regional restrictions or require authentication.")
    logger.error("")
    logger.error("Suggestions:")
    logger.error("1. Try a different YouTube video URL")
    logger.error("2. Check if the video is publicly accessible")
    logger.error("3. Verify your internet connection")
    logger.error("=" * 60)
    
    raise Exception(f"All download strategies failed. Last error: {last_error}")


# ============================================================================
# NODE 2: AUDIO SLICING
# ============================================================================

def node_2_slice(audio_path, ranges):
    """Slice full audio into clips based on time ranges.
    
    Args:
        audio_path: Path to the source audio file
        ranges: List of dicts with 'start' and 'end' keys (seconds or "m:s")
        
    Returns:
        List of clip directory paths
    """
    os.makedirs("clips", exist_ok=True)
    clip_dirs = []
    
    for i, range_obj in enumerate(ranges, start=1):
        start = parse_time(range_obj['start'])
        end = parse_time(range_obj['end'])
        
        # Format: clip_01_00m80s_01m45s
        clip_name = f"clip_{i:02d}_{format_time(start)}_{format_time(end)}"
        clip_dir = f"clips/{clip_name}"
        os.makedirs(clip_dir, exist_ok=True)
        clip_dirs.append(clip_dir)
        
        output_file = f"{clip_dir}/audio.mp3"
        checkpoint = f"{clip_dir}/.done_slice"
        
        if os.path.exists(checkpoint):
            logger.info(f"{clip_name}: Already sliced, skipping")
            continue
        
        # FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(start),
            '-to', str(end),
            '-i', audio_path,
            '-acodec', 'copy',
            output_file
        ]
        
        try:
            logger.info(f"{clip_name}: Slicing audio...")
            subprocess.run(cmd, check=True, capture_output=True)
            # Create checkpoint
            Path(checkpoint).touch()
            logger.info(f"{clip_name}: Sliced successfully")
        except Exception as e:
            logger.error(f"ERROR slicing {clip_name}: {e}")
    
    return clip_dirs


# ============================================================================
# MAIN PIPELINE RUNNER
# ============================================================================

def main():
    """Main pipeline execution."""
    # Load input configuration
    if not os.path.exists('input.json'):
        logger.error("input.json not found! Please create it first.")
        return
    
    with open('input.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    youtube_url = config['youtube_url']
    ranges = config['ranges']
    
    logger.info("=" * 60)
    logger.info("AUDIO SLICER PIPELINE START")
    logger.info("=" * 60)
    logger.info(f"YouTube URL: {youtube_url}")
    logger.info(f"Ranges: {ranges}")
    
    # Node 1: Download
    logger.info("-" * 60)
    logger.info("Node 1: Download")
    logger.info("-" * 60)
    try:
        audio_path = node_1_download(youtube_url)
    except Exception as e:
        logger.error(f"Download failed: {e}")
        logger.error("Pipeline aborted")
        return
    
    # Node 2: Slice
    logger.info("-" * 60)
    logger.info("Node 2: Slice")
    logger.info("-" * 60)
    clip_dirs = node_2_slice(audio_path, ranges)
    
    if not clip_dirs:
        logger.error("No clips created, pipeline aborted")
        return
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Output: {len(clip_dirs)} audio clips generated")
    logger.info(f"Location: clips/")


if __name__ == "__main__":
    main()
