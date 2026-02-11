
# Troubleshooting

## Installation

### Install pigpiod

pigpio is a C library for the Raspberry which allows control of the General Purpose Input Outputs.

Check version:

    $ pigpiod -v

Installation:

    $ sudo apt-get update
    $ sudo apt-get install pigpio

### Run bootstrap

sudo sh bootstrap.sh

Select Options:

```
> Would you like to use this Raspberry Pi for Lucy? [Y/n] Y
> ...
> TJBot name (current: raspberrypi): lucy
> Setting DNS hostname to lucy
> ...
> Disable ipv6? [y/N] y
> ...
> Enable Quad9 DNS? [y/N]: y
> ...
> Force locale to US English (en-US)? [y/N] y
> ...
> Proceed with apt-get dist-upgrade? [Y/n] n
> ...
> Would you like to install Node.js v18.x? [Y/n] Y
> ...
> ... To be continued
> ...
> ...
```

## Prerequisites

### Audio

Headjack may not be  blacklisted otherwise the USB Soundcard does not work.

You may want to delete the blacklist:

    $ rm /etc/modprobe.d/*-blacklist-snd.conf

Reboot after making any changes to `modprobe.d`.

Speaker Config for Lucy using a USB soundcard:

```
var tj = new TJBot(['speaker'], {log: {level: 'debug'}, speak: {speakerDeviceId: "plughw:1,0"}}, {});
```

### LED

To use the LED, audio should be blacklisted, but not all modules!

Copy to modprobe.d:

    $ cp ./bootstrap/lucybot-blacklist-snd.conf /etc/modprobe.d/

Make sure this line is NOT in this file:
```
blacklist snd
```

Reboot after making any changes to `modprobe.d`.

### Camera

The TJBot library is trying to use the Legacy Camera command (raspistill), but this tool is missing on newer Raspberry Pi OS versions.  
The legacy camera stack has been replaced by libcamera. 
To fix this we create a this script to simulate raspistill (old version of rpicam-still) for TJBot and Lucy:

Check your configuration file:

    $ sudo nano /boot/firmware/config.txt

- Set `camera_auto_detect` to `0`.
- Remove `start_x=1` and `gpu_mem=128` if present.
- Add `dtoverlay=ov5647,rotation=180` to the `[all]` section to always do `--vflip` for the ov5647 camera.

```
[all]
# Always do --vflip for the ov5647 camera
dtoverlay=ov5647,rotation=180
```

Reboot after making any changes to the `config.txt`.

To test the camera use stand alone:

    $ rpicam-hello

Or to capture a image:

    $ rpicam-still -o ~/Desktop/test_image.jpg

Or quick capture (no preview):

    $ rpicam-still -n -o ~/Desktop/test_image2.jpg

We use this script to simulate raspistill (old version of rpicam-still) for TJBot and Lucybot:

    $ sudo nano /usr/bin/raspistill

```
#!/bin/bash
# Mapping raspistill flags to rpicam-still
# TJBot uses: -n (nopreview), -e (encoding), -w (width), -h (height), -t (timeo>

args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n) args+=("--nopreview"); shift ;;
    -e) args+=("--encoding" "$2"); shift 2 ;;
    -w) args+=("--width" "$2"); shift 2 ;;
    -h) args+=("--height" "$2"); shift 2 ;;
    -t) args+=("--timeout" "$2"); shift 2 ;;
    -o) args+=("--output" "$2"); shift 2 ;;
    *) args+=("$1"); shift ;;
  esac
done

exec rpicam-still "${args[@]}"

```

Make script executable:

    $ sudo chmod +x /usr/bin/raspistill
    
# Tests

Run all tests with Node 18 (maximum supported version)!

    $ cd tests
    $ npm install

## Test the LED

    $ sudo node test.led.js

**Success:** LED changes color.

If using nvm to select node version you must use:

    $ sudo env "PATH=$PATH" node test.led.js 

## Test the servo arm

    $ sudo node test.servo.js

**Success:** Arm should move.

If using nvm to select node version you must use:

    $ sudo env "PATH=$PATH" node test.servo.js 

Issues when running with Node 22:

The NodeJS wrapper for the pigpio C library (used for the servo arm) requires Node 18.
Reason: pigpio uses NAN (Native Abstractions for Node) and native C++ bindings. 
Node 22 uses a newer V8 API that removed/changed NAN interfaces, so older native modules like pigpio simply do not compile on Node 20+ (especially 22).
This is very common with Raspberry Pi + pigpio.
Fix (recommended): downgrade Node, use Node 18 LTS (most stable for pigpio) or Node 16.


## Test the camera

Test using libcamera:

    $ rpicam-hello

Test using Lucy:

    $ sudo node test.camera.js

**Success:**: Image is captured and stored as picture.jpg

If using nvm to select node version you must use:

    $ sudo env "PATH=$PATH" node test.camera.js 


## Test the microphone

Test using pulseaudio utils:

    $ parecord recording.wav

then

    $ paplay recording.wav

Test using Lucy (needs SpeechToText service):

    $ sudo node test.mic.js 

If using nvm to select node version you must use:

    $ sudo env "PATH=$PATH" node test.mic.js 


## Test the speaker

    $ sudo node test.speaker.js 

**Success:**: Should play an audio file.

If using nvm to select node version you must use:

    $ sudo env "PATH=$PATH" node test.speaker.js 




