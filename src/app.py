import sys
sys.path.append('/src')

from states.state_machine import StateMachine
from states.drawing import DrawingState
from screen_manager import ScreenManager


class App(StateMachine):
    def __init__(self):
        super().__init__(ScreenManager, DrawingState)

        self.screen = ScreenManager.screen

    def loop(self):
        self.screen.fill(ScreenManager.COLORS['WHITE']) 
        self.screen.show()
        while True:
            self.update()
        

if __name__ == '__main__':
    App().loop()