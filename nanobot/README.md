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


## Installation

### Installation using uv

```bash
uv tool install --python 3.12 nanobot-ai
```

### Installation for Development

```bash
git clone https://github.com/HKUDS/nanobot.git
cd nanobot
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```


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

## Backup of nanobot workspace

Backup the nanobot workspace using:

```bash
cp -rf /home/pi/.nanobot/workspace/ /home/pi/Desktop/lucy/nanobot/ 
cd /home/pi/Desktop/lucy
git add *
git commit -m "Commit message"
git push
```






