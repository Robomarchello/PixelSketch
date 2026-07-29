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

        screen.fill(ScreenManager.COLORS['RED'])
        screen.text("An error occured.", 10, 10, ScreenManager.COLORS['WHITE'])

        for i, line in enumerate(error_text.splitlines()):
            offset = 30 + i * 10
            screen.text(line, 10, offset, ScreenManager.COLORS['WHITE'])

        with open('assets/error_skull.txt', 'r', encoding='utf-8') as file:
            for i, line in enumerate(file):
                offset_new = offset + (i + 3) * 10
                screen.text(line.rstrip(), 75, offset_new, ScreenManager.COLORS['WHITE'])

        screen.show()


class App(StateMachine):
    def __init__(self):
        self.screen = ScreenManager.screen
        super().__init__(GalleryState(self))

    def loop(self):
        while True:
            self.update()