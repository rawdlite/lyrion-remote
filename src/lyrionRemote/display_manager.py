#!/usr/bin/env python3
"""Display manager for OLED or LCD output."""
from pathlib import Path
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
from gpiozero import PWMLED


class Display:
    def __init__(self, config):
        led_config = config.get('led', {})
        active_high = led_config.get('active_high', True)
        self.green = PWMLED(led_config['led_green'], active_high=active_high, initial_value=False)
        self.red = PWMLED(led_config['led_red'], active_high=active_high, initial_value=False)
        yellow_pin = led_config.get('led_yellow')
        self.yellow = PWMLED(yellow_pin, active_high=active_high, initial_value=False) if yellow_pin else None

    def draw_text(self, text):
        print(text)

    def clear(self):
        self.draw_text('')

    def display_off(self):
        if hasattr(self, 'device') and hasattr(self.device, 'hide'):
            self.device.hide()
        else:
            self.clear()

    def pulse_green(self, on_time=0.1, off_time=0.1, n=1):
        self.green.pulse(on_time=on_time, off_time=off_time, n=n)

    def pulse_red(self, on_time=0.1, off_time=0.1, n=1):
        self.red.pulse(on_time=on_time, off_time=off_time, n=n)


class OLEDDisplay(Display):
    def __init__(self, config):
        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        super().__init__(config=config)
        self.oled_font = self._load_font()

    def _load_font(self):
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/DejaVuSans.ttf',
            Path.home() / '.fonts/DejaVuSans.ttf',
        ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(str(font_path), 20)
            except (FileNotFoundError, ImportError, OSError):
                continue
        try:
            return ImageFont.load_default()
        except Exception:
            return None

    def draw_text(self, text):
        with canvas(self.device) as draw:
            draw.text((5, 20), text, font=self.oled_font, fill='white')


class LCDisplay(Display):
    def __init__(self, config):
        from lcd import LCD1602 as LCD
        LCD.init(0x27, 1)
        LCD.closelight()
        self.device = LCD
        super().__init__(config=config)

    def draw_text(self, text):
        self.device.write(0, 1, text)

    def display_off(self):
        self.device.closelight()


def create_display(config):
    display_type = config.get('display', {}).get('type', 'lcd').lower()
    if display_type == 'oled':
        return OLEDDisplay(config)
    if display_type == 'lcd':
        return LCDisplay(config)
    return Display(config)
