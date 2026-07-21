from states.state import State
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class Brush:
    # TODO: use interpolation to draw circles between 2 positions, 
    # or a circle + a rectangle because we move one direction (l, r, u, d)
    def __init__(self, brush_color, tooltip_color, radius=2):
        self.pos = [SCREEN_W // 2, SCREEN_H // 2]
        self.radius = 3
        self.update_radius(radius)

        self.screen = ScreenManager.screen
        self.brush_color = brush_color
        self.tooltip_color = tooltip_color

        #self.mode = 'draw' | 'erase' | 'floating'

    def draw_stroke(self):
        pass

    def draw_circle(self):
        self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.brush_color, True)
        # tooltip
        self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.tooltip_color, False)
        self._refresh()

    def erase_tooltip(self):
        self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.brush_color, False)
        self._refresh()

    def _refresh(self):
        self.screen.show_region(self.pos[0] - self.radius, self.pos[1] - self.radius, self.pad, self.pad)

    def update_radius(self, radius):
        self.radius = radius
        self.pad = self.radius * 2 + 3


class DrawingState(State):
    def __init__(self, state_machine):
        self.state_machine = state_machine
        self.screen = ScreenManager.screen
        self.COLORS = ScreenManager.COLORS

        self.encoder_left = InputManager.encoder_left
        self.encoder_right = InputManager.encoder_right

        self.brush = Brush(
            [SCREEN_W // 2, SCREEN_H // 2],
            self.COLORS['RED'],
            radius=2
        )

        self.last_encoder_x = int(self.encoder_left.value)
        self.last_encoder_y = int(self.encoder_right.value)

    def draw(self, update=False):
        curr_encoder_x = int(self.encoder_left.value)
        curr_encoder_y = int(self.encoder_right.value)

        # Calculate position change (deltas)
        dx = (curr_encoder_x - self.last_encoder_x) * 2
        dy = (curr_encoder_y - self.last_encoder_y) * 2

        # keeping this separated for now, because could simplify logic
        # when filling spaces between two draw positions.
        if dx != 0 or update:
            self.brush.erase_tooltip()
            self.brush.pos[0] += dx
            self.brush.draw_circle()

        if dy != 0 or update:
            self.brush.erase_tooltip()
            self.brush.pos[1] += dy
            self.brush.draw_circle()

        self.last_encoder_x = curr_encoder_x
        self.last_encoder_y = curr_encoder_y

    def update(self):
        pass

    def on_enter(self):
        self.screen.fill(ScreenManager.COLORS['WHITE']) 
        self.screen.show()
    
    def on_exit(self):
        pass
    