#!/bin/sh

#========================================================================================
# Basic gpio script
#----------------------------------------------------------------------------------------
# squeezelite -S /home/tc/powerscript.sh
#
# squeezelite sets $1 to:
#	0: off
#	1: on
#	2: initialising
#----------------------------------------------------------------------------------------

# Version: 0.01 2016-03-03 GE
#	Original.

# type tty at prompt to determine dev

#TERMINAL=/dev/console		# boot console

TERMINAL=/dev/pts/1			# ssh window

case $1 in
	2)
		echo "$1: Initialising..." >$TERMINAL
		;;
	1)
		/home/tc/start.sh
		;;
	0)
		/home/tc/stop.sh
		;;
esac
