
from time import sleep
from pigpio_encoder.rotary import Rotary
from lyrionRemote.urls.LMSURL import URL, Saraswati

class RotaryEncoderManager:
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