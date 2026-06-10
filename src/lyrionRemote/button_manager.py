#!/usr/bin/env python3
import subprocess
import logging
from gpiozero import Button, PWMLED, Device,ButtonBoard
from lyrionRemote.lmscommander import LMServer,LMPlayer,PlayerCommands

logger = logging.getLogger(__name__)

class ButtonManager:
    def __init__(self, display,player,config):
        button_config = config['button_config']
        # build a button board from the config, the keys of button_config should be the same as the button names in the config
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
        self.red.off()
        cmd = self.actions[[k for k,v in button.value._asdict().items() if v == 1][0]]
        print(f"cmd: {cmd}")
        self.display.device.show()
        # shorten the cmd for display, remove 'lmscommander ' and limit to 10 chars
        action = cmd.replace('lmscommander ','')[0:10]
        self.display.draw_text(action)
        #ToDo: check if action is in allowed commands (solves virtual env prob)
        #getattr(self.player, cmd)(a
        if cmd in PlayerCommands:
            getattr(self.player, cmd)()
        else:    
            try:
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=False)
                logger.debug(res.stdout)       
            except subprocess.CalledProcessError as err:
                self.red.on()
                logger.error(f"{cmd} failed {err}")
                print(f"{cmd} failed {err}")
                pass
            except Exception as err:
                self.red.pulse()
                logger.error(f"{cmd} failed Unexpected error {err}")
                pass
            if res.returncode != 0:
                self.red.pulse()
                logger.error(f"{res.stderr.strip()} returncode:{res.returncode}")
            elif len(res.stderr):
                logger.warning(res.stderr)    
        self.green.off()
        self.display.device.hide()