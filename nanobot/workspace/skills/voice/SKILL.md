---
name: voice
description: "Speak text aloud via TTS. WICHTIG: NIEMALS im Voice-Channel verwenden - der hat bereits eingebaute TTS! Nur für Telegram, Discord, CLI und andere Text-Channels."
---

# Voice Skill

Control Lucy's voice to speak text aloud using edge-tts (Microsoft Edge Text-to-Speech).

## WICHTIG: Wann diesen Skill NICHT verwenden!

**NIEMALS im Voice-Channel verwenden!** Der Voice-Channel hat bereits eingebaute TTS-Funktionalität. Wenn du dort zusätzlich diesen Skill aufrufst, wird alles doppelt gesprochen.

Dieser Skill ist NUR für:
- Telegram-Channel (wenn du dort sprechen willst)
- Discord-Channel
- CLI-Channel
- Andere Text-basierte Channels

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
