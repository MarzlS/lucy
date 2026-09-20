# Long-term Memory

This file stores important information that should persist across sessions.

## User Information

- **Nora**: Telegram Chat-ID 8570293805 (Username: nori45)
- **Marcell**: Telegram Chat-ID 8334195719

## Preferences

- **Voice Channel**: Der Voice-Channel hat eingebaute TTS. **NICHT zusätzlich den Voice-Skill aufrufen, sonst kommt alles doppelt!** Der Voice-Skill prüft nun die Umgebungsvariable `NANOBOT_VOICE_CHANNEL` und unterdrückt TTS, wenn diese gesetzt ist.
- **Git Operations**: **NIE automatisch merges oder andere Git-Operationen durchführen!** Immer mit dem User absprechen.

## Important Notes

- **Gateway service restart**: `systemctl --user restart nanobot-gateway.service` (kein sudo nötig, es ist ein Benutzer-Service)
- **Code Sync**: Immer das Git-Repository (`/home/pi/Desktop/nanobot`) als Quelle der Wahrheit betrachten. Änderungen in die uv-Installation nur bei Bedarf kopieren.

## Development Setup (Git + uv)

Um Nanobot direkt aus dem Git-Repository zu betreiben und die uv-Installation zu nutzen:

1. **uv installieren**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Git-Repository klonen**:
   ```bash
   git clone https://github.com/PatrickLib/nanobot.git /home/pi/Desktop/nanobot
   ```

3. **uv-Tool installieren**:
   ```bash
   uv tool install nanobot-ai
   ```

4. **systemd-Service anpassen**:
   - `PYTHONPATH` auf das Git-Repository setzen:
     ```ini
     [Service]
     Environment="PYTHONPATH=/home/pi/Desktop/nanobot"
     ExecStart=/home/pi/.local/share/uv/tools/nanobot-ai/bin/python3 -m nanobot gateway
     ```

5. **System site-packages aktivieren (falls nötig)**:
   - Bearbeite `/home/pi/.local/share/uv/tools/nanobot-ai/pyvenv.cfg` und setze:
     ```ini
     include-system-site-packages = true
     ```

**Vorteile**: Änderungen im Git-Repository sind sofort aktiv nach einem Service-Neustart. Updates können einfach mit `git pull` und einem Merge mit dem Upstream durchgeführt werden.

## Lucy's Hardware & Skills

### Aura Skill (LED Control)
- **Location**: `/home/pi/.nanobot/workspace/skills/aura/scripts/aura.py`
- **Controls**: Neopixel LED on GPIO 18
- **Commands**: `shine`, `pulse`, `disco`, `off`, `emotion`
- **Emotions**: `happy` (gold pulse), `sad` (blue), `excited` (disco), `calm` (green pulse), `thinking` (purple pulse), `love` (pink pulse), `angry` (red), `surprised` (yellow pulse)
- **Run**: `sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py <command>`
- **Voice Channel Integration**: LED glows blue during listening phase after wake word detection.

### Arm Skill (Servo Control) - Completed
- **Location**: `/home/pi/.nanobot/workspace/skills/arm/scripts/arm.py`
- **Controls**: Servo motor on GPIO 7
- **Commands**: `wave [count]`, `raise`, `lower`, `back`, `position <value>`, `gesture <name>`
- **Gestures**: `hello`, `goodbye`, `celebrate`, `thinking`, `shrug`, `excited`, `nod`
- **Run**: `sudo python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py <command>`

### Voice Skill (TTS/Speaking) - Completed
- **Location**: `/home/pi/.nanobot/workspace/skills/voice/scripts/voice.py`
- **Purpose**: Text-to-Speech + playback via speaker
- **TTS Voice**: `de-DE-SeraphinaMultilingualNeural` (German female, multilingual)
- **Commands**: `say`, `play`, `list-voices`
- **Run**: `python3 /home/pi/.nanobot/workspace/skills/voice/scripts/voice.py <command>`
- **WICHTIG**: **NICHT im Voice-Channel verwenden!** Nur für Telegram/Discord/CLI (Voice-Channel hat eigene TTS).
  **Technische Lösung**: Der Voice-Skill prüft die Umgebungsvariable `NANOBOT_VOICE_CHANNEL` und unterdrückt TTS, wenn diese gesetzt ist.

### Ear Skill (Microphone/Listening) - Completed
- **Location**: `/home/pi/.nanobot/workspace/skills/ear/scripts/ear.py`
- **Purpose**: Record from microphone + transcribe via Groq Whisper API
- **Commands**: `record`, `transcribe`, `listen` (record + transcribe in one step)
- **Run**: `python3 /home/pi/.nanobot/workspace/skills/ear/scripts/ear.py <command>`

### Skill Description Format
- Skills use YAML frontmatter in `SKILL.md` for name and description.

## Audio Hardware
- **USB Audio Device**: Card 1 (both playback and capture)
- **HDMI Audio**: Available on card 0
- **PvRecorder Devices**: 0 = Monitor (output), 1 = Audio Adapter Mono (Unitek Y-247A) - input

## Wake Word Detection - Porcupine

- **Engine**: Porcupine by Picovoice (pvporcupine 4.0.2)
- **Recorder**: pvrecorder 1.2.7
- **API Key**: `eX0qc+y+Rq/2LlDD+T4K0nn+q7tY1349RuHkkutVawS+ZP8Zq5CkIw==`
- **Custom Wake Word**: `Hallo Lucy` (German)
- **Sensitivity**: 1.0 (maximum)
- **Status**: **Working**

## Voice Channel - Working (Angepasst)

### Implementation
- **Location**: `/home/pi/Desktop/nanobot/nanobot/channels/voice.py`
- **Purpose**: Local microphone/speaker interaction with wake word detection.
- **Flow (geplant)**:
  1. Wake-word → LED blue (listening)
  2. Record audio until silence detected
  3. **Audio als `OutboundMessage` an den Message-Bus senden** (statt selbst zu transkribieren)
  4. LED off
  5. **Agent oder Skill übernimmt die Weiterverarbeitung** (Transkription, Antwort, TTS).

### Nachrichtstruktur für Audio-Nachrichten (geplant)
```json
{
  "type": "voice_audio",
  "content": {
    "audio_base64": "UklGR...",  // Base64-codierte WAV-Datei
    "duration": 5,
    "mime_type": "audio/wav"
  },
  "metadata": {
    "source": "voice_channel",
    "timestamp": 1709956800
  }
}
```

### Bug Fixes
- **allowFrom Wildcard**: Fixed `is_allowed()` in `base.py` to handle `*` wildcard in `allowFrom` list.
- **UV Venv Fix**: Edited `pyvenv.cfg` to include system site-packages for access to system-installed packages.
- **Doppel-TTS-Vermeidung**: Voice-Skill prüft `NANOBOT_VOICE_CHANNEL` und unterdrückt TTS im Voice-Channel.

### Git Sync Status
- **voice.py**: Committed with message 'Update voice channel' (2026-03-05).
- **manager.py**: Modified (needs commit).
- **base.py**: Git version copied to uv installation.

## Technical Info

- **TJBot Libraries**: `/home/pi/Desktop/lucy/tests/node_modules/tjbot/`
- **TJBot Source**: `/home/pi/Desktop/lucy/tests/node_modules/tjbot/src/tjbot.js`
- **Lucy Main Code**: `/home/pi/Desktop/lucy/tjbot/lucy.js`
- **Nanobot Codebase**: `/home/pi/Desktop/nanobot/`
- **Config Location**: `/home/pi/.nanobot/config.json`
- **Channels**: `/home/pi/Desktop/nanobot/nanobot/channels/`
- **Providers**: `/home/pi/Desktop/nanobot/nanobot/providers/`
- **Base Channel Class**: `/home/pi/Desktop/nanobot/nanobot/channels/base.py`
- **Channel Manager**: `/home/pi/Desktop/nanobot/nanobot/channels/manager.py`

## API Keys

- **GROQ_API_KEY**: Available in `/home/pi/.nanobot/config.json` (used for Whisper transcription)
- **PICOVOICE_API_KEY**: `eX0qc+y+Rq/2LlDD+T4K0nn+q7tY1349RuHkkutVawS+ZP8Zq5CkIw==` (for Porcupine wake word)

## Python Package Installation

- **Raspberry Pi OS**: Uses externally-managed-environment
- **Installation**: `pip3 install <package> --break-system-packages`
- **Alternative**: Use virtual environments with `python3 -m venv`
- **Note**: `onnxruntime` NOT available for ARM (affects `openWakeWord`).

## Conversation Logs

### 2026-03-05
- **Voice Channel Test**: LED glows blue during listening phase after wake word detection. User confirmed functionality.
- **Git Commit**: User requested and approved a Git commit for changes in `voice.py` with the message 'Update voice channel'.
- **LED Feedback**: User noted improved functionality with extended LED response time.
- **Voice Channel LED Integration**: LED leuchtet blau während des Zuhörens nach Wake-Word-Erkennung.
- **Git-Operationen**: Bestätigt, dass keine automatischen Merges oder Pushes durchgeführt werden. Immer mit dem User absprechen.
- **Dokumentation**: Abschnitt 'Development Setup (Git + uv)' hinzugefügt.
- **Technische Lösung für Doppel-TTS**: Voice-Skill prüft `NANOBOT_VOICE_CHANNEL` und unterdrückt TTS im Voice-Channel.

### 2026-03-11
- **Latenzzeit-Benchmarking**: Benutzer fragte nach der Antwortzeit des Remote-Modells (z. B. Anthropic Claude Opus 4.5). Vorschläge für CLI-Tests und Log-Analyse gemacht.
- **Voice-Channel-Anpassung**: Benutzer wünscht, dass der Voice-Channel Audio-Nachrichten wie der Telegram-Channel an den Message-Bus weiterleitet, ohne selbst zu transkribieren oder zu antworten. Diskussion über die Umsetzung erfolgte.
- **Geplante Nachrichtstruktur**: Audio-Nachrichten sollen als Base64-codierte WAV-Dateien mit Metadata an den Bus gesendet werden.
- **Nächste Schritte**: Voice-Channel soll angepasst werden, um Audio-Nachrichten analog zum Telegram-Channel zu behandeln.