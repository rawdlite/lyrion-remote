#!/usr/bin/env python3
"""GPIO controller for lyrion-remote hardware interface."""
import logging
import sys
from signal import pause
from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory
from lyrionRemote.config import load_config
from lyrionRemote.lmscommander import LMServer, LMPlayer
from lyrionRemote.display_manager import Display
from lyrionRemote.rotary_encoder_manager import RotaryEncoderManager
from lyrionRemote.rfid_manager import RFIDManager
from lyrionRemote.button_manager import ButtonManager

logger = logging.getLogger(__name__)
Device.pin_factory = PiGPIOFactory()


class GpioControler:
    def __init__(self):
        """Initialize GPIO controller and all hardware interfaces."""
        settings = load_config()
        
        # Setup logging
        debug = str(settings.get('general', {}).get('debug', '')).lower() in ('1', 'true', 'yes', 'on')
        loglevel = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(filename='/var/log/gpio-process.log',
                            format='%(asctime)s %(levelname)s:%(message)s',
                            level=loglevel)
        self.logger = logger
        self.logger.info('Initialization started')
        
        # Initialize display
        self.display = Display(config=settings)
        self.display.green.pulse()
        
        # Connect to LMS server
        self.server = LMServer(settings.get('general', {}).get('server'))
        self.server.update()
        self.player = LMPlayer(self.server.get_player(settings['general']['player']), verbose=True)
        
        # Setup rotary encoder with config
        self.rotary_encoder = RotaryEncoderManager(display=self.display, player=self.player, config=settings)
        
        # Initialize RFID reader
        status_led = self.display.green
        self.rfid_reader = RFIDManager(led_reference=status_led)
        
        # Initialize buttons
        self.button_board = ButtonManager(display=self.display, player=self.player, config=settings)
        
        self.display.green.off()
    
    def run(self):
        """Start all hardware event handlers and enter main event loop."""
        self.logger.info('Entering main loop')
        
        self.button_board.bb.when_pressed = self.button_board.button_action
        
        self.rotary_encoder.rotary.setup_rotary(min=-1,
                                                 max=len(self.rotary_encoder.choices),
                                                 scale=1,
                                                 up_callback=self.rotary_encoder.up_callback,
                                                 down_callback=self.rotary_encoder.down_callback)
        
        self.rotary_encoder.rotary.setup_switch(debounce=200,
                                                 long_press=True,
                                                 sw_short_callback=self.rotary_encoder.sw_short,
                                                 sw_long_callback=self.rotary_encoder.sw_long)
        
        pause()

def main():
    """Start the GPIO controller daemon.
    
    Intended to run as a systemd service or supervisor process,
    running indefinitely to handle hardware events.
    """
    try:
        gc = GpioControler()
        gc.logger.info('Initialization complete, entering main loop')
        gc.display.draw_text('Ready')
        gc.run()
    except KeyboardInterrupt:
        logger.info('Shutdown signal received')
    except Exception as exc:
        logger.exception('Fatal error in GPIO controller: %s', exc)
        sys.exit(1)

if __name__ == '__main__':
    main()
