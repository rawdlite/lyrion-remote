#!/usr/bin/env python3
"""Display manager for OLED output."""
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
from gpiozero import PWMLED

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