#!/usr/bin/env python3
import threading
import time
import os
import tomllib
import subprocess
import logging
from time import sleep
from pathlib import Path
from gpiozero import Button, PWMLED, Device,ButtonBoard
from gpiozero.pins.pigpio import PiGPIOFactory
from pigpio_encoder.rotary import Rotary
from signal import pause
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106, ssd1306
from PIL import ImageFont, ImageDraw, Image
from urls.LMSURL import URL, Saraswati
from lyrionRemote.lmscommander import LMServer,LMPlayer,PlayerCommands


def main():
    with open(os.path.join(Path.home(),".config","lyrion-remote","config.toml"), mode="rb") as fp:
        settings = tomllib.load(fp)
    logelevel = logging.INFO
    debug = settings.get('general',{}).get('debug')
    if debug:
        loglevel = logging.DEBUG
    
    logging.basicConfig(filename='/var/log/gpio-process.log',
                        format='%(asctime)s %(levelname)s:%(message)s',
                        level=loglevel)
    logger.info('started')
    logger.debug(f"path: {os.environ['PATH']}")
    dsp = Display(config=settings)
    dsp.green.pulse()
    server = LMServer(settings.get('general',{}).get('server'))                       
    server.update()                                             
    player = LMPlayer(server.get_player(settings['general']['player']), verbose=True)
    pg = ProcessGPIO(display=dsp,player=player,config=settings)
    rt = RotaryEncoder(display=dsp,player=player,config=settings)
    dsp.green.off()
    pg.bb.when_pressed = pg.button_action
#
#sw1 = Button(5, pull_up=False
    rt.rotary.setup_rotary(min=-1,
                           max=len(rt.choices),
                           scale=1,
                       # debounce=2,
                       # # rotary_callback=rotary_callback,          
                           up_callback=rt.up_callback,
                           down_callback=rt.down_callback)           
                                                                          
    rt.rotary.setup_switch(debounce=200,
                           long_press=True,
                           sw_short_callback=rt.sw_short,
                           sw_long_callback=rt.sw_long)
    pause()


if __name__ == '__main__':
    main()
