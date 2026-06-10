#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-
import logging
import argparse
import sys
from lyrionRemote.config import load_config
from lyrionRemote.lmscommander import LMServer, LMPlayer, PlayerCommands
from pathlib import Path
from argparse import ArgumentParser

logger = logging.getLogger(__name__)


def main():
    LOGLEVEL = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    cmdhelpstr = "\n".join([f"{key}: {PlayerCommands[key]}" for key in PlayerCommands.keys()])
    settings = load_config()

    server_id = settings.get('general', {}).get('server')
    player_id = settings.get('general', {}).get('player')
    debug_setting = settings.get('general', {}).get('debug')
    log_dir = settings.get('general', {}).get('log_dir')
    debug = str(debug_setting).lower() in ('1', 'true', 'yes', 'on')

    parser = ArgumentParser(description="Interact with Logitech Media Server",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('cmd', help=cmdhelpstr)
    parser.add_argument("-v", "--verbose", action='count', default=0,
                    help="increase output verbosity")
    parser.add_argument("-s", "--server", dest="server", default=server_id)
    parser.add_argument("-p", "--player", dest="player", default=player_id)
    parser.add_argument("--log-dir", dest="log_dir", default=log_dir,
                    help="directory for debug log file")
    parser.add_argument("tracks", nargs="*", help='files or url')
    args = parser.parse_args()
    if not LOGLEVEL.get(args.verbose):
        print("invalid loglevel")
        exit(1)
    logging.basicConfig(format='%(asctime)s %(message)s',
                        level=LOGLEVEL[args.verbose])
    if debug or args.verbose == 2:
        log_dir_path = Path(args.log_dir) if args.log_dir else Path('/tmp')
        try:
            log_dir_path.mkdir(parents=True, exist_ok=True)
            log_file = log_dir_path / 'lmscommand.log'
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)
        except OSError as exc:
            print(f"Warning: Could not write log file to '{log_dir_path}': {exc}", file=sys.stderr)
    
    player_id = args.player
    server = LMServer(host=server_id)
    server.update()
    
    if args.cmd == 'status':
        if server.players:
            server.status()
        else:
            print(" No players found on the server.")
        exit(0) # Exit with an error code
    player_data = server.get_player(player_id)
    if player_data:
        my_player = LMPlayer(server.get_player(player_id))
    else:
        # If not found, print available players and exit gracefully
        print(f"Error: Player '{player_id}' not found.")
        if server.players:
            print("\nAvailable players:")
            for p in server.players:
                print(p.name)
        else:
            print(" No players found on the server.")
        exit(1) # Exit with an error code
    if args.verbose:
        print(my_player)
        print(args.cmd)
        print(args.tracks)

    logger.info(f"player: {my_player}\nargs: {args.cmd}\n tracks: {args.tracks}")
    if args.cmd == 'info':
        print(my_player)
    elif args.cmd == 'get_players':
        for player in server.players:
            print(player.name)
    else:
        getattr(my_player, args.cmd)(args.tracks)
    exit(0)

if __name__ == '__main__':
   main()
