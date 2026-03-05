# Voice Skill

Control Lucy's voice to speak text aloud using edge-tts (Microsoft Edge Text-to-Speech).

## Usage

```bash
# Speak text (uses default German voice)
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py say "Hallo, ich bin Lucy!"

# Speak with a specific voice
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py say "Hello, I am Lucy!" --voice en-US-JennyNeural

# Save audio to file
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py say "Test" --save /tmp/output.mp3

# Play an existing audio file
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py play /path/to/audio.mp3

# List available voices
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py list-voices

# List only German voices
python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py list-voices --lang de
```

## Favorite Voices

### German
- `de-DE-SeraphinaMultilingualNeural` - Female, multilingual (default)
- `de-DE-AmalaNeural` - Female, friendly
- `de-DE-KatjaNeural` - Female
- `de-DE-ConradNeural` - Male

### English
- `en-US-JennyNeural` - Female, US
- `en-US-AriaNeural` - Female, US
- `en-GB-SoniaNeural` - Female, British

## Requirements

- edge-tts: `pip install --break-system-packages edge-tts`
- Audio playback: paplay (PulseAudio) or aplay (ALSA)

## Notes

- No API key required - uses Microsoft's free Edge TTS service
- Fast and lightweight, perfect for Raspberry Pi
- Supports many languages and voices
