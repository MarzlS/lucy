#!/usr/bin/env python3
"""
Lucy's Voice - Text-to-Speech using edge-tts (Microsoft Edge TTS).

Usage:
    python3 voice.py say "Hello, I am Lucy!"
    python3 voice.py say "Hallo, ich bin Lucy!" --voice de-DE-SeraphinaMultilingualNeural
    python3 voice.py play /path/to/audio.wav
    python3 voice.py list-voices

Requires:
    - edge-tts (pip install edge-tts)
    - paplay or aplay for audio playback
"""

import argparse
import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Configuration
DEFAULT_VOICE = os.environ.get("TTS_VOICE", "de-DE-SeraphinaMultilingualNeural")
EDGE_TTS_PATH = os.path.expanduser("~/.local/bin/edge-tts")

# Some good voice options:
# German: de-DE-SeraphinaMultilingualNeural, de-DE-AmalaNeural, de-DE-KatjaNeural
# English: en-US-JennyNeural, en-US-AriaNeural, en-GB-SoniaNeural
FAVORITE_VOICES = [
    "de-DE-SeraphinaMultilingualNeural",
    "de-DE-AmalaNeural", 
    "de-DE-KatjaNeural",
    "de-DE-ConradNeural",
    "en-US-JennyNeural",
    "en-US-AriaNeural",
    "en-GB-SoniaNeural",
]


def play_audio(file_path: str) -> bool:
    """Play an audio file using paplay or aplay."""
    try:
        suffix = Path(file_path).suffix.lower()
        
        # Try paplay first (works with mp3)
        try:
            subprocess.run(["paplay", file_path], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback: convert to wav and use aplay
        if suffix == ".mp3":
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", file_path, "-ar", "24000", "-ac", "1", tmp_path],
                    check=True,
                    capture_output=True
                )
                subprocess.run(["aplay", tmp_path], check=True)
                return True
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        else:
            subprocess.run(["aplay", file_path], check=True)
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: No audio player found (paplay/aplay).", file=sys.stderr)
        return False


def text_to_speech(text: str, voice: str = DEFAULT_VOICE, output_path: str | None = None) -> str | None:
    """Convert text to speech using edge-tts.
    
    Returns the path to the generated audio file, or None on error.
    """
    if output_path:
        audio_path = output_path
    else:
        fd, audio_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
    
    try:
        # Use edge-tts CLI
        cmd = [EDGE_TTS_PATH, "--voice", voice, "--text", text, "--write-media", audio_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return audio_path
    except subprocess.CalledProcessError as e:
        print(f"edge-tts error: {e.stderr}", file=sys.stderr)
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return None
    except FileNotFoundError:
        print(f"Error: edge-tts not found at {EDGE_TTS_PATH}", file=sys.stderr)
        print("Install with: pip install --break-system-packages edge-tts", file=sys.stderr)
        return None


def say(text: str, voice: str = DEFAULT_VOICE, keep_audio: bool = False) -> bool:
    """Convert text to speech and play it."""
    print(f"Speaking: {text[:50]}..." if len(text) > 50 else f"Speaking: {text}")
    
    audio_path = text_to_speech(text, voice)
    if not audio_path:
        return False
    
    try:
        success = play_audio(audio_path)
        return success
    finally:
        if not keep_audio and audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)


def list_voices(filter_lang: str | None = None):
    """List available voices from edge-tts."""
    try:
        result = subprocess.run([EDGE_TTS_PATH, "--list-voices"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        
        if filter_lang:
            lines = [l for l in lines if filter_lang.lower() in l.lower()]
        
        for line in lines:
            print(line)
    except subprocess.CalledProcessError as e:
        print(f"Error listing voices: {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: edge-tts not found at {EDGE_TTS_PATH}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Lucy's Voice - Text-to-Speech with edge-tts")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # say command
    say_parser = subparsers.add_parser("say", help="Convert text to speech and play it")
    say_parser.add_argument("text", help="Text to speak")
    say_parser.add_argument("--voice", "-v", default=DEFAULT_VOICE, help="Voice to use")
    say_parser.add_argument("--save", "-s", help="Save audio to file instead of playing")
    
    # play command
    play_parser = subparsers.add_parser("play", help="Play an audio file")
    play_parser.add_argument("file", help="Audio file to play")
    
    # list-voices command
    list_parser = subparsers.add_parser("list-voices", help="List available voices")
    list_parser.add_argument("--lang", "-l", help="Filter by language (e.g. 'de', 'en')")
    
    args = parser.parse_args()
    
    if args.command == "say":
        if args.save:
            audio_path = text_to_speech(args.text, args.voice, args.save)
            if audio_path:
                print(f"Audio saved to: {audio_path}")
                sys.exit(0)
            sys.exit(1)
        else:
            success = say(args.text, args.voice)
            sys.exit(0 if success else 1)
    
    elif args.command == "play":
        success = play_audio(args.file)
        sys.exit(0 if success else 1)
    
    elif args.command == "list-voices":
        list_voices(args.lang if hasattr(args, 'lang') else None)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
