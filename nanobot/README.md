# Nanobot for Lucy

## Repository

Original nanobot repository: https://github.com/HKUDS/nanobot

## Prerequisites

### Install uv

Install uv with standalone installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart terminal after install.

### Python 3

```bash
which python
python --version
```

If other version than 3.12:

```bash
uv python install 3.12
uv python list
```

### Install Rust compiler

Rust is required to build the tiktoken depency when using uv.
Otherwise you will get error `Failed to build tiktoken`.


```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Select the default installation (option 1).

Restart terminal after install.

### Install libffi

```bash
sudo apt update
sudo apt install libffi-dev
```
### Autostart 

The pigpiod deamon must run for the servo arm to operate. Autostart it using: 

```bash
sudo systemctl enable pigpiod
```

## Installation

### Installation using uv

```bash
uv tool install --python 3.12 nanobot-ai
```

### Installation for Development Setup (Git + uv)

If you want to run nanobot directly from the Git repository while using uv's managed dependencies, you can configure the systemd service to use `PYTHONPATH`. This is useful for development: you can modify the code in the Git repo and the changes take effect immediately after a service restart — no reinstallation needed.

**1. Install nanobot with uv** (this sets up the virtual environment with all dependencies):

```bash
uv tool install nanobot-ai
```

**2. Clone the repository:**

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
```

**3. Update the systemd service** to use the Git repo as the Python source:

Edit `~/.config/systemd/user/nanobot-gateway.service`:

```ini
[Unit]
Description=Nanobot Gateway
After=network-online.target
Wants=network-online.target

[Service]
# Use Git repo as primary source, uv venv for dependencies
Environment="PYTHONPATH=/path/to/your/nanobot"
ExecStart=/home/YOUR_USER/.local/share/uv/tools/nanobot-ai/bin/python3 -m nanobot gateway
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

Replace `/path/to/your/nanobot` with the actual path to your cloned repository, and `YOUR_USER` with your username.

**4. Reload and restart:**

```bash
systemctl --user daemon-reload
systemctl --user restart nanobot-gateway
```

Now the gateway runs your local Git code with uv's dependencies. To update:

- **Your changes:** Edit files in the Git repo, then `systemctl --user restart nanobot-gateway`
- **Upstream changes:** `git pull` (or merge), then restart the service

> **Tip:** If you add custom channels or providers that require additional system packages (e.g. `pvporcupine` for wake-word detection), you may need to enable system site-packages in the uv venv. Edit `~/.local/share/uv/tools/nanobot-ai/pyvenv.cfg` and set `include-system-site-packages = true`.



## Onboarding

### Run onboard

```bash
nanobot onboard
```

This will create:
- config at /home/pi/.nanobot/config.json
- workspace at /home/pi/.nanobot/workspace
- ... at /home/pi/.nanobot/workspace/AGENTS.md
- ... at /home/pi/.nanobot/workspace/SOUL.md
- ... at /home/pi/.nanobot/workspace/USER.md
- ... at /home/pi/.nanobot/workspace/memory/MEMORY.md
- ... at /home/pi/.nanobot/workspace/memory/HISTORY.md

### Initial configuration

Add your API key to ~/.nanobot/config.json

Modify AGENTS.md and SOUL.md with the name, and add your initial user information to USER.md.

### Configure Channels

#### Telegram

**1. Create a bot**
- Open Telegram, search `@BotFather`
- Send `/newbot`, follow prompts
- Copy the token

**2. Configure**

In ~/.nanobot/config.json:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

> You can find your **User ID** in Telegram settings. It is shown as `@yourUserId`.
> Copy this value **without the `@` symbol** and paste it into the config file.

**3. Run**

```bash
nanobot gateway
```

**4. Groups**

To add the bot to a telegram group, make it group admin so it can see all messages. Or disable group pricacy mode for the bot in telegram BotFather configuration.

#### WhatsApp

Requires **Node.js 20**.

As baileys library is used, it would be best if using a dedicated phone number/whatsapp account just for the bot. 
Otherwise the bot is running as linked device on your whatsapp number.
This means that other people can send messages to you and thus your bot messages, but you can not send messages to yourself
as this would create an infinite loop.

**1. Link device**

```bash
nanobot channels login
# Scan QR with WhatsApp ? Settings ? Lnked Devices
```

**2. Configure**

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. Run** (two terminals)

```bash
# Terminal 1
nanobot channels login

# Terminal 2
nanobot gateway
```

### Autostart after reboot

Ask Lucy to setup autostart of the gateway herself using systemd and lingers so the service can start without user login.

Check status after reboot:

```bash
systemctl --user status nanobot-gateway
# Should show ... active (running) ...
```

Show live messages:

```bash
sudo journalctl -f | grep nanobot
```

As Lucy is now running as a user-service named nanobot-gateway.service you need to restart the service using this call after changing the configuration:

```bash
systemctl --user restart nanobot-gateway.service
```


## Implement your own skills

Bring up the interactive agent chat:

```bash
nanobot agent
```

Then describe the skill that you want, e.g.:

```
Hi Lucy, can you write yourself a skill for your aura. Using that skill you can e.g. 
express your emotions by shining the LED build in your hardware in different colors. 
Or you can even make disco and let the LED blink when you are super happy :-). 
Can you write such a skill? As a start you can look at the node js script that can be started using 
sudo env "PATH=$PATH" node /home/pi/Desktop/lucy/tests/test.led.js
```

```
Hi Lucy, can you write yourself a skill for your arm. Using that skill you can e.g. 
wave hello or goodbye to the user. 
Can you write such a skill? As a start you can look at the node js script that can be started using 
sudo env "PATH=$PATH" node /home/pi/Desktop/lucy/tests/test.servo.js
Please write the skill in python.
You can also have a look at the aura skill which should contain some additional info about the necessary python libraries.
```

## Voice Channel vs. Ear/Voice Skills                                              

Voice Channel (channels/voice.py):                                              

 • Autonomous interaction loop running in background                            
 • Flow: Wake-word detection → Record with silence detection → Transcribe via   
   Groq Whisper → Send to LLM → TTS response → Audio playback                   
 • Provides hands-free, always-listening voice interface                        
 • Users interact by saying "Hallo Lucy" and speaking naturally                 

Ear Skill (skills/ear/):                                                        

 • On-demand audio recording and transcription tool                             
 • Can be invoked by the agent from any channel (Telegram, CLI, etc.)           
 • Use case: "Lucy, listen to what I'm saying" via Telegram triggers recording  

Voice Skill (skills/voice/):                                                    

 • On-demand text-to-speech tool                                                
 • Can be invoked by the agent from any channel                                 
 • Use case: "Lucy, say hello" via CLI makes Lucy speak through the speaker     

Conclusion: All three components serve different purposes, so the skills still make sense. 

 • Voice Channel = passive, always-on voice interface                           
 • Ear/Voice Skills = active tools for cross-channel audio capabilities  

## Updates

When installed using uv udpate to the latest version using:

```bash
uv tool update --python 3.12 nanobot-ai
```
When running nanobot from the git-repo, the workflow for updates is:                                                           
                                                                                
```cd /home/pi/Desktop/nanobot                                                    
 git fetch upstream                                                             
 git merge upstream/main                                                        
 systemctl --user restart nanobot-gateway.service  
```

## Backup

### Backup of the nanobot workspace

Backup the nanobot workspace using:

```bash
cp -rf /home/pi/.nanobot/workspace/ /home/pi/Desktop/lucy/nanobot/
cp /home/pi/.nanobot/config.json  /home/pi/Desktop/lucy/nanobot/
cp -rf /home/pi/.nanobot/cron/ /home/pi/Desktop/lucy/nanobot/

cd /home/pi/Desktop/lucy

git add *
git commit -m "Commit message"
git push
```

The files `config.json` and all memory files in `workspace/memory` are not pushed to GIT as they can contain sensitive information.
You need to backup these files manually!







