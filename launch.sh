#!/bin/bash
sleep 15s
cd ~/SelfWeigh/
MAIN_UNIT_IP="empty"
if ! pgrep -x "socat" > /dev/null
then
	sudo socat pty,link=/dev/ttyV0,raw,ignoreeof,echo=0,group-late=dialout,mode=660 tcp:$MAIN_UNIT_IP:3333,forever,interval=2 &
fi

FILE=""
DIR="~/droplet"
if ! [ $MAIN_UNIT_IP == "empty" ]; then
	if ! [ "$(ls -A $DIR)" ]; then
		sshfs -o reconnect pi@$MAIN_UNIT_IP:~/SelfWeigh /home/pi/droplet
	fi
else
	echo "Main unit's IP not specified in launch.sh. Exiting."
	exit 1
fi

echo "Program started" | ts >> logfile.log
unbuffer ~/SelfWeigh/main.py | ts | tee -a logfile.log
