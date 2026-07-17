import utime
from states.state import State
from drivers.rotary_encoder import RotaryEncoder
from screen_manager import ScreenManager
from config import *


class Brush:
    def __init__(self):
        self.position = [0, 0]
        self.radius = 3
        self.color = COLORS 


class DrawingState(State):
    def __init__(self, state_machine, screen_manager: ScreenManager):
        self.state_machine = state_machine
        self.screen_manager = screen_manager
        self.screen = screen_manager.screen
        self.COLORS = screen_manager.COLORS

        # think of a good way of getting input
        self.encoder_left = RotaryEncoder(
            pin_a=ENCODER_L_CLK,
            pin_b=ENCODER_L_DT,
            decoding=2
        )
        self.encoder_right = RotaryEncoder(
            pin_a=ENCODER_R_CLK,
            pin_b=ENCODER_R_DT,
            decoding=2
        )

        self.etcher_pos = [0, 0]
        self.last_etcher_pos = None

    def draw(self):
        # Drawing simple shapes to the screen
        utime.sleep_ms(5)

        etcher_pos = self.etcher_pos
        encoder_x = int(self.encoder_left.value)
        encoder_y = int(self.encoder_right.value)

        if encoder_x != etcher_pos[0]:
            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['BLACK'], False)
            self.screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)
            
            etcher_pos[0] = encoder_x

            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['BLACK'], True)
            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['RED'], False)
            self.screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)

        if encoder_y != etcher_pos[1]:
            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['BLACK'], False)
            self.screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)
            
            etcher_pos[1] = encoder_y

            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['BLACK'], True)
            self.screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, self.COLORS['RED'], False)
            self.screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)
        
        self.last_etcher_pos = list(self.etcher_pos)

    def update(self):
        pass

    def on_enter(self):
        pass
    
    def on_exit(self):
        pass
    