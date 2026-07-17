# checkout experiments/drawing_prototype_circuit.png for the wiring
import sys
sys.path.append('/src')

import os

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

from lib.color_setup import screen
from machine import Pin
import utime
import struct
from drivers.rotary_encoder import RotaryEncoder
    
# config
SCREEN_SIZE = SCREEN_W, SCREEN_H = 480, 320

ENCODER_L_CLK, ENCODER_L_DT = 12, 13
ENCODER_R_CLK, ENCODER_R_DT = 18, 19

BRUSH_RADIUS = 3

CHUNK_SIZE = 512

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
    # inject save file
    if file_exists('save.bin'):
        with open('save.bin', 'rb') as file:
            while True:
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break

                binary = bytearray(chunk)
                pos = file.tell()
                screen.mvb[pos-CHUNK_SIZE:pos] = binary
    else:
        screen.fill(COLORS['WHITE']) 
    
    screen.show()

    etcher_pos = [0, 0]
    # Drawing simple shapes to the screen
    while True:
        utime.sleep_ms(5)
        
        encoder_x = int(encoder_left.value)
        encoder_y = int(encoder_right.value)

        if encoder_x != etcher_pos[0]:
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], False)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)
            
            etcher_pos[0] = encoder_x

            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], True)
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['RED'], False)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)

        if encoder_y != etcher_pos[1]:
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], False)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)
            
            etcher_pos[1] = encoder_y

            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['BLACK'], True)
            screen.ellipse(etcher_pos[0], etcher_pos[1], BRUSH_RADIUS, BRUSH_RADIUS, COLORS['RED'], False)
            screen.show_region(etcher_pos[0]-BRUSH_RADIUS, etcher_pos[1] - BRUSH_RADIUS, BRUSH_RADIUS*2+3, BRUSH_RADIUS*2+3)

try:
    main()
except Exception as e:
    print(e)
finally:
    # write save file
    with open('save.bin', 'wb') as file:
        file.write(screen.mvb)