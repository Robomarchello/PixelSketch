from states.state import State
from screen_manager import ScreenManager
from input_manager import InputManager
from config import *


class Brush:
    # TODO: use interpolation to draw circles between 2 positions, 
    # or a circle + a rectangle because we move one direction (l, r, u, d)
    BRUSH_COLORS = ['BLACK', 'BLUE', 'GREEN']
    MODES = ['draw', 'erase']

    def __init__(self, position, tooltip_color, radius=2):
        self.pos = position
        self.radius = 3
        self.update_radius(radius)

        self.screen = ScreenManager.screen
        self.color_index = 0
        self.brush_color = ScreenManager.COLORS[self.BRUSH_COLORS[self.color_index]]
        self.tooltip_color = tooltip_color
        self.bg_color = ScreenManager.COLORS[BG_COLOR]

        self.mode_index = 0
        self.mode = self.MODES[self.mode_index]

        self.changing_radius = False


    def draw_circle(self):
        if self.mode == 'draw':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.brush_color, True)
        elif self.mode == 'erase':
            self.screen.ellipse(self.pos[0], self.pos[1], self.radius, self.radius, self.bg_color, True)

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

    def update_radius_by(self, change):
        self.erase_tooltip()
        radius = self.radius + change
        self.update_radius(radius)


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
        self.encoder_left.func = self.toggle_brush_mode
        self.encoder_right.func = self.brush.toggle_color

        self.last_encoder_x = int(self.encoder_left.value)
        self.last_encoder_y = int(self.encoder_right.value)

        self.radius_updated = False

    def toggle_brush_mode(self):
        if self.encoder_left.button_pressed:
            self.radius_updated = False

        if not self.encoder_left.button_pressed: #when unpressing
            if self.radius_updated:
                self.radius_updated = False
                return
            self.brush.toggle_mode()
            self.draw(update=True)

    def draw(self, update=False):
        curr_encoder_x = int(self.encoder_left.value)
        curr_encoder_y = int(self.encoder_right.value)

        # Calculate position change (deltas)
        dx = (curr_encoder_x - self.last_encoder_x) * 2
        dy = (curr_encoder_y - self.last_encoder_y) * 2

        if dx != 0 and self.encoder_left.button_pressed:
            self.brush.update_radius_by(dx // 2)
            if not self.radius_updated:
                self.radius_updated = True
            dx = 0
            update = True

        if dy != 0 and self.encoder_left.button_pressed:
            self.brush.toggle_color()

            dy = 0
            update = True

        # keeping this separated for now, because could simplify logic
        # when filling spaces between two draw positions.
        if dx != 0 or update:
            self.brush.erase_tooltip()
            self.brush.pos[0] += dx
            self.brush.draw_circle()

            self.encoder_l_rotated = True

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
    