---
name: arm
description: Control Lucy's servo arm to wave, gesture, and express physical movements. Use this skill to greet users, wave hello or goodbye, celebrate, or show physical reactions.
---

# Arm - Lucy's Servo Control

This skill controls the servo motor attached to GPIO 7 on the Raspberry Pi to move Lucy's arm for waving and gestures.

## Prerequisites

The pigpiod daemon must be running:

```bash
sudo systemctl start pigpiod
sudo systemctl enable pigpiod  # to start on boot
```

## Quick Reference

Run commands from the skill directory:

```bash
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py <command> [args]
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `wave [count]` | Wave the arm (default: 2 times) | `wave 3` |
| `raise` | Raise arm up | `raise` |
| `lower` | Lower arm down | `lower` |
| `back` | Move arm to back/rest position | `back` |
| `position <value>` | Set specific position (500-2300) | `position 1400` |
| `gesture <name>` | Perform a predefined gesture | `gesture hello` |
| `stop` | Stop servo signal | `stop` |

## Gestures

| Gesture | Description |
|---------|-------------|
| `hello` | Friendly hello wave (3 quick waves) |
| `goodbye` | Slower farewell wave (4 waves) |
| `celebrate` | Excited rapid waving |
| `thinking` | Slow raise and hold |
| `shrug` | Quick up and down |
| `excited` | Super fast waving |
| `nod` | Small nodding motion |

## Servo Positions

- **BACK (500)**: Arm resting behind
- **UP (1400)**: Arm raised up
- **DOWN (2300)**: Arm lowered down

Valid range: 500-2500 microseconds pulse width

## Examples

```bash
# Wave hello
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py wave

# Wave 5 times
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py wave 5

# Greet with hello gesture
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py gesture hello

# Say goodbye
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py gesture goodbye

# Celebrate!
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py gesture celebrate

# Raise arm and hold
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py raise

# Return to rest
python3 /home/pi/.nanobot/workspace/skills/arm/scripts/arm.py back
```

## Notes

- Uses Python 3 with the `pigpio` library
- Requires `pigpiod` daemon to be running
- No sudo required (pigpiod handles GPIO access)
- Servo returns to back position after gestures
- GPIO Pin: 7 (physical pin 26)
