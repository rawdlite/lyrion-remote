#!/usr/bin/env bash
action=open
cmd=""
debug=false
ask=false
set -o noclobber -o noglob -o nounset -o pipefail
IFS=$'\n'
while getopts edav flag
do
    case "${flag}" in
        e) action=edit;;
        v) action=viewer;;
        a) ask=true;;
        d) debug=true;;
    esac
done
# Now handle positional arguments
shift $((OPTIND - 1))

FILE_PATH="${1}"         # Full path of the highlighted file
FILE_EXTENSION="${FILE_PATH##*.}"
FILE_EXTENSION_LOWER="$(printf "%s" "${FILE_EXTENSION}" | tr '[:upper:]' '[:lower:]')"
MIMETYPE="$( file --dereference --brief --mime-type -- "${FILE_PATH}" )"

view_mime() {
    local mimetype="${1}"
    case "$mimetype" in
        text/plain|application/x-sh|audio/mpegurl)
            cmd="$PAGER ${FILE_PATH}";;
        audio/mpeg|audio/flac)
            cmd="eyeD3 -v $FILE_PATH | fold -s | $PAGER";;
    esac        
}

open_mime() {
    local mimetype="${1}"
    if [ "$debug" = true ]; then
        echo "$MIMETYPE"
    fi
    case "${mimetype}" in
        text/plain)
            cmd="bat --style snip -p $FILE_PATH";;
        application/x-sh)
            cmd="bat -p $FILE_PATH";;
        audio/*)
            cmd="lmscommander play $FILE_PATH";;
    esac
}

edit_mime() {
    local mimetype="${1}"
    case "$mimetype" in
        text/plain|application/x-sh|audio/mpegurl)
            cmd="$EDITOR ${FILE_PATH}";;
        audio/mpeg|audio/flac)
            cmd="beet edit $FILE_PATH";;
    esac        
}

if [[ $action == open ]]; then
    open_mime "${MIMETYPE}"
elif [[ $action == viewer ]]; then
    view_mime "${MIMETYPE}"
elif [[ $action == edit ]]; then
    edit_mime "${MIMETYPE}"
fi


if [ "$debug" = true ]; then
    echo "
          action: $action
          mime: $MIMETYPE
          FILE: $FILE_PATH
          ext: $FILE_EXTENSION_LOWER
          cmd: $cmd"
    read -n 1 -p "continue..."
elif [ "$ask" = true ]; then
    read -r -p "Do you want to proceed [Y/n]?" response
    response=${response,,} # tolower
    if [[ $response =~ ^(yes|y| ) ]] || [[ -z $response ]]; then
        eval "${cmd}"
        echo -ne '\007'
    else
        exit 0
    fi
else
    eval "${cmd}"
fi
