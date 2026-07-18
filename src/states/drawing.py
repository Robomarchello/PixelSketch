from states.state import State
from screen_manager import ScreenManager
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

        # think of a good way of getting input

        self.brush = Brush(
            self.COLORS['BLACK'],
            self.COLORS['RED'],
            radius=2
        )

    def draw(self):
        # Drawing simple shapes to the screen
        encoder_x = int(self.encoder_left.value) * 2
        encoder_y = int(self.encoder_right.value) * 2

        if encoder_x != self.brush.pos[0]:
            self.brush.erase_tooltip()
            self.brush.pos[0] = encoder_x
            self.brush.draw_circle()

        if encoder_y != self.brush.pos[1]:
            self.brush.erase_tooltip()
            self.brush.pos[1] = encoder_y
            self.brush.draw_circle()

    def update(self):
        pass

    def on_enter(self):
        pass
    
    def on_exit(self):
        pass
    