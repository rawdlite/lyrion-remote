#!/usr/bin/env bash
PROG=$0
FILE=$1
if [[ -L $FILE ]]; then
        FILE=$(readlink $FILE)
        echo $FILE
fi
if [[ ${0##*/} == "l-mime-edit" ]]; then
	run-mailcap --action=edit $FILE
elif [[ ${0##*/} == "l-mime-run" ]]; then
	run-mailcap --action=print $FILE
else
	run-mailcap --debug $FILE
fi	
