#!/usr/bin/env python3
import os
import tomllib
import subprocess
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
from lyrionRemote.lmscommander import LMServer,LMPlayer
Device.pin_factory = PiGPIOFactory()

class RotaryEncoder():

    def __init__(self,display, player, config):
        _rotary = Rotary(clk_gpio=config['rotary']['clk_pin'],
                         dt_gpio=config['rotary']['dt_pin'],
                         sw_gpio=config['rotary']['sw_pin'])
        self.rotary = _rotary
        self.choices = list(URL.keys())
        self.display = display
        self.player = player
        self.sara = Saraswati()


    def up_callback(self, counter):
        if counter >= self.rotary.max:
            self.rotary.counter = 0
            counter = 0 
        self.display_choice(counter)

    def down_callback(self, counter):
        if counter <= -1:
            self.rotary.counter = self.rotary.max - 1
            counter = self.rotary.max - 1
        self.display_choice(counter)

    def sw_short(self):
        counter = self.rotary.counter
        if counter <= -1:
            counter = 0
        self.display_choice(counter)
        self.play_choice(counter)

    def sw_long(self):
        self.display.draw_text("clear display")
        sleep(1)
        self.display.device.hide()
        


    def display_choice(self, counter):
        #global runtime
        #runtime = 0
        self.display.device.show()
        self.display.draw_text(self.choices[counter])

    def play_choice(self,counter):
        url = self.sara.get_url(self.choices[counter])
        self.player.play([url])
        self.display.device.hide()
    

class Display():

    def __init__(self,config):
        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        self.oled_font = ImageFont.truetype('DejaVuSans.ttf', 20)
        self.green = PWMLED(config['led']['led_green'],active_high=True)
        self.red = PWMLED(config['led']['led_red'],active_high=True)


    def draw_text(self, text):
        with canvas(self.device) as draw:
        # draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((5, 20), text, font=self.oled_font, fill="white")        

class ProcessGPIO():

    def __init__(self, display,player,config):
        button_config = config['button_config']
        self.bb = ButtonBoard(hold_time=3,
                              hold_repeat=False,
                              pull_up=False,
                              **button_config)
        self.actions = config['button_actions']
        self.green = display.green
        self.red = display.red
        self.player = player
        self.display = display

    def button_action(self, button):
        self.green.on()
        cmd = self.actions[[k for k,v in button.value._asdict().items() if v == 1][0]]
        print(f"cmd: {cmd}")
        self.display.device.show()
        self.display.draw_text('action')
        #getattr(self.player, cmd)()
        try:
            res = subprocess.run(cmd, shell=True, check=True)
            print(res)
        except subprocess.CalledProcessError as err:
            self.red.on()
            print(f"{cmd} failed {err}")
            pass
        except Exception as err:
            self.red.pulse()
            print(f"Unexpected {err=}, {type(err)=}")
            pass
        finally:
            self.green.off()
            self.display.device.hide()

def main():
    with open(os.path.join(Path.home(),".config","niche-audio","config.toml"), mode="rb") as fp:
        settings = tomllib.load(fp)
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
