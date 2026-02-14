#!/usr/bin/env python3
"""
Lucy's Aura - LED control script
Controls a Neopixel LED on GPIO 18 to express emotions and moods.

Usage:
  python3 aura.py <command> [options]

Commands:
  shine <color>              - Set LED to a solid color
  pulse <color> [duration]   - Pulse the LED (duration: 0.5-2.0 seconds)
  disco [duration]           - Party mode! Random colors blinking
  off                        - Turn off the LED
  emotion <name>             - Show a predefined emotion

Colors: red, green, blue, yellow, orange, purple, pink, cyan, white, or hex (#FF0000)
Emotions: happy, sad, excited, calm, thinking, love, angry, surprised
"""

import sys
import time
import random
import signal
from rpi_ws281x import PixelStrip, Color

# LED configuration
GPIO_PIN = 18
NUM_LEDS = 1
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# Named colors
COLORS = {
    'red': 0xFF0000,
    'green': 0x00FF00,
    'blue': 0x0000FF,
    'yellow': 0xFFFF00,
    'orange': 0xFFA500,
    'purple': 0x800080,
    'pink': 0xFFC0CB,
    'cyan': 0x00FFFF,
    'white': 0xFFFFFF,
    'gold': 0xFFD700,
    'royalblue': 0x4169E1,
    'palegreen': 0x98FB98,
    'mediumpurple': 0x9370DB,
    'deeppink': 0xFF1493,
    'off': 0x000000,
    'on': 0xFFFFFF,
}

# Emotion color mappings
EMOTIONS = {
    'happy': {'color': '#FFD700', 'mode': 'pulse'},      # Gold
    'sad': {'color': '#4169E1', 'mode': 'shine'},        # Royal Blue
    'excited': {'color': 'random', 'mode': 'disco'},     # Disco!
    'calm': {'color': '#98FB98', 'mode': 'pulse'},       # Pale Green
    'thinking': {'color': '#9370DB', 'mode': 'pulse'},   # Medium Purple
    'love': {'color': '#FF1493', 'mode': 'pulse'},       # Deep Pink
    'angry': {'color': '#FF0000', 'mode': 'shine'},      # Red
    'surprised': {'color': '#FFFF00', 'mode': 'pulse'},  # Yellow
    'neutral': {'color': '#FFFFFF', 'mode': 'shine'},    # White
}

# Initialize the LED strip
strip = PixelStrip(NUM_LEDS, GPIO_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()


def normalize_color(color):
    """Convert color name or hex to integer."""
    if not color:
        return 0x000000
    
    c = color.lower().strip()
    
    if c == 'random':
        return random.randint(0, 0xFFFFFF)
    
    # Check named colors
    if c in COLORS:
        return COLORS[c]
    
    # Handle hex colors
    if c.startswith('#'):
        c = c[1:]
    if c.startswith('0x'):
        c = c[2:]
    
    # Check if valid hex
    try:
        if len(c) == 6:
            return int(c, 16)
    except ValueError:
        pass
    
    print(f"Unknown color: {color}, using white")
    return 0xFFFFFF


def int_to_color(value):
    """Convert integer to Color object."""
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return Color(r, g, b)


def shine(color):
    """Set LED to a solid color."""
    c = normalize_color(color)
    strip.setPixelColor(0, int_to_color(c))
    strip.show()
    print(f"LED shining: {color} (0x{c:06x})")


def pulse(color, duration=1.0):
    """Pulse the LED with fade in/out effect."""
    steps = 20
    c = normalize_color(color)
    r = (c >> 16) & 0xFF
    g = (c >> 8) & 0xFF
    b = c & 0xFF
    
    step_delay = duration / steps
    
    # Fade in
    for i in range(steps // 2 + 1):
        brightness = i / (steps / 2)
        pr = int(r * brightness)
        pg = int(g * brightness)
        pb = int(b * brightness)
        strip.setPixelColor(0, Color(pr, pg, pb))
        strip.show()
        time.sleep(step_delay)
    
    # Fade out
    for i in range(steps // 2, -1, -1):
        brightness = i / (steps / 2)
        pr = int(r * brightness)
        pg = int(g * brightness)
        pb = int(b * brightness)
        strip.setPixelColor(0, Color(pr, pg, pb))
        strip.show()
        time.sleep(step_delay)
    
    print(f"LED pulsed: {color}")


def disco(duration=5):
    """Party mode with random colors."""
    print(f"Disco mode for {duration} seconds!")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        c = random.randint(0, 0xFFFFFF)
        strip.setPixelColor(0, int_to_color(c))
        strip.show()
        time.sleep(0.1)
    
    # Turn off after disco
    strip.setPixelColor(0, Color(0, 0, 0))
    strip.show()
    print("Disco finished!")


def show_emotion(emotion_name):
    """Show a predefined emotion."""
    emotion = EMOTIONS.get(emotion_name.lower())
    if not emotion:
        print(f"Unknown emotion: {emotion_name}")
        print(f"Available emotions: {', '.join(EMOTIONS.keys())}")
        sys.exit(1)
    
    print(f"Showing emotion: {emotion_name}")
    
    mode = emotion['mode']
    color = emotion['color']
    
    if mode == 'shine':
        shine(color)
    elif mode == 'pulse':
        pulse(color, 1.5)
        pulse(color, 1.5)
    elif mode == 'disco':
        disco(3)


def off():
    """Turn off the LED."""
    strip.setPixelColor(0, Color(0, 0, 0))
    strip.show()
    print("LED off")


def cleanup(signum=None, frame=None):
    """Clean up on exit."""
    strip.setPixelColor(0, Color(0, 0, 0))
    strip.show()
    sys.exit(0)


# Handle cleanup on exit
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def main():
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python3 aura.py <command> [options]")
        print("Commands: shine, pulse, disco, off, emotion")
        print("Example: python3 aura.py shine red")
        print("Example: python3 aura.py emotion happy")
        print("Example: python3 aura.py disco 5")
        sys.exit(1)
    
    command = args[0].lower()
    
    try:
        if command == 'shine':
            shine(args[1] if len(args) > 1 else 'white')
        elif command == 'pulse':
            color = args[1] if len(args) > 1 else 'white'
            duration = float(args[2]) if len(args) > 2 else 1.0
            pulse(color, duration)
        elif command == 'disco':
            duration = float(args[1]) if len(args) > 1 else 5
            disco(duration)
        elif command == 'off':
            off()
        elif command == 'emotion':
            show_emotion(args[1] if len(args) > 1 else 'neutral')
        else:
            # Maybe it's a color directly
            shine(command)
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)


if __name__ == '__main__':
    main()
