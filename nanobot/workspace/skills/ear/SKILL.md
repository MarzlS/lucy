# Ear Skill

Control Lucy's ear to listen and transcribe speech from the microphone.

## Usage

```bash
# Record audio for 5 seconds
python3 /home/pi/.nanobot/workspace/skills/ear/scripts/ear.py record output.wav --duration 5

# Transcribe an existing audio file
python3 /home/pi/.nanobot/workspace/skills/ear/scripts/ear.py transcribe audio.wav

# Listen and transcribe in one step
python3 /home/pi/.nanobot/workspace/skills/ear/scripts/ear.py listen --duration 5

# Listen with different language
python3 /home/pi/.nanobot/workspace/skills/ear/scripts/ear.py listen --language en
```

## Commands

### record
Record audio from the microphone to a file.

```bash
python3 ear.py record output.wav --duration 10
```

### transcribe
Transcribe an existing audio file using Groq Whisper.

```bash
python3 ear.py transcribe recording.wav --language de
```

### listen
Record and transcribe in one step - the most common use case.

```bash
python3 ear.py listen --duration 5
```

## Requirements

- `GROQ_API_KEY` environment variable (for Whisper transcription - free tier available!)
- `arecord` for audio recording (part of alsa-utils)

## Environment Variables

- `GROQ_API_KEY` - API key for Groq Whisper transcription
- `WHISPER_MODEL` - Whisper model to use (default: whisper-large-v3-turbo)
- `WHISPER_LANGUAGE` - Default language for transcription (default: de)
- `MIC_DEVICE` - ALSA device for recording (default: plughw:1,0)

## Supported Languages

Common language codes:
- `de` - German (default)
- `en` - English
- `fr` - French
- `es` - Spanish
- `it` - Italian
- `nl` - Dutch
- `pl` - Polish
- `pt` - Portuguese
- `ru` - Russian
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean

## Examples

```bash
# Quick voice input in German
python3 ear.py listen -d 5

# Longer recording in English
python3 ear.py listen --duration 15 --language en

# Just record without transcribing
python3 ear.py record /tmp/memo.wav -d 30
```
