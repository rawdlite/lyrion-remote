#!/usr/bin/env python3
"""Chooser manager for rotary and button selection input."""
from time import sleep
from gpiozero import Button
from pigpio_encoder.rotary import Rotary
from lyrionRemote.urls.LMSURL import URL, Saraswati


def _resolve_rotary_config(config):
    return config.get('chooser', {}).get('rotary', {}) or config.get('rotary', {})


def _resolve_button_config(config):
    return config.get('chooser', {}).get('button', {}) or config.get('button_config', {})


class Chooser:
    def __init__(self, display, player, config):
        self.choices = list(URL.keys())
        self.display = display
        self.player = player
        self.sara = Saraswati()
        self.count = 0
        self.config = config

    def setup(self):
        return

    def next(self):
        self.count = (self.count + 1) % len(self.choices)
        self.display_choice()

    def previous(self):
        self.count = (self.count - 1) % len(self.choices)
        self.display_choice()

    def select(self):
        self.play_choice(self.count)

    def display_choice(self, index=None):
        if index is None:
            index = self.count
        self.display.draw_text(self.choices[index])

    def play_choice(self, index):
        url = self.sara.get_url(self.choices[index])
        self.player.play([url])
        self.display.display_off()


class RotaryChooser(Chooser):
    def __init__(self, display, player, config):
        super().__init__(display, player, config)
        settings = _resolve_rotary_config(config)
        self.rotary = Rotary(
            clk_gpio=settings['clk_pin'],
            dt_gpio=settings['dt_pin'],
            sw_gpio=settings['sw_pin'],
        )

    def setup(self):
        self.rotary.setup_rotary(
            min=-1,
            max=len(self.choices),
            scale=1,
            up_callback=self.up_callback,
            down_callback=self.down_callback,
        )
        self.rotary.setup_switch(
            debounce=200,
            long_press=True,
            sw_short_callback=self.sw_short,
            sw_long_callback=self.sw_long,
        )

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
        self.display.draw_text('clear display')
        sleep(1)
        self.display.display_off()


class ButtonChooser(Chooser):
    def __init__(self, display, player, config):
        super().__init__(display, player, config)
        settings = _resolve_button_config(config)
        self.button_fwd = Button(settings['button_fwd'])
        self.button_bwd = Button(settings['button_bwd'])
        self.button_sel = Button(settings['button_sel'])
        self.button_fwd.when_pressed = self.next
        self.button_bwd.when_pressed = self.previous
        self.button_sel.when_pressed = self.select

    def setup(self):
        self.display_choice()


def create_chooser(config, display, player):
    choice_type = config.get('chooser', {}).get('type', 'rotary').lower()
    if choice_type == 'button':
        return ButtonChooser(display, player, config)
    return RotaryChooser(display, player, config)
