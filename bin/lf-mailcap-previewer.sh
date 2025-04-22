#!/usr/bin/env bash
action=view
while getopts edp flag
do
    case "${flag}" in
        e) action=edit;;
        p) action=print;;
        d) debug=1;;
    esac
done
# Now handle positional arguments
shift $((OPTIND - 1))
FILE=$1

if [[ -L $FILE ]]; then
        FILE=$(readlink $FILE)
        echo $FILE
fi

if [[ $debug ]]; then
	run-mailcap --action=$action --debug --norun $FILE
else
  run-mailcap --action=$action $FILE
fi
