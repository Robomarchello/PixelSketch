import sys
sys.path.append('/src')

from states.state_machine import StateMachine
from states.unlock import UnlockState
from src.states.gallery import GalleryState
from states.drawing import DrawingState
from screen_manager import ScreenManager


class App(StateMachine):
    def __init__(self):
        self.screen = ScreenManager.screen
        super().__init__(GalleryState(self))

    def loop(self):
        while True:
            self.update()