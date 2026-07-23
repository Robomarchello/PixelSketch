from math import floor, sqrt
from states.state import State
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class Brush:
    # TODO: use interpolation to draw circles between 2 positions, 
    # or a circle + a rectangle because we move one direction (l, r, u, d)
    BRUSH_COLORS = ['BLACK', 'YELLOW', 'BLUE', 'CYAN', 'GREEN', 'PURPLE']
    MODES = ['draw', 'erase']

    def __init__(self, position, tooltip_color, radius=2):
        self.pos = position
        self.radius = 3
        self.move_resolution = 1
        self.update_radius(radius)

        self.screen = ScreenManager.screen
        self.color_index = 0
        self.brush_color = ScreenManager.COLORS[self.BRUSH_COLORS[self.color_index]]
        self.tooltip_color = tooltip_color
        self.bg_color = ScreenManager.COLORS[BG_COLOR]

        self.mode_index = 0
        self.mode = self.MODES[self.mode_index]

        self.changing_radius = False

    def draw_stroke(self, dx, dy, update):
        # assumes we draw either horizontal or vertical lines.
        curr_x = int(self.pos[0])
        curr_y = int(self.pos[1])

        if dx != 0:
            self.erase_tooltip()
            l_bound = min(0, dx)
            r_bound = max(0, dx)
            for dx_step in (list(range(l_bound, r_bound, self.move_resolution)) + [dx]):
                self.pos[0] = curr_x + dx_step
                self.draw_circle()

        if dy != 0:
            self.erase_tooltip()
            l_bound = min(0, dy)
            r_bound = max(0, dy)
            for dy_step in (list(range(l_bound, r_bound, self.move_resolution)) + [dy]):
                self.pos[1] = curr_y + dy_step
                self.draw_circle()

        if update:
            self.erase_tooltip()
            self.draw_circle()

        self.draw_tooltip()

    def draw_circle(self):
        if self.mode == 'draw':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.brush_color, True)
        elif self.mode == 'erase':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.bg_color, True)
        self._refresh()

    def draw_tooltip(self):
        # tooltip
        self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.tooltip_color, False)
        self._refresh()

    def erase_tooltip(self):
        if self.mode == 'draw':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.brush_color, False)
        elif self.mode == 'erase':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.bg_color, False)

        self._refresh() # could be optimized i think

    def toggle_mode(self):
        self.mode_index += 1
        self.mode_index %= len(self.MODES)
        self.mode = self.MODES[self.mode_index]

    def toggle_color(self):
        self.color_index += 1
        self.color_index %= len(self.BRUSH_COLORS)
        self.brush_color = ScreenManager.COLORS[self.BRUSH_COLORS[self.color_index]]

    def _refresh(self):
        self.screen.show_region(self.pos[0] - self.radius, self.pos[1] - self.radius, self.pad, self.pad)

    def update_radius(self, radius):
        self.radius = radius
        self.radius = max(0, self.radius)
        self.pad = self.radius * 2 + 3

        if self.radius == 0:
            self.move_resolution = 1
        else:
            # formula for calculating flat parallel lines on pixelated circle.
            self.move_resolution = 2 * floor(sqrt(self.radius - 0.25)) + 1
                
    def update_radius_by(self, change):
        self.erase_tooltip()
        radius = self.radius + change
        self.update_radius(radius)


class DrawingState(State):
    ENCODER_STEP = 2
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
        self.encoder_left.func = self.toggle_brush_mode
        self.encoder_right.func = self.toggle_brush_color

        self.last_encoder_x = int(self.encoder_left.value)
        self.last_encoder_y = int(self.encoder_right.value)

        self.radius_updated = False

    def toggle_brush_color(self):
        if not self.encoder_right.button_pressed:
            self.brush.toggle_color()
            self.brush.draw_stroke(0, 0, True)

    def toggle_brush_mode(self):
        if self.encoder_left.button_pressed:
            self.radius_updated = False

        if not self.encoder_left.button_pressed: #when unpressing
            if self.radius_updated:
                self.radius_updated = False
                return
            self.brush.toggle_mode()
            self.brush.draw_stroke(0, 0, True)

    def draw(self, update=False):
        curr_encoder_x = int(self.encoder_left.value)
        curr_encoder_y = int(self.encoder_right.value)

        # Calculate position change (deltas)
        dx = (curr_encoder_x - self.last_encoder_x) * self.ENCODER_STEP
        dy = (curr_encoder_y - self.last_encoder_y) * self.ENCODER_STEP

        if dx != 0 and self.encoder_left.button_pressed:
            self.brush.update_radius_by(dx // self.ENCODER_STEP)
            if not self.radius_updated:
                self.radius_updated = True
            dx = 0
            update = True

        # keeping this separated for now, because could simplify logic
        # when filling spaces between two draw positions.
        self.brush.draw_stroke(dx, dy, update)

        self.last_encoder_x = curr_encoder_x
        self.last_encoder_y = curr_encoder_y

    def update(self):
        pass

    def on_enter(self):
        self.screen.fill(ScreenManager.COLORS['WHITE']) 
        self.screen.show()
    
    def on_exit(self):
        pass
    