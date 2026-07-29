import io
import sys
sys.path.append('/src')

from states.state_machine import StateMachine
from states.unlock import UnlockState
from src.states.gallery import GalleryState
from states.drawing import DrawingState
from screen_manager import ScreenManager

def run_with_error_screen(func):
    try: 
        func()
    except Exception as e:
        screen = ScreenManager.screen

        buf = io.StringIO()
        sys.print_exception(e)
        sys.print_exception(e, buf)
        error_text = buf.getvalue()

        screen.fill(ScreenManager.COLORS['BLACK'])
        screen.text("An error occured.", 10, 10, ScreenManager.COLORS['WHITE'])

        for i, line in enumerate(error_text.splitlines()):
            screen.text(line, 10, 30 + i * 10)

        screen.show()


class App(StateMachine):
    def __init__(self):
        self.screen = ScreenManager.screen
        super().__init__(GalleryState(self))

    def loop(self):
        while True:
            self.update()
