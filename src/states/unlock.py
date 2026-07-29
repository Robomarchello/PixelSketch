from states.state import State
from src.states.gallery import GalleryState
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class UnlockState(State):
    UI_path = 'assets/unlock.bin'
    STEP = 4
    def __init__(self, state_machine):
        self.state_machine = state_machine

        self.screen = ScreenManager.screen
        self.COLORS = ScreenManager.COLORS

        self.encoder_left = InputManager.encoder_left
        self.encoder_right = InputManager.encoder_right

        self.min_bound = 52
        self.max_bound = 425

        self.y = 170
        self.h = 34

        # left rectangle grows rightward starting at min_bound
        self.x = int(self.min_bound)
        self.last_encoder_l = 0

        # right rectangle grows leftward starting at max_bound
        self.x_right = int(self.max_bound)
        self.last_encoder_r = 0

    def draw(self):
        pass

    def draw_rect(self, x, width):
        self.screen.fill_rect(x, self.y, width, self.h, self.COLORS['WHITE'])
        self.screen.show_region(x, self.y, width, self.h)

    def update(self):
        encoder_l = int(self.encoder_left.value) * self.STEP
        encoder_r = int(self.encoder_right.value) * self.STEP

        # LEFT: draw first at current x, then push x forward
        if self.last_encoder_l != encoder_l:
            change = abs(encoder_l - self.last_encoder_l)
            self.draw_rect(self.x, change)
            self.last_encoder_l = encoder_l

            self.x += change
            self.x = min(self.x, self.max_bound)

        # RIGHT: pull x_right back first, then draw at the new (leftmost) edge
        if self.last_encoder_r != encoder_r:
            change = abs(encoder_r - self.last_encoder_r)
            self.x_right -= change
            self.x_right = max(self.x_right, self.min_bound)

            self.draw_rect(self.x_right, change+3)
            self.last_encoder_r = encoder_r

        if self.x >= self.x_right:
            self.state_machine.change_state(GalleryState(self.state_machine))

    def on_enter(self):
        ScreenManager.write_image_to_screen(self.UI_path)
        ScreenManager.screen.show()

        InputManager.enable_input()

    def on_exit(self):
        InputManager.disable_input()
    