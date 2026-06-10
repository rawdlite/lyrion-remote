#!/usr/bin/env python3
"""Display manager for OLED output."""
from pathlib import Path
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
from gpiozero import PWMLED

class Display():

    def __init__(self, config):
        serial = i2c(port=1, address=0x3C)
        self.device = sh1106(serial)
        self.oled_font = self._load_font()
        self.green = PWMLED(config['led']['led_green'], active_high=True)
        self.red = PWMLED(config['led']['led_red'], active_high=True)
    
    def _load_font(self):
        """Load TrueType font with fallback to default font if FreeType unavailable."""
        # Try to load system DejaVuSans font
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux standard
            '/System/Library/Fonts/DejaVuSans.ttf',              # macOS
            Path.home() / '.fonts/DejaVuSans.ttf',               # User fonts
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(str(font_path), 20)
            except (FileNotFoundError, ImportError, OSError):
                continue
        
        # Fallback to default PIL font if TrueType unavailable
        try:
            return ImageFont.load_default()
        except Exception:
            # Last resort - return None and handle in draw_text
            return None


    def draw_text(self, text):
        """Draw text on OLED display."""
        with canvas(self.device) as draw:
            draw.text((5, 20), text, font=self.oled_font, fill="white")  