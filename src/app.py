import sys
sys.path.append('/src')

from states.state_machine import StateMachine
from states.unlock import UnlockState
from screen_manager import ScreenManager


class App(StateMachine):
    def __init__(self):
        super().__init__(UnlockState)

        self.screen = ScreenManager.screen

    def loop(self):
        while True:
            # utime.sleep_ms(2)
            self.update()
        

if __name__ == '__main__':
    App().loop()