#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-
import logging
from time import time
from datetime import timedelta
from json import dumps as to_json
from sys import stderr
from collections import OrderedDict
from lms import Server, __version__
from re import match

TIMEOUT = timedelta(seconds=5)

class LMServer(Server):
    def __init__(self,host=None, port=9000, username=None, password=None):
        super().__init__(host=host,port=port)

    def get_player(self, player_id=None):
        my_player = None
        if player_id:
            for player in self.players:
                if player_id.lower() in [
                    player.player_id,
                    player.name.lower(),
                    player.ip]:
                    my_player = player
        elif len(self.players) >= 1:
            my_player = self.players[0]
        return my_player

    def status(self,*args):
        print('status called')
        for player in self.players:
            if player.is_playing:
                status = 'playing'
            elif player.is_paused:
                status = 'paused'
            elif player.is_stopped:
                status = 'stopped'
            else:
                status = '?'
            print(f'- {player.name:10} {player.model:16} '
                  f'{player.ip:15} 📶{player.wifi_signal_strength:>4}% '
                  f'{status:7} '
                  f'{(player.artist or "")[:10]:10} {(player.title or "")[:10]:10} '
                  f'{round(player.position_pct):3}% '
                  f'{self._timeFmt(player.position) or "     "}/'
                  f'{self._timeFmt(player.duration) or "     "} ')


        
    def _timeFmt(self, secs):
        if not secs:
            return ''
        h, r = divmod(secs, 3600)
        m, secs = divmod(r, 60)
        return '%s%02d.%02d' % ('' if not h else '%02d:' % h, m, secs)        


class LMPlayer():
    def __init__(self, player, verbose=False):
        self.player = player
        self.server = player._server
        self.verbose = verbose
        self.PATH_ON_HOST = "/data/music/music_data"
        self.PATH_IN_DOCKER = "/music"

    def __str__(self):
        if self.player.is_playing:
            status = 'playing'
        elif self.player.is_paused:
            status = 'paused'
        elif self.player.is_stopped:
            status = 'stopped'
        else:
            status = '?'
        return (f"player: {self.player.name} {self.player.player_id} {self.player.model} {self.player.ip}"
                f"\n{self.player.artist or ''} {self.player.title or ''}"
                f"\n{self.player.position_pct}: {self.player.position} / {self.player.duration}"
                f"\nstatus: {status}")

    def vprint(self,text):
        if self.verbose:
            print(text)
        

    def parse_track(self, track):
        if track.startswith(self.PATH_ON_HOST):
            self.vprint('is file')
            return  f"file://{track.replace(self.PATH_ON_HOST,self.PATH_IN_DOCKER)}"
        elif track.startswith('http'):
            self.vprint('is_url')
            return track
        else:
            print(f"whats going on with {track}?")

    def build_tracks(self, tracks):
        track_list = []
        for track in tracks:
            track_uri = self.parse_track(track)
            self.vprint(track_uri)
            track_list.append(track_uri)
        return track_list     
    
    def status(self,*args):
        self.server.status()

    def show(self, line1, line2=''):
        self.player.query('display',line1,line2,'4')   

    def pause(self, *args):
        self.player.pause()
        self.show('pause')

    def play(self, tracks):
        track_list = None
        self.show('play',tracks)
        
        if tracks:
            track_list = self.build_tracks(tracks)
            self.vprint(track_list)
            if len(tracks) > 1:
                self.player.enqueue_uri(track_list)
                self.player.play()
            else:
                self.player.play_uri(track_list[0])
        else:
            self.player.play()

    def add(self, tracks):
        track_list = self.build_tracks(tracks)
        self.show('enqueue',track_list)
        self.player.enqueue_uri(track_list)
        
    def insert(self, tracks):
        track_list = self.build_tracks(tracks)
        self.show('insert',track_list)
        player.query('playlist', 'insert', track_list)

    def next(self, *args):
        self.show('next','')
        self.player.next()

    def prev(self, *args):
        self.show('previous','#')
        self.player.previous()

    def shuffle(self, *args):
        self.show('shuffle','')
        self.player.query('playlist', 'shuffle', 1)
        
    def unshuffle(self, *args):
        self.show('unshuffle','')
        self.player.query('playlist', 'shuffle', 0)
        
    def toggle_shuffle(self, *args):
        self.show('toggle_shuffle','')
        self.player.query('playlist', 'shuffle')
        
    def random(self, *args):
        self.show('random','')
        self.player.query('randomplay', 'albums')

    def sleep(self, args):
        res = self.player.query('sleep', '?')
        active_sleep = int(res.get('_sleep', 0))
        sleep_time = 600
        #print(f"active_sleep: {active_sleep} {res}")    
        if args:
            try:
                sleep_time = int(args[0]) * 60
            except ValueError:
                print(f"error: argument {args[0]} not a number")
        sleep_set = active_sleep + sleep_time
        #print(f"sleep_time: {sleep_set}")
        self.show('sleep',f"{sleep_set/60} min")
        self.player.query('sleep', sleep_set)

    def unsleep(self, *args):
        self.player.query('sleep', 0)
        
                
