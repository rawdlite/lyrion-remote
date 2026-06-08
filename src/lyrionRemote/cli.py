#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-
import logging
import tomllib
import argparse, textwrap
import os
from lyrionRemote.lmscommander import LMServer,LMPlayer,PlayerCommands
from pathlib import Path
from argparse import ArgumentParser
logger = logging.getLogger(__name__)
debug = True      
                
def main():
    LOGLEVEL = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    cmdhelpstr = "\n".join([f"{key}: {PlayerCommands[key]}" for key in PlayerCommands.keys()])
    lyrion_remote_config = Path(os.getenv("LYRION_REMOTE_CONFIG", "/config/lyrion-remote/config.toml"))
    if not lyrion_remote_config.is_file():
        lyrion_remote_config = Path.home() / ".config" / "lyrion-remote" / "config.toml"
    try:
        with open(lyrion_remote_config, mode="rb") as fp:
            settings = tomllib.load(fp)
            # print(f"Successfully loaded configuration from: {config_path}")
        
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{config_path}'")
        print("Please ensure the file exists or set the LYRION_REMOTE_CONFIG environment variable.")
        sys.exit(1)
        
    server_id = settings.get('general',{}).get('server')
    player_id = settings['general']['player']
    debug = settings.get('general',{}).get('debug')
    parser = ArgumentParser(description="Interact with Logitech Media Server",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('cmd', help=cmdhelpstr)
    parser.add_argument("-v", "--verbose", action='count', default=0,
                    help="increase output verbosity")
    parser.add_argument("-s", "--server", dest="server", default=server_id)
    parser.add_argument("-p", "--player", dest="player", default=player_id)
    parser.add_argument("tracks", nargs="*", help='files or url')
    args = parser.parse_args()
    if not LOGLEVEL.get(args.verbose):
        print("invalid loglevel")
        exit(1)
    logging.basicConfig(format='%(asctime)s %(message)s',
                        level=LOGLEVEL[args.verbose])
    if debug or args.verbose == 2:
        # ToDo: make dir configurable
        fh = logging.FileHandler('/tmp/lmscommand.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    
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
