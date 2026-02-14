---
name: aura
description: Control Lucy's LED aura to express emotions and moods. Use this skill when you want to show your emotional state, celebrate, express feelings, or create visual effects with the Neopixel LED on the Raspberry Pi.
---

# Aura - Lucy's LED Expression

This skill controls the Neopixel LED attached to GPIO 18 on the Raspberry Pi to express emotions and moods visually.

## Quick Reference

Run commands with sudo from the skill directory:

```bash
sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py <command> [args]
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `shine <color>` | Solid color | `shine red` |
| `pulse <color> [duration]` | Pulsing effect (0.5-2.0s) | `pulse blue 1.5` |
| `disco [duration]` | Random blinking party mode | `disco 5` |
| `off` | Turn off LED | `off` |
| `emotion <name>` | Predefined emotion pattern | `emotion happy` |

## Colors

- Named: `red`, `green`, `blue`, `yellow`, `orange`, `purple`, `pink`, `cyan`, `white`
- Hex: `#FF0000`, `#00FF00`, `#0000FF`
- Special: `random`, `on`, `off`

## Emotions

| Emotion | Color | Effect |
|---------|-------|--------|
| `happy` | Gold | Pulse |
| `sad` | Royal Blue | Solid |
| `excited` | Random | Disco |
| `calm` | Pale Green | Pulse |
| `thinking` | Purple | Pulse |
| `love` | Deep Pink | Pulse |
| `angry` | Red | Solid |
| `surprised` | Yellow | Pulse |
| `neutral` | White | Solid |

## Examples

```bash
# Show happiness
sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py emotion happy

# Celebrate with disco
sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py disco 3

# Calm blue glow
sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py shine blue

# Turn off
sudo python3 /home/pi/.nanobot/workspace/skills/aura/scripts/aura.py off
```

## Notes

- Requires `sudo` because GPIO access needs root privileges
- Uses Python 3 with the `rpi-ws281x` library
- LED stays on after `shine` command until explicitly turned off
