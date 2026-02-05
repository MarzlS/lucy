#!/bin/sh

#----make sure this is run as root
user=`id -u`
if [ $user -ne 0 ]; then
    echo "This script requires root permissions. Please run this script with sudo."
    exit
fi

#----ascii art!
echo " _                      _                 _       _                   "
echo "| |                    | |               | |     | |                  "
echo "| |  _   _ ___  _   _  | |__   ___   ___ | |_ ___| |_ _ __ __ _ _ __  "
echo "| | | | | | __\| | | | | '_ \ / _ \ / _ \| __/ __| __| '__/ _\`| '_ \ "
echo "| |_| |_| | |_ | |_| | | |_) | (_) | (_) | |_\__ \ |_| | | (_| | |_) |"
echo " \__|_____|___/ \__  | |_.__/ \___/ \___/ \__|___/\__|_|  \__,_| .__/ "
echo "                  _/ |                                         | |    "
echo "                 |__/                                          |_|    "

#----intro message
echo ""
echo "-----------------------------------------------------------------------"
echo "Welcome! Let's set up your Raspberry Pi with the Lucy software."
echo ""
echo "Important: This script was designed for setting up a Raspberry Pi after"
echo "a clean install of Raspbian. If you are running this script on a"
echo "Raspberry Pi that you've used for other projects, please take a look at"
echo "what this script does BEFORE running it to ensure you are comfortable"
echo "with its actions (e.g. performing an OS update, installing software"
echo "packages, removing old packages, etc.)"
echo "-----------------------------------------------------------------------"
echo "Based on TJBot bootstrap: http://ibm.biz/tjbot-bootstrap"
echo "-----------------------------------------------------------------------"

#----confirm bootstrap
read -p "Would you like to use this Raspberry Pi for Lucy? [Y/n] " choice </dev/tty
case "$choice" in
    "n" | "N")
        echo "OK, Lucy software will not be installed at this time."
        exit
        ;;
    *) ;;
esac

#----setting bot name
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
echo ""
echo "Please enter a name for your bot. This will be used for the hostname of"
echo "your Raspberry Pi."
read -p "Bot name (current: $CURRENT_HOSTNAME): " name </dev/tty
name=$(echo "$name" | tr -d ' ')
if [ -z $name ]; then
    name=$CURRENT_HOSTNAME
fi
echo "Setting DNS hostname to $name"
echo "$name" | tee /etc/hostname >/dev/null 2>&1
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$name/g" /etc/hosts

#----disabling ipv6
echo ""
echo "In some networking environments, disabling ipv6 may help your Pi get on"
echo "the network."
read -p "Disable ipv6? [y/N] " choice </dev/tty
case "$choice" in
    "y" | "Y")
        echo "Disabling ipv6"
        echo " ipv6.disable=1" | tee -a /boot/cmdline.txt
        echo "ipv6 has been disabled. It will take effect after rebooting."
        ;;
    *) ;;
esac

#----setting DNS to Quad9
echo ""
echo "In some networking environments, using Quad9's nameservers may speed up"
echo "DNS queries and provide extra security and privacy."
read -p "Enable Quad9 DNS? [y/N]: " choice </dev/tty
case "$choice" in
    "y" | "Y")
        echo "Adding Quad9 DNS servers to /etc/resolv.conf"
        if ! grep -q "nameserver 9.9.9.9" /etc/resolv.conf; then
            echo "nameserver 9.9.9.9" | tee -a /etc/resolv.conf
            echo "nameserver 149.112.112.112" | tee -a /etc/resolv.conf
        fi
        ;;
    *) ;;
esac

#----setting local to US
echo ""
read -p "Force locale to US English (en-US)? [y/N] " choice </dev/tty
case "$choice" in
    "y" | "Y")
        echo "Forcing locale to en-US. Please ignore any errors below."
        export LC_ALL="en_US.UTF-8"
        echo "en_US.UTF-8 UTF-8" | tee -a /etc/locale.gen
        locale-gen en_US.UTF-8
        ;;
    *) ;;
esac

#----update raspberry
echo ""
echo "Lucy requires an up-to-date installation of your Raspberry Pi's operating"
echo "system software. If you have never done this before, it can take up to an"
echo "hour or longer."
read -p "Proceed with apt-get dist-upgrade? [Y/n] " choice </dev/tty
case "$choice" in
    "n" | "N")
        echo "Warning: you may encounter problems running TJBot recipes without performing"
        echo "an apt-get dist-upgrade. If you experience these problems, please re-run"
        echo "the bootstrap script and perform this step."
        ;;
    *)
        echo "Updating apt repositories [apt-get update]"
        apt-get update
        echo "Upgrading OS distribution [apt-get dist-upgrade]"
        apt-get -y dist-upgrade
        ;;
esac

#----nodejs install
echo ""
RECOMMENDED_NODE_LEVEL="18"
MIN_NODE_LEVEL="18"
NEED_NODE_INSTALL=false

if which node > /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    NODE_LEVEL=$(node --version 2>&1 | cut -d '.' -f 1 | cut -d 'v' -f 2)
    if [ $NODE_LEVEL -lt $MIN_NODE_LEVEL ]; then
        echo "Node.js v$NODE_VERSION.x is currently installed. We recommend installing"
        echo "v$MIN_NODE_LEVEL.x or later."
        NEED_NODE_INSTALL=true
    fi
else
    echo "Node.js is not installed."
    NEED_NODE_INSTALL=true
fi

if $NEED_NODE_INSTALL; then
    read -p "Would you like to install Node.js v$RECOMMENDED_NODE_LEVEL.x? [Y/n] " choice </dev/tty
    case "$choice" in
        "" | "y" | "Y")
            curl -sL https://deb.nodesource.com/setup_${RECOMMENDED_NODE_LEVEL}.x | sudo bash -
            apt-get install -y nodejs
            ;;
        *)
            echo "Warning: Lucy may not operate without installing a current version of Node.js."
            ;;
    esac
fi

#----install additional packages
echo ""
echo "Installing additional software packages (alsa, libasound2-dev, git, pigpio)"
# apt-get install -y alsa-base alsa-utils libasound2-dev git pigpio
apt-get install -y libasound2-dev git pigpio

#----remove outdated apt packages
echo ""
echo "Removing unused software packages [apt-get autoremove]"
apt-get -y autoremove

#----clone lucybot
LUCYBOT_DIR='/home/pi/Desktop/lucy'
#echo ""
#echo "We are ready to clone the LucyBot project."
#read -p "Where should we clone it to? (default: /home/pi/Desktop/lucy): " LUCYBOT_DIR </dev/tty
#if [ -z $LUCYBOT_DIR ]; then
#    LUCYBOT_DIR='/home/pi/Desktop/lucy'
#fi
#
#if [ ! -d $LUCYBOT_DIR ]; then
#    echo "Cloning LucyBot project to $LUCYBOT_DIR"
#    sudo -u $SUDO_USER git clone https://github.com/MarzlS/lucy.git $LUCYBOT_DIR
#else
#    echo "Lucy project already exists in $LUCYBOT_DIR, leaving it alone"
#fi

#----blacklist audio kernel modules
echo ""
echo "On Raspberry Pi 3 models, there is a known conflict between the LED "
echo "and the built-in audio jack. In order for the LED to work, we need to"
echo "disable certain kernel modules to avoid this conflict. If you have "
echo "plugged in a speaker via HDMI, USB, or Bluetooth, this is a safe "
echo "operation and you will be able to play sound and use the LED at the "
echo "same time. If you plan to use the built-in audio jack, we recommend "
echo "NOT disabling the sound kernel modules."
read -p "Disable sound kernel modules? [Y/n] " choice </dev/tty
case "$choice" in
    "" | "y" | "Y")
        echo "Disabling the kernel modules for the built-in audio jack."
        cp $LUCYBOT_DIR/bootstrap/lucybot-blacklist-snd.conf /etc/modprobe.d/
        ;;
    "n" | "N")
        if [ -f /etc/modprobe.d/tjbot-blacklist-snd.conf ]; then
            echo "Enabling the kernel modules for the built-in audio jack."
            rm /etc/modprobe.d/lucybot-blacklist-snd.conf
        fi
        ;;
    *) ;;
esac

#----installation complete
sleep_time=0.1
echo ""
echo ""
echo "                           .yNNs\`                           "
sleep $sleep_time
echo "                           :hhhh-                           "
sleep $sleep_time
echo "/ssssssssssssssssssssssssssssssssssssssssssssssssssssssssss+"
sleep $sleep_time
echo "yNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMNmmmNMMMMMMMMMMMMMMMMMMMMMMNmmmMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMNd/\`\`\`.+NNMMMMMMMMMMMMMMMMNm+.\` \`/dNMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMNo     \`hMMMMMMMMMMMMMMMMMMy\`     oNMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMNm+.\`\`-sNMMMMMMMMMMMMMMMMMNNs-\`\`.+mNMMMMMMMMMMMy"
sleep $sleep_time
echo "yMMMMMMMMMMMMMMNmmMMMMMMMMMMMMMMMMMMMMMMMMmmNMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "yNNNNNMMMMMMMMMMMMNNNNNNMMNNNNNNNNNNMMMMMMMMMMMMMMMMMMMNNNMy"
sleep $sleep_time
echo "-::::::::::::::::::::::::::::::::::::::::::::::::::::::::::-"
sleep $sleep_time
echo "                                                            "
sleep $sleep_time
echo "                     \`\`\`\`\`\`\`\`....--::::////++++ooossyyhhhhh/"
sleep $sleep_time
echo "//++ossssssyyyyhhddmmmmmmmmmmmmNNNNNMMNNNNNNMMMMMMMMMMMMMNNo"
sleep $sleep_time
echo "dMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy"
sleep $sleep_time
echo "sMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd"
sleep $sleep_time
echo "oNMMMMMMMMMMMMMMMMNNNNNNNNMMMMMMNNNNNmmmmmmmmmddhhhhyyyyssss"
sleep $sleep_time
echo "+Nmmmddhhhhyyyyssoo++++/////:::---....\`\`\`\`\`\`\`\`        "
sleep $sleep_time
echo ""
sleep $sleep_time
echo "-------------------------------------------------------------------"
sleep $sleep_time
echo "Setup complete. Your Raspberry Pi is now set up as a LucyBot! ;)"
sleep $sleep_time
echo "-------------------------------------------------------------------"
echo ""
read -p "Press enter to continue" nonce </dev/tty

#——instructions for ...
echo ""
echo "See Troubleshooting.md for test instructions."
echo ""
read -p "Press enter to continue" nonce </dev/tty

#----reboot
echo ""
read -p "We recommend rebooting for all changes to take effect. Reboot? [Y/n] " choice </dev/tty
case "$choice" in
    "" | "y" | "Y")
        echo "Rebooting."
        reboot
        ;;
    *)
        echo "Please reboot your Raspberry Pi for all changes to take effect."
        ;;
esac
