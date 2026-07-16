import sys
sys.path.append('/src')

from lib.color_setup import screen
from machine import Pin
import utime
import struct
from drivers.rotary_encoder import RotaryEncoder

# config
SCREEN_SIZE = SCREEN_W, SCREEN_H = 480, 320

ENCODER_L_CLK, ENCODER_L_DT = 12, 13
ENCODER_R_CLK, ENCODER_R_DT = 18, 19

BRUSH_RADIUS = 5

# define colors to be used
COLORS_SETUP = [
    ("BLACK", screen.rgb(0, 0, 0)), 
    ("WHITE", screen.rgb(255, 255, 255)), 
    ("RED", screen.rgb(255, 0, 0)), 
    ("GREEN", screen.rgb(0, 255, 0)), 
    ("BLUE", screen.rgb(0, 0, 255)),
]

# Populate lookup table
COLORS = {}
for index, (color_name, color_value) in enumerate(COLORS_SETUP):
    struct.pack_into("<H", screen.lut, index * 2, color_value)
    COLORS[color_name] = index

encoder_left = RotaryEncoder(
    pin_a=ENCODER_L_CLK,
    pin_b=ENCODER_L_DT,
    decoding=2
)
encoder_right = RotaryEncoder(
    pin_a=ENCODER_R_CLK,
    pin_b=ENCODER_R_DT,
    decoding=2
)

def main():
    screen.fill(COLORS['WHITE']) 
    screen.show()

    etcher_pos = [0, 0]
    # Drawing simple shapes to the screen
    while True:
        utime.sleep_ms(2)
        
        current_x = encoder_left.value
        current_y = -encoder_right.value

        if current_x != etcher_pos[0]:
            etcher_pos[0] = int(current_x)
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], True)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)

        if current_y != etcher_pos[0]:
            etcher_pos[1] = int(current_y)
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], True)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)

main()