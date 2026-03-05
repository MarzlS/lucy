#!/usr/bin/env python3
"""
Lucy's Ear - Microphone recording and speech-to-text transcription.

Usage:
    python3 ear.py record output.wav --duration 5
    python3 ear.py transcribe audio.wav
    python3 ear.py listen --duration 5
    python3 ear.py listen --until-silence

Requires:
    - GROQ_API_KEY environment variable (for Whisper transcription)
    - arecord for audio recording
"""

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

# Configuration
def get_groq_api_key():
    """Get Groq API key from environment or config file."""
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    # Try reading from nanobot config
    config_path = os.path.expanduser("~/.nanobot/config.json")
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path) as f:
                config = json.load(f)
            key = config.get("providers", {}).get("groq", {}).get("apiKey")
            if key:
                return key
        except Exception:
            pass
    return None

GROQ_API_KEY = get_groq_api_key()
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "whisper-large-v3-turbo")
MIC_DEVICE = os.environ.get("MIC_DEVICE", "plughw:1,0")
SAMPLE_RATE = 16000
CHANNELS = 1
DEFAULT_DURATION = 5  # seconds
DEFAULT_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "de")  # German default


def record_audio(
    output_path: str,
    duration: int = DEFAULT_DURATION,
    device: str = MIC_DEVICE,
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS
) -> bool:
    """Record audio from microphone using arecord."""
    try:
        cmd = [
            "arecord",
            "-D", device,
            "-f", "S16_LE",
            "-r", str(sample_rate),
            "-c", str(channels),
            "-d", str(duration),
            output_path
        ]
        print(f"Recording for {duration} seconds...")
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Recording saved to: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error recording audio: {e.stderr.decode() if e.stderr else e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: arecord not found. Install alsa-utils.", file=sys.stderr)
        return False


def record_until_silence(
    output_path: str,
    device: str = MIC_DEVICE,
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
    max_duration: int = 30,
    silence_threshold: float = 2.0
) -> bool:
    """Record audio until silence is detected.
    
    Note: This is a simplified implementation that records for a fixed duration.
    For true silence detection, we'd need to analyze audio levels in real-time.
    """
    # For now, use a reasonable default duration
    # TODO: Implement actual silence detection using sox or similar
    print("Recording... (speak now, will stop after brief pause)")
    return record_audio(output_path, duration=max_duration, device=device, 
                       sample_rate=sample_rate, channels=channels)


def transcribe_audio(
    audio_path: str,
    language: str = DEFAULT_LANGUAGE,
    prompt: str | None = None
) -> str | None:
    """Transcribe audio file using Groq Whisper API.
    
    Returns the transcribed text, or None on error.
    """
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY environment variable not set.", file=sys.stderr)
        return None
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}", file=sys.stderr)
        return None
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    try:
        with open(audio_path, "rb") as audio_file:
            files = {
                "file": (Path(audio_path).name, audio_file, "audio/wav"),
            }
            data = {
                "model": WHISPER_MODEL,
                "language": language,
                "response_format": "text"
            }
            if prompt:
                data["prompt"] = prompt
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    GROQ_API_URL,
                    headers=headers,
                    files=files,
                    data=data
                )
                response.raise_for_status()
                
                return response.text.strip()
                
    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return None
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return None


def listen(
    duration: int = DEFAULT_DURATION,
    language: str = DEFAULT_LANGUAGE,
    until_silence: bool = False
) -> str | None:
    """Record audio and transcribe it.
    
    Returns the transcribed text, or None on error.
    """
    # Create temp file for recording
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    
    try:
        # Record
        if until_silence:
            success = record_until_silence(temp_path)
        else:
            success = record_audio(temp_path, duration=duration)
        
        if not success:
            return None
        
        # Transcribe
        print("Transcribing...")
        text = transcribe_audio(temp_path, language=language)
        
        if text:
            print(f"Heard: {text}")
        
        return text
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def main():
    parser = argparse.ArgumentParser(description="Lucy's Ear - Speech Recognition")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # record command
    record_parser = subparsers.add_parser("record", help="Record audio from microphone")
    record_parser.add_argument("output", help="Output file path")
    record_parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                              help=f"Recording duration in seconds (default: {DEFAULT_DURATION})")
    record_parser.add_argument("--device", default=MIC_DEVICE, help="Audio input device")
    
    # transcribe command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe an audio file")
    transcribe_parser.add_argument("file", help="Audio file to transcribe")
    transcribe_parser.add_argument("--language", "-l", default=DEFAULT_LANGUAGE,
                                  help=f"Language code (default: {DEFAULT_LANGUAGE})")
    transcribe_parser.add_argument("--prompt", "-p", help="Optional prompt to guide transcription")
    
    # listen command (record + transcribe)
    listen_parser = subparsers.add_parser("listen", help="Record and transcribe speech")
    listen_parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                              help=f"Recording duration in seconds (default: {DEFAULT_DURATION})")
    listen_parser.add_argument("--language", "-l", default=DEFAULT_LANGUAGE,
                              help=f"Language code (default: {DEFAULT_LANGUAGE})")
    listen_parser.add_argument("--until-silence", "-s", action="store_true",
                              help="Record until silence is detected")
    
    args = parser.parse_args()
    
    if args.command == "record":
        success = record_audio(args.output, duration=args.duration, device=args.device)
        sys.exit(0 if success else 1)
    
    elif args.command == "transcribe":
        text = transcribe_audio(args.file, language=args.language, prompt=args.prompt)
        if text:
            print(text)
            sys.exit(0)
        sys.exit(1)
    
    elif args.command == "listen":
        text = listen(
            duration=args.duration,
            language=args.language,
            until_silence=args.until_silence
        )
        if text:
            sys.exit(0)
        sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
