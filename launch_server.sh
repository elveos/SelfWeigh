#!/bin/bash
cd ~/SelfWeigh
if ! pgrep -x "socat" > /dev/null
then
	sudo socat -s pty,link=/dev/ttyV0,raw,\
	ignoreeof,echo=0,group-late=dialout,mode=660 tcp:localhost:3333 &
fi

DIR="/home/pi/droplet"


echo "Program start"
unbuffer ./main_server.py | ts | tee -a logfile.log
