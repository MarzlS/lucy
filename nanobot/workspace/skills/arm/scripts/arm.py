#!/usr/bin/env python3
"""
Lucy's Arm - Servo control script
Controls a servo motor on GPIO 7 to wave and gesture.

Usage:
  python3 arm.py <command> [options]

Commands:
  wave [count]     - Wave hello/goodbye (default: 2 times)
  raise            - Raise the arm up
  lower            - Lower the arm down
  back             - Move arm to back position
  position <value> - Set servo to specific position (500-2300)
  gesture <name>   - Perform a predefined gesture

Gestures: hello, goodbye, celebrate, thinking, shrug, excited
"""

import sys
import time
import pigpio

# Servo configuration
GPIO_PIN = 7  # GPIO 7 (physical pin 26)

# Servo positions (pulse width in microseconds)
# Valid range is typically 500-2500
SERVO_BACK = 500
SERVO_UP = 1400
SERVO_DOWN = 2300

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Error: Could not connect to pigpiod. Is it running?")
    print("Start it with: sudo systemctl start pigpiod")
    sys.exit(1)


def set_position(pulse_width):
    """Set servo to specific position (pulse width in microseconds)."""
    # Clamp to valid range
    pulse_width = max(500, min(2500, pulse_width))
    pi.set_servo_pulsewidth(GPIO_PIN, pulse_width)


def arm_back():
    """Move arm to back position."""
    print("Moving arm back")
    set_position(SERVO_BACK)


def raise_arm():
    """Raise the arm up."""
    print("Raising arm")
    set_position(SERVO_UP)


def lower_arm():
    """Lower the arm down."""
    print("Lowering arm")
    set_position(SERVO_DOWN)


def wave(count=2):
    """Wave the arm."""
    print(f"Waving {count} time(s)")
    delay = 0.2
    
    for i in range(count):
        set_position(SERVO_UP)
        time.sleep(delay)
        set_position(SERVO_DOWN)
        time.sleep(delay)
    
    # End with arm up
    set_position(SERVO_UP)
    time.sleep(delay)
    print("Wave complete")


def gesture_hello():
    """Friendly hello wave."""
    print("Gesture: Hello!")
    # Raise arm first
    set_position(SERVO_UP)
    time.sleep(0.3)
    
    # Quick waves
    for _ in range(3):
        set_position(SERVO_DOWN)
        time.sleep(0.15)
        set_position(SERVO_UP)
        time.sleep(0.15)
    
    time.sleep(0.3)
    # End with arm up


def gesture_goodbye():
    """Goodbye wave - slower, more deliberate."""
    print("Gesture: Goodbye!")
    set_position(SERVO_UP)
    time.sleep(0.4)
    
    # Slow waves
    for _ in range(4):
        set_position(SERVO_DOWN)
        time.sleep(0.3)
        set_position(SERVO_UP)
        time.sleep(0.3)
    
    time.sleep(0.3)
    # End with arm up


def gesture_celebrate():
    """Excited celebration - rapid waving."""
    print("Gesture: Celebrate!")
    
    # Rapid waves
    for _ in range(6):
        set_position(SERVO_UP)
        time.sleep(0.1)
        set_position(SERVO_DOWN)
        time.sleep(0.1)
    
    # End with arm up
    set_position(SERVO_UP)
    time.sleep(0.3)


def gesture_thinking():
    """Thinking pose - arm moves slowly up and holds."""
    print("Gesture: Thinking...")
    
    # Slowly raise
    current = SERVO_BACK
    target = SERVO_UP
    steps = 20
    step_size = (target - current) / steps
    
    for i in range(steps):
        current += step_size
        set_position(int(current))
        time.sleep(0.05)
    
    # Hold position, end with arm up
    time.sleep(1.0)


def gesture_shrug():
    """Shrug - quick up and down."""
    print("Gesture: Shrug")
    
    # Quick raise
    set_position(SERVO_UP)
    time.sleep(0.2)
    
    # Brief dip down and back up
    set_position(SERVO_DOWN)
    time.sleep(0.15)
    set_position(SERVO_UP)
    time.sleep(0.3)
    # End with arm up


def gesture_excited():
    """Very excited - super fast waving."""
    print("Gesture: Excited!")
    
    # Super fast waves
    for _ in range(10):
        set_position(SERVO_UP)
        time.sleep(0.05)
        set_position(SERVO_DOWN)
        time.sleep(0.05)
    
    # End with arm up
    set_position(SERVO_UP)
    time.sleep(0.3)


def gesture_nod():
    """Nodding motion - small up/down movements."""
    print("Gesture: Nod")
    
    mid = (SERVO_UP + SERVO_DOWN) // 2
    small_up = mid - 200
    small_down = mid + 200
    
    set_position(mid)
    time.sleep(0.2)
    
    for _ in range(3):
        set_position(small_up)
        time.sleep(0.15)
        set_position(small_down)
        time.sleep(0.15)
    
    # End with arm up
    set_position(SERVO_UP)
    time.sleep(0.2)


# Gesture mapping
GESTURES = {
    'hello': gesture_hello,
    'goodbye': gesture_goodbye,
    'celebrate': gesture_celebrate,
    'thinking': gesture_thinking,
    'shrug': gesture_shrug,
    'excited': gesture_excited,
    'nod': gesture_nod,
}


def show_gesture(name):
    """Perform a named gesture."""
    gesture_func = GESTURES.get(name.lower())
    if not gesture_func:
        print(f"Unknown gesture: {name}")
        print(f"Available gestures: {', '.join(GESTURES.keys())}")
        sys.exit(1)
    
    gesture_func()


def stop():
    """Stop servo signal (allows servo to rest)."""
    print("Stopping servo")
    pi.set_servo_pulsewidth(GPIO_PIN, 0)


def cleanup():
    """Clean up GPIO."""
    pi.set_servo_pulsewidth(GPIO_PIN, 0)
    pi.stop()


def main():
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python3 arm.py <command> [options]")
        print("Commands: wave, raise, lower, back, position, gesture, stop")
        print("Example: python3 arm.py wave 3")
        print("Example: python3 arm.py gesture hello")
        print(f"Available gestures: {', '.join(GESTURES.keys())}")
        sys.exit(1)
    
    command = args[0].lower()
    
    try:
        if command == 'wave':
            count = int(args[1]) if len(args) > 1 else 2
            wave(count)
        elif command == 'raise':
            raise_arm()
        elif command == 'lower':
            lower_arm()
        elif command == 'back':
            arm_back()
        elif command == 'position':
            if len(args) < 2:
                print("Error: position requires a value (500-2300)")
                sys.exit(1)
            pos = int(args[1])
            print(f"Setting position to {pos}")
            set_position(pos)
        elif command == 'gesture':
            if len(args) < 2:
                print(f"Available gestures: {', '.join(GESTURES.keys())}")
                sys.exit(1)
            show_gesture(args[1])
        elif command == 'stop':
            stop()
        else:
            # Maybe it's a gesture name directly
            if command in GESTURES:
                show_gesture(command)
            else:
                print(f"Unknown command: {command}")
                sys.exit(1)
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)
    finally:
        # Don't cleanup immediately - let servo hold position briefly
        time.sleep(0.5)
        cleanup()


if __name__ == '__main__':
    main()
